---
name: finishing-a-development-branch
description: 实现已经完成且全部测试通过，需要决定如何集成工作时使用
---

# 完成开发分支

## 概述

**核心原则：** 验证测试、识别 branch 状态、展示集成选项，并且只执行用户选择。

开始时声明：“我正在使用 finishing-a-development-branch skill 完成这项工作。”

## 步骤 1：验证测试

在将被集成的精确 tree 上运行项目完整测试集。测试失败时报告失败并停止；测试未绿之前不能展示集成选项。

## 步骤 2：确认集成快照

```bash
git status --short
```

主 agent 必须已经在最终验证后提交实现。若预期实现变更仍未提交，停止并返回验证与提交。绝不能把用户无关变更一并塞进提交。

## 步骤 3：识别 branch 状态

```bash
BRANCH=$(git branch --show-current)
HEAD_SHA=$(git rev-parse HEAD)
```

named branch 可用全部三个集成选项；detached HEAD 不能本地 merge，只能提供“作为新 branch 推送并建 PR”或“保持现状”。

## 步骤 4：确认 base branch

从对话、branch upstream 或 merge base 解析 base。仍有歧义时，必须在 merge 或创建 PR 前询问用户确认。

## 步骤 5：展示选项

named branch：

```text
实现已完成。你希望如何处理？

1. 在本地合并回 <base-branch>
2. 推送并创建 Pull Request
3. 保持当前 branch 不变

请选择：
```

detached HEAD：

```text
实现已完成，当前处于 detached HEAD。

1. 作为新 branch 推送并创建 Pull Request
2. 保持现状

请选择：
```

等待用户回答。丢弃永远不能成为菜单选项。

## 步骤 6：执行选择

### 选项 1：本地合并

```bash
git checkout <base-branch>
git pull --ff-only
git merge <feature-branch>
<full test command>
```

合并结果测试失败时停止并报告，不得删除 feature branch。全部通过后才可执行：

```bash
git branch -d <feature-branch>
```

### 选项 2：推送并创建 Pull Request

```bash
git push -u origin <feature-branch>
# Detached HEAD:
# git push origin HEAD:refs/heads/<new-branch>
```

按照仓库模板与惯例，对已确认 base branch 创建 PR 并报告 URL。

### 选项 3：保持现状

报告 branch 名称和当前 commit，不修改仓库。

### 用户明确要求丢弃

只有用户明确要求丢弃 branch 时才可执行。先展示精确 branch 和 commits，再要求用户输入精确确认词 `discard`。

确认后：

```bash
git checkout <base-branch>
git branch -D <feature-branch>
```

branch cleanup 绝不能删除 untracked 文件或无关 branch。

## 常见合理化借口

| 借口 | 事实 |
|---|---|
| “测试之前通过了” | 必须在将被集成的精确 tree 上重新运行。 |
| “用户显然想 merge” | 集成由用户决定，展示选项并等待。 |
| “丢弃更整洁” | 只有用户明确请求并精确确认后才能丢弃。 |
| “base 显然是 main” | 必须先解析或确认真实 base。 |
| “push 被拒，直接 force-push” | 先调查 remote 变化；force-push 需要明确授权。 |
