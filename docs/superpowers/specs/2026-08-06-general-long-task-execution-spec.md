# 通用长任务执行 Spec

**状态：** 已批准，待实现

**日期：** 2026-08-06

**设计前代码基线：** `0019bbc0d757ceeefea3dfba85a5bdc15d7e6648`

**批准 Spec review baseline：** 由本文件的首次独立 commit 定义；commit 后在进度版本中记录精确 `BASE_SHA`

## 目标与非目标

### 目标

把 Superpowers 从“每次会话自动注入的软件开发方法论”改为“按需触发的长任务执行协议”：

- 短小、自包含且能一次完成验证的任务不创建 spec，也不调用 `using-superpowers`。
- 多阶段、存在依赖、风险、不确定性、持久进度或上下文中断可能的任务，使用一份 executable spec 约束执行。
- 软件开发、分析研究和其它长任务共享同一个 spec 核心，但使用与交付物匹配的完成证据。
- 只有修改软件行为的任务进入 TDD、code review 和 branch finishing。
- 删除 Claude、Cursor、Kimi、Pi、OpenCode 和 Gemini 对 `using-superpowers` 的自动 bootstrap；保留各运行环境对 `skills/` 的发现能力。

### 非目标

- 不重命名现有 skill。
- 不恢复独立 implementation plan、todo ledger、worktree 或实现 subagent 流程。
- 不把 TDD 泛化到人工分析、写作、研究判断或纯操作任务。
- 不为所有可能任务类型建立固定枚举；未知类型通过自己的交付物与完成证据定义执行 contract。
- 不向上游仓库提交 PR；这是个人 fork 的工作流变更。

## 当前系统上下文

当前 `using-superpowers` 通过 SessionStart hook、manifest 或平台扩展在会话开始及压缩后自动注入，并要求任何对话在行动前检查 skill。`brainstorming` 把所有 creative work 导向一份软件 executable spec，批准后的唯一终点是 TDD。`verification-before-completion` 的原则可复用，但完成交接默认绑定代码 review、commit 和 branch finishing。

已有软件开发主路径仍然有效：`brainstorming -> executable spec -> main-agent TDD -> read-only review -> verification -> branch finishing`。本次修改保留该路径，把它降为通用长任务协议中的“行为证明”profile。

## Authority 与表示

- `skills/using-superpowers/SKILL.md` 拥有“何时进入长任务协议、如何恢复已有 spec、如何选择执行 profile”的 authority。
- `skills/brainstorming/SKILL.md` 拥有 executable spec 的通用 contract 与 profile 扩展。
- 任务 spec 是目标、边界、执行切片、进度和完成证据的唯一持久 outline；不得再创建第二份 plan 或 todo 文档。
- 项目级 `AGENTS.md`、`CLAUDE.md`、`GEMINI.md`、策略论文或其它明确 authority 高于任务 spec。Spec 必须引用这些 authority，不能取代它们。
- `skills/verification-before-completion/SKILL.md` 拥有完成声明前的证据检查，但不拥有各任务的具体完成定义；具体定义来自已批准 spec。

## 触发 Contract

满足任一可观察条件时使用 `using-superpowers`：

- 有多个相互依赖的阶段；
- 需要保存持久进度或很可能跨上下文恢复；
- 存在会改变执行方向的重要未知项或决策；
- 需要整合多个 authority、来源、数据集或系统；
- 存在显著副作用、成本、风险、迁移或回滚要求；
- 用户明确要求 plan、spec 或约束执行文档。

一个任务只有在自包含、无重要分支、可在一次连贯处理内完成并验证时才属于短任务。短任务直接执行；可独立适用的专业 skill 仍按自身 description 触发，不需要先经过 `using-superpowers`。

## 通用 Executable Spec Contract

每份长任务 spec 至少包含：

