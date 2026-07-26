# 系统组成与实现切片 - 可执行规范

**状态：** 已通过独立审计并由用户批准

## 1. 目标与非目标

### 目标

一份经过批准的 executable spec 必须足以指导长时间开发，不再生成第二份
implementation plan。spec 需要明确系统组成、职责边界、canonical data
structure、包含与引用关系、必要的数据转换、按依赖排序的 implementation
slices、验收标准和验证证据。

主 Agent 必须能够只依赖这份 spec 恢复工作，选择下一个未完成 slice，通过
TDD 实现，完成验证和已声明的只读 review gate，然后继续推进，不需要临时发明
架构，也不把实现委派给 subagent。

### 非目标

- 不恢复 `writing-plans`、plan mode、独立 plan 文件，或者 spec 外部的第二套
  todo/progress artifact。
- 不规定生产代码、逐行编辑、2-5 分钟微操作、commit 命令、时间估算或
  implementer task packet。
- 不要求与任务无关的数据库 schema 或僵硬数据字典。
- 不全面禁止 DTO、adapter、projection、persistence record 或 boundary model；
  它们在真实的信任、协议、兼容、安全、持久化或 invariant 边界上仍然合理。
- 不允许 reviewer subagent 编辑文件、编写实现、运行实现任务或提交。
- 不改变 `test-driven-development` 的 RED-GREEN-REFACTOR 核心契约。

## 2. 当前系统上下文

`skills/brainstorming/SKILL.md` 是 executable spec 的生成 authority。当前契约
要求 goal/non-goals、current context、target files、interfaces and data
contracts、behavioral slices、acceptance criteria、test mapping，以及
migration/compatibility，但存在三个可以被表面满足的缺口：

1. `Interfaces and data contracts` 可以只列 signature 和 schema，不解释系统
   职责、canonical ownership 或结构之间的关系。
2. `Behavioral slices` 没有定义可恢复执行的依赖、完成证据和 review gate。
3. 没有要求作者解释同形 DTO、重复 model 或只为模拟分层而存在的数据转换。

`skills/brainstorming/spec-document-reviewer-prompt.md` 检查完整性、contract、
acceptance 和 test mapping，但不会阻止组件 ownership 不清、重复结构过多或转换
理由不足的 spec。

`skills/requesting-code-review/code-reviewer.md` 检查一般性的 separation of
concerns 和 DRY，但不会明确对照批准 spec 中的 canonical model，检查实现新增的
结构和转换。

`skills/requesting-code-review/SKILL.md` 已经把批准 spec 设为唯一 review
authority，并要求主 Agent 修复 findings。`skills/verification-before-completion/
SKILL.md` 已经要求最终提交前检查 acceptance criteria。两者都还没有使用内嵌
implementation slices 定义完成状态。

`tests/workflow/test-spec-to-tdd-consistency.sh` 是现役 spec-to-TDD workflow 的
确定性回归测试。它目前只断言旧 contract，没有覆盖 system composition、
canonical ownership、transformation justification 或 implementation slices。

`README.md` 将公开 workflow 描述为一份 executable spec 后接主 Agent TDD；更新
后仍需与这个单一 authority 保持一致。

当前 contributor guide 提到的可选 `evals/` checkout 不存在。因此本次 skill
behavior evaluation 使用 fresh-context 只读 evaluator session，并在实现会话中
记录精确 prompt、response 和人工评分；确定性 workflow assertions 继续保存在
仓库测试中。

## 3. 文档语言契约

`brainstorming` 默认使用中文撰写 executable spec。以下情况可以覆盖默认值：

- 用户明确要求使用其他语言；
- 项目的权威规则文件明确规定正式文档语言；
- 修改既有 spec 时，其现有语言和项目约定要求保持一致。

代码标识符、类型名、API 字段、命令、路径、错误文本和其他必须精确匹配的
technical literal 保持原文，不做翻译。spec reviewer 默认使用 spec 的主要语言
返回 findings。所有读取 approved spec 的只读 reviewer，包括 code reviewer，都
默认跟随 spec 的主要语言；用户另有要求时服从用户要求。

语言规则只约束文档和 review 输出，不改变代码注释、UI copy 或项目本身的语言
规范。简单任务不能因为默认中文而增加无关说明。

## 4. 系统组成与数据流契约

### 4.1 系统组成与职责

