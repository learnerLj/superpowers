# Claude 会话格式与读取方法

Claude 本机历史有三类来源：`~/.claude/transcripts`、项目会话 jsonl、Claude Code session metadata。用户说 Claude、Claude Code、OpenCode 或 Oh My OpenCode 时，三类都要进 inventory。先判断路径和字段，再决定它能提供正文、索引还是状态。

## 1. 存储位置

`~/.claude/transcripts`。OpenCode / Oh My OpenCode 也把会话写在这里。依据：`local-verified`。

```text
~/.claude/transcripts/*.jsonl
```

项目级 Claude Code 会话。依据：`local-verified` + `docs/source-backed`。

```text
~/.claude/projects/*/*.jsonl
~/.claude/projects/*/sessions-index.json
```

Claude-3p / Claude Code session metadata。依据：`local-verified`。

```text
~/Library/Application Support/Claude-3p/claude-code-sessions/**/*.json
```

辅助配置与缓存：

```text
~/.claude/settings.json
~/.claude/config.json
~/.claude/tasks/
~/Library/Application Support/Claude/
```

`Claude/IndexedDB` 和 UI 缓存只在缺少明文 transcript 时探测，默认不作为主会话来源。

## 2. `~/.claude/transcripts/*.jsonl`

inventory 来源名：`claude-transcripts`。2026-01 本机样本里，这里既有「你好」空会话，也有 OpenCode / Oh My OpenCode 的完整工具会话（`type=user|tool_use|tool_result`）。不要因为路径叫 transcripts、不在 `projects/` 下，就整批标成桌面闲聊并跳过。

已见到的形态：

```json
{"type":"user","timestamp":"2026-01-13T14:06:18.786Z","content":"你好"}
```

顶层字段：

| 字段 | 含义 |
|---|---|
| `type` | 已见到 `user`、`tool_use`、`tool_result` |
| `timestamp` | 消息时间。inventory 用事件时间，不用文件 `mtime` |
| `content` | 用户正文；字符串或后续 TASK 包装 |

读取命令：

```bash
python3 "$AI_SESSION_REVIEW_DIR/scripts/local_session_inventory.py" \
  --source claude-transcripts --format jsonl
```

读取策略：

1. `content` 是字符串时，直接抽首条用户请求和后续关键请求。
2. 文件名通常不含可读标题，主题从 `content` 判断。
3. 只含「你好」的单条可以低价值，但必须先出现在 inventory 里；同一批里的 OpenCode 父会话和 `1. TASK:` 子任务不能跟着跳过。
4. 默认 `thread_kind=user`。不要把 transcripts 当成 subagent 藏起来。

## 3. 项目会话：`.claude/projects/*/*.jsonl`

inventory 来源名：`claude-code`。项目会话更接近 Claude Code 工作流记录。目录名称把绝对路径的斜杠（`/`）换成中划线（`-`），例如 `/Users/example/projects/sample-project/` 变成 `-Users-example-projects-sample-project-`。cwd 以 jsonl 记录里的 `cwd` 为准，不要靠解码目录名猜。

会话文件存储有两类结构：
1. **主会话**：`~/.claude/projects/<encoded-project-path>/<session-id>.jsonl`
2. **子代理（Subagent）会话**：`~/.claude/projects/<encoded-project-path>/<session-id>/subagents/<subagent-id>.jsonl`

资料依据：`claude-dev.tools` 描述了主会话格式，本机实测验证了 `subagents` 嵌套子目录的存在。

路径例子：

```text
~/.claude/projects/-Users-example-Documents-knowledge-vault/<session-id>.jsonl
~/.claude/projects/-Users-example-Documents-knowledge-vault/<session-id>/subagents/<subagent-id>.jsonl
```

已见到的顶层字段组合：

| 字段组合 | 含义 | 处理方式 |
|---|---|---|
| `type, operation, timestamp, sessionId, content` | 队列或操作事件 | 辅助判断会话启动、排队或操作状态 |
| `type, operation, timestamp, sessionId` | 无正文操作事件 | 只做状态证据 |
| `parentUuid, isSidechain, attachment, type, uuid, timestamp, userType, entrypoint, cwd, sessionId, version, gitBranch` | 附件或上下文事件 | 提取 cwd、git 分支、sessionId |
| `parentUuid, isSidechain, promptId, type, message, uuid, timestamp, permissionMode, promptSource, userType, entrypoint, cwd, sessionId, version, gitBranch` | 用户或助手消息 | 复盘正文主来源 |

已见到的 `type`：

