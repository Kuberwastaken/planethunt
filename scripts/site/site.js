(()=>{
const RM=matchMedia('(prefers-reduced-motion: reduce)');
const doc=document.documentElement;
/* Spring: velocity-aware, interruptible. zeta=1 is critically damped (no bounce). */
class Spring{
  constructor(v,o={}){this.x=v;this.v=0;this.t=v;this.k=o.k||260;this.z=o.z==null?1:o.z;this.cb=o.cb;this.raf=0;this.last=0}
  cfg(o){if(o.k)this.k=o.k;if(o.z!=null)this.z=o.z;return this}
  to(t,o={}){this.cfg(o);this.t=t;if(o.v!=null)this.v=o.v;
    if(RM.matches){this.x=t;this.v=0;cancelAnimationFrame(this.raf);this.raf=0;this.cb(this.x,true);return this}
    if(!this.raf){this.last=performance.now();this.raf=requestAnimationFrame(n=>this.tick(n))}return this}
  set(x){cancelAnimationFrame(this.raf);this.raf=0;this.x=x;this.t=x;this.v=0;this.cb(x,false);return this}
  tick(n){let dt=Math.min(.032,(n-this.last)/1000);this.last=n;const c=2*this.z*Math.sqrt(this.k);
    for(let i=0;i<4;i++){const h=dt/4,a=-this.k*(this.x-this.t)-c*this.v;this.v+=a*h;this.x+=this.v*h}
    if(Math.abs(this.x-this.t)<.0008&&Math.abs(this.v)<.01){this.x=this.t;this.v=0;this.raf=0;this.cb(this.x,true);return}
    this.cb(this.x,false);this.raf=requestAnimationFrame(m=>this.tick(m))}
}
const clamp=(a,b,c)=>Math.min(c,Math.max(b,a));
doc.classList.add('js');
document.querySelectorAll('.directory a').forEach(a=>a.classList.add('press'));
document.querySelectorAll('.press').forEach(el=>{
  const s=new Spring(1,{k:700,cb:v=>{el.style.transform=v===1?'':`scale(${v})`}});
  const dn=()=>s.to(.955,{k:900,z:1});const up=()=>s.to(1,{k:380,z:.62});
  el.addEventListener('pointerdown',dn);['pointerup','pointercancel','pointerleave'].forEach(e=>el.addEventListener(e,up));
});
/* reveal on scroll */
const rv=[...document.querySelectorAll('.rv')];let batch=0,bt=0;
const showNow=el=>{el.style.opacity=1;el.style.transform='';el.classList.remove('rv')};
const io=new IntersectionObserver(es=>{es.forEach(e=>{if(!e.isIntersecting&&e.boundingClientRect.top<0){showNow(e.target);io.unobserve(e.target);return}
  if(!e.isIntersecting)return;io.unobserve(e.target);const el=e.target,d=(batch++)*55;clearTimeout(bt);bt=setTimeout(()=>batch=0,200);
  if(RM.matches){showNow(el);return}
  const s=new Spring(0,{k:120,z:1,cb:(p,end)=>{const q=clamp(p,0,1);el.style.opacity=q;el.style.transform=`translateY(${(1-q)*28}px)`;if(end)showNow(el)}});
  setTimeout(()=>s.to(1),d)})},{rootMargin:'0px 0px -8% 0px'});
rv.forEach(el=>io.observe(el));
setTimeout(()=>{document.querySelectorAll('.rv').forEach(el=>{if(el.getBoundingClientRect().top<innerHeight*1.5&&getComputedStyle(el).opacity==='0')showNow(el)})},4000);
/* chapters: nav label, progress, active menu item */
const chapters=[...document.querySelectorAll('[data-chap]')];
const now=document.querySelector('.now'),prog=document.querySelector('.prog'),links=[...document.querySelectorAll('.sheet a')];
const hero=document.querySelector('.lens .ph');let tick=0;
const onScroll=()=>{if(tick)return;tick=requestAnimationFrame(()=>{tick=0;const y=scrollY,h=doc.scrollHeight-innerHeight;prog.style.transform=`scaleX(${h>0?clamp(y/h,0,1):0})`;
  let cur=null;for(const c of chapters){if(c.getBoundingClientRect().top<innerHeight*.4)cur=c}
  now.textContent=cur?cur.dataset.chap:'';links.forEach(a=>a.classList.toggle('on',!!cur&&a.getAttribute('href')==='#'+cur.id));
  if(hero&&!RM.matches&&y<innerHeight*1.2)hero.style.transform=`translateY(${y*.07}px)`})};
addEventListener('scroll',onScroll,{passive:true});onScroll();
/* menu sheet: springs out of the button, same path back */
const sheet=document.querySelector('.sheet'),scrim=document.querySelector('.scrim'),btn=document.querySelector('.menu');let open=false,dragY=0;
const paint=p=>{const q=clamp(p,0,1.06);const r=btn.getBoundingClientRect(),s=sheet.getBoundingClientRect();
  sheet.style.visibility=p>.001?'visible':'hidden';sheet.style.opacity=clamp(p*1.6,0,1);
  sheet.style.transformOrigin=`${r.left+r.width/2-s.left}px 0px`;
  sheet.style.transform=`translateY(${dragY}px) scale(${.3+.7*q})`;scrim.style.opacity=clamp(p,0,1)};
const sp=new Spring(0,{k:320,z:.9,cb:(p,end)=>{paint(p);if(end&&p===0){sheet.style.visibility='hidden'}}});
const setOpen=o=>{open=o;btn.setAttribute('aria-expanded',o);scrim.classList.toggle('on',o);sheet.toggleAttribute('inert',!o);
  if(o){dragY=0;sp.to(1,{z:.86})}else{sp.to(0,{z:1})}};
sheet.setAttribute('inert','');btn.addEventListener('click',()=>setOpen(!open));scrim.addEventListener('click',()=>setOpen(false));
sheet.addEventListener('click',e=>{if(e.target.closest('a'))setOpen(false)});
addEventListener('keydown',e=>{if(e.key==='Escape'){if(lb.classList.contains('on'))closeLB();else if(open)setOpen(false)}});
let sd=null;sheet.addEventListener('pointerdown',e=>{if(e.target.closest('a')&&e.pointerType==='mouse')return;sd={y:e.clientY,t:performance.now(),py:e.clientY,pt:performance.now(),v:0,id:e.pointerId,drag:false}});
addEventListener('pointermove',e=>{if(!sd||e.pointerId!==sd.id)return;const dy=e.clientY-sd.y;if(!sd.drag&&Math.abs(dy)>8&&sheet.scrollTop<=0){sd.drag=true;sheet.setPointerCapture(e.pointerId)}
  if(sd.drag){const n=performance.now();sd.v=(e.clientY-sd.py)/Math.max(1,n-sd.pt)*1000;sd.py=e.clientY;sd.pt=n;dragY=dy<0?dy:dy*.25;paint(sp.x)}});
const sEnd=()=>{if(!sd)return;const d=sd.drag,v=sd.v;sd=null;if(!d)return;const proj=dragY+v*.25;if(proj<-70)setOpen(false);else{const s=new Spring(dragY,{k:300,z:.8,cb:x=>{dragY=x;paint(sp.x)}});s.v=v;s.to(0)}};
addEventListener('pointerup',sEnd);addEventListener('pointercancel',sEnd);
/* lightbox: grows from the tapped figure, drag any way to dismiss with momentum */
const lb=document.querySelector('.lb'),stage=lb.querySelector('.stage'),bg=lb.querySelector('.bg'),cap=lb.querySelector('.cap'),xb=lb.querySelector('.x');
let src=null,from=null,ox=0,oy=0,opener=null;
const place=p=>{const q=p;const f=from,r=stage.__r;if(!r)return;const dx=(f.x+f.w/2)-(r.x+r.w/2),dy=(f.y+f.h/2)-(r.y+r.h/2),sx=f.w/r.w,sy=f.w/r.w;
  const u=1-q;stage.style.transform=`translate(${dx*u+ox}px,${dy*u+oy}px) scale(${sx*u+q})`;
  const f2=clamp(q,0,1)*(1-clamp(Math.hypot(ox,oy)/500,0,.7));bg.style.opacity=f2;cap.style.opacity=clamp(q*q,0,1)*(1-clamp(Math.hypot(ox,oy)/160,0,1));xb.style.opacity=clamp(q,0,1)};
const lp=new Spring(0,{k:260,z:.92,cb:(p,end)=>{place(p);if(end&&p===0){lb.classList.remove('on');stage.innerHTML='';doc.style.overflow='';if(opener)opener.focus({preventScroll:true})}}});
function openLB(fig){opener=fig;const m=fig.querySelector('img,svg');if(!m)return;const r=m.getBoundingClientRect();from={x:r.left,y:r.top,w:r.width,h:r.height};
  stage.innerHTML='';const c=m.cloneNode(true);c.removeAttribute('loading');c.removeAttribute('width');c.removeAttribute('height');stage.appendChild(c);
  cap.textContent=(fig.querySelector('figcaption')||{}).textContent||'';lb.classList.add('on');doc.style.overflow='hidden';ox=oy=0;
  stage.style.transform='';const go=()=>{const b=stage.getBoundingClientRect();stage.__r={x:b.left,y:b.top,w:b.width,h:b.height};lp.set(0);lp.to(1,{z:.9,k:260});xb.focus({preventScroll:true})};
  if(c.tagName==='IMG'&&!c.complete)c.onload=go;else go()}
function closeLB(v){lp.to(0,{z:1,k:300})}
let ld=null;stage.addEventListener('pointerdown',e=>{ld={x:e.clientX,y:e.clientY,px:e.clientX,py:e.clientY,pt:performance.now(),vx:0,vy:0,id:e.pointerId,ox,oy};stage.setPointerCapture(e.pointerId);lp.set(lp.x)});
stage.addEventListener('pointermove',e=>{if(!ld||e.pointerId!==ld.id)return;const n=performance.now(),dt=Math.max(1,n-ld.pt);ld.vx=(e.clientX-ld.px)/dt*1000;ld.vy=(e.clientY-ld.py)/dt*1000;ld.px=e.clientX;ld.py=e.clientY;ld.pt=n;ox=e.clientX-ld.x;oy=e.clientY-ld.y;place(lp.x)});
const lEnd=e=>{if(!ld)return;const d=ld;ld=null;const moved=Math.hypot(ox,oy);const px=ox+d.vx*.2,py=oy+d.vy*.2;
  if(moved<6){ox=oy=0;lp.set(1);closeLB();return}
  if(Math.hypot(px,py)>140){const sx=new Spring(ox,{k:200,z:1,cb:x=>{ox=x;place(lp.x)}}),sy=new Spring(oy,{k:200,z:1,cb:y=>{oy=y;place(lp.x)}});sx.v=d.vx;sy.v=d.vy;sx.to(0);sy.to(0);closeLB()}
  else{const sx=new Spring(ox,{k:300,z:.75,cb:x=>{ox=x;place(lp.x)}}),sy=new Spring(oy,{k:300,z:.75,cb:y=>{oy=y;place(lp.x)}});sx.v=d.vx;sy.v=d.vy;sx.to(0);sy.to(0);lp.to(1)}};
stage.addEventListener('pointerup',lEnd);stage.addEventListener('pointercancel',lEnd);
bg.addEventListener('click',closeLB);xb.addEventListener('click',()=>closeLB());
document.querySelectorAll('figure').forEach(f=>{if(!f.querySelector('img,svg')||f.closest('.lb'))return;f.dataset.zoom='';f.tabIndex=0;f.setAttribute('role','button');f.setAttribute('aria-label','Enlarge: '+((f.querySelector('figcaption')||{}).textContent||'figure').slice(0,80));f.classList.add('press');
  const s=new Spring(1,{k:700,cb:v=>{f.style.transform=v===1?'':`scale(${v})`}});f.addEventListener('pointerdown',()=>s.to(.97,{k:900,z:1}));['pointerup','pointercancel','pointerleave'].forEach(t=>f.addEventListener(t,()=>s.to(1,{k:380,z:.62})));
  f.addEventListener('click',e=>{if(e.target.closest('a'))return;openLB(f)});f.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();openLB(f)}})});
})();
