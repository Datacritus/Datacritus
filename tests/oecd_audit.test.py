import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from audit_oecd import screen

class ExactSliceTests(unittest.TestCase):
    def test_multiplier_missing_zero_and_flags(self):
        candidate = {'id': 'example', 'dimensions': {'REF_AREA': 'GRC', 'FREQ': 'A'}}
        rows = [dict(REF_AREA='GRC', FREQ='A', TIME_PERIOD=str(y), OBS_VALUE=v, UNIT_MULT='2', OBS_STATUS=f)
                for y, v, f in [(2020, '1.5', 'E'), (2021, '', 'K'), (2022, '0', 'A')]]
        result = screen(candidate, rows)
        self.assertEqual(result['values'], [[2020, 150], [2021, None], [2022, 0]])
        self.assertEqual(result['observations'], 2)
        self.assertEqual(result['flags']['2020'], {'OBS_STATUS': 'E'})

    def test_wrong_country_and_frequency_are_excluded(self):
        candidate = {'id': 'example', 'dimensions': {'REF_AREA': 'GRC', 'FREQ': 'A'}}
        rows = [dict(REF_AREA=c, FREQ=f, TIME_PERIOD='2020', OBS_VALUE='10')
                for c, f in [('FRA', 'A'), ('GRC', 'Q')]]
        self.assertEqual(screen(candidate, rows)['observations'], 0)

    def test_duplicate_year_and_nonfinite_fail(self):
        candidate = {'id': 'example', 'dimensions': {'REF_AREA': 'GRC'}}
        row = dict(REF_AREA='GRC', TIME_PERIOD='2020', OBS_VALUE='1')
        with self.assertRaises(ValueError):
            screen(candidate, [row, row])
        with self.assertRaises(ValueError):
            screen(candidate, [{**row, 'OBS_VALUE': 'nan'}])

if __name__ == '__main__':
    unittest.main()
