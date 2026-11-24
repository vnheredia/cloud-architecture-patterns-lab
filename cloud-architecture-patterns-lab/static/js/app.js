(() => {
  const labs = window.LABS || [];
  const grid = document.getElementById('lab-grid');
  const dashboard = document.getElementById('dashboard-view');
  const labView = document.getElementById('lab-view');
  const controlsBox = document.getElementById('controls');
  let activeLab = null;
  let selectedFilter = 'All';
  const params = {};

  const esc = (value) => String(value ?? '').replace(/[&<>"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));

  function renderDiagram(diagram) {
    const nodes = diagram.nodes || [];
    if (nodes[0] === 'Central Hub') {
      const width = 760, height = 220, hubX = width/2, hubY = 48, nodeW = 112, nodeH = 46;
      const spokeNodes = nodes.slice(1);
      const spacing = spokeNodes.length > 1 ? 620/(spokeNodes.length-1) : 0;
      const lines = spokeNodes.map((_,i)=>{const x=70+i*spacing;return `<path d="M ${hubX} ${hubY+nodeH/2} L ${x} 153" stroke="#52769e" stroke-width="1.8" fill="none"/>`;}).join('');
      const hub = `<g><rect x="${hubX-nodeW/2}" y="${hubY-nodeH/2}" width="${nodeW}" height="${nodeH}" rx="10" fill="#15253a" stroke="#61a5ff"/><circle cx="${hubX-nodeW/2+12}" cy="${hubY-nodeH/2+12}" r="3" fill="#61a5ff"/><text x="${hubX}" y="${hubY+4}" text-anchor="middle" fill="#dce8f8" font-size="12" font-family="DM Sans, sans-serif">Central Hub</text></g>`;
      const spokes = spokeNodes.map((name,i)=>{const x=70+i*spacing;return `<g><rect x="${x-nodeW/2}" y="${153-nodeH/2}" width="${nodeW}" height="${nodeH}" rx="9" fill="#15253a" stroke="#56d3a6" stroke-opacity=".75"/><circle cx="${x-nodeW/2+12}" cy="${153-nodeH/2+12}" r="3" fill="#56d3a6"/><text x="${x}" y="157" text-anchor="middle" fill="#dce8f8" font-size="11" font-family="DM Sans, sans-serif">${esc(name)}</text></g>`;}).join('');
      return `<svg viewBox="0 0 ${width} ${height}" role="img" aria-label="Hub and spoke network diagram">${lines}${hub}${spokes}</svg>`;
    }
    const w = Math.max(700, nodes.length * 170);
    const h = 190;
    const boxW = Math.min(145, Math.max(105, w / Math.max(1, nodes.length) - 24));
    const positions = nodes.map((_, i) => ({x: 35 + i * (w - 70) / Math.max(1, nodes.length - 1), y: h/2}));
    const edges = (diagram.edges || []).map(([from,to]) => {
      const a=positions[from], b=positions[to]; if(!a || !b) return '';
      const start=a.x+boxW/2+4, end=b.x-boxW/2-8;
      return `<path d="M ${start} ${a.y} L ${end} ${b.y}" stroke="#52769e" stroke-width="2" fill="none" marker-end="url(#arrow)"/>`;
    }).join('');
    const boxes = nodes.map((node,i) => {
      const p=positions[i]; const color=['#61a5ff','#56d3a6','#b39bff','#f5ae67','#66d0e2'][i%5];
      const label=esc(node); const maxChars=Math.floor(boxW/8); const lines=label.length>maxChars?[label.slice(0,maxChars),label.slice(maxChars,maxChars*2)]:[label];
      const txt=lines.map((line,j)=>`<text x="${p.x}" y="${p.y+5+(j-(lines.length-1)/2)*14}" text-anchor="middle" fill="#dce8f8" font-size="11" font-family="DM Sans, sans-serif">${line}</text>`).join('');
      return `<g><rect x="${p.x-boxW/2}" y="${p.y-30}" width="${boxW}" height="60" rx="10" fill="#15253a" stroke="${color}" stroke-opacity=".7"/><circle cx="${p.x-boxW/2+13}" cy="${p.y-17}" r="3" fill="${color}"/>${txt}</g>`;
    }).join('');
    return `<svg viewBox="0 0 ${w} ${h}" role="img" aria-label="Architecture flow"><defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L0,6 L6,3 z" fill="#52769e"/></marker></defs>${edges}${boxes}</svg>`;
  }

  function diagramForActiveLab() {
    if (!activeLab) return activeLab?.diagram;
    const diagram = JSON.parse(JSON.stringify(activeLab.diagram || {}));
    if (activeLab.id === 5) {
      const backends = Math.max(2, Math.min(6, Number(params.backend_count || 3)));
      diagram.nodes = ['Client', 'API Entry / Proxy', ...Array.from({length: backends}, (_,i)=>`Backend ${i+1}`)];
      diagram.edges = [[0,1], ...Array.from({length: backends}, (_,i)=>[1,i+2])];
      diagram.note = `Requests are routed from the entry point to ${backends} backend node(s) using Round Robin in the simulation.`;
    }
    if (activeLab.id === 6) {
      const spokes = Math.max(2, Math.min(6, Number(params.spoke_count || 4)));
      diagram.nodes = ['Central Hub', ...Array.from({length:spokes}, (_,i)=>`Spoke ${i+1}`)];
      diagram.edges = Array.from({length:spokes}, (_,i)=>[0,i+1]);
      diagram.note = `${spokes} spoke network(s) connect to the hub. Spoke-to-spoke traffic is ${params.allow_spoke_to_spoke === 'false' ? 'blocked by policy' : 'illustrated as permitted through the hub'}.`;
    }
    return diagram;
  }
  function updateDiagram() {
    if (!activeLab) return;
    const diagram = diagramForActiveLab();
    document.getElementById('diagram').innerHTML=renderDiagram(diagram);
    document.getElementById('diagram-note').textContent=diagram.note||'';
  }

  function renderControls(lab) {
    controlsBox.innerHTML = '';
    (lab.controls || []).forEach(control => {
      const defaultValue = control.default ?? (control.options ? control.options[0].value : '');
      params[control.name] = String(defaultValue);
      const group = document.createElement('div'); group.className='control-group';
      const label = document.createElement('label'); label.className='control-label'; label.innerHTML=`<span>${esc(control.label)}</span><span class="control-value" id="value-${control.name}">${esc(defaultValue)}</span>`;
      let input;
      if(control.type==='select') {
        input=document.createElement('select'); input.className='select-control';
        (control.options||[]).forEach(option=>{const opt=document.createElement('option');opt.value=option.value;opt.textContent=option.label;input.appendChild(opt);});
        input.value=String(defaultValue);
      } else if(control.type==='text') {
        input=document.createElement('input');input.type='text';input.className='text-control';input.maxLength=80;input.value=defaultValue;
      } else {
        input=document.createElement('input');input.type='range';input.className='control-range';input.min=control.min;input.max=control.max;input.step=control.step||1;input.value=defaultValue;
      }
      input.name=control.name;
      input.addEventListener('input',()=>{params[control.name]=input.value;const val=document.getElementById(`value-${control.name}`);if(val)val.textContent=input.value;if(activeLab && (activeLab.id===5 || activeLab.id===6)) updateDiagram();});
      group.appendChild(label);group.appendChild(input);controlsBox.appendChild(group);
    });
  }

  function openLab(id) {
    activeLab=labs.find(l=>l.id===Number(id));if(!activeLab)return;
    dashboard.classList.add('hidden');labView.classList.remove('hidden');document.getElementById('crumb-current').textContent=activeLab.name;
    document.getElementById('detail-icon').textContent=activeLab.icon;
    document.getElementById('detail-category').textContent=`${activeLab.category.toUpperCase()} PATTERN`;
    document.getElementById('detail-name').textContent=activeLab.name;
    document.getElementById('detail-summary').textContent=activeLab.summary;
    document.getElementById('description').textContent=activeLab.description;
    document.getElementById('how').textContent=activeLab.how;
    document.getElementById('use').textContent=activeLab.use;
    document.getElementById('aws').textContent=activeLab.aws;
    updateDiagram();
    document.getElementById('takeaway').textContent=activeLab.summary;
    document.getElementById('takeaway-title').textContent=`Why ${activeLab.name} matters`;
    document.getElementById('detail-status').innerHTML='<i></i> READY TO RUN';
    renderControls(activeLab);clearOutput();window.scrollTo({top:0,behavior:'smooth'});
  }

  function clearOutput() {
    document.getElementById('empty-output').classList.remove('hidden');
    document.getElementById('result-content').classList.add('hidden');
    document.getElementById('empty-output').querySelector('strong').textContent='Ready when you are';
    document.getElementById('empty-output').querySelector('span').textContent='Adjust the scenario, then run the demo to see the pattern in action.';
    document.getElementById('detail-status').innerHTML='<i></i> READY TO RUN';
  }
  function showResult(data) {
    document.getElementById('empty-output').classList.add('hidden');
    const result=document.getElementById('result-content');result.classList.remove('hidden');
    document.getElementById('result-summary').textContent=data.summary||'Simulation completed.';
    const metrics=document.getElementById('metrics');metrics.innerHTML='';
    Object.entries(data.metrics||{}).forEach(([key,value])=>{const card=document.createElement('div');card.className='metric';card.innerHTML=`<small>${esc(key.replaceAll('_',' ').toUpperCase())}</small><strong>${esc(value)}</strong>`;metrics.appendChild(card);});
    const logs=document.getElementById('logs');logs.innerHTML='';
    (data.logs||[]).forEach(item=>{const entry=document.createElement('div');entry.className='log-entry';entry.innerHTML=`<span class="log-time">${esc(item.time||'--:--:--')}</span><span class="log-level ${esc(item.level||'INFO')}">${esc(item.level||'INFO')}</span><span class="log-message">${esc(item.message)}</span>`;logs.appendChild(entry);});
    document.getElementById('log-count').textContent=`${(data.logs||[]).length} EVENTS`;
    const details=document.getElementById('result-details');details.innerHTML='';
    (data.details||[]).forEach(item=>{const row=document.createElement('div');row.className='detail-item';row.innerHTML=`<strong>${esc(item.service||item.server||'Detail')}</strong><span>${esc(item.result||`${item.requests} requests · ${item.response_ms??''} ms`)}</span>`;details.appendChild(row);});
    const status=document.getElementById('detail-status');status.innerHTML=`<i></i> ${esc(data.status||'COMPLETED')}`;
  }
  async function runSimulation() {
    if(!activeLab)return;
    const btn=document.getElementById('run-btn');btn.disabled=true;btn.innerHTML='<span>◌</span> Running…';
    document.getElementById('detail-status').innerHTML='<i></i> RUNNING';
    try {
      const response=await fetch(`/api/lab/${activeLab.id}/run`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(params)});
      const data=await response.json();if(!response.ok||!data.success)throw new Error(data.error||'Simulation failed');showResult(data);
    } catch(err) {
      document.getElementById('empty-output').classList.remove('hidden');document.getElementById('result-content').classList.add('hidden');
      document.getElementById('empty-output').querySelector('strong').textContent='Could not run simulation';document.getElementById('empty-output').querySelector('span').textContent=err.message;
      document.getElementById('detail-status').innerHTML='<i></i> ERROR';
    } finally {btn.disabled=false;btn.innerHTML='<span>▶</span> Run simulation';}
  }
  function backHome(){labView.classList.add('hidden');dashboard.classList.remove('hidden');document.getElementById('crumb-current').textContent='Overview';window.scrollTo({top:0,behavior:'smooth'});}
  function applyFilters(){const term=document.getElementById('search').value.toLowerCase().trim();let visible=0;document.querySelectorAll('.lab-card').forEach(card=>{const matchFilter=selectedFilter==='All'||card.dataset.category===selectedFilter;const matchSearch=card.dataset.name.includes(term)||card.textContent.toLowerCase().includes(term);card.style.display=matchFilter&&matchSearch?'flex':'none';if(matchFilter&&matchSearch)visible++;});let no=document.querySelector('.no-results');if(visible===0){if(!no){no=document.createElement('div');no.className='no-results';no.textContent='No labs match your search. Try another term or category.';grid.appendChild(no);}}else if(no)no.remove();}
  document.querySelectorAll('[data-open]').forEach(btn=>btn.addEventListener('click',()=>openLab(btn.dataset.open)));
  document.getElementById('back-btn').addEventListener('click',backHome);
  document.getElementById('config-form').addEventListener('submit',e=>{e.preventDefault();runSimulation();});
  document.getElementById('reset-btn').addEventListener('click',()=>{if(activeLab){renderControls(activeLab);clearOutput();}});
  document.getElementById('clear-results').addEventListener('click',clearOutput);
  document.getElementById('explore-btn').addEventListener('click',()=>document.getElementById('lab-grid').scrollIntoView({behavior:'smooth'}));
  document.getElementById('view-all').addEventListener('click',e=>{e.preventDefault();selectedFilter='All';document.querySelectorAll('.filter').forEach(f=>f.classList.toggle('active',f.dataset.filter==='All'));applyFilters();document.getElementById('lab-grid').scrollIntoView({behavior:'smooth'});});
  document.querySelectorAll('.filter').forEach(btn=>btn.addEventListener('click',()=>{selectedFilter=btn.dataset.filter;document.querySelectorAll('.filter').forEach(f=>f.classList.toggle('active',f===btn));applyFilters();}));
  document.getElementById('search').addEventListener('input',applyFilters);
  document.querySelectorAll('[data-nav]').forEach(btn=>btn.addEventListener('click',()=>{if(btn.dataset.nav==='home')backHome();else{selectedFilter='All';document.querySelectorAll('.filter').forEach(f=>f.classList.toggle('active',f.dataset.filter==='All'));applyFilters();document.getElementById('lab-grid').scrollIntoView({behavior:'smooth'});}}));
})();
