---
name: ai-session-review
description: 用户要求查找、筛选、归档、比较、保留或删除已落盘的一个或多个 AI agent 会话，或按 session ID、项目、来源、时间窗口、月份执行历史复盘、经验晋级、retention 或多会话 skill audit 时使用；用户主动复盘当前 active conversation 的错误、弯路、记忆和环境改进时改用 retro
---

# AI 会话复盘

AI 会话复盘先锁定用户指定的会话集合，再从可追溯证据恢复目标、执行与结果。普通复盘默认只在当前回答中交付；归档、经验晋级、Raw 迁移和删除分别经过独立闸门。

## 1. 必读 Reference

先识别来源，再读取对应格式 reference。不要在不了解格式时直接全文扫描。

| 来源 | 必读文件 |
|---|---|
| Codex CLI / Desktop | `references/codex.md` |
| Claude / Claude Code | `references/claude.md` |
| Grok Build 本地 CLI / Dashboard | `references/grok-build.md` |
| Grok Bot Desktop | `references/grok-bot.md` |
| Gemini CLI | `references/gemini-cli.md` |
| Antigravity | `references/antigravity.md` |
| Cursor / Continue / Roo / Cline / Windsurf / 未知 Agent | `references/common-agent-apps.md` |

任何经验提取、持久化、retention 或删除评估还必须读取 `references/review-contract.md`。多会话 skill 有效性审计必须同时读取 `references/skill-effectiveness-audit.md`。来源 reference 决定怎样读数据；review contract 决定怎样形成 lesson 和落点；audit reference 决定怎样区分触发、行为效果和静态维护。

## 2. 先锁定 Purpose 与 Scope

```text
review_purpose = session-outcome | skill-effectiveness-audit
default = session-outcome
```

用户明确询问哪些已安装 skill 有效、低效、未触发或需要修改，并要求比较多个历史会话时，选择 `skill-effectiveness-audit`，固定使用 `scope_kind=multi-session` 与 `review_depth=deep`。其它已落盘会话的查找、结果复盘、归档、经验晋级、retention 或删除保持 `session-outcome`。

入口按目的互斥：

1. 「复盘这次当前对话有哪些弯路、错误、记忆或改进」只选择 `retro`。
2. 指定旧 session ID、项目、月份、时间窗口或多次会话时选择本 skill。
3. 查找、归档、导出、保留或删除已落盘 session 时选择本 skill，即使目标恰好是当前 thread。
4. 比较当前会话与历史窗口时由本 skill 拥有跨会话 scope；当前会话只有形成可定位 snapshot 后才能进入样本，未落盘部分写 `unavailable`。

`review_purpose` 只控制 review 语义，不加入 inventory、来源 parser 或 retention 状态机。旧调用没有该字段时按 `session-outcome`。

| `scope_kind` | 触发表达 | 边界 |
|---|---|---|
| `single-session` | 当前对话、这次会话、一个 session ID 或 rollout path | 恰好一个 canonical user session；只形成 `session-local` lesson |
| `multi-session` | 多个 ID、项目、来源、时间窗口、月份、年度、历史清理 | 允许 0、1 或多个命中；至少 2 个独立 occurrence 才形成 `cross-session` lesson |

规则：

1. 用户指定单会话时，不扫描其他历史寻找重复模式。
2. 精确选择先保留去重后的 `selected_thread_ids`，再递归映射并去重 `canonical_scope_ids`：1 个可归因 user root 是 `single-session`，2 个以上是 `multi-session`。传入多个 subagent ID 但都指向同一 user root 时仍是 `single-session`。
3. 用户指定多个 ID 时，只读取去重后的指定集合；失败的 lineage 仍留在 `selected_thread_ids` 并逐条标 `unavailable`，不进入 `canonical_scope_ids`。可归因 subagent 只作 `evidence_filter`，不增加 occurrence。
4. 项目、时间或月份 discovery 即使命中 0 或 1 个会话，仍保持 `multi-session`。
5. 合法 discovery 零命中时成功返回空结果，lesson 与跨会话判断写 `not_needed`；不放宽筛选。
6. 当前 task ID 无法可靠取得时，只列最近候选供确认。rollout path 与 state DB 无法交叉核对时标 `unavailable`。两者都不扩大扫描。
7. subagent ID 必须按 `references/codex.md` 递归映射到 user root；lineage 冲突或缺失时标 `unavailable`，不猜测 parent。

同时记录持久化意图：

- `report-only + not_requested`：用户只要求查看、分析或复盘；不修改 vault。
- `persist + ready`：用户明确要求归档、写入或沉淀，且 deep review 已通过证据、晋级与 retention 闸门。
- `persist + blocked`：用户要求写入，但证据或 review depth 尚不足。

## 3. 建立只读 Inventory

Codex 使用本 skill 自带脚本：

