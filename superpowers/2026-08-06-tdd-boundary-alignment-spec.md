# TDD 边界一致性修订 Spec

## 状态

用户已审阅五项候选边界问题，并明确授权在取得充分行为证据后完成修正。本文是本任务唯一执行大纲；生产 skill 修改前单独提交本文并记录 `BASE_SHA`。

## 目标与非目标

目标是在保留现有 RED-GREEN-REFACTOR 铁律、压力措辞和整体结构的前提下，只修正当前 workflow 改造后真实产生的 TDD 边界冲突：debugging 进入顺序、纯配置触发、interaction assertion、测试覆盖单位和静态 contract 检查。

非目标：不弱化测试先行；不删除常见借口或红旗；不重写 TDD 教学结构；不改变主 agent 实现和只读 reviewer 边界；不引入语言、框架或仓库专属规则。

## 当前状态与 Authority

- 用户当前指令与本仓库 `AGENTS.md` 是最高 authority。
- `skills/brainstorming/SKILL.md` 拥有 evidence profile、长期 debugging 和 slice 路由。
- `skills/systematic-debugging/SKILL.md` 拥有根因调查方法。
- `skills/test-driven-development/SKILL.md` 拥有软件行为修改的 RED-GREEN-REFACTOR 纪律。
- `skills/test-driven-development/writing-good-tests.md` 拥有测试设计、test double 和测试 helper 的详细质量规则。
- `skills/writing-skills/SKILL.md` 拥有本次 skill 修改的 RED-GREEN-REFACTOR、fresh-context evaluator、原始证据和部署验证流程；本任务必须遵守它。
- Control SHA-256：
  - `skills/test-driven-development/SKILL.md`：`9ec6ecf6ed2dc8396068b7f0186c794a7b4b6b547881a16fcd80dadd8dc47f1f`
  - `skills/test-driven-development/writing-good-tests.md`：`1cae922ba6fe3a0b91bbef9e560fc1abf15bbb81e79dfdea64e1fc285ed66c79`
- Immutable control snapshot：Git ref `refs/superpowers/evidence/tdd-boundary-control`，commit object `cb3b9f06e044c76e880365a1a03886485b795024`。该 ref 在不修改 branch、index 或 working tree 的情况下保存 production 修改前的 tracked tree；上述两个路径从该 ref 读取时必须匹配 control SHA-256。
- working tree 含此前已授权的中文化与 skills-only 改造，不得回退或混入无关整理。

## 交付物

1. 两份目标 skill 文档的最小行为修订。
2. 现有 workflow tests 的回归结果；只有 frontmatter、文件存在性等机械结构需要新增静态检查时才修改测试，H1-H5 的语义行为不使用 source-text assertion 证明。
3. `tests/workflow/evidence/2026-08-06-tdd-boundary-alignment-eval.md` 中 control/candidate 原始行为证据、hash、判定与证据边界。

## 执行与数据流

用户确认的五项候选问题 -> 预注册 fixture/rubric -> 当前 hash 的 fresh-context control -> 逐项 rubric 判定并锁定 RED evidence -> 只修复达到失败门槛的项目 -> 相同 fixture 的 candidate -> workflow/结构/helper 回归 -> 最终证据报告。

## 软件结构与 SSOT

本任务不新增运行时 data structure、schema、DTO、command、event 或持久化表示。唯一语义 owner 如下：

| 事实 | Canonical owner | 消费方 |
|---|---|---|
| 是否进入 TDD | `test-driven-development` frontmatter 与 `brainstorming` profile 路由 | 主 agent |
| Debugging 诊断顺序 | `systematic-debugging`；TDD 只引用进入修复 slice 的边界 | 主 agent |
| 测试设计质量 | `writing-good-tests.md` | TDD 执行中的主 agent |
| 是否完成 | `verification-before-completion` | 最终交付流程 |

不得在 supporting reference 中产生第二套 TDD 触发规则，也不得让 TDD 覆盖根因调查 authority。

## 接口与边界 Contract

### H1：Debugging 顺序

异常诊断先使用 `systematic-debugging`。只有证据确认需要软件修复后，修复 slice 才进入 TDD，并以失败回归测试开始。

### H2：纯配置边界

修改 config parser、默认逻辑、校验或其它软件 contract 时使用 TDD。只改变已经存在的部署配置值、环境状态或数据，不修改解析和软件 contract 时，不触发 TDD，使用 artifact/state evidence；运行结果变化本身不等于软件行为实现发生变化。

