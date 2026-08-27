---
name: traceable-explainer
description: 用户要求忠实解释已有代码、已完成研究结论或现役 plan/spec，理解调用链、机制与因果说明、依赖、owner、状态变化、criterion、Oracle、error、fallback 或 terminal state，并需要可追溯且按需可视化的说明时使用；只解释已有 artifact，不用于采集或重新分析外部证据，也不用于创建、批准或修改 plan/spec
---

# 可追溯解释

先判断用户要理解哪一种 truth，再完整读取足以回答问题的 authority。保持只读；证据没有读通时明确写 `unavailable`，不用常识、目录形状或 diff 猜未知事实。

## 1 路由解释对象

```text
explanation_profile = code-path | research-mechanism | plan-flow
explanation_scope = focused-item | change-set | system-overview
reader_mode = direct | learning
```

| Profile | Authority | 必须解释 | 禁止行为 |
| :--- | :--- | :--- | :--- |
| `code-path` | 连续 `file:line`、运行配置和实际输出 | 入口、关键值、状态变化、owner、副作用、error、fallback 与 terminal state | 用架构常识补齐没读通的链路 |
| `research-mechanism` | 已完成研究 artifact 明示的来源、claim、样本窗口与 evidence status | 已写明的事实、推断、机制、替代解释、反证和不可观察边界 | 重新搜源、改判证据等级或补造因果 |
| `plan-flow` | 当前现役 plan/spec 及其状态 authority | 目标、owner、slice 依赖、criterion、Oracle、状态与 blocker | 把 proposed 写成 completed，或顺手批准、修改 plan |

需要重新分析外部证据时交给 `evidence-driven-research`；需要创建、批准或语义修改 plan/spec 时交给 `brainstorming`；需要正式质量判断时交给对应 review skill。

## 2 选择解释范围

| Profile × Scope | `focused-item` | `change-set` | `system-overview` |
| :--- | :--- | :--- | :--- |
| `code-path` | 支持：指定代码、错误、配置或 runtime 链 | 支持：有 scoped diff 或 commit range | 支持：有结构、入口、配置、部署和 runtime/data-flow authority |
| `research-mechanism` | 支持：一个完成的研究 artifact | 条件支持：同一 canonical artifact 的可定位版本或 diff | 无效：跨 corpus 综合与新因果判断交给研究 owner |
| `plan-flow` | 支持：一个 spec 段落、slice、criterion 或 blocker | 条件支持：同一 plan/spec 的可定位版本或 diff | 条件支持：canonical spec 或明确 SSOT 清单覆盖完整目标、依赖与状态 |

`conditional` 的 authority 不完整时，缩小为 `focused-item` 或交回专业 owner，不降级猜测。

### 2.1 单项解释

第一段直接说明对象做什么、为何重要。普通问题用 3 至 8 句；只读取能回答该问题的路径。

### 2.2 变更解释

Diff 只能证明改了什么。修改理由只接受 commit message、spec、issue、代码注释或当前可见对话；都不存在时写：

```text
reason=unavailable
```

交付文件变化、可定位理由、依赖、已运行测试、具体风险和未观察范围。不要从文件名、代码形状、删除动作、依赖变化或测试命令反推动机。过程中的弯路、skill 或记忆候选属于 `retro`。

### 2.3 系统全景

架构事实只能支持职责、边界、依赖、数据流和部署关系。近期变化、完成状态与 handoff 另需 spec、状态账本、明确 commit range 或 handoff artifact；缺少时逐项写 `unavailable`。

## 3 获取 Authority

### 3.1 代码路径

1. 定位入口、指定行所属函数、类型和模块。
2. 沿调用关系追踪关键参数、状态和类型转换。
3. 读到最终 state write、database mutation、publish、external I/O、event、error 或 return。
4. 覆盖会改变结论的成功、拒绝、异步边界、fallback、retry 和 terminal state。
5. 证明谁构造、持有、更新和消费状态，以及哪个事实源拥有最终 authority。

### 3.2 研究机制

只使用 artifact 明示的 source、claim、样本或数据窗口、evidence status、alternative explanation 和 unavailable field。研究文引用代码不会自动切换 profile。

### 3.3 Plan 执行流

读取当前 canonical plan/spec，保留原始状态字面量，定位 slice 依赖、criterion、Oracle、Evidence 和 blocker。代码注释提到计划不会自动成为 plan authority。

## 4 选择最小表达形式

短文字是默认。视觉只有在能降低理解成本时才出现：

| 关系 | 默认形式 |
| :--- | :--- |
| 单行、定义、一步转换 | 短文字或短代码 |
| 算法或规则步骤 | 伪代码 |
| caller/callee、文件或 artifact 层级 | 调用树或文件树 |
| 修改前后或多轴比较 | diff 或紧凑表格 |
| 跨 owner 时序、因果链、依赖或状态机 | Mermaid |
| 筛选、折叠、联动或多视图高密度承载 | HTML |

每次回答最多一个 primary visual。三个以下且无分支的节点通常保持文字。不要同时堆树、Mermaid、HTML 和重复 prose。

`reader_mode=direct` 是默认。用户明确要求教学、表现出零基础需求，或询问设计取舍时才使用 `learning`；最多补 1 至 2 个紧邻当前事实的原理点，不使用固定 `Insight` 横幅。

## 5 C4 与 Source Anchor

C4 只用于 `code-path + system-overview`，且问题确实关注 actor、外部系统、系统边界或独立部署单元。默认最多 Context + Container；Component 只在复杂 container 或用户明确要求时增加；不自动生成 Code level。

每个 Container 写 technology 与 responsibility；每条关系写具体 intent 和 protocol。双向流拆成两个方向；推断进入 `Assumptions`。

图后紧邻 source-anchor 表：

```text
anchor_id
diagram_element_or_relation
authority_kind = code | runtime-config | research-artifact | plan-spec
locator = absolute-file:line | artifact-section | criterion-id
evidence_status = verified | inferred | unavailable
assumption
```

`inferred` 必须写推断链；`unavailable` 不得画成确定关系。图不能代替 authority。

## 6 输出顺序

1. 结论前置：对象的实际作用、意义和最终结果。
2. Authority 链：连续位置、artifact section 或 criterion。
3. 关键值、状态、副作用、依赖与 owner。
4. 必要时加入一个最小视觉。
5. 明确 inferred、unavailable 和覆盖边界。

## 7 禁止项

- 不重新研究外部来源，不修改或批准 plan。
- 不顺手 review、修复或实现。
- 不画没有 anchor 的确定关系图。
- 不把 inference 写成 verified。
- 不把当前 diff 当完整 session transcript。
- 不把局部 cache、adapter 状态、UI 状态、test helper 或临时 snapshot 说成系统 authority。
