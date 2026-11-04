"""Guard against spreadsheet formula execution in user-supplied CSV text fields."""

from __future__ import annotations

import pandas as pd


def _escape(value: object) -> object:
    if not isinstance(value, str):
        return value
    # Spreadsheet programs can ignore leading whitespace before formula signs.
    if value.lstrip().startswith(("=", "+", "-", "@")) or value.startswith(("\t", "\r", "\n")):
        return "'" + value
    return value


def csv_safe(frame: pd.DataFrame) -> pd.DataFrame:
    """Return a copy safe for human spreadsheet viewing; never mutate analysis input.

    This is spreadsheet-viewer mitigation, not a data anonymisation method.
    """
    result = frame.copy()
    for column in result.columns:
        if result[column].dtype == object or pd.api.types.is_string_dtype(result[column].dtype):
            result[column] = result[column].map(_escape)
    return result
