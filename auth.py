"""Authentication helpers for admins and normal users."""

from __future__ import annotations

from pathlib import Path

from database import get_connection


def login(username: str, password: str, db_path: Path | str | None = None) -> dict | None:
    """
    Validate account credentials.

    Return user information on success, or None when the account/password pair
    is invalid.
    """
    username = username.strip()
    password = password.strip()
    if not username or not password:
        return None

    conn = get_connection(db_path)
    try:
        row = conn.execute(
            """
            SELECT id, username, role, name
            FROM users
            WHERE username = ?
              AND password = ?
              AND status = 'normal'
            """,
            (username, password),
        ).fetchone()
    finally:
        conn.close()

    return dict(row) if row is not None else None
