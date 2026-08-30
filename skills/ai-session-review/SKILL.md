---
name: ai-session-review
description: 用户要求查找、筛选、归档、比较、保留或删除已落盘的一个或多个 AI agent 会话，或按 session ID、项目、来源、时间窗口、月份执行历史复盘、经验晋级、retention 或多会话 skill audit 时使用；用户主动复盘当前 active conversation 的错误、弯路、记忆和环境改进时改用 retro
---

# AI 会话复盘

这是已落盘历史会话的复盘，不是当前对话的 retro。先圈定用户指定的那一批会话，再凭可回查证据恢复当时要做什么、实际做了什么、结果如何。

用户只说看、分析、复盘时，结论留在这次回答里，不改 vault。归档、把经验教训写进现役笔记、搬 Raw、删除，各自单独过闸。删除不是复盘的附带动作：经验教训总结完之后，才允许用户去删；到那一步可以询问，或等用户明确下令。没有询问、没有明确指令，不删。

## 对用户怎么说

对用户用中文。中文能准确说清的，就说中文。不要甩英文字段，也不要另造听不懂的词。

内部记账仍用合同英文字段；那是脚本、月度 ledger 和压力测试的列名，不是对用户的叫法。

| 内部字段 | 对用户 |
|---|---|
| `lesson` | 经验教训。禁止写成「课」 |
| `session-local` | 只适用于这一次会话 |
| `cross-session` | 跨多次会话重复出现 |
| `cooling` | 最后活动已满 7 天、未满 30 天。不要发明「冷却窗口」 |
| `mature` | 最后活动已满 30 天 |
| `active` | 7 天内还在活动 |
| `extracted` | 证据已经抽出 |
| `skimmed` | 只过了一遍，没有抽出经验教训 |
| `quick` | 轻量复盘 |
| `deep` | 完整复盘 |
| `not_needed` | 这次不必做，或没有可写的经验教训 |
| `unavailable` | 读不到、对不上 |
| `report-only` | 只在这次回答里说 |
| `persist` + `ready` | 可以写入 |
| `blocked` | 还不能写 |
| `retain_raw` | 原始记录继续留着 |
| `deletion_candidate` | 删除候选，还没删。总结完才可以问要不要删 |

对用户先讲：复了哪些会话、发现了什么、写到了哪里、原始记录还在不在。FORCE-QUICK 的固定状态行必须原样输出。用户没问字段名时，不要拿它们当正文标题。

## 1. 必读 Reference

先识别来源，再读对应格式 reference。格式没摸清之前，不要直接全文扫描。

| 来源 | 必读文件 |
|---|---|
| Codex CLI / Desktop | `references/codex.md` |
| Claude / Claude Code | `references/claude.md` |
| Grok Build 本地 CLI / Dashboard | `references/grok-build.md` |
| Grok Bot Desktop | `references/grok-bot.md` |
| Gemini CLI | `references/gemini-cli.md` |
| Antigravity | `references/antigravity.md` |
| Cursor / Continue / Roo / Cline / Windsurf / 未知 Agent | `references/common-agent-apps.md` |

提取经验教训、持久化、retention 或删除评估时，再读 `references/review-contract.md`。多会话 skill 有效性审计还要读 `references/skill-effectiveness-audit.md`。来源 reference 管怎么读数据；review contract 管经验教训怎么写、落到哪里；audit reference 管怎么区分触发、行为效果和静态维护。

## 2. 目的与范围

```text
review_purpose = session-outcome | skill-effectiveness-audit
default = session-outcome
```

用户明确问哪些已安装 skill 有效、低效、未触发或需要改，并且要比较多段历史会话时，用 `skill-effectiveness-audit`，同时固定 `scope_kind=multi-session`、`review_depth=deep`。其余查找、结果复盘、归档、晋级、retention 或删除，都用 `session-outcome`。

入口按目的互斥：

1. 「复盘这次当前对话有哪些弯路、错误、记忆或改进」只走 `retro`。
2. 指定旧 session ID、项目、月份、时间窗口或多次会话，走本 skill。
3. 查找、归档、导出、保留或删除已落盘 session，也走本 skill，哪怕目标恰好是当前 thread。
4. 拿当前会话和历史窗口比较时，跨会话 scope 归本 skill。当前会话只有形成可定位 snapshot 后才能进样本，未落盘部分写 `unavailable`。

