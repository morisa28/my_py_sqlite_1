# 基于 Python 的图书馆图书管理系统项目开发指导文档（Codex 使用版）

## 1. 项目目标

请基于 Python 开发一个图形化的图书馆图书管理系统，实现普通用户和管理员两个角色的图书管理、借阅管理、查询管理等功能。

系统必须使用 SQLite 数据库存储数据，使用 Tkinter 或 PyQt 等 Python 图形界面库实现图形化用户界面。推荐优先使用 Tkinter，因为它属于 Python 标准库，便于运行、演示和提交。

本项目应适合作为课程设计或大作业提交，最终应包含完整源码、数据库初始化逻辑、图形界面、测试数据和项目说明。

---

## 2. 硬性需求

开发时必须满足以下要求：

1. 使用 Python 语言实现。
2. 使用 SQLite 数据库存储数据。
3. 使用 Tkinter 或 PyQt 实现图形化界面，推荐 Tkinter。
4. 系统中必须包含两个角色：
   - 管理员
   - 普通用户
5. 图书数量不少于 20 本。
6. 用户数量不少于 10 个。
7. 每本图书有 3 个副本可供借阅。
8. 每个用户最多同时借阅 2 本书。
9. 用户存在超期未还图书时，不能借新书。
10. 图书信息必须包括：
    - 编号
    - 书名
    - 作者
    - 出版社
    - 出版日期
    - 价格
11. 管理员修改图书信息时，书名不允许修改，其余字段可以修改。
12. 系统界面必须提供清晰提示，用户根据界面按钮或输入完成操作。

---

## 3. 推荐技术栈

| 类型 | 技术 |
|---|---|
| 编程语言 | Python 3 |
| 数据库 | SQLite |
| 数据库模块 | sqlite3 |
| 图形界面 | Tkinter |
| 日期处理 | datetime |
| 表格展示 | ttk.Treeview |
| 消息提示 | tkinter.messagebox |

---

## 4. 系统角色与功能划分

### 4.1 普通用户功能

普通用户登录后应具有以下功能：

1. 查询图书信息。
2. 查询图书状态。
3. 借书。
4. 还书。
5. 查询自己当前已借图书。
6. 查询自己借阅图书的状态，包括：
   - 借书日期
   - 应还日期
   - 是否超期
   - 已超期天数
7. 有超期未还图书时，禁止借新书。
8. 当前已借图书数量达到 2 本时，禁止继续借书。

### 4.2 管理员功能

管理员登录后应具有以下功能：

1. 录入图书。
2. 删除图书。
3. 修改图书信息。
4. 查询某本图书的信息和状态。
5. 查询任意用户的借书状态。
6. 总览图书馆所有图书的信息和状态。
7. 查看图书副本可借数量、借出数量和整体状态。

---

## 5. 业务规则设计

### 5.1 图书副本规则

每本图书默认有 3 个副本。录入一本新书时，需要自动生成 3 条副本记录。

示例：

```text
图书：《Python 程序设计》
副本 1：available
副本 2：available
副本 3：available
```

### 5.2 图书状态规则

图书状态根据可借副本数量判断：

```text
可借副本数 > 0：在库
可借副本数 = 0：不在库
```

管理员界面应显示更加详细的状态，包括：

```text
总副本数
可借副本数
已借出副本数
每个副本状态
借出用户
借书日期
应还日期
是否超期
```

### 5.3 借书规则

用户借书前必须依次检查：

1. 用户是否存在超期未还图书。
2. 用户当前已借图书数量是否已经达到 2 本。
3. 目标图书是否存在。
4. 目标图书是否还有可借副本。

只有以上条件全部通过，才允许借书。

借书成功后需要：

1. 将某一个可借副本状态改为 `borrowed`。
2. 在借阅记录表中插入一条新记录。
3. 设置借书日期为当前日期。
4. 设置应还日期为当前日期后 30 天。
5. 弹窗提示借书成功。

### 5.4 还书规则

用户还书时需要：

1. 查询当前用户未归还的借阅记录。
2. 用户选择一本要归还的图书。
3. 将借阅记录状态改为 `returned`。
4. 填写实际归还日期。
5. 将对应副本状态改回 `available`。
6. 弹窗提示还书成功。

