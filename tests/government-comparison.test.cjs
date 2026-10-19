const assert=require('node:assert/strict'),C=require('../src/core.js'),G=require('../src/government-comparison.js');
const metric={code:'TEST',title:{en:'<Rate & example>',el:'Δείκτης'},providerTitle:'Rate',unit:'%',change:'pp',sourceName:'Eurostat',sourceUrl:'https://example.org/source',retrievedAt:'2026-10-03T00:00:00Z',series:{GRC:[[2018,99],[2019,8],[2020,null],[2021,0],[2022,5],[2023,7],[2024,10],[2025,20],[2026,30]]},flags:{GRC:{2019:'b',2021:'e',2026:'p'}}};
const terms=[{id:'A',name:{en:'<Leader A>',el:'Α'},coalition:{en:'Coalition A',el:'Α'},start:'2018-07-01',end:'2022-05-01'},{id:'B',name:{en:'Leader B',el:'Β'},coalition:{en:'Coalition B',el:'Β'},start:'2022-05-01',end:null}];
const m=G.model({metric,terms,asOf:'2026-10-03'});
assert.deepEqual(m.periods[0].eligible,[2019,2020,2021]);assert.deepEqual(m.periods[0].missing,[2020]);assert.equal(m.periods[0].mean,4);assert.equal(m.periods[0].delta,-8);assert.equal(m.periods[0].last[1],0);assert.deepEqual(m.periods[1].points,[[2023,7],[2024,10],[2025,20]]);assert.equal(m.periods[1].delta,13);assert.ok(!m.periods[1].flags.length);
assert.deepEqual(m.ticks,C.axisTicks([8,0,7,10,20]));
const chart=G.chart({period:m.periods[0],ticks:m.ticks});assert.equal((chart.match(/<path /g)||[]).length,2,'Missing 2020 must split the line');
const csv=G.csv(m);assert.ok(csv.includes('"2020","","%"'));assert.ok(!csv.includes('"2026","30"'));assert.ok(csv.includes('"2019","8","%","b"'));
const short=G.model({metric,terms:[{...terms[0],start:'2020-03-01',end:'2020-05-01'},terms[1]],asOf:'2026-10-03'});assert.equal(short.periods[0].mean,null);assert.equal(short.periods[0].delta,null);assert.deepEqual(short.periods[0].eligible,[]);
const one=G.model({metric,terms:[{...terms[0],start:'2020-03-01',end:'2022-01-01'},terms[1]],asOf:'2026-10-03'});assert.equal(one.periods[0].mean,0);assert.equal(one.periods[0].delta,null);
assert.ok(G.model({metric,terms:[terms[0],terms[0]],asOf:'2026-10-03'}).sameTerm);
for(const lang of ['en','el'])for(const format of ['landscape','portrait']){const image=G.build({comparison:m,lang,format});assert.ok(image.svg.startsWith('<svg'));assert.ok(!image.svg.includes('<Leader'));assert.ok(image.svg.includes('2019, 2021'));assert.ok(image.svg.includes(lang==='el'?'π.μ.':'pp'));assert.equal(image.height,format==='portrait'?1740:1100);}
const data=require('../data/indicators.json'),history=require('../data/history.json');let exportCount=0;
for(const item of data.metrics){const cmp=G.model({metric:item,terms:history.governments.filter(t=>['2015-09-21','2019-07-08'].includes(t.id)),asOf:history.verifiedAt});for(const lang of ['en','el'])for(const format of ['landscape','portrait']){const image=G.build({comparison:cmp,lang,format});assert.ok(!/NaN|undefined/.test(image.svg),item.code);assert.ok(image.svg.includes(item.code));exportCount++;}}
console.log(`Government comparison: correct full years, gaps, zero, averages, flags, pp, escaped text, CSV and ${exportCount} catalogue exports`);

// Annual credible bounds belong to source estimates, not arithmetic term averages.
const estimate={...metric,unit:'model index',change:'absolute',license:'CC BY-SA 4.0',termsUrl:'https://creativecommons.org/licenses/by-sa/4.0/',attribution:'V-Dem Project, Dataset v16',sourceVersion:'16',uncertaintyLevel:.68,uncertainty:{GRC:{2019:[-2,10],2021:[-3,2],2023:[4,11],2024:[6,14],2025:[15,25]}}};
const em=G.model({metric:estimate,terms,asOf:'2026-10-03'});
assert.ok(em.ticks[0]<=-3&&em.ticks.at(-1)>=25,'Bounds must fit the shared axis');
assert.equal(em.periods[0].mean,4,'Keep the mean of point estimates');
assert.equal(em.periods[0].meanUncertainty,undefined,'Do not invent a confidence interval for the mean');
assert.match(G.chart({period:em.periods[0],ticks:em.ticks}),/opacity=".35"/);
assert.match(G.csv(em),/uncertainty_low/);assert.match(G.csv(em),/"-2","10","0.68"/);
const eg=G.build({comparison:em});assert.ok(eg.svg.includes(estimate.termsUrl));assert.match(eg.svg,/not intervals for term averages/);
assert.equal(eg.height,1250,'Credit and uncertainty notes get their own space');

