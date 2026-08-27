# Codex 会话格式与读取合同

本 reference 记录 2026-07-31 在本机验证的 Codex CLI / Desktop 数据结构。`state_5.sqlite` 负责发现会话，rollout JSONL 负责恢复正文证据；两者不能互相替代。

## 1. 权威数据源

| 数据 | 位置 | 作用 | 依据 |
|---|---|---|---|
| 活跃 rollout | `~/.codex/sessions/` | 用户消息、助手消息、工具事件、结果与 lineage | `local-verified` |
| 已归档 rollout | `~/.codex/archived_sessions/` | 已归档会话的同类原始事件 | `local-verified` |
| Desktop state DB | `~/.codex/state_5.sqlite` | thread 清单、最后活动、pin、archive、rollout path、spawn edge | `local-verified` |
| 轻量索引 | `~/.codex/session_index.jsonl` | 标题与更新时间的次级索引 | `local-verified` |

旧的 `~/Library/Application Support/com.openai.chat/` 中 `codex-taskItems-*` / `codex-taskDetails-*` 路径在本机未发现，不能继续作为 Desktop 清单入口。依据：`local-verified-absent`。

## 2. Inventory 脚本

```bash
AI_SESSION_REVIEW_DIR="${AI_SESSION_REVIEW_DIR:-$HOME/.agents/skills/superpowers/ai-session-review}"
python3 "$AI_SESSION_REVIEW_DIR/scripts/codex_session_inventory.py" --help
```

脚本在复制前后核对显式 `--db` 或默认 `~/.codex/state_5.sqlite` 及现有 WAL / SHM 的 inode、size、mtime、ctime 和 SHA-256。任一文件变化时丢弃该次副本并重试；稳定后只把 DB 与 WAL 复制到权限隔离的临时目录，让 SQLite 在临时目录重建 SHM，再以 read-only URI 打开快照。它只读取 `threads`，不读取 JSONL 正文，不改动源 DB 或 sidecar，不创建写事务或持久化副本；进程退出时清理临时快照。

`threads` 的必需字段：

```text
id, title, cwd, rollout_path, created_at_ms, recency_at_ms,
archived, is_pinned, thread_source, source, model
```

缺少字段时脚本列出全部缺失列并失败。`source` 可以是普通字符串，也可以是 JSON 字符串；顶层含 `subagent` 的 JSON 对象优先归为 subagent。

`thread_kind` 的顺序：

1. `thread_source=subagent` 或 `source` 顶层含 `subagent` -> `subagent`。
2. `thread_source=user` 或 `source=cli/vscode` -> `user`。
3. 其他 -> `other`。

默认只输出 user。`--include-subagents` 加入 subagent，仍排除 other。完整筛选参数和输出字段以脚本 `--help` 为准。

## 3. 时间语义

`created_at_ms` 只表示创建时间；清理年龄使用 `recency_at_ms`。文件 `mtime` 会被 resume、迁移或复制改变，不能判断会话年龄。

| age bucket | 条件 |
|---|---|
| `active` | `age < 7d` |
| `cooling` | `7d <= age < 30d` |
| `mature` | `age >= 30d` |

未来 `recency_at_ms` 仍是 `active`，脚本同时写 `stderr` 警告。`--older-than` 使用严格小于；`--newer-than` 使用大于等于。`1m` 是日历月，`30d` 是固定 30 天。

月度 inventory 只生成宽候选：

```text
created_at_ms < month_end AND recency_at_ms >= month_start
```

最终月度归属必须回到 JSONL 的实际 turn 时间。一个会话五月创建、六月有 turn、七月 resume 时，六月 inventory 应命中，但只提取六月 turn。

## 4. 精确目标解析

当前 task：

1. 从当前 task 的 `session_meta.payload.id` 或 Desktop metadata 取得 ID。
2. 使用 `--id <SESSION_ID>` 精确查询。
3. 无法可靠取得时只列最近候选，不改成全历史扫描。

rollout path：

1. 读取文件首条 `session_meta.payload.id`。
2. 与 `threads.id`、`threads.rollout_path` 和文件名交叉核对。
3. 不一致时标 `unavailable`，不猜测 ID。

多个 `--id` 先去重。任一 ID 缺失、为 other，或 subagent 未显式允许时整次失败，不返回部分结果。

## 5. JSONL 顶层事件

每行是一个 JSON 对象：

```json
{"timestamp":"...","type":"response_item","payload":{}}
```

当前已见顶层类型包括：

