# 长任务审查收敛可执行规格

> 状态：2026-08-13，`S1: slice accepted, review closed`；`S2: slice accepted`；本规格达到 `spec complete` 和 `local validation accepted`。用户已授权提交、fast-forward 合入 `main` 并 push，Git 交接执行中。
> 分支：`codex/workflow-convergence`；起点：`bf87a3a42c4207bea5f8311beb8c2d0684402af7`。

## 1. 目标与非目标

### 1.1 目标

解决两个不同软件任务重复暴露的同一流程缺口：executable spec、TDD 和只读审查均存在时，阶段仍因全量 reviewer 反复启动、finding 缺少闭环记录、spec 修订类型混杂和完成声明越级而无法及时收敛。

修改后必须做到：

1. 同一审查 subject 只有一个完整 reviewer；当前 slice 使用独立 diff base，最终集成审查才读取批准 spec 后的完整 diff；修复后优先由原 reviewer 定点 closure。
2. findings 先完整核查并进入最小 ledger，再批量安排修复；不能靠启动新 reviewer 重置上下文。
3. 超过预定 closure 轮次时触发熔断，停止继续派 reviewer，重新检查 authority、范围或 spec。
4. spec 修改明确分为 Evidence update、Recovery metadata 和 Semantic revision；已有 criterion 的实现遗漏不自动膨胀为新 criterion。
5. 软件 slice 开始前完成 `criterion -> runtime owner -> mutation/publication point -> RED test` 对齐，并以真实 blast radius 决定是否拆分。
6. slice 进度标记只表示其 criterion 证据成立且声明的 review gate 已关闭；只有 accepted 的前置 slice 才满足后序依赖。
7. spec review 与 code review 使用同一套 full/closure、stable finding ID、有限替换和熔断语义。
8. 已有 criterion 的实现遗漏沿用原实现授权；新增 owner、架构、scope 或业务目标才按 Semantic revision 治理。
9. 完成声明同时携带 slice、spec 或 overall goal subject，并区分实现、审查、spec、本地运行和外部环境层级。

### 1.2 非目标

- 不修改 `test-driven-development` 的 RED-GREEN-REFACTOR 核心。
- 不新增 skill、agent manager、review registry、脚本、依赖或 harness 专属 API。
- 不要求每次 Evidence update 或 Recovery metadata 重新审批。
- 不把四项 slice 对齐扩张成第二份 workflow 文档或大型表格。
- 不规定所有任务都必须做两类 reviewer；保留现有风险与 ROI 门槛。
- 不通过新增独立章节堆叠规则；优先重写已有步骤、字段和验证门槛。
- 不运行 writing-skills control/candidate evaluator；以两个真实失败任务、静态 contract 和只读 diff review 验收。
- 不创建 PR、不发布；只按用户最新授权提交、fast-forward 合入仓库默认分支 `main` 并 push `origin/main`。

## 2. 当前状态与 Authority

优先级：当前用户要求 -> `AGENTS.md` / `CLAUDE.md` -> `writing-skills` -> 当前相关 workflow skills -> 本规格。

真实 RED 来自两个不同项目任务：

- 任务一在 reviewer 卡住后连续启动新 reviewer，后台 agent 堆积；spec 已写的 fence 在实现中遗漏；局部 spec 完成曾被表达成更大目标接近完成。
- Gate adapter 任务共启动 38 个 reviewer agent；同一架构阶段反复出现 `fresh/final/rereview`，finding 修复后多次全量重读大 diff；架构 spec 从 `AC-A10` 扩到 `AC-A33`；用户两次因耗时和复杂度要求暂停并询问进度。

现有 skill 已要求只读 reviewer、TDD 修复和重复审查至无 Critical/Important，但没有规定同一 scope 的 reviewer owner、closure 模式、finding ledger、审查熔断或分层完成词汇。

## 3. 文件 Owner 与执行流

| 文件 | 唯一职责 |
|---|---|
| `skills/brainstorming/SKILL.md` | spec 修订分类、slice 开始前对齐、accepted dependency、blast radius 与跨 spec 完成边界 |
| `skills/brainstorming/spec-document-reviewer-prompt.md` | spec full/closure 审查范围、stable finding ID 和只读输出 contract |
| `skills/requesting-code-review/SKILL.md` | reviewer 生命周期、完整审查与定点 closure、熔断和退出检查 |
| `skills/requesting-code-review/code-reviewer.md` | full/closure 输入与稳定 finding ID 输出 contract |
| `skills/receiving-code-review/SKILL.md` | finding ledger、一次性核查、修复与 closure 状态 |
| `skills/verification-before-completion/SKILL.md` | 分层完成声明和活跃 reviewer/session 检查 |
| `README.md` | 对外工作流摘要，不另行拥有细节规则 |
| `tests/workflow/test-spec-to-tdd-consistency.sh` | 上述静态 contract 的机械回归 |

