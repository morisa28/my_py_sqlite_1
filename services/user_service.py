"""User lookup and borrowing status services for administrators."""

from __future__ import annotations

from datetime import date
from pathlib import Path

from database import get_connection


def _overdue_info(due_date: str | None, status: str | None) -> tuple[str, int]:
    if not due_date or status != "borrowed":
        return "否", 0
    days = (date.today() - date.fromisoformat(due_date)).days
    return ("是", days) if days > 0 else ("否", 0)


def get_user_borrow_status(
    keyword: str,
    db_path: Path | str | None = None,
) -> list[dict]:
    """Search users by id, username, or name and return borrow status rows."""
    keyword = keyword.strip()
    like_keyword = f"%{keyword}%"
    conn = get_connection(db_path)
    try:
        rows = conn.execute(
            """
            SELECT
                u.id AS user_id,
                u.username,
                u.name,
                b.book_no,
                b.title,
                c.copy_no,
                r.borrow_date,
                r.due_date,
                r.return_date,
                r.status
            FROM users u
            LEFT JOIN borrow_records r ON u.id = r.user_id
            LEFT JOIN book_copies c ON r.copy_id = c.id
            LEFT JOIN books b ON c.book_id = b.id
            WHERE u.role = 'user'
              AND (
                ? = ''
                OR CAST(u.id AS TEXT) = ?
                OR u.username LIKE ?
                OR u.name LIKE ?
              )
            ORDER BY u.username, r.status, r.borrow_date DESC, r.id DESC
            """,
            (keyword, keyword, like_keyword, like_keyword),
        ).fetchall()
    finally:
        conn.close()

    result = []
    for row in rows:
        is_overdue, overdue_days = _overdue_info(row["due_date"], row["status"])
        result.append(
            {
                "user_id": row["user_id"],
                "username": row["username"],
                "name": row["name"],
                "book_no": row["book_no"] or "",
                "title": row["title"] or "",
                "copy_no": row["copy_no"] or "",
                "borrow_date": row["borrow_date"] or "",
                "due_date": row["due_date"] or "",
                "return_date": row["return_date"] or "",
                "status": row["status"] or "无借阅记录",
                "is_overdue": is_overdue,
                "overdue_days": overdue_days,
            }
        )
    return result


def get_all_users(db_path: Path | str | None = None) -> list[dict]:
    """Return all users without exposing passwords."""
    conn = get_connection(db_path)
    try:
        rows = conn.execute(
            """
            SELECT
                u.id AS user_id,
                u.username,
                u.name,
                u.role,
                u.status,
                COALESCE(SUM(CASE WHEN r.status = 'borrowed' THEN 1 ELSE 0 END), 0) AS current_borrows,
                COUNT(r.id) AS history_records
            FROM users u
            LEFT JOIN borrow_records r ON u.id = r.user_id
            GROUP BY u.id
            ORDER BY u.role, u.username
            """
        ).fetchall()
    finally:
        conn.close()

    return [
        {
            "user_id": row["user_id"],
            "username": row["username"],
            "name": row["name"],
            "role": row["role"],
            "role_name": "管理员" if row["role"] == "admin" else "普通用户",
            "status": row["status"],
            "current_borrows": int(row["current_borrows"]),
            "history_records": int(row["history_records"]),
        }
        for row in rows
    ]


def get_user_borrow_records(
    user_id: int,
    db_path: Path | str | None = None,
) -> list[dict]:
    """Return borrow records for one user, including a blank row when none exist."""
    conn = get_connection(db_path)
    try:
        rows = conn.execute(
            """
            SELECT
                u.id AS user_id,
                u.username,
                u.name,
                b.book_no,
                b.title,
                c.copy_no,
                r.borrow_date,
                r.due_date,
                r.return_date,
                r.status
            FROM users u
            LEFT JOIN borrow_records r ON u.id = r.user_id
            LEFT JOIN book_copies c ON r.copy_id = c.id
            LEFT JOIN books b ON c.book_id = b.id
            WHERE u.id = ?
            ORDER BY r.borrow_date DESC, r.id DESC
            """,
            (user_id,),
        ).fetchall()
    finally:
        conn.close()

    result = []
    for row in rows:
        is_overdue, overdue_days = _overdue_info(row["due_date"], row["status"])
        result.append(
            {
                "user_id": row["user_id"],
                "username": row["username"],
                "name": row["name"],
                "book_no": row["book_no"] or "",
                "title": row["title"] or "",
                "copy_no": row["copy_no"] or "",
                "borrow_date": row["borrow_date"] or "",
                "due_date": row["due_date"] or "",
                "return_date": row["return_date"] or "",
                "status": row["status"] or "无借阅记录",
                "is_overdue": is_overdue,
                "overdue_days": overdue_days,
            }
        )
    return result
