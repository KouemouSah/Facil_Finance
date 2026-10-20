/* deck.js — construit la coquille de présentation autour des <section class="slide"> */
(function(){
  const ICONS={
    'i-anchor':'<circle cx="12" cy="5" r="2"/><path d="M12 7v13M5 12H3a9 9 0 0 0 18 0h-2"/><path d="M8 11l-3 1M16 11l3 1"/>',
    'i-ship':'<path d="M3 14l1.5 5h15L21 14"/><path d="M5 14V8h9l5 6"/><path d="M12 14V5"/>',
    'i-map':'<path d="M9 4L3 6v14l6-2 6 2 6-2V4l-6 2-6-2z"/><path d="M9 4v14M15 6v14"/>',
    'i-flow':'<rect x="3" y="3" width="6" height="5" rx="1"/><rect x="15" y="16" width="6" height="5" rx="1"/><path d="M6 8v5a3 3 0 0 0 3 3h6"/>',
    'i-box':'<path d="M21 8l-9-5-9 5 9 5 9-5z"/><path d="M3 8v8l9 5 9-5V8M12 13v8"/>',
    'i-pen':'<path d="M16 3l5 5L8 21H3v-5z"/><path d="M14 5l5 5"/>',
    'i-warn':'<path d="M12 3l9 16H3z"/><path d="M12 9v5M12 17h0"/>',
    'i-users':'<circle cx="9" cy="8" r="3"/><path d="M3 20a6 6 0 0 1 12 0"/><path d="M16 6a3 3 0 0 1 0 6"/>',
    'i-bolt':'<path d="M13 2L4 14h7l-1 8 9-12h-7z"/>',
    'i-check':'<path d="M5 12l5 5L20 6"/>',
    'i-coins':'<ellipse cx="9" cy="6" rx="6" ry="2.6"/><path d="M3 6v5c0 1.4 2.7 2.6 6 2.6s6-1.2 6-2.6"/><path d="M15 11.5c2.8.2 6 1.3 6 3v5c0 1.4-2.7 2.6-6 2.6-2 0-3.8-.4-5-1.1"/><path d="M3 11v5c0 1.4 2.7 2.6 6 2.6 1 0 2-.1 2.8-.3"/>',
    'i-shield':'<path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z"/><path d="M9 12l2 2 4-4"/>',
    'i-q':'<circle cx="12" cy="12" r="9"/><path d="M9.5 9.5a2.5 2.5 0 0 1 4.5 1.5c0 1.7-2.5 2-2.5 3.5M12 17h0"/>',
    'i-road':'<path d="M6 3L3 21M18 3l3 18M12 4v2M12 10v2M12 16v2"/>',
    'i-lock':'<rect x="4" y="10" width="16" height="11" rx="2"/><path d="M8 10V7a4 4 0 0 1 8 0v3"/>',
    'i-target':'<circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="4"/><circle cx="12" cy="12" r="1"/>',
    'i-gear':'<circle cx="12" cy="12" r="3"/><path d="M19 12a7 7 0 0 0-.1-1l2-1.6-2-3.4-2.3 1a7 7 0 0 0-1.7-1L14.5 2h-5l-.4 2.4a7 7 0 0 0-1.7 1l-2.3-1-2 3.4L3 11a7 7 0 0 0 0 2l-2 1.6 2 3.4 2.3-1a7 7 0 0 0 1.7 1L9.5 22h5l.4-2.4a7 7 0 0 0 1.7-1l2.3 1 2-3.4-2-1.6c.07-.33.1-.66.1-1z"/>',
    'i-db':'<ellipse cx="12" cy="6" rx="8" ry="3"/><path d="M4 6v12c0 1.7 3.6 3 8 3s8-1.3 8-3V6M4 12c0 1.7 3.6 3 8 3s8-1.3 8-3"/>',
    'i-layers':'<path d="M12 3l9 5-9 5-9-5z"/><path d="M3 13l9 5 9-5M3 17l9 5 9-5"/>',
    'i-server':'<rect x="3" y="4" width="18" height="7" rx="1"/><rect x="3" y="13" width="18" height="7" rx="1"/><path d="M7 7.5h0M7 16.5h0"/>',
    'i-scale':'<path d="M12 3v18M7 21h10M5 7h14M5 7l-2.5 6a3 3 0 0 0 5 0L5 7zM19 7l-2.5 6a3 3 0 0 0 5 0L19 7z"/><path d="M5 7l7-2 7 2"/>',
    'i-doc':'<path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/><path d="M14 3v5h5M9 13h6M9 17h6"/>',
    'i-mail':'<rect x="2" y="4" width="20" height="16" rx="2"/><path d="M2 6l10 7L22 6"/>',
    'i-calendar':'<rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/>',
    'i-warehouse':'<path d="M3 21V9l9-4 9 4v12"/><path d="M2 21h20"/><path d="M7 21v-7h10v7"/>',
    'i-truck':'<path d="M1 6h13v11H1z"/><path d="M14 9h4l3 3v5h-7z"/><circle cx="5.5" cy="18.5" r="1.8"/><circle cx="17.5" cy="18.5" r="1.8"/>',
    'i-stamp':'<path d="M5 21h14"/><path d="M5 18h14v-2a2 2 0 0 0-2-2h-2c0-2 2-3 2-5a3 3 0 0 0-6 0c0 2 2 3 2 5H7a2 2 0 0 0-2 2z"/>',
    'i-sign':'<path d="M3 17c5 0 4-10 7-10 2 0 1 6 3 6 1.5 0 1.5-3 3-3"/><path d="M3 21h18"/>',
    'i-chart':'<path d="M4 4v16h16"/><path d="M8 16v-5M12 16V8M16 16v-9"/>',
    /* --- finance (additif) --- */
    'i-trend-up':'<path d="M3 17l6-6 4 4 8-8"/><path d="M15 7h6v6"/>',
    'i-trend-down':'<path d="M3 7l6 6 4-4 8 8"/><path d="M15 17h6v-6"/>',
    'i-percent':'<path d="M19 5L5 19"/><circle cx="7.5" cy="7.5" r="2.5"/><circle cx="16.5" cy="16.5" r="2.5"/>',
    'i-wallet':'<path d="M3 7a2 2 0 0 1 2-2h13v3"/><rect x="3" y="7" width="18" height="12" rx="2"/><path d="M16 12h3v3h-3a1.5 1.5 0 0 1 0-3z"/>',
    'i-bank':'<path d="M3 10l9-6 9 6"/><path d="M5 10v8M10 10v8M14 10v8M19 10v8"/><path d="M3 21h18"/>',
    'i-receipt':'<path d="M5 3h14v17l-2.3-1.4-2.3 1.4-2.4-1.4-2.3 1.4L5 20z"/><path d="M8 8h8M8 12h8M8 16h6"/>',
    'i-pie':'<path d="M12 3a9 9 0 1 0 9 9h-9z"/><path d="M12 3v9h9a9 9 0 0 0-9-9z"/>',
    'i-cash':'<rect x="2" y="6" width="20" height="12" rx="2"/><circle cx="12" cy="12" r="3"/><path d="M6 9.5h.01M18 14.5h.01"/>',
    'i-chevL':'<path d="M15 6l-6 6 6 6"/>','i-chevR':'<path d="M9 6l6 6-6 6"/>','i-menu':'<path d="M4 6h16M4 12h16M4 18h16"/>',
    'i-expand':'<path d="M4 9V4h5M20 9V4h-5M4 15v5h5M20 15v5h-5"/>','i-print':'<path d="M6 9V3h12v6M6 18H4a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v3a2 2 0 0 1-2 2h-2M6 14h12v7H6z"/>','i-home':'<path d="M3 11l9-8 9 8M5 10v10h14V10"/>'
  };
  // inject defs
  const defs=document.createElementNS('http://www.w3.org/2000/svg','svg'); defs.style.display='none';
  let sym=''; for(const k in ICONS){ sym+=`<symbol id="${k}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">${ICONS[k]}</symbol>`; }
  defs.innerHTML=sym; document.body.appendChild(defs);

  const title=document.body.dataset.deck||'Présentation';
  const sub=document.body.dataset.sub||'Logistics Project';
  const logo=document.body.dataset.logo||'icon_facil.png';
  const sections=[...document.querySelectorAll('section.slide')];

  const app=document.createElement('div'); app.className='app';
  app.innerHTML=`<aside class="side">
    <div class="top"><img src="${logo}" alt=""/><div class="nm"><div class="t1">${title}</div><div class="t2">${sub}</div></div><button class="collapse-btn" id="cb" title="Replier"><svg style="width:16px;height:16px"><use href="#i-chevL"/></svg></button></div>
    <nav id="menu"></nav>
    <div class="home"><a href="index.html" target="_top"><svg style="width:14px;height:14px"><use href="#i-home"/></svg><span>Retour au hub</span></a></div>
  </aside>
  <div class="main" id="main"><div class="progress"><i id="bar"></i></div><div class="stage" id="stage"></div>
    <div class="ctrl"><button id="cN" title="Menu (N)"><svg><use href="#i-menu"/></svg></button><button id="cP" title="Précédent (←)"><svg><use href="#i-chevL"/></svg></button><span class="count" id="count">01 / ${String(sections.length).padStart(2,'0')}</span><button id="cX" title="Suivant (→)"><svg><use href="#i-chevR"/></svg></button><button id="cR" title="Imprimer / PDF"><svg><use href="#i-print"/></svg></button><button id="cF" title="Plein écran (F)"><svg><use href="#i-expand"/></svg></button></div>
  </div>`;
  document.body.appendChild(app);
  const stage=app.querySelector('#stage'); sections.forEach(s=>stage.appendChild(s));
  const menu=app.querySelector('#menu'),bar=app.querySelector('#bar'),count=app.querySelector('#count');
  let cur=0;
  sections.forEach((s,i)=>{const b=document.createElement('button');b.innerHTML=`<span class="ix">${String(i+1).padStart(2,'0')}</span><svg><use href="#${s.dataset.icon||'i-flow'}"/></svg><span class="lbl">${s.dataset.title||('Slide '+(i+1))}</span>`;b.title=s.dataset.title||'';b.onclick=()=>go(i);menu.appendChild(b);});
  const btns=[...menu.children];
  let _scaleRetry=0;
  function scaleActive(){const s=sections[cur];if(!s)return;const pad=app.classList.contains('present')?0:28;const w=stage.clientWidth,h=stage.clientHeight;
    // pendant une bascule plein écran, le stage peut être momentanément quasi nul :
    // ne pas appliquer un scale minuscule, réessayer jusqu'à ce que la taille se stabilise.
    if((w<40||h<40)&&_scaleRetry<40){_scaleRetry++;setTimeout(scaleActive,60);return;}
    _scaleRetry=0;const k=Math.min((w-pad)/1920,(h-pad)/1080);if(k>0)s.style.transform=`translate(-50%,-50%) scale(${k})`;}
  function go(i,push=true){cur=Math.max(0,Math.min(sections.length-1,i));sections.forEach((s,k)=>s.classList.toggle('show',k===cur));btns.forEach((b,k)=>b.classList.toggle('active',k===cur));count.textContent=`${String(cur+1).padStart(2,'0')} / ${String(sections.length).padStart(2,'0')}`;bar.style.width=(sections.length>1?cur/(sections.length-1)*100:0)+'%';if(btns[cur])btns[cur].scrollIntoView({block:'nearest'});requestAnimationFrame(scaleActive);if(push)history.replaceState(null,'','#'+(cur+1));}
  app.querySelector('#cb').onclick=()=>{app.classList.toggle('collapsed');setTimeout(scaleActive,260);};
  const toggleNav=()=>{if(app.classList.contains('present'))app.classList.remove('present');else app.classList.toggle('collapsed');setTimeout(scaleActive,260);};
  app.querySelector('#cN').onclick=toggleNav;app.querySelector('#cP').onclick=()=>go(cur-1);app.querySelector('#cX').onclick=()=>go(cur+1);app.querySelector('#cR').onclick=()=>window.print();
  function toggleFull(){if(!document.fullscreenElement){document.getElementById('main').requestFullscreen?.();app.classList.add('present');}else{document.exitFullscreen?.();app.classList.remove('present');}setTimeout(scaleActive,260);}
  app.querySelector('#cF').onclick=toggleFull;
  document.addEventListener('fullscreenchange',()=>{if(!document.fullscreenElement)app.classList.remove('present');setTimeout(scaleActive,200);});
  document.addEventListener('keydown',e=>{if(e.key==='ArrowRight'||e.key==='PageDown'||e.key===' '){go(cur+1);e.preventDefault();}else if(e.key==='ArrowLeft'||e.key==='PageUp')go(cur-1);else if(e.key==='Home')go(0);else if(e.key==='End')go(sections.length-1);else if(e.key.toLowerCase()==='f')toggleFull();else if(e.key.toLowerCase()==='n')toggleNav();});
  let tx=0;stage.addEventListener('touchstart',e=>tx=e.touches[0].clientX,{passive:true});stage.addEventListener('touchend',e=>{const dx=e.changedTouches[0].clientX-tx;if(Math.abs(dx)>60)go(cur+(dx<0?1:-1));},{passive:true});
  window.addEventListener('resize',scaleActive);
  const start=Math.max(1,Math.min(sections.length,parseInt(location.hash.replace('#',''))||1))-1;
  go(start,false);setTimeout(scaleActive,150);window.addEventListener('load',()=>setTimeout(scaleActive,200));
})();
