import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from oecd import MANIFEST, parse_csv

class ProviderSemantics(unittest.TestCase):
    def fixture(self, observations):
        import csv,io
        config=MANIFEST[0]
        fields=list(config['dimensions'])+['TIME_PERIOD','OBS_VALUE','UNIT_MULT','OBS_STATUS','OBS_STATUS2']
        out=io.StringIO();writer=csv.DictWriter(out,fieldnames=fields);writer.writeheader()
        for extra in observations:
            writer.writerow({**config['dimensions'],'TIME_PERIOD':'2020','OBS_VALUE':'1.2','UNIT_MULT':'0','OBS_STATUS':'A',**extra})
        return out.getvalue().encode(),config

    def test_scale_missing_zero_and_source_estimate(self):
        raw,config=self.fixture([{'TIME_PERIOD':'2020','UNIT_MULT':'2','OBS_STATUS':'E'},
             {'TIME_PERIOD':'2021','OBS_VALUE':'','OBS_STATUS':'M'},
             {'TIME_PERIOD':'2022','OBS_VALUE':'0'}])
        points=parse_csv(raw,[config])[config['code']]['GRC']
        self.assertEqual([points[y]['value'] for y in (2020,2021,2022)],[120,None,0])
        self.assertIn('Estimated value',points[2020]['flags'])

    def test_slice_filters_sector_edition_unit_and_frequency(self):
        raw,config=self.fixture([{'SECTOR':'S1'},{'EDITION':'2024'},
                                {'UNIT_MEASURE':'PT_OTE_S13'},{'FREQ':'Q'}])
        self.assertEqual(parse_csv(raw,[config])[config['code']]['GRC'],{})

    def test_included_or_confidential_is_not_observed_zero(self):
        raw,config=self.fixture([{'OBS_VALUE':'0','OBS_STATUS2':'K'},
                                {'TIME_PERIOD':'2021','OBS_VALUE':'0','OBS_STATUS':'C'}])
        points=parse_csv(raw,[config])[config['code']]['GRC']
        self.assertIsNone(points[2020]['value']);self.assertIsNone(points[2021]['value'])

    def test_unknown_status_and_duplicate_fail(self):
        for extras in ([{'OBS_STATUS':'UNKNOWN'}],[{},{}]):
            raw,config=self.fixture(extras)
            with self.assertRaises(ValueError):parse_csv(raw,[config])

if __name__=='__main__':unittest.main()
