"""Check that published indicator pages expose consistent, crawlable source data."""
import csv
import json
import re
import unittest
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


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


if __name__ == '__main__':
    unittest.main()
