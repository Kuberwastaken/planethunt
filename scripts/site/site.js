/* Presentation only: all plotted measurements come from committed evidence exports. */
(() => {
'use strict';
document.documentElement.classList.add('js');
const $ = id => document.getElementById(id);
const V = 'analysis/validation-20261011/';
const palette = {ink:'#ffffff', muted:'#aaaaaa', line:'#333333', white:'#ffffff', sage:'#aaaaaa', yellow:'#ffffff'};
const escape = value => String(value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
let dataPromise;
function getData() {
  if (!dataPromise) dataPromise = fetch('docs/site-data.json').then(r => {if(!r.ok) throw new Error('data'); return r.json();}).catch(e => {dataPromise = null; throw e;});
  return dataPromise;
}
function svgPlot({title, xr, yr, xticks, yticks, xlabel, ylabel}) {
  const w=Math.max(320,Math.round($('signal-chart').clientWidth)),compact=w<600,h=compact?310:350,L=compact?64:94,R=compact?12:24,T=30,B=compact?58:64;
  if(compact) xticks=xticks.filter((_,i)=>i%2===0);
  const X=x=>L+(x-xr[0])/(xr[1]-xr[0])*(w-L-R);
  const Y=y=>h-B-(y-yr[0])/(yr[1]-yr[0])*(h-T-B);
  const parts=[`<svg viewBox="0 0 ${w} ${h}" role="img" aria-labelledby="dynamic-chart-title dynamic-chart-desc"><title id="dynamic-chart-title">${escape(title)}</title><desc id="dynamic-chart-desc">${escape(ylabel)} against ${escape(xlabel)}. Data download and description below.</desc><defs><clipPath id="plot-clip"><rect x="${L}" y="${T}" width="${w-L-R}" height="${h-T-B}"/></clipPath></defs>`];
  const text=(x,y,t,anchor='middle',color=palette.muted,size=13)=>`<text x="${x}" y="${y}" text-anchor="${anchor}" fill="${color}" font-family="IBM Plex Mono,monospace" font-size="${size}">${escape(t)}</text>`;
  yticks.forEach(y=>{parts.push(`<path d="M${L} ${Y(y)}H${w-R}" stroke="${y===0?'#666666':palette.line}"/>`);parts.push(text(L-12,Y(y)+5,compact&&Math.abs(y)>=1000?`${y/1000}k`:y.toLocaleString(),'end'));});
  xticks.forEach(x=>{parts.push(text(X(x),h-B+27,x));});
  parts.push(text((L+w-R)/2,h-10,xlabel));
  parts.push(`<text x="18" y="${(T+h-B)/2}" transform="rotate(-90 18 ${(T+h-B)/2})" text-anchor="middle" fill="${palette.muted}" font-size="12" font-family="IBM Plex Mono,monospace">${escape(ylabel)}</text>`);
  return {X,Y,parts,bounds:{x:L,y:T,width:w-L-R,height:h-T-B},finish:()=>parts.join('')+'</svg>'};
}
let currentView='fold', renderTicket=0;
async function renderSignal() {
  const ticket=++renderTicket;
  try {
    const d=await getData(); if(ticket!==renderTicket)return;
    if($('quarter').options.length===1) [...new Set(d.light.map(r=>r[2]))].sort((a,b)=>a-b).forEach(q=>{const o=new Option(`Quarter ${q}`,String(q));$('quarter').add(o);});
    let p,caption,filename,meta,denseRows;
    const hits=[];
    const hit=(x,y,title,rows)=>hits.push(`<rect class="chart-hit" x="${p.X(x)-8}" y="${p.Y(y)-8}" width="16" height="16" fill="transparent" data-chart-detail="${escape(JSON.stringify([title,rows]))}"/>`);
    $('event-controls').hidden=currentView!=='events'; $('light-controls').hidden=currentView!=='light';
    if(currentView==='fold') {
      p=svgPlot({title:'Folded transit of KIC 5689121',xr:[-8.5,8.5],yr:[-3400,1200],xticks:[-8,-6,-4,-2,0,2,4,6,8],yticks:[-3000,-2000,-1000,0,1000],xlabel:'Hours from the middle of the transit',ylabel:'Change in brightness (ppm)'});
      p.parts.push('<g clip-path="url(#plot-clip)">');
      d.fold.forEach(([x,y,e])=>{p.parts.push(`<path d="M${p.X(x)} ${p.Y(y-e)}V${p.Y(y+e)}" stroke="#666666" stroke-width="1.2"/><circle cx="${p.X(x)}" cy="${p.Y(y)}" r="3.5" fill="${palette.sage}"><title>${x.toFixed(2)} hours: ${Math.round(y)} ± ${Math.round(e)} ppm</title></circle>`);});
      p.parts.push(`<path d="${d.transitModel.map(([x,y],i)=>`${i?'L':'M'}${p.X(x).toFixed(2)},${p.Y(y).toFixed(2)}`).join('')}" fill="none" stroke="${palette.white}" stroke-width="2.4"/></g>`);
      d.fold.forEach(([x,y,e])=>hit(x,y,'15-minute transit bin',[['Hours from mid-transit',x.toFixed(3)],['Flux',`${y.toFixed(2)} ppm`],['Uncertainty',`±${e.toFixed(2)} ppm`]]));
      caption='Stack the observations on a 13.77-day clock: a dip emerges. White line: transit model. Bars: uncertainty.';
      filename='kic5689121_folded_15min_bins.csv';meta=`${d.fold.length} bins · 15-minute intervals`;
      $('signal-legend').innerHTML='<span><i></i> Kepler measurements</span><span><i class="model"></i> Transit model</span>';
    } else if(currentView==='events') {
      const rows=d.events.filter(r=>!$('heldout-only').checked||r[3]);
      p=svgPlot({title:'Individual event depths, 74 measured events',xr:[-50,28],yr:[-3000,11000],xticks:[-48,-36,-24,-12,0,12,24],yticks:[-2000,0,2000,4000,6000,8000,10000],xlabel:'Transit number relative to the saved reference epoch',ylabel:'Measured transit depth (ppm)'});
      p.parts.push(`<path d="M${p.X(-50)} ${p.Y(2400)}H${p.X(28)}" stroke="${palette.white}" stroke-dasharray="4 5"/><g clip-path="url(#plot-clip)">`);
      rows.forEach(([x,y,e,hold,q])=>{const c=hold?palette.yellow:palette.sage;p.parts.push(`<path d="M${p.X(x)} ${p.Y(y-e)}V${p.Y(y+e)}" stroke="${c}" opacity=".55"/><circle cx="${p.X(x)}" cy="${p.Y(y)}" r="4" fill="${c}"><title>Event ${x}, Q${q}${hold?', reserved quarter':''}: ${Math.round(y)} ± ${Math.round(e)} ppm</title></circle>`);});
      rows.forEach(([x,y,e,hold,q])=>hit(x,y,`Event ${x} / Q${q}`,[['Depth',`${y.toFixed(2)} ppm`],['Uncertainty',`±${e.toFixed(2)} ppm`],['Selection',hold?'Reserved':'Search']]));
      p.parts.push('</g>');caption='The dip returns across many events, but each depth is noisy. White points come from the held-back quarters; the dashed line marks 2,400 ppm.';
      filename='kic5689121_per_transit_depths.csv';meta=`${rows.length} events shown · error bars ±1σ`;
      $('signal-legend').innerHTML='<span><i></i> Discovery quarters</span><span><i style="background:#ffffff"></i> Reserved quarters</span>';
    } else {
      const q=$('quarter').value,rows=d.light.filter(r=>q==='all'||r[2]===Number(q));
      denseRows=rows;
      const lo=rows[0][0],hi=rows[rows.length-1][0],xr=[lo-1,hi+1];
      const xticks=Array.from({length:6},(_,i)=>Math.round(lo+(hi-lo)*i/5));
      p=svgPlot({title:`Kepler light curve ${q==='all'?'all quarters':`quarter ${q}`}`,xr,yr:[-7500,7500],xticks,yticks:[-6000,-3000,0,3000,6000],xlabel:'Time in BTJD (BJD TDB − 2,457,000)',ylabel:'Detrended brightness (ppm)'});
      for(const transit of [false,true]) {const path=rows.filter(r=>r[3]===transit).map(([t,y])=>`M${p.X(t).toFixed(1)},${p.Y(y).toFixed(1)}h.1`).join('');p.parts.push(`<path clip-path="url(#plot-clip)" d="${path}" stroke="${transit?palette.white:palette.sage}" stroke-width="${q==='all'?1.5:2.3}" stroke-linecap="round" opacity="${transit?.9:.4}"/>`);}
      const outside=rows.filter(r=>Math.abs(r[1])>7500).length;
      caption=`Every point is one brightness measurement. The long record lets us test whether the same timing holds years later. ${outside} points outside ±7,500 ppm are clipped; the CSV retains all values.`;
      filename='kic5689121_lightcurve_psf.csv';meta=`${rows.length.toLocaleString()} measurements · ${q==='all'?'2009–2013':`quarter ${q}`}`;
      $('signal-legend').innerHTML='<span><i></i> Original cadences</span><span><i style="background:#ffffff"></i> In-transit selection</span>';
    }
    window.chartInspector.hide();p.parts.push(...hits);$('signal-chart').innerHTML=p.finish();
    const svg=$('signal-chart').querySelector('svg');
    if(denseRows)window.chartInspector.register(svg,{rows:denseRows,X:p.X,Y:p.Y,bounds:p.bounds});
    window.chartInspector.enhance(svg);$('signal-caption').textContent=caption;$('chart-meta').textContent=meta;$('signal-download').href=V+'post/data/'+filename;
    document.querySelectorAll('[data-view]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.view===currentView)));
  } catch(e) {$('chart-meta').textContent='Interactive data could not load. The saved chart and CSV remain available; select a view to retry.';}
}
document.querySelectorAll('[data-view]').forEach(b=>b.addEventListener('click',()=>{currentView=b.dataset.view;renderSignal();}));
$('heldout-only').addEventListener('change',renderSignal);$('quarter').addEventListener('change',renderSignal);
// Load only when approaching the plot; the static SVG remains available before then.
const signalObserver=new IntersectionObserver(entries=>{if(entries.some(e=>e.isIntersecting)){renderSignal();signalObserver.disconnect();}},{rootMargin:'200px'});signalObserver.observe($('signal'));

const surveys={
 ps1:{src:V+'post/source_images/ps1_2arcmin.png',fov:.0333,hips:'CDS/P/PanSTARRS/DR1/color-z-zg-g',name:'Pan-STARRS1 DR1',width:'2′',scale:'20″',bar:20,credit:'Pan-STARRS1 / STScI via CDS',desc:'The neighbour is 2.1× brighter than the host in Gaia G.'},
 wide:{src:V+'post/source_images/ps1_10arcmin.png',fov:.1667,hips:'CDS/P/PanSTARRS/DR1/color-z-zg-g',name:'Pan-STARRS1 DR1',width:'10′',scale:'1′',bar:60,credit:'Pan-STARRS1 / STScI via CDS',desc:'The surrounding 10′ field in Lyra.'},
 dss:{src:V+'post/source_images/dss2_15arcmin.png',fov:.25,hips:'CDS/P/DSS2/color',name:'DSS2 photographic plates',width:'15′',scale:'2′',bar:120,credit:'DSS2 / STScI, AURA, Palomar, UK Schmidt via CDS',desc:'Older photographic plates; insufficient resolution to exclude a close companion.'},
 mass:{src:'docs/sky/2mass-10arcmin-clean.png',fov:.1667,hips:'CDS/P/2MASS/color',name:'2MASS near-infrared',width:'10′',scale:'1′',bar:60,credit:'2MASS / UMass, IPAC-Caltech via CDS',desc:'The field in near-infrared J, H and K bands.'},
 wise:{src:'docs/sky/allwise-10arcmin-clean.png',fov:.1667,hips:'CDS/P/allWISE/color',name:'AllWISE mid-infrared',width:'10′',scale:'1′',bar:60,credit:'AllWISE / NASA, JPL-Caltech, UCLA via CDS',desc:'The close pair is unresolved at this mid-infrared resolution.'}
};
let survey='ps1';
function renderSky(){
 const s=surveys[survey],span=s.fov*3600,neighbor=500+7.1/span*1000,r=survey==='ps1'?36:14;
 $('survey-image').src=s.src;$('survey-image').alt=`${s.name} survey centred on KIC 5689121, ${s.width} wide, north up and east left`;
 $('survey-overlay').innerHTML=`<g ${$('sky-labels').checked?'':'visibility="hidden"'}><circle cx="500" cy="500" r="${r}" fill="none" stroke="${palette.white}" stroke-width="2"/><circle cx="${neighbor}" cy="500" r="${survey==='ps1'?30:10}" fill="none" stroke="${palette.sage}" stroke-width="2" stroke-dasharray="5 5"/></g><g stroke="${palette.ink}" stroke-width="2" fill="none"><path d="M50 920h${s.bar/span*1000}M920 120V65m0 55h-55"/></g><g fill="${palette.ink}" font-size="18" font-family="IBM Plex Mono,monospace"><text x="50" y="903">${s.scale}</text><text x="912" y="48">N</text><text x="840" y="126">E</text></g>`;
 $('survey-description').textContent=s.desc;$('survey-caption').textContent=`${s.credit}. Solid: host. Dashed: neighbour. Markers show catalogue positions.`;
 $('survey-source').href='https://alasky.cds.unistra.fr/hips-image-services/hips2fits?'+new URLSearchParams({hips:s.hips,width:1200,height:1200,fov:s.fov,projection:'TAN',coordsys:'icrs',ra:285.907827,dec:40.941988,format:'png'});
 document.querySelectorAll('[data-survey]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.survey===survey)));
}
document.querySelectorAll('[data-survey]').forEach(b=>b.addEventListener('click',()=>{survey=b.dataset.survey;renderSky();}));$('sky-labels').addEventListener('change',renderSky);renderSky();
$('survey-colour').addEventListener('click',()=>{const active=$('survey-colour').getAttribute('aria-pressed')!=='true';$('survey-colour').setAttribute('aria-pressed',String(active));$('survey-frame').classList.toggle('show-colour',active);$('survey-colour').textContent=active?'Monochrome display':'Original colour';});
const dialog=$('image-dialog');
const expandIcon='<svg data-ui-icon viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M9 4H4v5m11-5h5v5M4 15v5h5m11-5v5h-5" fill="none" stroke="currentColor" stroke-width="1.5"/></svg>';
const chartSVG=fig=>fig.querySelector('svg:not([data-ui-icon])');
// Native dialog gives Escape handling, focus trapping and focus restoration.
document.querySelectorAll('figure').forEach(fig=>{
 if(!chartSVG(fig)||fig.classList.contains('hero-figure')||fig.querySelector('#survey-frame'))return;
 const button=document.createElement('button');button.className='figure-expand';button.innerHTML=expandIcon;
 const label='Enlarge '+(fig.querySelector('h3,svg title')?.textContent||'chart');button.setAttribute('aria-label',label);button.title=label;
 // Give every figure a single tool rail; keep controls outside horizontal plot scrolling.
 let rail=fig.querySelector('.plate-label')||fig.closest('.transit-plate')?.querySelector('.plate-label');
 if(!rail){rail=document.createElement('div');rail.className='figure-heading';const heading=fig.querySelector('h3');if(heading)rail.append(heading);fig.prepend(rail);}
 if(fig.querySelector('#signal-chart'))rail.append($('signal-download'));
 rail.append(button);fig.classList.add('has-expand');
 button.addEventListener('click',()=>{const source=chartSVG(fig);if(!source)return;const clone=source.cloneNode(true);clone.style.setProperty('--chart-reveal',1);clone.classList.add('expanded-chart');clone.querySelectorAll('[id]').forEach(el=>{const old=el.id;el.id='dialog-'+old;clone.querySelectorAll('[clip-path]').forEach(c=>{if(c.getAttribute('clip-path')===`url(#${old})`)c.setAttribute('clip-path',`url(#dialog-${old})`);});});clone.removeAttribute('aria-labelledby');clone.setAttribute('aria-label',source.querySelector('title')?.textContent||'Enlarged chart');dialog.querySelector('.dialog-media').replaceChildren(clone);window.chartInspector.copy(source,clone);$('dialog-title').textContent=fig.querySelector('h3,svg title')?.textContent||'Measurement';$('dialog-caption').textContent=fig.querySelector('figcaption')?.textContent||'';dialog.showModal();});
});
let resizeTimer;addEventListener('resize',()=>{clearTimeout(resizeTimer);resizeTimer=setTimeout(()=>{if(dataPromise)renderSignal();},160);});
$('enlarge-sky').innerHTML=expandIcon;$('survey-frame').append($('enlarge-sky'));
$('enlarge-sky').addEventListener('click',()=>{const copy=$('survey-frame').cloneNode(true);copy.removeAttribute('id');copy.querySelector('.figure-expand')?.remove();copy.querySelectorAll('[id]').forEach(el=>el.removeAttribute('id'));dialog.querySelector('.dialog-media').replaceChildren(copy);$('dialog-title').textContent=surveys[survey].name;$('dialog-caption').textContent=$('survey-caption').textContent;dialog.showModal();});
$('close-dialog').addEventListener('click',()=>dialog.close());dialog.addEventListener('click',e=>{if(e.target===dialog){const r=dialog.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)dialog.close();}});

document.querySelectorAll('[data-fpp]').forEach(button=>button.addEventListener('click',()=>{
 const hypothetical=button.dataset.fpp==='hypothetical',v=hypothetical?2.694156338609677:6.88513079714933;
 $('fpp-value').innerHTML=`${v.toFixed(1)}<span>%</span>`;$('fpp-bar').setAttribute('d',`M20 65H${20+v/10*480}`);
 $('fpp-scale').setAttribute('aria-label',`${hypothetical?'Hypothetical imaging scenario':'Available evidence'}: ${v.toFixed(1)} percent false-positive probability, above 1.5 percent threshold`);
 $('fpp-caption').textContent=hypothetical?'With hypothetical sharper imaging, the model gives 2.2–3.2% in alternative scenarios. That still misses the 1.5% threshold. These images have not been obtained.':'Modelled false-positive probability: 6.9%. Mostly a planet on a hidden companion; validation requires below 1.5%.';
 document.querySelectorAll('[data-fpp]').forEach(b=>b.setAttribute('aria-pressed',String(b===button)));
}));
// Colour appears on interaction; the first static presentation remains monochrome.
const planetImages=[...document.querySelectorAll('.planet-image')];
let planetScrollStarted=false;
const planetObserver=new IntersectionObserver(entries=>entries.forEach(entry=>entry.target.classList.toggle('is-revealed',planetScrollStarted && entry.isIntersecting)),{rootMargin:'-20% 0px -20% 0px',threshold:.25});
planetImages.forEach(el=>planetObserver.observe(el));
window.addEventListener('scroll',()=>{planetScrollStarted=true;planetImages.forEach(el=>{planetObserver.unobserve(el);planetObserver.observe(el);});},{once:true,passive:true});
planetImages.forEach(button=>button.addEventListener('click',()=>{const img=button.querySelector('img').cloneNode(true);img.removeAttribute('srcset');img.removeAttribute('sizes');img.className='planet-detail';dialog.querySelector('.dialog-media').replaceChildren(img);$('dialog-title').textContent=button.dataset.planetImage+' / artist’s interpretation';$('dialog-caption').textContent=button.closest('.planet-card').querySelector('.planet-copy>p').textContent;dialog.showModal();}));
$('planet-colour').addEventListener('click',()=>{const active=$('planet-colour').getAttribute('aria-pressed')!=='true';$('planet-colour').setAttribute('aria-pressed',String(active));document.querySelector('.planet-gallery').classList.toggle('colour-on',active);$('planet-colour').textContent=active?'Colour follows interaction':'Keep colour on';});
function updateTemperature(){const a=Number($('albedo').value);$('albedo-output').textContent=a+'%';$('temperature').textContent=Math.round(417.4280973054799*Math.pow(1-a/100,.25))+' K';}
let albedoManual=false;
['pointerdown','focus','input'].forEach(type=>$('albedo').addEventListener(type,()=>{albedoManual=true;}));
$('albedo').addEventListener('input',updateTemperature);

let files=null,limit=30,fileLoading=false;
async function loadFiles(){
 if(files){renderFiles();return;}if(fileLoading)return;fileLoading=true;$('file-count').textContent='Loading the checksummed inventory…';
 try{const responses=await Promise.all(['inventory.json','analysis/bulk-files.json'].map(async u=>{const r=await fetch(u);if(!r.ok)throw Error(u);return r.json();}));files=[...responses[0].files.map(f=>({...f,kind:'repo'})),...responses[1].files.map(f=>({...f,kind:'bulk'}))];renderFiles();}
 catch(e){$('file-count').textContent='File index could not load. Use the full inventory link, or close and reopen to retry.';}finally{fileLoading=false;}
}
function renderFiles(){if(!files)return;const query=$('file-query').value.trim().toLowerCase(),kind=$('file-type').value,terms=query.split(/\s+/).filter(Boolean);const filtered=files.filter(f=>(kind==='all'||kind===f.kind)&&terms.every(q=>f.path.toLowerCase().includes(q)));const list=$('file-list');list.replaceChildren();filtered.slice(0,limit).forEach(f=>{const item=document.createElement('li');if(f.kind==='repo'){const a=document.createElement('a');a.href=f.path.split('/').map(encodeURIComponent).join('/');a.textContent=f.path;item.append(a);}else{const path=document.createElement('div');path.className='bulk-path';path.textContent=f.path;item.append(path);const a=document.createElement('a');a.href='https://github.com/Kuberwastaken/planethunt/releases/tag/evidence-20261010';a.textContent='Find in the source release archives ↗';item.append(a);}const meta=document.createElement('div');meta.className='file-meta';meta.textContent=`${f.kind==='repo'?'Repository':'Archive'} · ${(f.bytes/1024).toLocaleString(undefined,{maximumFractionDigits:1})} KB · SHA-256 ${f.sha256}`;item.append(meta);list.append(item);});$('file-count').textContent=filtered.length?`Showing ${Math.min(limit,filtered.length)} of ${filtered.length.toLocaleString()} matching files (${files.length.toLocaleString()} total).`:'No matching files. Try a target number or a shorter term.';$('file-more').hidden=limit>=filtered.length;}
$('file-explorer').addEventListener('toggle',()=>{if($('file-explorer').open)loadFiles();});$('file-query').addEventListener('input',()=>{limit=30;renderFiles();});$('file-type').addEventListener('change',()=>{limit=30;renderFiles();});$('file-more').addEventListener('click',()=>{limit+=30;renderFiles();});
// One scroll-linked movement, only while the footer is near the viewport.
const footer=document.querySelector('.site-footer'),reduceMotion=matchMedia('(prefers-reduced-motion: reduce)');
let footerVisible=false,footerFrame=0;
function paintFooter(){footerFrame=0;const rect=footer.getBoundingClientRect();const progress=Math.max(0,Math.min(1,(innerHeight-rect.top)/Math.min(innerHeight,rect.height)));footer.style.setProperty('--footer-progress',reduceMotion.matches?1:progress);footer.style.setProperty('--footer-shift',`${reduceMotion.matches?0:(1-progress)*55}px`);footer.style.setProperty('--star-turn',`${reduceMotion.matches?0:progress*135}deg`);}
new IntersectionObserver(entries=>{footerVisible=entries[0].isIntersecting;footer.classList.toggle('in-view',footerVisible);if(footerVisible)paintFooter();},{rootMargin:'100px'}).observe(footer);
addEventListener('scroll',()=>{if(footerVisible&&!footerFrame)footerFrame=requestAnimationFrame(paintFooter);},{passive:true});
addEventListener('resize',paintFooter);reduceMotion.addEventListener('change',paintFooter);
// Scroll advances comparison views without moving focus or taking over scrolling.
// Any explicit choice locks that comparison for the rest of the visit.
const comparisons=[
 {anchor:$('signal-chart'),buttons:[...document.querySelectorAll('[data-view]')],index:0,locked:false,choose(i){currentView=this.buttons[i].dataset.view;renderSignal();}},
 {anchor:$('survey-frame'),buttons:[...document.querySelectorAll('[data-survey]')],index:0,locked:false,choose(i){survey=this.buttons[i].dataset.survey;renderSky();}}
];
comparisons.forEach(rule=>{
 rule.buttons.forEach(button=>button.addEventListener('click',()=>{rule.locked=true;},true));
 // Focus and touch in a plot mean someone is inspecting it; preserve that view.
 rule.anchor.addEventListener('focusin',()=>{rule.locked=true;});
 rule.anchor.addEventListener('click',()=>{rule.locked=true;});
});
[$('quarter'),$('heldout-only')].forEach(control=>control.addEventListener('change',()=>{comparisons[0].locked=true;},true));
let comparisonFrame=0,previousScroll=scrollY;
function advanceComparisons(){
 comparisonFrame=0;
 const down=scrollY>=previousScroll;previousScroll=scrollY;
 if(reduceMotion.matches||dialog.open)return;
 comparisons.forEach(rule=>{
  if(rule.locked)return;
  const rect=rule.anchor.getBoundingClientRect();
  if(rect.bottom<=0||rect.top>=innerHeight)return;
  const middle=rect.top+rect.height/2;
  const progress=Math.max(0,Math.min(.999,(innerHeight*.8-middle)/(innerHeight*.6)));
  const index=Math.floor(progress*rule.buttons.length);
  if(index===rule.index||(down&&index<rule.index)||(!down&&index>rule.index))return;
  rule.index=index;rule.choose(index);
 });
}
addEventListener('scroll',()=>{if(!comparisonFrame)comparisonFrame=requestAnimationFrame(advanceComparisons);},{passive:true});
// Scroll reveals data marks while axes stay fixed. Inspection always shows final values.
const growingCharts=[...document.querySelectorAll('svg')].filter(svg=>svg.querySelector('.chart-grow-bar,.chart-grow-horizontal')).map(svg=>({svg,progress:0}));
growingCharts.forEach(rule=>{
 const complete=()=>{rule.progress=1;rule.svg.style.setProperty('--chart-reveal',1);};
 ['pointerover','focusin','touchstart'].forEach(type=>rule.svg.addEventListener(type,complete,{passive:true}));
});
let detailFrame=0;
function paintDetails(){
 detailFrame=0;
 growingCharts.forEach(rule=>{
  const rect=rule.svg.getBoundingClientRect();if(!rect.height)return;
  const progress=reduceMotion.matches?1:Math.max(0,Math.min(1,(innerHeight*.9-rect.top)/(Math.min(rect.height,innerHeight)*.65)));
  rule.progress=Math.max(rule.progress,progress);rule.svg.style.setProperty('--chart-reveal',rule.progress);
 });
 if(reduceMotion.matches||dialog.open||albedoManual)return;
 const rect=document.querySelector('.temperature-lab').getBoundingClientRect();
 if(rect.bottom<=0||rect.top>=innerHeight)return;
 const progress=Math.max(0,Math.min(1,(innerHeight*.8-rect.top)/(innerHeight*.55)));
 const value=String(Math.round(progress*16)*5);
 if($('albedo').value!==value){$('albedo').value=value;updateTemperature();}
}
addEventListener('scroll',()=>{if(!detailFrame)detailFrame=requestAnimationFrame(paintDetails);},{passive:true});
addEventListener('resize',paintDetails);reduceMotion.addEventListener('change',paintDetails);
// Run after layout; no-JS and reduced-motion views show complete charts.
requestAnimationFrame(paintDetails);
// Illustrative orbits keep the period ratio; no motion is applied to measured points.
const orbitObserver=new IntersectionObserver(entries=>entries.forEach(entry=>entry.target.classList.toggle('is-in-view',entry.isIntersecting)),{threshold:.15});
document.querySelectorAll('.orbit-diagram').forEach(svg=>orbitObserver.observe(svg));
const navLinks=[...document.querySelectorAll('nav a')];const navObserver=new IntersectionObserver(entries=>entries.forEach(entry=>{if(entry.isIntersecting)navLinks.forEach(a=>{if(a.hash==='#'+entry.target.id)a.setAttribute('aria-current','location');else a.removeAttribute('aria-current');});}),{rootMargin:'-15% 0px -65% 0px'});navLinks.forEach(a=>navObserver.observe(document.querySelector(a.hash)));
})();
