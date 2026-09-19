/* Pure numerical and time functions, shared by the browser and regression checks. */
(function(root){
 'use strict';
 const valid=rows=>rows.filter(p=>Number.isInteger(p[0])&&typeof p[1]==='number'&&Number.isFinite(p[1])).sort((a,b)=>a[0]-b[0]);
 function within(rows,start,end){return valid(rows).filter(p=>p[0]>=start&&p[0]<=end);}
 function latest(rows){const points=valid(rows);return points.length?points[points.length-1]:null;}
 function change(rows,start,end){const p=within(rows,start,end);return p.length>=2?{first:p[0],last:p.at(-1),delta:p.at(-1)[1]-p[0][1],count:p.length}:null;}
 function sameYearGap(a,b,start,end){const aa=within(a,start,end),bb=new Map(within(b,start,end));for(let i=aa.length-1;i>=0;i--){if(bb.has(aa[i][0]))return{year:aa[i][0],a:aa[i][1],b:bb.get(aa[i][0]),delta:aa[i][1]-bb.get(aa[i][0])};}return null;}
 function yearFraction(iso){const d=new Date(iso+'T00:00:00Z');const y=d.getUTCFullYear();return y+(d-Date.UTC(y,0,1))/(Date.UTC(y+1,0,1)-Date.UTC(y,0,1));}
 function fullYears(term,asOf){const end=term.end||asOf;const out=[];for(let y=Number(term.start.slice(0,4));y<=Number(end.slice(0,4));y++){if(term.start<=`${y}-01-01`&&end>=`${y+1}-01-01`)out.push(y);}return out;}
 function termStats(rows,term,asOf){const eligible=new Set(fullYears(term,asOf));const p=valid(rows).filter(p=>eligible.has(p[0]));return{eligible:[...eligible],points:p,first:p[0]||null,last:p.at(-1)||null,delta:p.length>=2?p.at(-1)[1]-p[0][1]:null};}
 function segments(rows,start,end){const map=new Map(rows),out=[];let segment=[];for(let y=start;y<=end;y++){const v=map.get(y);if(typeof v==='number'&&Number.isFinite(v))segment.push([y,v]);else if(segment.length){out.push(segment);segment=[];}}if(segment.length)out.push(segment);return out;}
 function csvCell(x){let s=x==null?'':String(x);if(/^[=+@]/.test(s))s="'"+s;return '"'+s.replaceAll('"','""')+'"';}
 function csv(rows){return '\uFEFF'+rows.map(r=>r.map(csvCell).join(',')).join('\r\n');}
 const api={valid,within,latest,change,sameYearGap,yearFraction,fullYears,termStats,segments,csv};
 if(typeof module!=='undefined'&&module.exports)module.exports=api;else root.DatacritusCore=api;
})(typeof window!=='undefined'?window:globalThis);
