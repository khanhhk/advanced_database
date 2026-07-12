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
      if (item.entity_links) return `<div class="evidence-item"><strong>Bằng chứng ${index+1} · Liên kết thực thể</strong>${item.entity_links.map(link=>`<dl><dt>Dữ liệu nhập</dt><dd>${escapeHtml(link.input)}</dd><dt>Thực thể</dt><dd>${escapeHtml(link.canonical_name)}</dd><dt>Độ tin cậy</dt><dd>${Math.round(Number(link.confidence)*100)}%</dd></dl>`).join('')}</div>`;
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

  const movieCard = item => `<article class="movie-card"><div class="card-top"><h3>${escapeHtml(item.title)}</h3><span class="score">IDF ${Number(item.score).toFixed(2)}</span></div>${item.rating!=null?`<div class="rating">★ ${Number(item.rating).toFixed(1)}</div>`:''}${item.genres?.length?`<div class="chips">${item.genres.map(x=>`<span>${escapeHtml(x)}</span>`).join('')}</div>`:''}${item.explanation?`<p>${escapeHtml(item.explanation)}</p>`:''}</article>`;

  const movieName=$('#movieNameInput'), movieId=$('#movieIdInput'), suggestions=$('#movieSuggestions');
  let lookupTimer;
  const closeSuggestions=()=>{suggestions.hidden=true;suggestions.innerHTML='';};
  const chooseMovie=movie=>{movieName.value=`${movie.name}${movie.year?` (${movie.year})`:''}`;movieId.value=movie.id;closeSuggestions();$('#recommendStatus').textContent='';};
  movieName.addEventListener('input',()=>{movieId.value='';clearTimeout(lookupTimer);const query=movieName.value.trim();if(query.length<2){closeSuggestions();return;}lookupTimer=setTimeout(async()=>{try{const rows=(await api(`/entities/search?q=${encodeURIComponent(query)}&limit=8`)).filter(x=>x.type==='Movie');if(movieName.value.trim()!==query)return;suggestions.innerHTML=rows.map((x,i)=>`<button class="suggestion" type="button" role="option" data-index="${i}">${escapeHtml(x.name)}<span>${escapeHtml(x.year||'')}</span></button>`).join('');suggestions.hidden=!rows.length;suggestions.querySelectorAll('.suggestion').forEach((button,i)=>button.addEventListener('click',()=>chooseMovie(rows[i])));}catch{closeSuggestions();}},250);});
  movieName.addEventListener('keydown',event=>{if(event.key==='Escape')closeSuggestions();if(event.key==='ArrowDown'&&!suggestions.hidden){event.preventDefault();suggestions.querySelector('.suggestion')?.focus();}});
  suggestions.addEventListener('keydown',event=>{const buttons=[...suggestions.querySelectorAll('.suggestion')],index=buttons.indexOf(document.activeElement);if(event.key==='ArrowDown'){event.preventDefault();buttons[(index+1)%buttons.length]?.focus();}if(event.key==='ArrowUp'){event.preventDefault();(index<=0?movieName:buttons[index-1]).focus();}if(event.key==='Escape'){closeSuggestions();movieName.focus();}});
  document.addEventListener('click',event=>{if(!event.target.closest('.movie-picker'))closeSuggestions();});
  $('#recommendForm').addEventListener('submit',async event=>{event.preventDefault();const form=event.currentTarget,status=$('#recommendStatus'),out=$('#recommendResults');if(!movieId.value){status.textContent='Hãy chọn một phim trong danh sách gợi ý.';movieName.focus();return;}setBusy(form,true);status.textContent='Đang tìm các phim tương tự…';out.innerHTML='';try{const rows=await api('/recommend',{method:'POST',body:JSON.stringify({movie_id:Number(movieId.value),top_k:Number($('#topKInput').value)})});status.textContent=rows.length?`Đã tìm thấy ${rows.length} phim tương tự.`:'Không tìm thấy phim tương tự.';out.innerHTML=rows.map(movieCard).join('');}catch(error){status.textContent=`Lỗi: ${error.message}`;}finally{setBusy(form,false);}});

})();
