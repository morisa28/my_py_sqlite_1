"""Authentication helpers for admins and normal users."""

from __future__ import annotations

import sqlite3
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


def register_user(
    username: str,
    password: str,
    confirm_password: str,
    name: str,
    db_path: Path | str | None = None,
) -> tuple[bool, str]:
    """Register a normal user account."""
    username = username.strip()
    password = password.strip()
    confirm_password = confirm_password.strip()
    name = name.strip()

    if not username:
        return False, "账号不能为空"
    if not password:
        return False, "密码不能为空"
    if password != confirm_password:
        return False, "两次输入的密码不一致"
    if not name:
        return False, "姓名不能为空"

    conn = get_connection(db_path)
    try:
        with conn:
            conn.execute(
                """
                INSERT INTO users (username, password, role, name)
                VALUES (?, ?, 'user', ?)
                """,
                (username, password, name),
            )
    except sqlite3.IntegrityError:
        return False, "账号已存在"
    finally:
        conn.close()

    return True, "注册成功，请使用新账号登录"