### 5.5 超期规则

默认借阅期限为 30 天。

判断规则：

```text
当前日期 > 应还日期 且 return_date 为空，则该记录为超期。
```

已超期天数：

```text
已超期天数 = 当前日期 - 应还日期
```

---

## 6. 推荐项目目录结构

建议按模块拆分项目，便于维护和调试。

```text
library_system/
│
├── main.py                  # 程序入口
├── database.py              # 数据库连接、建表、初始化测试数据
├── auth.py                  # 登录验证与角色判断
│
├── services/
│   ├── __init__.py
│   ├── book_service.py      # 图书查询、录入、删除、修改
│   ├── borrow_service.py    # 借书、还书、超期判断
│   └── user_service.py      # 用户查询、用户借阅状态查询
│
├── ui/
│   ├── __init__.py
│   ├── login_window.py      # 登录窗口
│   ├── user_window.py       # 普通用户窗口
│   └── admin_window.py      # 管理员窗口
│
├── library.db               # SQLite 数据库文件，运行后自动生成
└── README.md                # 项目说明文档
```

如果为了课程提交方便，也可以简化为：

```text
library_system/
│
├── main.py
├── database.py
├── services.py
├── gui.py
├── library.db
└── README.md
```

推荐优先使用第一种结构。若实现时间较短，可以使用第二种简化结构。

---

## 7. 数据库设计

### 7.1 用户表：users

用于保存管理员和普通用户账号信息。

```sql
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('admin', 'user')),
    name TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'normal'
);
```

字段说明：

| 字段 | 说明 |
|---|---|
| id | 用户 ID |
| username | 登录账号 |
| password | 登录密码 |
| role | 角色，admin 或 user |
| name | 用户姓名 |
| status | 用户状态 |

---

### 7.2 图书表：books

用于保存图书基本信息。

```sql
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
```

字段说明：

| 字段 | 说明 |
|---|---|
| id | 图书 ID |
| book_no | 图书编号 |
| title | 书名 |
| author | 作者 |
| publisher | 出版社 |
| publish_date | 出版日期 |
| price | 价格 |
| is_deleted | 是否逻辑删除 |

注意：

```text
title 书名字段不能在修改图书功能中被修改。
```

---

### 7.3 图书副本表：book_copies

用于保存每一本图书的副本状态。

```sql
CREATE TABLE IF NOT EXISTS book_copies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER NOT NULL,
    copy_no INTEGER NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('available', 'borrowed', 'deleted')),
    FOREIGN KEY (book_id) REFERENCES books(id)
);
```

字段说明：

| 字段 | 说明 |
|---|---|
| id | 副本 ID |
| book_id | 所属图书 ID |
| copy_no | 副本编号，1、2、3 |
| status | 副本状态 |

---

### 7.4 借阅记录表：borrow_records

用于保存借书和还书记录。

```sql
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
```

字段说明：

| 字段 | 说明 |
|---|---|
| id | 借阅记录 ID |
| user_id | 借书用户 ID |
| copy_id | 图书副本 ID |
| borrow_date | 借书日期 |
| due_date | 应还日期 |
| return_date | 实际归还日期 |
| status | borrowed 或 returned |

---

## 8. 初始化数据要求

系统首次运行时应自动初始化基础数据。

### 8.1 初始化管理员

至少提供一个管理员账号：

```text
账号：admin
密码：admin123
角色：admin
```

### 8.2 初始化普通用户

至少初始化 10 个普通用户，例如：

```text
user01 / 123456
user02 / 123456
user03 / 123456
user04 / 123456
user05 / 123456
user06 / 123456
user07 / 123456
user08 / 123456
user09 / 123456
user10 / 123456
```

### 8.3 初始化图书

至少初始化 20 本图书，每本图书自动生成 3 个副本。

图书示例：

```text
B001 Python程序设计
B002 数据结构
B003 操作系统
B004 计算机网络
B005 数据库系统概论
B006 软件工程
B007 Java程序设计
B008 C语言程序设计
B009 算法导论
B010 人工智能基础
B011 机器学习
B012 深度学习入门
B013 Web前端开发
B014 Linux操作系统
B015 计算机组成原理
B016 离散数学
B017 编译原理
B018 信息安全基础
B019 大数据技术
B020 云计算基础
```