每份 substantial spec 必须把系统解释为一组有明确用途的组件。对于每个组件，
spec 需要说清楚：

- 它负责什么；
- 它拥有哪部分状态或业务事实；
- 它接收什么、产出什么；
- 它依赖哪些其他组件；
- 当边界可能影响实现时，哪些相邻职责明确不属于它。

目标是形成一致的 ownership model，不是为每个架构标签创建一个文件或类型。
简单系统可以用连续短段落说明；只有在关系复杂时才使用 tree、table 或关系图。

### 4.2 Canonical data 与结构关系

每个被修改的业务概念必须有明确的 canonical representation 和 owner。相关结构
之间的关系必须说明为 containment、reference、derivation、projection 或有理由的
duplication。

结构决策遵循以下优先级：

1. 现有结构的语义和 invariant 一致时，直接复用；
2. 使用组合或引用表达真实的包含关系；
3. owner 和生命周期不变时，扩展现有结构；
4. 只有存在独立语义、invariant、ownership、生命周期或真实 boundary contract
   时，才新增结构。

一个业务事实只有一个 canonical owner。derived、cached、serialized 或 projected
副本必须指向该 owner；当正确性依赖同步时，还必须说明 refresh、invalidation 或
consistency rule。

### 4.3 Boundary 与转换理由

目标是消除没有语义理由的转换，不是追求绝对零转换。

独立 DTO、adapter model、projection、persistence record、wrapper 或 mapping 只有
在表达以下可观察边界时才合理：

- 校验不可信的外部输入；
- public API 或 protocol version compatibility；
- 过滤敏感或不可访问字段；
- serialization、unit 或 wire format 差异；
- persistence constraint 与 runtime model 确实不同；
- 建立新的 invariant 或业务语义。

层级名称不能单独构成理由。同形的 `InternalDTO`、`ServiceDTO`、entity、model、
state object 或 wrapper 必须复用、组合、合并，或者给出明确理由。每个保留的转换
必须说明 source、target、owner、增加或丢失的信息，以及真实 boundary reason。

### 4.4 结构决策与数据流

spec 必须把重要结构明确判定为 reused、extended、merged、replaced、added 或
removed，并解释 input-to-core 和 core-to-output 数据流，包括 validation、
derivation、persistence、serialization 和 projection 发生的位置。

表达形式随任务复杂度调整。skill 必须要求这些决策，但不强制固定表格、关系图、
字段清单或数据库模板。如果 persistent、domain、transport、cache、event、
configuration 和 UI-state structure 都没有变化，spec 应直接明确说明并保持简短。

## 5. 内嵌 Implementation Slices 契约

executable spec 在 `Implementation Slices` 下包含唯一的执行大纲。slice 是按依赖
排序、能够独立测试和 review 的结果，不是微步骤说明。

external todo artifact 指 spec 外部任何重复记录 slice 状态的第二个文件、tool
state 或 ledger。spec 内嵌 checkbox 是 canonical slice status，不违反这条规则。

每个 slice 必须包含：

- 稳定 ID 和以 outcome 命名的标题；
- 批准 baseline 中的 unchecked progress marker；
- 完成 slice 时可以观察到的 outcome；
- 对前置 slice 的依赖，或者 `None`；
- 涉及的系统组件和职责边界；
- 重要数据结构与转换决策，或者明确说明没有变化；
- 预计 create、modify 或 delete 的精确文件；
- 该 slice 证明的 acceptance criterion ID；
- focused 和 broader verification command；
- 当 slice 跨组件、风险较高或被后续工作依赖时，声明 read-only review gate。

slice 不包含生产代码片段、完整测试实现、逐次编辑指令、commit 命令、时间估算
或 implementer subagent 分工。

实现阶段由主 Agent 按依赖顺序处理 slice。每个 slice 内执行
RED-GREEN-REFACTOR，运行声明的 focused/broader verification，完成 read-only
review gate，然后才能把 progress marker 从 unchecked 改为 checked。progress
marker 只表示状态，不改变批准的行为定义。

如果后续实现或 review fix 修改了某个已完成 slice 所证明的行为或文件，主 Agent
必须把该 slice 恢复为 unchecked，重跑受影响的 verification 和 evaluator/review
gate，取得 fresh evidence 后才能重新勾选。

只用于记录 RED baseline 的 evidence-only slice 是实现前行为的不可变历史证据。
预期中的后续 GREEN 修改不会重新打开它；只有 fixture、rubric、sampled response、
recorded scoring 被修改或证据被证明无效时，才恢复为 unchecked。

