# 编写有效测试

在编写或修改测试、加入 mock，或为测试增加 cleanup/helper method 时读取本参考。

## 概述

每个测试都应该捕获一种具体破坏。全部规则来自两个原则：

```
1. 每个测试都说清自己能捕获什么破坏
2. 每个测试都运行真实目标
```

严格 TDD 会自然产生这两点：先写并观察失败的测试已经证明自己能失败；只有真实 dependency 被证明太慢或位于外部时，mock 才有存在理由。

## 原则一：说清能捕获什么破坏

写测试正文前，回答：**哪项生产变更应该让这个测试失败？那项变更是 bug，还是有意决策？** 测试只有能捕获错误分支、缺失副作用、错误参数、边界场景或破坏的 contract，才值得存在。

**独立推导期望值。** 优先使用 literal 和人工检查过的 fixture；table-driven test 的 `want` 应该是 literal。用被测代码或它的 helper 计算期望值，无论实现做什么都可能通过：

```typescript
// ❌ 镜像断言：同一个 builder 计算两边，永远相等
const expected = buildSearchQuery({ tag: 'urgent' });
expect(buildSearchQuery({ tag: 'urgent' })).toBe(expected);

// ✅ 人工推导的 literal
expect(buildSearchQuery({ tag: 'urgent' })).toBe('tag:"urgent"');
```

**不要写变化探测器。** 如果测试只能因为有意设计决定而失败，例如 constant 值、精确消息文案或 private structure，它会在重设计时报警，却发现不了 bug。测试依赖该决定的行为：不要断言 `MAX_RETRIES === 5`，而要断言失败调用会重试 5 次，且第 6 次不会发生。

**测试行为，不测试文本。** 断言 script、skill 或 config 包含某一行，只能证明 source 仍是 source。用受控输入运行 script，断言 output、side effect 或 exit code。用于指导 agent 的文档通过消费它的 agent 行为测试；写给人看的 prose 不需要测试。

**测试自己的 contract，不测试 framework。** 测试代码在边界承诺的行为，例如注册的 route、发出的 query、生成的 payload。Upstream mechanics 应由 upstream 测试。只有 upstream 行为确实令人意外时，才写一个窄 characterization test 明确该假设。内部同样如此：constructor、getter、constant 和简单 forwarding 只有在负责校验、标准化、默认、推导、约束或副作用时才单独测试；否则断言第一个依赖它的消费方结果。

### 写测试前的门槛

```
说出哪项生产变更会让测试失败。

说不出来                -> 围绕可观察行为重新设计
“source text 改了”       -> 运行产物并断言效果
只有有意决策会触发       -> 这是变化探测器，改测依赖该决策的行为

确认期望值没有复用被测逻辑或 helper；
复用了就换成 literal 或人工检查 fixture。
```

## 原则二：运行真实目标

**Mock 不配拥有断言。** Mock assertion 只证明 mock 是否存在，没有证明组件行为。断言真实组件；如果你正在检查 mock，就取消 mock 或删除断言。

```typescript
// ✅ 真实行为
expect(screen.getByRole('navigation')).toBeInTheDocument();

// ❌ mock 是否存在
expect(screen.getByTestId('sidebar-mock')).toBeInTheDocument();
```

应主动问：**“我们是不是在测试 mock 的行为？”**

**在正确层级 mock。** 替换真实 method 前先了解它的全部副作用；只 mock 缓慢或外部操作，保留测试依赖的真实行为。不确定时，先用真实实现运行测试，观察真正必须发生什么。

```typescript
// ❌ mock 吞掉了 duplicate detection 依赖的 config write
vi.mock('ToolCatalog', () => ({
  discoverAndCacheTools: vi.fn().mockResolvedValue(undefined)
}));

// ✅ 只 mock 缓慢的 server startup，config write 保持真实
vi.mock('MCPServerManager');
```

**让 test double 具体。** 参数、调用次数或顺序属于 contract 时必须断言；接受任何内容的 fake 什么都没验证。成功、错误和 malformed 分支分别使用 fixture 或 spy，避免错误分支也能满足断言。

**完整模拟真实数据。** Mock 应包含真实结构的全部 documented field，不要只放当前测试读取的字段。Partial mock 会在下游读取缺失字段时静默失真：测试通过，integration 却失败。

**生产 class 只包含生产 method。** 只有测试需要的 cleanup 放进 test utility，不要给生产 class 增加 `destroy()`。检查：这个 method 是否只从测试调用？这个 class 是否真的拥有该 resource lifecycle？答案不对就放入 test utility。

**复杂 mock 应替换为真实组件。** Mock setup 比测试逻辑更大、mock 缺少真实组件 method，或测试总因 mock 变化而坏时，改用真实组件的 integration test。主动问：**“这里真的需要 mock 吗？”**

### 加入 Mock 或 Helper 前的门槛

```
列出真实 method 的副作用；保留测试依赖的真实部分，
只 mock 下层缓慢或外部操作。

Mock response 必须完整对应真实结构。

只有测试调用的 method 放进 test utility，不放生产代码。

准备断言 mock 本身？
  取消 mock 或删除断言。
```

## 测试与实现一起交付

失败测试、最小实现、refactor 构成完整 TDD。只交付行为真正需要的测试：trivial code 和人类 prose 不需要测试；为了满足流程而写的测试会永久增加维护成本。

## Mutation 检查

完成前，在脑中修改生产代码；每种现实 mutation 都应该至少让一个测试失败：

- 错误 constant 或参数；
- 错误分支 handler；
- 缺失状态变化或副作用；
- 空值或默认返回；
- 缺失对 zero、empty、nil、unauthorized 或 malformed input 的校验。

没有测试能捕获的 mutation，说明行为没有被保护，或测试是同义反复。

## 快速参考

| 当前动作 | 应该做什么 |
|---|---|
| 编写任何测试 | 说出它捕获的 bug，而不是有意决策 |
| 构造期望值 | 人工推导，不使用被测代码 |
| 测试 script 或 agent 文档 | 运行它或压力测试消费方，不 grep source text |
| 想测试 dependency | 测试自己的边界 contract，不重复 upstream mechanics |
| 想断言 mocked element | 测试真实组件，或取消 mock |
| 准备 mock method | 了解副作用，只 mock 缓慢或外部层 |
| 构造 mock response | 完整对应真实结构 |
| 测试需要专用 cleanup | 放进 test utility |
| Mock setup 不断膨胀 | 改用真实组件 integration test |
| 完成测试文件 | 运行 mutation 检查 |

## 警告信号

- setup 和 assertion 共享同一对象，保证永远相等；
- 测试只能因 panic、crash 或 selector 不存在而失败；
- 每次有意修改都会失败，却抓不到意外破坏；
- 期望值隐藏在 loop、builder 或 helper 后；
- 测试 grep source text，或断言已删除 symbol 必须继续不存在；
- 即使只剩 framework，测试仍然“有意义”；
- 测试只为 coverage 存在，不检查副作用或结果；
- 断言检查 `*-mock` test ID，或删除 mock 后测试就失败；
- method 只从测试文件调用；
- mock setup 超过测试一半，或无法解释为什么需要 mock；
- “为了保险”而 mock。