```bash
AI_SESSION_REVIEW_DIR="${AI_SESSION_REVIEW_DIR:-$HOME/.agents/skills/superpowers/ai-session-review}"
python3 "$AI_SESSION_REVIEW_DIR/scripts/codex_session_inventory.py" [filters]
```

Grok Build、Grok Bot、Gemini CLI 和 Antigravity 使用统一的本地只读入口：

```bash
AI_SESSION_REVIEW_DIR="${AI_SESSION_REVIEW_DIR:-$HOME/.agents/skills/superpowers/ai-session-review}"
python3 "$AI_SESSION_REVIEW_DIR/scripts/local_session_inventory.py" \
  --source all [filters]
```

`--source` 可选 `grok-build`、`grok-bot`、`gemini-cli`、`antigravity-desktop`、`antigravity-cli` 或 `all`。默认排除 subagent；需要时显式增加 `--include-subagents`。本入口只读取本机 transcript，不读取浏览器 History / IndexedDB、Cookie、Grok.com、X Grok、Gemini Apps 或云端账户数据。

`--source all --id <ID>` 命中多个来源的同一 ID 时原子失败，必须用具体 `--source` 消歧。同一来源发现多个同 ID artifact 时只保留一条 inventory row，并标 `evidence_status=unavailable`，不得静默选择其中一份作为完整正文。

常见自然语言映射：

| 用户表达 | 参数 |
|---|---|
| 一周以前 | `--older-than 7d` |
| 最近一周 | `--newer-than 7d` |
| 一个自然月以前 | `--older-than 1m` |
| 30 天以前 | `--older-than 30d` |
| 2026 年 6 月 | `--month 2026-06` |
| 指定项目 | `--cwd <exact-path>` |
| 一个或多个 ID | 重复 `--id <SESSION_ID>` |

`1m` 是日历月，`30d` 是固定 30 天。清理年龄只使用最后活动时间。完整参数以脚本 `--help` 和来源 reference 为准。

本地多来源 inventory 中，`archived`、pin 和云端删除状态不可统一观察，不得从文件位置或应用 UI 线索补猜。缺少正文 authority、时间或 cwd 时保留 `unavailable` / `null`，不使用文件 `mtime` 填充。

正文文件为空、只有无法识别的记录或含 malformed JSONL 时，`evidence_status=unavailable`。认证脱敏在最终序列化层覆盖所有字符串字段；Grok Bot 的真实 blob basename 含可逆账户 scope，只能在进程内定位，不能进入输出。

只探测 Agent 特征目录和 state DB，不递归扫描整个用户主目录或项目树。大文件先看字段、事件分布和首尾；认证值不进入清单或复盘。

## 4. 选择 Review Depth

每次任务都记录 `review_depth=quick / deep / not_needed`。

`single-session` 默认 `quick`，命中任一条件后自动使用 `deep`：

1. 用户纠正改变目标、scope、禁止事项或交付结果。
2. 执行失败、中止后未闭合，或关键结果缺少验证。
3. 发生明确返工、时间或资金损失、安全风险、不可逆外部影响。
4. 形成架构、业务、策略或项目边界等重大判断。
5. 涉及持久化、经验晋级、Raw retention 或删除评估。

`single-session` 用户明确要求只做轻量复盘时保持 `quick`，最高 `review_status=skimmed`。此时不晋级、不持久化、不生成删除候选；已有 `persist` 意图固定为 `blocked`。

强制 quick 同时包含归档、晋级或删除请求时，输出固定状态行：

```text
review_depth=quick, review_status=skimmed,
persistence_intent=persist, persistence_status=blocked
```

随后分别写明未执行的晋级、持久化和删除候选，以及完成 deep review 才能重新评估的条件。

`multi-session` 只要实际提取 lesson、判断跨会话模式、评估晋级、retention 或删除，就固定使用 `deep` 和 `references/review-contract.md` 的完整合同。多会话的“轻量”只能压缩最终展示，不能把内部 review 降为 `quick`。用户明确禁止 `deep` 时，只做到 inventory 和目标解析，使用 `review_depth=not_needed`：不读取会话正文、不提取 lesson、不评估晋级、retention 或删除；已有 `persist` 意图固定为 `blocked`。纯 inventory、目标解析或合法零命中同样使用 `not_needed`；discovery 命中 1 个并实际提取 `session-local` lesson 时仍是 `deep`。

优先级固定为：安全与删除闸门 > scope 能力边界 > scope 内用户显式 depth > 单会话自动 deep 条件。

## 5. 恢复证据

按来源 reference 分三层读取：

1. `inventory`：ID、时间、cwd、title、thread kind、pin 和 rollout path。
2. `skim`：真实用户请求、助手交付、工具调用、工具输出、错误和验证结果。
3. `extract`：只为有事实承重的候选形成 lesson。

Codex 的关键边界：

