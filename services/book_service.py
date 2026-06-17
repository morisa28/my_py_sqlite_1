"""Book search and administrator book-management services."""

from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path

from database import get_connection


BOOK_OVERVIEW_SQL = """
SELECT
    b.id,
    b.book_no,
    b.title,
    b.author,
    b.publisher,
    b.publish_date,
    b.price,
    COUNT(CASE WHEN c.status != 'deleted' THEN 1 END) AS total_copies,
    COALESCE(SUM(CASE WHEN c.status = 'available' THEN 1 ELSE 0 END), 0) AS available_copies,
    COALESCE(SUM(CASE WHEN c.status = 'borrowed' THEN 1 ELSE 0 END), 0) AS borrowed_copies
FROM books b
LEFT JOIN book_copies c ON b.id = c.book_id
WHERE b.is_deleted = 0
"""


def _format_book_row(row: sqlite3.Row) -> dict:
    available = int(row["available_copies"])
    return {
        "id": row["id"],
        "book_no": row["book_no"],
        "title": row["title"],
        "author": row["author"],
        "publisher": row["publisher"],
        "publish_date": row["publish_date"],
        "price": float(row["price"]),
        "total_copies": int(row["total_copies"]),
        "available_copies": available,
        "borrowed_copies": int(row["borrowed_copies"]),
        "book_status": "在库" if available > 0 else "不在库",
    }


def _validate_book_fields(
    book_no: str,
    author: str,
    publisher: str,
    publish_date: str,
    price: float | str,
    title: str | None = None,
) -> tuple[bool, str, float | None]:
    if not book_no.strip():
        return False, "图书编号不能为空", None
    if title is not None and not title.strip():
        return False, "书名不能为空", None
    if not author.strip():
        return False, "作者不能为空", None
    if not publisher.strip():
        return False, "出版社不能为空", None
    try:
        datetime.strptime(publish_date.strip(), "%Y-%m-%d")
    except ValueError:
        return False, "出版日期必须使用 YYYY-MM-DD 格式", None
    try:
        price_value = float(price)
    except (TypeError, ValueError):
        return False, "价格必须为数字", None
    if price_value < 0:
        return False, "价格不能为负数", None
    return True, "", price_value


def search_books(keyword: str = "", db_path: Path | str | None = None) -> list[dict]:
    """Search active books by book number or title."""
    keyword = keyword.strip()
    like_keyword = f"%{keyword}%"
    conn = get_connection(db_path)
    try:
        rows = conn.execute(
            BOOK_OVERVIEW_SQL
            + """
              AND (? = '' OR b.book_no LIKE ? OR b.title LIKE ?)
            GROUP BY b.id
            ORDER BY b.book_no
            """,
            (keyword, like_keyword, like_keyword),
        ).fetchall()
    finally:
        conn.close()
    return [_format_book_row(row) for row in rows]


def get_all_books_overview(db_path: Path | str | None = None) -> list[dict]:
    """Return status overview for all active books."""
    conn = get_connection(db_path)
    try:
        rows = conn.execute(
            BOOK_OVERVIEW_SQL
            + """
            GROUP BY b.id
            ORDER BY b.book_no
            """
        ).fetchall()
    finally:
        conn.close()
    return [_format_book_row(row) for row in rows]


def get_book_copies_detail(book_no: str, db_path: Path | str | None = None) -> list[dict]:
    """Return per-copy status details for an active book."""
    conn = get_connection(db_path)
    try:
        rows = conn.execute(
            """
            SELECT
                b.book_no,
                b.title,
                c.copy_no,
                c.status AS copy_status,
                u.username AS borrower_username,
                u.name AS borrower_name,
                r.borrow_date,
                r.due_date,
                r.return_date
            FROM books b
            JOIN book_copies c ON b.id = c.book_id
            LEFT JOIN borrow_records r ON c.id = r.copy_id AND r.status = 'borrowed'
            LEFT JOIN users u ON r.user_id = u.id
            WHERE b.book_no = ?
              AND b.is_deleted = 0
              AND c.status != 'deleted'
            ORDER BY c.copy_no
            """,
            (book_no.strip(),),
        ).fetchall()
    finally:
        conn.close()
    return [dict(row) for row in rows]


def add_book(
    book_no: str,
    title: str,
    author: str,
    publisher: str,
    publish_date: str,
    price: float | str,
    db_path: Path | str | None = None,
) -> tuple[bool, str]:
    """Add a new book and create three available copy records."""
    valid, message, price_value = _validate_book_fields(
        book_no, author, publisher, publish_date, price, title=title
    )
    if not valid:
        return False, message

    conn = get_connection(db_path)
    try:
        with conn:
            conn.execute(
                """
                INSERT INTO books
                    (book_no, title, author, publisher, publish_date, price)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    book_no.strip(),
                    title.strip(),
                    author.strip(),
                    publisher.strip(),
                    publish_date.strip(),
                    price_value,
                ),
            )
            book_id = conn.execute(
                "SELECT id FROM books WHERE book_no = ?",
                (book_no.strip(),),
            ).fetchone()["id"]
            conn.executemany(
                """
                INSERT INTO book_copies (book_id, copy_no, status)
                VALUES (?, ?, 'available')
                """,
                [(book_id, copy_no) for copy_no in range(1, 4)],
            )
    except sqlite3.IntegrityError:
        return False, "图书编号已存在"
    finally:
        conn.close()

    return True, "图书录入成功，并已生成 3 个副本"


def delete_book(book_no: str, db_path: Path | str | None = None) -> tuple[bool, str]:
    """Logically delete a book when none of its copies are borrowed."""
    book_no = book_no.strip()
    if not book_no:
        return False, "图书编号不能为空"

    conn = get_connection(db_path)
    try:
        with conn:
            book = conn.execute(
                "SELECT id FROM books WHERE book_no = ? AND is_deleted = 0",
                (book_no,),
            ).fetchone()
            if book is None:
                return False, "图书不存在"

            borrowed_count = conn.execute(
                """
                SELECT COUNT(*)
                FROM book_copies
                WHERE book_id = ?
                  AND status = 'borrowed'
                """,
                (book["id"],),
            ).fetchone()[0]
            if borrowed_count > 0:
                return False, "该图书仍有副本借出，不能删除"

            conn.execute(
                "UPDATE books SET is_deleted = 1 WHERE id = ?",
                (book["id"],),
            )
            conn.execute(
                "UPDATE book_copies SET status = 'deleted' WHERE book_id = ?",
                (book["id"],),
            )
    finally:
        conn.close()

    return True, "图书删除成功"


def update_book(
    book_no: str,
    author: str,
    publisher: str,
    publish_date: str,
    price: float | str,
    db_path: Path | str | None = None,
) -> tuple[bool, str]:
    """Update editable book fields. The title is intentionally immutable."""
    valid, message, price_value = _validate_book_fields(
        book_no, author, publisher, publish_date, price
    )
    if not valid:
        return False, message

    conn = get_connection(db_path)
    try:
        with conn:
            result = conn.execute(
                """
                UPDATE books
                SET author = ?,
                    publisher = ?,
                    publish_date = ?,
                    price = ?
                WHERE book_no = ?
                  AND is_deleted = 0
                """,
                (
                    author.strip(),
                    publisher.strip(),
                    publish_date.strip(),
                    price_value,
                    book_no.strip(),
                ),
            )
            if result.rowcount == 0:
                return False, "图书不存在"
    finally:
        conn.close()

    return True, "图书信息修改成功"
