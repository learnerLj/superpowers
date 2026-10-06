---
name: worktree-and-pr
description: 软件代码仓库里要提交的改动使用。在 git worktree 的非默认分支上改，并打开 GitHub pull request。
---

# worktree 和 pull request

软件代码仓库的改动落在非默认分支，并用 GitHub pull request 交给 Codex 审查。Codex 的 GitHub code review 只作用于 pull request：该仓库已经打开自动审查时等它跑完；没有自动审查时，在该 PR 评论 `@codex review`。仓库自己的审查细则写在目标仓库 `AGENTS.md` 的 `## Code Review Rules`，不另建审查 skill。

文档页面是 <https://learn.chatgpt.com/docs/third-party/github>。

## 1 范围

这条适用于会进入 git 的软件代码改动。知识库笔记仓库仍按该库自己的提交约定处理，不为此建 worktree，也不开 pull request。

默认分支用 `git symbolic-ref --short refs/remotes/origin/HEAD` 读取。读不到时，再确认远端的 `main` 或 `master` 哪一个是默认分支。不在默认分支上 commit。

用户当次明确说只留在本地、或不推远程时，停在本地分支，不开 pull request。

## 2 工作区

当前目录已经是 linked worktree 时，继续在这里改，不再新建。判断标准是 `git rev-parse --git-dir` 和 `git rev-parse --git-common-dir` 解析出的路径不同。

需要隔离时再执行 `git worktree add`。目录用仓库里已经在用的 `.worktrees/` 或 `worktrees/`；两处都没有时用 `.worktrees/<branch>`。

仓库有 `.codex/environments/environment.toml` 时，新 worktree 的本地文件以这份 Codex environment 为准。

- Codex 应用创建 worktree，且已经选中对应 local environment 时，让应用自己的 setup 跑，不要再手写一套链接。
- 自己执行 `git worktree add` 时，把 `CODEX_SOURCE_TREE_PATH` 设为源仓库根，把 `CODEX_WORKTREE_PATH` 设为新目录，然后运行 toml 里当前系统的 setup script。苹果系统读 `[setup.darwin]`，Linux 读 `[setup.linux]`。
- setup 拒绝覆盖已经存在的普通文件时停下来，不要改脚本去强行替换。
- 没有这份 toml 时，只建 worktree，不补配置链接。

## 3 审查单位

代码审查看 GitHub 上的这一个 pull request。Codex 的审查跑在这个 PR 上，规则仍来自目标仓库 `AGENTS.md` 的 `## Code Review Rules`。

一个 spec 写一个要迭代的功能。这个 spec 一般对应一个 pull request。同一功能后面的修改继续推到这个 PR 的分支。另一个功能另写 spec，并另开 pull request。

没有 spec 的短改动单独开一个 pull request，不为它补写 spec。

## 4 打开 pull request

已有未合并的 pull request 属于当前 spec 时，把这次提交推上去，不新开一个。否则用 `git push -u origin <branch>` 推送当前分支，分支名不要写成默认分支，再用 `gh pr create` 打开 pull request。只暂存这次任务的文件。不合并。

## 5 衔接

打开 pull request 之前，这次改动仍用 `verification-before-completion` 核对证据。本地独立审查仍用 `requesting-code-review`。这两步不代替 GitHub 上的 Codex review，也不负责推送。