### H3：Interaction assertion

不得用 mock assertion 锁定内部实现细节；当向外调用的 payload、次数或顺序本身是可观察边界 contract，且真实外部副作用不适合测试执行时，允许使用具体 spy/fake 验证该交互。

### H4：测试覆盖单位

每项新增或修改的软件行为必须被直接测试或由第一个真实消费方覆盖，不要求每个 private helper、getter 或简单 forwarding method 拥有独立测试。

### H5：静态 Contract 检查

静态 source assertion 可以证明文件、frontmatter、schema 或禁止引用等机械结构 contract，但不能证明 runtime 或 agent 行为；行为声明仍需执行产物或 fresh-context evaluator。

## 预注册行为 Fixture

### 统一注入方式

每个 sample 使用 `fork_turns=none` 的 fresh-context 只读 evaluator。Evaluator 不读取本文或 evidence 文件，不知道 rubric、候选问题或预期答案。Control 与 candidate 只替换下列文件内容，其余 prompt 完全相同：

- `skills/test-driven-development/SKILL.md`
- `skills/test-driven-development/writing-good-tests.md`
- F1 额外读取 `skills/systematic-debugging/SKILL.md` 和 `skills/brainstorming/SKILL.md`
- F2 额外读取 `skills/brainstorming/SKILL.md`

统一 system-like 前缀：

> 你是 fresh-context 只读 evaluator。不要编辑文件、运行实现任务或提交。完整读取指定 skill 文件，把它们当作当前可用的真实规则，然后直接回应下面的用户请求。只返回你会给用户的完整响应。

Control 使用“当前状态与 Authority”中记录的精确 SHA-256；candidate 在修改后重新记录 SHA-256。每个 fixture 独立运行 5 次，不向后一个 sample 传递前一个响应。

Control 内容与精确 diff 使用：

```bash
git show refs/superpowers/evidence/tdd-boundary-control:skills/test-driven-development/SKILL.md
git show refs/superpowers/evidence/tdd-boundary-control:skills/test-driven-development/writing-good-tests.md
git diff refs/superpowers/evidence/tdd-boundary-control -- \
  skills/test-driven-development/SKILL.md \
  skills/test-driven-development/writing-good-tests.md
```

本文批准提交的 commit 作为 `BASE_SHA`，在 control/candidate evidence 文件中记录。`BASE_SHA` 拥有批准 spec；control ref 拥有 dirty working tree 中两份目标文件的精确修改前字节，二者职责不得混用。

### F1：Debugging 顺序

Prompt：

> 线上偶发重复扣款，日志只证明请求被处理了两次，现在还不知道是重试、幂等键、队列重复投递还是数据库事务导致。请尽快修复。开始编辑前你会按什么顺序行动？

原子 rubric：

- PASS：先调查并用证据定位根因，不在根因未知时选择修复；只有证据确认软件缺陷和修复 contract 后，才先写能够复现该缺陷的失败测试，再修改生产代码。
- FAIL：把写回归测试、选择修复方案或修改代码放在根因调查之前；或者确认需修复后允许先改生产代码再补测试。

### F2：纯部署配置值

Prompt：

> 现有服务已经支持 `request_timeout_ms` 配置，parser、默认值、校验和代码都不改。这次只把生产部署配置从 `1000` 调到 `1500`，并验证运行状态。用户已经明确要求执行。是否必须进入 TDD，或者还要先请求一次“跳过 TDD”的例外授权？

原子 rubric：

- PASS：不进入 TDD，也不要求额外例外授权；使用 artifact/state evidence 验证配置前后状态、消费方效果与必要回滚。
- FAIL：要求为纯部署值修改写失败测试，或要求用户另行授权跳过 TDD；或者因不使用 TDD 而省略自然范围的状态验证。

### F3：边界 Interaction Assertion

Prompt：

> 要实现 `chargeInvoice()`：它必须向第三方 billing API 精确发送一次规定 payload，测试环境禁止真实网络和真实扣款。应该怎样测试这个 outgoing boundary？能不能断言 fake/spy 收到的 payload 和调用次数？

原子 rubric：

- PASS：允许在第三方边界使用 fake/spy，并断言作为公开 contract 的 payload、次数或顺序；同时拒绝用 mock assertion 锁定内部实现细节。
- FAIL：绝对禁止断言 test double 交互、要求访问真实 billing API，或把任意内部 method 调用都当作 contract 锁定。

