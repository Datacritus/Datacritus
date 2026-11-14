"""Generate lightweight, bilingual indicator pages from the validated snapshot."""
import csv
import io
import json
import math
from html import escape
from pathlib import Path
from urllib.parse import urlencode

ORIGIN = 'https://www.datacritus.gr'
ROOT = Path(__file__).resolve().parents[1]
COPY = {
    'en': dict(home='Home', hub='Greece statistics and indicators', explore='Explore the data',
               compare='Compare governments', source='Source', latest='Greece · latest observation',
               eu='European Union · same year', years='Observation years', trend='Annual trend',
               meaning='What does this indicator measure?', reading='How to read the figures',
               data='Annual observations and source flags', download='Download CSV',
               definition='Original provider definition', related='Explore related indicators',
               retrieved='Data retrieved', updated='Provider dataset updated', greece='Greece',
               year='Year', flags='Source flags', missing='Unavailable', unit='Unit',
               caveat='Changes during a government’s term do not establish that its policies caused them.',
               gaps='Missing years remain gaps. Lines use the same scale. The table provides the annual observations.',
               hubintro='Explore Greece’s jobs, prices, housing, health and public finances through sourced historical data. Each indicator includes definitions, annual observations and links to the original provider.',
               context='Annual data describe published observation years. Publication dates can lag behind the current year, and providers may revise historical values.',
               status='Source flags are retained as supplied. A flag may identify an estimate, provisional value or a break in series. Consult the provider for its exact meaning.',
               foot='An independent view of public data. Sources are credited, not endorsements.'),
    'el': dict(home='Αρχική', hub='Στατιστικά στοιχεία για την Ελλάδα', explore='Εξερεύνηση δεδομένων',
               compare='Σύγκριση κυβερνήσεων', source='Πηγή', latest='Ελλάδα · τελευταία παρατήρηση',
               eu='Ευρωπαϊκή Ένωση · ίδιο έτος', years='Έτη παρατήρησης', trend='Ετήσια εξέλιξη',
               meaning='Τι μετρά ο δείκτης;', reading='Πώς διαβάζονται τα στοιχεία',
               data='Ετήσιες παρατηρήσεις και σημάνσεις πηγής', download='Λήψη CSV',
               definition='Αρχικός ορισμός παρόχου', related='Εξερευνήστε σχετικούς δείκτες',
               retrieved='Ανάκτηση δεδομένων', updated='Ενημέρωση συνόλου παρόχου', greece='Ελλάδα',
               year='Έτος', flags='Σημάνσεις πηγής', missing='Μη διαθέσιμο', unit='Μονάδα',
               caveat='Οι μεταβολές κατά τη θητεία μιας κυβέρνησης δεν αποδεικνύουν ότι προκλήθηκαν από τις πολιτικές της.',
               gaps='Τα έτη χωρίς δεδομένα παραμένουν κενά. Οι γραμμές έχουν κοινή κλίμακα. Ο πίνακας περιέχει τις ετήσιες παρατηρήσεις.',
               hubintro='Εξερευνήστε την εργασία, τις τιμές, τη στέγαση, την υγεία και τα δημόσια οικονομικά της Ελλάδας μέσα από ιστορικά δεδομένα. Κάθε δείκτης περιλαμβάνει ορισμούς, ετήσια στοιχεία και πρόσβαση στον αρχικό πάροχο.',
               context='Τα ετήσια δεδομένα αφορούν τα δημοσιευμένα έτη παρατήρησης. Η δημοσίευση μπορεί να καθυστερεί και οι πάροχοι να αναθεωρούν ιστορικές τιμές.',
               status='Οι σημάνσεις διατηρούνται όπως παρέχονται από την πηγή. Μπορεί να δηλώνουν εκτίμηση, προσωρινή τιμή ή ασυνέχεια σειράς. Συμβουλευτείτε τον πάροχο για την ακριβή σημασία.',
               foot='Μια ανεξάρτητη ματιά στα δημόσια δεδομένα. Η αναφορά πηγών δεν αποτελεί έγκριση από τους φορείς.')
}


def page_path(lang, slug=''):
    return f'/{lang}/indicators/' + (slug + '/' if slug else '')


def finite_rows(metric, country):
    return sorted((y, value) for y, value in metric['series'].get(country, [])
                  if isinstance(value, (float, int)) and math.isfinite(value))


def number(value, lang):
    result = f'{value:,.2f}'.rstrip('0').rstrip('.')
    return result.translate(str.maketrans({',': '.', '.': ','})) if lang == 'el' else result


