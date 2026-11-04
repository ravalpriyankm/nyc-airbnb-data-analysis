"""Deterministic fictional listings for offline demonstration and tests."""

from __future__ import annotations

import pandas as pd


def make_synthetic_listings(count: int = 80) -> pd.DataFrame:
    if count < 5 or count > 100000:
        raise ValueError("count must be between 5 and 100000")
    boroughs = ["Brooklyn", "Manhattan", "Queens", "Bronx", "Staten Island"]
    rooms = ["Entire home/apt", "Private room", "Shared room"]
    policies = ["strict", "moderate", "flexible"]
    rows = []
    for i in range(count):
        borough = boroughs[(i * 7) % 5]
        room = rooms[(i * 5) % 3]
        price = 55 + (i * 31) % 190 + (40 if borough == "Manhattan" else 0)
        rows.append({
            "id": i + 1, "NAME": f"FICTIONAL sample listing {i+1}",
            "host name": "SYNTHETIC HOST", "neighbourhood group": borough,
            "neighbourhood": f"Demo district {i % 11}", "room type": room,
            "price": f"${price:,}.00", "service fee": f"${price * 0.12:.2f}",
            "minimum nights": (i % 15) + 1,
            "availability 365": (i * 17) % 366,
            "cancellation_policy": policies[i % 3],
            "number of reviews": (i * 13) % 100,
            "Construction year": 1950 + (i % 70),
        })
    return pd.DataFrame(rows)