---

## 9. 核心服务函数设计

请优先实现业务逻辑函数，再实现图形界面。

### 9.1 登录验证函数

建议函数：

```python
def login(username: str, password: str) -> dict | None:
    """
    根据账号和密码查询用户。
    登录成功返回用户信息字典。
    登录失败返回 None。
    """
```

返回数据示例：

```python
{
    "id": 1,
    "username": "admin",
    "role": "admin",
    "name": "管理员"
}
```

---

### 9.2 图书查询函数

建议函数：

```python
def search_books(keyword: str) -> list[dict]:
    """
    根据图书编号或书名模糊查询图书。
    返回图书基本信息和副本状态。
    """
```

返回内容应包含：

```text
图书编号
书名
作者
出版社
出版日期
价格
总副本数
可借副本数
已借出副本数
图书状态
```

---

### 9.3 借书函数

建议函数：

```python
def borrow_book(user_id: int, book_no: str) -> tuple[bool, str]:
    """
    用户借书。
    返回操作结果和提示信息。
    """
```

该函数内部必须检查：

1. 是否有超期未还图书。
2. 当前是否已经借满 2 本。
3. 图书是否存在。
4. 是否有可借副本。

成功后：

1. 更新副本状态。
2. 插入借阅记录。
3. 返回成功提示。

---

### 9.4 还书函数

建议函数：

```python
def return_book(user_id: int, record_id: int) -> tuple[bool, str]:
    """
    用户归还图书。
    返回操作结果和提示信息。
    """
```

成功后：

1. 更新借阅记录。
2. 更新副本状态。
3. 返回成功提示。

---

### 9.5 查询用户当前借阅函数

建议函数：

```python
def get_user_current_borrows(user_id: int) -> list[dict]:
    """
    查询用户当前未归还图书。
    """
```

返回内容应包含：

```text
借阅记录编号
图书编号
书名
副本编号
借书日期
应还日期
是否超期
已超期天数
```

---

### 9.6 管理员录入图书函数

建议函数：

```python
def add_book(book_no: str, title: str, author: str, publisher: str, publish_date: str, price: float) -> tuple[bool, str]:
    """
    管理员录入图书。
    录入成功后自动生成 3 个副本。
    """
```

注意：

1. 图书编号不能重复。
2. 价格必须为数字。
3. 出版日期建议使用 `YYYY-MM-DD` 格式。
4. 成功录入图书后必须自动创建 3 条副本记录。

---

### 9.7 管理员删除图书函数

建议函数：

```python
def delete_book(book_no: str) -> tuple[bool, str]:
    """
    管理员删除图书。
    建议使用逻辑删除。
    """
```

删除规则：

1. 如果图书不存在，提示不存在。
2. 如果图书有副本正在借出，不允许删除。
3. 如果图书没有借出副本，将 books.is_deleted 设置为 1。
4. 同时将该书副本状态设置为 `deleted`。

---

### 9.8 管理员修改图书函数

建议函数：

```python
def update_book(book_no: str, author: str, publisher: str, publish_date: str, price: float) -> tuple[bool, str]:
    """
    管理员修改图书信息。
    书名不允许修改。
    """
```

注意：

```text
不能提供修改 title 的入口。
```

---

### 9.9 管理员查询任意用户借阅状态函数

建议函数：

```python
def get_user_borrow_status(keyword: str) -> list[dict]:
    """
    管理员根据用户编号、账号或姓名查询用户借阅状态。
    """
```

返回内容应包含：

```text
用户账号
用户姓名
图书编号
书名
副本编号
借书日期
应还日期
归还日期
借阅状态
是否超期
已超期天数
```

---

### 9.10 管理员总览图书函数

建议函数：

```python
def get_all_books_overview() -> list[dict]:
    """
    管理员总览所有未删除图书的信息和状态。
    """
```

返回内容应包含：

```text
图书编号
书名
作者
出版社
出版日期
价格
总副本数
可借副本数
已借出副本数
图书状态
```

