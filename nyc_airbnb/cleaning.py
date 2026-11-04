"""Conservative cleaning: correct types without inventing prices or bookings."""

from __future__ import annotations

import re
from dataclasses import dataclass

import pandas as pd


REQUIRED_COLUMNS = {"neighbourhood_group", "room_type", "price"}
NUMERIC_NONNEGATIVE = ("service_fee", "number_of_reviews", "reviews_per_month", "calculated_host_listings_count")
BOROUGH_NAMES = {
    "brookln": "Brooklyn",
    "brooklyn": "Brooklyn",
    "manhatan": "Manhattan",
    "manhattan": "Manhattan",
    "queens": "Queens",
    "bronx": "Bronx",
    "staten island": "Staten Island",
}


def _column_name(name: object) -> str:
    return re.sub(r"_+", "_", re.sub(r"[^a-z0-9]+", "_", str(name).lower())).strip("_")


def _money(series: pd.Series) -> pd.Series:
    """Parse the source dataset's USD format, not arbitrary foreign formats."""
    text = series.astype("string").str.strip()
    text = text.str.replace(r"^\$\s*", "", regex=True).str.replace(",", "", regex=False)
    # Reject currency codes, parentheses or other adornments instead of guessing.
    valid = text.str.fullmatch(r"-?\d+(?:\.\d+)?").fillna(False)
    values = pd.to_numeric(text.where(valid), errors="coerce")
    return values.astype("Float64")


@dataclass
class CleanResult:
    frame: pd.DataFrame
    quality: dict


def clean_listings(source: pd.DataFrame) -> CleanResult:
    """Normalise and validate an in-memory NYC Airbnb source table.

    Missing values remain missing. The method never estimates occupancy, revenue,
    bookings or unknown prices. Exact duplicate raw rows are removed only once.
    """
    if source.empty:
        raise ValueError("Input dataset is empty.")
    df = source.copy()
    names = [_column_name(c) for c in df.columns]
    if len(set(names)) != len(names):
        raise ValueError("Column names collide after normalisation; inspect the source headings.")
    df.columns = names
    missing = REQUIRED_COLUMNS.difference(df.columns)
    if missing:
        raise ValueError("Required columns missing: " + ", ".join(sorted(missing)))

    raw_count = int(len(df))
    duplicate_count = int(df.duplicated().sum())
    df = df.drop_duplicates().copy()

    quality = {"source_rows": raw_count, "exact_duplicates_removed": duplicate_count}
    df["neighbourhood_group"] = df["neighbourhood_group"].astype("string").str.strip()
    df["neighbourhood_group"] = df["neighbourhood_group"].replace("", pd.NA)
    df["neighbourhood_group"] = df["neighbourhood_group"].map(
        lambda x: BOROUGH_NAMES.get(x.casefold(), x) if isinstance(x, str) else pd.NA
    )
    for key in ("room_type", "neighbourhood", "cancellation_policy", "host_identity_verified"):
        if key in df:
            df[key] = df[key].astype("string").str.strip().replace("", pd.NA)

    for key in ("price", "service_fee"):
        if key in df:
            original = df[key]
            values = _money(original)
            invalid = values.lt(0) | (values.eq(0) if key == "price" else False)
            quality[f"{key}_invalid_or_nonpositive"] = int(
                ((original.notna() & values.isna()) | invalid.fillna(False)).sum()
            )
            df[key] = values.mask(invalid)

    for key in (*NUMERIC_NONNEGATIVE, "minimum_nights", "availability_365", "construction_year", "review_rate_number"):
        if key not in df or key == "service_fee":
            continue
        original = df[key]
        values = pd.to_numeric(original, errors="coerce").astype("Float64")
        if key == "minimum_nights":
            invalid = values.lt(1)
        elif key == "availability_365":
            invalid = values.lt(0) | values.gt(365)
        elif key == "construction_year":
            invalid = values.lt(1700) | values.gt(2026)
        else:
            invalid = values.lt(0)
        quality[f"{key}_invalid"] = int(((original.notna() & values.isna()) | invalid.fillna(False)).sum())
        df[key] = values.mask(invalid)

    quality["cleaned_rows"] = int(len(df))
    quality["valid_prices"] = int(df["price"].notna().sum())
    quality["missing_by_column"] = {str(col): int(count) for col, count in df.isna().sum().items()}
    if "id" in df:
        quality["duplicate_non_null_listing_ids"] = int(df.loc[df["id"].notna(), "id"].duplicated().sum())
    return CleanResult(df.reset_index(drop=True), quality)


# Whitelisted exported columns omit names, description, coordinates and host IDs.
SAFE_EXPORT_COLUMNS = (
    "neighbourhood_group", "neighbourhood", "room_type", "price", "service_fee",
    "minimum_nights", "availability_365", "number_of_reviews", "reviews_per_month",
    "cancellation_policy", "construction_year", "review_rate_number", "host_identity_verified",
)


def safe_export(result: CleanResult) -> pd.DataFrame:
    from .safety import csv_safe

    return csv_safe(result.frame[[c for c in SAFE_EXPORT_COLUMNS if c in result.frame.columns]])
