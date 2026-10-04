#!/usr/bin/env bash
# Reproduce every table in RESULTS.md.
# GT=path/to/rgbd_dataset_freiburg1_xyz/groundtruth.txt  (TUM RGB-D, see README)
set -euo pipefail
cd "$(dirname "$0")"
: "${GT:?set GT to a TUM groundtruth.txt path}"

python run.py --selftest
python run.py --split 0.7 --out results/synth_heldout.json
python run.py --split 1.0 --out results/synth_full.json
python run.py --split 0.7 --heading absolute --out results/synth_abs_head.json
python run.py --gt "$GT" --mode se2 --step 10 --stride 1 --out results/tum_se2_s10.json
python run.py --gt "$GT" --mode se2 --step 2  --stride 1 --out results/tum_se2_s2.json
python run.py --gt "$GT" --mode xyz --step 10 --stride 1 --out results/tum_xyz_s10.json
python run.py --gt "$GT" --mode xyz --step 1  --stride 1 --out results/tum_xyz_s1.json
python report.py --dir results --out RESULTS.md
