const assert=require('node:assert/strict');
const C=require('../src/core.js'),I=require('../src/infographic.js');
const D=require('../data/indicators.json');
const fixture={...D.metrics[0],series:{GRC:[[2018,8],[2019,null],[2020,5],[2021,0]],EUU:[[2018,6],[2020,4]]},flags:{GRC:{2020:'p'}},unit:'%',change:'pp'};
const options={metric:fixture,countries:['GRC','EUU'],countryInfo:D.countries,from:2018,to:2021};
const exported=I.build(options);
// Different latest years must not produce a false comparison. 2020 is common.
assert.match(exported.svg,/>\+1<\/text>/);
assert.match(exported.svg,/>2020 · pp<\/text>/);
assert.match(exported.svg,/>-8<\/text>/);
assert.match(exported.svg,/Source flags: p/);
// Missing 2019 splits both lines. The 2021 Greek zero remains an observation.
assert.equal((exported.svg.match(/<path /g)||[]).length,4);
assert.equal((exported.svg.match(/<circle /g)||[]).length,5);
const missing=I.build({...options,from:2019,to:2019});
assert.match(missing.svg,/No observations in this period/);
assert.match(missing.svg,/No common year/);
const escaped=I.build({...options,title:'<script>alert("x")</script>',format:'portrait'});
assert.ok(!escaped.svg.includes('<script>'));
assert.match(escaped.svg,/&lt;script&gt;/);
assert.equal(escaped.width,1080);assert.equal(escaped.height,1350);
for(const values of [[],[0],[8,8],[-9.8,8.6],[.012,.03],[2e9,3e9]]){
 const ticks=C.axisTicks(values);assert.ok(ticks.length>=2&&ticks.every(Number.isFinite));
 assert.ok(ticks.every((t,i)=>i===0||t>ticks[i-1]));
 for(const value of values)assert.ok(value>=ticks[0]&&value<=ticks.at(-1));
}
// The published catalogue must export without non-finite geometry in either language/layout.
for(const metric of D.metrics)for(const lang of ['en','el'])for(const format of ['landscape','portrait']){
 const result=I.build({...options,metric,lang,format,from:2000,to:2025});
 assert.ok(!/NaN|Infinity|undefined/.test(result.svg),metric.code);
 assert.ok(result.svg.includes(metric.code)&&result.svg.includes(metric.sourceUrl.replaceAll('&','&amp;')));
}
console.log('Infographic checks passed: gaps, zero values, common-year comparisons, escaped titles, flags, axes and 236 catalogue exports');
