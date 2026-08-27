# 多会话 Skill 有效性审计

本合同用于比较多个已落盘会话，判断 skill 是否在应触发时被发现、是否改变目标行为，以及维护问题属于哪一个 owner。它不使用总分，不自动修改 skill。

## 1 Scope 预检

固定要求：

```text
review_purpose = skill-effectiveness-audit
scope_kind = multi-session
review_depth = deep
persistence_intent = report-only
```

先按来源 reference 建立 canonical session scope 和 lineage。至少保留一个 skill 已触发但仍返工的反例，以及一个未发现目标 skill 但结果成功的反例；没有足够正反例时写 `unavailable`，不提行为修改。

## 2 完整读取目标 Skill

审计前完整读取目标 `SKILL.md` 以及它标记为当前场景必读的 supporting files。不能只读 frontmatter、前 30 行或最后修改时间。

静态维护检查只覆盖：

- 引用路径是否存在；
- 明确命令能否执行；
- description 是否与其它 skill 重叠或漏掉已观察触发词；
- runtime validator 是否通过。

`last-modified` 只能决定检查顺序，不能证明 stale 或 ineffective。

## 3 行为证据

每个目标 skill 分开回答：

1. 哪些 session 按任务症状应发现该 skill。
2. 哪些 session 有可定位的发现或加载证据。
3. 加载后具体改变了哪个动作、边界或验证结果。
4. 哪些反例不支持「skill 导致成功」。
5. 最小修改本可以避免哪个已观察失败；无法回答时不提修改。

触发次数、coverage、总分和结果成功都不能单独证明行为效果。

## 4 失败归因

```text
failure_attribution =
  instruction-gap
  | description-gap
  | model-variance
  | tool-gap
  | existing-rule-ignored
  | unavailable
```

`existing-rule-ignored` 默认对应 `recommendation_status=not_needed`，不得追加同义规则。只有独立证据证明 description、工具或 validator 缺口时，才能改用相应 attribution。

静态维护状态另行记录：

```text
maintenance_status = invalid-path | invalid-command | overlapping-scope | validator-failure | maintenance-ok
```

静态错误不能写成行为效果差。

## 5 输出 Schema

```text
skill_name
skill_path
sessions_expected
sessions_detected
behavior_change_evidence
counterevidence
failure_attribution
maintenance_status
recommendation_owner
recommendation_status = proposed | not_needed | unavailable
```

所有建议默认 `report-only + not_requested`。用户明确批准修改后，才由 `writing-skills` 接管具体 RED/GREEN；本审计不得 patch、create、delete、commit 或自动应用 diff。

## 6 证据边界

观察性历史会话不能形成严格 A/B 因果。会话缺失、lineage 不清或 runtime 没有 skill-load 证据时保留 `unavailable`；不得从最终输出风格反推 skill 一定被加载。
