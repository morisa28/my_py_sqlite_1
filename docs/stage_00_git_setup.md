# 阶段 00：Git 基线与开发约定

## 目标

- 初始化项目 Git 仓库。
- 保留原始需求文档作为开发依据。
- 配置远端仓库地址。
- 启用项目内 Git worktree 工作流。

## 当前状态

- 项目目录：`F:\file\wsl_shared_files\study\py_sql_1`
- WSL 路径：`/home/just_monika/win_share/study/py_sql_1`
- 需求文档：`library_system_codex_guide.md`
- 远端仓库：`https://github.com/morisa28/my_py_sqlite_1`

## Worktree 约定

- 主工作区保存稳定基线与文档。
- 开发工作区位于 `.worktrees/`。
- 开发分支使用 `codex/` 前缀。
- 每个小阶段完成后提交一次 Git commit。

## 备注

该项目位于 Windows 共享目录中，WSL Git 在初始化 `.git` 时会遇到 chmod 限制。因此后续 Git 操作优先使用 Windows 侧 Git 执行。
