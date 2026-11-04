# Release notes - 2026 reproducibility refresh

**Scope:** Engineering refresh of the author's original 2023 NYC Airbnb exploratory notebook, also published on Kaggle. This is not a new research dataset or independent reanalysis of real listings.

## Changes

- Portable Python package, CLI and clean Jupyter quickstart.
- Replaced misleading `days_booked` / minimum-stay interpretations.
- Conservative price conversion, missingness checks and duplicate reporting.
- 19 Python regression tests, CI matrix and synthetic example charts.
- Preserved original notebook in `archive/` with personal paths and saved outputs removed.
- Linked original Kaggle notebook and profile; added Kaggle integration and licence-context docs.
- Added spreadsheet formula protection for exported free-text fields.
- Added code-of-conduct, security policy, contribution instructions and issue templates.

## Verified and not verified

- Local tests and synthetic CLI were executed in the release environment.
- Jupyter quickstart executed successfully with the installed `python3` kernel.
- Real-data analysis results were not independently reproduced because the original CSV is not packaged here.
- Hosted GitHub CI and Kaggle-side execution of the refreshed code remain unverified.
