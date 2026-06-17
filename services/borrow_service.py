"""Borrowing, returning, and overdue checking services."""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

from database import get_connection


BORROW_LIMIT = 2
BORROW_DAYS = 30


def _today() -> date:
    return date.today()


def _overdue_info(due_date: str, status: str = "borrowed") -> tuple[str, int]:
    if status != "borrowed":
        return "否", 0
    days = (_today() - date.fromisoformat(due_date)).days
    return ("是", days) if days > 0 else ("否", 0)


def has_overdue_books(user_id: int, db_path: Path | str | None = None) -> bool:
    """Return whether the user has unreturned overdue books."""
    conn = get_connection(db_path)
    try:
        count = conn.execute(
            """
            SELECT COUNT(*)
            FROM borrow_records
            WHERE user_id = ?
              AND status = 'borrowed'
              AND due_date < ?
            """,
            (user_id, _today().isoformat()),
        ).fetchone()[0]
    finally:
        conn.close()
    return count > 0


def get_current_borrow_count(user_id: int, db_path: Path | str | None = None) -> int:
    """Return the number of currently borrowed books for the user."""
    conn = get_connection(db_path)
    try:
        count = conn.execute(
            """
            SELECT COUNT(*)
            FROM borrow_records
            WHERE user_id = ?
              AND status = 'borrowed'
            """,
            (user_id,),
        ).fetchone()[0]
    finally:
        conn.close()
    return int(count)


def borrow_book(
    user_id: int,
    book_no: str,
    db_path: Path | str | None = None,
) -> tuple[bool, str]:
    """Borrow one available copy of the specified book."""
    book_no = book_no.strip()
    if not book_no:
        return False, "图书编号不能为空"

    conn = get_connection(db_path)
    try:
        with conn:
            user = conn.execute(
                "SELECT id FROM users WHERE id = ? AND role = 'user' AND status = 'normal'",
                (user_id,),
            ).fetchone()
            if user is None:
                return False, "用户不存在或状态异常"

            overdue_count = conn.execute(
                """
                SELECT COUNT(*)
                FROM borrow_records
                WHERE user_id = ?
                  AND status = 'borrowed'
                  AND due_date < ?
                """,
                (user_id, _today().isoformat()),
            ).fetchone()[0]
            if overdue_count > 0:
                return False, "存在超期未还图书，不能借新书"

            current_count = conn.execute(
                """
                SELECT COUNT(*)
                FROM borrow_records
                WHERE user_id = ?
                  AND status = 'borrowed'
                """,
                (user_id,),
            ).fetchone()[0]
            if current_count >= BORROW_LIMIT:
                return False, "当前已借满 2 本书，不能继续借书"

            book = conn.execute(
                "SELECT id FROM books WHERE book_no = ? AND is_deleted = 0",
                (book_no,),
            ).fetchone()
            if book is None:
                return False, "图书不存在"

            copy = conn.execute(
                """
                SELECT id
                FROM book_copies
                WHERE book_id = ?
                  AND status = 'available'
                ORDER BY copy_no
                LIMIT 1
                """,
                (book["id"],),
            ).fetchone()
            if copy is None:
                return False, "该图书暂无可借副本"

            borrow_date = _today()
            due_date = borrow_date + timedelta(days=BORROW_DAYS)
            conn.execute(
                "UPDATE book_copies SET status = 'borrowed' WHERE id = ?",
                (copy["id"],),
            )
            conn.execute(
                """
                INSERT INTO borrow_records
                    (user_id, copy_id, borrow_date, due_date, status)
                VALUES (?, ?, ?, ?, 'borrowed')
                """,
                (user_id, copy["id"], borrow_date.isoformat(), due_date.isoformat()),
            )
    finally:
        conn.close()

    return True, "借书成功"


def return_book(
    user_id: int,
    record_id: int,
    db_path: Path | str | None = None,
) -> tuple[bool, str]:
    """Return a borrowed book by borrow record id."""
    conn = get_connection(db_path)
    try:
        with conn:
            record = conn.execute(
                """
                SELECT id, copy_id
                FROM borrow_records
                WHERE id = ?
                  AND user_id = ?
                  AND status = 'borrowed'
                """,
                (record_id, user_id),
            ).fetchone()
            if record is None:
                return False, "还书记录不存在或已经归还"

            conn.execute(
                """
                UPDATE borrow_records
                SET status = 'returned',
                    return_date = ?
                WHERE id = ?
                """,
                (_today().isoformat(), record["id"]),
            )
            conn.execute(
                "UPDATE book_copies SET status = 'available' WHERE id = ?",
                (record["copy_id"],),
            )
    finally:
        conn.close()

    return True, "还书成功"


def get_user_current_borrows(
    user_id: int,
    db_path: Path | str | None = None,
) -> list[dict]:
    """Return unreturned borrow records for a user."""
    conn = get_connection(db_path)
    try:
        rows = conn.execute(
            """
            SELECT
                r.id AS record_id,
                b.book_no,
                b.title,
                c.copy_no,
                r.borrow_date,
                r.due_date,
                r.return_date,
                r.status
            FROM borrow_records r
            JOIN book_copies c ON r.copy_id = c.id
            JOIN books b ON c.book_id = b.id
            WHERE r.user_id = ?
              AND r.status = 'borrowed'
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
                "record_id": row["record_id"],
                "book_no": row["book_no"],
                "title": row["title"],
                "copy_no": row["copy_no"],
                "borrow_date": row["borrow_date"],
                "due_date": row["due_date"],
                "return_date": row["return_date"],
                "status": row["status"],
                "is_overdue": is_overdue,
                "overdue_days": overdue_days,
            }
        )
    return result
