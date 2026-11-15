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
    note.textContent = el ? 'ΤΥΧΑΙΑ ΣΥΓΚΡΙΣΗ · ΜΕΣΟΣ ΟΡΟΣ' : 'RANDOM COMPARISON · ANNUAL AVERAGE';
    art.append(note);
    for (const period of current.pair) {
      const row = document.createElement('div');
      row.className = 'dp-random-period';
      const name = document.createElement('span');
      name.textContent = text(period.name) + ' · ' + period.years[0] + '–' + period.years.at(-1);
      const value = document.createElement('strong');
      value.textContent = format(period.mean) + ' ' + (el ? greekUnits[metric.unit] || metric.unit : metric.unit);
      row.append(name,value);
      art.append(row);
    }
    const source = document.createElement('small');
    source.textContent = metric.source;
    art.append(source);
    const query = new URLSearchParams({page:'comparison',indicator:metric.code,periodA:current.pair[0].id,periodB:current.pair[1].id,lang});
    card.href = 'dashboard.html#' + query;
    button.textContent = el ? 'Άλλη τυχαία σύγκριση' : 'Try another comparison';
  }
  button.addEventListener('click',draw);
  document.querySelector('.dp-lang').addEventListener('click',update);
  draw();
})();
