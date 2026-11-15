"""Render crawlable language-specific homepages from the shared landing template."""
import re
from html import escape
from html.parser import HTMLParser
from urllib.parse import parse_qsl, urlencode

class LanguageHTML(HTMLParser):
    def __init__(self, other):
        super().__init__(convert_charrefs=False)
        self.other=other; self.skip=0; self.parts=[]
    def handle_starttag(self, tag, attrs):
        classes=dict(attrs).get('class','').split()
        if self.skip or any(c in classes for c in ('seo-'+self.other,'ds-copy-'+self.other)):
            if tag not in ('area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'): self.skip+=1
            return
        self.parts.append(self.get_starttag_text())
    def handle_endtag(self, tag):
        if self.skip: self.skip-=1
        else: self.parts.append('</'+tag+'>')
    def handle_data(self, data):
        if not self.skip:self.parts.append(data)
    def handle_entityref(self, name):
        if not self.skip:self.parts.append('&'+name+';')
    def handle_charref(self, name):
        if not self.skip:self.parts.append('&#'+name+';')
    def handle_decl(self, decl):
        self.parts.append('<!'+decl+'>')
    def handle_comment(self, data):
        if not self.skip:self.parts.append('<!--'+data+'-->')

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
        parser=LanguageHTML(other)
        parser.feed(page)
        page=''.join(parser.parts)
        def dashboard_link(match):
            fragment=match[1].replace('&amp;','&')
            query=dict(parse_qsl(fragment))
            query['lang']=lang
            return 'href="/dashboard.html#'+escape(urlencode(query),quote=True)+'"'
        page=re.sub(r'href="/dashboard.html#([^"]*)"',dashboard_link,page)
        page=page.replace('class="dp-logo" href="./"',f'class="dp-logo" href="/{lang}/"')
        if lang=='el':
            page=page.replace('GREECE · DEMOCRACY','ΕΛΛΑΔΑ · ΔΗΜΟΚΡΑΤΙΑ').replace('ILO estimates via World Bank','Εκτιμήσεις ILO μέσω Παγκόσμιας Τράπεζας')
            page=re.sub(r'(<b>)(\d+)\.(\d+)(%</b>)',r'\1\2,\3\4',page)
        target=ROOT/lang/'index.html'
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_text(page,encoding='utf-8')
        if lang=='el':
            (ROOT/'index.html').write_text(page,encoding='utf-8')
