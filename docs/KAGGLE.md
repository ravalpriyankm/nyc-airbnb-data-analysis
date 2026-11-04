# Kaggle and GitHub: how the projects relate

## Public Kaggle work

- Author profile: https://www.kaggle.com/priyankraval
- Original Airbnb analytics notebook (published around 2023): https://www.kaggle.com/code/priyankraval/airbnb-data-analytics-final-project-ipynb
- Notebook's original dataset: https://www.kaggle.com/datasets/arianazmoudeh/airbnbopendata

The Kaggle notebook shows the 2023 analysis as originally authored. It is **not** an independent test of the 2026 maintained code, nor evidence that the historical booking and availability interpretations were correct. The maintained package intentionally corrects those interpretations. User profile counts and notebook view numbers are omitted because they are time-sensitive.

## Run the 2026 package locally

```bash
python -m pip install -e ".[dev]"
python -m nyc_airbnb demo --out demo-output
python -m pytest -q
```

For real data, download `Airbnb_Open_Data.csv` yourself from the dataset page and run:

```bash
python -m nyc_airbnb analyse --input data/raw/Airbnb_Open_Data.csv --out reports/real-data
```

## Using a Kaggle Notebook

Kaggle can mount the third-party data in a read-only `/kaggle/input/` directory. The mounted directory name can change across versions; inspect it rather than hard-coding a guessed path:

```python
from pathlib import Path
matches = sorted(Path('/kaggle/input').glob('**/Airbnb_Open_Data.csv'))
assert len(matches) == 1, f'Expected one source file; found {matches}'
csv_path = matches[0]
```

To run the **maintained** package on Kaggle, supply its source files through a permitted GitHub checkout or an uploaded Kaggle Dataset, install the package from that local source, and use `csv_path` as the CLI `--input` path. Do not paste credentials into a public notebook or assume internet access during notebook execution. Always cite the original dataset author. Avoid publishing raw rows or sensitive host information in output artifacts.

## Linking profiles

Link the GitHub repository from the Kaggle notebook's description and add the Kaggle notebook and profile under the GitHub README. Use a description such as:

> The original NYC Airbnb EDA notebook was published in 2023. A reproducible GitHub refresh now includes corrected availability interpretation, testable Python code and synthetic examples: https://github.com/ravalpriyankm/nyc-airbnb-data-analysis

If the repository remains under its original name, use the actual live URL instead of the suggested renamed path.