---

## 10. 图形界面设计要求

### 10.1 登录窗口

登录窗口包含：

```text
系统标题：图书馆图书管理系统
账号输入框
密码输入框
登录按钮
退出按钮
```

登录后：

1. 如果是管理员，打开管理员主界面。
2. 如果是普通用户，打开用户主界面。
3. 登录失败时弹出错误提示。

---

### 10.2 普通用户主界面

用户主界面包含以下功能按钮：

```text
查询图书
借书
还书
我的借阅
退出登录
```

建议布局：

```text
左侧：功能按钮区
右侧：结果展示区
底部：提示信息区
```

普通用户查询图书时，使用表格显示：

```text
图书编号
书名
作者
出版社
出版日期
价格
总副本数
可借副本数
图书状态
```

---

### 10.3 管理员主界面

管理员主界面包含以下功能按钮：

```text
录入图书
删除图书
修改图书信息
查询图书
查询用户借阅状态
总览图书信息
退出登录
```

管理员总览图书时，使用表格显示：

```text
图书编号
书名
作者
出版社
出版日期
价格
总副本数
可借副本数
已借出副本数
图书状态
```

管理员查询用户借阅状态时，使用表格显示：

```text
用户账号
用户姓名
图书编号
书名
副本编号
借书日期
应还日期
归还日期
借阅状态
是否超期
已超期天数
```

---

## 11. 推荐开发顺序

请严格按以下顺序开发，避免先做界面导致后期逻辑混乱。

### 第 1 步：搭建项目结构

创建项目目录和基础文件：

```text
main.py
database.py
auth.py
services/
ui/
README.md
```

### 第 2 步：实现数据库初始化

在 `database.py` 中实现：

1. 连接 SQLite 数据库。
2. 创建 4 张核心表。
3. 插入管理员账号。
4. 插入 10 个普通用户。
5. 插入 20 本图书。
6. 每本图书生成 3 个副本。
7. 避免重复插入初始化数据。

### 第 3 步：实现登录模块

在 `auth.py` 中实现：

1. 用户名密码验证。
2. 角色判断。
3. 返回用户信息。

### 第 4 步：实现图书查询模块

在 `book_service.py` 中实现：

1. 根据编号查询。
2. 根据书名查询。
3. 统计总副本数。
4. 统计可借副本数。
5. 生成图书状态。

### 第 5 步：实现借书和还书模块

在 `borrow_service.py` 中实现：

1. 超期检查。
2. 借阅数量检查。
3. 可借副本检查。
4. 借书。
5. 还书。
6. 查询当前借阅。
7. 计算超期天数。

### 第 6 步：实现管理员图书管理模块

在 `book_service.py` 中继续实现：

1. 录入图书。
2. 删除图书。
3. 修改图书。
4. 总览图书。

### 第 7 步：实现管理员用户借阅查询模块

在 `user_service.py` 中实现：

1. 根据账号、姓名或用户 ID 查询用户。
2. 查询该用户当前借阅。
3. 查询该用户历史借阅。
4. 显示是否超期。

### 第 8 步：实现图形界面

在 `ui/` 目录中实现：

1. 登录窗口。
2. 用户主界面。
3. 管理员主界面。
4. 表格展示组件。
5. 弹窗提示。
6. 输入校验。

### 第 9 步：联调与测试

完成所有功能后，测试：

1. 管理员登录。
2. 用户登录。
3. 用户查询图书。
4. 用户借书。
5. 用户还书。
6. 用户借满 2 本后继续借书。
7. 用户有超期未还图书时借书。
8. 图书 3 个副本全部借出后的状态。
9. 管理员录入图书。
10. 管理员删除图书。
11. 管理员修改图书。
12. 管理员查询用户借阅状态。
13. 管理员总览图书。

---

## 12. 关键 SQL 查询参考

### 12.1 查询图书状态