| `type` | 用途 | 证据边界 |
|---|---|---|
| `session_meta` | `id`、`cwd`、`source`、fork / parent metadata | 会重复；先归 lineage |
| `turn_context` | `turn_id`、时间、cwd、model、summary | summary 只用于导航 |
| `event_msg` | 真实用户事件、turn 状态、进度事件 | 只有 `user_message` 归因给用户 |
| `response_item` | 助手消息、工具 call / output、组装上下文 | `role=user` 不是用户身份边界 |
| `world_state` | 运行时状态 | 不作为关键事实唯一证据 |
| `compacted` | 压缩上下文 | 不创建 occurrence |
| `inter_agent_communication_metadata` | agent 路由与通信元数据 | 只用于执行路由；不形成用户消息或 occurrence |

`session_meta` 会因 resume、fork 和复制历史重复出现。不要按 meta 数量统计会话或 lesson。

## 6. 真实用户消息

唯一可归因给用户的首选结构：

```jq
select(.type == "event_msg" and .payload.type == "user_message")
| {timestamp, message: .payload.message}
```

`response_item.payload.role == "user"` 是组装后的模型输入，可能同时含真实请求、`AGENTS.md`、environment、developer 指令和自动展开的 skill。它只能作上下文或重复副本核对，不能恢复用户原话、长期偏好或独立 occurrence。

目标 turn 缺少 `event_msg/user_message` 时：

- 用户请求与偏好标 `unavailable`。
- 助手消息、工具调用、工具输出和文件结果仍可支持「执行观察」。
- 不从助手行为或注入内容反推用户意图。

## 7. 工具与结果

`response_item.payload` 当前同时存在：

| subtype | 输入 / 输出字段 |
|---|---|
| `function_call` | `name`、`arguments`、`call_id` |
| `custom_tool_call` | `name`、`input`、`call_id` |
| `function_call_output` | `output`、`call_id` |
| `custom_tool_call_output` | `output`、`call_id` |

事件去重键必须含顶层 `type`、payload subtype 和稳定 ID。工具事件使用：

```text
top-level type + payload subtype + call_id
```

call 与 output 共用 `call_id` 时分别保留；同 subtype 的复制副本只留一条。没有稳定 ID 时使用：

```text
timestamp + top-level type + payload subtype + normalized payload SHA-256
```

认证字段只记录「存在认证配置」。token、cookie、OAuth、API key、access key、private key、PAT、auth、password、secret、credential、URI userinfo 和敏感 query value 都必须脱敏；key 判定不依赖大小写、snake_case、kebab-case、camelCase 或无分隔符写法。

## 8 User Fork 继承关系

物理 rollout 的当前 ID 取首条 `session_meta.payload.id`，并与文件名和 `threads.id` 交叉核对。

1. 当前 ID 的首条 `forked_from_id` 建立 user fork 边。
2. 扫描 JSONL 时，`session_meta.payload.id` 切换后续 segment 的归属。
3. 属于祖先 ID 的复制 segment 是继承前缀，只归祖先一次。
4. 切回当前 ID 后的新 tail 才能为 child 形成新 occurrence。
5. resume 保持同一 ID；重复 meta、compaction、summary、reasoning 和 world state 都不增加 occurrence。

单会话指定 fork child 时，parent 前缀只作 `out_of_scope` 上下文。child tail 没有新的可归因用户证据时，候选使用空 `occurrence_ids`、`independent_occurrences=0` 和 `evidence_status=unavailable`。

## 9 Subagent 继承关系

`thread_spawn_edges` 当前 schema：

```text
parent_thread_id, child_thread_id, status
```

对每个显式 selected subagent 逐跳递归：

1. immediate parent 优先取 `thread_spawn_edges`。
2. 与 child 的 `session_meta.payload.parent_thread_id` 或 `source.subagent.thread_spawn.parent_thread_id` 交叉核对。
3. parent kind 为 subagent 时继续；为 user 时写入 `canonical_scope_ids` 并终止。
4. 路径上的 subagent ID 只写入 `evidence_filter`。
5. 缺失 parent、多个 parent、来源冲突、parent kind 为 other 或循环时，整条 lineage 标 `unavailable`。

不按 cwd、标题或时间相近猜测 parent。多个 subagent leaf 指向同一 user root 时，inventory 保留多个 `selected_thread_ids`，review 只保留一个 canonical user occurrence。

## 10. 证据读取顺序

