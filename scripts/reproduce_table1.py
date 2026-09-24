"""S23 reconstruction from cached predictions and saved replicate statistics."""
from pathlib import Path
import argparse
import csv
import json
import numpy as np

def verify_transfer_oracle(root):
    root = Path(root)
    folder = root / 'frozen/table1_transfer'
    kappa = json.loads((root / 'protocols/table1.json').read_text())['kappa']
    results = []
    def oracle(x):
        x = x.astype(np.float64)
        contributions = -np.logaddexp(0., -(2 * x[:, 1:7, 4, None] - 1) * x[:, 1:7, :4] * kappa)
        ell = contributions.sum(axis=1)
        prior = x[:, 0, 6:10]
        logprior = np.full_like(prior, -np.inf)
        np.log(prior, out=logprior, where=prior > 0)
        weights = logprior + ell
        weights = np.exp(weights - weights.max(axis=1, keepdims=True))
        posterior = weights / weights.sum(axis=1, keepdims=True)
        q = (posterior * np.exp(-np.logaddexp(0., -kappa * x[:, 7, :4]))).sum(axis=1)
        return contributions, ell, posterior, q
    for panel in ['Z', 'P']:
        with np.load(folder / ('panel_' + panel + '.npz'), allow_pickle=False) as z:
            original, comp, positions = z['original'], z['comp'], z['position']
        expected = original.copy()
        ix, pos = np.arange(len(original)), positions + 1
        expected[ix, pos, :4] *= -1
        expected[ix, pos, 4] = 1 - expected[ix, pos, 4]
        np.testing.assert_array_equal(expected, comp)
        orig, transformed = oracle(original), oracle(comp)
        errors = {name: float(np.max(np.abs(a-b))) for name, a, b in zip(['contributions','log_likelihood','posterior','predictive'],orig,transformed)}
        if max(errors.values()) > 1e-12:
            raise ValueError('T_COMP oracle identity failed')
        with np.load(folder / ('ORACLE_' + panel + '.npz'), allow_pickle=False) as z:
            for key, actual in [('loglik_original',orig[1]),('loglik_comp',transformed[1]),('posterior_original',orig[2]),('posterior_comp',transformed[2]),('q_original',orig[3]),('q_comp',transformed[3])]:
                np.testing.assert_allclose(actual, z[key], rtol=0, atol=1e-12)
        with np.load(folder / ('predictions_' + panel + '.npz'), allow_pickle=False) as z:
            np.testing.assert_allclose(orig[3], z['oracle'], rtol=0, atol=1e-12)
            np.testing.assert_array_equal(positions, z['position'])
        results.append(dict(panel=panel, status='PASS', bases=len(original), max_errors=errors))
    return results

def reproduce(root):
    root = Path(root)
    folder = root / 'frozen/table1_transfer'
    def rows(name):
        with (folder / name).open(newline='') as f:
            return list(csv.DictReader(f))
    refs, cohorts, seeds = rows('PAIRED_CONTRASTS.csv'), rows('COHORT_RESULTS.csv'), rows('SEED_RESULTS.csv')
    protocol = json.loads((root / 'protocols/table1.json').read_text())
    result = []
    displays = {('Z','D-A'):'-0.74 [-2.09, 0.48] x 1e-6', ('Z','C-A'):'-15.57 [-17.70, -13.58] x 1e-6', ('P','D-A'):'-0.57 [-1.98, 0.65] x 1e-6', ('P','C-A'):'-16.29 [-18.60, -14.08] x 1e-6'}
    with np.load(folder / 'BOOTSTRAP_REPLICATES.npz', allow_pickle=False) as z:
        panels, branches, metrics, draws = list(z['panels']), list(z['branches']), list(z['metrics']), z['values']
        for panel in ['Z', 'P']:
            with np.load(folder / ('predictions_' + panel + '.npz'), allow_pickle=False) as pred:
                p, pb = pred['predictions'], list(pred['branches'])
                np.testing.assert_array_equal(pred['seeds'], np.arange(12001,12013))
            per_seed = ((p[...,1] - p[...,0])**2 / 4).mean(axis=2)
            values = per_seed.mean(axis=0)
            for bi, b in enumerate(pb):
                ref = next(r for r in cohorts if r['panel']==panel and r['branch']==b)
                np.testing.assert_allclose(values[bi], float(ref['E_WITHIN_T']), rtol=0, atol=1e-10)
                for si, seed in enumerate(range(12001,12013)):
                    sr = next(r for r in seeds if r['panel']==panel and r['branch']==b and int(r['seed'])==seed)
                    np.testing.assert_allclose(per_seed[si,bi],float(sr['E_WITHIN_T']),rtol=0,atol=1e-10)
            for b in ['D','C']:
                contrast = b + '-A'
                estimate = float(values[pb.index(b)] - values[pb.index('A')])
                d = draws[panels.index(panel)]
                rep = d[:,branches.index(b),metrics.index('E_WITHIN_T')] - d[:,branches.index('A'),metrics.index('E_WITHIN_T')]
                if len(rep) != 2000:
                    raise ValueError('Unexpected S23 draw count')
                lo, hi = map(float,np.quantile(rep,[.025,.975],method='linear'))
                ref = next(r for r in refs if r['panel']==panel and r['contrast']==contrast and r['metric']=='E_WITHIN_T')
                expected, exlo, exhi = [float(ref[k]) for k in ['estimate','lower','upper']]
                np.testing.assert_allclose([estimate,lo,hi],[expected,exlo,exhi],rtol=0,atol=1e-10)
                result.append(dict(item='Table 1',metric='E_WITHIN_COMP',context=panel + ' ' + contrast,estimate=estimate,lower95=lo,upper95=hi,
                    expected_estimate=expected,expected_lower95=exlo,expected_upper95=exhi,
                    source_file='frozen/table1_transfer/predictions_' + panel + '.npz;frozen/table1_transfer/BOOTSTRAP_REPLICATES.npz',
                    source_section='S23 panel ' + panel + ' ' + contrast,uncertainty_source=protocol['authority'],draws=2000,
                    sampling_unit=protocol['sampling_unit'],strata=protocol['strata'],percentile=protocol['percentile'],
                    reproduction_level='2 from cached per-example predictions; 3 from saved replicate statistics',tolerance=1e-10,
                    displayed_value=displays[panel,contrast]))
    return result

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    root = parser.parse_args().root
    result = reproduce(root)
    oracle = verify_transfer_oracle(root)
    (root / 'reproduced').mkdir(exist_ok=True)
    (root / 'reproduced/table1.json').write_text(json.dumps(result, indent=2) + '\n')
    (root / 'reproduced/transfer_oracle.json').write_text(json.dumps(oracle, indent=2) + '\n')
    print('PASS: Table 1 four paired contrasts; both T_COMP oracle panels')
