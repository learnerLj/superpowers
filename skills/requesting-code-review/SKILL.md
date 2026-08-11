---
name: requesting-code-review
description: 完成软件实现、重大或高风险功能、复杂 bug 修复、准备合并，或需要独立验证 diff 与当前需求 authority 时使用
---

# 请求代码审查

派出只读 reviewer subagent 捕获问题，但不委派实现。reviewer 只接收当前任务的 review authority、diff 和新鲜验证证据，绝不能得到当前 session 历史。

**核心原则：** 对高价值边界做独立审查；finding 的优先级由真实风险和修复 ROI 决定。

## 何时请求审查

重大或高风险功能完成后、公共 contract 或跨组件行为改变后、复杂 bug 修复后，以及软件变更合并到 main 前必须审查。卡住时或重构前需要独立基线检查时也应审查。

对局部、低风险且聚焦验证已经充分的软件改动，独立 review 是可选项。不要仅凭“存在潜在 bug”提高流程成本；先评估影响、真实触发路径与触发频率、影响范围、发现概率和修复成本。几乎不可达且影响很小的问题通常是 Minor 或不报告；低频但会造成资金、安全、数据丢失或不可逆状态的问题仍然是高优先级。

## 请求方法

### 1. 建立审查 Authority 与基线

先按任务类型选择唯一 review authority：

- 有 executable spec 的长任务：`REVIEW_AUTHORITY` 是已批准 spec，`BASE_SHA` 是单独提交该 spec 的 commit。
- 没有独立 spec 的短软件任务：`REVIEW_AUTHORITY` 是用户原始要求、适用的项目 authority 和可观察验收条件，`BASE_SHA` 是实现开始前的 commit。不得为了 review 事后补写 spec。

审查从 `BASE_SHA` 到当前 working tree 的任务相关内容，覆盖已提交、已暂存和未暂存的实现变更。工作树已有无关修改时，在 review 上下文中明确列出并排除，不能让 reviewer 把它们归入本任务。

```bash
BASE_SHA=<review-base-commit>
git status --short
git diff --stat "$BASE_SHA"
git diff "$BASE_SHA"
```

普通 Git diff 不包含 untracked 文件内容，因此必须在 reviewer 上下文中明确列出未跟踪的实现文件。

### 2. 执行审查前验证

运行覆盖变更行为的聚焦测试和相关的更广测试集。记录精确命令、exit code 和失败数量作为验证证据。不要让 reviewer 推断测试状态，也不要让它通过运行实现流程来修改 checkout。

### 3. 派出只读 reviewer

使用当前 harness 的原生 agent 工具派出 fresh-context、只读 reviewer，并填写 [code-reviewer.md](code-reviewer.md) 模板。

reviewer 不得编辑文件、运行实现任务或提交。它只返回 findings；reviewer 返回后，主 agent 必须加载 `receiving-code-review` 验证意见，获得修复授权后再通过 TDD 实施有效修复。

占位符：

- `{DESCRIPTION}`：实现内容的简述
- `{REVIEW_AUTHORITY}`：已批准 executable spec，或短任务的用户原始要求、项目 authority 与验收条件
- `{BASE_SHA}`：已批准 spec 的提交，或短任务实现开始前的提交
- `{UNTRACKED_FILES}`：未跟踪实现文件，或 `None`
- `{VERIFICATION_EVIDENCE}`：精确命令和新鲜结果

### 4. 处理反馈

- reviewer 返回 findings 后，必须先加载 `receiving-code-review`，不能把 finding 直接当成修改指令。
- 先把核查后的 findings 交给用户；只有已明确授权 review 后直接修复时，才立即修复 Critical、在继续前修复 Important，Minor 可留待以后。
- reviewer 错误时用技术证据反驳。
- 对每个 finding 核对可达触发路径、发生概率或频率、影响范围和修复成本；证据不足时标记 `NOT VERIFIED`，不能把理论可能性写成确定 bug。
- 新行为、行为修改或 bugfix finding 由主 session 先用失败测试复现，再实施修复。
- 纯行为保持型重构 finding 先确认相关测试的 GREEN 基线，再重构并让相同测试继续 GREEN；测试不足时先增加 characterization test 并确认旧行为。
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
  REVIEW_AUTHORITY: BASE_SHA 中的 docs/superpowers/specs/deployment-spec.md
  BASE_SHA: a7981ec
  UNTRACKED_FILES: None
  VERIFICATION_EVIDENCE: npm test -- indexer.test.ts (18 passed); npm test (142 passed)

[reviewer 返回 findings]

You: 加载 receiving-code-review，评估 finding，并向用户返回核查结果。

[用户授权直接修复]

You: 在主 session 按 finding 性质走 RED-GREEN 或 GREEN 基线重构，验证并再次审查。
```

## 常见合理化借口

| 借口 | 事实 |
|---|---|
| “自己看看 diff 就行，不用 reviewer” | 独立审查能发现实现 session 遗漏的假设。派只读 reviewer，所有编辑仍留在主 session。 |
| “reviewer 需要完整 session 历史” | 只提供精心整理的工作产物上下文，避免其被你的思考过程影响。 |
| “这个小问题让 reviewer 直接修” | 审查与实现的 authority 分离。reviewer 只报告，主 agent 按 finding 性质选择失败测试或 GREEN 基线后修复。 |

## 必须停下的信号

命中强制审查门槛时不能因为“很简单”而跳过；不能忽略 Critical，不能带着未修复 Important 继续，不能与正确的技术反馈争辩，也不能允许 reviewer 编辑、实现或提交。

reviewer 错误时，给出技术推理和能证明实现正确的代码/测试，必要时请求澄清。
