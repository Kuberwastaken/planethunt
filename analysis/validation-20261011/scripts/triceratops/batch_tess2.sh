#!/bin/bash
cd /root/ph/work/tri
while pgrep -f "run_tess.py tess_fold_600eq.npz 1e6 1" >/dev/null; do sleep 20; done
for s in 2 3; do /root/ph/venv/bin/python -I run_tess.py tess_fold_600eq.npz 1e6 $s > log_tess600_s$s.txt 2>&1; done
for s in 1 2; do /root/ph/venv/bin/python -I run_tess.py tess_fold_600eq.npz 1e6 $s hypo_cc_speckle832.txt > log_tess600cc_s$s.txt 2>&1; done
echo done > batch_tess2.done
