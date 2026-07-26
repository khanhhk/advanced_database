# Kết quả semantic

- `semantic_reasoning.json`: materialization và validation trên cùng snapshot CSV
  được nạp vào Neo4j.
- `sparql_execution.json`: kết quả catalog 10 truy vấn SPARQL sau materialization.

Đây là profile tương tác/kiểm chứng ngoại tuyến. Neo4j vẫn là kho vận hành duy
nhất. Profile chỉ tuyên bố các luật RDFS/OWL đã khai báo, không tuyên bố đầy đủ
OWL 2 DL.
