---
name: test-driven-development
description: 用于新增或修改软件行为、bugfix，以及行为保持型重构；行为变化使用 RED-GREEN-REFACTOR，纯重构使用 GREEN 基线保护
---

# 测试驱动开发（TDD）

## 概述

行为变化先写测试，亲眼看到它失败，再写让它通过的最小实现。纯行为保持型重构先证明旧行为已经由绿色测试保护。

**核心原则：行为变化没有先看到测试失败，就无法确认测试是否真的覆盖目标行为。**

**违反规则的字面要求，就是违反规则的精神。**

## 何时使用

以下情况始终使用：

- 新功能；
- bugfix；
- 行为变更；
- 纯行为保持型重构。

只改变已经存在的部署配置值、环境状态或数据，不修改 parser、默认值、校验或其它软件 contract 时，不进入 TDD，也不需要另行取得“跳过 TDD”授权。使用 artifact/state evidence 验证配置源、运行时实际值、消费方效果、服务状态和必要回滚。运行结果发生变化，不等于实现了新的软件行为。

修改 config parser、默认逻辑、校验或其它软件 contract 时，仍属于软件行为变更，必须使用 TDD。

以下软件实现例外必须先得到用户明确授权：

- 随用随弃的 prototype；
- generated code；

“这一次跳过 TDD”这个想法本身就是停下检查的信号。任务很小、时间很紧、已经手工试过，都不是例外。用户明确授权跳过时，可以按非 TDD 工作执行，但必须如实说明未采用 TDD，仍要完成自然范围的验证。

## 铁律

```
新增行为、修改行为或 bugfix 没有先失败的测试，就不能写生产代码
```

这类行为实现先写了代码？删除它，重新开始。

**没有变通方式：**

- 不要把实现保留为“参考”；
- 不要边写测试边“改造”已有实现；
- 不要继续查看它；
- 删除就是删除。

根据测试重新实现。

纯行为保持型重构不制造失败预期。先运行现有相关测试，确认 GREEN，再重构并让相同测试继续 GREEN，最后检查 diff 和结构。测试不足时，先增加 characterization test 并确认它记录旧行为；不要为了制造 RED 写错误预期。重构中需要改变行为时，回到 RED-GREEN。

## RED-GREEN-REFACTOR 循环

有已批准的软件 spec 时，测试和实现必须保持在 spec 确认的 owner 与系统边界内。如果需要新增未批准的状态 owner、状态机、重试、缓存、生命周期或其它通用机制，停止 TDD 并先修订 spec；不得用局部测试把平行系统固化下来。

```text
RED：编写失败测试
  -> 失败原因不对：修正测试，重新确认 RED
  -> 失败原因正确：进入 GREEN

GREEN：编写最小实现
  -> 测试未全部通过：修实现
  -> 测试全部通过：进入 REFACTOR

REFACTOR：在保持全部测试通过的前提下清理实现
  -> 下一个行为：回到 RED
```

### RED：编写失败测试

写一个最小测试，展示目标行为。

<Good>
```typescript
test('retries failed operations 3 times', async () => {
  let attempts = 0;
  const operation = () => {
    attempts++;
    if (attempts < 3) throw new Error('fail');
    return 'success';
  };

  const result = await retryOperation(operation);

  expect(result).toBe('success');
  expect(attempts).toBe(3);
});
```
名称清楚，测试真实行为，只覆盖一件事。
</Good>

<Bad>
```typescript
test('retry works', async () => {
  const mock = jest.fn()
    .mockRejectedValueOnce(new Error())
    .mockRejectedValueOnce(new Error())
    .mockResolvedValueOnce('success');
  await retryOperation(mock);
  expect(mock).toHaveBeenCalledTimes(3);
});
```
名称含糊，而且测试的是 mock，不是实际行为。
</Bad>

要求：

- 一个测试只证明一个行为；
- 名称说明预期行为；
- 使用真实代码，除非 mock 无法避免。

### 验证 RED：亲眼确认失败

**强制要求，绝不能跳过。**

```bash
npm test path/to/test.test.ts
```

确认：

- 测试是断言失败，不是运行错误；
- failure message 符合预期；
- 失败是因为目标行为尚未实现，而不是 typo。

测试直接通过，说明测到了已有行为，应修正测试。测试报错，先修复测试，直到它以正确原因失败。

### GREEN：编写最小实现

只写让测试通过的最简单代码。

<Good>
```typescript
async function retryOperation<T>(fn: () => Promise<T>): Promise<T> {
  for (let i = 0; i < 3; i++) {
    try {
      return await fn();
    } catch (e) {
      if (i === 2) throw e;
    }
  }
  throw new Error('unreachable');
}
```
只实现测试要求的行为。
</Good>

<Bad>
```typescript
async function retryOperation<T>(
  fn: () => Promise<T>,
  options?: {
    maxRetries?: number;
    backoff?: 'linear' | 'exponential';
    onRetry?: (attempt: number) => void;
  }
): Promise<T> {
  // YAGNI
}
```
加入了没有测试要求的设计。
</Bad>

不要增加功能、重构无关代码，或做超出测试要求的“改进”。

### 验证 GREEN：亲眼确认通过

**强制要求。**

```bash
npm test path/to/test.test.ts
```

确认：

- 新测试通过；
- 相关旧测试仍通过；
- 输出干净，没有错误或警告。

测试失败时修实现，不要为了配合实现修改测试。其它测试失败时立即处理。