```text
state_5.sqlite inventory
-> rollout_path
-> event_msg/user_message
-> assistant response_item
-> function/custom tool call and output
-> turn result / error / file evidence
-> fork and subagent lineage normalization
-> lesson candidate
```

summary、reasoning、compacted message 和 world state 可以帮助导航长会话，但不能成为关键结论的唯一证据。

## 11. 受限 JSONL Fallback

仅当 `state_5.sqlite` 缺失、无法只读打开或 `threads` schema 漂移时，才使用 JSONL fallback。它只恢复指定会话的身份与正文证据，不提供 Desktop inventory 的等价替代。

按以下优先级限定范围：

1. 用户给出的精确 rollout path。
2. 已知的 `~/.codex/sessions/YYYY/MM/` 目录或已归档目录中的精确文件。
3. 精确 session ID；只在 `~/.codex/sessions/` 和 `~/.codex/archived_sessions/` 内用 `rg` 找候选，再用首条 `session_meta.payload.id` 验证。

不要递归扫描项目树、整个 home 或其他 Agent 目录。已知文件时，先读取身份和真实用户消息：

```bash
ROLLOUT="/absolute/path/to/rollout.jsonl"

jq -c 'select(.type == "session_meta") | .payload' "$ROLLOUT" | sed -n '1p'
jq -c 'select(.type == "event_msg" and .payload.type == "user_message") |
  {timestamp, message: .payload.message}' "$ROLLOUT"
```

只有精确 ID 时，先生成受限候选，再逐个核对首条 meta；ID 出现在 parent、spawn edge 或注入上下文中不算命中：

```bash
SESSION_ID="01900000-0000-7000-8000-000000000000"

rg -l --glob '*.jsonl' --fixed-strings "$SESSION_ID" \
  "$HOME/.codex/sessions" "$HOME/.codex/archived_sessions" |
while IFS= read -r rollout; do
  first_id=$(jq -r 'select(.type == "session_meta") | .payload.id' "$rollout" |
    sed -n '1p')
  if [ "$first_id" = "$SESSION_ID" ]; then
    printf '%s\n' "$rollout"
  fi
done
```

fallback 结果必须显式降级：

- `is_pinned=unavailable`
- Desktop `archived=unavailable`
- `recency_at_ms=unavailable`
- 只根据文件所在目录记录 `raw_location=active / archived`，不能把它改写成 Desktop archive 状态

这些结果可以支持指定会话的 quick / deep review，但不能用于年龄清理、pin 保护判断或生成 `deletion_candidate`。恢复 state DB inventory 后才能重新评估 retention 和删除。

## 12. 运行时日志与 SQLite 瘦身 (Runtime Logs & Hygiene)

Codex 在长期运行中，除会话 JSONL 外，会在 `~/.codex/logs_2.sqlite` 中记录大量内部 transport、WebSocket 和 telemetry 调试日志（表名 `logs`，字段 `id`, `ts`, `level`, `target`, `feedback_log_body`）。

### 12.1 膨胀机理与性质边界

1. **Freelist 碎片膨胀**：Codex 虽会在内部按条数/时间自动删除旧日志记录，但 SQLite 默认在 WAL 模式下**不会将空闲页归还操作系统**，而是保留在内部 `freelist`。历史高频交互会导致 `logs_2.sqlite` 产生数 GB 的纯空闲死页。
2. **辅助资产性质**：`logs_2.sqlite` 纯属客户端内部运行日志，**不包含任何会话正文、消息历史、Prompt 规则或 memories**。清理或截断 `logs` 表不破坏任何会话可追溯证据。
3. **文件锁边界**：活跃的 `codex` 进程会持有 `logs_2.sqlite` 的打开句柄。在进程退出或通过脚本安全检查后，执行 `VACUUM` 与 WAL Checkpoint 即可释放空间。

### 12.2 盘点与清理命令

使用 `codex_runtime_hygiene.py`：

```bash
AI_SESSION_REVIEW_DIR="${AI_SESSION_REVIEW_DIR:-$HOME/.agents/skills/superpowers/ai-session-review}"

# 1. 盘点当前 logs 碎片、活跃句柄与会话资产体积
python3 "$AI_SESSION_REVIEW_DIR/scripts/codex_runtime_hygiene.py" --inspect

# 2. 清理旧日志并执行 VACUUM 释放磁盘（默认保留最近 7 天日志）
python3 "$AI_SESSION_REVIEW_DIR/scripts/codex_runtime_hygiene.py" --clean-logs --keep-days 7
```