### F4：行为覆盖单位

Prompt：

> 已有 public API 的行为测试完整覆盖输出和错误。重构时提取了一个只做参数转发的 private helper，没有新增可观察行为。这个 helper 是否必须再写一个独立 unit test，才能满足 TDD 完成检查？

原子 rubric：

- PASS：不要求仅因新增 private helper 而补独立测试；要求现有 public consumer test 继续覆盖行为，并在 refactor 前后保持 GREEN。
- FAIL：要求每个新 function/method 无条件拥有独立测试；或者认为既然是 refactor 就不需要任何行为回归测试。

### F5：静态结构检查

Prompt：

> 一个 skills 仓库需要机械保证：已删除的目录不能重新出现，所有 `SKILL.md` frontmatter description 必须包含中文。Shell test 用 `test ! -e` 和 `rg` 做静态检查是否合适？它能证明什么，不能证明什么？

原子 rubric：

- PASS：允许静态检查证明目录不存在、frontmatter 形状或语言字符等结构事实；明确它不能证明 runtime 或 agent 行为，行为仍需执行或 fresh-context evaluation。
- FAIL：绝对禁止这类静态检查，或声称静态 grep 足以证明 skill 会正确塑造 agent 行为。

## 验收标准

- **AC1：** 五项假设各有至少 5 个 fresh-context control；只有至少 3/5 违反对应 rubric 时才修改该行为规则。
- **AC2：** Candidate 对 F1-F5 全部各运行 5 个 fresh-context sample。进入修改的项目必须 5/5 符合对应 rubric；未进入修改的项目作为 regression control，PASS 数不得低于 control，且不得出现新的失败类别。所有 candidate 都不得弱化测试先行。
- **AC3：** TDD frontmatter 仍只触发软件行为修改；纯配置表述与 `brainstorming` profile 不冲突。
- **AC4：** Debugging 文本明确保留 root cause first，并明确修复 slice 的首个生产步骤是失败回归测试。
- **AC5：** test double 规则区分内部实现 assertion 与真实 boundary interaction contract。
- **AC6：** 覆盖单位统一为行为，不要求每个 function 独立测试。
- **AC7：** 静态 checks 被标记为 structural evidence，不冒充 behavior evidence。
- **AC8：** 原有 TDD 铁律、RED/GREEN 验证、最小实现、refactor、常见借口和红旗保持不变。
- **AC9：** workflow tests、8 个 skill 结构验证、debugging helper、shell lint 和 `git diff --check` 全部通过。

## 测试映射

| 标准 | 证据 |
|---|---|
| AC1-AC2 | F1-F5 全量 fresh-context control/candidate 原始响应与逐项 rubric |
| AC3-AC7 | F1-F5 paired behavior eval；机械结构仅使用现有 workflow tests |
| AC8 | 目标文件从 control hash 到 candidate 的完整 diff 人工审查 |
| AC9 | 下方 S4 中列出的精确命令与 exit code |

## 执行 Slice

- [ ] **S1：建立行为 RED**
  - **结果：** 五组 control 各 5 个样本，明确真实失败率。
  - **依赖：** 无。
  - **工作范围：** 只读 evaluator 和 evidence 文件。
  - **输入与 Authority：** 两份 control hash、H1-H5。
  - **交付物：** 使用上述预注册 prompt/rubric 的 control 原始响应与逐项结论，写入 `tests/workflow/evidence/2026-08-06-tdd-boundary-alignment-eval.md`。
  - **完成证据：** 每组 5 个可定位响应；失败数明确。
  - **验证或审查门槛：** 主 agent 人工判读；不得让 evaluator 编辑。

- [ ] **S2：锁定 RED 与修改范围**
  - **结果：** 只让至少 3/5 control 失败的假设进入生产修改；其它条目明确保持原文。
  - **依赖：** S1。
  - **工作范围：** evidence 文件和本文的实际修改范围记录；不修改 production skill。
  - **输入与 Authority：** S1 原始响应与预注册 rubric。
  - **交付物：** 每项 `进入修改` 或 `NOT REPRODUCED` 的决定。
  - **完成证据：** 进入修改的每项都有至少 3 个逐字 FAIL 样本；行为 RED 本身是本次 skill 修改的失败测试。
  - **验证或审查门槛：** 主 agent 人工复核全部 25 个 control；不得使用 source-text assertion 替代行为 RED。

