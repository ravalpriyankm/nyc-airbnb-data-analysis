# 2026 reproducibility review

The source archive supplied for this refresh contained four files: a 51-cell notebook, a short README, `.gitignore` and MIT `LICENSE`. There was **no source CSV**. The archived notebook had historical embedded tables and plots, but those cannot be independently verified without the source input.

### Confirmed original limitations
- Hard-coded `C:\\Users\\...\\Airbnb_Open_Data.csv` path.
- Used `list` as a dataframe variable, overshadowing the Python built-in.
- Filled all missing numeric values with column medians, obscuring missingness.
- Applied in-place filling and assumptions that can distort distributions.
- Renamed `availability 365` to `days_booked` (incorrect).
- Treated the sum of `minimum_nights` as booked nights (incorrect).
- Described the CSV as separate reviews and calendar tables (wrong input description).
- Displayed plots with deprecated/fragile seaborn arguments and did not separate source from derived conclusions.
- Mixed categorical counts with claims about which policy is "strictest" without standardisation.

### Treatment
- The original notebook is preserved in `archive/`, with execution output removed and the author's local file path changed to a relative example path. It is **archival**, not endorsed as scientifically correct.
- The maintained Python package and new quickstart notebook provide the corrected workflow.
- Synthetic figures are visually labelled and cannot be cited as real NYC results.
- The original MIT code licence is preserved; it does not cover third-party data.
- CSV text exports are spreadsheet-formula escaped to reduce accidental spreadsheet execution risk.

### Kaggle reference
The original author notebook is also published on Kaggle: https://www.kaggle.com/code/priyankraval/airbnb-data-analytics-final-project-ipynb. The 2026 changes in this repository are not yet uploaded to or verified on Kaggle. Licence contexts are recorded in `LICENSES_AND_PROVENANCE.md`.
