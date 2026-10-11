#!/bin/bash
cd /root/ph/work/tri
while pgrep -f "run_kepler.py bg_gaia_G21.csv 1e6 3" >/dev/null; do sleep 20; done
/root/ph/venv/bin/python -I run_kepler.py bg_gaia_G21.csv 1e6 4 > log_G21_s4.txt 2>&1
for s in 1 2; do /root/ph/venv/bin/python -I run_kepler.py bg_gaia_G22p5.csv 1e6 $s > log_G22p5_s$s.txt 2>&1; done
for s in 1 2; do /root/ph/venv/bin/python -I run_kepler.py bg_gaia_G21.csv 1e6 $s hypo_cc_keckK.txt K > log_G21cc_s$s.txt 2>&1; done
echo done > batch_kepler2.done
