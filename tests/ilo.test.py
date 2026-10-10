"""Reject changed dimensions and ambiguous years; retain survey provenance."""
import csv,io,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from ilo import MANIFEST,parse_csv
CONFIG=MANIFEST[0]
def raw(rows):
 base=dict(ref_area='GRC',source='BA:317',indicator=CONFIG['indicator'],sex='SEX_T',classif1='',classif2='',time='2024',obs_value='0',obs_status='',**{'note_indicator.label':'Survey method changed','note_source.label':'National survey'})
 data=[{**base,**r} for r in rows];s=io.StringIO();w=csv.DictWriter(s,fieldnames=list(base));w.writeheader();w.writerows(data);return s.getvalue().encode()
class Parser(unittest.TestCase):
 def test_zero_and_notes(self):
  p=parse_csv(raw([{}]),CONFIG)['GRC']['2024'];self.assertEqual(p['value'],0);self.assertIn('Survey method changed',p['flags']);self.assertEqual(p['source'],'BA:317')
 def test_exact_dimensions(self):
  p=parse_csv(raw([{'source':'NEW'},{'sex':'SEX_F'},{'classif1':'AGE_Y15-24'},{'indicator':'OTHER'},{'ref_area':'EUU'}]),CONFIG);self.assertFalse(any(p.values()))
 def test_suppress_unreliable_model_and_imputation(self):
  for flag in ['U','M','I']:
   p=parse_csv(raw([{'obs_status':flag,'obs_value':'5'}]),CONFIG)['GRC']['2024'];self.assertIsNone(p['value']);self.assertIn(flag+':',p['flags'])
 def test_break_retained(self):
  p=parse_csv(raw([{'obs_status':'B','obs_value':'3.2'}]),CONFIG)['GRC']['2024'];self.assertEqual(p['value'],3.2);self.assertIn('Break in series',p['flags'])
 def test_management_has_no_sex_dimension(self):
  config=next(m for m in MANIFEST if m['indicator']=='SDG_0552_NOC_RT')
  rows=raw([{'indicator':config['indicator'],'sex':'','obs_value':'35'}])
  self.assertEqual(parse_csv(rows,config)['GRC']['2024']['value'],35)
 def test_informality_total_views_are_not_doubled(self):
  config=next(m for m in MANIFEST if m['indicator']=='SDG_0831_SEX_ECO_RT')
  rows=raw([{'indicator':config['indicator'],'source':'BB:319','classif1':'ECO_SECTOR_TOTAL','obs_value':'4.2'},{'indicator':config['indicator'],'source':'BB:319','classif1':'ECO_AGGREGATE_TOTAL','obs_value':'4.2'}])
  points=parse_csv(rows,config)['GRC'];self.assertEqual(len(points),1);self.assertEqual(points['2024']['value'],4.2)
 def test_fail_duplicate_unknown_nonannual_and_invalid(self):
  for rows in [[{},{}],[{'obs_status':'X'}],[{'time':'2024Q1'}],[{'obs_value':'nan'}],[{'obs_value':'101'}]]:
   with self.assertRaises(ValueError):parse_csv(raw(rows),CONFIG)
if __name__=='__main__':unittest.main()
