---
name: brainstorming
description: 用于开始或恢复具有相互依赖阶段、重大不确定性或风险、需要持久保存进度、很可能跨越上下文边界的长任务，或用户明确要求 brainstorming、plan 或 specification 时；不用于一次完成的短任务，也不用于被派遣的只读审查和评估
---

# 用 Brainstorming 编写 Executable Spec

<READ-ONLY-REVIEWER-STOP>
如果你被派遣为只读 reviewer 或 skill 行为 evaluator，只执行分配给你的审查或评估。不要创建、修改、批准或推进 executable spec；不要编辑文件、实施修复、运行实现任务或提交变更。
</READ-ONLY-REVIEWER-STOP>

## 概述

把长任务整理成一份 executable spec，用它保存意图、约束执行、记录进度并定义完成证据。Spec 的详细程度取决于真实决策面，不要把所有任务强行写成软件开发形状。

<HARD-GATE>
在长任务的目标、authority、交付物、执行 slice、完成证据和修订条件全部写进同一份 spec 之前，不要开始执行。只有本 skill 正确触发后才应用此门槛；短小、自包含的任务不需要 spec。
</HARD-GATE>

<LANGUAGE-HARD-GATE>
编写 spec 前，按以下优先级锁定唯一叙述语言：用户直接要求、项目 authority 中的语言规则、现有 spec 已使用的语言，最后默认使用中文。

如果用户使用中文讨论需求，且没有更高优先级规则要求其它语言，整份 spec 必须使用中文。标题、正文、验收标准、证据描述和 slice 标签都要中文化。只有标识符、API 字段、命令、路径和精确错误等必要技术字面量保留原样。中文 spec 中的英文叙述标签属于语言漂移，不属于技术字面量。

除必要技术字面量外，整份 spec 始终使用选定的语言。
</LANGUAGE-HARD-GATE>

## 短任务

只有同时满足以下条件，任务才算短任务：范围自包含、没有会改变方向的重要分支决策，并且可以在一次连续处理中完成和验证。

短任务不调用本 skill，不创建 spec、plan 或进度产物；直接使用适用的专业 skill，并按任务的自然范围完成和验证。典型短任务包括事实回答、一次只读查询、简单解释，或 contract 已经明确的窄范围操作。小型软件行为修改仍可能需要 `test-driven-development`，但不会因此自动要求单独的 spec。

## 长任务

出现以下任一可观察条件时，使用本 skill：

- 任务包含相互依赖的阶段；
- 工作需要持久保存进度，或很可能跨越上下文边界；
- 重大不确定性或后续决策可能改变执行方向；
- 执行需要整合多个 authority、来源、数据集、组件或系统；
- 副作用、成本、迁移、回滚或其它风险需要显式约束；
- 用户明确要求 brainstorming、plan 或 specification。

本 skill 直接拥有长任务入口、spec 创建与恢复，不再经过其它路由 skill。

## 流程

1. **探索上下文**：阅读项目 authority、已有产物、真实入口、消费方以及近期相关工作。
2. **查找现有 spec**：如果现有 spec 仍拥有同一目标，修改或恢复它；不要分叉出第二份执行大纲。
3. **解决实质决策**：只询问会改变范围、authority、交付物、证据、风险或执行顺序的问题。用户已经做出选择时，不要强迫再次回答。
4. **必要时比较方案**：只有存在真实决策时才提出替代方案；先给推荐结论，再说明取舍。
5. **选择完成证据**：为任务分配 behavior evidence、research evidence、artifact or state evidence，或明确组合。
6. **编写 executable spec**：使用通用 contract，只加入适用 profile 的字段。
7. **自审**：消除占位符、矛盾、歧义、无证据假设、范围漂移和叙述语言漂移。
8. **审查重大风险**：跨组件、高风险或下游关键 spec 使用只读 reviewer。
9. **应用 profile 的执行门槛**：非软件工作完成必要审查后，按照用户的等待或继续指令执行。Behavior-evidence 软件工作只有在书面 spec 获批，或完整设计已被用户审阅且存在明确实现预授权后才能开始；生产修改前提交已批准 spec，并记录 `BASE_SHA`。

## 恢复工作

恢复长任务时：

1. 重新阅读用户指令、项目 authority 和现有 spec。
2. 检查声明的交付物与完成证据，不要只相信对话记忆或已勾选的进度框。
3. 如果某个已完成 slice 的输入、交付物或证据已经过期，重新打开该 slice。
4. 从下一个依赖已满足的 slice 继续。
5. 如果目标、authority、交付物、证据 profile 或风险边界发生实质变化，先修改 spec，再继续执行。

## Executable Spec Contract 结构

Spec 是唯一持久的执行大纲。一个没有对话历史的合格 agent 必须能够依靠它恢复工作，而不需要猜测目标、authority、下一步或完成定义。

