---
name: writing-skills
description: 创建新 skill、编辑已有 skill，或在部署前验证 skill 是否有效时使用
---

# 编写 Skills

## 概述

**编写 skill，就是把测试驱动开发应用到流程文档。**

个人 skill 位于 runtime 的 skills 目录：Claude Code 使用 `~/.claude/skills/`，Codex 使用 `~/.agents/skills/`。

先写测试场景，让 fresh-context 只读 evaluator 在没有 skill 时失败（baseline）；再写 skill，让相同测试通过；最后在保持通过的前提下堵住新漏洞。

**核心原则：** 如果没有亲眼看到 agent 在缺少该 skill 时失败，你就不知道 skill 是否教对了东西。

**必备背景：** 使用前必须理解 `test-driven-development` 的 RED-GREEN-REFACTOR 循环。本 skill 只是把它应用到文档。

Anthropic 官方建议见 [anthropic-best-practices.md](anthropic-best-practices.md)，它补充本 skill 的 TDD 方法。

## 什么是 Skill

skill 是已验证方法、模式、工具或参考的可复用指南，不是一次解决问题的经历叙事。

## TDD 映射

| TDD 概念 | Skill 创建 |
|---|---|
| 测试用例 | fresh-context 只读 evaluator 面对的压力场景 |
| 生产代码 | `SKILL.md` |
| RED | agent 在无 skill baseline 下违反规则 |
| GREEN | 加载 skill 后遵守规则 |
| REFACTOR | 保持遵守的同时堵住合理化漏洞 |
| 测试先行 | 写 skill 前先运行 baseline |
| 观察失败 | 记录 agent 的精确合理化措辞 |
| 最小实现 | 只针对已观察到的违规编写规则 |

## 何时创建

当方法并不直观、会跨项目重复使用、可广泛复用时创建。一次性解法、已有权威文档充分覆盖的标准实践、项目专属约定（应放项目 instruction），以及可由 regex/validator 自动执行的机械限制，都不应做成 skill。

## Skill 类型

- **Technique：** 有具体步骤的方法，如 condition-based-waiting、root-cause-tracing。
- **Pattern：** 解决问题的思维模式。
- **Reference：** API、语法或工具参考。

## 目录结构

```text
skills/
  skill-name/
    SKILL.md              # 必需入口
    supporting-file.*     # 仅在确有需要时添加
```

使用扁平可搜索 namespace。超过 100 行的重型参考和可复用脚本应拆出；原则、概念和小于 50 行的代码模式留在入口。

## SKILL.md 结构

frontmatter 必须包含 `name` 与 `description`，总长度不超过 1024 字符。

- `name` 只使用字母、数字和连字符。
- `description` 只描述何时触发，不总结流程；使用第三人称和具体症状，尽量少于 500 字符。
- 正文包含一两句核心原则、必要决策、实现方法、快速参考和常见错误。

## Skill 发现优化（SDO）

### Description 只拥有触发条件

agent 依靠 description 判断现在是否需要读 skill。description 总结流程时，agent 可能把它当捷径，跳过正文。例如“实现后派 reviewer”会诱发一次浅层审查，即使正文要求 spec 与质量两次检查。

```yaml
# 错误：总结流程
description: 实现 spec 时使用，会在每个切片后派 reviewer

# 错误：包含过多步骤
description: 做 TDD 时使用，先写测试、看它失败、写最小实现、再重构

# 正确：只描述触发条件
description: 完成工作并需要对照已批准 spec 审查时使用

# 正确：只描述触发条件
description: 实现任何 feature 或 bugfix，并且尚未编写实现代码时使用
```

description 要包含 agent 会搜索的错误、症状、同义词和工具名。除非 skill 本身绑定技术，否则描述问题而非某语言的实现细节。

### 描述性命名与关键词

使用主动、动词优先的名称，例如 `creating-skills`、`condition-based-waiting`。正文早期覆盖真实错误、症状、工具和文件类型，便于搜索。

### 控制 token

agent 已经很聪明，只加入非显而易见的上下文。常加载入口应极短，其它入口也尽量少于 500 words。把 flags 交给 `--help`，用明确交叉引用替代重复流程，一个优秀示例胜过多个普通示例。

### 交叉引用

只写 skill 名并标明强度：

- `**必需子 skill：** 使用 test-driven-development`
- `**必备背景：** 必须理解 systematic-debugging`

不要用含糊文件路径或强制预加载的 `@` 引用。

## 代码示例

一个完整、可运行、解释“为什么”、来自真实场景且可直接适配的示例，优于五种语言的平庸变体。测试方法优先 TypeScript/JavaScript，系统调试优先 Shell/Python，数据处理优先 Python。

## 铁律

```text
没有先看到失败测试，就不允许新增或编辑 SKILL
```

它同时适用于新 skill 和已有 skill 的修改。先写或先改了，就删除该变更并从 RED 重来。没有“只是增加一小节”“只是文档”“先留作参考”“边测试边适配”等例外。

## 按 Skill 类型测试

- **纪律型：** 用学术问题、多个压力叠加、合理化借口测试。成功标准是在最大压力下仍遵守。
- **Technique：** 用应用、变体和缺失信息场景测试。成功标准是能迁移到新场景。
- **Pattern：** 用识别、应用和反例测试。成功标准是知道何时用、如何用以及何时不用。
- **Reference：** 用检索、应用和缺口测试。成功标准是找到并正确使用信息。

