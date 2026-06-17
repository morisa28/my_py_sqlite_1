"""Database connection, schema creation, and seed data initialization."""

from __future__ import annotations

import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "library.db"

INITIAL_USERS = [
    ("admin", "admin123", "admin", "管理员"),
    ("user01", "123456", "user", "用户01"),
    ("user02", "123456", "user", "用户02"),
    ("user03", "123456", "user", "用户03"),
    ("user04", "123456", "user", "用户04"),
    ("user05", "123456", "user", "用户05"),
    ("user06", "123456", "user", "用户06"),
    ("user07", "123456", "user", "用户07"),
    ("user08", "123456", "user", "用户08"),
    ("user09", "123456", "user", "用户09"),
    ("user10", "123456", "user", "用户10"),
]

INITIAL_BOOKS = [
    ("B001", "Python程序设计", "张三", "清华大学出版社", "2021-01-10", 59.80),
    ("B002", "数据结构", "李四", "高等教育出版社", "2020-06-15", 45.50),
    ("B003", "操作系统", "王五", "机械工业出版社", "2019-09-01", 68.00),
    ("B004", "计算机网络", "赵六", "人民邮电出版社", "2022-03-18", 55.00),
    ("B005", "数据库系统概论", "萨师煊", "高等教育出版社", "2018-04-01", 49.90),
    ("B006", "软件工程", "郑人杰", "清华大学出版社", "2020-11-20", 52.00),
    ("B007", "Java程序设计", "刘强", "电子工业出版社", "2021-08-12", 62.50),
    ("B008", "C语言程序设计", "谭浩强", "清华大学出版社", "2017-05-01", 39.80),
    ("B009", "算法导论", "Thomas H. Cormen", "机械工业出版社", "2013-01-01", 128.00),
    ("B010", "人工智能基础", "陈明", "人民邮电出版社", "2022-10-09", 72.00),
    ("B011", "机器学习", "周志华", "清华大学出版社", "2016-01-01", 88.00),
    ("B012", "深度学习入门", "斋藤康毅", "人民邮电出版社", "2018-07-01", 59.00),
    ("B013", "Web前端开发", "何敏", "电子工业出版社", "2021-12-05", 58.00),
    ("B014", "Linux操作系统", "孙伟", "机械工业出版社", "2020-02-22", 66.00),
    ("B015", "计算机组成原理", "唐朔飞", "高等教育出版社", "2019-08-01", 48.00),
    ("B016", "离散数学", "屈婉玲", "高等教育出版社", "2018-09-10", 36.00),
    ("B017", "编译原理", "陈火旺", "国防工业出版社", "2017-03-01", 57.00),
    ("B018", "信息安全基础", "李华", "电子工业出版社", "2021-05-14", 64.00),
    ("B019", "大数据技术", "周强", "人民邮电出版社", "2022-06-30", 69.00),
    ("B020", "云计算基础", "林峰", "清华大学出版社", "2023-02-16", 61.00),
]


def get_connection(db_path: Path | str | None = None) -> sqlite3.Connection:
    """Return a SQLite connection configured for this application."""
    path = Path(db_path) if db_path is not None else DB_PATH
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def create_tables(conn: sqlite3.Connection) -> None:
    """Create all required database tables."""
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('admin', 'user')),
            name TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'normal'
        );

        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_no TEXT NOT NULL UNIQUE,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            publisher TEXT NOT NULL,
            publish_date TEXT NOT NULL,
            price REAL NOT NULL,
            is_deleted INTEGER NOT NULL DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS book_copies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER NOT NULL,
            copy_no INTEGER NOT NULL,
            status TEXT NOT NULL CHECK(status IN ('available', 'borrowed', 'deleted')),
            UNIQUE(book_id, copy_no),
            FOREIGN KEY (book_id) REFERENCES books(id)
        );

        CREATE TABLE IF NOT EXISTS borrow_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            copy_id INTEGER NOT NULL,
            borrow_date TEXT NOT NULL,
            due_date TEXT NOT NULL,
            return_date TEXT,
            status TEXT NOT NULL CHECK(status IN ('borrowed', 'returned')),
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (copy_id) REFERENCES book_copies(id)
        );
        """
    )


def seed_users(conn: sqlite3.Connection) -> None:
    """Insert default admin and normal users if they do not already exist."""
    conn.executemany(
        """
        INSERT OR IGNORE INTO users (username, password, role, name)
        VALUES (?, ?, ?, ?)
        """,
        INITIAL_USERS,
    )


def seed_books(conn: sqlite3.Connection) -> None:
    """Insert default books and ensure every book has three copy records."""
    conn.executemany(
        """
        INSERT OR IGNORE INTO books
            (book_no, title, author, publisher, publish_date, price)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        INITIAL_BOOKS,
    )

    for book_no, *_ in INITIAL_BOOKS:
        book = conn.execute(
            "SELECT id FROM books WHERE book_no = ?",
            (book_no,),
        ).fetchone()
        if book is None:
            continue
        conn.executemany(
            """
            INSERT OR IGNORE INTO book_copies (book_id, copy_no, status)
            VALUES (?, ?, 'available')
            """,
            [(book["id"], copy_no) for copy_no in range(1, 4)],
        )


def seed_data(conn: sqlite3.Connection) -> None:
    """Seed all initial data."""
    seed_users(conn)
    seed_books(conn)


def init_db(db_path: Path | str | None = None) -> Path:
    """Create schema and seed data, then return the database path."""
    path = Path(db_path) if db_path is not None else DB_PATH
    with get_connection(path) as conn:
        create_tables(conn)
        seed_data(conn)
    return path
