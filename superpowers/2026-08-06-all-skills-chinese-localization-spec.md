# Superpowers 全技能中文化 Spec

**状态：** 已完成

**日期：** 2026-08-06

**翻译前基线：** `dca68ca2b6a47114e11b824bb4a0adbef561751e`

## 目标与非目标

### 目标

- 把 `skills/` 下所有会被模型读取的说明、规则、提示词、测试场景和参考文档翻译成中文。
- 保持 9 个 skill 的名称、触发边界、执行顺序、硬门槛、例外、证据要求和失败处置语义不变。
- 让中文成为 skill 的唯一叙述语言，方便个人长期阅读和微调。
- 保留代码、命令、路径、标识符、API 字段、环境变量、协议名、错误字面量和必要技术术语的原始形式。

### 非目标

- 不重命名 skill 目录或 frontmatter `name`。
- 不改变短任务、长任务、TDD、debugging、review、verification 和 branch finishing 的行为 contract。
- 不翻译 JavaScript、Shell、TypeScript、HTML 等可执行源码；其中的用户界面文案不在本次范围内。
- 不恢复 plugin、hook、package 或其它 harness adapter。
- 不在本次修改 Claude/Codex 的本机安装链接或清理 Claude 的旧 plugin 缓存。

## 当前状态与 Authority

- 翻译前行为 authority 是提交 `dca68ca2b6a47114e11b824bb4a0adbef561751e` 中的 `skills/`。
- `skills/using-superpowers/SKILL.md` 拥有长短任务路由 authority。
- `skills/brainstorming/SKILL.md` 拥有 executable spec contract 与 evidence profile authority。
- 其它 7 个 `SKILL.md` 分别拥有对应专业流程。
- 同目录 supporting Markdown 只补充入口 skill 明确引用的细节，不得产生第二套规则。
- 本 spec 是中文化任务唯一的执行与进度 authority。

## 交付物

1. 9 个中文 `SKILL.md`，frontmatter `description` 也使用中文。
2. `skills/` 下所有模型可读 `.md` 与 `.dot` 参考使用中文叙述。
3. 中文化静态回归测试，能够发现英文标题、英文触发描述和遗漏的模型可读文件。
4. 翻译前后行为对照证据，覆盖路由、TDD、debugging、review、verification、branch finishing 和 skill authoring。

## 翻译 Contract

- 使用自然、直接、可执行的简体中文，不使用生硬逐词直译。
- 保持原文信息结构与规则强度；`MUST`、`NEVER`、`STOP`、硬门槛、红旗和禁止项必须用同等强度的中文表达。
- `name`、skill 名称、文件名、路径、命令、代码块、正则、Git ref、环境变量、API/字段名与精确错误保持原样。
- `TDD`、`RED-GREEN-REFACTOR`、`BASE_SHA`、`spec` 等已形成稳定 contract 的技术词可保留；第一次出现时用中文解释。
- 中文正文不保留平行英文段落，避免上下文翻倍和两套规则漂移。
- 示例代码内的字符串只有在它们承担教学叙述而非被测字面量时才翻译；测试断言依赖的字面量保持原样。
- 链接目标和相对路径必须保持有效。

## 完成证据

### 结构证据

- 9 个 skill 通过 `quick_validate.py`。
- 所有 `SKILL.md` 的 `description` 包含中文且不再以 `Use when` 开头。
- 所有模型可读 `.md`/`.dot` 不存在英文叙述标题；允许纯技术字面量标题白名单。
- supporting file 引用仍能解析到真实文件。

### 行为证据

- 翻译前后使用相同场景进行只读 evaluator 对照。
- 评估至少覆盖：短任务退出、长研究 spec、软件 spec/TDD、长 debugging 状态转换、拒绝跳过 TDD、质疑不可靠 review、只读 code review、完成前新鲜验证、branch finishing、skill authoring 测试纪律。
- 只有路由、门槛、顺序、证据和禁止项均保持等价，才判定翻译通过。