修改 slice outcome、system ownership、data decision、interface、acceptance
criteria 或 scope 属于 semantic spec change。主 Agent 必须停止实现、修订 spec、
重复适用的 spec review、取得用户批准，并单独提交修订后的 spec，不能在实现过程
中静默改变 authority。

## 6. 目标文件

### 新建

- `docs/superpowers/specs/2026-07-26-system-composition-and-implementation-slices-spec.md`
  - 本次改动的批准 authority 和 `BASE_SHA` 文档。

### 实现阶段修改

- `skills/brainstorming/SKILL.md`
  - 加入默认中文语言契约。
  - 加入 system composition 和 data flow contract。
  - 用内嵌 `Implementation Slices` contract 替代 `Behavioral slices`。
  - 定义逐 slice 主 Agent TDD 和 progress-marker 语义。
- `skills/brainstorming/spec-document-reviewer-prompt.md`
  - 默认使用 spec 的主要语言返回 findings。
  - 把职责不清、重复 model、无理由转换和不可执行 slice 设为 blocking finding。
- `skills/requesting-code-review/SKILL.md`
  - 让 review checkpoint 与完成的 implementation slice 对齐，同时保持批准 spec
    是唯一 authority。
- `skills/requesting-code-review/code-reviewer.md`
  - 默认使用 approved spec 的主要语言返回 findings。
  - 检查未批准结构、重复 canonical fact、同形 DTO chain、不必要 mapper，以及
    偏离 spec transformation boundary 的实现。
- `skills/verification-before-completion/SKILL.md`
  - 最终实现提交前，要求每个 implementation slice 和 acceptance criterion 都有
    fresh completion evidence。
- `tests/workflow/test-spec-to-tdd-consistency.sh`
  - 为新 contract、默认中文和 reviewer coverage 增加确定性 assertions。
- `README.md`
  - 将单一 spec workflow 描述为 system design 加内嵌、依赖有序的执行大纲。

除以上文件外，不预期修改其他 active skill、harness integration、manifest 或测试
文件。需要扩大范围时，先停止实现并修订本 spec。

## 7. 接口与边界契约

### Executable spec authority

批准 spec 保持唯一 implementation authority。内嵌 slice list 是 spec 的组成部分，
不是第二份 workflow 文档。`BASE_SHA` 仍然是只包含批准 spec 的 commit。

### Progress marker

canonical slice status 使用 Markdown checkbox：

```text
- [ ] 尚未完成
- [x] 已通过声明的 verification 和 review evidence
```

正常实现中只更新 marker。checked 不表示“测试文件已经存在”，而表示该 slice 的
outcome、acceptance criteria、verification command 和 review gate 全部通过。

### Review authority

spec reviewer 和 code reviewer subagent 保持只读，只返回 findings。主 Agent 负责
判断 findings、执行全部编辑，并通过 TDD 修复。

当缺少 composition、ownership、relationship、transformation、redundancy、
dependency 或 completion detail 会迫使 implementer 临时做设计时，spec reviewer
必须阻止批准。

code reviewer 对照批准的 canonical structure、ownership、transformation 和已完成
slice 审查完整实现。除非新同形 model 或 conversion layer 实现了 spec 已批准的真实
boundary，否则必须报告 finding。

### 比例原则

contract 是强制的，篇幅按任务复杂度调整。简单 configuration change 可以用几句
话说明没有数据结构或转换变化，并只包含一个小 slice；跨组件 feature 则提供足以
消除真实设计歧义的关系和决策。是否合格取决于 decision coverage，不取决于文档
长度。

## 8. Implementation Slices

