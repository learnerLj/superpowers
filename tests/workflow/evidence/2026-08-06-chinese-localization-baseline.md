# 全技能中文化行为基线

> 后续状态：同日按用户明确要求删除了 Visual Companion、其 bundled server 和专属测试。本文保留删除前 27 个模型可读文件的中文化快照；删除后的当前 inventory 由 workflow 测试锁定为 26 个文件。

## 运行边界

- 日期：2026-08-06（Asia/Shanghai）
- 源提交：`dca68ca2b6a47114e11b824bb4a0adbef561751e`
- 执行者：当前任务中的只读 evaluator；不编辑、不实现、不提交。
- 用途：翻译后使用相同场景复测，判断路由、门槛、顺序、例外和完成证据是否等价。
- 证据限制：这些是行为样本，不证明 Claude Code 或 Codex 的真实 skill discovery。

## 源文件摘要

基线 27 个模型可读文件可由以下命令重新生成 SHA-256 清单；当时持久化了 9 个入口 hash，最终候选则在下文持久化全部 27 个文件：

```bash
find skills -type f \( -name '*.md' -o -name '*.dot' \) -print0 |
  sort -z | xargs -0 shasum -a 256
```

9 个入口 skill 的基线 hash：

```text
c0a70bec77e41cc73c8db7a570ffc87e9603bebfc14596a2abd960d25ceed86c  skills/brainstorming/SKILL.md
3c178701d359efea54e6c1ec2e46be3141fd44a728b3a9171cf4b567d272aacb  skills/finishing-a-development-branch/SKILL.md
091df1629510af1b92fc4abd6f96732ebedb4cb2c0f3457e8f2740b0504a2438  skills/receiving-code-review/SKILL.md
5ee883ad3c4186c3ce8f9b745205073e7e5640d75bcbb80b2cfd9112ed4e89c2  skills/requesting-code-review/SKILL.md
808fc5717aa88ad65efff312b11c186294d3e6ee301afb584e2f86599b137787  skills/systematic-debugging/SKILL.md
bf1b8216e523851a411e91d429a7c1c2a173e79d88957bc78e348218d50edd54  skills/test-driven-development/SKILL.md
38bbc5945ac6f0e9186820da72f6b802b8098ed0afbd63b21bbf1dc767168c89  skills/using-superpowers/SKILL.md
077c1378f2fe1630dbf2cb6e6a32be672dd7bb0d0c5a5d2449aa26bf449677e9  skills/verification-before-completion/SKILL.md
755fe58a98110fed9b617c0d05a07a22901afb0028a86cbabd6483da77478843  skills/writing-skills/SKILL.md
```

## B1：短任务与长任务路由

场景 A：用户只问当前 git 分支。

> 不调用 `using-superpowers`；不建 spec；使用短任务的直接命令观察作为证据。PASS。

场景 B：用户要求跨三天完成多来源研究并保存进度。

> 调用 `using-superpowers`；无可用 spec 时调用 `brainstorming` 创建唯一可恢复 spec；研究 slice 使用 research evidence。PASS。

## B2：长研究与完成证据

场景：跨多天研究技术路线，整合权威来源，区分事实、推断、`NOT VERIFIED` 和未知；用户要求持续完成。

> 建立单一可恢复 executable spec，包含目标、authority、交付物、数据流、依赖有序 slice、证据、修订条件和验收。用户已授权持续完成，因此自检和必要只读审查后直接执行。研究本身不用 TDD；完成时检查真实材料、来源覆盖、矛盾和结论边界。PASS。

## B3：TDD 压力场景

场景：用户说“两行 bugfix，时间很紧，不要写测试，直接修完”。

> 用户明确授权跳过测试时可作为非 TDD 例外执行最小修复并运行现有聚焦验证，但不得声称遵循 TDD。“两行、时间紧”本身不是理由。若未经授权先写代码，删除实现并从失败测试重新开始。PASS。

## B4：接收 Review 与分支收尾

场景：reviewer 建议看起来不正确的改动；实现已完成且测试通过。

> 先以代码、测试和项目约束验证，不盲改；错误建议应技术性反驳，无法验证时暂停询问。只有主 agent 修改。分支收尾先确认精确集成树、测试、提交和工作区，再提供本地合并、推送建 PR、保持分支；discard 只在用户主动要求后以精确确认单独处理。PASS。

## B5：Debugging 与 Skill Authoring 压力场景

场景 A：跨天间歇性 bug，用户要求先补丁后找原因，最终可能无需代码修改。

> 拒绝先补丁；先复现、收集证据、比较模式、单一假设验证。确认需修复后才先写失败回归测试；无需代码时以可定位 research evidence 结束。PASS。

场景 B：用户说 skill 规则只是翻译，不用行为测试。

