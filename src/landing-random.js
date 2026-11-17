(() => {
  const groups = /*__RANDOM_POOL__*/;
  const card = document.querySelector('[data-tool-page="comparison"]');
  if (!groups.length || !card) return;
  const button = document.createElement('button');
  button.type = 'button';
  button.className = 'dp-random-button';
  card.after(button);
  const greekUnits = {"constant 2015 US$":"δολάρια ΗΠΑ, σε σταθερές τιμές 2015","0–100 index":"δείκτης 0–100","% of population":"% του πληθυσμού","EUR per year":"ευρώ ανά έτος","% of children under 18":"% των παιδιών κάτω των 18","% of disposable household income":"% του διαθέσιμου εισοδήματος νοικοκυριών","% annual average price change":"% ετήσια μέση μεταβολή τιμών","index (0–1)":"δείκτης 0–1","% of population ages 15–24":"% του πληθυσμού 15–24 ετών","% of labour force ages 15–74":"% του εργατικού δυναμικού 15–74 ετών","% of employed people aged 18+":"% των εργαζομένων 18 ετών και άνω","% of part-time workers aged 20–64":"% των εργαζομένων μερικής απασχόλησης 20–64 ετών","hours per week":"ώρες την εβδομάδα","index (2020=100)":"δείκτης (2020=100)","years":"έτη","per 1,000 live births":"ανά 1.000 γεννήσεις ζώντων","per 1,000 people":"ανά 1.000 άτομα","% of GDP":"% του ΑΕΠ","% of current health expenditure":"% των τρεχουσών δαπανών υγείας","% of people aged 16+":"% των ατόμων 16 ετών και άνω","pupils per teacher":"μαθητές ανά εκπαιδευτικό","% of population ages 18–24":"% του πληθυσμού 18–24 ετών","% of population ages 25–34":"% του πληθυσμού 25–34 ετών","% of recent graduates aged 20–34":"% των πρόσφατων αποφοίτων 20–34 ετών","t CO₂e/person":"τόνοι ισοδυνάμου CO₂ ανά άτομο","% of final energy consumption":"% της τελικής κατανάλωσης ενέργειας","% of electricity output":"% της παραγωγής ηλεκτρικής ενέργειας","% of energy use":"% της χρήσης ενέργειας","% of municipal waste":"% των αστικών αποβλήτων","arrivals":"αφίξεις","current US$":"δολάρια ΗΠΑ, σε τρέχουσες τιμές","per 100,000 people":"ανά 100.000 άτομα","WGI estimate":"εκτίμηση WGI","births per woman":"γεννήσεις ανά γυναίκα","% of households":"% των νοικοκυριών"};
  let current;
  const pick = items => items[Math.floor(Math.random() * items.length)];
  function draw() {
    const metrics = groups.flat();
    const available = metrics.filter(metric => metric.code !== current?.metric.code);
    current = {metric: pick(available.length ? available : metrics)};
    current.pair = pick(current.metric.pairs).map(index => current.metric.periods[index]);
    update();
  }
  function update() {
    const lang = document.documentElement.lang === 'el' ? 'el' : 'en';
    const el = lang === 'el';
    const metric = current.metric;
    const text = value => typeof value === 'object' ? value[lang] || value.en : value;
    const format = value => new Intl.NumberFormat(el ? 'el-GR' : 'en-GB', {maximumFractionDigits:2}).format(value);
    const art = card.querySelector('.dp-tool-art');
    art.replaceChildren();
    const heading = document.createElement('strong');
    heading.textContent = text(metric.title);
    art.append(heading);
    const note = document.createElement('span');
    note.className = 'dp-mini-label';
    note.textContent = el ? 'ΤΥΧΑΙΑ ΣΥΓΚΡΙΣΗ · ΕΤΗΣΙΑ ΕΞΕΛΙΞΗ' : 'RANDOM COMPARISON · ANNUAL TREND';
    art.append(note);
    for (const period of current.pair) {
      const row = document.createElement('div');
      row.className = 'dp-random-period';
      const leader = document.createElement('strong');
      leader.className = 'dp-random-government';
      leader.textContent = text(period.government || period.party);
      const name = document.createElement('span');
      const term = period.termYears[0] + '–' + (period.ongoing ? (el ? 'σήμερα' : 'present') : period.termYears[1]);
      const pm = text(period.name);
      name.textContent = pm + (el ? ' · Κυβέρνηση ' : ' · Government ') + term + (el ? ' · πλήρη έτη ' : ' · full years ') + period.years[0] + '–' + period.years.at(-1);
      const value = document.createElement('strong');
      value.textContent = format(period.first) + ' → ' + format(period.last) + ' ' + (el ? greekUnits[metric.unit] || metric.unit : metric.unit);
      const summary = document.createElement('small');
      const delta = period.last-period.first;
      const changeUnit = metric.unit.startsWith('%') ? (el ? 'π.μ.' : 'pp') : (el ? greekUnits[metric.unit] || metric.unit : metric.unit);
      summary.textContent = (el ? 'Μεταβολή: ' : 'Change: ') + (delta>0?'+':'') + format(delta) + ' ' + changeUnit + (el ? ' · Μέσος όρος: ' : ' · Average: ') + format(period.mean);

      row.append(leader,name,value,summary);
      art.append(row);
    }
    if (metric.history?.length > 1) {
      const rows = metric.history, first=rows[0][0], last=rows.at(-1)[0];
      const values=rows.map(p=>p[1]), low=Math.min(...values), high=Math.max(...values), pad=(high-low)*.12||1;
      const x=year=>100+(year-first)/(last-first+1)*446;
      const y=value=>124-(value-low+pad)/(high-low+2*pad)*94;
      let svg='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 580 160">';
      current.pair.forEach((period,i)=>{const fraction=s=>{const d=new Date(s+'T00:00:00Z'),yr=d.getUTCFullYear();return yr+(d-new Date(Date.UTC(yr,0,1)))/(new Date(Date.UTC(yr+1,0,1))-new Date(Date.UTC(yr,0,1)));};const left=Math.max(first,fraction(period.start)),right=Math.min(last,fraction(period.end));svg+='<rect x="'+x(left)+'" y="16" width="'+Math.max(0,x(right)-x(left))+'" height="114" fill="'+(i?'#93691e':'#086a88')+'" opacity=".13"/>';});
      for(const value of [low,high])svg+='<text x="3" y="'+(y(value)+4)+'" fill="#123b48" font-family="Arial" font-size="13">'+format(value)+'</text>';
      let previous;
      for(const point of rows){if(previous&&point[0]===previous[0]+1)svg+='<path d="M'+x(previous[0]+.5)+','+y(previous[1])+'L'+x(point[0]+.5)+','+y(point[1])+'" stroke="#073b4c" stroke-width="3" fill="none"/>';previous=point;}
      for(const year of [first,last])svg+='<text x="'+x(year+.5)+'" y="150" text-anchor="middle" fill="#123b48" font-family="Arial" font-size="14">'+year+'</text>';
      svg+='</svg>';
      const trend=document.createElement('img');trend.src='data:image/svg+xml;charset=utf-8,'+encodeURIComponent(svg);trend.alt=(el?'Πλήρης ιστορική εξέλιξη. Σκιασμένες οι δύο επιλεγμένες κυβερνήσεις.':'Full historical trend. Shading marks the two selected governments.')+' '+metric.unit;trend.style.width='100%';trend.style.height='auto';art.append(trend);
      const context=document.createElement('small');context.textContent=el?'Πλήρης διαθέσιμη ιστορία · μπλε σκίαση: πρώτη κυβέρνηση · χρυσή: δεύτερη':'Full available history · blue shading: first government · gold: second';art.append(context);
    }
    const source = document.createElement('small');
    source.textContent = el && metric.source.startsWith('ILO modelled') ? 'Μοντελοποιημένη εκτίμηση ILO, μέσω World Bank WDI' : metric.source;
    art.append(source);
    const caveat = document.createElement('small');
    caveat.className = 'dp-random-note';
    caveat.textContent = el ? 'Πρώτες/τελευταίες παρατηρήσεις και μέσοι όροι πλήρων ετών μέσα σε κάθε κυβερνητική περίοδο· εξαιρούνται τα έτη αλλαγής κυβέρνησης. Εξωτερικά γεγονότα (π.χ. COVID-19) και η καθυστερημένη επίδραση πολιτικών επίσης επηρεάζουν τα αποτελέσματα· η σύγκριση δεν αποδεικνύει αιτιότητα.' : 'First/last observations and averages use full years within each government period; transition years are excluded. External events (such as COVID-19) and policy lags also affect outcomes; the comparison does not establish cause.';
    art.append(caveat);
    const query = new URLSearchParams({page:'comparison',indicator:metric.code,periodA:current.pair[0].id,periodB:current.pair[1].id,lang});
    card.href = '/dashboard.html#' + query;
    button.textContent = el ? 'Άλλη τυχαία σύγκριση' : 'Try another comparison';
  }
  button.addEventListener('click',draw);
  document.querySelector('.dp-lang').addEventListener('click',update);
  draw();

  const previewCard = document.querySelector('[data-tool-page="infographic"]');
  if (previewCard) {
    const previewButton = document.createElement('button');
    previewButton.type = 'button';
    previewButton.className = 'dp-random-button';
    previewCard.after(previewButton);
    let previewMetric;
    const previewMetrics = groups.flat().filter(metric => Array.isArray(metric.latest));
    function drawPreview() {
      const available = previewMetrics.filter(metric => metric.code !== previewMetric?.code && metric.code !== current?.metric.code);
      previewMetric = pick(available.length ? available : previewMetrics);
      if (!previewMetric) return;
      renderPreview();
    }
    function renderPreview() {
      if (!previewMetric) return;
      const el = document.documentElement.lang === 'el';
      const lang = el ? 'el' : 'en';
      const metric = previewMetric;
      const [year, value] = metric.latest;
      const art = previewCard.querySelector('.dp-tool-art');
      art.replaceChildren();
      const panel = document.createElement('div');
      panel.className = 'dp-export-preview';
      const brand = document.createElement('span');
      brand.textContent = 'DATACRITUS / ' + (el ? 'ΕΛΛΑΔΑ' : 'GREECE') + ' / ' + year;
      const figure = document.createElement('b');
      figure.textContent = new Intl.NumberFormat(el ? 'el-GR' : 'en-GB', {maximumFractionDigits:2}).format(value);
      figure.style.fontSize = 'clamp(25px,3vw,42px)';
      const unit = document.createElement('small');
      unit.textContent = el ? greekUnits[metric.unit] || metric.unit : metric.unit;
      const title = document.createElement('strong');
      title.textContent = metric.title[lang] || metric.title.en;
      const source = document.createElement('span');
      source.textContent = el && metric.source.startsWith('ILO modelled') ? 'Μοντελοποιημένη εκτίμηση ILO, μέσω World Bank WDI' : metric.source;
      panel.append(brand,figure,unit,title,source);
      art.append(panel);
      previewCard.href = '/dashboard.html#' + new URLSearchParams({page:'explore',indicator:metric.code,lang});
      previewButton.textContent = el ? 'Άλλος δείκτης σε μια ματιά' : 'Preview another indicator';
    }
    previewButton.addEventListener('click', drawPreview);
    document.querySelector('.dp-lang').addEventListener('click', renderPreview);
    drawPreview();
  }

})();