每份长任务 spec 都包含：

1. **目标与非目标**：可观察结果和明确排除项。
2. **当前状态与 Authority**：真实起点、优先规则、已有产物和恢复位置。
3. **交付物**：文件、报告、代码、数据或外部状态，以及它们的 owner 和消费方。
4. **执行与数据流**：输入如何形成交付物；不存在数据或状态转换时也要明确写出。
5. **执行 Slice**：按依赖排序、以结果为导向的检查点。
6. **完成证据**：每个 slice 和最终验收所需的证据。
7. **修订条件**：哪些事实或变化会使当前 contract 失效。
8. **最终验收**：完成前必须使用新鲜证据重新验证的全部声明。

不要创建第二份 workflow 文档、implementation plan、todo ledger 或进度产物。Spec 同时拥有范围和进度。

### 执行 Slice

已批准基线中的每个 slice 使用未勾选的 Markdown 进度标记，并用 spec 选定的语言表达以下字段：

- **结果**：slice 完成时可观察到的结果。
- **依赖**：前置 slice ID；没有时写 `无`。
- **工作范围**：受影响的产物、系统、来源或责任边界。
- **输入与 Authority**：所需起始证据和治理来源。
- **交付物**：该 slice 产生的精确产物或状态。
- **完成证据**：证明结果的新鲜证据。
- **验证或审查门槛**：所需检查和只读审查；没有时写 `无`。

只有声明的证据已经存在且可以定位时，才把 slice 标记为完成。如果后续工作改变了它的输入、交付物或证据，重新打开该 slice 并再次验证。

## 完成证据 Profile

### Behavior Evidence（软件行为证据）

用于改变软件行为的工作。除通用 contract 外，还要定义：

- **目标文件**以及每个文件的职责；
- **系统组成与数据流**；
- **关键数据结构与 SSOT**，包括精确字段、层级、owner、关系和转换；
- **接口与边界 contract**，包括精确名称、签名、schema、状态转换、校验和错误；
- 带有软件专用文件与数据决策的 **Implementation Slice**；
- 覆盖可观察成功和失败场景的**验收标准**；
- 从每条标准映射到测试文件、场景和聚焦验证命令的**测试映射**；
- 迁移、兼容、发布与回滚，或者明确写出不适用。

#### 关键数据结构与 SSOT

软件 spec 必须在 Implementation Slice 之前把结构设计摊开，不能只写“新增 model”“调整 DTO”或把结构留给实现阶段决定。

1. **结构清单**：逐个列出所有关键结构，包括 domain entity/value object、command、event、config、持久化记录、transport request/response 和跨模块 model。为每个结构写出精确名称、所属 module/file、所属层级、职责、生命周期、构造方、读写方和消费方。
2. **完整定义**：使用目标语言的 declaration、伪代码或字段表写出完整字段与类型，并标明 required/optional、默认值、单位、合法范围和不变量。只列结构名称或几个示例字段不算完成。
3. **层级与关系**：明确结构之间的嵌套、包含或引用关系，以及 identity、parent/child 和 ownership 边界。用结构树或关系表说明谁持有谁、谁只保存 ID/reference、谁能够修改状态。
4. **业务事实 SSOT**：为每项业务事实指定唯一 canonical owner 和 representation，并列出合法 writer 与 reader。其它结构只能引用它，或成为有明确边界理由的只读 projection；projection 不得成为第二个 authority，不得独立校验、推导或更新同一业务事实。
5. **重复表示门槛**：两个结构若共享大部分业务字段，默认视为同一表示。优先复用 canonical type、组合已有 value object，或只保存 identity/reference。仅重命名、逐字段复制、包装或格式转换，不能证明新结构合理；“解耦”“分层更干净”也不是充分理由。
6. **允许的 projection**：只有 transport、persistence、外部协议、版本兼容或安全裁剪确实要求不同 shape 时，才允许字段重叠。Spec 必须说明该 projection 为什么不能直接复用 canonical type、它删除或增加了什么、是否可逆、由谁转换，以及如何保证它永远不拥有业务规则。
7. **转换表**：逐项列出 `source -> target`、触发边界、owner、消费方、字段如何增加、删除、重命名、校验或编码，以及无法复用 canonical type 的边界理由。若转换不增加或删除任何语义，只做机械逐字段复制，应删除该转换层或合并结构。
8. **结构验收**：验收标准和测试映射必须覆盖 canonical owner 的不变量、合法 writer、serialization、边界转换、round-trip/不可逆裁剪，以及任何 projection 不得绕过 canonical owner 直接形成下一层业务状态。

每个软件 **Implementation Slice** 还包含：

