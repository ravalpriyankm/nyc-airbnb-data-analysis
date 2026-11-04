"""Local-first CLI; never downloads or uploads source data."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

from .cleaning import clean_listings, safe_export
from .demo import make_synthetic_listings
from .figures import export_figures
from .reporting import write_report


def _analyse(source: pd.DataFrame, output: Path, *, synthetic: bool) -> None:
    result = clean_listings(source)
    paths = write_report(result, output / "tables", synthetic=synthetic)
    figures = export_figures(result, output / "figures", synthetic=synthetic)
    print(f"Input rows: {result.quality['source_rows']:,}; exact duplicates removed: {result.quality['exact_duplicates_removed']:,}")
    print(f"Valid listed prices: {result.quality['valid_prices']:,}")
    print(f"Generated {len(paths)} report tables and {len(figures)} figures under {output}")
    if synthetic:
        print("NOTICE: SYNTHETIC DEMO - no results refer to actual NYC listings.")
    else:
        print("NOTICE: Descriptive listing data only; availability is not occupancy or booked nights.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="nyc-airbnb", description="Reproducible NYC Airbnb listing analysis")
    sub = parser.add_subparsers(dest="action", required=True)
    demo = sub.add_parser("demo", help="Run offline using fabricated sample listings")
    demo.add_argument("--out", type=Path, default=Path("demo-output"))
    demo.add_argument("--rows", type=int, default=80)
    analyse = sub.add_parser("analyse", help="Analyse a local copy of Airbnb_Open_Data.csv")
    analyse.add_argument("--input", type=Path, required=True)
    analyse.add_argument("--out", type=Path, default=Path("reports/analysis"))
    clean = sub.add_parser("clean", help="Write locally cleaned, limited-column CSV")
    clean.add_argument("--input", type=Path, required=True)
    clean.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)

    try:
        if args.action == "demo":
            frame = make_synthetic_listings(args.rows)
            args.out.mkdir(parents=True, exist_ok=True)
            frame.to_csv(args.out / "synthetic_listings.csv", index=False)
            _analyse(frame, args.out, synthetic=True)
        else:
            if not args.input.is_file():
                raise ValueError(f"Source CSV not found: {args.input}")
            frame = pd.read_csv(args.input, low_memory=False)
            if args.action == "analyse":
                _analyse(frame, args.out, synthetic=False)
            else:
                result = clean_listings(frame)
                args.out.parent.mkdir(parents=True, exist_ok=True)
                safe_export(result).to_csv(args.out, index=False)
                print(f"Wrote {len(result.frame):,} cleaned records to {args.out}; no names/host IDs exported.")
    except (ValueError, OSError, pd.errors.ParserError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    return 0
