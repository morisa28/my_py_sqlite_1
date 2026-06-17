"""Application entry point for the library management system."""

import tkinter as tk
from tkinter import messagebox

from database import init_db
from ui.login_window import LoginWindow


def main() -> None:
    """Start the application."""
    try:
        init_db()
    except Exception as exc:
        messagebox.showerror("启动失败", f"数据库初始化失败：{exc}")
        return

    root = tk.Tk()
    LoginWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