- [ ] **S1. 建立 RED workflow 与行为证据**

  **Outcome：** 确定性 workflow assertions 和 fresh-context baseline evaluation
  证明当前 skills 尚未强制 composition、transformation、redundancy、slice 和默认
  中文 contract。

  **Depends on：** None

  **System scope：** 只修改 workflow consistency test 并运行只读 skill behavior
  evaluation，不修改生产 skill 文本。

  **Data decisions：** 不改变 runtime data structure。evaluation fixture 使用同形
  DTO chain、模糊 ownership 和英文默认输出作为可观察 failure stimulus。

  **Files：** 修改 `tests/workflow/test-spec-to-tdd-consistency.sh`。

  **Acceptance criteria：** AC-10。为 AC-1 至 AC-9、AC-11 和 AC-12 建立 RED
  evidence，不声称它们已经 GREEN。

  **Verification：** 新 assertion 加入后，focused
  `tests/workflow/test-spec-to-tdd-consistency.sh` 必须在 skill 修改前失败；broader
  `tests/workflow/run-tests.sh` 必须报告同一个预期失败。使用当前未修改的 skill 或
  reviewer surface，对固定 fixture F1-F6 和 F7 中文默认组各运行 5 个
  fresh-context samples。只有至少 3/5 samples 违反该 fixture rubric，才建立 RED；
  否则停止并移除或缩小相应 guidance。F7 英文 override 组不是 RED failure
  hypothesis，不在 S1 评分。每个 response 都必须人工评分和记录。

  **Review gate：** None。主 Agent 检查 RED evidence 后才能继续。

- [ ] **S2. 让 executable spec 描述系统结构和执行路径**

  **Outcome：** `brainstorming` 默认用中文生成 spec，并要求比例合适的 system
  composition、canonical ownership、data relationship、justified transformation、
  redundancy decision 和 implementation slices，可直接进入主 Agent TDD。

  **Depends on：** S1

  **System scope：** executable-spec authoring 和公开 workflow 描述。

  **Data decisions：** spec 用同一个比例化 composition model 描述 domain、
  transport、persistence、cache、event、configuration 和 UI-state structure，
  不增加 registry 或第二份文档。

  **Files：** 修改 `skills/brainstorming/SKILL.md` 和 `README.md`。

  **Acceptance criteria：** AC-1 至 AC-5、AC-10、AC-11、AC-12。

  **Verification：** focused `tests/workflow/test-spec-to-tdd-consistency.sh`；
  broader `tests/workflow/run-tests.sh` 和 `git diff --check`。

  **Review gate：** Mandatory。使用 candidate `brainstorming` guidance 对 F1、F2
  和 F7 中文默认组各运行 5 个 fresh-context samples，再对 F7 英文 override 组
  运行 5 个 samples。每组必须 5/5 完整通过 rubric。failed run 后产生的新 wording
  variant 必须重新运行自己的全部 guided sample groups，并与 S1 control 对照。
  没有 GREEN evidence 不能进入 S3。

- [ ] **S3. 在只读 review 中执行同一架构约束**

  **Outcome：** spec review 阻止 ownership 缺失和无理由转换，code review 捕获实现
  阶段的重复结构与 mapping，同时不取得 implementation authority。

  **Depends on：** S2

  **System scope：** read-only spec review、code review 和 slice review checkpoint。

  **Data decisions：** reviewer 读取批准 spec 的 canonical structure 和
  transformation decision，不建立独立 architecture model。

  **Files：** 修改 `skills/brainstorming/spec-document-reviewer-prompt.md`、
  `skills/requesting-code-review/SKILL.md` 和
  `skills/requesting-code-review/code-reviewer.md`。

  **Acceptance criteria：** AC-6 至 AC-8、AC-10、AC-12。

  **Verification：** focused `tests/workflow/test-spec-to-tdd-consistency.sh`；
  broader `tests/workflow/run-tests.sh`。对 spec-reviewer prompt 运行 F3，对
  code-reviewer prompt 运行 F4，各 5 个 fresh-context samples。每个 sample 必须为
  对应 reviewer 的全部 seeded defects 返回 blocking findings，并使用 fixture 中
  approved spec 的主要语言；需要 5/5 通过。修订 wording 后必须重新运行 5 个
  guided samples 并与 S1 control 对照。

  **Review gate：** Mandatory read-only code-quality review，范围覆盖 S1-S3 完整
  diff。reviewer 只返回 findings。

