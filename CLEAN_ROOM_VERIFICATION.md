# Clean-room verification

ARTIFACT_LOCALLY_VERIFIED: PASS

The exact ZIP was extracted into a new directory. Only documented NumPy was installed in a fresh virtual environment; source-study environments were not used by the commands. Reproduction commands require no network, GPU, model weights, panels generation or RNG.

Archive: `reviewer_artifact_v1.zip`

SHA256: `bc31f7288a7b41a00d8bdf54bffcece1d5c12ccdf294d78f75939b303d58a5ca`

```json
{
  "environment": {
    "python": "3.8.20 (default, Oct  2 2024, 15:21:04) [MSC v.1929 64 bit (AMD64)]",
    "packages": {
      "numpy": "1.22.3"
    }
  },
  "runs": [
    {
      "command": "python scripts/verify_hashes.py",
      "exit_code": 0,
      "seconds": 0.6670229999999719
    },
    {
      "command": "python scripts/reproduce_main_results.py",
      "exit_code": 0,
      "seconds": 2.7752592999995613
    }
  ],
  "results": {
    "status": "PASS",
    "mapped_claims": 150,
    "numeric_comparisons": 414,
    "failures": [],
    "seconds": 2.6510694999999997,
    "new_random_draws": 0,
    "model_forwards": 0,
    "training_updates": 0
  }
}
```

This report is external to the ZIP to avoid a self-referential archive hash. It establishes local execution, not remote availability or manuscript synchronization.
