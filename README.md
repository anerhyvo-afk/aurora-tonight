# Aurora Tonight in Lapland

Free, live northern lights verdicts for Rovaniemi, Levi and Saariselkä.

`fetch.py` (Python standard library only) pulls live data and writes `data.json`; `index.html` renders it.
A GitHub Actions workflow refreshes every 15 minutes and deploys to GitHub Pages.

## Setup
1. Push to GitHub, then Settings → Pages → Source: **GitHub Actions**.
2. Custom domain: add it in Settings → Pages (or add a `CNAME` file containing the domain, e.g. `example.fi`) and point DNS at GitHub Pages. No CNAME file is included yet.

## Scoring
score = 100 × activity × (1 − cloud/100) × darkness. Good ≥ 40, Possible ≥ 15, else Unlikely.

## Data credits
- Finnish Meteorological Institute (FMI): R-index auroral activity and HARMONIE cloud cover forecast. Licensed CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/).
- NOAA Space Weather Prediction Center: planetary Kp index and forecast (public domain).

A forecast, not a guarantee.