1. **目标与非目标：** 可观察的最终结果与明确排除项。
2. **当前状态与 Authority：** 真实入口、已有产物、优先规则和恢复位置。
3. **交付物：** 最终文件、报告、代码、数据或外部状态，以及各自 owner。
4. **执行与数据流：** 输入如何经过分析、转换或实现形成交付物；不存在数据变化时明确写出。
5. **执行切片：** 依赖有序、结果导向、可独立验证的唯一执行 outline。
6. **完成证据：** 每个切片与整个任务凭什么算完成。
7. **调整条件：** 哪些新事实会使现有 spec 失效并要求重新批准。
8. **最终验收：** 完成前必须重新检查的 contract。

每个执行切片使用 Markdown 进度标记，并包含与任务语言一致的字段：

- **结果**
- **依赖**
- **工作范围**
- **输入与 Authority**
- **交付物**
- **完成证据**
- **验证或审查门槛**

完成的切片只有在声明证据新鲜且可定位时才能勾选。后续工作改变其输入、交付物或证据时必须重新打开。

## 完成证据 Profile

### 行为证明

适用于修改软件行为的任务。Spec 额外定义 owner、接口、schema、目标文件、acceptance criteria、test mapping、migration 与 compatibility。执行由主 agent 使用 TDD；完成后走 code review、verification 和 branch finishing。

### 证据证明

适用于分析和研究。Spec 额外定义核心问题、已知事实、假设与未知项、来源优先级、证据门槛、交叉验证、反证或冲突处置，以及事实、推断和未验证项的输出边界。人工研究和判断不进入 TDD；任务中新写的软件行为仍对那部分单独使用 TDD。

### 产物或状态证明

适用于写作、数据整理、配置、迁移、运维及其它长任务。Spec 额外定义目标产物或前后状态、允许的副作用、完整性检查、回滚或恢复证据，以及消费方验收。只有其中实际修改软件行为的切片进入 TDD。

同一任务可以组合 profile，但每个切片必须声明自己的完成证据，不能因为任务中存在少量代码就把全部工作强行解释成软件实现。

## 用户交互与恢复

- 用户要求“先规划”或“先给我看”时，写完 spec 后等待批准。
- 对证据证明和产物或状态证明，用户要求“直接做”“持续完成”或等价指令时，写完并自检 spec 后直接执行第一个依赖就绪切片；只有高优先级规则要求批准时才暂停。
- 对行为证明的软件任务，用户可以批准最终书面 spec，也可以在审阅完整设计后明确预授权继续实现。预授权仅在最终 spec 没有新增实质决策时有效；若 spec 改变目标、authority、交付物、完成证据或风险边界，仍须重新批准。无论采用哪种批准方式，实现前都必须把最终 spec 提供给用户并记录独立 baseline，不能让生产改动与 spec baseline 混合。
- 目标、authority、交付物、完成证据或风险边界发生实质变化时，停止执行、修订 spec 并取得必要批准。
- 恢复长任务时先定位已有 spec 与交付物，确认最后一个有证据的已完成切片，再从下一个依赖就绪切片继续；不得依赖聊天记忆重建状态。

## 自动 Bootstrap 移除

- Claude 与 Cursor：删除 SessionStart hook 配置、脚本和专用测试。
- Kimi：删除 `sessionStart.skill`，保留 skills 注册和平台工具映射。
- Pi：保留 `resources_discover` 的 `skillPaths`，删除 session、compaction 和 context bootstrap 注入。
- OpenCode：保留 `config.skills.paths`，删除首条用户消息 bootstrap transform 与缓存逻辑。
- OpenCode 的 action-to-tool mapping 迁到 `skills/using-superpowers/references/opencode-tools.md`，由 `using-superpowers` 在 OpenCode 上实际触发时按需读取。
- Gemini：停止强制 include `using-superpowers`；平台映射可继续独立加载。
- Codex 通过 `.codex-plugin/plugin.json` 的 `skills` 字段发现 bundled skills。仓库自带 Claude-compatible marketplace 使用 `.claude-plugin/marketplace.json` 的 `source: "./"` 安装仓库根，根目录 `skills/` 是 repo-owned discovery owner；Copilot CLI、Factory Droid 等外部 consumer/marketplace 是否正确安装该根目录，需要各自 clean-session transcript 证明，不能只凭本仓库 manifest 推断。Cursor 通过 `.cursor-plugin/plugin.json` 的 `skills` 字段注册 bundled skills。Antigravity 的 repo-root 安装和 Gemini extension package 保留 bundled `skills/` 与按需工具映射。这些路径都不补充等价的自动 prompt 注入。