- [ ] **S4. 闭合完成状态与全文一致性**

  **Outcome：** 最终 verification 证明所有内嵌 slices、acceptance criteria 和
  review gates，全部 active workflow surface 使用同一套 single-spec、main-agent
  implementation process。

  **Depends on：** S3

  **System scope：** completion verification 和 deterministic workflow
  consistency。

  **Data decisions：** 不新增数据结构。slice marker 是批准 spec 内的状态，不是
  独立 progress store。

  **Files：** 修改 `skills/verification-before-completion/SKILL.md`，并完成
  `tests/workflow/test-spec-to-tdd-consistency.sh` assertions。

  **Acceptance criteria：** AC-5、AC-9 至 AC-12。

  **Verification：** focused `tests/workflow/run-tests.sh`；broader 为
  `docs/testing.md` 记录的全部相关 harness tests、Bash/Node/JSON syntax checks、
  `git diff --check` 和最终 working-tree inspection。使用完成后的 guidance 对 F5、
  F6 各运行 5 个 fresh-context samples。F5 必须 5/5 拒绝错误完成；F6 必须 5/5
  选择 dependency-ready slice、保持主 Agent TDD，并仅让 subagent 提供只读
  findings。修订 wording 后必须重新运行 5 个 guided samples 并与 S1 control 对照。

  **Review gate：** Mandatory final read-only code review，范围为 `BASE_SHA` 到完整
  working tree。每个有效 Critical 或 Important fix 后重新运行 fresh verification
  和 review。

## 9. 验收标准

- **AC-1 - 系统组成：** 每份 substantial spec 都能识别有意义的组件、职责、拥有
  状态、输入、输出、依赖和必要排除项，不要求每个 layer 对应一个新类型。
- **AC-2 - Canonical ownership：** 每个变化的业务事实只有一个 canonical owner；
  相关结构通过 reuse、composition、reference、derivation、projection 或 justified
  duplication 表达。
- **AC-3 - 只保留必要转换：** 每个 DTO、wrapper、adapter model、projection、
  persistence record 或 mapper 都指向真实 boundary，并说明信息或 invariant 变化；
  layer name 不能单独构成理由。
- **AC-4 - 冗余决策：** spec 把重要结构判定为 reused、extended、merged、
  replaced、added 或 removed，并明确处理同形内部结构。
- **AC-5 - 可执行 slices：** 唯一 spec 包含 dependency-ordered、outcome-oriented
  checkbox slices，写明 components、data decisions、exact files、acceptance
  references、verification commands 和 proportional review gates，不包含 micro-step
  implementation plan。
- **AC-6 - Spec review：** 当 ownership 不清、结构重复、转换无理由或 slice 不完整
  会迫使实现阶段发明设计时，只读 spec reviewer 将其作为 blocking finding。
- **AC-7 - Code review：** 只读 code reviewer 检查未批准结构、重复 canonical
  facts、同形 DTO chains、pass-through mapper、不必要转换和 boundary violation。
- **AC-8 - 顺序执行：** 主 Agent 按依赖顺序通过 TDD 实现 slices，完成全部编辑和
  修复，验证 slice、通过 review gate 后再标记完成。
- **AC-9 - 完成证据：** 最终完成要求所有 slices 已勾选，每条 acceptance criterion
  和 review gate 都有 fresh evidence；被后续改动影响的普通 slice 会重新打开。
- **AC-10 - 单一 authority：** 不引入独立 plan、外部 todo artifact、progress
  store、worktree workflow 或 implementer subagent。
- **AC-11 - 比例原则：** 简单改动可以简短说明没有结构或转换变化；复杂改动只
  提供消除真实设计歧义所需的信息。
- **AC-12 - 默认中文：** executable spec 默认使用中文；用户或项目 authority
  明确要求其他语言时覆盖默认值。technical literal 保持原文，review finding 默认
  跟随 approved spec 的主要语言，包括 spec review 和 code review。

## 10. 测试与行为评估映射

### 固定行为 fixtures

- **F1 - 长时间订单 feature：** 要求为一个订单系统撰写 executable spec。输入
  架构包含 `OrderRequest -> CreateOrderDTO -> OrderCommand -> OrderEntity ->
  OrderModel -> OrderResponseDTO`，内部结构重复相同字段且没有提供语义边界。合格
  输出必须识别组件和 canonical ownership，裁决每个结构与转换，在语义一致时使用
  composition，并提供 dependency-ordered outcome slices 和 completion evidence，
  不写 micro-steps。
- **F2 - 简单 configuration change：** 要求为一次配置 key rename 撰写 spec，
  persistent、domain、transport、cache、event、configuration shape 和 UI-state
  structure 均不改变。合格输出简短说明 no-data-change，并只提供一个比例合适的
  slice，不虚构 schema inventory 或额外组件。
