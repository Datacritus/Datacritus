"""Guard against false zeros, wrong units, unreviewed scales and lost provenance."""
import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from vetted import MANIFEST, parse_uis, numeric, metrics_from_receipt

class SourceSemantics(unittest.TestCase):
    def setUp(self):
        self.config=[next(m for m in MANIFEST if m['provider']=='uis')]
        self.code=self.config[0]['sourceCode']
    def payload(self, records):
        return {'hints':[],'indicatorMetadata':[{'indicatorCode':self.code,'name':'Mobile students','glossaryTerms':[]}], 'records':records}
    def row(self, year, value, magnitude=None, qualifier=None):
        return {'indicatorId':self.code,'geoUnit':'GRC','year':year,'value':value,'magnitude':magnitude,'qualifier':qualifier,'footnotes':[]}
    def test_not_applicable_is_not_zero(self):
        records=[self.row(2020,0,'NA'),self.row(2021,0,'NIL'),self.row(2022,4,qualifier='NAT_EST'),self.row(2023,None,'SUPP')]
        values,_=parse_uis(self.payload(records),self.config)
        greek=values[self.code]['GRC']
        self.assertIsNone(greek[2020]['value']);self.assertEqual(greek[2021]['value'],0)
        self.assertEqual(greek[2022]['flags'],'NAT_EST');self.assertIsNone(greek[2023]['value'])
    def test_source_footnote_not_applicable(self):
        row=self.row(2020,0);row['footnotes']=[{'type':'Data Status','subtype':'Data reporting','value':'NA'}]
        values,_=parse_uis(self.payload([row]),self.config)
        self.assertIsNone(values[self.code]['GRC'][2020]['value'])
    def test_duplicate_and_new_quality_code_stop_import(self):
        row=self.row(2020,3)
        with self.assertRaises(ValueError):parse_uis(self.payload([row,row]),self.config)
        with self.assertRaises(ValueError):parse_uis(self.payload([self.row(2020,3,'NEW_STATUS')]),self.config)
    def test_unknown_country_and_unselected_indicator_do_not_pollute_series(self):
        row=self.row(2020,3);row['geoUnit']='USA'
        values,_=parse_uis(self.payload([row]),self.config)
        self.assertFalse(any(values[self.code].values()))
    def test_no_data_and_negative_values(self):
        self.assertIsNone(numeric(float('nan')));self.assertEqual(numeric(-2.3),-2.3)
        self.assertEqual(numeric(0),0)
        with self.assertRaises(ValueError):numeric('unknown')
    def test_pwt_fractions_are_percentages_but_ratios_are_not(self):
        configs=[m for m in MANIFEST if m['provider']=='pwt']
        observations={m['sourceCode']:{'GRC':{str(y):{'value':.5+(y-1974)*.001,'flags':'i_irr: Regular','bounds':None} for y in range(1974,2024)}} for m in configs}
        receipt={'provider':'pwt','dataUrl':'https://example.org/data','retrievedAt':'2026-10-06T00:00:00Z','sha256':'0'*64,'receiptSha256':'1'*64,'upstreamHashes':{},'observations':observations,'definitions':{m['sourceCode']:{'title':m['title'],'definition':m['title']} for m in configs}}
        items={m['sourceCode']:m for m in metrics_from_receipt(receipt)}
        self.assertEqual(items['labsh']['series']['GRC'][0],[1974,50])
        self.assertEqual(items['labsh']['change'],'pp')
        self.assertEqual(items['pl_c']['series']['GRC'][0],[1974,.5])
        self.assertEqual(items['pl_c']['change'],'absolute')
        self.assertEqual(items['pl_c']['series']['EUU'],[])
        observations['labsh']['GRC']={}
        with self.assertRaises(ValueError):metrics_from_receipt(receipt)

if __name__=='__main__':unittest.main()
