(() => {
  const groups = /*__RANDOM_POOL__*/;
  const card = document.querySelector('[data-tool-page="comparison"]');
  if (!groups.length || !card) return;
  const button = document.createElement('button');
  button.type = 'button';
  button.className = 'dp-random-button';
  card.after(button);
  let current;
  const pick = items => items[Math.floor(Math.random() * items.length)];
  function draw() {
    current = {metric: pick(pick(groups))};
    current.pair = pick(current.metric.pairs);
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
      value.textContent = format(period.mean) + ' ' + metric.unit;
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