执行流：

```text
批准的 spec
-> slice 开始前四项对齐与 blast-radius 判断
-> TDD 实现
-> 以当前 slice/criterion 和独立 diff base 为 subject 的一个完整 reviewer（该 slice 要求时）
-> findings 全量核查并写入 spec/task record ledger
-> 主 agent 逐项 TDD 修复
-> 原 reviewer 定点 closure
-> criterion 证据与 review gate 均关闭后标记 slice accepted
-> 下一个依赖已满足的 slice
-> 最终以批准 spec 为 authority 做一次完整集成验证和适用的集成 review
-> 只声明带 subject 且有证据支持的完成层级
```

不新增持久化数据结构。Finding ledger 是现有 executable spec 的一小段，短任务则留在当前 task record；它不是第二份计划。建议字段固定为：`ID`、`verdict`、`criterion/authority`、`RED 或事实证据`、`fix/diff`、`verification`、`closure`。

当前 finding ledger：

| ID | Verdict | Criterion/Authority | RED 或事实证据 | Fix/Diff | Verification | Closure |
|---|---|---|---|---|---|---|
| `CR-001` | `VERIFIED` Important | `WC-03` | 没有已授权 checkpoint commit 时，Git SHA 无法表示下一个独立 slice 的增量；第一次 closure 又确认 approved-spec baseline commit 同样缺少授权门槛 | `FULL_BASE_SHA` 和 slice checkpoint commit 均只在用户或治理流程授权后创建；任一未获授权都停止，禁止回退累计 diff | 两类授权 gate 均先静态 RED、修复后聚焦与 workflow tests exit 0；`git diff --check` exit 0 | `CLOSED`，原 reviewer 第二轮 closure 确认 |
| `CR-002` | `VERIFIED` Important | `WC-05` | `S1` 曾勾选 accepted，但接受它的 full review 被放进依赖 `S1` 的 `S2`，形成循环依赖 | full review 归入 `S1` 自身 gate；`S1` 恢复未勾选，`S2` 仅在 `S1` accepted 后做最终机械验证，不再启动第二次 full review | 2026-08-13：spec 依赖与状态已直接复核；workflow tests、validators 与 diff check 均 exit 0 | `CLOSED`，原 reviewer 第一次 closure 确认 |
| `CR-003` | `VERIFIED` Important | `WC-01/WC-04` | “更新原 criterion”可被解释为改变 criterion 定义，而任意 criterion 变化又属于 Semantic revision | `brainstorming` 明确 implementation omission 只更新原 criterion 的完成证据和 closure，不得改变定义或新增重复 criterion | 2026-08-13：相关 contract assertion 与 workflow tests exit 0；残留搜索只在 finding 事实描述中发现旧歧义措辞 | `CLOSED`，原 reviewer 第一次 closure 确认 |

## 4. 验收标准与验证合同

| ID | 要证明的事实 | Oracle 与通过条件 | 完成证据 | 覆盖边界 |
|---|---|---|---|---|
| `WC-01` | spec 修订不会混淆 | workflow contract test 检查恢复步骤中的三类修改及 Semantic revision 门槛 | 2026-08-13：聚焦静态 RED 首次因缺少 `slice accepted` 合同 exit 1；实现后 `bash tests/workflow/test-spec-to-tdd-consistency.sh` exit 0 | 不决定具体项目审批规则 |
| `WC-02` | slice 在编码前对齐真实 owner 与失败测试 | workflow contract test 检查既有 Implementation Slice 字段中的四项对齐和 blast-radius 拆分判断 | 2026-08-13：同一 contract test exit 0 | 不取代具体 spec 的结构设计 |
| `WC-03` | spec 与 code review lifecycle 在连续 slice 中收敛 | 两类 reviewer contract 都明确 review subject、一个 full reviewer、原 reviewer closure、stable finding ID、有限替换和两轮 closure 熔断；code review 以 `FULL_BASE_SHA` 拥有完整任务、以 `DIFF_BASE_SHA` 隔离当前 slice，只有最终集成 review 使用完整范围 | 2026-08-13：同一 contract test exit 0；唯一 full reviewer 返回 `CR-001..003`，原 reviewer 两轮定点 closure 后全部 `CLOSED`，0 Critical / 0 Important | harness 必须提供 reviewer 生命周期工具；不强制每个低风险 slice 独立 review |
| `WC-04` | findings 可追踪且授权不重复等待 | workflow contract test 检查最小 ledger、全量核查和 closure 更新；已有 criterion 的 implementation omission 沿用原实现授权，只有架构、owner、scope 或业务目标扩张进入 Semantic revision | 2026-08-13：同一 contract test exit 0 | 不新增机器持久化 registry；用户只授权 review 时仍保持只读 |
| `WC-05` | slice 依赖和完成声明不越级 | workflow contract test 检查 checkbox 只表示 `slice accepted`、review gate closure 属于依赖满足条件，并强制完成层级携带 slice/spec/overall goal subject、报告未完成上层和活跃 reviewer | 2026-08-13：同一 contract test exit 0；README 摘要同步为 accepted prerequisite 与 slice/checkpoint review | 短任务不强制罗列不适用层级 |
| `WC-06` | 修改保持项目 contract | workflow tests、skill validators、中文内容检查与 `git diff --check` 全部通过 | 2026-08-13：`bash tests/workflow/run-tests.sh`、四个 `quick_validate.py` 和 `git diff --check` 均 exit 0 | 不运行 writing-skills control/candidate evaluator |

