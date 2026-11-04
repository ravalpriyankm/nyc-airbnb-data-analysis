from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pandas as pd
import pytest

from nyc_airbnb.cleaning import clean_listings, safe_export
from nyc_airbnb.demo import make_synthetic_listings
from nyc_airbnb.figures import export_figures
from nyc_airbnb.reporting import build_tables, write_report
from nyc_airbnb.safety import csv_safe


def source(**extra):
    df = pd.DataFrame(
        [
            {"neighbourhood group": "Brookln", "room type": "Private room", "price": "$120", "minimum nights": 3, "availability 365": 100},
            {"neighbourhood group": "Manhatan", "room type": "Entire home/apt", "price": "$1,200.50", "minimum nights": 5, "availability 365": 365},
        ]
    )
    for k, v in extra.items():
        df[k] = v
    return df


def test_column_normalisation():
    df = clean_listings(source()).frame
    assert {"neighbourhood_group", "room_type", "price", "availability_365"} <= set(df.columns)
    assert set(df.neighbourhood_group) == {"Brooklyn", "Manhattan"}


def test_money_values_are_conservative():
    df = source()
    df.loc[0, "price"] = "$12x"
    df.loc[1, "price"] = "$-5"
    result = clean_listings(df)
    assert result.frame.price.isna().all()
    assert result.quality["price_invalid_or_nonpositive"] == 2


def test_duplicate_rows_removed_only_if_exact():
    df = source()
    df = pd.concat([df, df.iloc[[0]]], ignore_index=True)
    result = clean_listings(df)
    assert result.quality["source_rows"] == 3
    assert result.quality["exact_duplicates_removed"] == 1
    assert len(result.frame) == 2


def test_duplicate_listing_ids_reported_but_not_removed():
    df = source(id=[11, 11])
    result = clean_listings(df)
    assert len(result.frame) == 2
    assert result.quality["duplicate_non_null_listing_ids"] == 1


def test_borough_unknown_remains_missing():
    df = source()
    df.loc[0, "neighbourhood group"] = None
    assert pd.isna(clean_listings(df).frame.loc[0, "neighbourhood_group"])


def test_invalid_minimum_nights_and_availability():
    df = source()
    df.loc[0, "minimum nights"] = 0
    df.loc[1, "availability 365"] = 390
    result = clean_listings(df)
    assert pd.isna(result.frame.loc[0, "minimum_nights"])
    assert pd.isna(result.frame.loc[1, "availability_365"])
    assert result.quality["minimum_nights_invalid"] == 1
    assert result.quality["availability_365_invalid"] == 1


def test_required_columns_and_empty_input():
    with pytest.raises(ValueError, match="Required columns"):
        clean_listings(pd.DataFrame({"room type": ["a"], "price": ["$100"]}))
    with pytest.raises(ValueError, match="empty"):
        clean_listings(pd.DataFrame())


def test_duplicate_column_names_after_normalisation():
    df = source()
    df["room_type"] = "Private room"
    with pytest.raises(ValueError, match="collide"):
        clean_listings(df)


def test_never_infer_occupancy_or_bookings():
    tables = build_tables(clean_listings(source()))
    assert "availability_by_borough" in tables
    assert "listings_minimum_stay_up_to_10_nights" not in tables # no neighbourhood column
    assert all("booking" not in name and "occupancy" not in name for name in tables)


def test_summary_uses_price_median_and_count():
    result = clean_listings(source())
    price = build_tables(result)["price_by_borough"]
    manhattan = price.loc[price.neighbourhood_group == "Manhattan"].iloc[0]
    assert manhattan.median_usd == 1200.5
    assert manhattan.listings_with_price == 1


def test_safe_export_excludes_host_and_names():
    result = clean_listings(source(**{"host name": ["Alice", "Bob"], "name": ["A", "B"], "host id": [1, 2]}))
    export = safe_export(result)
    assert "host_name" not in export.columns
    assert "host_id" not in export.columns
    assert "name" not in export.columns


def test_csv_formula_mitigation():
    result = csv_safe(pd.DataFrame({"category": ["=2+3", "\t@CMD", "+SUM(1,2)", "-2+3", "Normal"], "count": [1, 2, 3, 4, 5]}))
    assert result.category.tolist() == ["'=2+3", "'\t@CMD", "'+SUM(1,2)", "'-2+3", "Normal"]
    assert result["count"].tolist() == [1, 2, 3, 4, 5]


def test_synthetic_is_deterministic_and_contains_no_real_addresses():
    a = make_synthetic_listings(25)
    b = make_synthetic_listings(25)
    assert a.equals(b)
    assert all("FICTIONAL" in name for name in a.NAME)


def test_synthetic_rejects_large_counts():
    with pytest.raises(ValueError):
        make_synthetic_listings(0)
    with pytest.raises(ValueError):
        make_synthetic_listings(100001)


def test_writes_reports(tmp_path):
    result = clean_listings(make_synthetic_listings(15))
    outputs = write_report(result, tmp_path, synthetic=True)
    assert outputs["quality"].exists()
    assert json.loads(outputs["quality"].read_text())["synthetic"] is True
    assert outputs["price_by_room_type"].exists()


def test_writes_four_figure_files(tmp_path):
    result = clean_listings(make_synthetic_listings(30))
    outputs = export_figures(result, tmp_path, synthetic=True)
    assert len(outputs) == 4
    assert all(p.stat().st_size > 1000 for p in outputs)


def test_cli_demo(tmp_path):
    proc = subprocess.run(
        [sys.executable, "-m", "nyc_airbnb", "demo", "--out", str(tmp_path)],
        capture_output=True, text=True, timeout=120, check=False,
    )
    assert proc.returncode == 0, proc.stderr
    assert "SYNTHETIC" in proc.stdout
    assert (tmp_path / "tables" / "quality.json").exists()


def test_cli_missing_input(tmp_path):
    proc = subprocess.run(
        [sys.executable, "-m", "nyc_airbnb", "analyse", "--input", str(tmp_path / "missing.csv")],
        capture_output=True, text=True, timeout=120, check=False,
    )
    assert proc.returncode == 2
    assert "Source CSV not found" in proc.stderr


def test_demo_safe_export_csv(tmp_path):
    df = make_synthetic_listings(10)
    df.loc[0, "neighbourhood"] = "=HYPERLINK(\"https://malicious.invalid\",\"click\")"
    src = tmp_path / "data.csv"
    df.to_csv(src, index=False)
    dest = tmp_path / "cleaned.csv"
    proc = subprocess.run([sys.executable, "-m", "nyc_airbnb", "clean", "--input", str(src), "--out", str(dest)],capture_output=True,text=True,timeout=120,check=False)
    assert proc.returncode == 0, proc.stderr
    assert "'=HYPERLINK" in dest.read_text()
