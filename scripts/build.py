#!/usr/bin/env python3
"""Build a standalone GitHub Pages index. No npm or remote browser dependencies."""
import json,shutil
from pathlib import Path
from build_history import build as build_history
ROOT=Path(__file__).resolve().parents[1]
def build():
    build_history()
    template=(ROOT/'src/index.html').read_text()
    for marker,path in [('STYLE','src/style.css'),('DATA','data/indicators.json'),('HISTORY','data/history.json'),('CORE','src/core.js'),('APP','src/app.js')]:
        value=(ROOT/path).read_text()
        if marker in ('DATA','HISTORY'):value=value.replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
        if marker in ('CORE','APP') and '</script' in value.lower():raise ValueError('Unsafe inline script closing tag')
        template=template.replace('/*__'+marker+'__*/',value)
    if '/*__' in template:raise ValueError('Unresolved build marker')
    (ROOT/'index.html').write_text(template,encoding='utf-8')
    (ROOT/'.nojekyll').touch()
    (ROOT/'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: https://www.datacritus.gr/sitemap.xml\n')
    (ROOT/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://www.datacritus.gr/</loc></url></urlset>\n')
    print('Built index.html:',len(template.encode()),'bytes')
if __name__=='__main__':build()
