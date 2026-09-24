# Artifact size audit

Snapshot before ZIP packaging; this audit and manifest add small text overhead.

| Directory/file group | Bytes |
| --- | ---: |
| .gitignore | 38 |
| ANONYMITY_AUDIT.md | 950 |
| NOTICE | 713 |
| README.md | 4493 |
| REPRODUCIBILITY.md | 3158 |
| environment_core.yml | 119 |
| expected | 112805 |
| frozen | 70616961 |
| protocols | 10476 |
| requirements-core.txt | 14 |
| scripts | 31751 |

## Individual files

| File | Bytes |
| --- | ---: |
| .gitignore | 38 |
| ANONYMITY_AUDIT.md | 950 |
| environment_core.yml | 119 |
| expected/claim_source_map.csv | 81272 |
| expected/main_result_values.csv | 15464 |
| expected/manuscript_display_values.csv | 16069 |
| frozen/figure2_longitudinal/04_layer_metrics.csv | 16250 |
| frozen/figure2_longitudinal/04b_cohort_layer_metrics_CI95.csv | 7215 |
| frozen/figure2_longitudinal/05_output_metrics.csv | 3674 |
| frozen/figure2_longitudinal/05b_cohort_output_metrics_CI95.csv | 1733 |
| frozen/figure2_longitudinal/06_primary_estimands.json | 9380 |
| frozen/figure2_longitudinal/mlp_saved_statistics.npz | 386814 |
| frozen/figure2_longitudinal/transformer_saved_statistics.npz | 568507 |
| frozen/figure3_extended/authority.json | 3293 |
| frozen/figure3_extended/bootstrap_replicates.npz | 2880524 |
| frozen/figure3_extended/seed_values.csv | 2727 |
| frozen/figure4_factorial/BOOTSTRAP_INTERVALS.csv | 16593 |
| frozen/figure4_factorial/BOOTSTRAP_REPLICATES.npz | 1218224 |
| frozen/figure4_factorial/D_A_REFERENCE_CONTRASTS.csv | 3051 |
| frozen/figure4_factorial/E_C_CONTRASTS.csv | 3038 |
| frozen/figure4_factorial/E_COHORT_RESULTS.csv | 2241 |
| frozen/figure4_factorial/E_SEED_RESULTS.csv | 24053 |
| frozen/table1_transfer/BOOTSTRAP_REPLICATES.npz | 897336 |
| frozen/table1_transfer/COHORT_RESULTS.csv | 1879 |
| frozen/table1_transfer/ORACLE_P.npz | 1246992 |
| frozen/table1_transfer/ORACLE_Z.npz | 1246992 |
| frozen/table1_transfer/PAIRED_CONTRASTS.csv | 4596 |
| frozen/table1_transfer/panel_P.npz | 2236718 |
| frozen/table1_transfer/panel_Z.npz | 2196594 |
| frozen/table1_transfer/predictions_P.npz | 4500373 |
| frozen/table1_transfer/predictions_Z.npz | 4502160 |
| frozen/table1_transfer/SEED_RESULTS.csv | 21697 |
| frozen/table2_external/bootstrap_indices_n10.npz | 15599477 |
| frozen/table2_external/bootstrap_indices_n15.npz | 15388052 |
| frozen/table2_external/BOOTSTRAP_INTERVALS.csv | 1072 |
| frozen/table2_external/COHORT_RESULTS.csv | 602 |
| frozen/table2_external/panel_n10.npz | 7017452 |
| frozen/table2_external/panel_n15.npz | 10204486 |
| frozen/table2_external/predictions_n10.npz | 200788 |
| frozen/table2_external/predictions_n15.npz | 202378 |
| NOTICE | 713 |
| protocols/figure2.json | 2463 |
| protocols/figure3.json | 3799 |
| protocols/figure4.json | 1023 |
| protocols/README.md | 901 |
| protocols/table1.json | 1003 |
| protocols/table2.json | 1287 |
| README.md | 4493 |
| REPRODUCIBILITY.md | 3158 |
| requirements-core.txt | 14 |
| scripts/reproduce_figure2.py | 6740 |
| scripts/reproduce_figure3.py | 5594 |
| scripts/reproduce_figure4.py | 3949 |
| scripts/reproduce_main_results.py | 2191 |
| scripts/reproduce_table1.py | 6373 |
| scripts/reproduce_table2.py | 5027 |
| scripts/verify_hashes.py | 1136 |
| scripts/verify_oracle_identities.py | 741 |

Large frozen evidence may be served as an immutable release ZIP. No Git LFS or model-weight download is required for core reconstruction.
