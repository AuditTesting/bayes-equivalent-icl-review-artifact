Anonymous reviewer artifact for a double-blind ICLR submission.

## Download the complete verified artifact

Download [reviewer_artifact_v1.zip](https://github.com/AuditTesting/bayes-equivalent-icl-review-artifact/releases/download/v1/reviewer_artifact_v1.zip) from release v1 and extract it before running the commands below. This repository provides browsable code and documentation; the release ZIP includes all frozen numerical inputs. GitHub's automatically generated source ZIP is not the complete artifact.

Archive SHA256: `bc31f7288a7b41a00d8bdf54bffcece1d5c12ccdf294d78f75939b303d58a5ca`

See [CLEAN_ROOM_VERIFICATION.md](CLEAN_ROOM_VERIFICATION.md) for measured verification: 150 mapped claims, 414 numerical comparisons, zero failures. Only cached Levels 1–3 are supported; checkpoint forward evaluation and full training are not supplied.

# Scope

This package reconstructs the principal numerical data behind Figures 2–4 and Tables 1–2, including selected frozen uncertainty calculations. It uses existing machine-readable seed statistics, prediction caches, saved bootstrap statistics or indices. It runs no model inference or training and creates no new evaluation panels or resampling draws.

## Quick start

Use Python 3.8–3.10 with the documented NumPy version. A fresh environment is recommended:

```text
python -m venv .venv
# Activate .venv using your operating system's usual command.
python -m pip install -r requirements-core.txt
python scripts/verify_hashes.py
python scripts/reproduce_main_results.py
```

Once NumPy is installed, both verification commands are entirely offline and CPU-only. Run them from the extracted artifact root. Results appear under `reproduced/`, including a PASS/FAIL record for every mapped numerical claim.

## Main-paper mapping

| Item | Inputs | Reconstruction |
| --- | --- | --- |
| Figure 2 | Per-seed checkpoint metrics; frozen bootstrap statistics | Longitudinal/depth numerical data |
| Figure 3 | Twelve seed trajectories at 200k/400k/800k; saved trajectory draws | Cohort points and paired changes |
| Figure 4 / S22 | A/C/D/E seed endpoints; common-four-cell saved draws | All four endpoints; D-A and E-C within-error/K contrasts |
| Table 1 / S23 | A/C/D transfer predictions, encoded panels, saved draws | Z/P recoding contrasts and posterior identity |
| Table 2 / S24 | Serialized panels, predictions, saved position-stratified indices | Seven metrics, intervals and continuous oracle identity |

See `expected/claim_source_map.csv` for exact sources, display values, full-precision values, uncertainty authorities and tolerances. Numerical data reconstruction is the target; this package does not recreate figure artwork.

## Statistical reconstruction

Levels 1–3 are supported for the mapped outputs: inspection, cached-input point estimates, and selected intervals from frozen resampling records. Figure 4 uses S22 common-four-cell draws, never historical S21 intervals. S23 and S24 retain their own uncertainty populations. For Table 2, pairs and demonstration-position counts stay intact; F_WITHIN and RMS are recomputed for every saved draw. No new RNG is used.

The exact squared-error identities `E_PAIR = E_SHARED + E_WITHIN` and `F_WITHIN = E_WITHIN/E_PAIR = RMS_DELTA**2/(4*E_PAIR)` are checked from full-precision external predictions. See `REPRODUCIBILITY.md` and `protocols/` for limitations and units.

## External checkpoint provenance

The external task uses the public Garg et al. model from [the official repository](https://github.com/dtsip/in-context-learning). `protocols/table2.json` records the release URL, commit and checkpoint/config hashes. For optional provenance inspection, download the official `models.zip` release listed there, extract `models/linear_regression/pretrained/state.pt`, and compare its SHA256 against the recorded hash. That download is not needed by any command in this package. No checkpoint-forward workflow is supplied or claimed.

## Included and excluded assets

Included: anonymous reconstruction scripts, necessary cached statistics/predictions, selected serialized oracle panels, frozen resampling records and expected numerical values. Excluded: historical training checkpoints, third-party weights/source code, optimizer states, credentials, local paths, local git history, manuscript project files and full training infrastructure. An external model being public does not by itself reproduce this audit's frozen outputs.

## Known limitations

Cached-statistic reconstruction does not independently validate training or all upstream raw measurements. Where saved replicate statistics are used, their percentile endpoints are checked but no new hierarchical resampling is performed. Uncertainty is study-specific; the external audit is conditional on one fixed checkpoint and is not training-seed replication. Levels 4 and 5—checkpoint-forward and full-training reproduction—are not supported.

## Runtime and integrity

The intended runtime is a few minutes or less on ordinary CPU. The accompanying clean-room verification records the measured runtime and exact archive hash. `MANIFEST.sha256` covers distributed files; generated `reproduced/` files are excluded. See `NOTICE` for review-only availability and third-party boundaries.
