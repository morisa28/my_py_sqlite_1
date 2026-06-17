"""Normal user main window."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
from typing import Callable

from services.book_service import search_books
from services.borrow_service import borrow_book, get_user_current_borrows, return_book


BOOK_COLUMNS = [
    ("book_no", "图书编号", 90),
    ("title", "书名", 160),
    ("author", "作者", 100),
    ("publisher", "出版社", 130),
    ("publish_date", "出版日期", 100),
    ("price", "价格", 70),
    ("total_copies", "总副本数", 80),
    ("available_copies", "可借副本数", 90),
    ("book_status", "图书状态", 80),
]

BORROW_COLUMNS = [
    ("record_id", "记录编号", 80),
    ("book_no", "图书编号", 90),
    ("title", "书名", 160),
    ("copy_no", "副本编号", 80),
    ("borrow_date", "借书日期", 100),
    ("due_date", "应还日期", 100),
    ("is_overdue", "是否超期", 80),
    ("overdue_days", "超期天数", 80),
]


class UserWindow:
    """Main window for normal users."""

    def __init__(
        self,
        window: tk.Toplevel,
        user: dict,
        on_logout: Callable[[tk.Toplevel], None],
    ) -> None:
        self.window = window
        self.user = user
        self.on_logout = on_logout
        self.status_var = tk.StringVar(value=f"当前用户：{user['name']}（{user['username']}）")
        self.table_frame: ttk.Frame | None = None
        self.tree: ttk.Treeview | None = None
        self._build()

    def _build(self) -> None:
        self.window.title("普通用户 - 图书馆图书管理系统")
        self.window.geometry("980x620")
        self.window.minsize(880, 540)
        self.window.protocol("WM_DELETE_WINDOW", self.logout)

        root = ttk.Frame(self.window, padding=12)
        root.pack(fill=tk.BOTH, expand=True)
        root.columnconfigure(1, weight=1)
        root.rowconfigure(0, weight=1)

        sidebar = ttk.Frame(root, width=160)
        sidebar.grid(row=0, column=0, sticky=tk.NS, padx=(0, 12))

        ttk.Label(sidebar, text="普通用户", font=("Microsoft YaHei", 14, "bold")).pack(fill=tk.X, pady=(0, 12))
        ttk.Button(sidebar, text="查询图书", command=self.query_books).pack(fill=tk.X, pady=4)
        ttk.Button(sidebar, text="借书", command=self.borrow).pack(fill=tk.X, pady=4)
        ttk.Button(sidebar, text="还书", command=self.return_selected_book).pack(fill=tk.X, pady=4)
        ttk.Button(sidebar, text="我的借阅", command=self.show_my_borrows).pack(fill=tk.X, pady=4)
        ttk.Button(sidebar, text="退出登录", command=self.logout).pack(fill=tk.X, pady=(24, 4))

        content = ttk.Frame(root)
        content.grid(row=0, column=1, sticky=tk.NSEW)
        content.rowconfigure(0, weight=1)
        content.columnconfigure(0, weight=1)

        self.table_frame = ttk.Frame(content)
        self.table_frame.grid(row=0, column=0, sticky=tk.NSEW)

        status = ttk.Label(content, textvariable=self.status_var, anchor=tk.W)
        status.grid(row=1, column=0, sticky=tk.EW, pady=(8, 0))

        self.query_books(default=True)

    def _show_table(self, columns: list[tuple[str, str, int]], rows: list[dict]) -> None:
        assert self.table_frame is not None
        for child in self.table_frame.winfo_children():
            child.destroy()

        keys = [column[0] for column in columns]
        tree = ttk.Treeview(self.table_frame, columns=keys, show="headings")
        vertical = ttk.Scrollbar(self.table_frame, orient=tk.VERTICAL, command=tree.yview)
        horizontal = ttk.Scrollbar(self.table_frame, orient=tk.HORIZONTAL, command=tree.xview)
        tree.configure(yscrollcommand=vertical.set, xscrollcommand=horizontal.set)

        tree.grid(row=0, column=0, sticky=tk.NSEW)
        vertical.grid(row=0, column=1, sticky=tk.NS)
        horizontal.grid(row=1, column=0, sticky=tk.EW)
        self.table_frame.rowconfigure(0, weight=1)
        self.table_frame.columnconfigure(0, weight=1)

        for key, title, width in columns:
            tree.heading(key, text=title)
            tree.column(key, width=width, minwidth=60, anchor=tk.CENTER)

        for row in rows:
            values = [row.get(key, "") for key in keys]
            tree.insert("", tk.END, values=values)

        self.tree = tree

    def query_books(self, default: bool = False) -> None:
        keyword = "" if default else simpledialog.askstring("查询图书", "请输入图书编号或书名关键字：", parent=self.window)
        if keyword is None:
            return
        rows = search_books(keyword)
        self._show_table(BOOK_COLUMNS, rows)
        self.status_var.set(f"查询到 {len(rows)} 条图书记录")
        if not rows and not default:
            messagebox.showinfo("查询结果", "未查询到相关图书")

    def borrow(self) -> None:
        book_no = simpledialog.askstring("借书", "请输入要借阅的图书编号：", parent=self.window)
        if book_no is None:
            return
        ok, message = borrow_book(self.user["id"], book_no)
        if ok:
            messagebox.showinfo("借书成功", message)
            self.show_my_borrows()
        else:
            messagebox.showwarning("借书失败", message)
        self.status_var.set(message)

    def return_selected_book(self) -> None:
        rows = get_user_current_borrows(self.user["id"])
        self._show_table(BORROW_COLUMNS, rows)
        if not rows:
            messagebox.showinfo("还书", "当前没有未归还图书")
            self.status_var.set("当前没有未归还图书")
            return

        record_id = simpledialog.askinteger("还书", "请输入要归还的借阅记录编号：", parent=self.window)
        if record_id is None:
            return
        ok, message = return_book(self.user["id"], record_id)
        if ok:
            messagebox.showinfo("还书成功", message)
            self.show_my_borrows()
        else:
            messagebox.showwarning("还书失败", message)
        self.status_var.set(message)

    def show_my_borrows(self) -> None:
        rows = get_user_current_borrows(self.user["id"])
        self._show_table(BORROW_COLUMNS, rows)
        self.status_var.set(f"当前未归还图书 {len(rows)} 本")
        if not rows:
            messagebox.showinfo("我的借阅", "当前没有未归还图书")

    def logout(self) -> None:
        self.on_logout(self.window)