```sql
SELECT
    b.id,
    b.book_no,
    b.title,
    b.author,
    b.publisher,
    b.publish_date,
    b.price,
    COUNT(c.id) AS total_copies,
    SUM(CASE WHEN c.status = 'available' THEN 1 ELSE 0 END) AS available_copies,
    SUM(CASE WHEN c.status = 'borrowed' THEN 1 ELSE 0 END) AS borrowed_copies
FROM books b
LEFT JOIN book_copies c ON b.id = c.book_id
WHERE b.is_deleted = 0
GROUP BY b.id;
```

### 12.2 查询用户当前借阅数量

```sql
SELECT COUNT(*)
FROM borrow_records
WHERE user_id = ?
  AND status = 'borrowed';
```

### 12.3 查询用户是否存在超期未还图书

```sql
SELECT COUNT(*)
FROM borrow_records
WHERE user_id = ?
  AND status = 'borrowed'
  AND due_date < date('now');
```

### 12.4 查询某本书的可借副本

```sql
SELECT c.id
FROM book_copies c
JOIN books b ON c.book_id = b.id
WHERE b.book_no = ?
  AND b.is_deleted = 0
  AND c.status = 'available'
LIMIT 1;
```

### 12.5 查询用户当前未还图书

```sql
SELECT
    r.id AS record_id,
    b.book_no,
    b.title,
    c.copy_no,
    r.borrow_date,
    r.due_date,
    r.return_date,
    r.status
FROM borrow_records r
JOIN book_copies c ON r.copy_id = c.id
JOIN books b ON c.book_id = b.id
WHERE r.user_id = ?
  AND r.status = 'borrowed';
```

---

## 13. 界面实现建议

### 13.1 表格展示

使用 `ttk.Treeview` 展示查询结果。

表格建议封装成通用方法：

```python
def show_table(parent, columns, rows):
    """
    在指定父容器中显示表格。
    columns 为列名列表。
    rows 为数据列表。
    """
```

### 13.2 输入弹窗

可以使用：

```python
tkinter.simpledialog
```

也可以自定义 `Toplevel` 窗口，用于录入图书、修改图书、借书、还书等操作。

### 13.3 消息提示

使用：

```python
messagebox.showinfo()
messagebox.showwarning()
messagebox.showerror()
```

### 13.4 界面风格

要求：

1. 界面标题清楚。
2. 按钮功能明确。
3. 表格列名清晰。
4. 操作成功或失败都必须弹窗提示。
5. 查询无结果时给出提示。
6. 输入为空或格式错误时给出提示。

---

## 14. 异常处理要求

代码中必须处理以下异常情况：

1. 登录账号不存在。
2. 密码错误。
3. 图书编号重复。
4. 查询图书不存在。
5. 借书时无可借副本。
6. 用户已借满 2 本。
7. 用户存在超期未还图书。
8. 还书记录不存在。
9. 删除不存在的图书。
10. 删除仍有副本借出的图书。
11. 修改图书时输入价格不是数字。
12. 数据库操作失败。

---

## 15. 测试用例设计

### 15.1 登录测试

| 测试内容 | 输入 | 预期结果 |
|---|---|---|
| 管理员登录 | admin / admin123 | 进入管理员界面 |
| 用户登录 | user01 / 123456 | 进入用户界面 |
| 错误密码 | user01 / wrong | 提示账号或密码错误 |
| 不存在账号 | test / 123456 | 提示账号或密码错误 |

### 15.2 借书测试

| 测试内容 | 操作 | 预期结果 |
|---|---|---|
| 正常借书 | user01 借 B001 | 借书成功 |
| 借满 2 本 | user01 已借 2 本后继续借书 | 禁止借书 |
| 无可借副本 | 同一本书 3 个副本都借出后再借 | 提示暂无可借副本 |
| 超期限制 | 用户有超期未还图书时借书 | 禁止借书 |

### 15.3 还书测试

| 测试内容 | 操作 | 预期结果 |
|---|---|---|
| 正常还书 | user01 归还一本已借图书 | 还书成功 |
| 重复还书 | 归还已归还的记录 | 提示无效记录 |
| 还书后再借 | 归还后再借新书 | 借书成功 |

### 15.4 管理员测试

