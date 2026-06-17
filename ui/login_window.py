"""Login window for the library management system."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from auth import login
from ui.admin_window import AdminWindow
from ui.user_window import UserWindow


class LoginWindow:
    """Login screen that routes users to role-specific windows."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self._build()

    def _build(self) -> None:
        self.root.title("图书馆图书管理系统")
        self.root.geometry("420x280")
        self.root.resizable(False, False)

        outer = ttk.Frame(self.root, padding=28)
        outer.pack(fill=tk.BOTH, expand=True)

        title = ttk.Label(outer, text="图书馆图书管理系统", font=("Microsoft YaHei", 18, "bold"))
        title.pack(pady=(0, 24))

        form = ttk.Frame(outer)
        form.pack(fill=tk.X)

        ttk.Label(form, text="账号").grid(row=0, column=0, sticky=tk.W, pady=8)
        username_entry = ttk.Entry(form, textvariable=self.username_var)
        username_entry.grid(row=0, column=1, sticky=tk.EW, pady=8)

        ttk.Label(form, text="密码").grid(row=1, column=0, sticky=tk.W, pady=8)
        password_entry = ttk.Entry(form, textvariable=self.password_var, show="*")
        password_entry.grid(row=1, column=1, sticky=tk.EW, pady=8)
        form.columnconfigure(1, weight=1)

        buttons = ttk.Frame(outer)
        buttons.pack(fill=tk.X, pady=(24, 0))
        ttk.Button(buttons, text="登录", command=self._handle_login).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 8))
        ttk.Button(buttons, text="退出", command=self.root.destroy).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(8, 0))

        self.root.bind("<Return>", lambda _event: self._handle_login())
        username_entry.focus_set()

    def _handle_login(self) -> None:
        user = login(self.username_var.get(), self.password_var.get())
        if user is None:
            messagebox.showerror("登录失败", "账号或密码错误")
            return

        self.root.withdraw()
        window = tk.Toplevel(self.root)
        if user["role"] == "admin":
            AdminWindow(window, user, self._restore_login)
        else:
            UserWindow(window, user, self._restore_login)

    def _restore_login(self, window: tk.Toplevel) -> None:
        window.destroy()
        self.password_var.set("")
        self.root.deiconify()
        self.root.lift()