### REFACTOR：绿色状态下清理

只有 GREEN 后才能：

- 消除重复；
- 改善命名；
- 提取 helper。

始终保持测试通过，不增加新行为。

### 重复循环

为下一个行为写下一个失败测试。

## 好测试的标准

| 标准 | 好测试 | 坏测试 |
|---|---|---|
| **最小** | 只覆盖一件事；名称出现“并且”时考虑拆分 | 一个测试验证多个独立行为 |
| **清楚** | 名称准确描述行为 | `test1` |
| **表达意图** | 展示期望 API 和 contract | 被 setup 或 mock 细节淹没 |

编写或修改测试时，读取 [writing-good-tests.md](writing-good-tests.md)：

- 写测试前先说出哪项生产变更会让它失败；
- 断言真实行为，不断言 mock 行为；
- 测试专用代码放在 test utility，不放进生产 class；
- mock dependency 前先理解它的副作用。

## 常见借口

| 借口 | 事实 |
|---|---|
| “太简单，不用测试” | 简单代码同样会坏，测试通常只需很短时间。 |
| “之后补测试” | 后写测试一开始就通过，不能证明它能发现目标 bug。 |
| “后写测试精神一样” | 后写回答“代码现在做什么”，先写回答“代码应该做什么”；实现会偏置后写测试。 |
| “已经手工测试” | 手工检查不可稳定重放，也容易遗漏边界。 |
| “删除几小时工作太浪费” | 时间已经花掉；保留无法证明的实现才是继续扩大损失。 |
| “保留作参考，再先写测试” | 你会照着它改，这仍然是后写测试。 |
| “需要先探索” | 可以探索，但探索实现必须丢弃，然后从测试重新开始。 |
| “测试很难写” | 这通常说明接口很难使用，应先简化设计。 |
| “TDD 太慢” | 提前发现回归比生产环境 debugging 更快。 |
| “手工测试更快” | 手工测试不证明边界，每次修改都要重新手工检查。 |
| “现有代码没有测试” | 本次变更仍应补上能保护目标行为的测试。 |

## 行为变化必须停下并重新开始的信号

- 新行为、行为修改或 bugfix 代码写在测试之前；
- 实现后才补测试；
- 新测试第一次运行就通过；
- 无法解释为什么失败；
- 说测试以后再加；
- 为“就这一次”找理由；
- “我已经手工测过”；
- “后写也实现相同目标”；
- “重精神，不重形式”；
- “保留作参考”或“根据现有实现改造”；
- “已经投入很多时间，不能删除”；
- “TDD 太教条，我是在务实”；
- “这个情况不一样”。

行为变化出现任何一项，都说明应该删除先写的实现，从失败测试重新开始。只有用户明确授权的例外可以跳过，而且必须标记为非 TDD。纯行为保持型重构按 GREEN 基线路径执行。

## Bugfix 示例

问题：接受了空 email。

**RED**

```typescript
test('rejects empty email', async () => {
  const result = await submitForm({ email: '' });
  expect(result.error).toBe('Email required');
});
```

确认 RED：

```text
FAIL: expected 'Email required', got undefined
```

**GREEN**

```typescript
function submitForm(data: FormData) {
  if (!data.email?.trim()) {
    return { error: 'Email required' };
  }
  // ...
}
```

确认 GREEN：测试通过。

**REFACTOR**：需要验证多个字段时，再提取 validation。

## 完成检查表

完成前确认：

- [ ] 每个新 function/method 都有需要它的测试；
- [ ] 每个新行为或 bugfix 测试都在实现前以正确原因失败过；
- [ ] 只写了让测试通过的最小实现；
- [ ] 所有相关测试通过；
- [ ] 输出干净，没有错误或警告；
- [ ] 测试使用真实代码，mock 只在无法避免时使用；
- [ ] 边界和错误场景得到覆盖。

无法勾选时，就没有执行 TDD，应重新开始或如实声明获得了用户例外授权。

## 下一步

TDD 只拥有 RED-GREEN-REFACTOR 实现循环，不拥有审查或完成声明。重大或高风险功能、复杂 bug、跨组件或公共 contract 变更，以及准备合并的软件变更，下一步使用 `requesting-code-review`；reviewer 有 findings 时使用 `receiving-code-review`，按授权边界处理完毕后再使用 `verification-before-completion`。未命中强制 review 门槛的局部低风险变更可直接进入最终验证。

## 遇到困难时

| 问题 | 处理方式 |
|---|---|
| 不知道怎么测试 | 先写理想 API 和断言；必要时询问用户。 |
| 测试过于复杂 | 设计过于复杂，简化接口。 |
| 必须 mock 一切 | 代码耦合过强，使用 dependency injection。 |
| setup 过大 | 提取 helper；仍然复杂时简化设计。 |

## 与 Debugging 的关系

发现 bug 且根因尚未确认时，先使用 `systematic-debugging` 定位并确认根因。只有进入已授权的软件修复切片后，才以能够复现已确认根因的失败回归测试开始 TDD；不要用猜测出的修复方案反推测试。回归测试既证明修复，也防止复发。

未经用户明确授权，绝不在没有失败测试的情况下修 bug。

## 最终规则

```
行为变化 -> 测试先存在并以正确原因失败
纯重构   -> 相关测试先 GREEN，重构后继续 GREEN
```

只有用户明确授权才能例外。
