# 图书馆图书管理系统

## 项目简介

本项目是一个基于 Python、SQLite 和 Tkinter 的图书馆图书管理系统，包含管理员和普通用户两个角色。系统支持图书查询、借书、还书、管理员图书管理、用户借阅状态查询等功能。

## 技术栈

- Python 3
- SQLite
- sqlite3
- Tkinter
- ttk.Treeview
- unittest

## 项目结构

```text
library_system/
├── main.py
├── database.py
├── auth.py
├── services/
│   ├── __init__.py
│   ├── book_service.py
│   ├── borrow_service.py
│   └── user_service.py
├── ui/
│   ├── __init__.py
│   ├── login_window.py
│   ├── user_window.py
│   └── admin_window.py
├── tests/
│   └── test_services.py
├── docs/
├── library.db
└── README.md
```

## 运行方法

在项目目录下执行：

```bash
python main.py
```

如果使用 Linux 或 WSL 环境，需要确保 Python 安装了 Tkinter 支持。例如 Ubuntu / Debian 可安装：

```bash
sudo apt install python3-tk
```

当前项目目录位于 Windows 共享路径时，推荐使用 Windows Python 运行：

```powershell
cd F:\file\wsl_shared_files\study\py_sql_1\.worktrees\library-system
python main.py
```

## 测试账号

管理员账号：

```text
账号：admin
密码：admin123
```

普通用户账号：

```text
账号：user01
密码：123456
```

其他普通用户账号为 `user02` 到 `user10`，密码均为 `123456`。

## 主要功能

普通用户：

- 注册普通用户账号。
- 查询图书信息和可借状态。
- 借阅图书。
- 归还图书。
- 查看自己当前未归还图书。
- 查看借书日期、应还日期、是否超期和超期天数。

管理员：

- 录入图书，并自动生成 3 个副本。
- 删除没有借出副本的图书。
- 修改图书作者、出版社、出版日期和价格。
- 查询图书信息和图书状态。
- 查询任意用户借阅状态。
- 总览所有未删除图书的信息和副本状态。

## 数据库说明

系统首次运行会自动创建 `library.db`，包含以下表：

- `users`：用户和管理员账号。
- `books`：图书基本信息。
- `book_copies`：图书副本状态。
- `borrow_records`：借阅记录。

初始化数据包括：

- 1 个管理员账号。
- 10 个普通用户账号。
- 20 本图书。
- 每本图书 3 个副本，共 60 个副本。

## 业务规则

- 每个用户最多同时借阅 2 本书。
- 用户有超期未还图书时，不能借新书。
- 每本书默认有 3 个副本。
- 图书没有可借副本时不能借出。
- 管理员删除图书时，如果仍有副本借出则禁止删除。
- 管理员修改图书信息时，书名不允许修改。

## 界面操作

- 登录页点击“注册”可以注册普通用户账号。
- 图书表格默认按“图书编号”升序显示。
- 点击表格上方的列标题可以按该列升序排序，再次点击同一列会切换为降序。
- 左侧“查看全部”按钮可恢复显示所有图书。
- 在图书表格中右键某一行可执行当前可用操作：
  - 普通用户可直接借阅有可借副本的图书。
  - 普通用户在“我的借阅”表格中可右键归还当前图书。
  - 管理员可右键修改图书信息；没有借出副本的图书还可以右键删除。

## 运行测试

服务层测试使用临时数据库，不会修改正式 `library.db`：

```bash
python -m unittest
```

## 注意事项

- 如果在 WSL 中运行提示 `No module named 'tkinter'`，需要安装 `python3-tk` 或改用 Windows Python。
- `library.db` 可删除后重新运行 `python main.py` 自动生成。
- 项目使用明文测试密码，符合课程演示要求，不适合作为生产系统认证方案。
