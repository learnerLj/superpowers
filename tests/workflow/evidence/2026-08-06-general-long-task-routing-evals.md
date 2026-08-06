# General Long-Task Routing Paired Evals

## Run Metadata

- Date: 2026-08-06 (Asia/Shanghai)
- Harness: Codex desktop, read-only evaluator subagents in the implementation task
- Model: inherited evaluator model; exact model ID was not exposed to the main task
- Control source: committed baseline `0019bbc0d757ceeefea3dfba85a5bdc15d7e6648`, read with `git show HEAD:<skill-path>`
- Candidate source: the content-addressed working-tree skill snapshot below
- Evaluator authority: return sampled behavior only; no edits, implementation, or commits
- Sampling: one paired control/candidate response per scenario. These samples establish the observed routing cases, not a statistical model-quality claim.

Candidate snapshot SHA-256 values used by the final recheck:

```text
38bbc5945ac6f0e9186820da72f6b802b8098ed0afbd63b21bbf1dc767168c89  skills/using-superpowers/SKILL.md
c0a70bec77e41cc73c8db7a570ffc87e9603bebfc14596a2abd960d25ceed86c  skills/brainstorming/SKILL.md
808fc5717aa88ad65efff312b11c186294d3e6ee301afb584e2f86599b137787  skills/systematic-debugging/SKILL.md
bf1b8216e523851a411e91d429a7c1c2a173e79d88957bc78e348218d50edd54  skills/test-driven-development/SKILL.md
5ee883ad3c4186c3ce8f9b745205073e7e5640d75bcbb80b2cfd9112ed4e89c2  skills/requesting-code-review/SKILL.md
077c1378f2fe1630dbf2cb6e6a32be672dd7bb0d0c5a5d2449aa26bf449677e9  skills/verification-before-completion/SKILL.md
```

Each evaluator received the named scenario and the same instruction: compare the committed control guidance with the current candidate guidance, use the fixed fields shown below, remain read-only, and return a concise raw response.

## E1: Short Read-Only Lookup

Evaluator task: `/root/eval_short_task`

Prompt scenario: `用户只问“当前 git 分支叫什么？”`

Raw response:

> SCENARIO：用户只问“当前 git 分支叫什么？”
>
> CONTROL：using-superpowers=是，旧版要求任何任务先调用；spec=否，无实现；TDD=否，无行为改动。
>
> CANDIDATE：using-superpowers=否，当前版明确排除一次完成的只读短任务；spec=否；TDD=否。
>
> VERDICT：Candidate 去除无效流程，同时保留直接只读查询与自然验证。

Final candidate recheck:

> CANDIDATE_FINAL：不调用 using-superpowers，不建 spec，不用 TDD；直接只读查询并以输出验证。
>
> VERDICT：符合当前短任务排除规则，审批门收紧未改变 E1 结论。

## E2: Long Research

Evaluator task: `/root/eval_analysis_task`

Prompt scenario: `跨数天研究技术路线，整合多篇权威材料、保存进度、最终区分事实/推断/未知。`

Raw response:

> SCENARIO：跨数天技术路线研究，整合权威材料、持久化进度，区分事实/推断/未知。  
> CONTROL：spec=强制软件化 executable spec；profile=无研究证据类型；TDD=批准后必进；结束证据=验收标准、测试映射与验证，难约束研究结论边界。  
> CANDIDATE：spec=单一可恢复执行与进度 authority；profile=研究证据+产物证据；TDD=仅改软件行为的 slice；结束证据=新鲜可定位证据、交叉印证、反证、覆盖缺口及最终核验。  
> VERDICT：Candidate 明确适配长期研究，避免误用全程 TDD。

Final candidate recheck:

> CANDIDATE_FINAL：使用单一可恢复 spec，按研究证据与产物证据分阶段保存进度；用户明确“持续做”时，经自检及必要只读审查后直接执行。事实、推断、NOT VERIFIED、未知均须有新鲜可定位证据，最终统一核验。TDD 仅用于改变软件行为的 slice。
>
> VERDICT：通过。审批门禁已区分非软件直行与软件批准基线，适配 E2。

## E3: Configuration Migration

Evaluator task: `/root/eval_general_task`

Prompt scenario: `长时间多系统配置迁移，有顺序、回滚、消费方验证，不修改软件行为。`

Raw response:

> SCENARIO：长时多系统配置迁移；顺序执行，保留回滚证据并验证消费方；不改软件行为。  
> CONTROL：spec=软件型可执行spec；profile=未区分；TDD=强制终态；review=重大spec只读审查，代码审查边界不清；finishing=未明确分型。  
> CANDIDATE：spec=唯一分片进度authority；profile=artifact/state；TDD=否；review=高风险spec只读审查，无代码review；finishing=否。以迁移前后状态、完整性、消费方、未变行为及回滚恢复为证据，最终执行完成前验证。  
> VERDICT：Candidate正确消除纯配置迁移被误路由到软件TDD与分支收尾的问题。

