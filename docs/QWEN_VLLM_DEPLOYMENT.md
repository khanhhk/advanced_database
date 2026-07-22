# Runbook chi tiết — Dựng Qwen3-8B-AWQ với vLLM

## 1. Mục tiêu

Dựng một model server local để `src.qa.planner.QuestionPlanner` gọi qua API tương
thích OpenAI. Model chỉ tạo QueryPlan JSON cho Movie Knowledge Graph.

Kiến trúc runtime:

```text
FastAPI process (.venv)
  → HTTP 127.0.0.1:8001/v1/chat/completions
  → vLLM process (.venv-llm)
  → Qwen3-8B-AWQ trên RTX 3060
```

## 2. Cấu hình đã kiểm chứng

| Thành phần | Giá trị |
|---|---|
| GPU | NVIDIA GeForce RTX 3060 12 GB |
| Driver đã thử | 580.126.09 |
| Driver-reported CUDA | 13.0 |
| Python | 3.11 |
| Model | `Qwen/Qwen3-8B-AWQ` |
| vLLM | `0.25.0` |
| Context | 4096 |
| GPU utilization target | 0.85 |
| Sampling backend | native (`VLLM_USE_FLASHINFER_SAMPLER=0`) |
| Bind | `127.0.0.1:8001` |

Driver-reported CUDA version không đồng nghĩa máy đã cài CUDA toolkit/nvcc.
Thiết lập này cố ý không yêu cầu `/usr/local/cuda`.

## 3. Kiểm tra máy

```bash
nvidia-smi
python3 --version
df -h . ~/.cache
```

Yêu cầu thực tế:

- NVIDIA driver hoạt động.
- Khoảng 12 GB VRAM cho cấu hình hiện tại.
- Khoảng 15–20 GB disk trống để chứa environment/cache an toàn.
- RAM đủ cho quá trình load model; máy đã thử có hơn 20 GB available.

## 4. Cài môi trường model

Không cài vLLM vào `.venv` của ứng dụng.

```bash
make llm-setup
```

Make target thực hiện:

```bash
python3 -m venv .venv-llm
.venv-llm/bin/pip install --upgrade pip 'vllm==0.25.0'
.venv-llm/bin/pip uninstall -y torchcodec
```

### Tại sao uninstall torchcodec

vLLM 0.25.0 import optional video backend. Trên máy hiện tại, torchcodec cố load
FFmpeg shared libraries như `libavutil.so` và làm startup lỗi dù Qwen là
text-only. Khi không có package, vLLM dùng placeholder cho video và text serving
vẫn hoạt động.

Không cần cài FFmpeg system chỉ để phục vụ model text.

## 5. Tải và chạy model

```bash
make llm-run
```

Lệnh đầy đủ:

```bash
VLLM_USE_FLASHINFER_SAMPLER=0 \
.venv-llm/bin/vllm serve Qwen/Qwen3-8B-AWQ \
  --host 127.0.0.1 \
  --port 8001 \
  --max-model-len 4096 \
  --gpu-memory-utilization 0.85
```

Lần đầu Hugging Face tải khoảng 5,68 GiB checkpoint. Các lần sau dùng cache.

### Ý nghĩa tham số

- `VLLM_USE_FLASHINFER_SAMPLER=0`: không JIT FlashInfer sampling bằng nvcc.
- `--host 127.0.0.1`: không public model server.
- `--port 8001`: tránh trùng FastAPI 8000.
- `--max-model-len 4096`: đủ cho system prompt + JSON Schema + câu hỏi.
- `--gpu-memory-utilization 0.85`: chừa headroom cho desktop/driver.

## 6. Dấu hiệu startup thành công

Log cần có:

```text
Resolved architecture: Qwen3ForCausalLM
Using MarlinLinearKernel for AutoAWQMarlinLinearMethod
Model loading took ... GiB
FlashInfer top-p/top-k sampling disabled
Starting vLLM server on http://127.0.0.1:8001
Application startup complete
```

Kiểm tra:

```bash
curl -f http://127.0.0.1:8001/health
curl -s http://127.0.0.1:8001/v1/models
nvidia-smi
```

## 7. Cấu hình ứng dụng

`.env`:

```dotenv
LLM_API_KEY=local
LLM_BASE_URL=http://127.0.0.1:8001/v1
LLM_MODEL=Qwen/Qwen3-8B-AWQ
LLM_TIMEOUT=60
```

`LLM_API_KEY=local` là placeholder vì vLLM local chưa bật authentication. Không
public port 8001.

Khởi động ứng dụng ở terminal khác:

```bash
make demo
```

## 8. Cách planner gọi Qwen

Planner gửi:

