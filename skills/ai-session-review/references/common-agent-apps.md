# 常见 Agent 应用会话探测

这份 reference 处理 Codex、Claude、Antigravity 之外的常见 agent 应用。先找明文 transcript、项目索引和状态库；只看到缓存或配置时，只标成线索。

## 1. 通用探测顺序

按这个顺序查。先使用 `$HOME`，不要写死具体用户名。

1. 用户主目录下的隐藏目录，例如 `~/.cursor`、`~/.continue`、`~/.roo`、`~/.cline`。
2. 当前项目下的隐藏目录，例如 `.cursor/`、`.continue/`、`.roo/`、`.windsurf/`、`.aider-desk/`。
3. macOS app 支持目录，例如 `~/Library/Application Support/Cursor`。
4. VS Code / Electron 状态库，例如 `User/globalStorage/state.vscdb`、`User/workspaceStorage/*/state.vscdb`。
5. logs 目录、History 目录、workspace state。
6. Cache、GPUCache、Code Cache 只在缺少其他线索时扫关键字。

通用命令：

```bash
find "$HOME" -maxdepth 3 \( -path "$HOME/Library" -prune -o -type d \( \
  -iname '.cursor' -o -iname '.continue' -o -iname '.roo*' -o -iname '.cline' -o -iname '.windsurf' \
  -o -iname '.aider*' \
\) -print \)

find "$HOME/Library/Application Support" -maxdepth 2 -type d \( \
  -iname '*Cursor*' -o -iname '*Windsurf*' -o -iname '*Continue*' -o -iname '*Cline*' -o -iname '*Roo*' \
  -o -iname '*Trae*' -o -iname '*Aider*' \
\) -print
```

## 2. 本机已见路径

| 应用 / 工具 | 已见路径 | 读取策略 |
|---|---|---|
| Cursor | `~/.cursor/` | 优先看 `chats/`、`projects/<encoded-path>/agent-transcripts/<session-id>/` 下的主会话 `.jsonl` 与 `subagents/` 子代理会话；路径依据为 `local-verified`。编码目录名如 `Users-example-projects-sample-project`。 |
| Cursor app | `~/Library/Application Support/Cursor/` | 按 VS Code / Electron 状态库探测；路径依据为 `local-verified` |
| Continue | `~/.continue/sessions/`、项目 `.continue/` | 优先找 `sessions.json` 和 `<uuid>.json`；路径依据为 `docs/source-backed`，本机当前只验证目录存在性 |
| Cline | `~/.cline/data/`、`~/.cline/data/tasks/taskHistory.json`、`~/.cline/data/tasks/<id>/api_conversation_history.json` | 优先读任务索引和单任务对话；路径依据为 `docs/source-backed`，本机当前只验证 `~/.cline/` 目录存在性 |
| Roo Code | `~/.roo/`、项目 `.roo/` | 当前只验证目录存在性；公开来源未确认 transcript 路径，按 `unknown-probe` 探测 |
| Windsurf / Cascade | 项目 `.windsurf/` | 当前只验证项目目录存在性；Firecrawl 搜索未找到可靠本地 transcript 文档，按 `unknown-probe` 探测 |
| Aider Desk | `~/.aider-desk/`、项目 `.aider-desk/` | 当前只验证目录存在性；无会话文件样本时不写正文复盘 |
| CodexBar | `~/.codexbar/`、`~/Library/Application Support/CodexBar/` | 只作为 Codex 管理器线索 |
| OpenAI / Codex app | `~/Library/Application Support/OpenAI/Codex`、`~/Library/Application Support/Codex`、`~/Library/Application Support/com.openai.codex` | 与 Codex Desktop 元数据交叉验证 |

资料分级：

| 等级 | 含义 |
|---|---|
| `local-verified` | 已在本机看到路径或字段 |
| `docs/source-backed` | 文档、源码说明或带源码引用的资料支持 |
| `community-reference` | 社区文章或论坛经验，可辅助探测 |
| `unknown-probe` | 只按通用 VS Code / Electron 目录规律探测 |

Continue 的 `~/.continue/sessions/` 来自 DeepWiki 对 Continue 源码的索引说明，页面引用 `core/util/history.ts`。Cline 的 `~/.cline/data/` 来自官方仓库 `.clinerules/storage.md`，单任务对话路径来自 `openDiskConversationHistory.ts`。Cursor 的 `~/.cursor/chats/`、`~/.cursor/projects/*/agent-transcripts/` 和 Cursor `state.vscdb` 来自社区逆向文章，按 `community-reference` 使用。

## 3. Cline 读取口径

Cline 的公开源码说明采用 file-backed JSON stores：

```text
~/.cline/data/globalState.json
~/.cline/data/secrets.json
~/.cline/data/tasks/taskHistory.json
~/.cline/data/tasks/<task-id>/api_conversation_history.json
~/.cline/data/workspaces/<hash>/workspaceState.json
```

