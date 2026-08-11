---
name: code-simplification-review
description: 审查代码、模块、本地变更或项目中的过度设计、无必要抽象、wrapper 与分层膨胀、意大利面式分支、巨型文件、错误所有权边界和可维护性退化时使用
---

# 代码简化审查

严格审查代码中的偶然复杂度。在保留真实行为、authority、安全约束和项目所有权边界的前提下，删除不需要存在的概念，得到最小正确实现。

## 先锁定范围

按用户给出的文件、模块、子系统、项目区域、commit、range 或 diff 审查。用户说“我的改动”“当前分支”或“dirty diff”时，审查当前本地变更。只有用户明确要求全项目审查时，才扩大到整个项目。

范围没有明确给出时，只读检查 workspace，选择最小有用范围并说明假设。不要要求必须存在 PR，也不要假定任务与 GitHub 有关。

本 skill 默认只返回审查结果。用户只要求 review、检查或分析时，不编辑代码；只有用户明确要求修复时，才按已确认 finding 进入实现流程。

## 审查原则

1. 判断前先读真实代码路径。涉及架构时，追踪入口、下一跳、owner、状态读写、副作用和消费方。
2. 项目内的 `AGENTS.md`、`CLAUDE.md`、设计原则、架构文档和本地 skill 优先于本 skill。
3. 简化不能删除必要的校验、错误处理、安全检查、无障碍基础、审计能力、资金或账务正确性、并发安全和领域 authority。
4. 不用通用的“代码更少”覆盖项目不变量。代码因维护 authority、显式状态或可恢复性而较长时，应明确保留。
5. 优先删除复杂度，不要只是移动复杂度。把同一组概念分散到更多文件不算简化。

## 简化阶梯

对每一块有意义的代码按顺序判断：

1. 它是否服务于当前消费方、不变量或已验证工作流？
2. 代码库是否已有 canonical type、helper、module、owner 或既定模式？
3. 标准库、语言 runtime、数据库、操作系统、浏览器或平台原语能否直接完成？
4. 已安装依赖能否完成，而且不会产生新的所有权成本？
5. 能否重构状态模型或所有权边界，让分支、模式或 wrapper 直接消失？
6. 能否缩短直接路径，同时不隐藏重要语义？
7. 只有前面都不成立时，才建议新增 abstraction、helper、module、dependency 或配置项。

在第一个能够保留正确性和真实边界的层级停止。

## 重点查找

严格检查：

- 没有当前消费方、已验证路径或明确不变量的代码；
- 只有一个实现的 trait、interface、factory 或 policy object；
- thin wrapper、纯转发 helper、facade、identity conversion，或只给另一个 API 改名的 helper module；
- 重复状态、与 authority object 并行传递的派生字段，或会与 SSOT 漂移的 snapshot；
- 用临时 flag、optional mode、boolean、nullable branch 或 silent fallback 掩盖缺失的状态模型；
- 塞进繁忙共享路径的特殊条件分支；
- 用通用 magic code 隐藏简单数据形状；
- 没有复用 canonical helper 的复制逻辑；
- feature logic 泄漏进共享基础设施，或实现细节泄漏进 public API；
- 让独立步骤更难推理的串行编排；
- 本可原子更新却分批写入的相关状态；
- 接近或超过约 1000 行的文件，或已经需要过多审查工作记忆的大型函数和模块；
- 重复平台或项目能力的新依赖、配置层、runtime store、script 或 helper crate。

## 优先的简化动作

- 删除一层，而不是继续打磨这一层。
- 把逻辑移回已经拥有 authority 的 owner。
- 重构状态模型，让重复条件分支消失。
- 把重复分支合并为一条直接路径。
- 在边界显式表示无效或缺失状态，不把 optionality 向内传播。
- 用标准库、原生能力或平台原语替换自定义实现。
- 把散落在共享代码中的 feature check 收回专门的 model 或 dispatch point。
- 只有拆分后形成清楚所有权时才拆大文件；不要用许多小文件隐藏同一条流程。
- 当编排与业务逻辑分开后两者都会更小时，才分离它们。
- 保持直接路径直接；出现第二个真实消费方后再增加扩展点。

## 领域边界

- 交易、金融、会计、余额、订单状态、风险、执行与对账：不得删除 SSOT、事件 authority、审计轨迹或显式上报状态。
- adapter、provider、client、transport、cache、message bus 与 runtime：事实必须流经 canonical owner，不要为了方便跨层读取另一层内部状态。
- 异步、并发和 runtime：不要用更短的控制流换掉显式取消、timeout、atomicity 或 lifecycle 边界。
- Rust：提出风格判断前，先读取仓库的 Rust 规则、feature flag、format、lint 和 ownership 约定。
- unsafe、FFI 和安全边界：如果缩短代码会让不变量变得隐式，就不属于简化。

## 审查问题

- 谁拥有这个状态或事实？
- 当前谁在消费这段代码？
- 哪条路径证明它是现役能力，而不是推测需求？
- 它让 authority 路径更清楚，还是更间接？
- 重构模型后，这个 branch、helper、wrapper 或 config 能否消失？
- 这个抽象是否由多个真实消费方或硬边界证明了必要性？
- 本地 canonical helper、type 或 module 是否应该吸收它？
- 这次改动是否增加了另一个未来必须同步维护的位置？
- 最简单的版本是否仍然可审计、可恢复？

## 输出

Findings 前置，按影响排序：

1. 能删除概念或恢复正确 owner 的结构性简化；
2. 未使用抽象、wrapper、config、dependency 和推测路径等过度设计；
3. 意大利面式分支、optionality、fallback 和散落的 feature check；
4. 边界、authority、type contract 和状态所有权问题；
5. 文件大小、拆分和可读性问题。

每项 finding 包含：

- 尽可能提供 `scope:path:line`；
- 应删除或重构的复杂度；
- 它为什么会伤害当前项目；
- 更直接的实现方向或 owner 边界。

没有需要删除的实质复杂度时，明确写：`未发现需要实质简化的内容。` 随后说明未读取的路径、未运行的测试或尚未验证的 authority 等审查边界。

## 表达要求

直接、严格、以证据为基础。存在结构性问题时，不要纠缠命名或格式。代码能够运行不代表结构合理，但也不要攻击为了保护真实不变量而保留的显式性。

可以使用以下判断：

- `这个 wrapper 没有形成真实边界；在出现第二个消费方前直接内联。`
- `这个分支正在补偿含糊的状态模型；应在边界显式建模。`
- `这里复制了 authority object；传递 owner，并由 owner 生成 projection。`
- `这是 feature logic 泄漏进共享路径；应移回 canonical owner。`
- `这次重构只移动了复杂度，没有删除任何概念。`
- `这里代码更长有正当理由：它保留了 authority 与审计路径，应当保留。`
