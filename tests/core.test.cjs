const assert=require('node:assert/strict');
const C=require('../src/core.js');
// A fall from 8% to 5% is -3 percentage points; missing entries are not zero.
const rows=[[2018,8],[2019,null],[2020,5],[2021,0],[2022,NaN]];
assert.equal(C.change(rows,2018,2020).delta,-3);
assert.equal(C.change(rows,2019,2020),null);
assert.deepEqual(C.latest(rows),[2021,0]);
assert.deepEqual(C.sameYearGap(rows,[[2017,3],[2018,6],[2020,4],[2022,9]],2018,2022),{year:2020,a:5,b:4,delta:1});
assert.equal(C.sameYearGap([[2020,5]],[[2021,4]],2018,2022),null);
assert.deepEqual(C.segments(rows,2018,2022),[[[2018,8]],[[2020,5],[2021,0]]]);
assert.deepEqual(C.fullYears({start:'2019-07-08',end:'2023-05-25'},'2026-09-19'),[2020,2021,2022]);
assert.deepEqual(C.fullYears({start:'2023-05-25',end:'2023-06-26'},'2026-09-19'),[]);
assert.deepEqual(C.fullYears({start:'2020-01-01',end:'2022-01-01'},'2026-09-19'),[2020,2021]);
assert.deepEqual(C.fullYears({start:'2023-06-26',end:null},'2026-09-19'),[2024,2025]);
assert.equal(C.termStats(rows,{start:'2019-07-08',end:'2020-12-31'},'2026-09-19').delta,null);
assert.equal(C.yearFraction('2020-01-01'),2020);
assert.ok(Math.abs(C.yearFraction('2020-07-02')-2020.5)<1e-9);
assert.equal(C.csv([['Ελλάδα','a"b',null,-3]]),'\uFEFF"Ελλάδα","a""b","","-3"');
console.log('12 calculation, missing-data, timeline and CSV checks passed');