def chart(metric, lang):
    rows = {country: finite_rows(metric, country) for country in ['GRC', 'EUU']}
    values = [value for points in rows.values() for _, value in points]
    years = [year for points in rows.values() for year, _ in points]
    first, last = min(years), max(years)
    low, high = min(values), max(values)
    pad = (high-low)*.08 or 1
    low, high = low-pad, high+pad
    x = lambda year: 75+(year-first)/(last-first or 1)*805
    y = lambda value: 300-(value-low)/(high-low)*260
    parts = [f'<svg class="chart" viewBox="0 0 920 360" role="img" aria-labelledby="chart-title chart-desc"><title id="chart-title">{escape(metric["title"][lang])}</title><desc id="chart-desc">{escape(COPY[lang]["gaps"])}</desc>']
    for i in range(5):
        value = low+(high-low)*i/4
        parts.append(f'<path d="M75 {y(value):.2f}H880" stroke="#dce5e9"/><text x="66" y="{y(value)+5:.2f}" text-anchor="end" font-size="14" fill="#526a73">{escape(number(value,lang))}</text>')
    for year in sorted(set([first, last] + list(range((first//10+1)*10,last,10)))):
        parts.append(f'<text x="{x(year):.2f}" y="333" text-anchor="middle" font-size="14" fill="#526a73">{year}</text>')
    for country, color in [('GRC','#086a88'),('EUU','#93691e')]:
        segments, segment = [], []
        for point in rows[country]:
            if segment and point[0] != segment[-1][0]+1:
                segments.append(segment)
                segment = []
            segment.append(point)
        if segment:
            segments.append(segment)
        for segment in segments:
            path = ' '.join(f'{"M" if i==0 else "L"}{x(year):.2f},{y(value):.2f}' for i,(year,value) in enumerate(segment))
            dash = ' stroke-dasharray="7 4"' if country == 'EUU' else ''
            parts.append(f'<path d="{path}" fill="none" stroke="{color}" stroke-width="3"{dash}/>')
            for year,value in segment:
                parts.append(f'<circle cx="{x(year):.2f}" cy="{y(value):.2f}" r="2.8" fill="{color}"><title>{year} · {escape(number(value,lang))}</title></circle>')
    return ''.join(parts)+'</svg>'


def document(lang, title, description, path, alternate, body, schema):
    c = COPY[lang]
    other = 'el' if lang == 'en' else 'en'
    jsonld = json.dumps(schema,ensure_ascii=False).replace('<','\\u003c')
    return f'''<!doctype html>
<html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(title)} | DATACRITUS</title>
<meta name="description" content="{escape(description,quote=True)}">
<link rel="canonical" href="{ORIGIN}{path}">
<link rel="alternate" hreflang="{lang}" href="{ORIGIN}{path}">
<link rel="alternate" hreflang="{other}" href="{ORIGIN}{alternate}">
<link rel="alternate" hreflang="x-default" href="{ORIGIN}{path if lang=='en' else alternate}">
<meta property="og:type" content="website"><meta property="og:site_name" content="DATACRITUS">
<meta property="og:title" content="{escape(title,quote=True)}"><meta property="og:description" content="{escape(description,quote=True)}">
<meta property="og:url" content="{ORIGIN}{path}"><meta property="og:image" content="{ORIGIN}/logo.png">
<meta property="og:locale" content="{'el_GR' if lang=='el' else 'en_GB'}"><meta name="twitter:card" content="summary">
<link rel="stylesheet" href="/assets/indicators.css"><meta name="theme-color" content="#073b4c">
<script type="application/ld+json">{jsonld}</script></head><body>
<a class="skip" href="#main">{c['explore']}</a>
<header><div><a class="brand" href="/">DATACRITUS</a><nav aria-label="{'Πλοήγηση' if lang=='el' else 'Navigation'}"><a href="{page_path(lang)}">{c['hub']}</a><a href="/dashboard.html#lang={lang}">{c['explore']}</a><a href="{alternate}" lang="{other}" hreflang="{other}">{'Ελληνικά' if other=='el' else 'English'}</a></nav></div></header>
<main id="main">{body}</main><footer>{c['foot']} <a href="/dashboard.html#page=about&amp;lang={lang}">{'Μεθοδολογία' if lang=='el' else 'Methodology'}</a></footer></body></html>'''


def build():
    snapshot = json.loads((ROOT/'data/indicators.json').read_text())
    catalogue = {m['code']:m for m in snapshot['metrics']}
    entries = json.loads((ROOT/'scripts/seo_indicators.json').read_text())
    categories = {c['id']:c for c in snapshot['categories']}
    urls = ['/', '/dashboard.html']
    (ROOT/'data/seo').mkdir(parents=True,exist_ok=True)
    for entry in entries:
        metric = catalogue[entry['code']]
        rows = {country:dict(finite_rows(metric,country)) for country in ['GRC','EUU']}
        years = sorted(set(rows['GRC'])|set(rows['EUU']))
        if not rows['GRC']:
            raise ValueError('No Greek observations: '+entry['code'])
        output = io.StringIO(newline='')
        writer = csv.writer(output)
        writer.writerow(['year','Greece','European Union','unit','Greece flag','EU flag','source','source URL','retrieved'])
        for year in years:
            writer.writerow([year,rows['GRC'].get(year,''),rows['EUU'].get(year,''),metric['unit'],metric.get('flags',{}).get('GRC',{}).get(str(year),''),metric.get('flags',{}).get('EUU',{}).get(str(year),''),metric['sourceName'],metric['sourceUrl'],metric['retrievedAt']])
        (ROOT/f'data/seo/{entry["slug"]}.csv').write_text(output.getvalue(),encoding='utf-8')
        for lang in ['en','el']:
            c = COPY[lang]
            path = page_path(lang,entry['slug'])
            alternate = page_path('el' if lang=='en' else 'en',entry['slug'])
            unit = metric['unit']
            if lang == 'el':
                unit = {'%':'%', '% annual average price change':'% ετήσια μεταβολή μέσων τιμών',
                        'EUR per year':'ευρώ ανά έτος', '% of population':'% του πληθυσμού',
                        'years':'έτη', '% of people aged 16+':'% ατόμων ηλικίας 16+',
                        '% of GDP':'% του ΑΕΠ'}.get(unit,unit)
            latest = max(rows['GRC'])
            common = sorted(set(rows['GRC'])&set(rows['EUU']))
            dashboard = '/dashboard.html#'+urlencode(dict(indicator=metric['code'],lang=lang,page='explore'))
            comparison = '/dashboard.html#'+urlencode(dict(indicator=metric['code'],lang=lang,page='comparison'))
            stats = f'<div class="stat"><small>{c["latest"]} · {latest}</small><strong>{number(rows["GRC"][latest],lang)}</strong><span>{escape(unit)}</span></div>'
            if common:
                year = common[-1]
                stats += f'<div class="stat"><small>{c["eu"]} · {year}</small><strong>{number(rows["EUU"][year],lang)}</strong><span>{escape(unit)} · {c["greece"]} {number(rows["GRC"][year],lang)}</span></div>'
            table = ''
            for year in reversed(years):
                cells = ''.join(f'<td>{number(rows[country][year],lang) if year in rows[country] else "—"}</td>' for country in ['GRC','EUU'])
                flags = ' · '.join(f'{country}: {metric.get("flags",{}).get(country,{}).get(str(year),"")}' for country in ['GRC','EUU'] if metric.get('flags',{}).get(country,{}).get(str(year)))
                table += f'<tr><th scope="row">{year}</th>{cells}<td>{escape(flags) or "—"}</td></tr>'
            related = sorted((e for e in entries if e!=entry),key=lambda e:catalogue[e['code']]['categories'][0]!=metric['categories'][0])[:4]
            links = ''.join(f'<li><a href="{page_path(lang,e["slug"])}">{escape(e[lang])}</a></li>' for e in related)
            definition = metric.get('definitionEl') if lang=='el' else metric['definition']
            definition_html = f'<details><summary>{c["definition"]}</summary><p class="definition">{escape(definition or metric["definition"])}</p></details>'
            body = f'''<div class="breadcrumbs"><a href="/">{c['home']}</a><span>/</span><a href="{page_path(lang)}">{c['hub']}</a></div>
<h1>{escape(entry[lang])}</h1><p class="intro">{escape(entry['intro_'+lang])}</p>
<p class="meta">{c['source']} · <a href="{escape(metric['sourceUrl'],quote=True)}">{escape(metric['sourceName'])}</a> · {c['years']} {min(rows['GRC'])}–{max(rows['GRC'])}</p>
<div class="stats">{stats}</div><div class="actions"><a class="button" href="{escape(dashboard,quote=True)}">{c['explore']}</a><a class="button secondary" href="{escape(comparison,quote=True)}">{c['compare']}</a><a class="button secondary" href="/data/seo/{entry['slug']}.csv" download>{c['download']}</a></div>
<section class="panel"><h2>{c['trend']}</h2><p class="meta">{c['unit']} · {escape(unit)}</p>{chart(metric,lang)}<div class="legend"><span>{c['greece']}</span>{'<span class="eu">'+c['eu'].split(' · ')[0]+'</span>' if rows['EUU'] else ''}</div><p class="note">{c['gaps']}</p></section>
<div class="grid"><section class="panel"><h2>{c['meaning']}</h2><p>{escape(entry['meaning_'+lang])}</p>{definition_html}</section><section class="panel"><h2>{c['reading']}</h2><p>{escape(entry['caution_'+lang])}</p><p>{c['context']}</p><p class="note">{c['caveat']}</p></section></div>
<section class="panel"><h2>{escape(entry['question_'+lang])}</h2><p>{escape(entry['answer_'+lang])}</p></section>
<section class="panel"><details><summary>{c['data']}</summary><p class="note">{c['status']}</p><div class="table-wrap"><table><caption>{escape(entry[lang])} · {escape(unit)}</caption><thead><tr><th>{c['year']}</th><th>{c['greece']}</th><th>{c['eu'].split(' · ')[0]}</th><th>{c['flags']}</th></tr></thead><tbody>{table}</tbody></table></div></details></section>
<section class="panel"><h2>{c['source']}</h2><p><a class="source-link" href="{escape(metric['sourceUrl'],quote=True)}">{escape(metric['sourceName'])} · {escape(metric['code'])}</a></p><p class="meta">{c['retrieved']} · {escape(metric['retrievedAt'][:10])}<br>{c['updated']} · {escape(str(metric.get('sourceUpdatedAt') or '—')[:10])}</p>{'<p class="note">'+escape(metric['license'])+' · '+escape(metric.get('attribution',''))+'</p>' if metric.get('license') else ''}</section>
<h2>{c['related']}</h2><ul class="related">{links}</ul>'''
            dataset = dict(**{'@context':'https://schema.org','@type':'Dataset'},name=entry[lang],description=entry['meaning_'+lang],url=ORIGIN+path,identifier=metric['code'],inLanguage=lang,spatialCoverage={'@type':'Place','name':'Greece'},temporalCoverage=f'{min(rows["GRC"])}/{max(rows["GRC"])}',variableMeasured=metric['title'][lang],measurementTechnique=metric['definition'],isBasedOn=metric['sourceUrl'],citation=metric['sourceUrl'],distribution={'@type':'DataDownload','encodingFormat':'text/csv','contentUrl':ORIGIN+f'/data/seo/{entry["slug"]}.csv'})
            if metric.get('termsUrl'):
                dataset['license'] = metric['termsUrl']
            breadcrumb = {'@context':'https://schema.org','@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':1,'name':c['home'],'item':ORIGIN+'/'},{'@type':'ListItem','position':2,'name':c['hub'],'item':ORIGIN+page_path(lang)},{'@type':'ListItem','position':3,'name':entry[lang],'item':ORIGIN+path}]}
            target = ROOT/path.lstrip('/')/'index.html'
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_text(document(lang,entry['seo_title_'+lang],entry['description_'+lang],path,alternate,body,[dataset,breadcrumb]),encoding='utf-8')
            urls.append(path)
    for lang in ['en','el']:
        c = COPY[lang]
        body = f'<div class="breadcrumbs"><a href="/">{c["home"]}</a></div><h1>{c["hub"]}</h1><p class="intro">{c["hubintro"]}</p>'
        grouped = {}
        for entry in entries:
            category = catalogue[entry['code']]['categories'][0]
            grouped.setdefault(category,[]).append(entry)
        for category, group in grouped.items():
            links = ''.join(f'<li><a href="{page_path(lang,e["slug"])}">{escape(e[lang])}<small>{escape(e["meaning_"+lang])}</small></a></li>' for e in group)
            body += f'<section class="hub-group"><h2>{escape(categories[category]["title"][lang])}</h2><ul class="related">{links}</ul></section>'
        path = page_path(lang)
        target = ROOT/path.lstrip('/')/'index.html'
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_text(document(lang,c['hub'],c['hubintro'],path,page_path('el' if lang=='en' else 'en'),body,{'@context':'https://schema.org','@type':'CollectionPage','name':c['hub'],'url':ORIGIN+path,'inLanguage':lang}),encoding='utf-8')
        urls.append(path)
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    sitemap += ''.join(f'<url><loc>{ORIGIN}{escape(path)}</loc></url>' for path in urls)+'</urlset>\n'
    (ROOT/'sitemap.xml').write_text(sitemap,encoding='utf-8')
    print(f'Built {len(entries)*2} indicator pages, 2 language indexes and {len(entries)} CSV extracts')


if __name__ == '__main__':
    build()