Final candidate recheck:

> CANDIDATE_FINAL：建立唯一中文 spec，按 artifact/state 分片；经自检和高风险只读审查后，因用户已授权“持续完成”可直接执行。以顺序、回滚、消费方及未变行为证据验收；不进 TDD、代码 review 或 branch finishing，最终执行完成前验证。  
> VERDICT：通过；审批门区分正确。

## E4: Cross-Module Software Change

Evaluator task: `/root/eval_software_task`

Prompt scenario: `跨模块新功能，有接口/schema 变化和兼容要求。`

Raw response:

> SCENARIO：跨模块新功能，接口/schema变化并要求兼容迁移。  
> CONTROL：无批准spec先brainstorm；用户批准后仅提交spec为BASE_SHA。按依赖slice做RED-GREEN-REFACTOR；接口、兼容、迁移均映射测试。跨组件spec只读审查，完成后基于BASE_SHA和新鲜测试做只读代码审查，主代理修复。  
> CANDIDATE：判定为长期任务；复用现有spec，否则建立唯一中文spec。行为slice需书面批准，或完整设计审阅后的明确预授权；生产变更前仍须独立spec baseline。按证据推进TDD，迁移可另列状态证据；证据失效即重开。  
> VERDICT：Candidate胜。保留批准、baseline、TDD与review门槛，同时强化任务路由、证据分类、续跑和失效重验。

Final candidate recheck:

> CANDIDATE_FINAL：通过。第9步明确：仅在书面spec批准，或用户审阅完整设计后明确预授权，才可执行；最终spec新增实质决定会使预授权失效。生产变更前必须单独提交approved spec并记录BASE_SHA，随后按slice TDD，跨模块spec/code只读审查。
>
> VERDICT：批准门无旁路；满足schema兼容场景的spec、baseline、TDD与review约束。

## E5: Long Intermittent Debugging

Evaluator task: `/root/review_long_task_spec` acting only as a behavior evaluator

Prompt scenario: `跨多天间歇性 bug，先复现/排除假设，根因后可能修代码，也可能无需代码。`

Raw response:

> SCENARIO  
> 跨多天排查间歇性 bug：复现、记录边界观测并排除假设；根因后可能修代码，也可能无需修改。
>
> CONTROL  
> 先走 systematic-debugging，能约束先查根因；但无持久、可恢复的诊断 spec/profile。brainstorming 终点固定为 TDD，也未定义“无需修改”的 research-only 终态。
>
> CANDIDATE  
> 建立唯一 mixed-profile spec；诊断切片保存复现、观测、排除项和根因证据，不进 TDD。仅需修复时转 behavior evidence + TDD；无需改代码则以 research evidence 完成，可跨上下文恢复。
>
> VERDICT  
> PASS：补齐可恢复诊断、profile 边界及无代码终态，同时保留修复时的严格 TDD。

Final candidate recheck:

> CANDIDATE_FINAL: 长期 debugging 建立唯一 mixed-profile spec；诊断由 systematic-debugging 驱动，以 research evidence 保存复现、边界观测、假设排除和根因。仅确认需修复时，修复切片进入 behavior evidence 与 TDD；无需代码修改则以研究证据结束，并支持跨上下文恢复。
>
> VERDICT: PASS。路由、证据边界及无代码终态均明确，修复时仍保持严格 TDD。

## Final Skills-Only Recheck

After plugin, package, hook, and harness-adapter removal, the five read-only evaluators re-read the final skill sources identified by the hashes above.

- **E1 short lookup:** `using-superpowers` is not invoked; no spec or TDD; direct read-only command output is the evidence. PASS.
- **E2 long research:** one resumable spec using research plus artifact evidence; human research does not use TDD; completion rechecks coverage, conflicts, unknowns, and claim boundaries. PASS.
- **E3 configuration migration:** one Chinese artifact/state spec; no TDD, code review, or branch finishing unless a slice changes software behavior; completion requires before/after state, consumer acceptance, protected-state, and rollback evidence. PASS.
- **E4 software change:** written approval or valid complete-design pre-authorization, separate approved-spec commit and `BASE_SHA`, slice-level RED-GREEN-REFACTOR, read-only review, and fresh final verification remain mandatory. PASS.
- **E5 long debugging:** one resumable mixed-profile spec; diagnosis uses research evidence, only a confirmed software fix uses TDD, and a no-code outcome may finish with verified research evidence. PASS.

All evaluators were read-only and made no edits, implementation changes, or commits.

## Evidence Boundary

These are fresh-context behavior samples, not plugin-installation, native-discovery, or external-harness integration transcripts. This skills-only repository does not claim or test end-to-end discovery for a specific harness.