| 测试内容 | 操作 | 预期结果 |
|---|---|---|
| 录入图书 | 新增 B021 | 录入成功并生成 3 个副本 |
| 重复编号 | 新增已有编号 B001 | 提示编号重复 |
| 修改图书 | 修改 B001 作者、出版社、日期、价格 | 修改成功 |
| 删除无借出图书 | 删除没有借出的图书 | 删除成功 |
| 删除借出中图书 | 删除仍有副本借出的图书 | 禁止删除 |
| 总览图书 | 点击总览 | 显示所有未删除图书 |

---

## 16. 最终验收标准

项目完成后必须达到以下标准：

1. 运行 `main.py` 可以启动系统。
2. 首次运行会自动创建 SQLite 数据库。
3. 数据库中至少有 1 个管理员、10 个普通用户、20 本图书。
4. 每本图书都有 3 个副本。
5. 普通用户可以正常查询、借书、还书、查看自己的借阅状态。
6. 管理员可以录入、删除、修改、查询、总览图书。
7. 管理员可以查询任意用户的借阅状态。
8. 借书数量限制、超期限制、副本数量限制都能正确生效。
9. 图形界面操作提示清晰。
10. 所有主要功能都有异常提示。
11. 代码结构清晰，文件命名合理。
12. README 中说明运行方法和测试账号。

---

## 17. README 编写要求

最终请生成 `README.md`，内容包括：

```text
项目名称
项目简介
技术栈
项目结构
运行方法
测试账号
主要功能
数据库说明
注意事项
```

测试账号必须写明：

```text
管理员账号：admin
管理员密码：admin123

普通用户账号：user01
普通用户密码：123456
```

---

## 18. Codex 开发执行要求

请 Codex 按以下方式实现项目：

1. 不要只生成框架，必须实现可运行完整项目。
2. 优先保证功能正确，再考虑界面美观。
3. 不要跳过 SQLite 数据库初始化。
4. 不要把数据只保存在内存中。
5. 不要省略普通用户和管理员两个角色。
6. 不要省略图书副本表。
7. 不要把“一本书 3 个副本”简单写成一个库存数字，推荐用副本表实现。
8. 不要让用户超过 2 本借阅限制。
9. 不要允许有超期未还图书的用户继续借书。
10. 管理员修改图书信息时，不要允许修改书名。
11. 所有按钮都应有明确操作反馈。
12. 所有数据库写操作应使用事务提交。
13. 界面中表格查询结果应支持刷新。
14. 代码中应添加必要注释。
15. 完成后请说明如何运行和测试。

---

## 19. 推荐实现优先级

如时间有限，按以下优先级实现：

### 优先级 P0：必须完成

1. SQLite 数据库。
2. 登录。
3. 角色区分。
4. 图书查询。
5. 借书。
6. 还书。
7. 每人最多借 2 本。
8. 每书 3 个副本。
9. 管理员录入图书。
10. 管理员总览图书。

### 优先级 P1：重要功能

1. 管理员删除图书。
2. 管理员修改图书。
3. 管理员查询任意用户借阅状态。
4. 超期判断。
5. 用户查看自己的借阅状态。

### 优先级 P2：优化功能

1. 界面美化。
2. 查询条件优化。
3. 表格刷新优化。
4. 输入格式校验增强。
5. README 完善。

---

## 20. 项目完成后的交付物

最终应交付：

```text
library_system/
│
├── main.py
├── database.py
├── auth.py
├── services/
├── ui/
├── library.db
└── README.md
```

并确保：

```text
python main.py
```

可以直接启动系统。

---

## 21. 可直接交给 Codex 的开发指令

请根据本文档开发一个完整可运行的 Python 图书馆图书管理系统。系统使用 SQLite 保存数据，使用 Tkinter 实现图形化界面，包含管理员和普通用户两个角色。系统需要实现图书录入、删除、修改、查询、借书、还书、用户借阅状态查询、管理员总览图书信息等功能。每本书必须有 3 个副本，每个用户最多同时借 2 本书，用户有超期未还图书时不能借新书。首次运行程序时应自动初始化数据库，包含不少于 20 本图书和不少于 10 个用户。请按照本文档中的数据库结构、业务规则、项目目录、开发顺序和验收标准完成项目，并保证运行 `python main.py` 后可以直接启动系统。
