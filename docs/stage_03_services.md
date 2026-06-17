# 阶段 03：认证与服务层

## 目标

实现图形界面之前的核心业务函数，确保数据库规则可以通过服务层统一执行。

## 完成内容

- `auth.login()`：验证账号密码并返回用户角色信息。
- `book_service.search_books()`：按编号或书名模糊查询图书。
- `book_service.get_all_books_overview()`：管理员总览所有未删除图书。
- `book_service.get_book_copies_detail()`：查询某本书的副本借阅详情。
- `book_service.add_book()`：录入图书并自动生成 3 个副本。
- `book_service.delete_book()`：逻辑删除无借出副本的图书。
- `book_service.update_book()`：修改作者、出版社、出版日期、价格，保持书名不可修改。
- `borrow_service.borrow_book()`：执行超期、借阅数量、图书存在性和可借副本检查。
- `borrow_service.return_book()`：归还当前用户的有效借阅记录。
- `borrow_service.get_user_current_borrows()`：查询普通用户当前未还图书。
- `user_service.get_user_borrow_status()`：管理员按用户 ID、账号或姓名查询借阅状态。

## 关键业务规则

- 每个用户最多同时借阅 2 本书。
- 用户存在超期未还图书时禁止借新书。
- 图书无可借副本时禁止借出。
- 删除图书前必须确认没有副本处于借出状态。
- 修改图书时不提供修改书名的服务入口。

## 验证重点

- 登录管理员和普通用户账号。
- 查询初始化图书状态。
- 正常借书、还书。
- 借满 2 本后继续借书应失败。
- 新增图书后应有 3 个可借副本。
- 删除有借出副本的图书应失败。

## 下一阶段

实现 Tkinter 登录窗口、普通用户主界面和管理员主界面，并将按钮操作接入服务层函数。