`review_purpose` 只改 review 语义，不进 inventory、来源 parser 或 retention 状态机。旧调用没这个字段时，按 `session-outcome`。

| `scope_kind` | 触发表达 | 边界 |
|---|---|---|
| `single-session` | 当前对话、这次会话、一个 session ID 或 rollout path | 恰好一个 canonical user session；只形成单次会话的经验教训 |
| `multi-session` | 多个 ID、项目、来源、时间窗口、月份、年度、历史清理 | 允许 0、1 或多个命中；至少 2 个独立 occurrence 才形成跨会话经验教训 |

范围决定：

1. 用户指定单会话时，不扫其他历史找重复模式。
2. 精确选择先保留去重后的 `selected_thread_ids`，再递归映射并去重 `canonical_scope_ids`：1 个可归因 user root 是 `single-session`，2 个以上是 `multi-session`。传入多个 subagent ID 但都指向同一 user root 时，仍是 `single-session`。
3. 用户指定多个 ID 时，只读去重后的指定集合。失败的 lineage 仍留在 `selected_thread_ids`，逐条标 `unavailable`，不进 `canonical_scope_ids`。可归因 subagent 只作 `evidence_filter`，不增加 occurrence。
4. 项目、时间或月份 discovery 即使命中 0 或 1 个会话，仍保持 `multi-session`。
5. 合法 discovery 零命中时，成功返回空结果；经验教训与跨会话判断写 `not_needed`，不放宽筛选。
6. 当前 task ID 无法可靠取得时，只列最近候选供确认。rollout path 与 state DB 对不上时标 `unavailable`。两者都不扩大扫描。
7. subagent ID 必须按 `references/codex.md` 递归映射到 user root。lineage 冲突或缺失时标 `unavailable`，不猜 parent。

是否写入：

- `report-only + not_requested`：用户只要求查看、分析或复盘；不改 vault。
- `persist + ready`：用户明确要求归档、写入或沉淀，且完整复盘已过证据、晋级与 retention 闸门。
- `persist + blocked`：用户要求写入，但证据或复盘深度还不够。

## 3. 只读 Inventory

Codex 用本 skill 自带脚本：

```bash
AI_SESSION_REVIEW_DIR="${AI_SESSION_REVIEW_DIR:-$HOME/.agents/skills/superpowers/ai-session-review}"
python3 "$AI_SESSION_REVIEW_DIR/scripts/codex_session_inventory.py" [filters]
```

Grok Build、Grok Bot、Gemini CLI 和 Antigravity 走统一的本地只读入口：

```bash
AI_SESSION_REVIEW_DIR="${AI_SESSION_REVIEW_DIR:-$HOME/.agents/skills/superpowers/ai-session-review}"
python3 "$AI_SESSION_REVIEW_DIR/scripts/local_session_inventory.py" \
  --source all [filters]
```

`--source` 可选 `grok-build`、`grok-bot`、`gemini-cli`、`antigravity-desktop`、`antigravity-cli` 或 `all`。默认排除 subagent；需要时显式加 `--include-subagents`。这里只读本机 transcript，不读浏览器 History / IndexedDB、Cookie、Grok.com、X Grok、Gemini Apps 或云端账户。

`--source all --id <ID>` 命中多个来源的同一 ID 时原子失败，必须换成具体 `--source` 消歧。同一来源发现多个同 ID artifact 时只留一条 inventory row，并标 `evidence_status=unavailable`，不得静默挑其中一份当完整正文。

常见说法对照：

| 用户表达 | 参数 |
|---|---|
| 一周以前 | `--older-than 7d` |
| 最近一周 | `--newer-than 7d` |
| 一个自然月以前 | `--older-than 1m` |
| 30 天以前 | `--older-than 30d` |
| 2026 年 6 月 | `--month 2026-06` |
| 指定项目 | `--cwd <exact-path>` |
| 一个或多个 ID | 重复 `--id <SESSION_ID>` |

`1m` 是日历月，`30d` 是固定 30 天。清理年龄只看最后活动时间。完整参数以脚本 `--help` 和来源 reference 为准。

本地多来源 inventory 里，`archived`、pin 和云端删除状态不可统一观察，不得从文件位置或应用 UI 线索补猜。缺少正文 authority、时间或 cwd 时保留 `unavailable` / `null`，不用文件 `mtime` 填。

