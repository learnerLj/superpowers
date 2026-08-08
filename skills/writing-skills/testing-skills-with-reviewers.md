# 用只读 Evaluator 测试 Skills

**加载时机：** 创建或编辑 skill 后、部署前，需要验证行为改变而静态检查不足时使用。

## 概述

evaluator 的职责是产生可比较的行为证据，不是替作者实施、编辑或决定规则。先定义可观察缺口，再用最小代表场景比较 no-skill control 与 candidate；证据足够改变决定就停止。

不是所有修改都需要 evaluator。规范事实、引用新鲜度、frontmatter、链接和机械约束应优先使用当前 authority、静态 contract 和 validator。真实 session artifact 已经清楚暴露缺口时，也可以直接作为 RED 证据。

## 先选择证据类型

| 可观察缺口 | 首选证据 | 不要默认使用 |
|---|---|---|
| description 错触发或漏触发 | 应触发/不应触发 prompt | 压力场景 |
| 明知规则仍合理化绕过 | 同一任务的 control/candidate | 学术复述题 |
| Technique 无法应用或迁移 | 真实任务、一个关键变体 | 强制 A/B/C |
| Pattern 被误用 | 正例、反例、边界例 | 只问定义 |
| Reference 找不到或已过时 | 检索任务、当前 authority | 纪律压力 |
| 输出缺字段或形状错误 | schema/template contract | “不要遗漏”的禁令 |
| script 行为错误 | 确定性测试和代表样本 | LLM 自评 |

只有预期 skill 会改变 agent 行为、且其它证据不足时，才调用 fresh-context evaluator。

## TDD 映射

| 阶段 | Skill 测试 | 动作 |
|---|---|---|
| RED | control 或真实 artifact | 记录无指导时的具体缺口 |
| GREEN | candidate | 加载最小修改后运行同一代表场景 |
| REFACTOR | 定向回归 | 只处理新观察到的漏洞并复验受影响场景 |

## 场景设计

1. 先写成功标准：哪些输出或动作可以直接观察，什么结果会推翻修改。
2. 使用真实任务形状、真实约束和足够上下文，但不泄露预期答案或作者结论。
3. control 与 candidate 除 skill 是否加载外保持一致。
4. evaluator 只返回响应或 artifact，不编辑 skill、不实现任务、不提交。
5. 保留 prompt、skill source/hash、原始输出、判定和证据边界。

### 按 skill 类型设计

- **纪律型：** 从已经观察到的合理化或违规出发，只加入与该失败相关的时间、沉没成本、权威或疲劳压力。允许 agent 解释行动，不强制把复杂现实压成 A/B/C。
- **Technique：** 让 agent 完成一个代表任务，再测试一个真正改变应用方式的变体或缺失信息场景。
- **Pattern：** 测试何时采用、如何采用和何时不用；反例与边界比重复正例更有价值。
- **Reference：** 测试能否找到、正确应用并识别过时或缺失信息。
- **Trigger：** 使用应触发、相邻但不应触发和明确显式调用的 prompt。

压力不是目标本身。没有实际纪律失败时，不叠加压力；一个真实 pressure 已能暴露缺口时，不为达到数量要求继续堆叠。

## 评测预算

默认只运行 1 次 RED control 和 1 次 GREEN candidate。只有实际响应出现方差、规则歧义或 candidate 仍违规时，才逐次增加样本；每次增加前说明它会改变哪个决定。

多场景、多候选任务必须先设置 evaluator 总调用预算，禁止直接展开 `fixture × candidate × wording × repeat` 完整矩阵。先用最小代表场景淘汰明显不合格方案；回归只覆盖被修改规则直接影响的场景。

普通 Technique、Pattern、Reference 或 trigger 场景单项最多 3 次。5 次重复只用于已有证据表明存在高方差的高压力纪律型 skill，并须事先获得 human partner 对总预算的明确批准。

## RED：记录缺口

control 不是为了让 agent “输”，而是确认问题存在。记录：

- 哪个可观察标准未满足；
- 原始输出中的决定、缺失字段或合理化；
- 哪部分场景触发了问题；
- 哪项最小规则可能改变该结果。

control 没有暴露目标缺口，就停止 authoring 或重写场景。不要增加重复次数来等待一次失败。

## GREEN：验证最小修改

只针对 RED 证据修改 skill，再运行同一代表场景。通过意味着当前缺口已被覆盖，不代表 skill 在所有任务、模型和 runtime 上普遍有效。

GREEN 已通过且没有观察到新违规时停止。candidate 仍失败时，先判断是规则缺失、场景歧义、宿主未加载 skill，还是判定标准无法观察；不要自动归因于“措辞不够强”。

## REFACTOR：定向堵漏

只有 candidate 出现新的、可复核的漏洞时才添加 counter。规则形式要匹配失败：

- 合理化绕过：明确 predicate、禁止项和停止信号；
- 输出形状：正向 schema、template 或 required slot；
- 检索失败：调整结构、关键词和入口导航；
- 机械约束：validator 或 script；
- 权限风险：宿主权限、approval 或隔离，不靠说服措辞。

修改后只重跑直接受影响的场景。历史 fixture 未触及该规则时，不重新执行。

## Meta-Test 元测试

当 candidate 失败且原因不清时，可以问 evaluator 它为何采取该行动、缺了什么信息、哪段未被发现。Meta-test 只提供诊断线索，不是行为通过或 skill 完成的证据；模型对自身原因的解释可能不准确，必须回到原始输出和可观察结果验证。

## 判定状态

- **VERIFIED：** candidate 满足预先定义的可观察标准，control 显示对应缺口，且没有相关新回归。
- **NOT VERIFIED：** candidate 仍违反标准，或 skill 没有改变目标行为。
- **INCONCLUSIVE：** 场景、加载状态、judge 或输出无法区分结果。

遇到 `INCONCLUSIVE` 就停止当前扩样，先修场景、判定标准或证据来源。它不是继续调用直到出现期望答案的许可。

## 完成标准

完成需要原始 control/candidate artifact、明确判定标准、预算内结果和已知证据边界。引用规则、选择预设选项、声称“我会遵守”或通过 meta-test，都不能单独证明真实任务行为。

## Checklist 检查表

- [ ] 已定义可观察缺口与能推翻修改的结果
- [ ] 已选择适合 skill 类型的最小证据
- [ ] control/candidate 除 skill 外保持一致
- [ ] evaluator 只读，未实施或编辑
- [ ] 已保留 prompt、skill 版本、原始输出和判定
- [ ] 已预设总调用预算和停止条件
- [ ] 只在实际方差、歧义或继续违规时扩样
- [ ] 只重跑受修改规则影响的场景
- [ ] meta-test 只作为诊断线索
- [ ] 结果标为 VERIFIED、NOT VERIFIED 或 INCONCLUSIVE

## 常见错误

- 把每次文档更新都变成行为评测；
- 用固定三重压力或强制选择替代真实任务；
- 把 evaluator 的自我解释当作行为证据；
- candidate 通过后继续寻找假想漏洞；
- 展开完整组合矩阵；
- judge 无法区分结果时继续抽样；
- 修改一条规则后无差别重跑全部历史 fixture。

**结论：** evaluator 是有限预算的测量工具。先匹配证据类型，得到足够证据后停止。
