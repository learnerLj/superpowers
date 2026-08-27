# Grok Bot Desktop 本地会话格式与读取合同

Grok Bot Desktop 的本地 transcript replica 位于 Electron Application Support。它能支持本机已同步内容的复盘，不能证明云端历史完整。

## 1 权威路径

```text
~/Library/Application Support/Grok Bot/sand-client-persistence/*.blob
```

文件名是无 padding 的小写 Base32 key。只读取解码后匹配以下结构的文件：

```text
sand.client.slice.account.<account-scope>.transcript.replicas.<conversation-id>
```

`<account-scope>` 可能包含账户标识，只用于定位，禁止进入 inventory、复盘正文或日志。`<conversation-id>` 才是本地会话 ID。

不要读取 `sand-secrets.json`、`box-secrets-*`、Cookie、Local Storage、Session Storage、Cache、GPUCache、Crashpad、Sentry 或 SharedStorage。

## 2 Replica 结构

当前本机样本是 JSON：

```text
schemaVersion
value.entries[]
value.epochHint
value.acceptedSequenceHint
value.persistedAt
```

`entries[]` 当前已见：

| `kind` | 作用 | 读取边界 |
|---|---|---|
| `send-message` | 客户端发送的 text、attachment 或 widget | text 是用户 prompt 候选；attachment / widget 不转成虚构文本 |
| `message` | 服务端复制回本地的消息 | 读取 `role`、`content`、`id`、`clientNonce` |
| `event` | automation 等状态变化 | 只作执行线索 |

同一用户输入可能同时存在于 `send-message` 和复制后的 `message`。优先使用稳定 `id` / `clientNonce` 关联；缺少稳定关联时，只有内容、时间和顺序同时一致才能标为 duplicate candidate，不能据此静默删除一份证据或增加 occurrence。

## 3 会话清单

```bash
AI_SESSION_REVIEW_DIR="${AI_SESSION_REVIEW_DIR:-$HOME/.agents/skills/superpowers/ai-session-review}"
python3 "$AI_SESSION_REVIEW_DIR/scripts/local_session_inventory.py" \
  --source grok-bot --format jsonl
```

时间取 `entries[].timestampMs` 与 `persistedAt`。cwd、model、pin、archive 在当前 replica 中不可观察，保持 `null` / `unavailable`。文件 `mtime` 不能补成最后活动时间。

inventory 的 `transcript_path` 使用 `grok-bot://transcript/<conversation-id>`，不得输出真实 `.blob` basename。需要读取正文时，在进程内重新扫描 `sand-client-persistence/*.blob`，解码并严格匹配完整 account slice key，再按 `<conversation-id>` 定位；真实 basename 和 `<account-scope>` 不进入 stdout、复盘或日志。

`entries[]` 至少含一条可识别的 `send-message`、`message` 或 `event` 才能标 `evidence_status=available`。空数组、`[{}]`、JSON 损坏或未知结构一律标 `unavailable`。

## 4 证据与 retention

1. 只有 `entries` 可解析时才能写正文复盘；空 blob、配置 slice 和迁移标记只作线索。
2. replica 是本机同步快照。缺失消息可能来自未同步、Private Chat、另一设备或格式漂移，不能写成用户没有该会话。
3. 多个 replica ID 分别保留。没有稳定 lineage 时不按标题或相似内容合并。
4. 本 skill 不访问 Grok.com、X Grok、浏览器 IndexedDB 或账户导出。
5. 删除单个 blob 不等同于删除账户会话，也可能破坏客户端状态。本地 Raw 默认 `retain_raw`；没有产品级精确删除合同前不直接删除 blob。

## 5 依据

- 本机 Grok Bot `0.20.0` 的 `sand-client-persistence` 字段实测，采样时间 `2026-08-19`。
- 本机已见 `schemaVersion=1` 的 transcript replica；格式漂移时先重采样 key 与 entry schema。