- **F3 - 缺陷 spec review：** 输入 spec 包含模糊 component ownership、F1 的同形
  DTO chain、只用 layer name 解释的转换，以及缺少 dependency/completion evidence
  的 slice。合格 reviewer 返回 `Issues Found`，将每个 seeded defect 判定为阻止
  直接实现的问题。
- **F4 - 冗余 implementation review：** 批准 spec 只有一个 canonical `Order`；
  implementation diff 新增重复 canonical fields、`InternalOrderDTO` 和没有新边界
  的 pass-through mapper。合格 reviewer 把每个 seeded deviation 报告为 Critical
  或 Important，使用 approved spec 的主要语言，并保持只读。
- **F5 - 错误完成声明：** spec 有一个 unchecked slice，另一个 completed slice
  缺少已声明 review evidence，然后要求声明完成。合格 evaluator 拒绝完成并指出
  两个缺失 gate。
- **F6 - 恢复顺序实现：** 批准 spec 有一个 completed slice、一个
  dependency-ready slice 和一个仍被阻塞的后续 slice，然后要求继续。合格
  evaluator response 选择 dependency-ready slice，声明主 Agent 第一个实现动作是
  RED test，并且只在声明的 read-only review 中使用 subagent。
- **F7 - 默认语言：** 用户用中文讨论需求，没有要求其他语言，项目也没有相反的
  authoritative language rule。合格 spec 使用中文叙述，technical literal 保持
  原文。GREEN evaluation 的第二组明确要求英文；合格 spec 必须改用英文，证明
  用户要求能够覆盖默认值。S1 只把中文默认组作为 RED control。

| Criteria | Owning slice | Deterministic proof | Behavior proof |
|---|---|---|---|
| AC-1, AC-2 | S2 | workflow test 要求 `brainstorming` 包含 system composition 和 canonical ownership | F1 guided samples 5/5 识别 components、ownership 和 containment |
| AC-3, AC-4 | S2 | workflow test 要求 author contract 包含 transformation justification 和 redundancy decisions | F1 guided samples 5/5 合并、删除或明确解释 seeded DTO 和 mapper |
| AC-5 | S2 | workflow test 要求 implementation-slice fields 并排除第二份 workflow document | F1 guided samples 5/5 生成 outcome slices，不生成 code-level micro-steps |
| AC-6 | S3 | workflow test 要求 spec reviewer 检查 composition、redundancy、transformation 和 slice | F3 guided samples 5/5 为全部 seeded defects 返回 `Issues Found` |
| AC-7 | S3 | workflow test 要求 code reviewer 检查 canonical data 和 conversion | F4 guided samples 5/5 报告全部 DTO-chain 和 mapper defects |
| AC-8, AC-10 | S4 | 现有 main-agent/read-only-review assertions 保持绿色，新 assertions 覆盖 slice order 和 authority | F6 guided samples 5/5 保持主 Agent 有序 TDD、reviewer 只读 |
| AC-9 | S4 | workflow test 要求 `verification-before-completion` 检查 slice 和 acceptance completion | F5 guided samples 5/5 拒绝 unchecked 或未 review 的 slice |
| AC-11 | S2 | workflow test 要求 explicit proportional/no-data-change path | F2 guided samples 5/5 简短处理 no-change，不强制 inventory |
| AC-12 | S2, S3 | workflow test 要求默认中文，spec/code reviewer 跟随 approved spec 语言 | F7 中文默认组、F3 和 F4 各 5/5 使用中文；F7 英文 override 组 5/5 使用英文 |

skill-behavior sample 必须人工评分。只有 required decision 出现在 evaluator 自己的
输出或 finding 中才算通过；仅引用 prompt、复述 prohibition，或者只列 DTO 而不做
裁决均不计分。

## 11. 迁移与兼容

不改变 runtime data、public API、plugin manifest、installed skill path 或 harness
integration。现有批准 spec 作为历史 artifact 继续有效；新的 substantial spec
采用更强 contract。

workflow 继续使用 approved-spec commit 作为 `BASE_SHA`。现有 review tooling
继续检查 baseline 之后的 committed、staged、unstaged，以及明确列出的 untracked
implementation files。

本次属于 skill guidance behavior change。部署前必须取得 fresh RED/GREEN evaluator
evidence 并通过完整 deterministic workflow suite。如果 wording 导致 spec 退化成
code-level plan、在章节之间机械重复同一信息、拒绝合理的 external-boundary DTO，
或在用户明确要求英文时仍输出中文，则验收失败，提交前必须收紧规则。