正文为空、只有无法识别的记录，或含 malformed JSONL 时，`evidence_status=unavailable`。认证脱敏在最终序列化层覆盖所有字符串字段。Grok Bot 的真实 blob basename 含可逆账户 scope，只能在进程内定位，不能进输出。

只探测 Agent 特征目录和 state DB，不递归扫整个用户主目录或项目树。大文件先看字段、事件分布和首尾；认证值不进清单或复盘。

## 4. 复盘深度

每次任务都记下 `review_depth=quick / deep / not_needed`。对用户分别说轻量复盘、完整复盘、这次不必读正文。

`single-session` 默认轻量复盘，命中任一条件后改完整复盘：

1. 用户纠正改变了目标、scope、禁止事项或交付结果。
2. 执行失败、中止后未闭合，或关键结果缺少验证。
3. 发生明确返工、时间或资金损失、安全风险、不可逆外部影响。
4. 形成架构、业务、策略或项目边界等重大判断。
5. 涉及持久化、经验晋级、Raw retention 或删除评估。

`single-session` 用户明确只要轻量复盘时保持 `quick`，最高 `review_status=skimmed`。此时不晋级、不持久化、不生成删除候选；已有 `persist` 意图固定为 `blocked`。

强制轻量复盘同时又要求归档、晋级或删除时，先输出固定状态行：

```text
review_depth=quick, review_status=skimmed,
persistence_intent=persist, persistence_status=blocked
```

随后分别写明未执行的晋级、持久化和删除候选，以及完成完整复盘才能重新评估的条件。

`multi-session` 只要实际提取经验教训、判断跨会话模式、评估晋级、retention 或删除，就固定用 `deep`，并走 `references/review-contract.md` 的完整合同。多会话的「轻量」只能压缩最终展示，不能把内部 review 降成 `quick`。用户明确禁止完整复盘时，只做到盘点和目标解析，使用 `review_depth=not_needed`：不读会话正文、不提取经验教训、不评估晋级、retention 或删除；已有 `persist` 意图固定为 `blocked`。纯盘点、目标解析或合法零命中同样用 `not_needed`；discovery 命中 1 个并实际提取单次会话经验教训时仍是 `deep`。

优先级：安全与删除闸门 > scope 能力边界 > scope 内用户显式深度 > 单会话自动改完整复盘的条件。

## 5. 恢复证据

按来源 reference 分三层读：

1. `inventory`：ID、时间、cwd、title、thread kind、pin 和 rollout path。
2. `skim`：真实用户请求、助手交付、工具调用、工具输出、错误和验证结果。
3. `extract`：只为有事实承重的候选形成经验教训。

Codex 的关键边界：

- 真实用户输入只归因于 `event_msg/user_message`。
- 缺失真实用户事件时标 `unavailable`，不从注入的 `response_item.role=user` 补猜。
- 工具调用同时覆盖 `function_call.arguments` 与 `custom_tool_call.input`。
- call 与 output 即使共用 `call_id` 也分别保留；同类型副本去重。
- fork 继承前缀归 parent 一次，不为 child 重复计数；child 新 tail 的用户证据可以另计一次。只有用户明确指定 child 单会话时，parent 前缀才是 `out_of_scope`。
- 用户要求统计整个 fork lineage 的经验教训出现次数、且未限制只看 child 时，统计范围包含 parent 与 child：parent 前缀贡献 parent occurrence，child 新 tail 贡献 child occurrence。
- resume、compaction、重复 meta 和 subagent 不增加独立 occurrence。
- `world_state`、reasoning 和 summary 只用于导航，不能当关键事实的唯一证据。

## 6. 怎么写复盘

轻量复盘固定结构：

```text
一句话结论
1. 目标与明确约束
2. 实际结果与验证状态
3. 关键偏差与有效做法
4. 经验教训（0 至 3 条）
   事实 -> 判断 -> 下次动作 -> 验证方法 -> 适用边界
5. 已产生资产、未完成事项与证据边界
```

没有可复用的经验教训时，写 `not_needed` 和原因。不要为填模板硬造。

完整复盘按 `references/review-contract.md` 写完整经验教训。每项判断必须挂具体事实、证据状态、替代解释、适用边界、action 与 verification。`independent_occurrences` 必须等于去重后的 `occurrence_ids` 数量。ledger 列名仍用 `lesson_scope` 等英文字段。

## 7. 写到哪里