- system prompt chứa graph schema và mapping rules;
- user question;
- `temperature=0`;
- `response_format.type=json_schema`;
- schema lấy từ `QueryPlan.model_json_schema()`.

`/no_think` ở đầu system prompt tắt thinking mode. Tác vụ là extraction/plan,
không cần chain-of-thought dài.

### Vì sao không chỉ dùng `json_object`

Thử nghiệm thực tế cho thấy `json_object` có thể trả JSON hợp lệ nhưng sai schema:

- bỏ `entity.type`;
- dùng `role=genre`;
- đổi `filters` list thành object;
- đổi cấu trúc `sort`.

JSON Schema constrained decoding sửa lớp lỗi này trước khi Pydantic validate.

## 9. Smoke test planner

```bash
.venv/bin/python -c "from src.qa.planner import QuestionPlanner; \
p=QuestionPlanner('local','http://127.0.0.1:8001/v1',\
'Qwen/Qwen3-8B-AWQ',60); \
print(p.plan('Gợi ý phim giống Inception').model_dump_json(indent=2))"
```

Output mong đợi có dạng:

```json
{
  "operation": "recommend",
  "target": "Movie",
  "entities": [
    {"type": "Movie", "name": "Inception", "role": null}
  ],
  "filters": [],
  "sort": null,
  "limit": 10,
  "confidence": 0.9,
  "clarification": ""
}
```

## 10. End-to-end test với Neo4j

```bash
.venv/bin/python -c "from src.config import get_settings; \
from src.kg.repository import Neo4jRepository; \
s=get_settings(); r=Neo4jRepository(s.neo4j_uri,s.neo4j_user,\
s.neo4j_password,s.neo4j_database); \
print(r.answer('Elisa Gabrielli từng góp mặt trong phim nào?')); r.close()"
```

Luồng này kiểm tra model, schema, linker, compiler và Neo4j trong một request.

## 11. SSH từ máy demo

Trên máy demo:

```bash
ssh -N -L 8001:127.0.0.1:8001 user@may-gpu
```

FastAPI trên máy demo tiếp tục gọi `http://127.0.0.1:8001/v1`. SSH mã hóa kết
nối và không yêu cầu public vLLM.

Khuyến nghị:

- Dùng SSH key.
- Bật keepalive.
- Không dùng `--host 0.0.0.0` trừ khi có firewall/authentication.
- Kiểm tra tunnel bằng `/health` trước khi demo.

## 12. Troubleshooting

### `Could not load libtorchcodec`

Nguyên nhân: thiếu FFmpeg shared library hoặc mismatch torchcodec.

Giải pháp cho model text:

```bash
.venv-llm/bin/pip uninstall -y torchcodec
```

### `Could not find nvcc` hoặc `/usr/local/cuda doesn't exist`

Nguyên nhân: FlashInfer sampler JIT trong khi chỉ có driver.

Giải pháp:

```bash
export VLLM_USE_FLASHINFER_SAMPLER=0
```

### CUDA out of memory

1. Dừng process GPU không cần thiết.
2. Giảm `--gpu-memory-utilization` xuống `0.80` nếu lỗi ở startup.
3. Giảm `--max-model-len` xuống `3072` nếu prompt vẫn vừa.
4. Không chạy thêm model/process CUDA trên cùng GPU.

### Planner fallback về regex

Kiểm tra:

- `.env` có `LLM_API_KEY` và `LLM_MODEL`.
- `/health` của vLLM.
- model name đúng `/v1/models`.
- timeout đủ lớn cho request đầu.

### JSON hợp lệ nhưng plan sai nghĩa

JSON Schema chỉ bảo đảm cấu trúc. Cần:

- thêm rule/few-shot có mục tiêu vào system prompt;
- bổ sung case vào corpus planner;
- đánh giá execution accuracy, không chỉ JSON validity.

Một lỗi đã quan sát: “mới nhất trước” từng bị model tự thêm filter ngày. Prompt
được bổ sung quy tắc và example để chỉ tạo `sort release_date desc`.

## 13. Vận hành và quan sát

Trước demo:

```bash
curl -f http://127.0.0.1:8001/health
nvidia-smi
curl -f http://127.0.0.1:8000/health
pytest -q
```

Nên warm-up bằng 2–3 câu hỏi trước khi trình bày để kernel/cache đã sẵn sàng.

## 14. Reproducibility record

Khi thay model/runtime, ghi lại:

- model repository và revision;
- quantization;
- vLLM version;
- driver/GPU;
- startup flags;
- system prompt version;
- QueryPlan schema version;
- evaluation corpus/result.

Không so sánh model bằng cảm nhận trên vài câu demo; dùng cùng corpus và metric.
