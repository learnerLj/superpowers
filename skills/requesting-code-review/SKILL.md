---
name: requesting-code-review
description: 重大实现、复杂修复、公共接口或跨组件变更完成后，及用户要求独立审查时使用。
---

# 独立代码审查

重大实现、复杂修复、公共接口、跨组件或高风险变更完成后，派一个独立只读 reviewer；项目要求的合并审查照常执行。局部低风险修改可自审。

给 reviewer 用户要求、项目约束、本 skill 的审查边界、已有 spec 的位置、本次修改范围和有效验证结果。用 commit、快照或 patch 区分任务修改，明确未跟踪文件及基线缺口；不为审查额外要求 checkpoint 提交。

审查目标是确认需求与正确性，并识别可去除的复杂度。让 reviewer 自行选择检查方法；必要时使用 [code-reviewer.md](code-reviewer.md)。Reviewer 不实施修改，不把实现者的总结当作证据。

生产代码不为测试加入运行时不用的接口、字段、分支或旁路；测试专用 helper、fixture 和替身留在测试代码中。判断依据是有无真实生产职责，正常的依赖注入或生产边界不因方便测试而被禁止。

反馈交给 `receiving-code-review` 核查，按已有授权修复；原 reviewer 定点复查相关问题，不重复全量审查。最终由 `verification-before-completion` 验收整个任务。审查不增加提交或发布权限。
