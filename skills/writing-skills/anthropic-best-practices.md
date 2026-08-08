# Skill 格式与宿主差异

> 最后核对：2026-08-08。这里只保留当前 authority、可移植 contract 和平台差异；authoring 方法以 `SKILL.md` 为准。

## 当前 Authority

- [Agent Skills 开放规范](https://agentskills.io/specification)：可移植目录、frontmatter 和 resources contract。
- [Anthropic authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)：Claude 的写作与渐进披露建议。
- [Anthropic Skills overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)：Claude surface、安全和运行边界。
- [Claude Code skills](https://code.claude.com/docs/en/skills)：Claude Code 专属字段、发现和调用行为。
- [OpenAI Build skills](https://developers.openai.com/codex/build-skills)：Codex 专属发现路径、调用方式和 `agents/openai.yaml`。

开放规范定义可移植下限；目标宿主文档定义平台增量。冲突时先确认实际 runtime，再按当前 authority 和本地 validator 处理。

## 可移植 Contract

最小目录：

```text
skill-name/
├── SKILL.md
├── scripts/       # 可选：确定性工具
├── references/    # 可选：按需读取的资料
└── assets/        # 可选：输出模板和静态资源
```

`SKILL.md` 使用 YAML frontmatter 加 Markdown 正文：

- `name`：1-64 字符，只含小写字母、数字和连字符；与父目录名一致；
- `description`：1-1024 字符，说明做什么、何时使用，并提供发现关键词；
- 正文：agent 触发后读取的执行指导；
- resources：只在任务需要时读取或运行。

开放规范可能允许其它可选字段，但宿主支持程度不同。不要把某个平台字段写成所有 runtime 的必需项。

## 渐进披露

入口只保留核心 workflow、决策边界和资源导航。长 reference、变体与 API 资料拆出；从 `SKILL.md` 直接引用，避免多层跳转和重复维护。

script 要明确依赖、输入输出、错误行为，以及 agent 应执行还是阅读。批量、破坏性或高风险操作优先提供 machine-readable preview 和 validator。

## 平台差异

### Claude 专属

Claude Platform、claude.ai 与 Claude Code 的 skill 管理并不完全相同，自定义 skill 也不会自动跨 surface 同步。上传、runtime 包、MCP 名称和 Claude 专属字段以当前 Anthropic 文档为准。

### Codex 专属

Codex 支持仓库级、用户级、管理员级和系统级发现路径，也支持显式调用与基于 description 的隐式调用。`agents/openai.yaml` 是 Codex/ChatGPT 的可选 UI、调用策略和依赖 metadata，不是可移植 `SKILL.md` 的必需 frontmatter。

## 安全

skill 能指示 agent 执行代码、访问文件、调用工具和读取网络内容。部署前要像安装软件一样审计：

1. 阅读目录中的全部文件，而不只是 `SKILL.md`；
2. 核对外部 URL、网络请求、依赖下载和内容漂移；
3. 核对文件、shell、代码执行和工具权限；
4. 核对 secrets、用户数据、日志和中间产物是否可能外泄；
5. 不可信来源先在低权限隔离环境审计和验证。

## 快速检查

- [ ] 已确认目标 runtime 和当前 authority；
- [ ] `name`、目录名与 `description` 满足目标 contract；
- [ ] 入口简洁，resources 按需加载且只引用一层；
- [ ] script 的依赖、错误、权限和输出可验证；
- [ ] 已审计 bundled files、外部来源和数据暴露；
- [ ] 已运行目标 runtime 的结构 validator。
