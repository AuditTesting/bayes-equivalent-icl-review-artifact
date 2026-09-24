"""Reconstruct Figure 3 from cached seed statistics and saved bootstrap replicates."""
import argparse
import csv
import json
from pathlib import Path

import numpy as np


def reproduce(root):
    root = Path(root)
    rel = 'frozen/figure3_extended/'
    data = root / rel
    authority = json.loads((data / 'authority.json').read_text(encoding='utf-8'))
    protocol = json.loads((root / 'protocols/figure3.json').read_text(encoding='utf-8'))
    with (data / 'seed_values.csv').open(encoding='utf-8', newline='') as stream:
        rows = list(csv.DictReader(stream))
    metrics = authority['metric_order']
    times = authority['times']
    assert len(rows) == 36
    assert len({(r['seed'], r['updates']) for r in rows}) == 36
    values = np.asarray([[[float(next(r for r in rows if int(r['seed']) == seed and int(r['updates']) == time)[m]) for m in metrics] for time in times] for seed in protocol['seeds']])
    assert values.shape == (12, 3, 3) and np.isfinite(values).all()
    means = values.mean(axis=0)
    with np.load(data / 'bootstrap_replicates.npz', allow_pickle=False) as stored:
        trajectory = stored['trajectory']
        summaries = stored['summaries']
    assert trajectory.shape == (20000, 3, 3)
    assert summaries.shape == (20000, 9)
    assert np.isfinite(trajectory).all() and np.isfinite(summaries).all()
    ci = np.quantile(trajectory, [0.025, 0.975], axis=0, method='linear')
    result = []

    def add(metric, context, estimate, expected, interval=None, expected_interval=None, section='', display=''):
        row = dict(item='Figure 3', metric=metric, context=context,
                   estimate=float(estimate), expected_estimate=float(expected),
                   lower95=None if interval is None else float(interval[0]),
                   upper95=None if interval is None else float(interval[1]),
                   expected_lower95=None if expected_interval is None else float(expected_interval[0]),
                   expected_upper95=None if expected_interval is None else float(expected_interval[1]),
                   source_file=rel+'seed_values.csv', source_section=section,
                   uncertainty_source=rel+'bootstrap_replicates.npz' if interval is not None else 'not reported',
                   draws=protocol['draws'] if interval is not None else 0,
                   sampling_unit=protocol['sampling_unit'] if interval is not None else '12 fixed seeds',
                   strata=protocol['strata'], percentile=protocol['percentile'] if interval is not None else 'not applicable',
                   reproduction_level='2+3' if interval is not None else '2',
                   tolerance=1e-10, displayed_value=display)
        for actual, target in [('estimate','expected_estimate'),('lower95','expected_lower95'),('upper95','expected_upper95')]:
            if row[target] is not None and abs(row[actual]-row[target]) > row['tolerance']:
                raise AssertionError(f'{metric} {context}: {actual} mismatch')
        result.append(row)

    for j,time in enumerate(times):
        for k,metric in enumerate(metrics):
            add(metric, f'cohort at {time} updates', means[j,k], authority['cohort_means'][j][k], ci[:,j,k], np.asarray(authority['trajectory_intervals'])[:,j,k],
                f'12 seed rows at updates={time}; authority.json/cohort_means[{j}][{k}] and trajectory_intervals[:,{j},{k}]', protocol['displayed'].get(f'{metric}@{time}', ''))
    for column, summary in enumerate(protocol['summaries']):
        a=times.index(summary['earlier']); b=times.index(summary['later']); m=metrics.index(summary['metric'])
        if summary['operation'] == 'ratio':
            assert means[a,m] > 0 and np.all(trajectory[:,a,m] > 0)
            point=means[b,m]/means[a,m]
            reconstructed=trajectory[:,b,m]/trajectory[:,a,m]
        else:
            point=means[b,m]-means[a,m]
            reconstructed=trajectory[:,b,m]-trajectory[:,a,m]
        np.testing.assert_allclose(reconstructed, summaries[:,column], rtol=0, atol=1e-14)
        name=summary['name']
        interval=np.quantile(summaries[:,column], [0.025,0.975], method='linear')
        add(name, f"paired {summary['earlier']} to {summary['later']} updates", point, authority['summaries'][name], interval, authority['summary_intervals'][name]['interval'],
            f'cohort {summary["operation"]}; authority.json/summaries/{name}; bootstrap summaries[:,{column}]', protocol['displayed'].get(name,''))
    n=metrics.index('N0_ABS')
    add('N0_ABS_reduction_percent','200000 to 800000 updates',100*(1-means[2,n]/means[0,n]),100*(1-authority['summaries']['R_N_200_800']),section='100*(1-R_N_200_800); authority.json/summaries',display=protocol['displayed']['N0_ABS_reduction_percent'])
    add('N0_ABS_benchmark_multiple','800000 updates divided by epsilon0',means[2,n]/authority['epsilon0'],authority['cohort_means'][2][n]/authority['epsilon0'],section='800000 N0_ABS / 0.01; authority.json/cohort_means and epsilon0',display=protocol['displayed']['N0_ABS_benchmark_multiple'])
    return result


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    args=parser.parse_args()
    rows=reproduce(args.root)
    output=args.root/'reproduced/figure3.json'
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(rows,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    print(f'PASS Figure 3: {len(rows)} records; frozen seed means and saved-replicate percentiles verified.')
