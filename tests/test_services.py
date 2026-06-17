"""Service-layer tests using a temporary SQLite database."""

from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from auth import login, register_user
from database import init_db
from services.book_service import (
    add_book,
    delete_book,
    export_books_to_markdown,
    get_all_books_overview,
    import_books_from_markdown,
    search_books,
    update_book,
)
from services.borrow_service import borrow_book, get_user_current_borrows, return_book
from services.user_service import get_user_borrow_status
from ui.table_utils import sort_rows


class LibraryServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.tmp_dir.name) / "library_test.db"
        init_db(self.db_path)

    def tearDown(self) -> None:
        self.tmp_dir.cleanup()

    def test_initial_data_counts(self) -> None:
        conn = sqlite3.connect(self.db_path)
        try:
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM users").fetchone()[0], 11)
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM books").fetchone()[0], 20)
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM book_copies").fetchone()[0], 60)
        finally:
            conn.close()

    def test_login_roles(self) -> None:
        admin = login("admin", "admin123", self.db_path)
        user = login("user01", "123456", self.db_path)
        self.assertIsNotNone(admin)
        self.assertIsNotNone(user)
        self.assertEqual(admin["role"], "admin")
        self.assertEqual(user["role"], "user")
        self.assertIsNone(login("user01", "wrong", self.db_path))

    def test_register_user(self) -> None:
        ok, message = register_user("reader01", "abc123", "abc123", "新读者", self.db_path)
        self.assertTrue(ok, message)

        user = login("reader01", "abc123", self.db_path)
        self.assertIsNotNone(user)
        self.assertEqual(user["role"], "user")
        self.assertEqual(user["name"], "新读者")

        ok, message = register_user("reader01", "abc123", "abc123", "重复读者", self.db_path)
        self.assertFalse(ok)
        self.assertIn("已存在", message)

        ok, message = register_user("reader02", "abc123", "different", "读者02", self.db_path)
        self.assertFalse(ok)
        self.assertIn("不一致", message)

    def test_borrow_limit_and_return(self) -> None:
        user = login("user01", "123456", self.db_path)
        self.assertTrue(borrow_book(user["id"], "B001", self.db_path)[0])
        self.assertTrue(borrow_book(user["id"], "B002", self.db_path)[0])

        ok, message = borrow_book(user["id"], "B003", self.db_path)
        self.assertFalse(ok)
        self.assertIn("2", message)

        current = get_user_current_borrows(user["id"], self.db_path)
        self.assertEqual(len(current), 2)

        ok, message = return_book(user["id"], current[0]["record_id"], self.db_path)
        self.assertTrue(ok, message)
        self.assertEqual(len(get_user_current_borrows(user["id"], self.db_path)), 1)

    def test_admin_book_management(self) -> None:
        ok, message = add_book("B021", "测试图书", "测试作者", "测试出版社", "2024-01-01", "38.5", self.db_path)
        self.assertTrue(ok, message)
        self.assertEqual(search_books("B021", self.db_path)[0]["total_copies"], 3)

        ok, message = add_book("B021", "重复图书", "测试作者", "测试出版社", "2024-01-01", 38.5, self.db_path)
        self.assertFalse(ok)
        self.assertIn("已存在", message)

        ok, message = update_book("B021", "新作者", "新出版社", "2024-02-01", "45", self.db_path)
        self.assertTrue(ok, message)
        self.assertEqual(search_books("B021", self.db_path)[0]["title"], "测试图书")

        ok, message = delete_book("B021", self.db_path)
        self.assertTrue(ok, message)
        self.assertEqual(search_books("B021", self.db_path), [])

    def test_delete_borrowed_book_is_blocked(self) -> None:
        user = login("user01", "123456", self.db_path)
        self.assertTrue(borrow_book(user["id"], "B001", self.db_path)[0])

        ok, message = delete_book("B001", self.db_path)
        self.assertFalse(ok)
        self.assertIn("借出", message)

    def test_user_borrow_status_query(self) -> None:
        user = login("user01", "123456", self.db_path)
        self.assertTrue(borrow_book(user["id"], "B001", self.db_path)[0])

        rows = get_user_borrow_status("user01", self.db_path)
        self.assertGreaterEqual(len(rows), 1)
        self.assertEqual(rows[0]["username"], "user01")
        self.assertEqual(rows[0]["book_no"], "B001")

    def test_overview_and_search(self) -> None:
        overview = get_all_books_overview(self.db_path)
        self.assertEqual(len(overview), 20)
        self.assertGreaterEqual(len(search_books("Python", self.db_path)), 1)

    def test_book_number_sort_uses_numeric_suffix(self) -> None:
        rows = [{"book_no": "B010"}, {"book_no": "B002"}, {"book_no": "B001"}]
        sorted_rows = sort_rows(rows, "book_no", descending=False)
        self.assertEqual([row["book_no"] for row in sorted_rows], ["B001", "B002", "B010"])

    def test_export_books_to_markdown(self) -> None:
        output_path = Path(self.tmp_dir.name) / "books.md"
        ok, message = export_books_to_markdown(output_path, self.db_path)
        self.assertTrue(ok, message)

        content = output_path.read_text(encoding="utf-8")
        self.assertIn("| 图书编号 | 书名 | 作者 | 出版社 | 出版日期 | 价格 |", content)
        self.assertIn("| B001 | Python程序设计 | 张三 | 清华大学出版社 | 2021-01-10 | 59.80 |", content)

    def test_import_books_from_markdown_overwrites_books_and_skips_invalid_rows(self) -> None:
        user = login("user01", "123456", self.db_path)
        self.assertTrue(borrow_book(user["id"], "B001", self.db_path)[0])

        input_path = Path(self.tmp_dir.name) / "import_books.md"
        input_path.write_text(
            "\n".join(
                [
                    "# 图书馆图书清单",
                    "",
                    "| 图书编号 | 书名 | 作者 | 出版社 | 出版日期 | 价格 |",
                    "|---|---|---|---|---|---|",
                    "| X001 | 新书一 | 作者一 | 出版社一 | 2025-01-01 | 21.5 |",
                    "| X002 | 新书二 | 作者二 | 出版社二 | 2025-02-02 | 32.0 |",
                    "| X003 | 缺少价格 | 作者三 | 出版社三 | 2025-03-03 |",
                    "| X004 | 日期错误 | 作者四 | 出版社四 | 2025/04/04 | 44.0 |",
                    "| X002 | 编号重复 | 作者五 | 出版社五 | 2025-05-05 | 55.0 |",
                ]
            )
            + "\n",
            encoding="utf-8",
        )

        ok, message = import_books_from_markdown(input_path, self.db_path)
        self.assertTrue(ok, message)
        self.assertIn("成功导入 2 本图书", message)
        self.assertIn("跳过 3 行", message)

        overview = get_all_books_overview(self.db_path)
        self.assertEqual([row["book_no"] for row in overview], ["X001", "X002"])
        self.assertEqual(overview[0]["total_copies"], 3)
        self.assertEqual(overview[0]["available_copies"], 3)

        conn = sqlite3.connect(self.db_path)
        try:
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM book_copies").fetchone()[0], 6)
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM borrow_records").fetchone()[0], 0)
        finally:
            conn.close()

    def test_import_books_from_markdown_rejects_non_markdown_and_empty_valid_rows(self) -> None:
        text_path = Path(self.tmp_dir.name) / "books.txt"
        text_path.write_text("| X001 | 新书 | 作者 | 出版社 | 2025-01-01 | 10 |", encoding="utf-8")
        ok, message = import_books_from_markdown(text_path, self.db_path)
        self.assertFalse(ok)
        self.assertIn(".md", message)

        invalid_path = Path(self.tmp_dir.name) / "invalid.md"
        invalid_path.write_text(
            "| 图书编号 | 书名 | 作者 | 出版社 | 出版日期 | 价格 |\n"
            "|---|---|---|---|---|---|\n"
            "| X001 | 缺少价格 | 作者 | 出版社 | 2025-01-01 |\n",
            encoding="utf-8",
        )
        ok, message = import_books_from_markdown(invalid_path, self.db_path)
        self.assertFalse(ok)
        self.assertIn("未找到有效图书行", message)
        self.assertEqual(len(get_all_books_overview(self.db_path)), 20)


if __name__ == "__main__":
    unittest.main()