## 长时间 Debugging

长 bug、测试失败或异常行为任务使用一份 mixed-profile spec：

1. `systematic-debugging` 先拥有 root-cause 调查方法；诊断切片使用证据证明，保存复现、边界观测、假设排除和根因证据，不进入 TDD。
2. 根因得到证据支持后，修复切片切换为行为证明，先写能复现问题的失败测试，再使用 TDD 实现修复。
3. 如果调查证明无需软件修改，任务以证据证明结束，不创建虚假的实现切片。

长任务 spec 负责持久进度和 profile 边界，`systematic-debugging` 负责诊断方法，二者不能互相替代。

## 目标文件

- 修改 `skills/using-superpowers/SKILL.md`：收窄触发、增加短任务退出、profile 路由和恢复 contract。
- 修改 `skills/brainstorming/SKILL.md`：改为通用 executable spec 生成器，并保留软件 profile 的既有严格字段。
- 修改 `skills/verification-before-completion/SKILL.md`：按 spec 声明的证据完成验证，代码交接仅用于行为证明。
- 保持 `skills/test-driven-development/SKILL.md`、`skills/requesting-code-review/SKILL.md` 和 `skills/finishing-a-development-branch/SKILL.md` 为软件专用。
- 修改 `README.md`、`CLAUDE.md`、平台 README、porting/testing 文档、`.github` issue/PR 模板及 manifests，使产品描述与新路由一致。
- 删除 `hooks/` 下自动 bootstrap 资产及其测试。
- 简化 `.pi/extensions/superpowers.ts`、`.opencode/plugins/superpowers.js` 与 `.kimi-plugin/plugin.json`，只保留 skill discovery 或工具映射。
- 修改 `scripts/sync-to-codex-plugin.sh`，使未来 Codex plugin 同步也永久排除根目录 `hooks/`，避免自动注入资产回流。
- 新增 `skills/using-superpowers/references/opencode-tools.md`，接管从 OpenCode bootstrap 中迁出的工具映射。
- 修改 workflow、Codex、Kimi、Pi、OpenCode、Antigravity 和 packaging 测试，锁定“可发现但不自动注入”。

## 验收标准

- **AC1：** 短任务不会被 `using-superpowers` 强制接管，也不要求创建 spec。
- **AC2：** 长分析任务生成证据证明 spec，可跨上下文恢复，不把人工分析强制送入 TDD。
- **AC3：** 长软件任务仍生成完整软件 spec，并进入主 agent TDD、只读 review 和验证。
- **AC4：** 其它长任务使用产物或状态证明，只有实际软件行为切片进入 TDD。
- **AC5：** 一个长任务只维护一份 spec 作为执行 outline 和进度 authority。
- **AC6：** 用户明确要求持续执行时，非软件 profile 在 spec 自检后可直接开始；行为证明的软件任务必须获得最终书面 spec 批准，或使用“完整设计已审阅且最终 spec 未新增实质决策”的明确预授权，并保留独立 baseline；重大 contract 变化会暂停修订。
- **AC7：** Claude、Cursor、Kimi、Pi、OpenCode 和 Gemini 不再自动注入 `using-superpowers`。
- **AC8：** 各 harness 的原生 discovery owner、manifest/package 注册和平台工具映射保持有效。当前环境没有对应可执行 harness 时，证据只证明发行/配置 contract，并明确标为未做 live end-to-end 验证，不能把静态检查表述成真实会话证明。
- **AC9：** 完成验证依据 spec 声明的行为、证据或产物/状态证明，不默认要求代码 commit。
- **AC10：** 活跃文档、贡献/issue 模板、manifest、package、同步脚本和测试不再把 SessionStart bootstrap 描述为正确集成条件，也不会在未来同步时重新引入根目录 hook 资产。
- **AC11：** 长时间 debugging 使用诊断证据切片与软件修复切片的 mixed profile，只有修复切片进入 TDD。
- **AC12：** OpenCode 删除 bootstrap 后仍有可发现、按需读取且被正向测试覆盖的工具映射。

