# AI 会话 Review 与 Retention 合同

这个合同统一定义单会话与多会话复盘、lesson 字段、证据状态、知识晋级和 Raw retention。来源 reference 负责解释数据格式；本文件负责决定复盘结果能写成什么、能落到哪里、能否进入删除候选。

## 1. Scope 与持久化

每次 review 先记录：

| 字段 | 值 | 规则 |
|---|---|---|
| `scope_kind` | `single-session / multi-session` | 由用户目标范围决定 |
| `selected_thread_ids` | 原始精确 ID 集合 | inventory 去重后的选择结果 |
| `canonical_scope_ids` | user root ID 集合 | lineage 归一后的计数权威 |
| `evidence_filter` | subagent / fork tail ID | 只限定可读证据，不增加 occurrence |
| `review_depth` | `quick / deep / not_needed` | 由是否进入正文 review 和任务能力决定 |
| `persistence_intent` | `report-only / persist` | 只由用户是否明确要求写入决定 |
| `persistence_status` | `not_requested / ready / blocked` | 由深度和证据闸门决定 |

`single-session` 恰好包含一个 canonical user session。`multi-session` 可以命中 0、1 或多个 canonical user session；discovery 命中数不改变用户目标 scope。

## 2 Review 深度

每次任务都记录 `review_depth`：

| 深度 | 条件 | 能力边界 |
|---|---|---|
| `quick` | 单会话默认，且没有深度条件 | 最多 3 条 lesson；允许零 lesson；当前回答交付 |
| `deep` | 单会话明确要求或命中深度条件；多会话实际进行 lesson、晋级、retention 或删除评估 | 完整 lesson、occurrence、晋级、retention 与持久化评估 |
| `not_needed` | 纯 inventory、目标解析或合法零命中，没有进入会话正文 review | 只交付清单、解析状态或空结果；不形成 lesson |

深度条件：

1. 用户纠正改变目标、scope、禁止事项或交付结果。
2. 执行失败、中止后未闭合，或关键结果缺少验证。
3. 发生明确返工、时间或资金损失、安全风险、不可逆外部影响。
4. 形成架构、业务、策略或项目边界等重大判断。
5. 原始会话仍是关键事实的唯一证据，或任务涉及归档、晋级、retention、删除评估。

多会话不使用 `quick`。只要读取会话正文并提取 `session-local` 或 `cross-session` lesson，或评估知识晋级、Raw retention、删除候选，就固定为 `deep`。多会话的“轻量”只能限制最终展示篇幅，不能降低内部 review depth。用户明确禁止 `deep` 时，只执行 inventory 和目标解析并使用 `not_needed`；不读取会话正文、不提取 lesson、不评估晋级、Raw retention 或删除。项目或时间 discovery 命中 1 个会话并实际提取 lesson 时仍是 `deep`；合法零命中为 `not_needed`。`review_depth` 不改变 `persistence_intent`。

优先级：安全与删除闸门 > scope 能力边界 > scope 内用户显式 depth > 单会话自动 deep 条件。

`single-session` 用户强制 quick 时：

- 保持 `quick`，列出未深入评估的深度条件。
- `review_status` 最高为 `skimmed`。
- 不晋级 durable lesson、不持久化、不标删除候选。
- 用户同时要求写入时保留 `persistence_intent=persist`，固定 `persistence_status=blocked`。

`multi-session` 用户禁止 deep 且同时要求写入时，保留 `persistence_intent=persist`，固定 `persistence_status=blocked`；结果停在 inventory / target resolution，不能借“先轻量提取”进入正文 review。

## 3. Quick 固定投影

```text
一句话结论
1. 目标与明确约束
2. 实际结果与验证状态
3. 关键偏差与有效做法
4. 经验教训（0 至 3 条）
   事实 -> 判断 -> 下次动作 -> 验证方法 -> 适用边界
5. 已产生资产、未完成事项与证据边界
```

简单、一次成功且结果已验证的会话允许零 lesson。第 4 节写 `not_needed` 和具体原因，不提炼「保持目标清晰」之类无证据泛化。

## 4. Deep Lesson 字段

每条候选 lesson 必须包含：

