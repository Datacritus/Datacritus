"""AMECO connector tests: exact slices, immutable release, forecasts and failures."""
import copy,csv,hashlib,io,json,sys,tempfile,unittest,zipfile
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import ameco

def fixture(change=None):
    rows={f'AMECO{i}.CSV':[] for i in range(1,19)}
    for m in ameco.MANIFEST:
        r={'CODE':'GRC.'+m['slice']+'.'+m['variable'],'COUNTRY':'Greece','TITLE':m['providerTitle'],'UNIT':m['sourceUnit']}
        r.update({str(y):str(y-2010) for y in range(2010,2025)});r['2011']='NA';r['2009']='-2';r['2025']='999999';r['2026']='888888'
        rows[m['sourceFile']].append(r)
    if change:change(rows)
    out=io.BytesIO()
    with zipfile.ZipFile(out,'w') as z:
        for name,records in rows.items():
            text=io.StringIO();writer=csv.DictWriter(text,fieldnames=['CODE','COUNTRY','TITLE','UNIT',*[str(y) for y in range(1974,2027)]]);writer.writeheader();writer.writerows(records);z.writestr(name,text.getvalue().encode('cp1252'))
    return out.getvalue()
class Tests(unittest.TestCase):
    def parse(self,raw):
        with patch.dict(ameco.CONFIG,{'archiveSha256':hashlib.sha256(raw).hexdigest()}):return ameco.parse_archive(raw)
    def test_zero_null_negative_and_forecasts(self):
        p=self.parse(fixture());v=p[ameco.MANIFEST[0]['code']]['GRC'];self.assertEqual(v['2010'],0);self.assertIsNone(v['2011']);self.assertEqual(v['2009'],-2);self.assertNotIn('2025',v);self.assertEqual(p[ameco.MANIFEST[0]['code']]['EUU'],{})
    def test_checksum(self):
        with self.assertRaisesRegex(ValueError,'release changed'):ameco.parse_archive(fixture())
    def test_unit_drift(self):
        raw=fixture(lambda rows:rows[ameco.MANIFEST[0]['sourceFile']][0].update(UNIT='unexpected base year'))
        with self.assertRaisesRegex(ValueError,'unit drift'):self.parse(raw)
    def test_duplicate(self):
        def double(rows):rows[ameco.MANIFEST[0]['sourceFile']].append(copy.deepcopy(rows[ameco.MANIFEST[0]['sourceFile']][0]))
        with self.assertRaisesRegex(ValueError,'Duplicate AMECO'):self.parse(fixture(double))
    def test_nonfinite(self):
        def corrupt(rows):rows[ameco.MANIFEST[0]['sourceFile']][0]['2020']='NaN'
        with self.assertRaisesRegex(ValueError,'Nonfinite'):self.parse(fixture(corrupt))
    def test_wrong_slice(self):
        def wrong(rows):rows[ameco.MANIFEST[0]['sourceFile']][0]['CODE']='GRC.9.9.9.9.'+ameco.MANIFEST[0]['variable']
        with self.assertRaisesRegex(ValueError,'Insufficient'):self.parse(fixture(wrong))
    def test_receipt_cannot_leak_forecasts(self):
        observations=self.parse(fixture());observations[ameco.MANIFEST[0]['code']]['GRC']['2025']=42
        receipt={'archiveSha256':ameco.CONFIG['archiveSha256'],'historicalCutoff':2024,'retrievedAt':'2026-10-19','observations':observations}
        with self.assertRaisesRegex(ValueError,'Forecast-year'):ameco.metrics_from_receipt(receipt)
    def test_raw_replay_if_available(self):
        raw=ROOT/'data/raw/ameco-source.zip'
        if not raw.exists():self.skipTest('Pinned archive not present in source-only checkout')
        values=ameco.parse_archive(raw.read_bytes());self.assertEqual(len(values),14)
        for config in ameco.MANIFEST:
            years=[int(y) for y,v in values[config['code']]['GRC'].items() if v is not None]
            self.assertGreaterEqual(len(years),15);self.assertEqual(max(years),2024)
if __name__=='__main__':unittest.main()
