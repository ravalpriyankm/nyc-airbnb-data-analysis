# Update your existing GitHub repository

The ZIP is a **replacement working tree**, not a Git clone. Preserve your existing `.git/` history.

1. Clone the existing repository locally and make a backup of the original branch.
2. Extract this ZIP. Copy its content *inside* `nyc-airbnb-data-analysis/` to the cloned repo's root, including the hidden `.github` and `.gitattributes` files.
3. Replace the old root-level `Airbnb_Data_Analytics_Final_Project.ipynb` with the maintained `notebooks/quickstart.ipynb`. The original code remains archived under `archive/`.
4. Review any current files not supplied here before removing them. Do not delete unrelated commits or rewrite Git history merely to tidy the root.
5. Run `python -m pip install -e ".[dev]"`, `python -m pytest -q`, and `python -m nyc_airbnb demo --out demo-output`.
6. Review `git status`, stage intentional changes, commit and push via a pull request if feasible.
7. Inspect Actions results after upload; do not assume CI passes on GitHub just because local checks pass.
8. Set a clear repository description, topics, and optionally rename to `nyc-airbnb-data-analysis`. If renamed, update the README badge and `CITATION.cff` repository URL, plus Kaggle and external links. Use `docs/PORTFOLIO.md` for copyable text.
9. The GitHub profile README is delivered separately as `GitHub-Profile-README-with-Kaggle.md`. Paste that file into your special `ravalpriyankm` profile repository rather than inside this analysis repository.

Never upload the Kaggle source dataset or local real-data reports without verifying reuse terms and inspecting identifying fields.
