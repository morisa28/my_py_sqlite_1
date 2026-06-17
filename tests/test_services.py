"""Service-layer tests using a temporary SQLite database."""

from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from auth import login
from database import init_db
from services.book_service import add_book, delete_book, get_all_books_overview, search_books, update_book
from services.borrow_service import borrow_book, get_user_current_borrows, return_book
from services.user_service import get_user_borrow_status


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


if __name__ == "__main__":
    unittest.main()
