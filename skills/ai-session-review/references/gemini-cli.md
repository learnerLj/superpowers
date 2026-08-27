# Gemini CLI 本地会话格式与读取合同

Gemini CLI 使用项目级 JSONL 保存可恢复会话。`~/.gemini/history/` 是输入历史目录，不能替代 `tmp/<project-id>/chats/` 的会话正文。

## 1 权威路径

```text
~/.gemini/projects.json
~/.gemini/tmp/<project-id>/chats/session-*.jsonl
~/.gemini/tmp/<project-id>/chats/<parent-session-id>/<subagent-id>.jsonl
```

`projects.json.projects` 是 `absolute cwd -> project-id` 映射。反向映射失败时读取 `tmp/<project-id>/.project_root`；仍失败则 cwd 为 `unavailable`，不得按 slug 猜测。

不要读取 `oauth_creds.json`、Google account 文件、`.env`、MCP OAuth token、keychain、browser profile 或其他认证配置。

## 2 JSONL 重放

会话不是普通 append-only message list。抽取前必须按顺序重放：

1. 含 `sessionId`、`projectHash`、`startTime`、`lastUpdated`、`kind` 的记录初始化 metadata。
2. 含 `id` 的记录是 message，按 ID 保持顺序并允许后写更新。
3. `{"$set": {...}}` 更新 metadata；若包含 `messages`，它是 checkpoint，替换当前 message state。
4. `{"$rewindTo": "<message-id>"}` 删除该 ID 及之后的当前消息；找不到 ID 时当前消息状态清空。

不完成重放就直接逐行计数，会把已 rewind 的 turn、checkpoint 旧副本和 subagent context 重复算入正文。

## 3 消息归因

| `type` | 归因 |
|---|---|
| `user` | 用户候选 |
| `gemini` | 助手回复、thought、tool call 和 token metadata |
| `info`、`error`、`warning` | 运行状态，不是用户消息 |

`type=user` 的内容为空，或以 `/`、`?`、`<session_context>`、`<hook_context>` 开头时，不作为真实用户 prompt。tool response 可能使用 user role 进入模型 history，必须结合 message record 与 tool call ID 判断，不能只按 role 计 occurrence。

## 4 会话清单

```bash
AI_SESSION_REVIEW_DIR="${AI_SESSION_REVIEW_DIR:-$HOME/.agents/skills/superpowers/ai-session-review}"
python3 "$AI_SESSION_REVIEW_DIR/scripts/local_session_inventory.py" \
  --source gemini-cli --format jsonl
```

`kind=subagent` 归为 subagent，默认排除。`startTime` 与 `lastUpdated` 负责时间筛选；缺失时可以使用仍在当前重放状态内的 message timestamp，不能使用文件 `mtime`。

JSONL 含 malformed 行时，即使其余 metadata 与 message 可重放，也必须标 `evidence_status=unavailable`。多个文件重放出同一 `sessionId` 时 inventory 只保留一条并标 `unavailable`，不能静默选择某个 resume artifact 作为完整正文。

## 5 Lineage、retention 与删除

1. subagent 文件位于完整 parent session ID 子目录下；该目录只提供 immediate parent 候选，仍需与 metadata 交叉核对。
2. main 与 subagent 的 `sessionId` 分别去重；checkpoint、rewind 和 resume 不增加 occurrence。
3. `~/.gemini/history/` 只用于 prompt 输入历史或迁移定位，不进入 canonical session scope。
4. 本 skill 不读取 Gemini Apps、Google My Activity、Takeout 或浏览器数据。
5. 删除单个 JSONL 前仍需 deep review、retention gate 和精确文件授权；项目 registry、认证文件和其他 session 不在默认删除范围。

## 6 依据

- `google-gemini/gemini-cli` 源码 `packages/core/src/services/chatRecordingService.ts`、`chatRecordingTypes.ts`、`packages/core/src/config/storage.ts`，commit `571851b1077a51cef757146ce13f9da887326bec`。
- 本机 `~/.gemini/projects.json` schema 实测，采样时间 `2026-08-19`；本机当前 `tmp/*/chats` 可为零命中，零命中不扩大到云端来源。
