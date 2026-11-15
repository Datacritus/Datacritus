"""Render crawlable language-specific homepages from the shared landing template."""
import re
from html import escape
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ORIGIN='https://www.datacritus.gr'
def render_homepages(landing):
    block=re.search(r"const copy=\{en:\{(.*?)\},el:\{(.*?)\}\};",landing,re.S)
    if not block:
        raise ValueError('Missing bilingual landing copy')
    for lang,part in zip(('en','el'),block.groups()):
        copy=dict(re.findall(r"(\w+):'([^']*)'",part))
        page=re.sub(r'<html lang="[^"]*">',f'<html lang="{lang}">',landing,count=1)
        for key in ('label','motto','description','metrics','enter','compare','challenge','footer'):
            pattern=r'(<[^>]+id="dp-'+key+r'"[^>]*>).*?(</(?:div|h1|p|span|a)>)'
            page,n=re.subn(pattern,lambda m:m[1]+copy[key]+m[2],page,count=1,flags=re.S)
            if n!=1: raise ValueError('Missing landing element '+key)
        def translate(m):
            return m[1]+escape(copy.get(m[2],m[3]))+m[4]
        page=re.sub(r'(<(?:strong|small|span|h2)[^>]*data-tool-copy="([^"]+)"[^>]*>)(.*?)(</(?:strong|small|span|h2)>)',translate,page,flags=re.S)
        title=('Στατιστικά για την Ελλάδα και συγκρίσεις κυβερνήσεων' if lang=='el' else 'Greece Statistics &amp; Government Comparisons')+' | DATACRITUS'
        description=copy['description']
        page=re.sub(r'<title>.*?</title>','<title>'+title+'</title>',page,count=1)
        page=re.sub(r'(<meta (?:name="description"|property="og:description") content=")[^"]*',lambda m:m[1]+escape(description,quote=True),page)
        page=re.sub(r'(<meta property="og:title" content=")[^"]*',lambda m:m[1]+title,page)
        url=ORIGIN+'/'+lang+'/'
        page=page.replace('<link rel="canonical" href="'+ORIGIN+'/">','<link rel="canonical" href="'+url+'">')
        page=page.replace('property="og:url" content="'+ORIGIN+'/"','property="og:url" content="'+url+'"')
        alternates=''.join('<link rel="alternate" hreflang="'+code+'" href="'+ORIGIN+path+'">' for code,path in [('el','/el/'),('en','/en/'),('x-default','/')])
        page=page.replace('</head>',alternates+'</head>')
        page=page.replace('href="dashboard.html','href="/dashboard.html').replace("'dashboard.html","'/dashboard.html").replace("fetch('data/","fetch('/data/")
        page=page.replace('data-lang="en"',f'data-lang="{lang}"')
        other='en' if lang=='el' else 'el'
        page=re.sub(r'<button type="button" class="dp-lang"[^>]*>.*?</button>',f'<a class="dp-lang" href="/{other}/" aria-label="Switch language to {other}">'+('EN' if lang=='el' else 'ΕΛ')+'</a>',page,count=1)
        page=page.replace('<body>','<body><style>html[lang="'+lang+'"] .seo-'+other+',html[lang="'+lang+'"] .ds-copy-'+other+'{display:none}</style>',1)
        target=ROOT/lang/'index.html'
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_text(page,encoding='utf-8')
        if lang=='el':
            (ROOT/'index.html').write_text(page,encoding='utf-8')