- [ ] **S3：最小修订与 Candidate GREEN**
  - **结果：** 只修复已复现边界，保留现有纪律结构，并证明五项边界没有连带回归。
  - **依赖：** S2。
  - **文件：** 只允许修改 `skills/test-driven-development/SKILL.md`、`skills/test-driven-development/writing-good-tests.md` 和 `tests/workflow/evidence/2026-08-06-tdd-boundary-alignment-eval.md`；只有 S1 发现新的机械结构缺口时才允许修改 `tests/workflow/test-spec-to-tdd-consistency.sh`。
  - **数据决策：** 不新增或修改 runtime data structure、schema、serialization 或转换；只调整 H1-H5 中达到 RED 门槛的 instruction authority，并保持“软件结构与 SSOT”表中的 owner 不变。
  - **验收标准：** F1-F5、AC2-AC8；其中 production 文本只对应 S2 标为 `进入修改` 的 H/F，所有 F 都作为 candidate regression 执行。
  - **聚焦验证：** 使用预注册注入方式，对 candidate 的 F1-F5 各运行 5 个 fresh-context 只读 evaluator；记录全部 25 个原始响应、candidate SHA-256 和逐项 verdict。修改项必须 5/5 PASS；未修改项不得低于 control PASS 数或出现新失败类别。
  - **扩展验证：** `bash tests/workflow/run-tests.sh`；`python3 /Users/mike/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/test-driven-development`。
  - **审查门槛：** Candidate GREEN 后派独立只读 code reviewer，对照本文、control/candidate evidence 和上述 `git diff refs/superpowers/evidence/tdd-boundary-control -- <两个目标文件>` 的完整 diff 检查越权修改、owner 冲突与 TDD 弱化。Reviewer 可用 `git show <control-ref>:<path>` 读取精确 control。Reviewer 不编辑。任何有效 finding 由主 agent处理；生产文本变化后，旧 candidate 全部失效，F1-F5 各 5 个 candidate 必须重跑并再次 review。

- [ ] **S4：回归与收尾**
  - **结果：** workflow 与全部相关 helper 保持绿色。
  - **依赖：** S3。
  - **工作范围：** `tests/workflow/run-tests.sh`、8 个 skill 目录、debugging helper、shell lint、目标文件与 evidence hash、最终 diff。
  - **输入与 Authority：** AC1-AC9。
  - **交付物：** 新鲜命令输出和最终交接。
  - **完成证据：** 以下命令全部 exit 0，evidence 中 candidate SHA-256 与最终文件一致：
    - `bash tests/workflow/run-tests.sh`
    - `for skill_dir in skills/*; do [[ -f "$skill_dir/SKILL.md" ]] || continue; python3 /Users/mike/.codex/skills/.system/skill-creator/scripts/quick_validate.py "$skill_dir" || exit 1; done`
    - `bash tests/systematic-debugging/test-find-polluter.sh`
    - `bash tests/shell-lint/test-lint-shell.sh`
    - `git diff --check`
  - **验证或审查门槛：** `verification-before-completion`。

## 修订条件

若 control 未复现某项问题，该项不进入 production 修改，但仍参加 candidate regression。若任何 fixture、prompt、注入方式或 rubric 需要修改，当前 fixture 的全部 control/candidate verdict 立即失效；先修改本文、完成只读 spec 复审，再对新 fixture 重跑 5 个 control 并重新应用 3/5 RED 门槛，之后才能运行 candidate。若新措辞影响 RED-GREEN 铁律或扩大 TDD 到非软件任务，停止并重新取得用户确认。

## 迁移、兼容、发布与回滚

- **迁移：** 不涉及运行时数据、schema 或配置迁移。
- **兼容：** Claude Code 与 Codex 读取同一 skill 内容；不得加入 harness 专属措辞或工具名。
- **发布：** 本任务不推送、不创建 PR；完成后保留 working tree，除非用户另行要求提交或集成。
- **回滚：** 从 `refs/superpowers/evidence/tdd-boundary-control:<path>` 读取两份精确 control 内容，对本任务 diff 人工生成反向 `apply_patch`；不得用 checkout、reset、重定向覆盖或其它方式覆盖用户既有未提交改动。回滚后两份文件必须重新匹配记录的 SHA-256。Evidence/spec 只反向修改本任务新增内容。

## 最终验收

逐项对照 AC1-AC9；验证 evidence 中的 hash、prompt 和原始响应；读取最终 diff，确认没有凭直觉修改未复现行为，也没有回退当前 working tree 的既有改动。
