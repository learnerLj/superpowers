---
name: ai-session-review
description: 查找、复盘、归档或清理已落盘的 AI 历史会话；当前对话复盘使用 retro。
---

# AI 历史会话

先圈定用户指定的 ID、项目、来源或时间窗口，做只读盘点。零命中不放宽筛选，正文或 lineage 不可确认时保留未知，不扫描整个主目录补猜。

## 按来源读取

- Codex：[references/codex.md](references/codex.md)。
- Claude Code／OpenCode：同时检查 projects 与 transcripts，见 [references/claude.md](references/claude.md)。
- Grok Build：[references/grok-build.md](references/grok-build.md)；Grok Bot：[references/grok-bot.md](references/grok-bot.md)。
- Gemini CLI：[references/gemini-cli.md](references/gemini-cli.md)。
- Antigravity：[references/antigravity.md](references/antigravity.md)。
- 其它来源：[references/common-agent-apps.md](references/common-agent-apps.md)。

Codex 使用 `scripts/codex_session_inventory.py`，其它本地来源使用 `scripts/local_session_inventory.py`；参数以脚本 `--help` 和来源文档为准。只查本地会话，不探测浏览器凭据或云端账户；输出不包含认证值。

## 按目的展开

只查找或盘点时不加载复盘合同。提取经验、比较多次会话、持久化或评估删除时，读取 [references/session-review-workflow.md](references/session-review-workflow.md) 与 [references/review-contract.md](references/review-contract.md)，保留其中的 lineage 去重、深度、晋级及保留条件。审计历史 skill 效果时另读 [references/skill-effectiveness-audit.md](references/skill-effectiveness-audit.md)。

默认只报告。写笔记、归档、删除各自遵循用户授权；总结完成不等于可以删除。删除仍需精确目标、成熟年龄、pin 保护、完整复盘与证据已承接等条件，并取得对应范围的明确授权。运行时日志清理与会话正文分开处理。

用中文交代范围、发现、证据边界、写入和删除的实际结果，不把内部字段当成正文。专项任务需要的机器字段与固定状态行以对应合同为准。
