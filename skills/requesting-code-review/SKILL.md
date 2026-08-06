---
name: requesting-code-review
description: 完成任务、实现重大功能或准备合并，并需要验证工作是否满足要求时使用
---

# 请求代码审查

派出只读 reviewer subagent 捕获问题，但不委派实现。reviewer 只接收已批准的 executable spec 和 diff，绝不能得到当前 session 历史。

**核心原则：** 尽早审查，频繁审查。

## 何时请求审查

重大功能完成后和合并到 main 前必须审查。卡住时、重构前需要基线检查时，以及修复复杂 bug 后，也很有价值。

## 请求方法

### 1. 建立审查基线

已批准 spec 的提交是必需基线。审查从该提交到当前 working tree 的全部内容，确保已提交、已暂存和未暂存的实现变更都在范围内。

```bash
BASE_SHA=<approved-spec-commit>
git status --short
git diff --stat "$BASE_SHA"
git diff "$BASE_SHA"
```

普通 Git diff 不包含 untracked 文件内容，因此必须在 reviewer 上下文中明确列出未跟踪的实现文件。

### 2. 执行审查前验证

运行覆盖变更行为的聚焦测试和相关的更广测试集。记录精确命令、exit code 和失败数量作为验证证据。不要让 reviewer 推断测试状态，也不要让它通过运行实现流程来修改 checkout。

### 3. 派出只读 reviewer

派出 `general-purpose` subagent，并填写 [code-reviewer.md](code-reviewer.md) 模板。

reviewer 不得编辑文件、运行实现任务或提交。它只返回 findings；主 agent 评估意见，并通过 TDD 实施有效修复。

占位符：

- `{DESCRIPTION}`：实现内容的简述
- `{APPROVED_SPEC}`：已批准 executable spec 的路径和内容
- `{BASE_SHA}`：已批准 spec 所在的基线提交
- `{UNTRACKED_FILES}`：未跟踪实现文件，或 `None`
- `{VERIFICATION_EVIDENCE}`：精确命令和新鲜结果

### 4. 处理反馈

- 立即修复 Critical；继续前修复 Important；Minor 可留待以后。
- reviewer 错误时用技术证据反驳。
- 每个有效代码 finding 都必须由主 session 先用失败测试复现，再实施修复。
- 修复后重新验证并重复审查，直到没有 Critical 或 Important。

## 示例

```text
[working tree 已完成批准的 spec]

You: 合并前先请求 code review。

BASE_SHA=$(git rev-parse HEAD) # spec 在该提交获批
git status --short
git diff "$BASE_SHA"

[运行聚焦测试和相关的更广测试集]

[派出只读 code reviewer]
  DESCRIPTION: 添加 verifyIndex() 和 repairIndex()，覆盖 4 种问题
  APPROVED_SPEC: BASE_SHA 中的 docs/superpowers/specs/deployment-spec.md
  BASE_SHA: a7981ec
  UNTRACKED_FILES: None
  VERIFICATION_EVIDENCE: npm test -- indexer.test.ts (18 passed); npm test (142 passed)

[reviewer 返回 findings]

You: 评估 finding，在主 session 添加失败测试、修复、验证并再次审查。
```

## 常见合理化借口

| 借口 | 事实 |
|---|---|
| “自己看看 diff 就行，不用 reviewer” | 独立审查能发现实现 session 遗漏的假设。派只读 reviewer，所有编辑仍留在主 session。 |
| “reviewer 需要完整 session 历史” | 只提供精心整理的工作产物上下文，避免其被你的思考过程影响。 |
| “这个小问题让 reviewer 直接修” | 审查与实现的 authority 分离。reviewer 只报告，主 agent 用失败测试复现后修复。 |

## 红旗

绝不能因为“很简单”就跳过审查，不能忽略 Critical，不能带着未修复 Important 继续，不能与正确的技术反馈争辩，也不能允许 reviewer 编辑、实现或提交。

reviewer 错误时，给出技术推理和能证明实现正确的代码/测试，必要时请求澄清。
