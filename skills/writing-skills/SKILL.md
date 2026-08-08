---
name: writing-skills
description: 创建新 skill、编辑已有 skill，或在部署前验证 skill 是否有效时使用
---

# 编写 Skills

## 核心原则

**默认 agent 已经足够聪明。** skill 只补充它无法可靠推导、容易判断错或必须稳定执行的内容：方向、边界、工具、真实 owner 和高频失败点。

先取得能被本次修改改变的证据，再写最小指导。行为问题使用 fresh-context control；规范、引用、结构和安全问题使用当前 authority、静态 contract 或真实 artifact。复验通过就停止，不为假想漏洞继续扩写或测试。

## 先判断是否该写 Skill

适合创建 skill：

- 方法不直观，而且会跨项目重复使用；
- 需要稳定的多步骤 workflow、领域知识或工具集成；
- 某个高频错误不能靠宿主规则、validator 或现有文档解决。

不要创建 skill：

- 一次性任务或某次 session 的复盘；
- 项目专属约定，它应进入项目 instruction；
- regex、schema、formatter 或 validator 能直接执行的机械限制；
- 当前官方文档已经充分覆盖、且没有额外 workflow 的内容。

## 写作指引

### 一个 Skill 只做一件事

明确它做什么、不做什么、谁会触发它，以及完成后产生什么。名称和目录使用同一个短、可搜索的动作名称。

### Description 负责发现

可移植 Agent Skills contract 至少要求：

- `name` 为 1-64 字符，只含小写字母、数字和连字符；不以连字符开头或结尾，不含连续连字符，并与目录名一致；
- `description` 为 1-1024 字符，说明 skill 做什么以及何时使用，并包含任务、症状、文件类型或边界关键词。

description 不复制 workflow。步骤、顺序和例外放在正文，否则 agent 可能根据 metadata 走捷径而不读入口。

### 只写非显然内容

- 优先写决策边界、真实 owner、必要输入输出和常见失败；
- 一个完整示例优于多组平庸变体；
- 多种方法都可行时给原则，脆弱流程给精确步骤，确定性操作优先 script；
- 重型 reference、可复用 script 和 output asset 按需拆出，入口只保留导航与核心 workflow；
- 引用 supporting file 时说明何时读取或运行，避免多层 reference 链。

当前格式和宿主差异见 [anthropic-best-practices.md](anthropic-best-practices.md)。行为评测方法仅在需要时读取 [testing-skills-with-reviewers.md](testing-skills-with-reviewers.md)。

## 证据驱动修改

### RED：确认缺口

- 行为规则：运行一个最小 no-skill control，保留 prompt、原始输出和可观察缺口；
- 规范或引用：记录现有文本与当前 authority 的冲突；
- 结构或机械约束：写一个会因旧文本失败的静态 contract；
- 真实使用已经暴露问题：直接使用该 artifact，不为形式重复生成 evaluator。

没有缺口就停止 authoring。

### GREEN：写最小指导

只处理 RED 已经证明的问题，并用同类证据复验。不要顺手增加相邻理论、多个语言示例或未经观察的防御条款。

### REFACTOR：只处理新观察

只有复验出现新的可观察缺口时才继续。行为失败要先分类：

| 失败 | 优先形式 |
|---|---|
| 合理化绕过明确规则 | predicate、禁止项、停止信号 |
| 输出形状或缺字段 | 正向 template/schema |
| 检索不到内容 | description 关键词、入口导航 |
| 机械错误 | validator 或 script |
| 权限风险 | approval、最小权限、隔离 |

强硬措辞不能替代清晰 contract、确定性工具或权限控制。

## 评测预算

默认只运行一对 fresh-context 样本：1 次 RED control + 1 次 GREEN candidate。只读 evaluator 不得实现或编辑。

只有观察到实际输出方差、规则歧义或 candidate 仍违规时才增加样本。每次增加前说明新增调用会改变哪个具体决策；不能改变就停止。多场景、多候选任务先设置总 evaluator 调用预算，不得展开 `fixture × candidate × wording × repeat` 全矩阵。

修改后只重跑被修改规则直接影响的场景。普通 Technique、Pattern、Reference 或 trigger 场景单项最多 3 次；5 次重复只用于已有高方差证据的高压力纪律型 skill，并需 human partner 事先批准预算。

无法区分结果时标记 `INCONCLUSIVE`，先修场景或判定标准，不继续调用直到出现期望答案。

## 安全审查

安装、部署或更新前，审计 skill 目录中的全部文件：

- script、asset、reference、隐藏配置和生成资源是否符合声明目的；
- 外部 URL、网络请求和依赖是否存在 prompt injection 或 supply-chain drift；
- 文件读写、shell、代码执行和工具权限是否最小；
- secrets、敏感数据、日志和中间产物是否可能外泄。

把第三方 skill 当作软件依赖，不因旧版本可信就自动信任更新版本。

## 高频错误

- 把一次成功经历整理成“通用方法”，却没有重复使用证据；
- description 只写“帮助处理 X”，或把完整步骤塞进 description；
- 重复官方文档，导致内容快速过时；
- 用长篇背景解释代替可执行方向；
- 为多个语言、候选、场景和措辞展开完整评测矩阵；
- candidate 已通过仍继续寻找假想漏洞；
- script 未实际运行，或只验证 `SKILL.md` 而忽略 bundled files；
- 用模型自评、meta-test 或规则复述代替真实行为证据。

## 完成检查

- [ ] skill 只拥有一个清楚、可复用的任务；
- [ ] `name`、目录名和 `description` 满足目标 runtime contract；
- [ ] 正文只保留非显然指导、高频错误和必要导航；
- [ ] 指导形式匹配已观察到的失败类型；
- [ ] 若修改行为塑造措辞，已完成默认的 1 次 control + 1 次 candidate；
- [ ] 若增加样本，已记录方差、会改变的决定和批准预算；
- [ ] 只重测受影响场景，通过后停止；
- [ ] 已审计全部 bundled files、外部来源、权限和数据暴露；
- [ ] 已运行目标 runtime 的结构 validator 和最小相关验证。
