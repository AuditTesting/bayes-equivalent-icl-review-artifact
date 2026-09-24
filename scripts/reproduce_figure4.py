"""S22 endpoint reconstruction and saved common-four-cell percentiles. No RNG."""
from pathlib import Path
import argparse
import csv
import json
import numpy as np

METRICS = ['E_WITHIN', 'E_PAIR', 'E_SHARED', 'F_WITHIN', 'K', 'N0_ABS', 'BETA_POS']

def reproduce(root):
    root = Path(root)
    folder = root / 'frozen/figure4_factorial'
    def rows(name):
        with (folder / name).open(newline='') as f:
            return list(csv.DictReader(f))
    seeds = rows('E_SEED_RESULTS.csv')
    cohorts = {r['condition']: r for r in rows('E_COHORT_RESULTS.csv')}
    refs = rows('BOOTSTRAP_INTERVALS.csv')
    protocol = json.loads((root / 'protocols/figure4.json').read_text())
    values = {}
    for c in 'ACDE':
        selected = [r for r in seeds if r['condition'] == c]
        if sorted(int(r['seed']) for r in selected) != list(range(12001, 12013)):
            raise ValueError('Missing or duplicate endpoint lineage')
        values[c] = {m: float(np.mean([float(r[m]) for r in selected])) for m in METRICS if m != 'F_WITHIN'}
        values[c]['F_WITHIN'] = values[c]['E_WITHIN'] / values[c]['E_PAIR']
    result = []
    with np.load(folder / 'BOOTSTRAP_REPLICATES.npz', allow_pickle=False) as z:
        conditions, metrics, draws = list(z['conditions']), list(z['metrics']), z['values']
        if draws.shape[0] != 2000 or conditions != list('ACDE'):
            raise ValueError('Not the common-four-cell frozen draw population')
        def add(context, m, estimate, rep, ref, expected):
            lo, hi = map(float, np.quantile(rep, [.025, .975], method='linear'))
            exlo, exhi = float(ref['lower']), float(ref['upper'])
            if not np.allclose([estimate, lo, hi], [expected, exlo, exhi], rtol=0, atol=1e-10):
                raise ValueError('S22 reconstruction mismatch: ' + context + ' ' + m)
            display = {('E', 'E_WITHIN'): '1.40e-7', ('D', 'BETA_POS'): '1.068', ('E', 'BETA_POS'): '1.035', ('E-C', 'E_WITHIN'): '-6.733e-6 [-7.568e-6, -5.946e-6]', ('E-C', 'K'): '1.291e-4 [1.148e-4, 1.453e-4]'}
            result.append(dict(item='Figure 4', metric=m, context=context, estimate=estimate, lower95=lo, upper95=hi,
                expected_estimate=expected, expected_lower95=exlo, expected_upper95=exhi,
                source_file='frozen/figure4_factorial/E_SEED_RESULTS.csv;frozen/figure4_factorial/BOOTSTRAP_REPLICATES.npz',
                source_section='S22 common-four-cell ' + context, uncertainty_source=protocol['authority'], draws=2000,
                sampling_unit=protocol['sampling_unit'], strata=protocol['strata'], percentile=protocol['percentile'],
                reproduction_level='2 point estimates from seed summaries; 3 intervals from saved statistics', tolerance=1e-10,
                displayed_value=display.get((context, m))))
        for c in 'ACDE':
            for m in METRICS:
                ref = next(r for r in refs if r['condition'] == c and r['metric'] == m)
                add(c, m, values[c][m], draws[:, conditions.index(c), metrics.index(m)], ref, float(cohorts[c][m]))
        for context in ['D-A', 'E-C']:
            a, b = context.split('-')
            for m in ['E_WITHIN', 'K']:
                ref = next(r for r in refs if r['contrast'] == context and r['metric'] == m)
                rep = draws[:, conditions.index(a), metrics.index(m)] - draws[:, conditions.index(b), metrics.index(m)]
                add(context, m, values[a][m] - values[b][m], rep, ref, float(ref['estimate']))
    return result

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    root = parser.parse_args().root
    result = reproduce(root)
    (root / 'reproduced').mkdir(exist_ok=True)
    (root / 'reproduced/figure4.json').write_text(json.dumps(result, indent=2) + '\n')
    print('PASS: Figure 4, 28 endpoint metrics and four S22 paired contrasts')
