# Verified scope and statistical boundaries

## Reproducibility levels

1. Inspect machine-readable frozen values: included for all five mapped main items.
2. Reconstruct points: Figure 2/3/4 from seed-level cached summaries; Table 1/2 from saved per-example predictions. These are not reconstructions from training initialization.
3. Reconstruct intervals: Figures 2–4 and Table 1 use exact saved per-draw statistics; Table 2 uses exact saved stratified episode index arrays. Each study's own percentiles are retained. Original index arrays are not included for studies using saved statistics, so the package does not independently repeat their upstream hierarchical resampling algorithm.
4. Checkpoint-forward evaluation: NO. Model weights and a tested inference environment are not bundled.
5. Full training: NO. Historical training/checkpoints/optimizers are absent.

## Units and definitions

The original Figure 2 measures use their frozen depth/output definitions. Figure 3 preserves its normalized N0_ABS, positive-relevance BETA_POS and held-out Bayesian KL K. Figure 4 uses probability squared-error decompositions and K in bits. Table 1 contrasts are raw squared-probability units; displayed main-paper values multiply them by one million. Table 2 uses continuous squared-output approximation errors, raw-output ABS/RMS and dimensionless F_WITHIN (displayed as percent). These units must not be pooled or interchanged.

For each stored interval, the claim map and protocol report its study, draw count, sampling unit, strata and percentile convention. Internal multi-seed uncertainty differs from external fixed-checkpoint episode uncertainty. No new resampling, p-values or familywise inference is performed.

## Reconstructing the saved uncertainty

Saved statistic arrays are numerical outputs of the frozen original resampling calculations, not newly generated approximations. Scripts independently take their specified percentiles and compare against separately stored authoritative intervals. Table 2 reconstructs every nonlinear statistic from the resampled intact episode pairs. Figure 4 uses the same common-four-cell draw index for both D-A and E-C. Historical S21 remains outside the Figure 4 authority.

## Oracle checks

`python scripts/verify_oracle_identities.py` checks the already-stored S23 complement recoding and S24 continuous sign recoding, including agreement with stored posterior/predictive references. It does not generate prompts or call a model. Full-precision stored predictions support the decomposition and error-share checks; rounded manuscript cells are never statistical inputs.

## Integrity and limits

All distributed inputs and code are covered by `MANIFEST.sha256`. These hashes detect changed artifacts; they do not independently authenticate upstream experimental execution. Expected CSVs are taken from frozen authoritative result records, not rounded PDF readings. Exact display strings annotate presentation only. A PASS means the mapped frozen numerical chain was reconstructed within declared absolute tolerance; it does not mean every historical scientific claim or experiment has been reproduced.
