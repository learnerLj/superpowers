# Skills 组合一致性收尾 Spec

## 目标与非目标

目标是让当前七个 skill 形成一套无隐藏入口、无重复 owner、可从触发条件走到明确终态的个人工作流，并删除会误导 Claude Code 或 Codex 的过时辅助材料。

不重写已经过行为验证的 TDD、系统化调试和 code review 核心纪律；不恢复 plugin、hook、session bootstrap、worktree 或独立 branch-finishing 流程；不重写历史 release notes 和已完成的历史 spec。

## 当前状态与 Authority

- 用户在本轮及前序讨论中已经确定：仓库只维护 skills；只支持 Claude Code 与 Codex 的原生发现；重要长任务由 `brainstorming` 产出唯一 executable spec；短任务不强制创建 spec；软件修改使用 TDD；reviewer 只读；最终以新鲜证据验证；删除 `using-superpowers` 与 `finishing-a-development-branch`。
- `AGENTS.md` 与 `CLAUDE.md` 是仓库级规则，但其中残留的 `superpowers:` plugin 命名空间已经与 skills-only 分发方式冲突。
- 当前七个入口是 `brainstorming`、`test-driven-development`、`systematic-debugging`、`requesting-code-review`、`receiving-code-review`、`verification-before-completion` 和 `writing-skills`。
- 基线提交是 `bf4f017`；工作树中已有本轮前序修改，必须保留并在其上收敛。

## 交付物

1. 七个 `SKILL.md` 的触发条件、职责、路由与终态一致。
2. `AGENTS.md`、`CLAUDE.md`、`README.md`、`docs/testing.md` 与当前 skills-only 流程一致。
3. workflow tests 直接断言当前 contract，不依赖一次性 evaluator 文件或固定历史文件数。
4. 删除没有活跃消费方且已与当前流程冲突的 skill 创建日志、压力题、CLAUDE.md bootstrap 实验和 `tests/workflow/evidence/`。

## 执行与数据流

```text
短任务 -> 适用专业 skill -> verification-before-completion

长任务 -> brainstorming -> 唯一 executable spec
  -> research/artifact slice -> 声明的研究或状态证据
  -> software slice -> test-driven-development
       -> requesting-code-review -> receiving-code-review
  -> verification-before-completion -> 交接或等待用户授权的 Git 操作

bug/失败 -> systematic-debugging
  -> 仅诊断时以根因证据结束
  -> 需要软件修复时进入 test-driven-development
```

唯一 owner：

| 事实 | 唯一 owner | 消费方 |
|---|---|---|
| 长短任务分类与 spec | `brainstorming` | 所有长任务 |
| 软件实现循环 | `test-driven-development` | software slice、有效 review finding 的修复 |
| 根因调查 | `systematic-debugging` | bug、失败和异常行为 |
| 发起只读审查 | `requesting-code-review` | 完成的软件实现 |
| 验证并处理审查意见 | `receiving-code-review` | reviewer findings |
| 完成声明 | `verification-before-completion` | 所有 evidence profile |
| skill 作者方法 | `writing-skills` | 新建或修改 skill |

## 执行 Slice

- [ ] **S1 当前 contract 的失败保护**
  - **结果：** tests 能发现 plugin 命名空间、过宽 review 触发、一次性 evidence 依赖和过时 supporting artifact。
  - **依赖：** 无。
  - **工作范围：** `tests/workflow/`。
  - **输入与 Authority：** 上述用户决定、七个现行 skill 与真实引用扫描。
  - **交付物：** 面向当前 contract 的静态失败断言。
  - **完成证据：** 修改 skill 前，新断言以预期原因失败。
  - **验证或审查门槛：** 检查失败信息只命中目标不一致。

- [ ] **S2 最小一致性修正**
  - **结果：** 活跃入口只有一套裸 skill 名路由，review 只针对软件实现，过时材料不再参与发现或测试。
  - **依赖：** S1。
  - **工作范围：** 仓库 authority、相关 skill、README/testing 文档及已识别的过时文件。
  - **输入与 Authority：** S1 的失败、引用与消费方扫描。
  - **交付物：** 最小文本修正和精确文件删除。
  - **完成证据：** S1 断言转为通过，所有链接仍可解析。
  - **验证或审查门槛：** 不压缩 TDD/debugging 中没有行为失败依据的纪律性重复。

- [ ] **S3 全量验证与只读审查**
  - **结果：** 七个 skill 的组合 contract、中文内容、辅助脚本和最终 diff 均通过检查。
  - **依赖：** S2。
  - **工作范围：** 当前工作树全部相关修改。
  - **输入与 Authority：** 当前 spec、workflow tests 和 skill validators。
  - **交付物：** 新鲜验证结果与 reviewer findings。
  - **完成证据：** workflow、七个 quick validator、debug helper、shell lint、`git diff --check` 通过；只读 reviewer 无阻塞 finding。
  - **验证或审查门槛：** reviewer 不得编辑或实施修复。

## 完成证据

这是 behavior evidence 与 artifact evidence 的混合任务。skill 路由和触发词由失败先行的静态 contract test 保护；删除文件由引用/消费方扫描、链接检查和完整测试保护。一次性 evaluator 原始响应属于任务过程证据，不再作为仓库运行时或测试输入保存。

## 修订条件

如果扫描发现某个待删文件仍被活跃 skill 直接加载、某项修改会改变已验证的 TDD/debugging 行为，或 Claude Code/Codex 的原生发现要求必须使用命名空间，则停止对应删除或措辞修改并修订本 spec。

## 最终验收

- 七个入口名称和全部内部路由一致，不出现 `superpowers:` 前缀。
- `requesting-code-review` 与 `receiving-code-review` 只在软件审查链路触发。
- 不存在 `using-superpowers`、`finishing-a-development-branch`、plugin/hook 的活跃引用。
- `tests/workflow/evidence/` 不存在，测试不读取一次性评估文件。
- 已删除 supporting artifact 没有活跃消费方，保留的 supporting file 都能从入口按需到达。
- 全部声明以当前工作树上的新鲜命令输出为证据。
