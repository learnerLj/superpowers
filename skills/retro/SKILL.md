---
name: retro
description: 用户主动要求复盘当前对话，识别本次 Agent 工作中的目标偏差、用户纠正、工具错误、弯路、导航与信息缺口、自动检查、skill 与规则改进、上下文协作问题、长期记忆候选、可复用资产或未关闭事项时使用；默认只审查调用时可见的当前会话证据及已回传的子任务结果，不自动扫描历史、修改文件或持久化任何内容
---

# 当前会话复盘

只在用户明确要求复盘当前对话时运行。冻结触发消息之前的会话边界，扫描完整诊断角度，只展示有证据和实际影响的 finding。默认 `report-only`，不写 memory、skill、instruction、hook、note 或 commit。

## 1 锁定证据边界

```text
current_session_authority = runtime-current-thread-reader | runtime-visible-context | unavailable
acquisition_status = complete | context-bounded | unavailable
review_cutoff = 用户触发 retro 的 message boundary
persistence_intent = not_requested
```

1. Runtime 有当前 thread 的直接 reader 时，只读该 thread 到 cutoff；只沿上下文已明确关联的 child ID 读取已回传结果，不先搜索全部历史。
2. 没有直接 reader 时，只使用当前可见消息、tool output、compaction summary 和已回传 child result，固定写 `context-bounded`。
3. 无法确定当前目标、关键 turn 或 cutoff 时写 `unavailable` 并停止诊断；不得用历史 inventory 补齐。
4. 不复盘 `retro` 自己为取证产生的动作。
5. 用户指定旧 session、项目、月份、时间窗口、多次会话、归档或删除时，改用 `ai-session-review`。

## 2 读取完整合同

取得证据边界后，完整读取 [retrospective-contract.md](retrospective-contract.md)，逐类扫描 taxonomy，并按其中 finding schema 去重和路由。

日常报告使用 `material-only`。只有用户明确要求审计完整 taxonomy 或行为 evaluator 需要证明逐类检查时，才使用 `audit` 并输出 `taxonomy_closure_map`。

## 3 输出顺序

1. 目标、约束与实际结果快照。
2. 按优先级排序的 material findings。
3. 值得保留或实施的候选及唯一 owner。
4. 未关闭事项、不可观察边界和 acquisition status。

没有证据的类别内部关闭为 `not_needed`，不展示空表格。一次 occurrence 只能形成 session-local 判断，不能写成跨会话稳定模式。

## 4 写入门槛

- `memory`：只提出候选；用户批准后交给运行环境的 memory update owner。
- `skill`：只指出目标、证据和最小候选；用户批准后交给 `writing-skills`。
- `instruction`、`automated-check`、`tool`、`documentation`：交给对应 repo owner。
- `session-only`：只保留在本次报告。

任何候选都保持 `proposed`。本 skill 不自动修改、创建、删除、提交、排期或持久化。