### 仓库证据

- `tests/workflow/run-tests.sh`、保留 helper tests、`git diff --check` 和相关语法检查通过。
- 最终只读 reviewer 对 `BASE_SHA..working tree` 无 Critical/Important finding。

## 调整条件

以下情况要求停止对应分片并修订本 spec：

- 中文无法在不改变语义的情况下表达原规则；
- 静态测试要求与必须保留的技术字面量冲突；
- evaluator 显示触发率、规则强度或流程顺序发生实质变化；
- supporting file 存在原文内部矛盾，无法判断应翻译哪一套语义；
- 用户要求改变流程本身，而不再只是中文化。

## 最终验收

- `skills/` 内模型可读叙述统一为中文。
- 9 个 skill 的行为边界与 `dca68ca` 基线等价。
- 不存在为了中文化新增的重复文档、第二套 spec 或平台适配层。
- 所有完成声明都有可定位的静态、行为和仓库验证证据。

## 执行切片

- [x] **C1：建立中文化 RED 与行为基线**
  - **结果：** 静态测试能在英文基线上失败，关键行为场景有翻译前样本。
  - **依赖：** 无。
  - **工作范围：** workflow 测试与只读 evaluator evidence。
  - **输入与 Authority：** `dca68ca` 中全部 skill。
  - **交付物：** 中文化检查脚本、失败输出和 baseline evidence。
  - **完成证据：** 失败只来自尚未中文化；行为样本可定位。
  - **验证或审查门槛：** 主 agent 检查每个断言未误伤技术字面量。

- [x] **C2：中文化总路由与 spec 核心**
  - **结果：** `using-superpowers`、`brainstorming`、`verification-before-completion` 及其直接 prompt/reference 全中文化。
  - **依赖：** C1。
  - **工作范围：** 3 个核心 skill 与直接 supporting 文件。
  - **输入与 Authority：** 翻译 Contract、核心行为 baseline。
  - **交付物：** 中文核心流程。
  - **完成证据：** 结构验证与核心场景候选复测通过。
  - **验证或审查门槛：** 只读 reviewer 检查路由、evidence profile 和完成门槛。

- [x] **C3：中文化软件开发流程**
  - **结果：** TDD、systematic-debugging、requesting/receiving review、branch finishing 及其 supporting 文件全中文化。
  - **依赖：** C1。
  - **工作范围：** 5 个软件流程 skill、prompt、方法参考和测试场景。
  - **输入与 Authority：** 翻译 Contract、软件纪律 baseline。
  - **交付物：** 中文软件开发与调试流程。
  - **完成证据：** 各 skill 的静态验证与对应压力场景候选复测通过。
  - **验证或审查门槛：** 只读 reviewer 检查硬门槛、禁止项和 review authority。

- [x] **C4：中文化 skill authoring 体系**
  - **结果：** `writing-skills` 及其全部模型可读参考全中文化。
  - **依赖：** C1。
  - **工作范围：** `writing-skills` 下 `.md` 与 `.dot`。
  - **输入与 Authority：** 翻译 Contract、skill authoring baseline。
  - **交付物：** 中文 skill 编写、测试和说服原则参考。
  - **完成证据：** 结构验证、链接检查、authoring 场景候选复测通过。
  - **验证或审查门槛：** 只读 reviewer 检查测试纪律未弱化。

- [x] **C5：全量复核与收尾**
  - **结果：** 全部模型可读 skill 内容为中文，行为等价，仓库测试通过。
  - **依赖：** C2、C3、C4。
  - **工作范围：** `skills/` 全量与相关 workflow tests。
  - **输入与 Authority：** C1 baseline、最终候选和测试映射。
  - **交付物：** 最终 diff、行为对照证据和验证记录。
  - **完成证据：** 所有验收项通过，review 无 Critical/Important。
  - **验证或审查门槛：** 独立只读最终 review。