// Regression: topic and two-period coverage, not undefined `category` equality.
const jobs={...metric,code:'SL.UEM.TOTL.ZS',categories:['jobs'],primaryCategory:'jobs'};
const related={...jobs,code:'SL.UEM.1524.ZS'};
const other={...jobs,code:'ELECTRICITY',categories:['environment'],primaryCategory:'environment'};
const sparse={...jobs,code:'SPARSE',series:{GRC:[[2021,0]]}};
const matches=G.suggestions({metric:jobs,metrics:[jobs,related,other,sparse],terms,asOf:'2026-10-03'});
assert.ok(matches.some(s=>s.metric.code===related.code&&s.available));
assert.ok(!matches.some(s=>s.metric.code===other.code));
assert.ok(matches.some(s=>s.metric.code===sparse.code&&!s.available));
assert.equal(G.canExport([m]),true);
assert.equal(G.canExport([short]),false,'Either empty period blocks export');
assert.equal(G.canExport([m,short]),false,'Every selected KPI needs both periods');
assert.equal(G.canExport([G.model({metric,terms:[terms[0],terms[0]],asOf:'2026-10-03'})]),false);
assert.equal(G.canExport([]),false);

// Exercise the actual application URL and SVG functions without browser dependencies.
const fs=require('node:fs'),vm=require('node:vm'),app=fs.readFileSync(require.resolve('../src/app.js'),'utf8');
const extract=(start,end)=>app.slice(app.indexOf(start),app.indexOf(end,app.indexOf(start)));
const ctx={D:{metrics:[jobs,related,other,sparse],categories:[{id:'jobs'},{id:'environment'}],countries:{GRC:'Greece'}},H:{governments:terms},state:{metric:jobs.code,category:'jobs',page:'comparison',lang:'en',start:2000,end:2025,countries:['GRC'],bands:true,elections:false},comparisonState:{a:'A',b:'B',format:'landscape'},multiCodes:[related.code,sparse.code],MAX_YEAR:2025,ASOF:'2026-10-03',URLSearchParams,location:{hash:''},history:{replaceState(_a,_b,hash){ctx.location.hash=hash;}},metric:()=>ctx.D.metrics.find(m=>m.code===ctx.state.metric)};
vm.createContext(ctx);
vm.runInContext(extract('function readURL()','readURL();')+extract('function multiMetrics()','function multiModels()'),ctx);
ctx.writeURL();assert.ok(ctx.location.hash.includes('kpis='));ctx.multiCodes=[];ctx.readURL();assert.deepEqual(Array.from(ctx.multiCodes),[related.code,sparse.code]);
ctx.location.hash+='%2CUNKNOWN%2C'+related.code;ctx.readURL();assert.deepEqual(Array.from(ctx.multiCodes),[related.code,sparse.code],'Invalid and duplicate selections are ignored');
ctx.location.hash='#page=comparison&indicator='+jobs.code;ctx.readURL();assert.deepEqual(Array.from(ctx.multiCodes),[],'Legacy links remain a single KPI');
Object.assign(ctx,{multiModels:()=>[m,em],label:o=>typeof o==='object'?o[ctx.state.lang]||o.en:o,esc:s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])),format:n=>n==null?'—':String(n),signed:n=>(n>0?'+':'')+n,deltaUnit:m=>m.change==='pp'?'pp':m.unit});
vm.runInContext(extract('function multiSvg()','function multiCsv()'),ctx);
for(const lang of ['en','el']){ctx.state.lang=lang;const svg=ctx.multiSvg();assert.ok(!/NaN|undefined|<Leader/.test(svg));assert.ok(svg.includes(terms[0].start));assert.ok(svg.includes(terms[1].start));assert.ok(svg.includes(metric.sourceUrl));assert.ok(svg.includes(metric.retrievedAt.slice(0,10)));assert.ok(svg.includes(estimate.license));assert.ok(svg.includes(estimate.termsUrl));assert.ok(svg.includes('2019, 2021'));assert.ok(svg.includes(lang==='el'?'Κενά':'Missing'));}
console.log('Studio regressions: relevant suggestions, two-period export guards, restored/legacy URLs and bilingual sourced SVG passed');