读取命令：

```bash
find "$HOME/.cline/data" -maxdepth 4 -type f -print
jq 'if type=="object" then keys_unsorted else type end' "$HOME/.cline/data/tasks/taskHistory.json"
jq '.[0] // .messages?[0] // keys_unsorted' "$HOME/.cline/data/tasks/<task-id>/api_conversation_history.json"
```

读取策略：

1. `taskHistory.json` 用来建立任务清单、时间和标题。
2. `api_conversation_history.json` 才是单任务对话候选。
3. `secrets.json` 不展开 value，只记录存在认证配置。
4. 旧版 VS Code 扩展可能还在 VS Code global storage 里留有 legacy task；没有 `~/.cline/data/` 时再按扩展状态库探测。

## 4. 常见文件形态

| 形态 | 识别方式 | 读取策略 |
|---|---|---|
| `*.jsonl` | 一行一个 JSON 对象 | 先看顶层 keys，再按 role/type/message/content 抽取 |
| `*.json` | 单个 JSON 对象或数组 | 先看顶层 keys、数组长度、是否有 session/title/cwd/messages |
| SQLite `state.vscdb` | `ItemTable(key,value)` | 查 key 分布，再挑 chat、history、agent、task 相关 key |
| logs | `*.log` 文本 | 只做运行线索，除非含明文 prompt / response |
| History | 编辑器历史目录 | 辅助判断文件和 workspace，不直接当会话 |
| Cache / Code Cache / GPUCache | 缓存文件 | 默认跳过 |

通用格式探测：

```bash
# jsonl 顶层 key
head -n 5 "$file" | jq -r 'keys_unsorted | @json'

# jsonl 类型分布
jq -r '.type? // .role? // .event? // empty' "$file" | sort | uniq -c

# json 顶层形态
jq 'if type=="object" then keys_unsorted elif type=="array" then {array_length:length, first:(.[0] // null)} else type end' "$file"

# SQLite key 分布
sqlite3 "$db" 'select key, length(value) from ItemTable order by length(value) desc limit 80;'
```

## 5. 判断正文来源

优先级：

1. 明文 `user` / `assistant` / `message` / `content` / `messages` 字段。
2. session index 中可定位到的会话文件。
3. project / workspace state 中的 cwd、title、timestamp。
4. logs 中的请求、traceId、错误和 artifact 线索。
5. 缓存目录里的关键词命中。

只在第 1 或第 2 层成立时写会话内容复盘。第 3 到第 5 层只能写运行线索、项目线索或待深挖项。

## 6. 月度归档口径

整理这些应用时，月度复盘表格的 `来源` 可以写：

| 来源写法 | 适用情况 |
|---|---|
| `cursor` | Cursor 明文会话或项目级历史 |
| `continue` | Continue 明文会话或项目历史 |
| `roo` | Roo 任务 / 会话 |
| `cline` | Cline 任务 / 会话 |
| `windsurf` | Windsurf 项目状态或会话 |
| `aider-desk` | Aider Desk 项目状态或会话 |
| `gemini-cli` | Gemini CLI 明文会话；见 `references/gemini-cli.md` |
| `antigravity-desktop` / `antigravity-cli` | Antigravity 两套 brain transcript；见 `references/antigravity.md` |
| `agent-app-log` | 只有日志和状态线索 |

如果只有缓存、空 index 或配置文件，不要进入高价值会话表。可以放进“可删除或降级的原始材料”或“待确认来源”。

## 7. 安全边界

这些应用常把 token、账户状态、OAuth、模型偏好和同步状态放在状态库里。复盘时不要复制密钥、token、cookie 或账户标识到 vault 正文。

看到类似 `oauthToken`、`apiKey`、`secret`、`credential`、`cookie` 的 key，只记录“存在认证配置”，不要展开 value。

## 8. 资料来源

| 来源 | 用途 |
|---|---|
| `https://deepwiki.com/continuedev/continue/8.7-history-and-session-persistence` | Continue session 持久化路径和字段参考；页面引用 Continue 源码 |
| `https://github.com/cline/cline/blob/main/.clinerules/storage.md` | Cline file-backed JSON storage 结构参考 |
| `https://github.com/cline/cline/blob/main/apps/vscode/src/core/controller/file/openDiskConversationHistory.ts` | Cline 单任务 `api_conversation_history.json` 路径参考 |
| `https://vibe-replay.com/blog/cursor-local-storage/` | Cursor 本地存储逆向参考；按社区资料处理 |
| 本机 `$HOME/.cursor`、`$HOME/.continue`、`$HOME/.roo`、`$HOME/.cline`、项目 `.windsurf`、项目 `.aider-desk` | 路径存在性实测 |
