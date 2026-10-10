#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
BASE="$(pwd)"
if [ ! -d ../upstream-tess/.git ]; then git clone https://github.com/paraschopra/tess-planet-candidates.git ../upstream-tess; fi
git -C ../upstream-tess checkout 74d5624f25391f459864fdeb4027d682b7c930a3
if [ ! -d ../upstream-eumemic/.git ]; then git clone https://github.com/eumemic/exoplanets.git ../upstream-eumemic; fi
git -C ../upstream-eumemic checkout 2cf0b116e08c3f692febc4a447cc8ad9ebe0713d
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-core.txt
mkdir -p lightcurves manifests results figures
