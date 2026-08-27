# Antigravity 本地会话格式与读取合同

Antigravity Desktop 与 Antigravity CLI 都把明文 agent transcript 放在各自的 `brain/<session-id>` 下。CLI 的 `history.jsonl` 只记录终端输入历史，不是 canonical conversation。

## 1 权威路径

```text
~/.gemini/antigravity/brain/<session-id>/.system_generated/logs/transcript.jsonl
~/.gemini/antigravity-cli/brain/<session-id>/.system_generated/logs/transcript.jsonl
```

| 来源写法 | 路径 |
|---|---|
| `antigravity-desktop` | `~/.gemini/antigravity/brain/.../transcript.jsonl` |
| `antigravity-cli` | `~/.gemini/antigravity-cli/brain/.../transcript.jsonl` |

session ID 取 `brain/` 的直接子目录名。过滤 `tempmediaStorage` 等非 session 目录，并要求目标文件精确位于 `.system_generated/logs/`。

## 2 Transcript 结构

当前明文 JSONL 每行包含 `step_index`、`source`、`type`、`status`、`created_at`，再按事件带 `content`、`thinking`、`tool_calls` 或结果字段。

| `type` | 读取策略 |
|---|---|
| `USER_INPUT` | 真实用户输入首选来源 |
| `CONVERSATION_HISTORY` | 组装上下文，只作重复核对 |
| `PLANNER_RESPONSE` | 助手规划与工具意图；thinking 不作关键事实唯一证据 |
| 工具事件 | 结合 `step_index`、tool call 和结果恢复执行证据 |

标题使用第一条 `USER_INPUT.content`。时间窗口使用事件 `created_at`；缺失时标 `unavailable`，不用 transcript `mtime` 补齐。当前 transcript 未稳定提供 cwd 时保持 `null`，不按相邻项目、日志或标题猜测。

transcript 必须至少含一条具备 `step_index`、`source` 和非空 `type` 的 canonical record，且不能混有 malformed 行。空文件、`{}` 或部分损坏都标 `evidence_status=unavailable`。

## 3 会话清单

```bash
AI_SESSION_REVIEW_DIR="${AI_SESSION_REVIEW_DIR:-$HOME/.agents/skills/superpowers/ai-session-review}"
python3 "$AI_SESSION_REVIEW_DIR/scripts/local_session_inventory.py" \
  --source antigravity-desktop --format jsonl

python3 "$AI_SESSION_REVIEW_DIR/scripts/local_session_inventory.py" \
  --source antigravity-cli --format jsonl
```

## 4 非正文路径

以下路径不进入 canonical session inventory：

- `~/.gemini/antigravity-cli/history.jsonl`：prompt / command history，只作 locator。
- `~/.gemini/antigravity-cli/cache/`、`log/`：管理缓存与运行日志。
- `~/.gemini/antigravity-cli/conversations/*.pb`：未解析的 Protobuf 备份。
- `~/Library/Application Support/Antigravity/`：IDE 状态、cloudcode / artifacts / tasks 日志。
- `GPUCache/`、`DawnGraphiteCache/`、`Crashpad/`、`CacheStorage/`：渲染或崩溃缓存。

只有 locator 命中、正文缺失时标 `unavailable`，不从 `history.jsonl` 或 protobuf 补造对话结果。

## 5 Lineage 与删除

当前本机 transcript 没有经过验证的统一 parent 字段。没有稳定 lineage 时，每个 brain ID 独立保留，但不得仅因 assistant 或 subagent 复述就增加 lesson occurrence。

删除必须以精确 transcript 或 session 目录为候选，并经过主 skill 的 retention 与二次授权。CLI history、cache、protobuf 和 Desktop brain 不属于同一个隐式删除范围。

## 6 依据

- 本机 Desktop brain 与 CLI brain 的 `transcript.jsonl` 字段实测，采样时间 `2026-08-19`。
- 本机同时存在两套 brain；旧规则只读取 CLI `history.jsonl` 会漏掉真实 CLI conversation。