| 字段 | 类型 | 合同 |
|---|---|---|
| `lesson_scope` | enum | `session-local / cross-session` |
| `category` | enum | `collaboration-pattern / failure-mode / judgment-shift / project-boundary` |
| `value` | enum | `low / medium / high / critical`；不直接决定 retention |
| `trigger` | text | 问题出现的可观察条件 |
| `goal` | text | 用户试图完成的结果 |
| `facts` | list | 每项带 session ID、turn timestamp、evidence type、evidence status 和事实 |
| `outcome_or_cost` | text | 成功、失败、返工、风险或实际代价 |
| `inference` | text | 事实支持的判断 |
| `alternative_explanations` | list | 其他可成立解释；没有时写 `not_needed` |
| `boundary` | text | 项目、环境、版本与时效 |
| `action` | text | 下一次可执行动作 |
| `verification` | text | 证明 action 正确执行的方法 |
| `occurrence_ids` | list | 产生新用户证据的 canonical user session ID |
| `independent_occurrences` | integer | 去重后 `occurrence_ids` 的数量 |
| `destinations` | list | canonical 目标、路径、状态与理由 |
| `evidence_status` | enum | lesson 总体证据状态 |

### 4.1 证据类型

```text
user_message, assistant_message, function_call, custom_tool_call,
tool_output, file, error, result
```

### 4.2 证据状态

| 状态 | 含义 |
|---|---|
| `verified` | 已由可回查事实支持 |
| `rejected` | 候选被反证或不满足合同 |
| `unavailable` | 权威数据缺失或 lineage 无法归因 |
| `out_of_scope` | 证据存在，但不属于用户选定 scope |
| `not_needed` | 合法空结果或无需该字段 |

`facts` 的固定列表形式：

```text
session ID · turn timestamp · evidence type · evidence status · fact
```

月度文件不记录原始绝对路径。

## 5. Occurrence 合同

1. `session-local` 的已验证 lesson 使用 1 个 canonical user session occurrence。
2. 无法归因的候选使用空 `occurrence_ids` 和 `independent_occurrences=0`。
3. `cross-session` 至少包含 2 个不同 canonical user session ID。
4. 同一会话内多次重复只算 1 个 occurrence。
5. resume、compaction、重复 meta、fork 继承前缀和 subagent 不增加 occurrence。
6. fork child 新 tail 中产生的新用户证据可以归 child；指定 child 的单会话 review 不把 parent 前缀计入当前 scope。
7. `independent_occurrences` 必须等于 `occurrence_ids` 去重后的数量。

多会话只命中一个会话时，可以形成 `session-local` lesson，同时把跨会话模式标为证据不足。合法零命中时不创建 lesson，跨会话判断为 `not_needed`。

## 6. Destination 合同

每个 destination 固定包含：

| 字段 | 值 |
|---|---|
| `destination_type` | `session-history / area / AGENTS / skill / repo-doc` |
| `path` | canonical 路径 |
| `promotion_status` | `planned / promoted / rejected / not_needed` |
| `reason` | 晋级或拒绝理由 |

路由：

| 内容角色 | Canonical consumer |
|---|---|
| 历史会话、代表证据、review 进度、删除迁移 | `area/codex-archive-review/ai-sessions/YYYY/YYYY-MM.md` |
| 跨月主题和已完成晋级 | `area/codex-archive-review/ai-sessions/YYYY/YYYY-summary.md` |
| 仍在生效的 AI 协作判断 | `area/ai/` 的已有或明确批准文章 |
| 全局高代价护栏 | 根 `AGENTS.md` |
| 可执行重复流程 | 对应 skill |
| Agent 格式与 parser 事实 | 来源 reference |
| 项目专属边界 | repo 本地规则或设计文档 |

根 `AGENTS.md` 的同一 lesson 必须同时满足：

1. 真实发生。
2. 至少 2 个独立 canonical user session occurrence。
3. 代价明确。

不同 lesson 的 occurrence 与代价不能拼接成一条根规则。单会话可以晋级项目事实、skill 流程、parser reference 或已有 / 明确批准的 `area/ai/` 文章，但必须保留单次证据边界。

### 6.1 Skill Audit 候选衔接

`skill-effectiveness-audit` 的 finding 是 report-only 投影，不直接进入本合同的 canonical lesson schema。只有 finding 同时具备可定位行为事实、实际代价、替代解释、正确 owner 和验证动作时，才可形成 lesson 候选；仍需重新通过本合同的 scope、occurrence、destination 与 persistence 门槛。

静态 maintenance finding 只能支持路径、命令、scope 或 validator 维护，不得写成 skill 行为无效。`recommendation_status=proposed` 不代表已经晋级、修改或持久化。

## 7. Review 与 Retention 状态机

Review 进度：

```text
candidate -> skimmed -> extracted -> promoted
```

Raw retention：

