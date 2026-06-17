"""Application entry point for the library management system."""

from database import init_db


def main() -> None:
    """Start the application."""
    db_path = init_db()
    print(f"数据库初始化完成：{db_path}")


if __name__ == "__main__":
    main()
