"""Shared helpers for sortable Treeview tables."""

from __future__ import annotations

import re
from datetime import date
from typing import Any


ColumnSpec = tuple[str, str, int]


def initial_sort_key(columns: list[ColumnSpec]) -> str:
    """Use book number as the default sort key when the table has it."""
    keys = [column[0] for column in columns]
    return "book_no" if "book_no" in keys else keys[0]


def sort_rows(rows: list[dict], key: str, descending: bool) -> list[dict]:
    """Return rows sorted by a Treeview column."""
    return sorted(rows, key=lambda row: sortable_value(row.get(key)), reverse=descending)


def sortable_value(value: Any) -> tuple:
    """Normalize common table values for predictable ascending/descending sort."""
    if value is None:
        return (5, "")
    if isinstance(value, (int, float)):
        return (0, value)

    text = str(value).strip()
    if not text:
        return (5, "")

    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", text):
        try:
            return (1, date.fromisoformat(text))
        except ValueError:
            pass

    try:
        return (2, float(text))
    except ValueError:
        pass

    match = re.fullmatch(r"([A-Za-z]+)(\d+)", text)
    if match:
        prefix, number = match.groups()
        return (3, prefix.lower(), int(number))

    return (4, text.casefold())


def heading_text(title: str, key: str, sort_key: str, descending: bool) -> str:
    """Return heading text with a compact sort indicator."""
    if key != sort_key:
        return title
    return f"{title} {'↓' if descending else '↑'}"