| 内容角色 | Canonical 位置 |
|---|---|
| 历史会话、代表证据、review 状态、删除迁移 | `area/codex-archive-review/ai-sessions/YYYY/YYYY-MM.md` |
| 跨月主题与已完成晋级 | `area/codex-archive-review/ai-sessions/YYYY/YYYY-summary.md` |
| 仍在生效的 AI 协作判断 | `area/ai/` 的已有或明确批准文章 |
| 全局高代价护栏 | 根 `AGENTS.md` |
| 可执行重复流程 | 对应 skill |
| Agent 格式与 parser 事实 | 对应 `references/*.md` |
| 项目专属边界 | repo 本地规则或设计文档 |

根 `AGENTS.md` 的同一条经验教训必须同时满足：真实发生、至少 2 个独立 canonical user session occurrence、代价明确。不同条目不能拆开拼够门槛。

新建正式笔记前先检索 canonical 入口。改已有笔记前把原文读完。月度历史和现役 consumer 分开写，月度历史不是仍生效经验的 SSOT。写进月度稿不等于总结完成，也不等于可以删：应晋级的经验教训还要进入 `area/ai/`、对应 skill 或根规则；明确不必晋级的，在条目里写清原因。

## 8. Retention 与删除

### 8.1 会话证据删除闸门

年龄、`archived=1`、`promoted`、体积过大，都不能单独触发删除。vault 月度稿和本机原始会话是两类对象，问的时候分开说清范围。

只有经验教训已经总结完，才允许进入删除候选：完整复盘完成、应晋级内容已进入现役位置（或条目写明不必晋级）、原始记录不再是唯一证据、年龄为 `mature`、pin 保护已处理。写进月度稿本身不够。

到这一步仍然不删。展示精确 session ID 或文件范围，然后询问用户要不要删，或等待用户明确下令。用户说「以后会删」「太大了」「总结完再删」，只是打开这条路径，不是现在删除。没有询问、没有针对精确范围的明确指令，保持 `retain_raw`。

pinned 会话默认 `retain_raw`。用户按 ID 解除 pin 候选保护后，只能重新评估候选；这一步不等于最终删除授权。

本 skill 不提供默认批量删除命令，也不自行删除来源不明的新文件。从 `deletion_candidate` 进入 `approved`，只能来自这次询问后的明确同意，或用户另行给出的精确范围指令。宽泛的旧授权不能替代。

删除、迁移或删除后验证失败，以及只删除部分 artifact 时，`approved` 立即退回 `retain_raw`。记录已删除项、仍存项和失败原因，重新 inventory 并从删除闸门开始评估；旧批准不复用，新候选仍需新的精确授权。

### 8.2 运行时日志瘦身

`~/.codex/logs_2.sqlite`、`*.sqlite-wal` 这类运行时辅助资产只含 WebSocket / transport 调试遥测，不含会话正文和 Prompt 证据：

- 不受会话 review 流程与 `deletion_candidate` 闸门约束。
- 可用 `codex_runtime_hygiene.py` 检查死页（Freelist），并安全截断日志、VACUUM 瘦身：

```bash
python3 "$AI_SESSION_REVIEW_DIR/scripts/codex_runtime_hygiene.py" --inspect
python3 "$AI_SESSION_REVIEW_DIR/scripts/codex_runtime_hygiene.py" --clean-logs --keep-days 7
```

## 9. 交付

用中文把事情讲完。用户要的是结论，不是字段清单。

正文交代：

1. 这次圈了哪些会话、命中多少、原始记录还在不在。
2. 抽出了哪些经验教训；证据到哪里为止；没有可写的经验教训时说明原因。
3. 写过哪些月度历史或现役笔记；没写就明说没写。
4. 删除有没有发生。经验教训总结完后，可以询问要不要删、删哪一类（月度稿还是本机原始会话），或等明确指令；没有这两件事，不要暗示已经可删。
5. 读不到、对不上、超出范围或本来就不需要处理的项，用中文说清，并在 compact 状态里标 `unavailable` / `rejected` / `out_of_scope` / `not_needed`。

合同状态收在回答末尾的 compact 块里，让 evaluator 和月度 ledger 能读到 `scope_kind`、命中数、`review_depth`、`persistence_intent`、`persistence_status`、`review_status`、`retention_status`。FORCE-QUICK 必须先输出固定状态行。

未运行、未读取或未验证的内容，不得写成已经完成。
