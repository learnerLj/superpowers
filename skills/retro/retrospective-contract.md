# 当前会话复盘合同

本合同拥有 `retro` 的证据 acquisition、完整 taxonomy、finding schema、去重和 action routing。

## 1 证据获取

```text
retro_scope = 当前 root session 在 review_cutoff 前可定位的证据
lineage_scope = 当前上下文已明确关联且在 cutoff 前回传的子任务证据
review_cutoff = 用户触发 retro 的 message boundary；runtime 有 timestamp 时同时记录
acquisition_status = complete | context-bounded | unavailable
persistence_intent = not_requested
```

`complete` 只用于 direct reader 已覆盖 root 和全部已关联 child。可见上下文可能缺少 compaction 前内容时必须用 `context-bounded`。缺失关键证据时保留 `unavailable`，不得猜测或扫描无关历史。

## 2 完整诊断 Taxonomy

| Category | 检查内容 |
| :--- | :--- |
| `goal-outcome` | 用户目标、约束、实际交付和完成层级是否一致 |
| `user-correction` | 用户纠正暴露的遗漏 authority、错误假设、scope 或表达偏差 |
| `navigation-authority` | owner、入口、真实配置、依赖或 SSOT 是否难找 |
| `hidden-dependency` | 文件、规则、runtime 或消费方之间未记录的依赖 |
| `tool-failure-recovery` | 调用错误、根因、重试、fallback 和最终恢复路径 |
| `tool-economy` | 重复读取、串行调用、无变化重试或大体积低收益读取 |
| `detour-scope` | 弯路、返工、scope creep 与额外探索的代价或资产 |
| `information-access` | 缺少日志、只读 API、状态入口、权限或可回查 authority |
| `automated-checks` | lint、test、schema、hook 或状态检查能否更早拦截错误 |
| `skill-effectiveness` | skill 是否应触发、实际触发、改变行为、重复或存在 instruction/description gap |
| `coding-standards-review` | reviewer 是否缺少应执行的标准，或标准需要删除、澄清 |
| `global-instruction-pressure` | 全局 instruction 是否过大，规则是否应下沉 |
| `knowledge-placement` | 内容应进入导航指针、review standard、reference、skill 或 repo doc |
| `instruction-ownership` | 规则的唯一 owner 是 instruction、skill、reference、reviewer 还是自动检查 |
| `no-op-guidance` | 哪些指令占用上下文却没有改变行为 |
| `implementation-review-boundary` | 高上下文实施与低上下文 reviewer 是否正确分工 |
| `collaboration-ownership` | 主 Agent、subagent、validator 与人工决定是否分工正确 |
| `context-lineage` | compaction、分支或 child lineage 是否造成重复探索或信息丢失 |
| `verification-completion` | 是否混淆 proposed、implementation green、review closed 与 overall complete |
| `memory-artifact` | 哪些稳定事实、偏好、失败模式、命令或 artifact 值得长期保留 |
| `successful-pattern` | 哪些选择减少了返工、风险或工具成本 |
| `handoff-continuity` | 交接是否保留目标、证据、dirty state、blocker 和下一 slice |
| `safety-permission` | 是否越过只读、写入、删除、secret、外部通信、提交或发布授权 |
| `unresolved` | 哪些结论未验证、动作待授权、失败未关闭或证据不可得 |

内部扫描全部 24 类。完整扫描不要求每类产生 finding。

## 3 Finding 数据结构

```text
finding_id
category
secondary_categories = []
priority = high | medium | low
evidence_locator
observed_fact
cost_or_impact
alternative_explanation
recommendation_owner
minimal_action
verification
retention_destination = memory | skill | instruction | automated-check | tool | documentation | session-only | none
recommendation_status = proposed | not_needed | unavailable
```

同一 `observed_fact` 只产生一条 finding。能解释问题并指向动作的根因类别是 `category`；症状、后果和相邻视角进入 `secondary_categories`。多个候选动作仍共享一个 primary owner，其它去向只作为 consumer。

## 4 Taxonomy 关闭映射

`audit` 投影为每个类别记录：

```text
category -> finding:<id> | not_needed | unavailable -> 基于输入的一句理由
```

Closure map 只证明这次逐类检查，不进入日常报告或长期记忆。

## 5 Instruction 与 Skill 健康检查

只有同时满足以下条件才提出变更：

1. 有可定位的重复失败，或单次高代价失败证明 contract 缺失。
2. 已完整读完目标 instruction 或 skill，不能只读开头。
3. 能指出唯一 owner、现有缺口和最小替换位置；已有规则被忽略时不追加同义句。
4. 先判断能否交给 validator、lint、hook 或 script；机械规则不继续挤压全局上下文。
5. 静态失效与行为效果分开：无效路径、命令和重叠 scope 是 maintenance；行为效果需要会话正反例。
6. 所有结论保持 `report-only`。

## 6 动作路由

| Destination | Owner 与门槛 |
| :--- | :--- |
| `memory` | 用户明确批准后，交给环境 memory owner |
| `skill` | 用户批准后由 `writing-skills` 进行 RED/GREEN |
| `instruction` | 交给该 repo instruction owner；不自动编辑 |
| `automated-check` | 交给 validator、lint、hook 或测试 owner |
| `tool` | 交给工具或集成 owner |
| `documentation` | 交给 canonical doc owner |
| `session-only` | 只保留当前报告 |
| `none` | 没有可执行落点 |

## 7 禁止项

- 不自动运行，不扫描未指定历史。
- 不输出没有证据意义的总分。
- 不为填 taxonomy 制造问题。
- 不把一次事实写成长期规律。
- 不写 memory、skill、instruction、hook、note 或 commit。
- 不把 diff 解释混成 process retro。
