"""Check that published indicator pages expose consistent, crawlable source data."""
import csv
import json
import re
import unittest
import xml.etree.ElementTree as ET
import sys
from PIL import Image
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from build_public_context import government_table


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.language = None

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if tag == 'html':
            self.language = attrs.get('lang')
        if tag in ('a', 'link'):
            self.links.append((tag, attrs))


class SEO(unittest.TestCase):
    def test_indicator_pages(self):
        catalogue = {m['code']: m for m in json.loads((ROOT/'data/indicators.json').read_text())['metrics']}
        entries = json.loads((ROOT/'scripts/seo_indicators.json').read_text())
        sitemap = ET.fromstring((ROOT/'sitemap.xml').read_text())
        urls = {node.text for node in sitemap.findall('{*}url/{*}loc')}
        titles = set()
        for entry in entries:
            metric = catalogue[entry['code']]
            greek = {y:v for y,v in metric['series']['GRC'] if isinstance(v,(int,float))}
            with (ROOT/f'data/seo/{entry["slug"]}.csv').open() as file:
                rows = list(csv.DictReader(file))
            self.assertEqual({int(r['year']):float(r['Greece']) for r in rows if r['Greece']}, greek)
            for lang in ('en','el'):
                path = f'/{lang}/indicators/{entry["slug"]}/'
                html = (ROOT/path.lstrip('/')/'index.html').read_text()
                parser = Links()
                parser.feed(html)
                self.assertEqual(parser.language,lang)
                self.assertIn('https://www.datacritus.gr'+path,urls)
                canonical = [a['href'] for tag,a in parser.links if a.get('rel')=='canonical']
                self.assertEqual(canonical,['https://www.datacritus.gr'+path])
                alternates = {a['hreflang']:a['href'] for tag,a in parser.links if a.get('rel')=='alternate'}
                self.assertEqual(set(alternates),{'en','el','x-default'})
                title = re.search('<title>(.*?)</title>',html).group(1)
                self.assertNotIn(title,titles)
                titles.add(title)
                self.assertIn('<h1>',html)
                self.assertIn('content="summary_large_image"',html)
                self.assertIn(f'/assets/social/{entry["slug"]}-{lang}.png',html)
                with Image.open(ROOT/f'assets/social/{entry["slug"]}-{lang}.png') as image:
                    self.assertEqual(image.size,(1200,630))
                self.assertIn('Coverage / years' if lang=='en' else 'Κάλυψη / έτη',html)
                self.assertIn(f'href="/{lang}/methodology/"',html)
                if entry['slug']=='unemployment':
                    self.assertIn('ELSTAT' if lang=='en' else 'ΕΛΣΤΑΤ',html)
                    self.assertIn('modelled' if lang=='en' else 'Μοντελοποιημένη',html)
                if lang=='el':
                    self.assertIn('μετάφραση Datacritus',html)
                self.assertIn('type="application/ld+json"',html)
                for match in re.findall('<script type="application/ld\\+json">(.*?)</script>',html):
                    schema = json.loads(match)
                    dataset = schema[0]
                    self.assertEqual(dataset['identifier'],entry['code'])
                    self.assertEqual(dataset['citation'],metric['sourceUrl'])
                    self.assertEqual(dataset['inLanguage'],lang)
                for tag,attrs in parser.links:
                    href = attrs.get('href','')
                    if href.startswith('/') and not href.startswith('//'):
                        local = ROOT/href.split('#')[0].lstrip('/')
                        if href.split('#')[0].endswith('/'):
                            local /= 'index.html'
                        self.assertTrue(local.exists(),href)
                svg = re.search('(<svg class="chart".*?</svg>)',html).group(1)
                ET.fromstring(svg)
                self.assertNotIn('NaN',svg)

    def test_navigation(self):
        html = (ROOT/'index.html').read_text()
        self.assertIn('href="/en/indicators/"',html)
        self.assertIn('href="/el/indicators/"',html)
        self.assertIn('https://www.datacritus.gr/sitemap.xml',(ROOT/'robots.txt').read_text())

    def test_public_pages(self):
        for lang in ['el','en']:
            for slug in ['about','methodology']:
                page=(ROOT/lang/slug/'index.html').read_text()
                self.assertIn(f'/{lang}/{slug}/',page)
                self.assertIn(f'https://www.datacritus.gr/{lang}/{slug}/',(ROOT/'sitemap.xml').read_text())
                self.assertNotIn('dashboard.html#page=about',page)
                if slug=='about':
                    self.assertNotIn('Ioannis',page)
                    self.assertNotIn('Beris',page)
                    self.assertIn('private initiative' if lang=='en' else 'ιδιωτική πρωτοβουλία',page)
                    self.assertIn('self-funded' if lang=='en' else 'αυτοχρηματοδοτούμενο',page)

    def test_homepage_chart_language_parity(self):
        charts={}
        for path,lang in [('index.html','el'),('el/index.html','el'),('en/index.html','en')]:
            html=(ROOT/path).read_text()
            svg=re.search(r'<svg class="chart".*?</svg>',html,re.S).group(0)
            root=ET.fromstring(svg)
            description=root.find('{*}desc').text
            labels=[n.text for n in root.findall('.//{*}text')]
            numeric=[v for v in labels if '.' in v or ',' in v]
            self.assertTrue(numeric)
            if lang=='en':
                self.assertIn('Missing years',description)
                self.assertFalse(re.search('[\u0370-\u03ff]', ''.join(root.itertext())))
                self.assertTrue(all('.' in v for v in numeric))
            else:
                self.assertIn('Τα έτη',description)
                self.assertTrue(all(',' in v for v in numeric))
            # Localisation must change labels, never the underlying observations.
            paths=[n.get('d') for n in root.findall('.//{*}path')]
            charts[path]=paths
        self.assertEqual(charts['el/index.html'],charts['en/index.html'])
        self.assertEqual(charts['index.html'],charts['el/index.html'])

    def test_government_table_missing_and_transition_years(self):
        metric={'series':{'GRC':[[2015,99],[2016,10],[2017,None],[2018,7],[2019,99]]},'title':{'en':'Example'},'unit':'%','change':'pp'}
        history={'verifiedAt':'2020-01-01','governments':[{'start':'2015-09-21','end':'2019-07-08','name':{'en':'PM'},'coalition':{'en':'Party'}}]}
        table=government_table(metric,history,'en',lambda n,lang:str(n))
        self.assertIn('2016: 10',table)
        self.assertIn('2018: 7',table)
        self.assertIn('-3 pp',table)
        self.assertIn('8.5',table)
        self.assertIn('2/3',table)
        self.assertNotIn('2015: 99',table)
        metric['series']['GRC']=[[2016,0]]
        table=government_table(metric,history,'en',lambda n,lang:str(n))
        self.assertIn('2016: 0',table)
        self.assertIn('<td>— </td>',table)


if __name__ == '__main__':
    unittest.main()
