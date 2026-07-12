(() => {
  'use strict';
  const $ = selector => document.querySelector(selector);
  const escapeHtml = value => String(value ?? '').replace(/[&<>'"]/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[char]));
  const api = async (url, options = {}) => {
    const response = await fetch(url, {headers: {'Content-Type': 'application/json'}, ...options});
    const body = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(body.detail || `Lỗi HTTP ${response.status}`);
    return body;
  };
  const setBusy = (form, busy) => { const button = form.querySelector('button[type="submit"]'); button.disabled = busy; button.textContent = busy ? 'Đang xử lý…' : button.dataset.label; };
  document.querySelectorAll('form').forEach(form => { const button=form.querySelector('button[type="submit"]'); if(button) button.dataset.label=button.textContent; });

  document.querySelectorAll('.tab').forEach(tab => tab.addEventListener('click', () => {
    document.querySelectorAll('.tab').forEach(x => x.classList.toggle('active', x === tab));
    document.querySelectorAll('.panel').forEach(panel => { const active=panel.id===tab.dataset.panel; panel.classList.toggle('active',active); panel.hidden=!active; });
  }));

  const chat = $('#chatHistory');
  const addMessage = (role, html) => { const item=document.createElement('div'); item.className=`message ${role}`; item.innerHTML=html; chat.appendChild(item); chat.scrollTop=chat.scrollHeight; };
  const evidenceHtml = evidence => {
    if (!evidence?.length) return '<div class="empty-evidence">Câu trả lời này không có bản ghi bằng chứng.</div>';
    return evidence.map((item,index) => {
      if (item.entity_links) return `<div class="evidence-item"><strong>Liên kết thực thể</strong>${item.entity_links.map(link=>`<dl><dt>Dữ liệu nhập</dt><dd>${escapeHtml(link.input)}</dd><dt>Thực thể</dt><dd>${escapeHtml(link.canonical_name)}</dd><dt>Độ tin cậy</dt><dd>${Math.round(Number(link.confidence)*100)}%</dd></dl>`).join('')}</div>`;
      const fields=Object.entries(item).filter(([,value])=>value!==null&&value!==undefined&&value!==''&&(!Array.isArray(value)||value.length));
      return `<div class="evidence-item"><strong>Bằng chứng ${index+1}</strong><dl>${fields.map(([key,value])=>`<dt>${escapeHtml(key.replaceAll('_',' '))}</dt><dd>${escapeHtml(Array.isArray(value)?value.join(' → '):typeof value==='object'?JSON.stringify(value):value)}</dd>`).join('')}</dl></div>`;
    }).join('');
  };
  $('#askForm').addEventListener('submit', async event => {
    event.preventDefault();
    const form=event.currentTarget, input=$('#questionInput'), question=input.value.trim(); if(!question) return;
    addMessage('user', escapeHtml(question)); input.value=''; setBusy(form,true);
    const pending=document.createElement('div'); pending.className='message assistant pending'; pending.textContent='Đang truy vấn Knowledge Graph…'; chat.appendChild(pending);
    try { const result=await api('/ask',{method:'POST',body:JSON.stringify({question})}); pending.remove(); addMessage('assistant',`<div>${escapeHtml(result.answer)}</div><div class="meta"><span>${escapeHtml(result.intent)}</span><span>${result.query_time_ms.toFixed(1)} ms</span><span>${result.evidence.length} bằng chứng</span></div><details class="evidence"><summary>Xem bằng chứng (${result.evidence.length})</summary><div class="evidence-list">${evidenceHtml(result.evidence)}</div></details>`); }
    catch(error){ pending.remove(); addMessage('error',`Không thể trả lời: ${escapeHtml(error.message)}`); }
    finally { setBusy(form,false); input.focus(); }
  });
  $('#clearChat').addEventListener('click',()=>{chat.innerHTML='<div class="message assistant">Hội thoại đã được làm mới. Bạn muốn hỏi gì tiếp theo?</div>';$('#questionInput').focus();});

  const movieCard = (item, type) => `<article class="movie-card"><div class="card-top"><h3>${escapeHtml(item.title)}</h3><span class="score">${Math.round(item.score*100)}%</span></div>${item.rating!=null?`<div class="rating">★ ${Number(item.rating).toFixed(1)}</div>`:''}${item.genres?.length?`<div class="chips">${item.genres.map(x=>`<span>${escapeHtml(x)}</span>`).join('')}</div>`:''}<p>${escapeHtml(item.explanation)}</p>${type==='recommend'&&item.graph_score!=null?`<div class="score-bars"><small>Graph ${Number(item.graph_score).toFixed(3)} · Nội dung ${Number(item.semantic_score).toFixed(3)} · Chất lượng ${Number(item.quality_score).toFixed(3)}</small></div>`:''}</article>`;
  $('#searchForm').addEventListener('submit',async event=>{event.preventDefault();const form=event.currentTarget,status=$('#searchStatus'),out=$('#searchResults');setBusy(form,true);status.textContent='Đang tìm trong 2.000 phim…';out.innerHTML='';try{const rows=await api('/search',{method:'POST',body:JSON.stringify({query:$('#searchInput').value.trim(),top_k:10})});status.textContent=rows.length?`Tìm thấy ${rows.length} kết quả phù hợp.`:'Không tìm thấy phim phù hợp.';out.innerHTML=rows.map(x=>movieCard(x,'search')).join('');}catch(error){status.textContent=`Lỗi: ${error.message}`;}finally{setBusy(form,false);}});

  const methodDescriptions={overlap:'Ưu tiên phim có nhiều đạo diễn, diễn viên, thể loại và từ khóa chung.',weighted_jaccard:'Giảm thiên lệch đối với phim có quá nhiều diễn viên hoặc từ khóa.',hybrid:'Kết hợp quan hệ graph với độ giống nội dung; hiện là phương pháp thử nghiệm.'};
  $('#methodInput').addEventListener('change',event=>{$('#methodHelp').textContent=methodDescriptions[event.target.value];});
  $('#recommendForm').addEventListener('submit',async event=>{event.preventDefault();const form=event.currentTarget,status=$('#recommendStatus'),out=$('#recommendResults');setBusy(form,true);status.textContent='Đang phân tích các đường liên hệ…';out.innerHTML='';try{const rows=await api('/recommend',{method:'POST',body:JSON.stringify({movie_id:Number($('#movieIdInput').value),top_k:Number($('#topKInput').value),method:$('#methodInput').value})});status.textContent=rows.length?`Đã tạo ${rows.length} gợi ý có giải thích.`:'Không tìm thấy phim tương tự.';out.innerHTML=rows.map(x=>movieCard(x,'recommend')).join('');}catch(error){status.textContent=`Lỗi: ${error.message}`;}finally{setBusy(form,false);}});

})();
