/* Exercise the production scroll controller with deterministic viewport geometry. */
const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const source=fs.readFileSync(__dirname+'/site.js','utf8');
const start=source.indexOf('// Scroll advances comparison views');
const end=source.indexOf('// Scroll reveals data marks');
assert(start>=0&&end>start,'Scroll controller boundaries must remain identifiable');
function setup(){
 const events={},frames=[];
 const element=(dataset={})=>({dataset,events:{},addEventListener(type,fn){this.events[type]=fn;},getBoundingClientRect(){return this.rect;}});
 const nodes=Object.fromEntries(['signal-chart','survey-frame','quarter','heldout-only'].map(id=>[id,element()]));
 const views=['fold','events','light'].map(view=>element({view}));
 const surveys=['ps1','wide','dss','mass','wise'].map(survey=>element({survey}));
 nodes['signal-chart'].rect={top:600,bottom:950,height:350};
 nodes['survey-frame'].rect={top:5000,bottom:5600,height:600};
 const context={document:{querySelectorAll:selector=>selector==='[data-view]'?views:surveys},$:id=>nodes[id],scrollY:0,innerHeight:1000,currentView:'fold',survey:'ps1',reduceMotion:{matches:false},dialog:{open:false},renderSignal(){},renderSky(){},requestAnimationFrame(fn){frames.push(fn);return frames.length;},addEventListener(type,fn){events[type]=fn;}};
 vm.createContext(context);vm.runInContext(source.slice(start,end),context);
 function scroll(y){context.scrollY=y;nodes['signal-chart'].rect={top:600-y,bottom:950-y,height:350};events.scroll();while(frames.length)frames.shift()();}
 return {context,nodes,views,scroll};
}
test('scroll advances through all three views and reverses naturally',()=>{
 const t=setup();t.scroll(30);assert.equal(t.context.currentView,'fold');t.scroll(250);assert.equal(t.context.currentView,'events');t.scroll(500);assert.equal(t.context.currentView,'light');t.scroll(250);assert.equal(t.context.currentView,'events');t.scroll(0);assert.equal(t.context.currentView,'fold');
});
test('manual selection and inspecting a mark preserve the selected view',()=>{
 const t=setup();t.views[0].events.click();t.scroll(500);assert.equal(t.context.currentView,'fold');
 const focused=setup();focused.nodes['signal-chart'].events.focusin();focused.scroll(500);assert.equal(focused.context.currentView,'fold');
});
test('reduced motion and an open dialog suppress automatic changes',()=>{
 const t=setup();t.context.reduceMotion.matches=true;t.scroll(500);assert.equal(t.context.currentView,'fold');
 const dialog=setup();dialog.context.dialog.open=true;dialog.scroll(500);assert.equal(dialog.context.currentView,'fold');
});
test('offscreen plots do not change; filtering locks the visible plot',()=>{
 const t=setup();t.scroll(1200);assert.equal(t.context.currentView,'fold');
 const filter=setup();filter.nodes.quarter.events.change();filter.scroll(500);assert.equal(filter.context.currentView,'fold');
});

function setupDetails(){
 const events={},frames=[];
 function element(){return {events:{},style:{values:{},setProperty(k,v){this.values[k]=v;}},addEventListener(type,fn){(this.events[type]??=[]).push(fn);},fire(type){this.events[type]?.forEach(fn=>fn());},getBoundingClientRect(){return this.rect;}};}
 const albedo=element();albedo.value='0';
 const nodes={albedo,'albedo-output':{},temperature:{}};
 const lab=element();lab.rect={top:900,bottom:1250,height:350};
 const svg=element();svg.rect={top:1000,bottom:1360,height:360};svg.querySelector=()=>true;
 const context={document:{querySelectorAll:()=>[svg],querySelector:()=>lab},$:id=>nodes[id],innerHeight:1000,reduceMotion:{matches:false,addEventListener(){}},dialog:{open:false},requestAnimationFrame(fn){frames.push(fn);return frames.length;},addEventListener(type,fn){events[type]=fn;}};
 vm.createContext(context);
 const inputCode=source.slice(source.indexOf('function updateTemperature'),source.indexOf('let files=null'));
 const motionCode=source.slice(source.indexOf('// Scroll reveals data marks'),source.indexOf('// Illustrative orbits'));
 vm.runInContext(inputCode+motionCode,context);
 const paint=()=>vm.runInContext('paintDetails()',context);
 return {context,albedo,nodes,lab,svg,paint};
}
test('scroll moves reflectivity through its bounds; manual keyboard control wins',()=>{
 const t=setupDetails();t.paint();assert.equal(t.albedo.value,'0');
 t.lab.rect={top:525,bottom:875,height:350};t.paint();assert.equal(t.albedo.value,'40');assert.equal(t.nodes.temperature.textContent,'367 K');
 t.lab.rect={top:150,bottom:500,height:350};t.paint();assert.equal(t.albedo.value,'80');
 t.albedo.fire('focus');t.albedo.value='35';t.albedo.fire('input');t.lab.rect={top:900,bottom:1250,height:350};t.paint();assert.equal(t.albedo.value,'35');
});
test('bar entrance grows once, never shrinks, and inspection reveals the full data',()=>{
 const t=setupDetails();t.paint();assert.equal(t.svg.style.values['--chart-reveal'],0);
 t.svg.rect={top:800,bottom:1160,height:360};t.paint();const partial=t.svg.style.values['--chart-reveal'];assert(partial>0&&partial<1);
 t.svg.rect={top:950,bottom:1310,height:360};t.paint();assert.equal(t.svg.style.values['--chart-reveal'],partial);
 t.svg.fire('focusin');assert.equal(t.svg.style.values['--chart-reveal'],1);
});
test('reduced motion completes the plot and preserves the chosen temperature',()=>{
 const t=setupDetails();t.context.reduceMotion.matches=true;t.lab.rect={top:100,bottom:450,height:350};t.paint();assert.equal(t.svg.style.values['--chart-reveal'],1);assert.equal(t.albedo.value,'0');
});
