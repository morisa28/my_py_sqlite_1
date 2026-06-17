# 阶段 01：项目结构搭建

## 目标

按照需求文档建立模块化项目结构，为后续数据库、服务层和 Tkinter 界面开发提供清晰边界。

## 完成内容

- 创建程序入口 `main.py`。
- 创建数据库模块 `database.py`。
- 创建登录认证模块 `auth.py`。
- 创建服务层目录 `services/`。
- 创建界面目录 `ui/`。
- 创建 README 初始说明。

## 模块职责

- `database.py`：负责 SQLite 连接、建表和初始化测试数据。
- `auth.py`：负责账号密码验证和角色判断。
- `services/book_service.py`：负责图书查询、录入、删除、修改和总览。
- `services/borrow_service.py`：负责借书、还书、当前借阅和超期判断。
- `services/user_service.py`：负责管理员查询用户借阅状态。
- `ui/`：负责 Tkinter 登录窗口、普通用户窗口和管理员窗口。

## 下一阶段

实现 SQLite 数据库建表逻辑，并插入管理员、普通用户、图书和图书副本初始化数据。