| `type` | 含义 | 读取价值 |
|---|---|---|
| `user` | 用户消息 | 判断主题和需求 |
| `assistant` | 助手消息 | 抽取结论、操作说明、最终交付 |
| `attachment` | 附件 / 上下文 | 判断输入材料 |
| `last-prompt` | 最近 prompt | 辅助定位主题 |
| `queue-operation` | 队列操作 | 判断运行状态 |

读取命令：

```bash
python3 "$AI_SESSION_REVIEW_DIR/scripts/local_session_inventory.py" \
  --source claude-code --format jsonl
find "$HOME/.claude/projects" -type f -name '*.jsonl' -print
jq -r '.type? // .role? // empty' "$file" | sort | uniq -c
jq -c '{type,timestamp,sessionId,cwd,gitBranch,uuid,parentUuid,userType,entrypoint}' "$file" | head
jq -r 'select(.type=="user") | (.message.content // .message // .content // empty)' "$file"
jq -r 'select(.type=="assistant") | (.message.content // .message // .content // empty)' "$file" | tail -n 80
```

注意：`message` 可能是字符串、对象或数组。读取前先检查：

```bash
jq -c 'select(.message != null) | {type,message_type:(.message|type)}' "$file" | head
```

## 4. 项目索引：`sessions-index.json`

项目目录下可能有：

```text
sessions-index.json
```

已见到顶层字段：

```json
{"version":1,"entries":{...}}
```

读取命令：

```bash
jq '{version, entry_count:(.entries|length)}' "$index"
jq -c '.entries | to_entries[] | {id:.key, value:.value}' "$index" | head
```

读取策略：

1. 用它建立项目级 session 清单。
2. 用 entries 里的时间、标题或路径字段辅助定位正文 jsonl。
3. 不把 index 当作正文来源。

## 5 Claude Code 会话元数据：`Claude-3p/claude-code-sessions/**/*.json`

这类文件是单个 JSON 对象，主要提供状态和索引。

已见到字段：

```json
{
  "sessionId": "local_aee11091-e724-47e3-b4e0-9f489204c017",
  "cliSessionId": "b7190c6d-43f9-4a7b-8376-805e8dfd6348",
  "cwd": "$HOME",
  "originCwd": "$HOME",
  "createdAt": 1779816509952,
  "lastActivityAt": 1779816520325,
  "model": "claude-sonnet-4-6",
  "effort": "high",
  "isArchived": false,
  "title": "Initial greeting session",
  "titleSource": "auto",
  "permissionMode": "acceptEdits",
  "completedTurns": 1
}
```

字段用途：

| 字段 | 用途 |
|---|---|
| `sessionId` | Claude-3p 本地 session ID |
| `cliSessionId` | CLI session ID，可能与项目 transcript 对应 |
| `cwd` / `originCwd` | 项目归类 |
| `createdAt` / `lastActivityAt` | 时间归档 |
| `model` / `effort` | 模型和思考强度 |
| `isArchived` | UI 归档状态 |
| `title` / `titleSource` | 辅助主题判断 |
| `permissionMode` | 执行权限模式 |
| `completedTurns` | 轮次数，只是状态数字 |

读取命令：

```bash
find "$HOME/Library/Application Support/Claude-3p/claude-code-sessions" \
  -type f -name '*.json' -print
jq '{sessionId,cliSessionId,cwd,originCwd,createdAt,lastActivityAt,model,effort,isArchived,title,titleSource,permissionMode,completedTurns}' "$file"
```

读取策略：

1. 这类 JSON 先用于建清单和判断状态。
2. `completedTurns` 不代表正文已经在这个文件里。
3. 需要正文时，回到 `~/.claude/projects/*/*.jsonl` 或 `~/.claude/transcripts/*.jsonl`。

## 6. 判断注意事项

Claude 有多套历史来源。复盘时先跑 `local_session_inventory.py` 的 `claude-code` 与 `claude-transcripts`。`Claude-3p/claude-code-sessions` 只做索引和归档状态，不是正文。`sessions-index.json` 和 `memory/MEMORY.md` 不是会话原文。

项目目录名经过路径编码，例如 `-Users-example-projects-sample-project`。cwd 只取 jsonl 里的 `cwd` 字段；目录名只用于定位文件。

只含问候、短确认或单轮空会话的文件先标低价值，但仍要出现在清单里。含有 cwd、gitBranch、工具执行、长助手输出和多轮用户修正的会话优先进入 skim。

## 7. 资料来源

| 来源 | 用途 |
|---|---|
| `https://claude-dev.tools/docs/jsonl-format` | Claude Code JSONL transcript 路径和字段参考；非 Anthropic 官方文档 |
| 本机 `$HOME/.claude/` 与 `~/Library/Application Support/Claude-3p/` | 路径和字段实测 |
