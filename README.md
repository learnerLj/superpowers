# Superpowers

这是个人维护的 agent skills 库。保留目标、项目约定和关键审查流程，让 agent 根据任务选择具体开发方法；不重复教授通用能力，也不为简单任务增加完整流程。

## 设计原则

- **目标清楚**：说明预期结果、真实依据和必要边界，避免固定字段和机械步骤。
- **约定可定位**：项目规则留在项目，skill 保留可复用流程与按需参考入口。
- **必要时独立审查**：长任务 spec 在实施前审查，重大实现完成后审查，修复后定点复查。
- **简化实现**：减少不必要的概念、状态和间接层，保留正确性与真实边界。
- **证据与声明匹配**：验证实际改变的行为或状态；有效证据可以复用，不重复运行以满足形式。

具体触发条件和执行指导以各 skill 的 `SKILL.md` 为准；本 README 提供概览，不另建一套规则。

## 工作流程

1. **规划**：用户要求设计、存在重要设计分歧或需要跨会话恢复时，使用 `brainstorming`。沿用同一目标的计划；新 spec 优先使用项目指定位置，默认 `<project-root>/superpowers/YYYY-MM-DD-<topic>-spec.md`。
2. **Spec 审查**：用于执行长任务的 spec 在实施前交给独立只读 reviewer，解决影响执行的问题，再按已有授权继续。
3. **开发与测试**：根据任务实现、测试和整理代码，遵守项目范围与资源限制。用户明确要求 TDD 时才调用 `test-driven-development`；它提供简短的测试先行思路，不约束普通开发。
4. **实现审查与复查**：重大实现、复杂修复、公共接口、跨组件或高风险变更使用 `requesting-code-review`；反馈由 `receiving-code-review` 核查，在授权内修复并定点复查。项目要求的合并审查照常执行。
5. **最终验收**：`verification-before-completion` 对照目标、必要审查和实际证据确认交付。局部低风险改动可以自审，不强制写 spec。

Reviewer 只检查与报告，实施者负责修复。用户只要求规划或审查时交付对应结果；已有实现授权不因进入这些环节而失效。提交、发布等操作遵循用户授权。

## 安装与目录

实际内容在 `skills/<name>/SKILL.md`。参考文档和工具保留在对应 skill 目录，按任务需要读取或运行。无需安装额外的会话启动 hook。

可以将所需 skill 目录链接到使用环境的 skills 目录。以下命令中的仓库路径替换为实际位置；链接前检查已有同名项，保留现有配置。

Claude Code 示例：

```bash
mkdir -p "$HOME/.claude/skills"
for skill in /absolute/path/to/superpowers/skills/*; do
  [ -d "$skill" ] || continue
  ln -s "$skill" "$HOME/.claude/skills/$(basename "$skill")"
done
```

Codex 示例：

```bash
mkdir -p "$HOME/.agents/skills"
for skill in /absolute/path/to/superpowers/skills/*; do
  [ -d "$skill" ] || continue
  ln -s "$skill" "$HOME/.agents/skills/$(basename "$skill")"
done
```

TDD 的入口只匹配用户明确请求；`skills/test-driven-development/agents/openai.yaml` 另为 Codex 配置关闭自动调用。其它 skill 按各自 description 选择，不能因为安装了就全部加载。

## Skills

| Skill | 用途 |
|---|---|
| `brainstorming` | 规划、spec 审查入口与任务恢复 |
| `test-driven-development` | 明确要求时使用的开发与测试思路 |
| `systematic-debugging` | 用证据定位未确认的根因 |
| `requesting-code-review` | 组织必要的独立代码审查 |
| `receiving-code-review` | 核查反馈、修复与复查 |
| `verification-before-completion` | 交付前验收 |
| `verify-this` | 核实用户指定的声明 |
| `code-simplification-review` | 识别值得去除的复杂度 |
| `traceable-explainer` | 依据已有产物解释机制 |
| `retro` | 复盘当前会话 |
| `ai-session-review` | 查找和复盘历史会话，按专项合同处理归档与保留 |
| `writing-skills` | 编写、验证和审查 skill 修改 |

## 修改本库

按 [CLAUDE.md](CLAUDE.md) 和 [writing-skills](skills/writing-skills/SKILL.md) 工作。选择能证明本次修改的检查：格式与引用用静态检查，行为变化用代表任务；需要证明增量效果时才做对照评测。

只报告实际执行的验证和覆盖边界。使用 PR 时按[模板](.github/PULL_REQUEST_TEMPLATE.md)填写，不适用项可以省略；本库的维护流程不等同于向上游投稿。向上游贡献时另读目标仓库的当前规定。

## 来源与许可

本库基于 [obra/superpowers](https://github.com/obra/superpowers) 定制，保留其来源归属。许可见 [LICENSE](LICENSE)。
