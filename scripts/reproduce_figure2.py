"""Reconstruct Figure 2 from cached seed metrics and saved bootstrap statistics.

Requires only NumPy and the Python standard library. Never samples randomness.
"""
from pathlib import Path
import argparse
import csv
import json
import numpy as np


def reproduce(root):
    root = Path(root)
    base = root / 'frozen/figure2_longitudinal'
    protocol = json.loads((root / 'protocols/figure2.json').read_text(encoding='utf-8'))
    primary = json.loads((base / '06_primary_estimands.json').read_text(encoding='utf-8'))

    def read_csv(name):
        with (base / name).open(newline='', encoding='utf-8') as handle:
            return list(csv.DictReader(handle))

    seed_hidden = read_csv('04_layer_metrics.csv')
    seed_output = read_csv('05_output_metrics.csv')
    expected_hidden = read_csv('04b_cohort_layer_metrics_CI95.csv')
    expected_output = read_csv('05b_cohort_output_metrics_CI95.csv')
    times = protocol['checkpoints']
    rows = []

    def add(metric, context, value, expected, draws, expected_ci, expected_file, section, arch, displayed=None):
        ci = [None, None] if draws is None else np.quantile(draws, [.025, .975], method='linear').tolist()
        expected_ci = [None, None] if expected_ci is None else expected_ci
        row = dict(item='Figure 2', metric=metric, context=context, estimate=float(value),
                   lower95=ci[0], upper95=ci[1], expected_estimate=float(expected),
                   expected_lower95=expected_ci[0], expected_upper95=expected_ci[1],
                   source_file='frozen/figure2_longitudinal/' + expected_file,
                   source_section=section,
                   uncertainty_source=('not applicable' if draws is None else 'frozen/figure2_longitudinal/' + arch + '_saved_statistics.npz'),
                   draws=0 if draws is None else len(draws),
                   sampling_unit='individual cached seed' if draws is None else protocol['uncertainty']['sampling_unit'],
                   strata='not applicable' if draws is None else protocol['uncertainty']['strata'],
                   percentile='not applicable' if draws is None else protocol['uncertainty']['percentile'],
                   reproduction_level=2 if draws is None else 3, tolerance=1e-10,
                   displayed_value=displayed)
        for computed, wanted in [('estimate','expected_estimate'),('lower95','expected_lower95'),('upper95','expected_upper95')]:
            if row[computed] is not None:
                if not np.isfinite(row[computed]) or abs(row[computed]-row[wanted]) > row['tolerance']:
                    raise ValueError(f'{context} {metric} failed {computed}: {row[computed]} != {row[wanted]}')
        rows.append(row)

    for arch, config in protocol['architectures'].items():
        seeds, locations = config['seeds'], config['locations']
        hidden = np.empty((len(seeds), len(times), len(locations)))
        outputs = np.empty((len(seeds), len(times)))
        for si, seed in enumerate(seeds):
            for ti, checkpoint in enumerate(times):
                for li, layer in enumerate(locations):
                    values = [r for r in seed_hidden if r['architecture'] == arch and int(r['seed']) == seed and int(r['checkpoint']) == checkpoint and r['layer'] == layer]
                    if len(values) != 1:
                        raise ValueError('Missing or duplicate hidden seed row')
                    hidden[si, ti, li] = float(values[0]['M'])
                values = [r for r in seed_output if r['architecture'] == arch and int(r['seed']) == seed and int(r['checkpoint']) == checkpoint]
                if len(values) != 1:
                    raise ValueError('Missing or duplicate output seed row')
                outputs[si, ti] = float(values[0]['P'])
        mean_m, mean_p = hidden.mean(axis=0), outputs.mean(axis=0)
        early, late = config['early_index'], config['late_index']
        attenuation = mean_m[:, late] / mean_m[:, early]
        with np.load(base / (arch + '_saved_statistics.npz'), allow_pickle=False) as saved:
            for ti, checkpoint in enumerate(times):
                for li, layer in enumerate(locations):
                    expected = next(r for r in expected_hidden if r['architecture'] == arch and int(r['checkpoint']) == checkpoint and r['layer'] == layer)
                    add('M', f'{arch}; checkpoint={checkpoint}; layer={layer}', mean_m[ti, li], float(expected['M']), saved['M'][:, ti, li], [float(expected['M_lo95']), float(expected['M_hi95'])], '04b_cohort_layer_metrics_CI95.csv', f'{arch}/{checkpoint}/{layer}', arch)
                expected = next(r for r in expected_output if r['architecture'] == arch and int(r['checkpoint']) == checkpoint)
                add('P', f'{arch}; checkpoint={checkpoint}', mean_p[ti], float(expected['P']), saved['P'][:, ti], [float(expected['P_lo95']),float(expected['P_hi95'])], '05b_cohort_output_metrics_CI95.csv', f'{arch}/{checkpoint}', arch)
                display = None
                if checkpoint == 200000:
                    display = {'mlp':'0.2990 [0.2818, 0.3158]','transformer':'0.4123 [0.3639, 0.4503]'}[arch]
                add('A', f'{arch}; checkpoint={checkpoint}', attenuation[ti], primary[arch]['A_by_checkpoint'][ti], saved['A'][:, ti], primary[arch]['A95_by_checkpoint'][ti], '06_primary_estimands.json', f'{arch}/A_by_checkpoint/{ti}', arch, display)
            for si, seed in enumerate(seeds):
                add('seed_A200k', f'{arch}; seed={seed}; checkpoint=200000', hidden[si,-1,late]/hidden[si,-1,early], primary[arch]['seed_A200k'][si], None, None, '06_primary_estimands.json', f'{arch}/seed_A200k/{si}', arch)
            displays = {'mlp':{'T_A':'0.2966 [0.2761, 0.3178]','R_P':'0.3990 [0.3672, 0.4334]'},'transformer':{'T_A':'0.5084 [0.4674, 0.5367]','R_P':'0.4020 [0.3334, 0.4629]'}}
            for metric, value in [('T_A', attenuation[-1]/attenuation[0]), ('R_P',mean_p[-1]/mean_p[0])]:
                add(metric, f'{arch}; checkpoint=200000/5000', value, primary[arch][metric]['estimate'], saved[metric], primary[arch][metric]['CI95'], '06_primary_estimands.json', f'{arch}/{metric}', arch, displays[arch][metric])
    return rows


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    results = reproduce(args.root)
    output = args.root / 'reproduced/figure2.json'
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(results, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    print(f'Figure 2: PASS, {len(results)} numerical rows; 64 saved-statistic intervals and 10 seed endpoint points.')
