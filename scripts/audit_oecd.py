"""Revalidate exact OECD candidate slices; never count variants as additions.

This audit deliberately does not clear source rights or publish observations.
Those require review of dataset-specific metadata in addition to live values.
"""
import argparse
import csv
import datetime as dt
import hashlib
import io
import json
import math
from pathlib import Path
import urllib.request

def screen(candidate, rows):
    selected = [r for r in rows if all(r.get(k) == v for k, v in candidate['dimensions'].items())]
    observations = {}
    flags = {}
    for row in selected:
        year = int(row['TIME_PERIOD'])
        if not 1974 <= year <= dt.date.today().year:
            continue
        if year in observations:
            raise ValueError(f'Duplicate observation: {candidate["id"]}, {year}')
        raw = row.get('OBS_VALUE', '')
        value = float(raw) if raw.strip() else None
        if value is not None:
            value *= 10 ** int(row.get('UNIT_MULT') or 0)
            if not math.isfinite(value):
                raise ValueError('Nonfinite observation')
        observations[year] = value
        flags[str(year)] = {k: v for k, v in row.items() if k.startswith('OBS_STATUS') and v}
    valid = {y: v for y, v in observations.items() if v is not None}
    years = sorted(valid)
    density = len(years) / (years[-1] - years[0] + 1) if years else 0
    passed = len(years) >= 10 and years[-1] >= 2020 and density >= .7 and len(set(valid.values())) > 1
    return {'liveHistoryPass': passed, 'firstYear': years[0] if years else None,
            'lastYear': years[-1] if years else None, 'observations': len(years),
            'density': density, 'flags': flags, 'values': [[y, observations[y]] for y in sorted(observations)]}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('candidates', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    candidates = [c for c in json.loads(args.candidates.read_text()) if c['provider'].lower() == 'oecd']
    args.output.mkdir(parents=True, exist_ok=True)
    fetched = {}
    results = []
    for c in candidates:
        url = c['apiUrl']
        if url not in fetched:
            print('Fetching', url, flush=True)
            request = urllib.request.Request(url, headers={'Accept': 'application/vnd.sdmx.data+csv;version=1.0', 'User-Agent': 'Datacritus/1.0 (Greek public statistics validation)'})
            try:
                with urllib.request.urlopen(request, timeout=45) as response:
                    raw = response.read()
                rows = list(csv.DictReader(io.StringIO(raw.decode('utf-8-sig'))))
                if not rows or 'OBS_VALUE' not in rows[0]:
                    raise ValueError('Unexpected CSV response')
                name = c['seriesKey'].split('|')[0].replace('@', '-') + '.csv'
                (args.output / name).write_bytes(raw)
                fetched[url] = (rows, hashlib.sha256(raw).hexdigest(), None)
            except Exception as exc:
                fetched[url] = ([], None, str(exc))
        rows, digest, error = fetched[url]
        try:
            result = screen(c, rows) if not error else {'liveHistoryPass': False, 'error': error}
        except Exception as exc:
            result = {'liveHistoryPass': False, 'error': str(exc)}
        results.append({'id': c['id'], 'conceptId': c['conceptId'], 'title': c['productTitle'],
                        'flow': c['seriesKey'].split('|')[0], 'dimensions': c['dimensions'],
                        'apiUrl': url, 'sha256': digest, **result,
                        'publicationReady': False, 'pending': ['Definition and source-rights review', 'Semantic duplicate check']})
    report = {'retrievedAt': dt.datetime.now(dt.timezone.utc).isoformat(), 'candidateCount': len(results),
              'liveHistoryPassCount': sum(r['liveHistoryPass'] for r in results), 'candidates': results}
    (args.output / 'live-audit.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
    print('Live history screen:', report['liveHistoryPassCount'], '/', len(results), flush=True)

if __name__ == '__main__':
    main()
