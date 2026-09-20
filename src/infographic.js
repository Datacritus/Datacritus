/* Branded, self-contained exports drawn from the selected observations. */
(function(root){
 'use strict';
 const C=typeof module!=='undefined'&&module.exports?require('./core.js'):root.DatacritusCore;
 const escape=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 function wrap(value,max){const out=[];let line='';const words=String(value).split(/\s+/).flatMap(word=>word.length>max?word.match(new RegExp('.{1,'+max+'}','gu')):word);for(const word of words){if(line&&(line+' '+word).length>max){out.push(line);line=word;}else line+=(line?' ':'')+word;}if(line)out.push(line);return out;}
 function build({metric:m,countries,countryInfo,from,to,lang='en',title='',format='landscape',logoUri=''}){
  const el=lang==='el',portrait=format==='portrait',W=portrait?1080:1600,H=portrait?1350:1000,M=64;
  const label=o=>typeof o==='object'?(o[lang]||o.en):o;
  const fmt=n=>n===null||n===undefined?'—':new Intl.NumberFormat(el?'el-GR':'en-GB',{maximumFractionDigits:Math.abs(n)>=1000?0:2,notation:Math.abs(n)>=1e6?'compact':'standard'}).format(Object.is(n,-0)?0:n);
  const signed=n=>(n>0?'+':'')+fmt(n),unit=m.change==='pp'?(el?'π.μ.':'pp'):m.unit;
  const p=C.within(m.series.GRC,from,to),last=p.at(-1),change=C.change(m.series.GRC,from,to),peer=countries.find(c=>c!=='GRC'),gap=peer?C.sameYearGap(m.series.GRC,m.series[peer],from,to):null;
  const ink='#123b48',muted='#526a73',navy='#073b4c',gold='#ffd166';let out=[];
  const rect=(x,y,w,h,fill,rx=0)=>out.push(`<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="${rx}" fill="${fill}"/>`);
  const text=(x,y,content,size=22,color=ink,weight=400,extra='')=>out.push(`<text x="${x}" y="${y}" font-size="${size}" fill="${color}" font-weight="${weight}" ${extra}>${escape(content)}</text>`);
  const lines=(x,y,content,size,width,color=ink,weight=400)=>{const rows=wrap(content,Math.max(8,Math.floor(width/(size*.62))));rows.forEach((row,i)=>text(x,y+i*size*1.3,row,size,color,weight));return rows.length*size*1.3;};
  out.push(`<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" font-family="Arial, sans-serif" role="img"><title>${escape(label(m.title))}, ${from}–${to}</title><desc>${escape(countries.map(c=>label(countryInfo[c])).join(', '))}. ${escape(el?'Ετήσιες παρατηρήσεις. Τα κενά δεν συμπληρώνονται.':'Annual observations. Missing values remain missing.')}</desc>`);
  rect(0,0,W,H,'#ffffff');rect(0,0,W,298,navy);rect(0,298,W,6,gold);
  if(logoUri)out.push(`<image href="${escape(logoUri)}" x="${M}" y="28" width="255" height="75" preserveAspectRatio="xMidYMid slice"/>`);else text(M,75,'DATACRITUS',30,gold,700);
  text(W-M,74,`${from}–${to}`,24,'#d8e8ed',400,'text-anchor="end"');
  const heading=title.trim().slice(0,80)||label(m.title);let headingSize=portrait?40:46;
  while(headingSize>28&&wrap(heading,Math.floor((W-2*M)/(headingSize*.62))).length>2)headingSize-=2;
  lines(M,160,heading,headingSize,W-2*M,'#ffffff',700);
  lines(M,254,`${label(m.title)} · ${m.unit}`,20,W-2*M,'#cce0e6');
  const cards=[{label:`${label(countryInfo.GRC)} · ${last?last[0]:(el?'Χωρίς δεδομένα':'No data')}`,value:last?fmt(last[1]):'—',detail:m.unit},
   {label:el?'Μεταβολή περιόδου':'Period change',value:change?signed(change.delta):'—',detail:change?`${change.first[0]}–${change.last[0]} · ${unit}`:(el?'Απαιτούνται 2 παρατηρήσεις':'Needs 2 observations')},
   {label:peer?`${el?'Διαφορά από':'Gap to'} ${label(countryInfo[peer])}`:(el?'Παρατηρήσεις':'Observations'),value:peer?(gap?signed(gap.delta):'—'):String(p.length),detail:peer?(gap?`${gap.year} · ${unit}`:(el?'Χωρίς κοινό έτος':'No common year')):`${from}–${to}`}];
  const cw=(W-2*M-32)/3;
  cards.forEach((c,i)=>{const x=M+i*(cw+16);rect(x,326,cw,132,i===0?'#eaf4f5':'#f4f6f6',12);lines(x+18,351,c.label,portrait?17:20,cw-36,muted,500);text(x+18,406,c.value,portrait?38:46,navy,700);lines(x+18,434,c.detail,portrait?16:18,cw-36,muted);});
  const L=M+65,R=W-M-22,T=496,B=H-244,all=countries.flatMap(c=>C.within(m.series[c],from,to).map(r=>r[1])),ticks=C.axisTicks(all),lo=ticks[0],hi=ticks.at(-1),x=year=>L+(year-from+.5)/(to-from+1)*(R-L),y=value=>B-(value-lo)/(hi-lo||1)*(B-T);
  for(const v of ticks){out.push(`<line x1="${L}" x2="${R}" y1="${y(v)}" y2="${y(v)}" stroke="${v===0?'#a7bbc3':'#dfe7ea'}"/>`);text(L-15,y(v)+6,fmt(v),19,muted,400,'text-anchor="end"');}
  const span=to-from,step=span<=5?1:span<=12?2:span<=25?5:10,years=new Set([from,to]);for(let year=Math.ceil(from/step)*step;year<=to;year+=step)if(year-from>=step*.8&&to-year>=step*.8)years.add(year);
  for(const year of [...years].sort((a,b)=>a-b))text(x(year),B+33,year,20,muted,400,'text-anchor="middle"');
  for(const c of [...countries].reverse())for(const seg of C.segments(m.series[c],from,to)){
   const color=countryInfo[c].color,d=seg.map((point,i)=>`${i?'L':'M'}${x(point[0]).toFixed(2)},${y(point[1]).toFixed(2)}`).join(' ');
   out.push(`<path d="${d}" fill="none" stroke="${escape(color)}" stroke-width="${c==='GRC'?5:3}" stroke-linecap="round" stroke-linejoin="round" ${c==='GRC'?'':'stroke-dasharray="10 6"'}/>`);
   for(const point of seg)out.push(`<circle cx="${x(point[0])}" cy="${y(point[1])}" r="${c==='GRC'?4:3}" fill="${escape(color)}"/>`);
  }
  if(!all.length)text((L+R)/2,(T+B)/2,el?'Δεν υπάρχουν παρατηρήσεις':'No observations in this period',24,muted,400,'text-anchor="middle"');
  const cols=portrait?3:6,legendW=(W-2*M)/cols;
  countries.forEach((c,i)=>{const xx=M+(i%cols)*legendW,yy=H-176+Math.floor(i/cols)*32;rect(xx,yy-9,22,5,countryInfo[c].color);text(xx+31,yy,label(countryInfo[c]),portrait?17:18,ink,c==='GRC'?700:400);});
  rect(M,H-116,W-2*M,1,'#dce5e9');
  const retrieved=new Intl.DateTimeFormat(el?'el-GR':'en-GB',{day:'numeric',month:'short',year:'numeric',timeZone:'UTC'}).format(new Date(m.retrievedAt));
  text(M,H-89,`${m.sourceName} · ${el?'Ανάκτηση':'Retrieved'} ${retrieved} · ${m.code}`,portrait?15:17,muted);
  text(M,H-64,m.sourceUrl,portrait?14:16,muted);
  const flags=[...new Set(countries.flatMap(c=>Object.entries(m.flags?.[c]||{}).filter(([yr])=>Number(yr)>=from&&Number(yr)<=to).map(([,flag])=>flag)))];
  const note=(el?'Τα κενά σημαίνουν απουσία δεδομένων. Οι μεταβολές δεν αποδεικνύουν αιτιότητα.':'Gaps mean unavailable data. Observed changes do not establish causation.')+(flags.length?` ${el?'Σημάνσεις πηγής':'Source flags'}: ${flags.join(', ')}.`:'');
  lines(M,H-38,note,portrait?14:16,W-2*M-205,muted);text(W-M,H-22,'www.datacritus.gr',18,navy,700,'text-anchor="end"');out.push('</svg>');
  return{svg:out.join(''),width:W,height:H};
 }
 const api={build};if(typeof module!=='undefined'&&module.exports)module.exports=api;else root.DatacritusInfographic=api;
})(typeof window!=='undefined'?window:globalThis);
