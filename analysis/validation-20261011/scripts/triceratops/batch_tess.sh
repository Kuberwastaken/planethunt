#!/bin/bash
cd /root/ph/work/tri
for s in 1 2 3 4 5; do /root/ph/venv/bin/python -I run_tess.py tess_fold_600eq.npz 1e6 $s > log_tess600_s$s.txt 2>&1; done
for s in 1 2 3; do /root/ph/venv/bin/python -I run_tess.py tess_fold_600eq.npz 1e6 $s hypo_cc_speckle832.txt > log_tess600cc_s$s.txt 2>&1; done
echo done > batch_tess.done
