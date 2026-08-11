---
name: code-path-explainer
description: 用户要求解释某一行或一段代码、理解调用链、追踪执行流程、数据或状态变化、owner、authority、副作用、消费方、错误路径、fallback 或 terminal state 时使用
---

# 代码路径解释

先读真实代码，再用可追溯的 `file:line` 证据解释代码语义和执行路径。链路没有读通时继续查找，或明确说明证据缺口；不用架构常识补齐未知部分。

## 按问题尺度读取

- 用户指向某一行或表达式时，先解释这一行实际做了什么、所在函数和分支、关键变量或返回值的含义；再向上追踪输入和值的来源，向下追踪它改变的状态、控制流和消费方。只读取足以回答问题的路径。
- 用户询问完整流程时，从命令、handler、route、public API、engine method、adapter method、test case 或指定调用点开始，一直读到最终副作用或返回。

## 读取顺序

1. 定位入口或用户指定行所属的函数、类型和模块。
2. 沿调用关系追踪下一跳，记录传递的关键参数、状态和类型转换。
3. 读到最终结果：state write、cache 或 database mutation、message publish、external I/O、event、report、task spawn、error 或 return。
4. 覆盖会改变结论的成功、拒绝、错误、异步边界、fallback、retry 和 terminal state；不要罗列无关分支。
5. 标明谁构造、持有、更新和消费相关状态，以及哪个事实源拥有最终 authority。
6. 优先遵循项目内的 `AGENTS.md`、`CLAUDE.md`、架构文档、领域原则和 canonical helper 或 API。

## 输出

按问题复杂度裁剪回答，优先让用户不必在 IDE 中反复跳转：

- 第一段直接说明本行或整条路径的实际作用、authority 和最终结果。
- 使用连续的 `file:line` 链路说明入口、下一跳、关键分支和终点。
- 解释关键值从哪里来、在哪里变化、由谁读取；不要只复述函数名。
- 明确状态写入、事件、外部调用和其它副作用。
- 只在代码片段能直接证明判断时引用短片段，不复制大段源码。
- 区分代码已经证明的事实、基于现有证据的推断和仍未验证的缺口。
- 用户只要求解释、review 或设计判断时保持只读，不顺手修改代码。

## 不要做

- 不要只画抽象流程，或给出没有代码位置的架构概述。
- 不要用“应该、可能、通常”替代代码证据。
- 不要为了显得完整而追踪与问题无关的所有分支。
- 不要跳过会改变结果的 error path、fallback、retry 或 terminal state。
- 不要把局部 cache、adapter-local 状态、UI 状态、test helper 或临时 snapshot 说成系统 authority。
- 不要把相邻模块的职责合并为一个 owner；owner 必须由构造、持有、更新和消费路径证明。