## 常见跳过测试的借口

| 借口 | 事实 |
|---|---|
| “skill 显然很清楚” | 对作者清楚不代表对其它 agent 清楚。必须测试。 |
| “只是参考资料” | 参考也可能缺内容或难以检索。 |
| “测试太重” | 15 分钟测试能避免生产中数小时返工。 |
| “有问题再测” | 那意味着 agent 已经无法使用它。部署前测试。 |
| “学术审查足够” | 阅读不等于实际使用。 |
| “我很有信心” | 信心不是证据。 |

## 让形式匹配失败类型

先分类 baseline failure：

| 失败类型 | 正确形式 | 错误形式 |
|---|---|---|
| 明知规则却在压力下跳过 | 禁止项 + 合理化表 + 停止信号 | “建议”“考虑”式软指导 |
| 输出形状错误 | 正向 recipe/contract，明确输出由哪些部分按何顺序组成 | 一长串“不要……” |
| 已有输出缺少必需元素 | 在模板中加入 REQUIRED 字段/slot | 模板附近的散文提醒 |
| 行为取决于条件 | 绑定可观察 predicate 的条件句 | 无条件规则加例外条款 |

禁止项会让输出形状问题变得更糟：在“必须自包含”等竞争激励下，agent 会与“不要 X”谈判；正向 recipe 则只有匹配或不匹配。不要添加“除非有必要”这类 nuance clause。若有真实例外，把它写成以可观察条件为键的独立规则。豁免条款也常无法正确缩小范围，应重构规则，让它根本触及不到豁免内容。

## 加固纪律型 Skill

这套工具只适用于“知道规则但在压力下跳过”的纪律失败，不适用于输出形状或缺字段问题。

1. 明确堵住每个已观察到的绕过方式，不只说“先写测试”，还要说先写实现就删除、不能留作参考、不能一边写测试一边看它。
2. 尽早声明“违反字面规则就是违反规则精神”。
3. 把 baseline 中每句借口和对应事实加入 rationalization table。
4. 建立显眼的停止信号列表；命中任何一项都要求停止并重来。
5. description 加入即将违规时会出现的症状。

说服原则的研究背景见 [persuasion-principles.md](persuasion-principles.md)。

## Skill 的 RED-GREEN-REFACTOR

### RED：先运行失败 baseline

让 fresh-context 只读 evaluator 在**没有 skill**时运行压力场景。它只返回响应，不编辑文件、不实现、不提交。记录它的选择、逐字合理化借口，以及哪些压力触发了违规。

### GREEN：写最小 Skill

只针对已观察到的具体合理化编写规则，再让相同 evaluator 在加载 skill 后运行同一场景。

### REFACTOR：堵住漏洞

出现新借口就添加精确 counter，并重复相同测试，直到在压力下稳定遵守。

### 完整场景前先微测措辞

1. 每次调用只取一个 fresh-context 样本；只读 evaluator 不得实现或编辑。
2. 必须包含 no-guidance control；control 不出现失败，就没有要修的问题，应停止 authoring。
3. 每个措辞变体至少 5 次。
4. 人工阅读每个命中；模板回显和引用反例会制造假阳性。
5. 把方差当指标；五次得到五种解释说明措辞没有约束力。

微测只验证措辞，不替代纪律型 skill 的完整压力场景。完整方法见 [testing-skills-with-reviewers.md](testing-skills-with-reviewers.md)。

## 反模式

- 用某次 session 的故事代替可复用规则。
- 为同一模式维护多语言低质量示例。
- 使用 `helper1`、`step2` 之类无语义标签。

## 停止：完成当前 Skill 后才能继续

编写任何 skill 后，必须停止并完成该 skill 的部署验证。不得批量创建多个未测试 skill，不得因“批量更高效”而先进入下一个。未测试 skill 等于未测试代码。

## 创建 Checklist

### RED 阶段

- [ ] 创建压力场景；纪律型至少叠加 3 种压力
- [ ] 无 skill 运行并逐字记录失败与合理化
- [ ] 识别重复失败模式

### GREEN 阶段

- [ ] `name` 与 YAML 合法，description 是中文触发条件而非流程摘要
- [ ] 覆盖检索关键词，概述与核心原则清楚
- [ ] 只针对 baseline failure 编写最小指导
- [ ] 指导形式匹配失败类型
- [ ] 行为塑造措辞已与 no-guidance control 做 5+ 次微测
- [ ] 代码 inline 或链接到真实 supporting file
- [ ] 使用一个优秀示例
- [ ] 加载 skill 后同场景通过

### REFACTOR 阶段

- [ ] 捕获新合理化并为纪律型规则添加精确 counter
- [ ] 更新 rationalization table 与停止信号
- [ ] 重测直到没有新漏洞

### 质量与部署

- [ ] 有快速参考与常见错误
- [ ] supporting file 只用于工具或重型参考
- [ ] 运行结构验证和行为验证
- [ ] 按仓库要求提交；只有用户或流程明确要求时才 push/提 PR

## 发现路径

未来 agent 会经历：遇到问题 -> 从 description 找到 skill -> 扫描概述 -> 读取模式 -> 需要时加载示例。为这条路径优化，把可搜索触发词放在前面，并通过渐进披露保持入口精简。
