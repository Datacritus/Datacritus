#!/usr/bin/env python3
"""Build a standalone GitHub Pages index. No npm or remote browser dependencies."""
import base64,json,shutil
from build_random_home import render as render_random
from build_seo import build as build_seo, chart as history_chart
from build_homepages import render_homepages
from pathlib import Path
from build_history import build as build_history
from build_landing_sources import render as render_sources
ROOT=Path(__file__).resolve().parents[1]
def build():
    build_history()
    template=(ROOT/'src/index.html').read_text()
    template=template.replace('/*__LOGO__*/','data:image/png;base64,'+base64.b64encode((ROOT/'logo.png').read_bytes()).decode())
    for marker,path in [('STYLE','src/style.css'),('DATA','data/indicators.json'),('HISTORY','data/history.json'),('CORE','src/core.js'),('INFOGRAPHIC','src/infographic.js'),('GOVCOMPARISON','src/government-comparison.js'),('APP','src/app.js')]:
        value=(ROOT/path).read_text()
        if marker=='DATA':
            payload=json.loads(value)
            definitions=json.loads((ROOT/'scripts/definitions_el.json').read_text())
            for item in payload['metrics']:
                if item['code'] in definitions:item['definitionEl']=definitions[item['code']]
            value=json.dumps(payload,ensure_ascii=False,separators=(',',':'))
        if marker in ('DATA','HISTORY'):value=value.replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
        if marker in ('CORE','INFOGRAPHIC','GOVCOMPARISON','APP') and '</script' in value.lower():raise ValueError('Unsafe inline script closing tag')
        template=template.replace('/*__'+marker+'__*/',value)
    if '/*__' in template:raise ValueError('Unresolved build marker')
    (ROOT/'dashboard.html').write_text(template,encoding='utf-8')
    landing=(ROOT/'src/landing.html').read_text().replace('/*__LOGO__*/','data:image/png;base64,'+base64.b64encode((ROOT/'logo.png').read_bytes()).decode())
    snapshot=json.loads((ROOT/'data/indicators.json').read_text())
    landing=landing.replace('/*__SOURCES__*/',render_sources(snapshot)).replace('/*__SOURCES_STYLE__*/',(ROOT/'src/landing-sources.css').read_text()).replace('/*__SOURCES_JS__*/',(ROOT/'src/landing-sources.js').read_text())
    pool=render_random(snapshot,json.loads((ROOT/'data/history.json').read_text()))
    random_script=(ROOT/'src/landing-random.js').read_text().replace('/*__RANDOM_POOL__*/',pool)
    landing=landing.replace('</div>\n</body>', '<script>'+random_script+'</script>\n</div>\n</body>')
    metrics={m['code']:m for m in snapshot['metrics']}
    unemployment=dict(metrics['SL.UEM.TOTL.ZS']['series']['GRC'])
    # Use the same term boundaries and full-calendar-year rule as the comparison tool.
    history=json.loads((ROOT/'data/history.json').read_text())
    comparison_markers={}
    for slot,term_id in [('A','2015-09-21'),('B','2019-07-08')]:
        term=next(g for g in history['governments'] if g['id']==term_id)
        years=[y for y in range(int(term['start'][:4]),int(term['end'][:4])+1)
               if term['start']<=f'{y}-01-01' and term['end']>=f'{y+1}-01-01']
        if not years or any(unemployment.get(y) is None for y in years):
            raise ValueError('Incomplete homepage comparison data: '+term_id)
        prefix='UNEMP_'+slot
        comparison_markers.update({prefix:f'{sum(unemployment[y] for y in years)/len(years):.1f}',
            prefix+'_ID':term_id,prefix+'_NAME_EN':term['name']['en'],prefix+'_NAME_EL':term['name']['el'],
            prefix+'_GOVERNMENT_EN':term['coalition']['en'],prefix+'_GOVERNMENT_EL':term['coalition']['el'],
            prefix+'_TERM':term['start'][:4]+'–'+term['end'][:4],
            prefix+'_YEARS':str(years[0])+'–'+str(years[-1])})
    landing=landing.replace('/*__HISTORY_CHART__*/',history_chart(metrics['SL.UEM.TOTL.ZS'],'en'))
    internet=[p for p in metrics['ESTAT.INTERNET.HOUSEHOLDS']['series']['GRC'] if p[1] is not None][-1]
    for marker,value in {'KPI_COUNT':len(metrics),**comparison_markers,'INTERNET':f"{internet[1]:.2f}",'INTERNET_YEAR':internet[0]}.items():
        landing=landing.replace('/*__'+marker+'__*/',str(value))
    if '/*__' in landing:raise ValueError('Unresolved landing marker')
    (ROOT/'index.html').write_text(landing,encoding='utf-8')
    (ROOT/'.nojekyll').touch()
    (ROOT/'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: https://www.datacritus.gr/sitemap.xml\n')
    build_seo()
    render_homepages(landing,metrics['SL.UEM.TOTL.ZS'])
    print('Built dashboard.html:',len(template.encode()),'bytes')
if __name__=='__main__':build()
