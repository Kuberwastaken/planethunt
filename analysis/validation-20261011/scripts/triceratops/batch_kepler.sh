#!/bin/bash
cd /root/ph/work/tri
for s in 1 2 3 4 5 6; do /root/ph/venv/bin/python -I run_kepler.py bg_gaia_G21.csv 1e6 $s > log_G21_s$s.txt 2>&1; done
for s in 1 2 3 4; do /root/ph/venv/bin/python -I run_kepler.py bg_gaia_G22p5.csv 1e6 $s > log_G22p5_s$s.txt 2>&1; done
echo done > batch_kepler.done