- 真实用户输入只归因于 `event_msg/user_message`。
- 缺失真实用户事件时标 `unavailable`，不从注入的 `response_item.role=user` 补猜。
- 工具调用同时覆盖 `function_call.arguments` 与 `custom_tool_call.input`。
- call 与 output 即使共用 `call_id` 也分别保留；同类型副本去重。
- fork 继承前缀归 parent 一次，不为 child 重复计数；child 新 tail 的用户证据可以另计一次。只有用户明确指定 child 单会话时，parent 前缀才是 `out_of_scope`。
- 用户要求统计整个 fork lineage 的 lesson occurrence 且未限制只看 child 时，统计范围包含 parent 与 child：parent 前缀贡献 parent occurrence，child 新 tail 贡献 child occurrence。
- resume、compaction、重复 meta 和 subagent 不增加独立 occurrence。
- `world_state`、reasoning 和 summary 只用于导航，不能成为关键事实的唯一证据。

## 6. 形成 Review

`quick` 固定输出：

```text
一句话结论
1. 目标与明确约束
2. 实际结果与验证状态
3. 关键偏差与有效做法
4. 经验教训（0 至 3 条）
   事实 -> 判断 -> 下次动作 -> 验证方法 -> 适用边界
5. 已产生资产、未完成事项与证据边界
```

没有可复用 lesson 时明确写 `not_needed` 和原因。不要为填模板制造经验。

`deep` 按 `references/review-contract.md` 写完整 lesson。每项判断必须挂载具体事实、证据状态、替代解释、适用边界、action 与 verification。`independent_occurrences` 必须等于去重后的 `occurrence_ids` 数量。

## 7. 路由与持久化

| 内容角色 | Canonical 位置 |
|---|---|
| 历史会话、代表证据、review 状态、删除迁移 | `area/codex-archive-review/ai-sessions/YYYY/YYYY-MM.md` |
| 跨月主题与已完成晋级 | `area/codex-archive-review/ai-sessions/YYYY/YYYY-summary.md` |
| 仍在生效的 AI 协作判断 | `area/ai/` 的已有或明确批准文章 |
| 全局高代价护栏 | 根 `AGENTS.md` |
| 可执行重复流程 | 对应 skill |
| Agent 格式与 parser 事实 | 对应 `references/*.md` |
| 项目专属边界 | repo 本地规则或设计文档 |

根 `AGENTS.md` 的同一条 lesson 必须同时满足：真实发生、至少 2 个独立 canonical user session occurrence、代价明确。不同 lesson 不能拆开拼够门槛。

新建正式笔记前先检索 canonical 入口。修改已有笔记前完整读完原文。月度历史与现役 consumer 分开写，不让月度历史成为仍生效经验的 SSOT。

## 8. Retention 与删除

### 8.1 会话证据删除闸门

年龄、`archived=1`、`promoted` 都不能单独触发会话删除。只有 deep review 完成、应晋级内容已进入 canonical consumer、Raw 不再是唯一证据、年龄为 `mature` 且 pin 保护已处理，才可标记 `deletion_candidate`。

pinned 会话默认 `retain_raw`。用户按 ID 解除 pin 候选保护后，只能重新评估候选；这一步不等于最终删除授权。

候选清单生成后，必须再次取得用户对精确 session ID 或文件范围的授权，才能从 `deletion_candidate` 进入 `approved`。本 skill 不提供默认批量删除命令，也不自行删除来源不明的新文件。

删除、迁移或删除后验证失败，以及只删除部分 artifact 时，`approved` 立即退回 `retain_raw`。记录已删除项、仍存项和失败原因，重新 inventory 并从删除闸门开始评估；旧批准不复用，新候选仍需新的精确授权。

### 8.2 运行时日志与 SQLite 瘦身 (Runtime Logs Hygiene)

对 `~/.codex/logs_2.sqlite`、`*.sqlite-wal` 等运行时辅助资产，因其仅包含 WebSocket/transport 调试遥测日志，**不包含任何会话正文与 Prompt 证据**：

- 不受会话 Review 流程与 Deletion Candidate 闸门约束。
- 可使用 `codex_runtime_hygiene.py` 检查死页（Freelist）并安全执行日志截断与 VACUUM 瘦身：
  ```bash
  python3 "$AI_SESSION_REVIEW_DIR/scripts/codex_runtime_hygiene.py" --inspect
  python3 "$AI_SESSION_REVIEW_DIR/scripts/codex_runtime_hygiene.py" --clean-logs --keep-days 7
  ```


## 9. 交付

最终回答至少说明：

1. 实际 scope、命中数、review depth 与 persistence 状态。
2. 已确认的 lesson、证据边界和未形成 lesson 的原因。
3. 新增或更新的月度历史与 canonical consumer。
4. `retain_raw`、`deletion_candidate` 和已获批准范围。
5. `unavailable / rejected / out_of_scope / not_needed` 项及原因。

未运行、未读取或未验证的内容不得写成已完成。
