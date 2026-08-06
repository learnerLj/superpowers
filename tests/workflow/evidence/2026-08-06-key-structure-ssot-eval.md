# 软件 Spec 关键结构与 SSOT 行为证据

## 边界

- 日期：2026-08-06（Asia/Shanghai）
- evaluator：`eval_software_task`，只读，不编辑、不实现、不提交
- 场景：Rust order service 同时提议 `CreateOrderRequest`、`OrderCommand`、`Order`、`PersistedOrder`、`OrderResponse`，并在五个结构间重复订单字段和逐字段转换
- 候选 skill SHA-256：`9c40695a56492022f47fd204ea7016f9377925bf3d8a51d6b47eadb6a80b1365`
- workflow test SHA-256：`481b58d01419723732554160c66f4ee332f0068254f84aee8282bd074af09618`

## RED

修改前的 skill 能要求 canonical owner、结构关系和 transformation 理由，但没有强制逐个写出所有关键结构的完整字段、所属层级、owner 和转换表。Evaluator 能依靠自身判断补出较好的表格，同时明确指出：不写这些表也可能字面满足原规则，结构决策仍会被留给实现阶段。

## GREEN

相同场景加载候选 skill 后，spec 被强制在 Implementation Slice 前提供：

- 完整结构清单与字段定义；
- module/file、层级、职责、生命周期、构造方、读写方和消费方；
- containment/reference/identity/ownership 关系；
- 每项业务事实的 canonical owner、representation、writer 和 reader；
- 重复结构处置、projection 证明和完整 `source -> target` 转换表；
- 结构不变量、serialization、round-trip/裁剪和禁止绕过 SSOT 的测试映射。

Evaluator 的结构判断：保留 `Order` 作为唯一 SSOT；`CreateOrderRequest` 只保留非可信输入；仅逐字段复制的 `OrderCommand` 删除或合并；`PersistedOrder` 与 `OrderResponse` 只有真实 persistence、wire protocol、版本或安全边界时才允许存在，并且不得成为第二个业务 authority。

结论：`PASS`。原先“只有原则，没有强制输出形状”的缺口已关闭。
