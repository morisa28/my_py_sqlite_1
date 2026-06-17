"""Administrator main window."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
from typing import Callable

from services.book_service import add_book, delete_book, get_all_books_overview, search_books, update_book
from services.user_service import get_user_borrow_status


BOOK_COLUMNS = [
    ("book_no", "图书编号", 90),
    ("title", "书名", 160),
    ("author", "作者", 100),
    ("publisher", "出版社", 130),
    ("publish_date", "出版日期", 100),
    ("price", "价格", 70),
    ("total_copies", "总副本数", 80),
    ("available_copies", "可借副本数", 90),
    ("borrowed_copies", "已借出副本数", 100),
    ("book_status", "图书状态", 80),
]

USER_BORROW_COLUMNS = [
    ("username", "用户账号", 90),
    ("name", "用户姓名", 90),
    ("book_no", "图书编号", 90),
    ("title", "书名", 150),
    ("copy_no", "副本编号", 80),
    ("borrow_date", "借书日期", 100),
    ("due_date", "应还日期", 100),
    ("return_date", "归还日期", 100),
    ("status", "借阅状态", 90),
    ("is_overdue", "是否超期", 80),
    ("overdue_days", "超期天数", 80),
]


class BookFormDialog(simpledialog.Dialog):
    """Modal form used for adding and updating books."""

    def __init__(
        self,
        parent: tk.Toplevel,
        title: str,
        fields: list[tuple[str, str]],
        initial_values: dict | None = None,
    ) -> None:
        self.fields = fields
        self.initial_values = initial_values or {}
        self.entries: dict[str, ttk.Entry] = {}
        self.result: dict | None = None
        super().__init__(parent, title)

    def body(self, master: tk.Widget) -> ttk.Entry | None:
        for row_index, (key, label) in enumerate(self.fields):
            ttk.Label(master, text=label).grid(row=row_index, column=0, sticky=tk.W, padx=8, pady=6)
            entry = ttk.Entry(master, width=34)
            entry.insert(0, self.initial_values.get(key, ""))
            entry.grid(row=row_index, column=1, sticky=tk.EW, padx=8, pady=6)
            self.entries[key] = entry
        master.columnconfigure(1, weight=1)
        return next(iter(self.entries.values()), None)

    def apply(self) -> None:
        self.result = {key: entry.get().strip() for key, entry in self.entries.items()}


class AdminWindow:
    """Main window for administrators."""

    def __init__(
        self,
        window: tk.Toplevel,
        user: dict,
        on_logout: Callable[[tk.Toplevel], None],
    ) -> None:
        self.window = window
        self.user = user
        self.on_logout = on_logout
        self.status_var = tk.StringVar(value=f"当前管理员：{user['name']}（{user['username']}）")
        self.table_frame: ttk.Frame | None = None
        self.tree: ttk.Treeview | None = None
        self._build()

    def _build(self) -> None:
        self.window.title("管理员 - 图书馆图书管理系统")
        self.window.geometry("1120x660")
        self.window.minsize(960, 560)
        self.window.protocol("WM_DELETE_WINDOW", self.logout)

        root = ttk.Frame(self.window, padding=12)
        root.pack(fill=tk.BOTH, expand=True)
        root.columnconfigure(1, weight=1)
        root.rowconfigure(0, weight=1)

        sidebar = ttk.Frame(root, width=180)
        sidebar.grid(row=0, column=0, sticky=tk.NS, padx=(0, 12))

        ttk.Label(sidebar, text="管理员", font=("Microsoft YaHei", 14, "bold")).pack(fill=tk.X, pady=(0, 12))
        ttk.Button(sidebar, text="录入图书", command=self.add_book_dialog).pack(fill=tk.X, pady=4)
        ttk.Button(sidebar, text="删除图书", command=self.delete_book_dialog).pack(fill=tk.X, pady=4)
        ttk.Button(sidebar, text="修改图书信息", command=self.update_book_dialog).pack(fill=tk.X, pady=4)
        ttk.Button(sidebar, text="查询图书", command=self.query_books).pack(fill=tk.X, pady=4)
        ttk.Button(sidebar, text="查询用户借阅状态", command=self.query_user_status).pack(fill=tk.X, pady=4)
        ttk.Button(sidebar, text="总览图书信息", command=self.show_overview).pack(fill=tk.X, pady=4)
        ttk.Button(sidebar, text="退出登录", command=self.logout).pack(fill=tk.X, pady=(24, 4))

        content = ttk.Frame(root)
        content.grid(row=0, column=1, sticky=tk.NSEW)
        content.rowconfigure(0, weight=1)
        content.columnconfigure(0, weight=1)

        self.table_frame = ttk.Frame(content)
        self.table_frame.grid(row=0, column=0, sticky=tk.NSEW)

        status = ttk.Label(content, textvariable=self.status_var, anchor=tk.W)
        status.grid(row=1, column=0, sticky=tk.EW, pady=(8, 0))

        self.show_overview()

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

    def add_book_dialog(self) -> None:
        dialog = BookFormDialog(
            self.window,
            "录入图书",
            [
                ("book_no", "图书编号"),
                ("title", "书名"),
                ("author", "作者"),
                ("publisher", "出版社"),
                ("publish_date", "出版日期 YYYY-MM-DD"),
                ("price", "价格"),
            ],
        )
        if dialog.result is None:
            return
        ok, message = add_book(**dialog.result)
        self._show_operation_result(ok, message)
        if ok:
            self.show_overview()

    def delete_book_dialog(self) -> None:
        book_no = simpledialog.askstring("删除图书", "请输入要删除的图书编号：", parent=self.window)
        if book_no is None:
            return
        ok, message = delete_book(book_no)
        self._show_operation_result(ok, message)
        if ok:
            self.show_overview()

    def update_book_dialog(self) -> None:
        book_no = simpledialog.askstring("修改图书", "请输入要修改的图书编号：", parent=self.window)
        if book_no is None:
            return
        exact = next((row for row in search_books(book_no) if row["book_no"] == book_no.strip()), None)
        if exact is None:
            messagebox.showwarning("修改图书", "图书不存在")
            return

        dialog = BookFormDialog(
            self.window,
            "修改图书信息",
            [
                ("author", "作者"),
                ("publisher", "出版社"),
                ("publish_date", "出版日期 YYYY-MM-DD"),
                ("price", "价格"),
            ],
            initial_values=exact,
        )
        if dialog.result is None:
            return
        ok, message = update_book(book_no, **dialog.result)
        self._show_operation_result(ok, message)
        if ok:
            self.show_overview()

    def query_books(self) -> None:
        keyword = simpledialog.askstring("查询图书", "请输入图书编号或书名关键字：", parent=self.window)
        if keyword is None:
            return
        rows = search_books(keyword)
        self._show_table(BOOK_COLUMNS, rows)
        self.status_var.set(f"查询到 {len(rows)} 条图书记录")
        if not rows:
            messagebox.showinfo("查询结果", "未查询到相关图书")

    def query_user_status(self) -> None:
        keyword = simpledialog.askstring("查询用户借阅状态", "请输入用户 ID、账号或姓名：", parent=self.window)
        if keyword is None:
            return
        rows = get_user_borrow_status(keyword)
        self._show_table(USER_BORROW_COLUMNS, rows)
        self.status_var.set(f"查询到 {len(rows)} 条用户借阅记录")
        if not rows:
            messagebox.showinfo("查询结果", "未查询到相关用户")

    def show_overview(self) -> None:
        rows = get_all_books_overview()
        self._show_table(BOOK_COLUMNS, rows)
        self.status_var.set(f"当前共有 {len(rows)} 本未删除图书")

    def _show_operation_result(self, ok: bool, message: str) -> None:
        if ok:
            messagebox.showinfo("操作成功", message)
        else:
            messagebox.showwarning("操作失败", message)
        self.status_var.set(message)

    def logout(self) -> None:
        self.on_logout(self.window)