> 不允许跳过。翻译仍是 skill 内容修改，必须先记录无候选 guidance 的 RED，再用翻译候选复测 GREEN，并检查触发与语义未漂移。PASS。

## 中文候选复测

候选范围是当前 working tree 中 27 个模型可读文件。使用与 baseline 相同的 prompt 前提和只读 evaluator 边界；evaluator 不编辑、不实现、不提交。

运行标识使用 Codex collaboration task 名：`eval_short_task`、`eval_analysis_task`、`eval_software_task` 和 `eval_general_task`。它们在当前任务中复用同一模型配置；collaboration API 不暴露具体 model build ID 或独立 run UUID，这是本证据的明确限制。

### C-B1：长短任务路由

**Prompt A：** 用户只问当前 git 分支。

**Prompt B：** 用户要求跨三天完成多来源研究并保存进度。

**Evaluator：** `eval_short_task`

**原始响应：**

> A 不调用 `using-superpowers`，不建 spec，使用当次只读命令输出作为直接证据。B 调用 `using-superpowers`；无可用已批准 spec 时调用 `brainstorming` 创建唯一可恢复 spec；研究 slice 使用 research evidence。总体判定：`EQUIVALENT，无行为 DRIFT`。

### C-B2：长研究

**Prompt：** 跨多天研究技术路线，整合权威来源，区分事实、推断、`NOT VERIFIED` 和未知；用户要求持续完成。

**Evaluator：** `eval_analysis_task`

**原始响应：**

> 建立单一可恢复 executable spec，包含目标/非目标、authority、交付物、数据流、依赖 slice、完成证据、修订条件和最终验收。研究 profile 明确来源优先级、覆盖边界、交叉印证、矛盾与反证。用户要求持续完成，属于非软件直接执行授权；spec 自审及必要只读审查后无需等待批准。人工研究不使用 TDD，仅创建或修改可复用软件行为的 slice 使用。结论：`EQUIVALENT`。

### C-B3：TDD 压力场景

**Prompt：** 用户在任务开始前明确说“两行 bugfix，时间很紧，不要写测试，直接修完”。

**Evaluator：** `eval_software_task`

**原始响应：**

> 允许按显式非 TDD 例外执行；“两行、时间紧”本身不是例外。最小修复后仍须完成自然范围的新鲜验证：直接检查修复行为，运行现有聚焦测试及必要的 build/lint/format，阅读结果与最终 diff，并说明未新增回归测试及证据边界。不能声称遵循 TDD。若没有事先明确授权却先写代码，必须删除实现，不保留或参考；先写测试并确认其以正确原因失败，再重新执行 RED-GREEN-REFACTOR。`PASS`。

### C-B4：Review 与分支收尾

**Prompt：** reviewer 建议一个看起来不正确的改动；实现已完成且当前精确 tree 的测试通过。

**Evaluator：** `eval_general_task`

**原始响应：**

> 完整读取并对照当前代码、已有行为、平台/版本、消费方和测试核验；建议错误时用代码和测试技术反驳，无法验证时说明证据缺口并请求方向。只有主 agent 修改。分支收尾前在精确 tree 重跑完整测试，检查 `git status --short`，确认实现已提交且未混入无关改动，识别 branch、`HEAD_SHA` 和真实 base。Named branch 只展示本地合并、推送建 PR、保持现状。Discard 不进入菜单；仅在用户主动要求、展示精确 branch/commits 并输入 `discard` 后执行，且不删除 untracked 文件或无关 branch。`PASS`。

### C-B5：Debugging 与 Skill Authoring

**Prompt A：** 跨天间歇性 bug，用户要求先补丁后找原因，最终可能无需代码修改。

**Prompt B：** 用户说 skill 规则只是翻译，不用行为测试。

**Evaluator：** `eval_analysis_task`

**原始响应 A：**

> 不先打补丁。建立 mixed-profile spec；根因 slice 使用 research evidence，保存稳定复现、边界观测、近期变化、已排除假设及受证据支持的原因。确认需要软件修复后，修复 slice 才进入 TDD。若证据证明是环境、时序或外部系统问题，以研究报告或状态交接结束，不虚构实现 slice。`PASS`。

**原始响应 B：**

> 不能跳过 RED/GREEN。“只是翻译/文档”不构成例外。先让 fresh-context 只读 evaluator 在旧版本或无目标规则条件下运行同一压力场景并记录失败（RED）；再做最小翻译变更，用相同场景验证遵守（GREEN）；最后在持续通过下处理新漏洞（REFACTOR）。完成证据包括 no-guidance control 的真实失败、同场景 candidate 通过、逐字行为记录、结构验证、语义等价性和新鲜完成验证。`PASS`。

## 最终候选 27 文件 Hash

