const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const html=fs.readFileSync('index.html','utf8'),dashboard=fs.readFileSync('dashboard.html','utf8');
assert.ok(html.includes('data:image/png;base64,')&&!html.includes('/*__'));
assert.ok(dashboard.includes('ESTAT.HEALTH.UNMET.ACCESS'));
assert.ok(html.includes('width:200px')&&html.includes('dp-tool-grid'));
assert.ok(html.includes('page=comparison')&&html.includes('ESTAT.INTERNET.HOUSEHOLDS'));
assert.ok(dashboard.includes('href="./"'));
const source=html.match(/<script>([\s\S]*?)<\/script>/)[1];
function element(dataset={}){return {dataset,events:{},attrs:{},innerHTML:'',textContent:'',addEventListener(k,f){this.events[k]=f},setAttribute(k,v){this.attrs[k]=v}}}
const nodes=new Map();
for(const k of ['#dp-label','#dp-description','#dp-metrics','#dp-enter','#dp-compare','#dp-challenge','#dp-footer','#dp-motto','.dp-lang','.dp-circle'])nodes.set(k,element());
nodes.get('.dp-circle').href='dashboard.html#page=explore';nodes.get('#dp-compare').href='dashboard.html#page=comparison';
for(const k of ['.dp-circle','#dp-compare'])nodes.get(k).getAttribute=()=>nodes.get(k).href;
const copyNode=element({toolCopy:'comparison'}),toolLink=element({toolPage:'comparison'});toolLink.href='dashboard.html#page=comparison';toolLink.getAttribute=()=>toolLink.href;
const root={querySelector:k=>nodes.get(k),querySelectorAll:k=>k==='[data-tool-copy]'?[copyNode]:[toolLink,nodes.get('.dp-circle'),nodes.get('#dp-compare')]};let redirect=null;
const document={documentElement:{lang:'en'},getElementById:()=>root};
vm.runInNewContext(source,{document,location:{hash:'#indicator=FP.CPI.TOTL.ZG',replace(x){redirect=x}},URLSearchParams});
assert.equal(redirect,'dashboard.html#indicator=FP.CPI.TOTL.ZG');
assert.match(nodes.get('#dp-motto').innerHTML,/Greece/);assert.match(nodes.get('#dp-description').innerHTML,/500 indicators/);
assert.ok(!source.includes('setInterval'),'The introduction must remain stable');
nodes.get('.dp-lang').events.click();assert.equal(document.documentElement.lang,'el');assert.match(nodes.get('#dp-motto').innerHTML,/Ελλάδα/);
assert.match(nodes.get('.dp-circle').href,/page=explore/);assert.match(nodes.get('.dp-circle').href,/lang=el/);assert.match(toolLink.href,/page=comparison/);assert.match(toolLink.href,/lang=el/);assert.equal(copyNode.textContent,'Σύγκριση κυβερνήσεων');
console.log('Landing: stable bilingual introduction, translated actions and legacy deep links passed');
// Source badges remain aligned with the actual published catalogue, including WB's two feeds.
const providers=JSON.parse(fs.readFileSync('scripts/landing_sources.json','utf8'));
const snapshot=JSON.parse(fs.readFileSync('data/indicators.json','utf8'));
const credited=new Set();
for(const p of providers){
 const metrics=snapshot.metrics.filter(m=>p.matchSources.includes(m.source));assert.ok(metrics.length);
 for(const m of metrics){assert.ok(!credited.has(m.code));credited.add(m.code)}
 assert.ok(html.includes('id="ds-'+p.id+'"')&&html.includes('data-source="'+p.id+'"'));
 assert.ok(html.includes('>'+metrics.length+' <span class="ds-copy-en"'));
 assert.ok(p.en&&p.el&&p.url.startsWith('https://'));
 if(p.logo)assert.ok(fs.existsSync('src/source-logos/'+p.logo));
}
assert.equal(credited.size,snapshot.metrics.length);
assert.ok(html.includes('data:image/svg+xml;base64,')&&html.includes('Trace the evidence.'));
const sourceButtons=providers.map(p=>{const b=element({source:p.id});b.attrs={'aria-expanded':'false','aria-controls':'ds-'+p.id};b.getAttribute=k=>b.attrs[k];return b});
const sourcePanels=providers.map(p=>({id:'ds-'+p.id,hidden:true}));
const section={dataset:{},querySelectorAll:k=>k==='[data-source]'?sourceButtons:sourcePanels};
const languageButton=element();languageButton.textContent='ΕΛ';
const sourceDocument={getElementById:()=>section,querySelector:()=>languageButton};
const scripts=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)];assert.equal(scripts.length,2);
vm.runInNewContext(scripts[1][1],{document:sourceDocument});assert.equal(section.dataset.lang,'en');
sourceButtons[0].events.click();assert.equal(sourceButtons[0].attrs['aria-expanded'],'true');assert.equal(sourcePanels[0].hidden,false);
sourceButtons[1].events.click();assert.equal(sourcePanels[0].hidden,true);assert.equal(sourcePanels[1].hidden,false);
sourceButtons[1].events.click();assert.ok(sourcePanels.every(p=>p.hidden));
languageButton.textContent='EN';languageButton.events.click();assert.equal(section.dataset.lang,'el');
console.log('Sources: all 9 providers, accurate counts, embedded logos, exclusive disclosure, closing and Greek language passed');
