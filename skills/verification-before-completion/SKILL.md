---
name: verification-before-completion
description: 用于准备声称任务、修复、分析、交付物、迁移或实现已经完成、正确或通过时；必须在提交、发布、交接或结束工作之前使用
---

# 完成前验证

## 概述

没有新鲜证据就声称完成，不是高效，而是不诚实。

**核心原则：先证明，再声明。**

## 不可违反的规则

```
没有新鲜验证证据，就不能声称完成
```

如果当前消息里没有运行或检查能直接证明声明的证据，就不能说它已经通过、正确、完成、修复、可发布或准备好。

已批准 spec 拥有声明的完成证据。短任务没有 spec 时，明确指出能够证明当前声明的直接观察或命令。

## 验证门槛

在任何完成声明之前：

1. **确定声明**：把要说的话改写成可证伪的命题，明确 subject 是具体 slice、spec 还是 overall goal，并定位当前完成层级。
2. **定位证据**：找到能够直接证明该命题的检查、命令、产物或 observation。
3. **执行完整验证**：现在运行它，不依赖旧输出或他人摘要。
4. **阅读完整结果**：检查退出码、失败、警告、跳过项、覆盖范围和证据边界。
5. **比较声明与证据**：只选择最高、适用且有新鲜证据支持的层级；证据冲突时报告冲突。
6. **然后再表达结论**：把结论和证据放在一起，并明确仍未完成的适用上层。

跳过任何一步，都不是验证。

完成层级依次为 `implementation green`、`review closed`、`spec complete`、`local runtime accepted`、`external/testnet/remote accepted` 和 `overall goal complete`。每个完成声明都携带可定位 subject，例如 `S2: implementation green`、`<spec path>: review closed` 或 `<overall goal>: incomplete`；不能用无 subject 的局部层级暗示整个目标。较低层级不能替代较高层级的独立证据；不必罗列不适用层级。声称某 subject 达到 `review closed` 或更高层级前，确认它没有活跃 reviewer 或相关 agent session。

## 按 Evidence Profile 验证

### Behavior Evidence（软件行为证据）

用于软件行为修改：

- 逐项执行 spec 中 criterion 对应的 Oracle，对照通过条件，原位回填 Evidence，并保持声明的覆盖边界；
- 运行 spec 映射的聚焦测试、扩展测试、build、lint、format 和 integration 检查；
- 确认测试实际覆盖目标行为，而不只是命令退出 0；
- 检查 schema、serialization、binding、API、兼容和迁移消费方；
- 阅读从已批准 `FULL_BASE_SHA` 到当前 working tree 的完整任务 diff；
- 代码在验证后发生变化时，重新运行受影响的检查。

### Research Evidence（研究证据）

用于分析和研究：

- 检查真实来源、提取结果和可定位引用；
- 验证 authority、时间、范围和覆盖边界；
- 检查独立印证、矛盾、反证和未解决未知项；
- 明确区分已验证事实、推断、`NOT VERIFIED` 和假设；
- 确认结论没有超出证据。

测试和代码输出不能证明人工判断正确；它们只能证明产生这些输出的软件行为。

### Artifact or State Evidence（产物或状态证据）

用于写作、数据、配置、迁移和运维：

- 检查目标 artifact 或真实前后状态，而不只检查命令成功；
- 验证格式、完整性、语义、消费方和受保护状态；
- 适用时证明 provenance、回滚或恢复路径；
- 检查副作用是否落在 spec 允许范围内；
- 对外部系统使用读回、状态查询或消费方验收。

文件存在不等于内容正确；命令成功不等于目标状态已经成立。

## 常见失败

| 失败方式 | 为什么不成立 |
|---|---|
| “应该已经可以了” | 推测不是证据。 |
| 引用之前的测试 | 之后的改动可能使证据失效。 |
| 只运行一部分检查，却声称整体通过 | 局部证据不能证明整体。 |
| 相信 reviewer 或 subagent 的结论 | 报告是输入，不是完成 authority。 |
| 看到文件存在就说产物正确 | 存在性不证明格式、语义或完整性。 |
| 来源很多就说研究可靠 | 数量不证明 authority、覆盖或独立性。 |
| 因为任务太长或上下文快满而结束 | 时间压力不会降低完成门槛。 |

## 需求复核

逐行重新阅读已批准 spec。已勾选进度标记本身不是证据。确认每个 slice 都有新鲜、可定位的证据；后续工作影响到某个 slice 时，重新打开它。

Reviewer finding 是证据输入，不是 authority：

```
reviewer 报告问题 -> 对照 spec/artifact 复现 -> 验证证据 -> 主 agent 修复
```

绝不让 reviewer 实施修改，也不采信没有证据支持的 finding。

## 完成交接

Behavior-evidence 软件工作交接前：

1. 重新阅读已批准软件 spec，并验证每条验收标准。
2. 在当前 tree 上运行完整的相关验证。
3. 检查最终 diff，确认只有预期修改。
4. 只有用户或治理流程授权时才提交、push、merge 或创建 PR。

Research evidence 和 artifact/state evidence 以 spec 声明的报告、产物、状态或交接结束。除非某个软件 slice 单独要求，否则不需要代码提交或开发分支流程。

验证后发生的任何变化都会使受影响证据失效。完成声明前重新运行相关检查。

## 必须停下的信号

- 用“应该”“大概”“看起来”表达成功；
- 依赖旧的运行结果；
- 把 reviewer 或 subagent 报告当作证明；
- 从局部检查推断整个任务；
- 未检查覆盖范围就把来源数量当作研究质量；
- 把文件存在当作语义正确；
- 把测试当作分析结论正确的证明；
- 因任务太长或上下文快满而结束。

出现任何上述信号时，找出缺失证据并完成验证，然后再继续。