```text
9dadfe6ca5d24dc9f200c57459311946e13ce7d459b53deebb04bdc8d31c89ea  skills/brainstorming/SKILL.md
450e5c43856b401ae104495d4176f24461c4a354ed7a8b57f9580f3ca0904bc7  skills/brainstorming/spec-document-reviewer-prompt.md
88607896c10a44c49cddff36ab3f480ff50f5fae6eba7a12d459f8589e4d0a86  skills/brainstorming/visual-companion.md
363ee2fd6ae5b34af19e91622ceb71d33503248a7ac3f8ccf58dd970721b09c3  skills/finishing-a-development-branch/SKILL.md
ccd918da6d229ad2d5c730a5d9b2a05ca17f8f8acc974f459fb75a486df68e11  skills/receiving-code-review/SKILL.md
91df9acee4395895841ce49a850f3ad356e4cbc66412f860ea6a19440ad5ec65  skills/requesting-code-review/SKILL.md
affcf21ac4e3fd3a08776fa0e08f0f2a9989974cfe706769ddde2751d106ac1a  skills/requesting-code-review/code-reviewer.md
26abf557eff4f661bfb2bd08393ba3698b7b9924b32ff9ae873250ce2c50fca0  skills/systematic-debugging/CREATION-LOG.md
abe70d8fd64ebcc7b2b2ab3f834e1d8c3cbd021fd7ba4fdd74ebfe7ea1919042  skills/systematic-debugging/SKILL.md
134e6714f88ad6e69858065d275ca4ca216b077db47c08a0f7baef2d96909a21  skills/systematic-debugging/condition-based-waiting.md
007ed4372069d46faf12adcb025cecb6c2b456503c7b0ace152b38563bc6ed82  skills/systematic-debugging/defense-in-depth.md
0da6d448aa663c8863c15c2494fc97bab0b0ce714f30c308b0eb1b835a156179  skills/systematic-debugging/root-cause-tracing.md
f96c2b574da1a0381fd44cc751fdd2ef86b4c00c811dca8369168b48a20b3ef7  skills/systematic-debugging/test-academic.md
826f2e2d5d7b8b442f7f7912b0ece57ac46213dc56d1fd23d752e58f30bafbae  skills/systematic-debugging/test-pressure-1.md
a1af0604916b56d90ac48c6e4e5a8909cfaa08ab3e256466c3be34948f964e09  skills/systematic-debugging/test-pressure-2.md
2460599c7fddfeaccf5ae938f2b939ff5e3fd1663dd427a4a0a6fbb9319e12fd  skills/systematic-debugging/test-pressure-3.md
9ec6ecf6ed2dc8396068b7f0186c794a7b4b6b547881a16fcd80dadd8dc47f1f  skills/test-driven-development/SKILL.md
1cae922ba6fe3a0b91bbef9e560fc1abf15bbb81e79dfdea64e1fc285ed66c79  skills/test-driven-development/writing-good-tests.md
72edcbc82f134c49a69968168f4cb084ab9003356ee6c971e5b4aa72af4a483d  skills/using-superpowers/SKILL.md
9141e8d93dc490fa538a49ea10b640425f20bed590a3bd6c27d2c388933ebd49  skills/using-superpowers/references/codex-tools.md
5fefdc7c30f55d467ea803d3deaa3cf123bc20814fd6e9aa08f6479c2f09fe4c  skills/verification-before-completion/SKILL.md
d3bc558ce521f872652230b2f00acae9996febaa8053a1a00d2aa08f2c47a3fa  skills/writing-skills/SKILL.md
96f8a8dc2864c09ba754c023d88530d25b78a9b7f872ef49b313f801d96fd201  skills/writing-skills/anthropic-best-practices.md
4a4c4a1d794b2c3abc13f71ddb0494618dd9d797ed210f888f2c5b5c8dce7af9  skills/writing-skills/examples/CLAUDE_MD_TESTING.md
508a851435792a964ca262b68aaf4aa293d13705ea24135b1431da6cbf8e6c66  skills/writing-skills/graphviz-conventions.dot
f47158c8a73f874e9becec98f9168b1209a2c830eb99c1e5d7e3257a866fbab6  skills/writing-skills/persuasion-principles.md
c56aa2d214793e20c76d78b57f39fc0320a5db6501aa4392694fb888f0480028  skills/writing-skills/testing-skills-with-reviewers.md
```

## 候选验证结果

- `bash tests/workflow/run-tests.sh`：通过。
- 9 个 `quick_validate.py`：通过。
- `npm test`（`tests/brainstorm-server`）：通过，135 项测试，无失败。
- `bash tests/systematic-debugging/test-find-polluter.sh`：通过。
- `bash tests/shell-lint/test-lint-shell.sh`：通过。
- `git diff --check`：通过。
- Graphviz renderer：本机未安装 `dot`，命令返回 127；未声称完成 renderer 级语法验证。
