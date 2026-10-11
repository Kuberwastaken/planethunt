#!/bin/bash
cd /root/ph/work/tess
python3 -I tfit.py free all 2500 1 > log_free_all.txt 2>&1
python3 -I tfit.py rho all 2500 2 > log_rho_all.txt 2>&1
python3 -I tfit.py free disc 2000 3 > log_free_disc.txt 2>&1
python3 -I tfit.py free late 2000 4 > log_free_late.txt 2>&1
echo done > batch_tfit.done