```text
unassessed -> retain_raw
unassessed -> deletion_candidate -> approved -> deleted
retain_raw -> deletion_candidate
deletion_candidate -> retain_raw
approved -> retain_raw
```

两个状态机独立。`promoted`、`archived=1` 和 `mature` 都不能单独改变 retention。

旧状态读取映射：

| 旧值 | 新值 | 条件 |
|---|---|---|
| `candidate` | `review_status=candidate` | 直接映射 |
| `skimmed` | `review_status=skimmed` | 直接映射 |
| `summarized` | `review_status=extracted` | 摘要含可回查事实；否则退回 `skimmed` |
| `migrated` | `review_status=promoted` | 已记录 canonical consumer；否则为 `extracted` |
| `deletable` | `retention_status=deletion_candidate` | 重新通过当前全部删除闸门 |

## 8. 删除闸门

只有全部满足才可标记 `deletion_candidate`：

1. `review_status` 至少为 `extracted`。
2. 关键错误、结果、判断变化和有效方法已有证据。
3. 应晋级内容已经进入 canonical consumer，并记录目标。
4. 原始会话不再是关键断言的唯一证据；否则 `retain_raw`。
5. 已记录删除后失去的内容和保留边界。
6. 年龄为 `mature`。
7. `is_pinned` 不为真，或用户已在看到 pin 状态后按 ID 解除候选保护。

pinned 会话先进入 `retain_raw`。解除 pin 候选保护只触发重新评估，不等于最终删除授权。

候选清单生成后，用户必须再次明确批准精确 session ID 或文件范围，才能进入 `approved`。宽泛的旧授权不能替代这一步。skill 不提供默认批量删除命令。

删除、迁移或删除后验证失败，以及只删除部分 artifact 时，`approved -> retain_raw`。记录已删除项、仍存项和原始错误，重新 inventory 并从全部删除闸门开始评估。执行后的 artifact 集合已经改变，原批准不能用于重试；重新形成候选后必须再次取得精确授权。

## 9. Raw 保留与迁移

关键断言仍只存在于原始 JSONL 时，维持 `retain_raw`。只有用户另行批准证据迁移后，才可把不可替代的大体积 Raw 写入与 vault 平行的：

```text
obsidian_raw_reference/ai-sessions/
```

详细迁移 manifest 固定写入 vault 外的：

```text
obsidian_raw_reference/ai-sessions/migration-manifest.jsonl
```

每条 manifest 至少包含：

```text
migration_id, session_id, source_path, source_sha256,
destination_path, destination_sha256, evidence_consumer,
migrated_at, migration_status, deleted_artifacts,
remaining_artifacts, last_error
```

`source_path` 与 `destination_path` 是执行时核验过的绝对路径，只存在于 vault 外的 manifest。源、目标 SHA-256 必须分别记录并相等后，迁移才是 `verified`。

月度 archive 只写可迁移 locator：

```text
migration_id, session_id, manifest_ref,
source_root, source_relpath,
destination_root, destination_relpath,
sha256, migration_status
```

`source_root=codex-home` 解析为当前 `$CODEX_HOME` 或 `~/.codex`；`destination_root=obsidian-raw-reference` 解析为当前 vault 的平行 Raw 根。相对路径不能包含 `..`。执行删除前，用 root + relpath 解析绝对目标，并与 manifest 的绝对路径、session ID 和 SHA-256 交叉核对。

迁移不由 review 自动触发。迁移、删除或验证失败，以及证据消费者失效时，状态回到 `retain_raw`。

## 10. 月度 Lesson 与 Ledger

每条 deep lesson 使用：

```markdown
### N.N Lesson 标题

| 字段 | 内容 |
|---|---|
| `lesson_scope` |  |
| `category` |  |
| `value` |  |
| `trigger` |  |
| `goal` |  |
| `outcome_or_cost` |  |
| `inference` |  |
| `alternative_explanations` |  |
| `boundary` |  |
| `action` |  |
| `verification` |  |
| `occurrence_ids` |  |
| `independent_occurrences` |  |
| `destinations` |  |
| `evidence_status` |  |

#### N.N.N 证据

- `session ID · turn timestamp · evidence type · evidence status`：fact
```

Session retention ledger 固定字段：

```text
session_id, source, review_status, retention_status, age_bucket,
is_pinned, promoted_to, decision_basis, reviewed_at
```

`promoted_to` 可以记录多个 consumer；没有晋级时写 `not_needed` 并说明原因。年度总结只汇总跨月主题和已完成晋级，不复制 session 级 ledger。
