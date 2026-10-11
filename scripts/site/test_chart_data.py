"""Check that interactive readouts retain the saved scientific measurements.
Run after building: python3 -m unittest discover -s scripts/site -p 'test_*.py'
"""
import csv
import json
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
V = ROOT / 'analysis/validation-20261011'

def hits(name):
    svg = ET.parse(ROOT / f'docs/charts/{name}.svg')
    return [json.loads(e.attrib['data-chart-detail']) for e in svg.iter() if 'data-chart-detail' in e.attrib]

def csvrows(name):
    with (V / 'post/data' / name).open() as f:
        return list(csv.DictReader(f))

class ChartReadouts(unittest.TestCase):
    def test_all_timeline_events_preserve_timing_and_depth(self):
        events = csvrows('kic5689121_per_transit_depths.csv')
        actual = {title: dict(rows) for title, rows in hits('quarter-baseline') if title.startswith('Event')}
        self.assertEqual(len(actual), len(events))
        for r in events:
            tip = actual[f"Event {r['epoch']} / Q{r['quarter']}"]
            self.assertEqual(float(tip['Mid-transit BTJD']), float(r['predicted_mid_btjd']))
            self.assertEqual(tip['Depth'], f"{float(r['depth_ppm']):,.2f} ± {float(r['err_ppm']):,.2f} ppm")
            self.assertEqual(tip['Selection'], 'Reserved' if r['held_out'] == 'True' else 'Search')

    def test_quarter_counts_and_endpoints(self):
        light = csvrows('kic5689121_lightcurve_psf.csv')
        quarters = {int(r['quarter']) for r in light}
        actual = {title: dict(rows) for title, rows in hits('quarter-baseline') if title.startswith('Quarter')}
        self.assertEqual(len(actual), len(quarters))
        for q in quarters:
            times = [float(r['time_btjd']) for r in light if int(r['quarter']) == q]
            tip = actual[f'Quarter {q}']
            self.assertEqual(tip['Cadences'], f'{len(times):,}')
            self.assertEqual(tip['First / last BTJD'], f'{min(times):.5f} / {max(times):.5f}')

    def test_gaia_ids_remain_exact_strings(self):
        saved = csvrows('kic5689121_gaia_neighbours_120arcsec.csv')
        actual = {title.removeprefix('Gaia DR3 '): dict(rows) for title, rows in hits('gaia-field')}
        self.assertEqual(set(actual), {r['source_id'] for r in saved})
        for r in saved:
            self.assertEqual(actual[r['source_id']]['RA'], f"{float(r['ra']):.7f}°")

    def test_centroid_components_and_uncertainties(self):
        saved = json.loads((V / 'results/kepler/kcentroid_tpf.json').read_text())['per_quarter']
        actual = {title: dict(rows) for title, rows in hits('centroid-vectors')}
        self.assertEqual(len(actual), len(saved))
        for r in saved:
            tip = actual[f"Quarter {r['q']} / centroid"]
            for i, axis in enumerate(['Column', 'Row']):
                self.assertEqual(tip[axis+' measured'], f"{r['meas_mpix'][i]:.4f} ± {r['err_mpix'][i]:.4f} mpix")
                self.assertEqual(tip[axis+' target'], f"{r['pred_target'][i]:.4f} mpix")
                self.assertEqual(tip[axis+' neighbour'], f"{r['pred_neighbour'][i]:.4f} mpix")

    def test_histogram_keeps_all_events_and_reserved_split(self):
        bins = [dict(rows) for _, rows in hits('event-depth-distribution')]
        self.assertEqual(sum(int(r['Total']) for r in bins), 74)
        self.assertEqual(sum(int(r['Reserved events']) for r in bins), 23)

if __name__ == '__main__':
    unittest.main()
