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
const document={documentElement:{lang:'el'},getElementById:()=>root};
vm.runInNewContext(source,{document,location:{hash:'#indicator=FP.CPI.TOTL.ZG',replace(x){redirect=x}},URLSearchParams});
assert.equal(redirect,'/dashboard.html#indicator=FP.CPI.TOTL.ZG');
assert.match(nodes.get('#dp-motto').innerHTML,/Ελλάδα/);assert.match(nodes.get('#dp-description').innerHTML,/500 δείκτες/);
assert.ok(!source.includes('setInterval'),'The introduction must remain stable');
nodes.get('.dp-lang').events.click();assert.equal(document.documentElement.lang,'en');assert.match(nodes.get('#dp-motto').innerHTML,/Greece/);
assert.match(nodes.get('.dp-circle').href,/page=explore/);assert.match(nodes.get('.dp-circle').href,/lang=en/);assert.match(toolLink.href,/page=comparison/);assert.match(toolLink.href,/lang=en/);assert.equal(copyNode.textContent,'Compare governments');
console.log('Landing: stable bilingual introduction, translated actions and legacy deep links passed');
// Source badges remain aligned with the actual published catalogue, including WB's two feeds.
const providers=JSON.parse(fs.readFileSync('scripts/landing_sources.json','utf8'));
const snapshot=JSON.parse(fs.readFileSync('data/indicators.json','utf8'));
const credited=new Set();
for(const p of providers){
 const metrics=snapshot.metrics.filter(m=>p.matchSources.includes(m.source));assert.ok(metrics.length);
 for(const m of metrics){assert.ok(!credited.has(m.code));credited.add(m.code)}
 assert.ok(html.includes('id="ds-'+p.id+'"')&&html.includes('data-source="'+p.id+'"'));
 assert.ok(html.includes('>'+metrics.length+' <span class="ds-copy-el"'));
 assert.ok(p.en&&p.el&&p.url.startsWith('https://'));
 if(p.logo)assert.ok(fs.existsSync('src/source-logos/'+p.logo));
}
assert.equal(credited.size,snapshot.metrics.length);
assert.ok(html.includes('data:image/svg+xml;base64,')&&html.includes('Γνωρίστε τις πηγές.'));
const sourceButtons=providers.map(p=>{const b=element({source:p.id});b.attrs={'aria-expanded':'false','aria-controls':'ds-'+p.id};b.getAttribute=k=>b.attrs[k];return b});
const sourcePanels=providers.map(p=>({id:'ds-'+p.id,hidden:true}));
const section={dataset:{},querySelectorAll:k=>k==='[data-source]'?sourceButtons:sourcePanels};
const languageButton=element();languageButton.textContent='EN';
const sourceDocument={getElementById:()=>section,querySelector:()=>languageButton};
const scripts=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)];assert.equal(scripts.length,4);
vm.runInNewContext(scripts[1][1],{document:sourceDocument});assert.equal(section.dataset.lang,'el');
sourceButtons[0].events.click();assert.equal(sourceButtons[0].attrs['aria-expanded'],'true');assert.equal(sourcePanels[0].hidden,false);
sourceButtons[1].events.click();assert.equal(sourcePanels[0].hidden,true);assert.equal(sourcePanels[1].hidden,false);
sourceButtons[1].events.click();assert.ok(sourcePanels.every(p=>p.hidden));
languageButton.textContent='ΕΛ';languageButton.events.click();assert.equal(section.dataset.lang,'en');
console.log('Sources: all 9 providers, accurate counts, embedded logos, exclusive disclosure, closing and Greek language passed');
// The teaser must describe exactly the terms and annual observations opened by its link.
const C=require('../src/core.js');
const timeline=JSON.parse(fs.readFileSync('data/history.json','utf8'));
const unemployment=snapshot.metrics.find(m=>m.code==='SL.UEM.TOTL.ZS');
for(const [path,lang] of [['index.html','el'],['el/index.html','el'],['en/index.html','en']]){
 const page=fs.readFileSync(path,'utf8');
 const card=page.match(/<a class="dp-tool" data-tool-page="comparison"[\s\S]*?<\/a>/)[0];
 const href=card.match(/href="([^"]+)"/)[1].replaceAll('&amp;','&');const q=new URLSearchParams(href.split('#')[1]);
 for(const slot of ['A','B']){
  const term=timeline.governments.find(g=>g.id===q.get('period'+slot));assert.ok(term);
  const stats=C.termStats(unemployment.series.GRC,term,timeline.verifiedAt);
  assert.equal(stats.points.length,stats.eligible.length);
  assert.ok(card.includes(term.name[lang]));
  assert.ok(card.includes(term.coalition[lang]));
  assert.ok(card.includes(term.start.slice(0,4)+'–'+term.end.slice(0,4)));
  assert.ok(card.includes(stats.eligible[0]+'–'+stats.eligible.at(-1)));
  const average=(stats.points.reduce((sum,p)=>sum+p[1],0)/stats.points.length).toFixed(1);
  assert.ok(card.includes('<b>'+(lang==='el'?average.replace('.',','):average)+'%</b>'));
 }
 assert.ok(!card.includes('2019–present')&&!card.includes('Θητεία'));
 for(const p of providers){
  const button=page.match(new RegExp('<button[^>]*data-source="'+p.id+'"[\\s\\S]*?</button>'))[0];
  assert.equal(button.split(p.name).length-1,1,'Source name repeated: '+p.id);
  assert.ok(!/>\s*\+\s*</.test(button),'Stray plus in source badge');
 }
}
console.log('Homepage comparison: named governments, correct term ends, full-year averages and source badges match in Greek and English');
// The random comparison replaces the fallback card: every drawn pair needs its own leaders.
function randomElement(){return {children:[],events:{},style:{},textContent:'',append(...els){this.children.push(...els)},replaceChildren(...els){this.children=[...els]},addEventListener(k,f){this.events[k]=f}}}
const randomScript=scripts.at(-1)[1];
for(const lang of ['en','el']){
 const art=randomElement(),nextButtons=[],langButton=randomElement();
 const card={href:'',after(b){nextButtons.push(b)},querySelector:()=>art};
 const doc={documentElement:{lang},createElement:randomElement,querySelector:k=>k==='[data-tool-page="comparison"]'?card:k==='.dp-lang'?langButton:null};
 vm.runInNewContext(randomScript,{document:doc,URLSearchParams,Intl,Math:{random:()=>0,floor:Math.floor,min:Math.min,max:Math.max}});
 for(let draw=0;draw<20;draw++){
  assert.ok(card.href.startsWith('/dashboard.html#'),'Random links must work from language subdirectories');
  const context=nextButtons.find(e=>e.className==='dp-history-context');const trend=context.children.find(e=>e.src?.startsWith('data:image/svg+xml'));assert.ok(trend,'Every random comparison needs full-history context');
  const graphic=decodeURIComponent(trend.src.split(',').slice(1).join(','));assert.ok(!graphic.includes('NaN'));assert.equal((graphic.match(/<rect /g)||[]).length,2);
  const q=new URLSearchParams(card.href.split('#')[1]);const rows=art.children.filter(e=>e.className?.split(' ').includes('dp-random-period'));assert.equal(rows.length,2);assert.ok(rows.every(row=>row.children.some(e=>e.className==='dp-period-trend')),'Each government must have its own trend');
  for(const [i,key] of ['periodA','periodB'].entries()){
   const term=timeline.governments.find(g=>g.id===q.get(key));
   const legend=context.children.find(e=>e.className==='dp-history-legend');assert.equal(legend.children.length,2);
   const legendItem=legend.children[i];assert.equal(legendItem.children[0].style.backgroundColor,timeline.parties[term.party].color);assert.ok(legendItem.children[1].textContent.includes(term.name[lang]));assert.ok(graphic.includes('fill="'+timeline.parties[term.party].color+'"'));
   assert.equal(rows[i].children[0].textContent,term.coalition[lang]);
   assert.ok(rows[i].children[1].textContent.includes(term.name[lang]));
   assert.ok(rows[i].children[1].textContent.includes((lang==='el'?'Κυβέρνηση ':'Government ')+term.start.slice(0,4)+'–'+term.end.slice(0,4)));
  }
  nextButtons[0].events.click();
 }
}
console.log('Random comparison: drawn government names and term labels match the actual links in both languages');
