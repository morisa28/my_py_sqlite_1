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

BOOK_LIST_COLUMNS = ["图书编号", "书名", "作者", "出版社", "出版日期", "价格"]


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


def export_books_to_markdown(
    file_path: Path | str,
    db_path: Path | str | None = None,
) -> tuple[bool, str]:
    """Export all active books to a Markdown table file."""
    path = Path(file_path)
    if path.suffix.lower() != ".md":
        return False, "导出文件必须使用 .md 格式"

    rows = get_all_books_overview(db_path)
    lines = [
        "# 图书馆图书清单",
        "",
        "导入时请保留以下 Markdown 表格格式。",
        "",
        "| 图书编号 | 书名 | 作者 | 出版社 | 出版日期 | 价格 |",
        "|---|---|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            "| "
            + " | ".join(
                [
                    _escape_markdown_cell(row["book_no"]),
                    _escape_markdown_cell(row["title"]),
                    _escape_markdown_cell(row["author"]),
                    _escape_markdown_cell(row["publisher"]),
                    _escape_markdown_cell(row["publish_date"]),
                    f"{float(row['price']):.2f}",
                ]
            )
            + " |"
        )

    try:
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    except OSError as exc:
        return False, f"导出失败：{exc}"

    return True, f"成功导出 {len(rows)} 本图书到 {path}"


def import_books_from_markdown(
    file_path: Path | str,
    db_path: Path | str | None = None,
) -> tuple[bool, str]:
    """
    Import books from the fixed Markdown table format.

    Valid rows replace the current book list. Invalid or incomplete rows are
    skipped. If no valid book rows exist, the current database is left unchanged.
    """
    path = Path(file_path)
    if path.suffix.lower() != ".md":
        return False, "导入文件必须使用 .md 格式"

    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return False, f"导入失败：{exc}"
    except UnicodeDecodeError:
        return False, "导入失败：文件必须使用 UTF-8 编码"

    books, skipped_count = _parse_markdown_book_rows(text)
    if not books:
        return False, f"未找到有效图书行，已跳过 {skipped_count} 行，当前图书信息未改变"

    conn = get_connection(db_path)
    try:
        with conn:
            conn.execute("DELETE FROM borrow_records")
            conn.execute("DELETE FROM book_copies")
            conn.execute("DELETE FROM books")
            for book in books:
                conn.execute(
                    """
                    INSERT INTO books
                        (book_no, title, author, publisher, publish_date, price)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        book["book_no"],
                        book["title"],
                        book["author"],
                        book["publisher"],
                        book["publish_date"],
                        book["price"],
                    ),
                )
                book_id = conn.execute(
                    "SELECT id FROM books WHERE book_no = ?",
                    (book["book_no"],),
                ).fetchone()["id"]
                conn.executemany(
                    """
                    INSERT INTO book_copies (book_id, copy_no, status)
                    VALUES (?, ?, 'available')
                    """,
                    [(book_id, copy_no) for copy_no in range(1, 4)],
                )
    finally:
        conn.close()

    return True, f"成功导入 {len(books)} 本图书，跳过 {skipped_count} 行无效数据"


def _parse_markdown_book_rows(text: str) -> tuple[list[dict], int]:
    books = []
    skipped_count = 0
    seen_book_numbers = set()

    for line in text.splitlines():
        cells = _split_markdown_table_row(line)
        if cells is None:
            continue
        if _is_markdown_separator(cells) or cells == BOOK_LIST_COLUMNS:
            continue
        if len(cells) != len(BOOK_LIST_COLUMNS):
            skipped_count += 1
            continue

        book_no, title, author, publisher, publish_date, price = cells
        if book_no in seen_book_numbers:
            skipped_count += 1
            continue

        valid, _message, price_value = _validate_book_fields(
            book_no,
            author,
            publisher,
            publish_date,
            price,
            title=title,
        )
        if not valid or price_value is None:
            skipped_count += 1
            continue

        seen_book_numbers.add(book_no)
        books.append(
            {
                "book_no": book_no.strip(),
                "title": title.strip(),
                "author": author.strip(),
                "publisher": publisher.strip(),
                "publish_date": publish_date.strip(),
                "price": price_value,
            }
        )

    return books, skipped_count


def _split_markdown_table_row(line: str) -> list[str] | None:
    stripped = line.strip()
    if not stripped.startswith("|") or not stripped.endswith("|"):
        return None

    body = stripped[1:-1]
    cells = []
    current = []
    escaped = False
    for char in body:
        if escaped:
            current.append(char)
            escaped = False
            continue
        if char == "\\":
            escaped = True
            continue
        if char == "|":
            cells.append("".join(current).strip())
            current = []
            continue
        current.append(char)
    if escaped:
        current.append("\\")
    cells.append("".join(current).strip())
    return cells


def _is_markdown_separator(cells: list[str]) -> bool:
    return all(cell and set(cell) <= {"-", ":"} for cell in cells)


def _escape_markdown_cell(value: object) -> str:
    text = str(value).replace("\\", "\\\\").replace("|", "\\|")
    return " ".join(text.splitlines())
