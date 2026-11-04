# Contributing

Thank you for helping improve reproducible, transparent data analysis.

1. Review [METHODS](docs/METHODS.md), [DATA](data/README.md), and existing Issues.
2. Fork the repository and create a focused branch.
3. Install: `python -m pip install -e ".[dev]"`.
4. Reproduce using fictional data: `python -m nyc_airbnb demo --out demo-output`.
5. Run `python -m pytest -q` and include tests for any behaviour change.
6. Submit a pull request, noting data assumptions and research limitations.

Do not submit the large Kaggle CSV, scraped records, private keys, host names or guest information.
Avoid unsupported causal claims, bookings estimates, occupancy or revenue conclusions.
Use safe, synthetic test cases and avoid uploading personally identifying records in issues.

Beginner contributions: improve chart accessibility; enhance Windows setup notes;
add a sample notebook walkthrough or tests for malformed data.