两个真实任务是行为缺口 authority；不把 evaluator 回答当作验收 Oracle。

S0 旧 skill SHA-256：`brainstorming=01e2fa4a...e14e87e`、`requesting=7563cb9c...230d62`、`code-reviewer=8a9abeaf...a7659d`、`receiving=30d1da19...e991ef7`、`verification=25c72d5c...2aae0`。静态 RED 首次失败于缺少 spec 修订分类，原因与目标 contract 一致。

## 5. 执行 Slice

### [x] `S0`：冻结真实 RED 与静态 RED

- **结果：** 已保存当前 skill hash；静态测试因新 contract 缺失而 RED。
- **依赖：** 无。
- **工作范围：** 真实任务证据与 workflow contract test。
- **输入与 Authority：** 第2节两份真实任务和用户不使用行为 evaluator 的直接要求。
- **交付物：** 旧 skill hash 和失败的 contract assertions；旧规则缺少 reviewer/closure/ledger/完成层级边界。
- **验收标准：** `WC-01..05`。
- **审查门槛：** 无。

### [x] `S1`：有机整合最小收敛 contract

- **结果：** 六个 owner 文件和现有 README 摘要通过重写原步骤形成第3节执行流；不增加新章节体系、skill或旁支文档。
- **依赖：** `S0`。
- **工作范围：** 第3节所列 skill、prompt 和 workflow contract test。
- **输入与 Authority：** 两份真实任务的共同失败和静态 RED。
- **交付物：** 最小 skill 和 reviewer prompt 文本修改。
- **验收标准：** `WC-01..05`。
- **审查门槛：** 一个 fresh-context 只读 reviewer 完整审查当前 final-integration subject；有 finding 时由同一 reviewer 定点 closure。
- **完成证据：** 唯一 full reviewer 报告 `CR-001..003`；主 agent 核查并修复后，原 reviewer 在两轮定点 closure 内全部关闭，最终 0 Critical / 0 Important；reviewer session 已完成。

### [x] `S2`：最终机械验证与交接

- **结果：** `S1` review closed 后，在最终 tree 上重新运行相关 contract tests、validators 和 diff 检查，并准确回填完成层级。
- **依赖：** `S1`。
- **工作范围：** 当前分支完整 diff 和直接验证，不再启动第二次 full review。
- **输入与 Authority：** 用户最新修订要求、本规格`WC-01..06`。
- **交付物：** 本规格 Evidence 回填和最终验证结论。
- **验收标准：** `WC-01..06`。
- **审查门槛：** 无；`S1` 已拥有唯一 full review 与 closure。
- **完成证据：** 2026-08-13 在最终 tree 上重新运行 `bash tests/workflow/run-tests.sh`，中文内容与长任务 workflow contract 均通过；四个修改 skill 的 `quick_validate.py` 均通过；tracked 和 untracked diff whitespace 检查通过；旧 `BASE_SHA`、无限重复审查、旧授权等待和 `dependency-ready slices` 术语无生产残留；最终 diff 范围为 README、六个 owner/prompt 文件、一个 workflow test 和本规格。
- **当前停点：** `S2: slice accepted`；本规格 `spec complete`、`local validation accepted`。

## 6. 修订、回滚与最终验收

- 若静态 contract 或只读 review 表明规则仍是旁路追加、互相矛盾或无法闭合，再重写现有步骤，不新增配套流程。
- 若修改需要新skill、script、harness API或改变TDD核心，停止并修订本规格。
- 回滚只针对本分支本任务diff，不使用破坏性Git命令。
- Git 交接验收要求本地 `main` 与 `origin/main` 指向同一交付 commit；没有 PR 或发布证据时，这些层级仍明确未执行。
