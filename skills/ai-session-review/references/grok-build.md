# Grok Build 本地会话格式与读取合同

Grok Build 把 TUI、headless 和 ACP 会话持久化到本机。`summary.json` 负责 inventory，`updates.jsonl` 负责恢复用户消息、助手消息、工具调用与结果。

## 1 权威路径

默认根目录是 `~/.grok`；设置 `GROK_HOME` 时使用实际值，不同时扫描默认根和覆盖根。

```text
~/.grok/sessions/<encoded-cwd>/<session-id>/
  summary.json
  updates.jsonl
  chat_history.jsonl
  plan.json
  rewind_points.jsonl
  signals.json
  subagents/
```

长 cwd 可能改用 slug + hash，原 cwd 记录在分组目录的 `.cwd`。优先读取 `summary.json.info.cwd`，缺失时才读取 `.cwd`，不得只按 URL 解码猜路径。

| 文件 | 用途 | 证据边界 |
|---|---|---|
| `summary.json` | ID、cwd、标题、时间、model、session kind、parent | inventory authority，不替代正文 |
| `updates.jsonl` | ACP session update stream | 正文与工具执行 authority |
| `chat_history.jsonl` | 发给模型的原始 history | 含 system、synthetic user、compaction 内容，不直接归因给用户 |
| `plan.json`、`signals.json` | 计划与计数状态 | 只作辅助证据 |
| `compaction/`、`compaction_checkpoints/` | 压缩过程与快照 | 不增加 occurrence |

## 2 会话清单

```bash
AI_SESSION_REVIEW_DIR="${AI_SESSION_REVIEW_DIR:-$HOME/.agents/skills/superpowers/ai-session-review}"
python3 "$AI_SESSION_REVIEW_DIR/scripts/local_session_inventory.py" \
  --source grok-build --format jsonl
```

`session_kind=subagent` 和 `subagent_resume` 都归为 `thread_kind=subagent`。默认排除，只有用户指定 subagent 或 lineage 时才加 `--include-subagents`。

`created_at` 与 `last_active_at` / `updated_at` 负责时间筛选。缺失时标 `unavailable`，不用 session 目录或文件 `mtime` 填补。

`updates.jsonl` 必须至少含一条可识别的 `session/update` canonical 事件，且不能混有 malformed 行。文件为空、只有未知结构或部分损坏时保留 inventory row 并标 `evidence_status=unavailable`。

## 3 正文恢复

逐行读取 `updates.jsonl`：

| `params.update.sessionUpdate` | 归因 |
|---|---|
| `user_message_chunk` | 可归因用户输入；同一 prompt 的分块先按顺序合并 |
| `agent_message_chunk` | 助手可见回复 |
| `agent_thought_chunk` | 内部推理，只作导航，不作为关键事实唯一证据 |
| `tool_call` | 工具调用 |
| `tool_call_update` | 工具进度或结果；按 `toolCallId` 与 subtype 去重 |
| `plan` | 计划状态，不是用户消息 |
| `turn_completed` | turn 结果、stop reason 与 usage |

`chat_history.jsonl` 中的 `type=user` 可能是 synthetic context、工具响应或压缩重建内容。只有 `updates.jsonl` 的 `user_message_chunk` 能直接归因给用户；两者不一致时保留冲突并以 update stream 为正文 authority。

## 4 Lineage 与远端结果

1. `summary.json.info.id` 必须与 session 目录名交叉核对；冲突时标 `unavailable`。
2. fork / restore 使用 `parent_session_id` 建 lineage。继承前缀只归 parent 一次，child 新 prompt 才能形成 child occurrence。
3. subagent metadata 只能建立 evidence filter，不自动增加 canonical user occurrence。
4. `grok sessions search` 可混合本地索引与 remote results。本 skill 只接受能映射到本机 session 目录和 `updates.jsonl` 的结果；remote-only row 标 `out_of_scope`。
5. Grok Build 可接续其他产品的会话。无法证明同一稳定 conversation ID 时，不把标题、时间或相似内容当作去重依据。

## 5 安全与删除

不要读取或输出 `~/.grok/auth.json`、API key、OAuth token、Cookie 或 managed credential。标题和工具输入沿用 inventory 的认证值脱敏。

`grok sessions delete <id>` 和应用内 `/delete` 都是永久删除入口。只有通过主 skill 的 deep review、retention 与精确 ID 二次授权后才能执行；目录里存在多个 sidecar，部分删除或验证失败立即回退为 `retain_raw`。

## 6 依据

- 本机 Grok Build `1.0.5` 的 `~/.grok/docs/user-guide/17-sessions.md`。
- 本机 `~/.grok/sessions/*/*/{summary.json,updates.jsonl,chat_history.jsonl}` 字段实测，采样时间 `2026-08-19`。