- **文件**：预计创建、修改或删除的精确文件；
- **数据决策**：引用上面的结构定义和转换条目，说明该 slice 创建或修改哪些结构；不得在 slice 中临时发明未进入 SSOT 设计的新 model；
- **验收标准**：该 slice 证明的精确 criterion ID；
- **聚焦验证**：针对直接行为的精确命令；
- **扩展验证**：变更 contract 所需的最小下游或集成命令；
- **审查门槛**：跨组件、高风险或下游关键工作必须单独只读审查，否则写 `无`。

把所有结构关系归类为 containment、reference、derivation、projection 或有理由的 duplication。除非上述真实边界能够证明分离合理，否则把相同形状的 DTO、command、entity、model、state object 和 wrapper 视为同一结构。

主 agent 为这些 slice 调用 `test-driven-development`。跨组件、高风险、公共 contract 或下游关键行为完成后，必须进入 `requesting-code-review`；reviewer 返回 findings 时进入 `receiving-code-review`，按授权边界处理完毕后再进入 `verification-before-completion`。未命中强制 review 门槛的软件行为可直接进入最终验证。

### Research Evidence（研究证据）

用于分析和研究。除通用 contract 外，还要定义：

- 核心问题与明确排除项；
- 已知事实、假设和未知项；
- 来源与 authority 优先级；
- 证据门槛和覆盖边界；
- 收集、提取、比较和综合方法；
- 独立印证、矛盾与反证的处置方式；
- 已验证事实、推断、`NOT VERIFIED` 和未解决不确定性的输出标签。

人工研究和判断不使用 TDD。如果某个 slice 为收集或分析创建、修改可复用软件行为，只对该 slice 使用 TDD。只有声明的证据已经存在，并且报告没有超出证据，结论才算完成。

### Artifact or State Evidence（产物或状态证据）

用于写作、数据整理、配置、迁移、运维和其它长交付物。除通用 contract 外，还要定义：

- 目标产物或前后状态；
- 允许的副作用和受保护状态；
- 完整性、格式、语义或消费方检查；
- 适用时的回滚、恢复或 provenance 证据；
- 下游验收和未改变的行为。

只有改变软件行为的 slice 使用 `test-driven-development`。其它 slice 使用 artifact/state contract 声明的检查。

### 混合任务

一份 spec 可以组合多个 profile。逐 slice 指定完成证据。不能因为某个 slice 使用代码，就把整个分析、迁移或写作任务归类为软件实现。

### 长时间 Debugging

长时间 debugging 使用一份 mixed-profile spec，并调用 `systematic-debugging` 负责诊断方法。根因调查 slice 使用 research evidence 保存复现、边界观测、已排除假设和有证据支持的原因，不使用 TDD。如果需要软件修复，修复 slice 使用 behavior evidence，并且只有修复 slice 调用 `test-driven-development`。如果证据表明无需修改软件，就以 research evidence 结束，不要虚构实现 slice。

## 批准与直接执行

- 如果用户说“先规划”“只写 spec”“执行前给我看”或同义指令，写完并审查 spec 后等待批准。
- 对非软件 profile，如果用户授权直接执行、继续、不要停或同义指令，完成 spec 自审和必要独立审查后，开始第一个依赖就绪的 slice。
- Behavior-evidence 软件工作必须获得书面 spec 批准，或在用户审阅完整设计后获得明确实现预授权。生产修改前，单独提交最终已批准 spec，并把该提交记录为 `BASE_SHA`；实现、review 和最终 diff 验证都使用这个已批准 spec 基线。如果最终 spec 加入了已审阅设计中不存在的实质决策，预授权立即失效。
- 更高优先级的项目指令要求批准或安全门槛时，无论一般执行指令如何都必须遵守。

目标、authority、交付物、证据 profile、风险边界、验收标准或 slice 结果发生变化，属于语义 spec 变化。停止执行、修改 spec、完成必要审查，并在治理规则要求时重新取得批准。

## 审查

长任务或跨范围 spec 使用 `spec-document-reviewer-prompt.md` 派遣只读 reviewer。Reviewer 只报告缺口和矛盾，不编辑文件、不执行任务 slice、不实施修复、不提交变更。主 agent 处理有效 finding，并重复审查，直到没有阻塞问题。

## Spec 完成后

- 把 spec 保存在项目 authority 指定的位置；未指定时默认使用 `docs/superpowers/specs/YYYY-MM-DD-<topic>-spec.md`。
- 只执行依赖已经满足的 slice。
- 只有新鲜完成证据存在后才更新进度标记。
- 只有专业 skill 的自身触发条件成立时才使用它。
- 最后调用 `verification-before-completion`，按照 spec 声明的证据完成验证。

## 指令优先级

用户直接指令以及 `AGENTS.md`、`CLAUDE.md` 等项目 authority 高于任务 spec。Spec 必须引用这些 authority，不能取代它们。
