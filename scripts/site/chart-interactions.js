/* Inspect committed measurements without adding a DOM node for every cadence. */
(() => {
'use strict';
const dense = new WeakMap(), enhanced = new WeakSet();
const tooltip = document.createElement('div');
tooltip.className = 'chart-tooltip'; tooltip.id = 'chart-tooltip'; tooltip.hidden = true;
tooltip.setAttribute('role', 'tooltip'); document.body.append(tooltip);
let active = null;
function hide() {
  active?.classList.remove('is-inspected'); active?.removeAttribute('aria-describedby');
  active = null; tooltip.hidden = true;
}
function show(mark, detail, event) {
  if (active !== mark) { hide(); active = mark; mark.classList.add('is-inspected'); }
  const container = mark.closest('dialog') || document.body;
  if (tooltip.parentElement !== container) container.append(tooltip);
  tooltip.replaceChildren();
  const title = document.createElement('strong'); title.textContent = detail[0]; tooltip.append(title);
  for (const [label, value] of detail[1]) {
    const row = document.createElement('div'), term = document.createElement('span'), val = document.createElement('b');
    term.textContent = label; val.textContent = value; row.append(term, val); tooltip.append(row);
  }
  tooltip.hidden = false; mark.setAttribute('aria-describedby', tooltip.id);
  const rect = mark.getBoundingClientRect(), box = tooltip.getBoundingClientRect();
  const x = event?.clientX ?? rect.left + rect.width / 2;
  const y = event?.clientY ?? rect.top + rect.height / 2;
  tooltip.style.left = Math.max(8, Math.min(innerWidth - box.width - 8, x + 16)) + 'px';
  tooltip.style.top = Math.max(8, Math.min(innerHeight - box.height - 8, y + 18)) + 'px';
}
function enhance(svg) {
  if (!svg || enhanced.has(svg)) return;
  enhanced.add(svg);
  const marks = [...svg.querySelectorAll('[data-chart-detail]')];
  if (marks.length) {
    svg.setAttribute('role', 'group');
    svg.setAttribute('aria-description','Hover or tap a mark for saved measurements. Tab to enter the chart; arrow keys move between marks; Escape dismisses details.');
    marks.forEach((mark, i) => {
      const detail = JSON.parse(mark.dataset.chartDetail);
      mark.setAttribute('tabindex', i === 0 ? '0' : '-1');
      mark.setAttribute('role', 'img'); mark.setAttribute('aria-label', [detail[0], ...detail[1].map(r => r.join(': '))].join('; '));
      mark.querySelectorAll('title').forEach(t => t.remove());
      mark.addEventListener('pointerenter', e => show(mark, detail, e));
      mark.addEventListener('pointermove', e => show(mark, detail, e));
      mark.addEventListener('pointerleave', () => { if (document.activeElement !== mark) hide(); });
      mark.addEventListener('focus', () => { marks.forEach(m=>m.setAttribute('tabindex',m===mark?'0':'-1')); show(mark, detail); });
      mark.addEventListener('blur', hide);
      mark.addEventListener('click', e => { mark.focus({preventScroll:true}); show(mark, detail, e); });
      mark.addEventListener('keydown', e => {
        let next;
        if (e.key === 'ArrowRight' || e.key === 'ArrowDown') next = (i + 1) % marks.length;
        if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') next = (i - 1 + marks.length) % marks.length;
        if (e.key === 'Home') next = 0;
        if (e.key === 'End') next = marks.length - 1;
        if (next !== undefined) { e.preventDefault(); marks.forEach(m => m.setAttribute('tabindex','-1')); marks[next].setAttribute('tabindex','0'); marks[next].focus({preventScroll:true}); }
      });
    });
  }
  const config = dense.get(svg);
  if (config) attachDense(svg, config);
}
function attachDense(svg, {rows, X, Y, bounds}) {
  const NS = 'http://www.w3.org/2000/svg', surface = document.createElementNS(NS,'rect'), dot = document.createElementNS(NS,'circle');
  surface.classList.add('chart-surface'); surface.setAttribute('x',bounds.x); surface.setAttribute('y',bounds.y); surface.setAttribute('width',bounds.width); surface.setAttribute('height',bounds.height); surface.setAttribute('fill','transparent'); surface.setAttribute('tabindex','0'); surface.setAttribute('role','img'); surface.setAttribute('aria-label','Individual Kepler measurements. Arrow keys step through time; Home and End jump to the first and last measurement.');
  dot.setAttribute('r','5'); dot.setAttribute('fill','none'); dot.setAttribute('stroke','white'); dot.setAttribute('stroke-width','1.5'); dot.style.pointerEvents='none'; dot.style.display='none';
  svg.append(surface,dot); svg.setAttribute('role','group'); let index=0;
  function inspect(e) {
    const [t,y,q,transit]=rows[index];
    surface.setAttribute('aria-label',`Quarter ${q}, BTJD ${t.toFixed(7)}, ${y.toFixed(2)} ppm${transit?', in-transit selection':''}`);
    dot.setAttribute('cx',X(t)); dot.setAttribute('cy',Math.max(bounds.y,Math.min(bounds.y+bounds.height,Y(y)))); dot.style.display='';
    show(surface,[`Kepler cadence / Q${q}`,[['Time (BTJD)',t.toFixed(7)],['Flux',y.toLocaleString(undefined,{maximumFractionDigits:2})+' ppm'],['Selection',transit?'In-transit':'Out-of-transit'],['Measurement',`${index+1} / ${rows.length.toLocaleString()}`]]],e);
  }
  surface.addEventListener('pointermove',e=>{
    const pt=new DOMPoint(e.clientX,e.clientY).matrixTransform(svg.getScreenCTM().inverse());
    // Binary search bounds a small x-window; choose the closest observed point inside it.
    let lo=0,hi=rows.length;
    while(lo<hi){const mid=(lo+hi)>>1;if(X(rows[mid][0])<pt.x-8)lo=mid+1;else hi=mid;}
    let best=Infinity;index=Math.min(lo,rows.length-1);
    for(let i=Math.max(0,lo-1);i<rows.length;i++) {
      const dx=X(rows[i][0])-pt.x,dy=Y(rows[i][1])-pt.y,dist=dx*dx+dy*dy;
      if(dist<best){best=dist;index=i;}
      if(dx>8 && i>lo)break;
    }
    inspect(e);
  });
  surface.addEventListener('pointerleave',()=>{if(document.activeElement!==surface){dot.style.display='none';hide();}});
  surface.addEventListener('click',e=>{surface.focus({preventScroll:true});inspect(e);});
  surface.addEventListener('focus',()=>inspect());
  surface.addEventListener('blur',()=>{dot.style.display='none';hide();});
  surface.addEventListener('keydown',e=>{
    const step=e.shiftKey?100:1;
    if(['ArrowRight','ArrowDown','ArrowLeft','ArrowUp','Home','End'].includes(e.key)){
      e.preventDefault();index=e.key==='Home'?0:e.key==='End'?rows.length-1:Math.max(0,Math.min(rows.length-1,index+(['ArrowRight','ArrowDown'].includes(e.key)?step:-step)));inspect();
    }
  });
}
document.addEventListener('keydown',e=>{if(e.key==='Escape')hide();});
document.addEventListener('pointerdown',e=>{if(!e.target.closest('.chart-hit,.chart-surface'))hide();});
addEventListener('scroll',hide,{passive:true,capture:true});
document.querySelector('dialog')?.addEventListener('close',hide);
window.chartInspector={enhance,hide,register(svg,config){dense.set(svg,config);},copy(source,clone){clone.querySelectorAll('.chart-surface').forEach(el=>el.remove());clone.querySelectorAll('.is-inspected').forEach(el=>el.classList.remove('is-inspected'));clone.querySelectorAll('[aria-describedby]').forEach(el=>el.removeAttribute('aria-describedby'));if(dense.has(source)){const last=clone.lastElementChild;if(last?.tagName==='circle')last.remove();dense.set(clone,dense.get(source));}enhance(clone);}};
document.querySelectorAll('svg').forEach(enhance);
})();
