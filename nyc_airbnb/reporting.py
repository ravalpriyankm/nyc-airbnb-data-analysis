"""Descriptive statistics. No booking, causal, or revenue claims."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from .cleaning import CleanResult
from .safety import csv_safe


def _count(df: pd.DataFrame, group: str) -> pd.DataFrame:
    if group not in df:
        return pd.DataFrame(columns=[group, "listings"])
    out = df.groupby(group, dropna=True).size().rename("listings").reset_index()
    return out.sort_values("listings", ascending=False).reset_index(drop=True)


def _price(df: pd.DataFrame, group: str) -> pd.DataFrame:
    if group not in df:
        return pd.DataFrame(columns=[group, "listings_with_price", "median_usd", "mean_usd"])
    out = (
        df.dropna(subset=["price", group])
        .groupby(group)["price"]
        .agg(listings_with_price="count", median_usd="median", mean_usd="mean")
        .reset_index()
    )
    return out.sort_values("median_usd", ascending=False).reset_index(drop=True)


def build_tables(result: CleanResult) -> dict[str, pd.DataFrame]:
    df = result.frame
    tables: dict[str, pd.DataFrame] = {
        "listings_by_borough": _count(df, "neighbourhood_group"),
        "listings_by_room_type": _count(df, "room_type"),
        "price_by_borough": _price(df, "neighbourhood_group"),
        "price_by_room_type": _price(df, "room_type"),
    }
    if {"room_type", "cancellation_policy"} <= set(df.columns):
        tables["cancellation_policy_by_room_type"] = (
            df.dropna(subset=["room_type", "cancellation_policy"])
            .groupby(["room_type", "cancellation_policy"]).size()
            .rename("listings").reset_index().sort_values(["room_type", "listings"], ascending=[True, False])
        )
    if {"minimum_nights", "neighbourhood"} <= set(df.columns):
        short = df.loc[df["minimum_nights"].le(10).fillna(False)]
        tables["listings_minimum_stay_up_to_10_nights"] = _count(short, "neighbourhood").head(15)
    if "availability_365" in df:
        tables["availability_by_borough"] = (
            df.dropna(subset=["neighbourhood_group", "availability_365"])
            .groupby("neighbourhood_group")["availability_365"]
            .agg(listings_with_availability="count", median_available_days="median")
            .reset_index().sort_values("median_available_days", ascending=False)
        )
    if "construction_year" in df:
        tables["reported_construction_year_counts"] = _count(
            df.dropna(subset=["construction_year"]), "construction_year"
        ).sort_values("construction_year")
    return tables


def write_report(result: CleanResult, output: Path, *, synthetic: bool) -> dict[str, Path]:
    output.mkdir(parents=True, exist_ok=True)
    quality_path = output / "quality.json"
    quality_path.write_text(json.dumps({**result.quality, "synthetic": synthetic}, indent=2), encoding="utf-8")
    table_paths = {}
    for name, table in build_tables(result).items():
        path = output / f"{name}.csv"
        csv_safe(table).to_csv(path, index=False)
        table_paths[name] = path
    return {"quality": quality_path, **table_paths}
