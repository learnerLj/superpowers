# 基于条件的等待

## 核心原则

异步测试应等待真正关心的可观察条件，不要用任意 `sleep` 或固定延迟猜测执行速度。

## 何时使用

出现以下情况时使用：

- 测试在不同机器或负载下偶发失败；
- 代码用固定延迟等待事件、状态、文件或数量变化；
- 并发执行时 timeout，但单独运行通常通过。

如果被测行为本身就是时间语义，例如 debounce、throttle、租约或 deadline，则应测试明确的时钟 contract，优先使用可控时钟；确实使用真实时间时记录依据。

## 通用模式

```typescript
async function waitFor<T>(
  observe: () => T | undefined | null | false,
  description: string,
  timeoutMs = 5000,
): Promise<T> {
  const deadline = Date.now() + timeoutMs;

  while (Date.now() <= deadline) {
    const value = observe();
    if (value) return value;
    await new Promise(resolve => setTimeout(resolve, 10));
  }

  throw new Error(`等待 ${description} 超过 ${timeoutMs}ms`);
}
```

这个 helper 只是模式，不是要求复制的项目代码。优先复用当前测试框架已有的事件等待、fake clock、eventually assertion 或通知机制。

## 使用要求

1. 等待可观察结果，例如目标事件、状态、数量或文件，而不是等待“足够久”。
2. 每次轮询重新读取状态，不使用循环外缓存的旧值。
3. 必须有总 timeout 和包含目标条件的错误信息。
4. 轮询间隔应避免忙等；具体数值服从项目测试基础设施。
5. 条件满足后仍要断言最终业务结果；等待本身不是验证。

## 常见错误

| 错误 | 处理 |
|---|---|
| 任意延迟 | 改为等待目标条件 |
| 没有总 timeout | 增加有限 deadline 和清晰错误 |
| 轮询过快 | 使用项目合理的间隔或事件通知 |
| 只等待内部实现细节 | 改为观察消费方可见状态 |
| 用真实时间测试时间语义 | 优先注入可控时钟 |

只有延迟本身属于被测 contract 时才直接等待时间；此时必须说明时钟来源、预期区间和容差。