## 测试映射

- `tests/workflow/test-spec-to-tdd-consistency.sh`：扩展为通用长任务 contract，覆盖 AC1-AC6、AC9。
- `tests/hooks/`：删除自动注入测试，workflow 测试断言 hook 资产不存在，覆盖 AC7、AC10。
- `tests/kimi/test-plugin-manifest.sh`：断言无 `sessionStart` 且 skills/mapping 保留，覆盖 AC7-AC8。
- `tests/pi/test-pi-extension.mjs`：断言只注册 skill path、不注册 bootstrap 生命周期 handler，覆盖 AC7-AC8。
- `tests/opencode/`：断言 skills path 注册且不存在消息 transform/bootstrap，覆盖 AC7-AC8。
- `tests/opencode/`：同时断言 `opencode-tools.md` 存在、被 `using-superpowers` 引用并保留 reviewer、skill、read/edit/bash/search/fetch 映射，覆盖 AC12。
- `tests/codex/test-marketplace-manifest.sh` 与 packaging 测试：断言发行包不重新引入 SessionStart hook，覆盖 AC7、AC10。
- `tests/codex-plugin-sync/test-sync-to-codex-plugin.sh`：使用包含 SessionStart 资产的上游 fixture，断言同步预览和目标插件永久排除根目录 `hooks/`，覆盖 AC7、AC10。
- `tests/antigravity/test-antigravity-tools.sh`：断言仓库内 Antigravity 映射存在且不依赖 bootstrap；这是 package contract 检查，不声称已启动真实 Antigravity 会话，覆盖 AC8 的静态部分。
- `tests/plugin-discovery/test-native-skill-discovery.sh`：断言仓库自带 Claude-compatible marketplace 的 `source: "./"`、仓库根 `skills/`、Cursor/Codex skills 字段均存在且无 hook 注册；它证明本仓库的共享 discovery owner，不替代外部 Copilot marketplace 的 clean-session transcript，覆盖 AC7-AC8 的静态部分、AC10。
- `tests/gemini/test-context.sh`：断言 Gemini extension context 不再 include `using-superpowers`，仍按需保留工具映射引用；本地未启动 Gemini CLI，覆盖 AC7 与 AC8 的静态部分。
- fresh-context 行为评估：分别使用短任务、长分析、其它长任务、长 debugging 和长软件任务，比较修改前后路由，覆盖 AC1-AC4、AC11。
- `tests/workflow/evidence/2026-08-06-general-long-task-routing-evals.md`：保存五组 paired control/candidate 的场景、运行边界和逐次原始返回，使行为证据可定位和复核。

## 行为评估证据

修改前的 fresh-context control 暴露了以下失败：短分支查询仍调用 `using-superpowers`；长研究虽生成 spec，随后仍被导向 TDD；纯配置迁移被强制解释成完整软件/TDD profile。长 debugging control 基本把 TDD 限于修复，但跨天诊断没有可恢复 spec，也没有“无需代码修改”的 research-only 验收终态。长软件开发 control 已保留严格的软件路径，说明本次修改需要防止该 contract 退化。

修改后对当前 skill 内容运行了五类只读 fresh-context evaluator：

