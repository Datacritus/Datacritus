/* Observed outcomes in cabinet periods; no causal score or political ranking. */
(function(root){
 'use strict';
 const C=typeof module!=='undefined'&&module.exports?require('./core.js'):root.DatacritusCore;
 const escape=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 const wrap=(s,n)=>{const lines=[];let line='';for(const word of String(s).split(/\s+/).flatMap(word=>word.length>n?word.match(new RegExp('.{1,'+n+'}','gu')):word)){if(line&&(line+' '+word).length>n){lines.push(line);line=word;}else line+=(line?' ':'')+word;}if(line)lines.push(line);return lines;};
 const label=(o,lang)=>typeof o==='object'?(o[lang]||o.en):o;
 const format=(n,lang)=>n==null?'—':new Intl.NumberFormat(lang==='el'?'el-GR':'en-GB',{maximumFractionDigits:Math.abs(n)>=1000?0:Math.abs(n)<10?4:2,notation:Math.abs(n)>=1e6?'compact':'standard'}).format(Object.is(n,-0)?0:n);
 function model({metric,terms,asOf}){
  if(!metric||!Array.isArray(terms)||terms.length!==2||!terms.every(Boolean))throw new Error('Choose a metric and two valid cabinet periods');
  const periods=terms.map(term=>{
   const stats=C.termStats(metric.series.GRC,term,asOf),observed=new Set(stats.points.map(p=>p[0]));
   const missing=stats.eligible.filter(y=>!observed.has(y));
   const mean=stats.points.length?stats.points.reduce((n,p)=>n+p[1],0)/stats.points.length:null;
   const flags=stats.points.filter(p=>metric.flags?.GRC?.[p[0]]).map(p=>({year:p[0],flag:metric.flags.GRC[p[0]]}));
   return{term,...stats,mean,missing,flags,uncertainty:metric.uncertainty?.GRC||{}};
  });
  return{metric,periods,asOf,sameTerm:terms[0].id===terms[1].id,ticks:C.axisTicks(periods.flatMap(p=>p.points.flatMap(x=>[x[1],...(p.uncertainty[x[0]]||[])])))};
 }
 function chart({period,ticks,color='#086a88',lang='en'}){
  const el=lang==='el',points=period.points,years=period.eligible;
  const W=600,H=220,L=74,R=22,T=22,B=166;
  let out=`<svg xmlns="http://www.w3.org/2000/svg" width="600" height="220" viewBox="0 0 600 220" role="img" font-family="Arial, sans-serif"><title>${escape(label(period.term.name,lang))} · ${escape(points.map(p=>p[0]).join(', '))}</title><desc>${escape(el?'Ίδια κατακόρυφη κλίμακα και για τις δύο περιόδους. Τα κενά παραμένουν.':'Both periods use the same vertical scale. Missing years remain gaps.')}</desc>`;
  if(!points.length)return out+`<text x="300" y="110" text-anchor="middle" fill="#526a73" font-size="22">${el?'Χωρίς διαθέσιμα πλήρη έτη':'No available full-year observations'}</text></svg>`;
  const lo=ticks[0],hi=ticks.at(-1),first=years[0],last=years.at(-1),x=y=>L+(y-first+.5)/(last-first+1)*(W-L-R),y=v=>B-(v-lo)/(hi-lo||1)*(B-T);
  for(const v of ticks)out+=`<line x1="${L}" x2="${W-R}" y1="${y(v)}" y2="${y(v)}" stroke="#dce5e9"/><text x="${L-10}" y="${y(v)+5}" text-anchor="end" fill="#526a73" font-size="17">${escape(format(v,lang))}</text>`;
  for(const year of [...new Set([first,last])])out+=`<text x="${x(year)}" y="${B+32}" text-anchor="middle" fill="#526a73" font-size="19">${year}</text>`;
  for(const segment of C.segments(points,first,last)){
   out+=`<path d="${segment.map((p,i)=>(i?'L':'M')+x(p[0]).toFixed(2)+','+y(p[1]).toFixed(2)).join(' ')}" fill="none" stroke="${escape(color)}" stroke-width="4" stroke-linecap="round"/>`;
   for(const p of segment){const b=period.uncertainty?.[p[0]];if(b)out+=`<line x1="${x(p[0])}" x2="${x(p[0])}" y1="${y(b[0])}" y2="${y(b[1])}" stroke="${escape(color)}" stroke-width="2" opacity=".35"/>`;out+=`<circle cx="${x(p[0])}" cy="${y(p[1])}" r="5" fill="${escape(color)}"><title>${p[0]}: ${escape(format(p[1],lang))}</title></circle>`;}
  }
  return out+'</svg>';
 }
 function build({comparison,lang='en',format:layout='landscape',logoUri=''}){
  const el=lang==='el',portrait=layout==='portrait',W=portrait?1080:1600,H=portrait?1740:1100,M=52;
  const {metric:m,periods,asOf}=comparison,ink='#123b48',muted='#526a73',navy='#073b4c',gold='#ffd166';
  const credit=[m.license,m.attribution,m.sourceVersion].filter(Boolean).join(' · '),creditSize=portrait?15:17,creditHeight=wrap(credit,Math.max(12,Math.floor((W-2*M)/(creditSize*.6)))).length*creditSize*1.3,noteY=H+18+creditHeight+14,exportH=H+(m.license?Math.max(150,Math.ceil(noteY-H+70)):0);
  const out=[`<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${exportH}" viewBox="0 0 ${W} ${exportH}" font-family="Arial, sans-serif" role="img"><title>${escape(label(m.title,lang))}: ${escape(periods.map(p=>label(p.term.name,lang)).join(' vs '))}</title><desc>${escape(el?'Σύγκριση παρατηρούμενων τιμών σε πλήρη ημερολογιακά έτη. Δεν αποτελεί αιτιώδη αξιολόγηση.':'Comparison of observed values in full calendar years. Not a causal assessment.')}</desc>`];
  const rect=(x,y,w,h,fill,rx=0)=>out.push(`<rect x="${x}" y="${y}" width="${w}" height="${h}" fill="${fill}" rx="${rx}"/>`);
  const text=(x,y,s,size=24,color=ink,weight=400,extra='')=>out.push(`<text x="${x}" y="${y}" font-size="${size}" fill="${color}" font-weight="${weight}" ${extra}>${escape(s)}</text>`);
  const lines=(x,y,s,size,width,color=ink,weight=400)=>wrap(s,Math.max(12,Math.floor(width/(size*.6)))).forEach((v,i)=>text(x,y+i*size*1.3,v,size,color,weight));
  rect(0,0,W,exportH,'#fff');rect(0,0,W,242,navy);rect(0,242,W,5,gold);
  if(logoUri)out.push(`<image href="${escape(logoUri)}" x="${M}" y="20" width="285" height="85" preserveAspectRatio="xMidYMid slice"/>`);else text(M,77,'DATACRITUS',36,gold,700);
  text(W-M,72,el?'ΣΥΓΚΡΙΣΗ ΚΥΒΕΡΝΗΣΕΩΝ':'GOVERNMENT COMPARISON',portrait?19:24,'#cce0e6',600,'text-anchor="end"');
  const title=label(m.title,lang);let size=portrait?39:44;while(size>22&&wrap(title,Math.floor((W-2*M)/(size*.85))).length>2)size-=2;
  wrap(title,Math.floor((W-2*M)/(size*.85))).forEach((line,i)=>text(M,145+i*size*1.12,line,size,'#fff',700));
  const nominal=m.unit.includes('EUR')||m.unit.includes('current');
  text(M,222,`${el?'Ελλάδα':'Greece'} · ${m.unit}${nominal?' · '+(el?'ονομαστικές τιμές':'nominal values'):''}`,portrait?21:24,'#cce0e6');
  const cw=portrait?W-2*M:(W-2*M-24)/2,ch=portrait?594:602;
  periods.forEach((p,i)=>{
   const x=portrait?M:M+i*(cw+24),y=portrait?273+i*(ch+22):273,color=i===0?'#086a88':'#93691e';
   rect(x,y,cw,ch,'#f1f6f7',18);rect(x,y,7,ch,color,3);
   text(x+26,y+38,i===0?(el?'ΠΕΡΙΟΔΟΣ Α':'PERIOD A'):(el?'ΠΕΡΙΟΔΟΣ Β':'PERIOD B'),18,color,700);
   lines(x+26,y+79,label(p.term.name,lang),portrait?33:31,cw-52,ink,700);
   text(x+26,y+140,`${p.term.start} → ${p.term.end||(el?'σε εξέλιξη':'ongoing')}`,20,muted);
   lines(x+26,y+171,label(p.term.coalition,lang),18,cw-52,muted);
   text(x+26,y+229,el?'ΜΕΣΟΣ ΟΡΟΣ ΠΑΡΑΤΗΡΗΣΕΩΝ':'OBSERVED ANNUAL AVERAGE',18,muted,600);
   text(x+26,y+279,format(p.mean,lang),48,navy,700);
   const dx=(cw-52)/3;
   const cells=[{name:el?'Πρώτη':'First',value:p.first?.[1],year:p.first?.[0]},{name:el?'Τελευταία':'Last',value:p.last?.[1],year:p.last?.[0]},{name:el?'Μεταβολή':'Change',value:p.delta,year:m.change==='pp'?(el?'π.μ.':'pp'):(el?'ίδιες μονάδες':'same unit')}];
   cells.forEach((c,j)=>{const xx=x+26+j*dx;text(xx,y+317,c.name+(j<2&&c.year?' · '+c.year:''),18,muted);text(xx,y+351,(j===2&&c.value>0?'+':'')+format(c.value,lang),30,ink,700);if(j===2)lines(xx,y+377,c.year,15,dx-12,muted);});
   const svg=chart({period:p,ticks:comparison.ticks,color,lang}).replace('width="600" height="220"',`x="${x+18}" y="${y+391}" width="${cw-36}" height="160"`);out.push(svg);
   const years=p.points.map(v=>v[0]).join(', ')||'—';lines(x+26,y+566,`${el?'Έτη':'Years'}: ${years} · ${p.points.length}/${p.eligible.length} ${el?'παρατηρήσεις':'observations'}`,16,cw-52,muted);
  });
  const footer=portrait?1528:910;rect(M,footer-18,W-2*M,1,'#dce5e9');
  lines(M,footer+10,el?'Πλήρη ημερολογιακά έτη μόνο · ίδια κατακόρυφη κλίμακα · τα κενά δεν συμπληρώνονται.':'Full calendar years only · shared vertical scale · missing years remain gaps.',portrait?19:21,W-2*M,muted);
  const flags=[...new Set(periods.flatMap(p=>p.flags.map(f=>f.flag)))];
  lines(M,footer+68,`${m.sourceName} · ${m.code} · ${el?'Ανάκτηση':'Retrieved'} ${m.retrievedAt.slice(0,10)}${flags.length?' · '+(el?'Σημάνσεις':'Flags')+': '+flags.join(', '):''}`,portrait?14:16,W-2*M,muted);
  text(M,footer+96,m.sourceUrl,portrait?15:17,muted);
  text(M,footer+123,`${el?'Χρονολόγιο ελέγχθηκε':'Timeline verified'}: ${asOf} · gslegal.gov.gr`,portrait?16:18,muted);
  lines(M,footer+151,el?'Οι μεταβολές κατά τη θητεία δεν αποδεικνύουν αιτιότητα.':'Changes during a term do not establish causation.',portrait?18:20,W-2*M-220,muted);
  if(m.license){out.push(`<a href="${escape(m.termsUrl)}" target="_blank">`);lines(M,H+18,credit,creditSize,W-2*M,muted);out.push('</a>');lines(M,noteY,m.uncertaintyLevel?(el?'Ερευνητικές εκτιμήσεις · ετήσια όρια αβεβαιότητας 68%, όχι όρια μέσου όρου θητείας.':'Research estimates · annual 68% uncertainty bounds, not intervals for term averages.'):(el?'Διατηρήστε την αναφορά πηγής και τους όρους άδειας κατά την αναδημοσίευση.':'Retain source attribution and licence terms when republishing.'),portrait?16:18,W-2*M,muted);}
  text(W-M,H-24,'www.datacritus.gr',19,navy,700,'text-anchor="end"');out.push('</svg>');
  return{svg:out.join(''),width:W,height:exportH};
 }
 function csv(comparison){
  const m=comparison.metric,rows=[['indicator_code','indicator','period_id','government','term_start','term_end','year','value','unit','source_status','source_url','retrieved_at','timeline_verified_at','uncertainty_low','uncertainty_high','uncertainty_level','source_version','licence','terms_url','attribution']];
  for(const p of comparison.periods){const values=new Map(p.points);for(const year of p.eligible)rows.push([m.code,m.providerTitle,p.term.id,p.term.name.en,p.term.start,p.term.end||'',year,values.get(year)??'',m.unit,m.flags?.GRC?.[year]||'',m.sourceUrl,m.retrievedAt,comparison.asOf,...(m.uncertainty?.GRC?.[year]||['','']),m.uncertaintyLevel??'',m.sourceVersion||'',m.license||'',m.termsUrl||'',m.attribution||'']);}
  return C.csv(rows);
 }
 const api={model,chart,build,csv};if(typeof module!=='undefined'&&module.exports)module.exports=api;else root.DatacritusGovernmentComparison=api;
})(typeof window!=='undefined'?window:globalThis);
