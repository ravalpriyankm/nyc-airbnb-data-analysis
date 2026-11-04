"""Export well-labelled plots; avoid implying that availability equals bookings."""

from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from .cleaning import CleanResult
from .reporting import build_tables


def export_figures(result: CleanResult, output: Path, *, synthetic: bool = False) -> list[Path]:
    output.mkdir(parents=True, exist_ok=True)
    tables = build_tables(result)
    specifications = [
        ("listings_by_borough", "neighbourhood_group", "listings", "Listings by NYC borough", "Listing records"),
        ("price_by_borough", "neighbourhood_group", "median_usd", "Median listed price by borough", "Median listed price (USD)"),
        ("listings_by_room_type", "room_type", "listings", "Listings by room type", "Listing records"),
        ("price_by_room_type", "room_type", "median_usd", "Median listed price by room type", "Median listed price (USD)"),
    ]
    created = []
    for table_name, category, value, title, xlabel in specifications:
        table = tables.get(table_name)
        if table is None or table.empty:
            continue
        data = table.sort_values(value, ascending=True).tail(12)
        fig, ax = plt.subplots(figsize=(8.5, max(3.5, len(data) * 0.48 + 1.7)))
        ax.barh(data[category].astype(str), data[value].astype(float))
        ax.set_title(title)
        ax.set_xlabel(xlabel)
        if synthetic:
            fig.text(0.5, 0.02, "SYNTHETIC DEMO - NOT REAL NYC LISTING FINDINGS", ha="center", fontsize=9)
        fig.tight_layout(rect=(0, 0.06 if synthetic else 0, 1, 1))
        target = output / f"{table_name}.png"
        fig.savefig(target, dpi=140)
        plt.close(fig)
        created.append(target)
    return created