| 场景 | 修改后结果 | 判定 |
| --- | --- | --- |
| 单次 git 分支查询 | 直接只读查询，不调用 `using-superpowers`，不创建 spec | AC1 通过 |
| 跨数天多来源研究 | 使用唯一 research-evidence spec，保存来源、冲突、未知项与证据边界；人工判断不进入 TDD | AC2 通过 |
| 多系统配置迁移 | 使用 artifact/state-evidence spec，声明顺序、消费方、回滚和前后状态；纯配置工作不进入 TDD/code review/branch finishing | AC4、AC9 通过 |
| 跨模块软件功能 | 使用 behavior-evidence spec、批准的 spec commit/`BASE_SHA`、主 agent TDD、只读 review 和 fresh verification | AC3、AC6 通过 |
| 跨天间歇性 debugging | 使用 mixed-profile spec；诊断走 `systematic-debugging` + research evidence，只有确认需要软件修复的 slice 进入 TDD；无需代码时以诊断证据结束 | AC11 通过 |

这些 evaluator 只返回行为判断，没有编辑、实现或提交。逐次 prompt、control/candidate 来源、harness/model 边界及原始返回保存在 `tests/workflow/evidence/2026-08-06-general-long-task-routing-evals.md`。平台 discovery 的静态测试与模型行为 evaluator 是两种不同证据，不能互相替代。

## 迁移与兼容

这是有意的行为变更。依赖旧 bootstrap 的 harness 将从自动强制触发改为原生 description discovery 或显式 skill 调用。Skill 名称和目录保持稳定，现有显式 `using-superpowers`、`brainstorming`、TDD、debugging、review 与 verification 调用继续有效。

平台不支持原生 skill discovery 时，不再通过全局 prompt 注入模拟；该平台必须提供自己的 skill 注册能力，或者由用户显式加载。历史 release notes 与旧 plans/specs 保留为记录，不作为活跃 workflow 检查对象。

## 实现切片

- [ ] **S1：建立新路由的 RED 证据**
  - **结果：** 静态 workflow 测试在现有实现上因短任务退出、非软件 profile、长 debugging mixed profile、OpenCode 映射迁移和无 bootstrap contract 缺失而失败。
  - **依赖：** 无。
  - **工作范围：** workflow 与 harness 回归测试。
  - **输入与 Authority：** AC1-AC12、现有行为评估样本。
  - **交付物：** 修改后的测试与失败输出。
  - **完成证据：** 失败原因只指向尚未实现的新 contract。
  - **验证或审查门槛：** `bash tests/workflow/run-tests.sh` 及相关 harness exact tests。

- [ ] **S2：实现通用长任务 spec 路由**
  - **结果：** `using-superpowers`、`brainstorming` 和 verification 支持短任务退出及三类完成证据。
  - **依赖：** S1。
  - **工作范围：** 三个 skill 与活跃 workflow 说明。
  - **输入与 Authority：** 通用 spec contract、现有软件 profile。
  - **交付物：** 更新后的 skill 文档与 README。
  - **完成证据：** workflow 测试通过；软件 profile 的 owner/interface/test contract 未退化。
  - **验证或审查门槛：** fresh-context 只读 evaluator review。

- [ ] **S3：移除跨平台自动 bootstrap**
  - **结果：** 所有活跃 harness 只注册技能发现或工具映射，不再注入 `using-superpowers`。
  - **依赖：** S1。
  - **工作范围：** hooks、manifests、Pi、OpenCode、Gemini、平台测试与文档。
  - **输入与 Authority：** 自动 bootstrap 移除 contract。
  - **交付物：** 删除/简化后的平台集成与同步测试。
  - **完成证据：** exact harness tests 通过，全文活跃扫描无 bootstrap 正向要求。
  - **验证或审查门槛：** 只读代码 review。

- [ ] **S4：全链路验证与行为复测**
  - **结果：** 静态 contract、平台集成、package 与短任务、长分析、其它长任务、长 debugging、长软件任务五类行为场景全部符合 AC1-AC12。
  - **依赖：** S2、S3。
  - **工作范围：** 当前变更覆盖的最小跨平台集合。
  - **输入与 Authority：** 测试映射和修改前基线样本。
  - **交付物：** 验证输出、修改后 evaluator 样本和最终 diff review。
  - **完成证据：** AC1-AC12 对应的所有相关测试退出 0，五类行为复测符合路由 contract，review 无 Critical/Important 问题。
  - **验证或审查门槛：** 独立只读 reviewer。
