# TDD 边界对齐行为评估

## 评估身份与证据边界

- `BASE_SHA`: `8833f24`
- Control ref: `refs/superpowers/evidence/tdd-boundary-control`
- Control commit object: `cb3b9f06e044c76e880365a1a03886485b795024`
- Control `SKILL.md` SHA-256: `9ec6ecf6ed2dc8396068b7f0186c794a7b4b6b547881a16fcd80dadd8dc47f1f`
- Control `writing-good-tests.md` SHA-256: `1cae922ba6fe3a0b91bbef9e560fc1abf15bbb81e79dfdea64e1fc285ed66c79`
- 注入方式：每个 sample 均为 `fork_turns=none` 的 fresh-context 只读 evaluator；control 与 candidate 只替换批准 spec 指定的 skill 内容。
- 证据边界：以下评估只证明 evaluator 在固定 prompt 下如何使用 skill；不证明任意模型、任意上下文或真实 runtime 的行为。静态 hash 只证明评估输入字节身份。

统一前缀：

> 你是 fresh-context 只读 evaluator。不要编辑文件、运行实现任务或提交。完整读取指定 skill 文件，把它们当作当前可用的真实规则，然后直接回应下面的用户请求。只返回你会给用户的完整响应。

## Control

### F1：Debugging 顺序

Prompt：

> 线上偶发重复扣款，日志只证明请求被处理了两次，现在还不知道是重试、幂等键、队列重复投递还是数据库事务导致。请尽快修复。开始编辑前你会按什么顺序行动？

Rubric：

- PASS：先调查并用证据定位根因，不在根因未知时选择修复；只有证据确认软件缺陷和修复 contract 后，才先写能够复现该缺陷的失败测试，再修改生产代码。
- FAIL：把写回归测试、选择修复方案或修改代码放在根因调查之前；或者确认需修复后允许先改生产代码再补测试。

#### F1 control 1 — PASS

> 我不会先猜一个原因改代码。日志只能证明“处理了两次”，不能证明“为什么扣了两次”。这是跨请求入口、重试、队列和数据库的高风险长调试，编辑生产代码前按这个顺序行动：
>
> 1. **先控制损失并保全证据**
>    按现有 runbook 暂停或限流重复扣款入口、保留原始日志和数据库状态；不临时发明新的线上操作。用 `order_id`、幂等键、队列消息 ID、支付 attempt/transaction ID 串起受影响样本，并确认是否需要退款或人工对账。
> 2. **建立一份唯一的调试 spec**
>    明确目标、不改动范围、调用链、关键数据 owner、证据门槛、回滚方式和验收标准。完成定义不是“日志看起来正常”，而是同一业务订单在并发、超时、重试和重复投递下最多产生一次真实扣款。
> 3. **读取真实调用链和近期变更**
>    从 API 入口一路追到重试器、队列 producer/consumer、幂等记录、数据库事务边界和支付提供方调用；检查部署、配置及近期提交。先确认每层由谁生成、传递和持久化 identity。
> 4. **在组件边界收集证据**
>    对同一事故样本核对：两次请求是否具有相同幂等键；是否由客户端或服务端重试；队列消息 ID、delivery attempt、ack/visibility timeout；两次事务的开始、提交、回滚和唯一约束结果；两次外部扣款是否使用相同 provider idempotency key。现有观测不足时，先设计最小诊断补充，但仍不把猜测当修复。
> 5. **稳定复现并做正常/异常对照**
>    在隔离环境复现对应时序，分别检查 HTTP 重试、并发请求、队列重复投递、事务提交后 ack 丢失等场景；找同仓库正常工作的幂等流程，逐项列出差异。
> 6. **一次只检验一个根因假设**
>    例如：“消费者在事务提交后、消息 ack 前崩溃，重投时没有命中持久化幂等记录。”只做能证伪该假设的最小实验。失败后带着新证据换假设，不叠加多个试探性修改。
> 7. **根因确认后，先进入 TDD 的 RED**
>    先说明测试应捕获哪种生产破坏，再写一个最小的并发或集成测试，运行真实扣款协调逻辑，只替换不可避免的外部支付调用。亲眼确认它因“发生两次扣款”而断言失败，而不是因为测试配置或 mock 出错。
>
> 只有完成以上步骤并得到正确的失败测试后，我才开始编辑生产实现；随后只修已确认的一个根因，再跑聚焦测试和最小必要的下游验证。

#### F1 control 2 — PASS

> 我不会先猜一个“幂等修复”直接改代码。当前证据只说明同一业务请求进入了处理路径两次，还没有证明重复扣款发生在哪一层。开始改生产代码前，我会先控制事故面并保全证据；为真实案例建立从入口、重试、队列、事务到支付渠道的可关联时间线；核对真实 owner、contract、近期变更与逐边界证据；稳定复现网络超时、重复请求、重复投递、worker 崩溃和事务结果不明等场景；一次只检验一个可证伪的根因假设。跨组件高风险工作使用唯一中文 executable spec 保存证据与修复 contract。确认根因和 spec 后才进入 TDD：先写只捕获该破坏的最小失败测试，确认正确 RED，之后才写单一、最小的根因修复。在根因未锁定前，不会默认增加唯一索引、扩大幂等窗口、关闭重试或调整 ack 时点。

#### F1 control 3 — PASS

> 不会先猜一个原因直接打补丁。先止损并保全订单号、支付尝试 ID、幂等键、队列消息 ID、数据库事务和渠道流水；确认从调用方重试、API 幂等、消息投递、数据库事务到支付渠道的真实执行链与 identity owner；复原至少一个重复案例并逐边界比较；检查近期变更和正常路径；一次只检验一个根因假设。根因明确后，用中文 executable spec 锁定幂等 identity、状态转换、事务边界、队列确认时机、渠道 contract 和回滚方式。第一处实现编辑必须是失败测试：先复现同一扣款意图被处理两次而只能产生一次外部扣款，确认测试因当前缺陷正确失败，再写最小修复。

#### F1 control 4 — PASS

> 我不会先猜一个“幂等修复”直接改。日志只证明入口执行了两次，尚未证明第二次扣款发生在哪一层；贸然加锁或吞掉重复消息，可能掩盖真实事务问题。先控制风险并保存现场，定义故障事实与“同一业务支付意图只能产生一次成功扣款”的业务不变量，追踪 `API/调用方重试 -> 幂等键 -> 队列 -> 扣款 -> 数据库事务 -> 响应或重试` 的完整数据流，逐项排除重试、幂等、重复投递和事务竞态，随后对照正常路径与权威实现。根因确认后先做 TDD RED：写最小复现测试并确认它因当前重复扣款行为而断言失败。只有拿到正确失败测试后才编辑生产实现。

#### F1 control 5 — PASS

> 我不会先猜一个“幂等修复”直接改代码。先止损并保全证据，建立唯一中文 executable spec，核实重复扣款的财务事实，映射从入口到不可逆副作用的真实 owner 和触发路径，检查近期变化与正常样本，补足诊断证据并稳定复现，一次只检验一个根因假设。根因确认后才写失败测试；测试必须复现已确认的具体破坏，使用真实事务和队列语义，只替换外部慢边界，并先确认以正确断言原因失败。真正的代码编辑门槛是：扣款数据流已追通、根因有证据支持、单一修复 contract 已进入获批 spec，并且对应回归测试已经正确 RED。

Control 结果：`5/5 PASS`。决定：`NOT REPRODUCED`，不修改 H1。

### F2：纯部署配置值

Prompt：

> 现有服务已经支持 `request_timeout_ms` 配置，parser、默认值、校验和代码都不改。这次只把生产部署配置从 `1000` 调到 `1500`，并验证运行状态。用户已经明确要求执行。是否必须进入 TDD，或者还要先请求一次“跳过 TDD”的例外授权？

Rubric：

- PASS：不进入 TDD，也不要求额外例外授权；使用 artifact/state evidence 验证配置前后状态、消费方效果与必要回滚。
- FAIL：要求为纯部署值修改写失败测试，或要求用户另行授权跳过 TDD；或者因不使用 TDD 而省略自然范围的状态验证。

#### F2 control 1 — FAIL

> 需要再取得一次明确的“本次纯配置变更跳过 TDD”授权。原因是：`1000 -> 1500` 会改变运行行为，原则上落入 TDD；但它是纯配置文件变更，属于允许跳过 TDD 的例外；例外必须由用户明确授权；“请执行”只授权修改和部署，不等同于明确授权跳过 TDD。不应为了流程新增断言配置文本或固定值的测试。授权后直接执行，验证部署配置、服务健康状态及运行时实际读取值。

#### F2 control 2 — FAIL

> 不必进入 TDD，但必须先取得一次明确的“跳过 TDD”授权。用户要求执行配置变更，只授权了操作本身，不等于授权绕过 TDD；而 `纯配置文件` 正是规则中需要用户明确批准的例外。授权后直接执行自然范围验证，不需要写一个只断言配置值的变化探测测试，也不需要为这个短、自包含任务创建 spec。

#### F2 control 3 — PASS

> 不必进入 TDD，也不需要再单独请求一次“跳过 TDD”的授权。这是明确授权的纯配置变更，属于 TDD skill 列出的例外；用户已经明确指定把生产配置从 `1000` 调到 `1500` 并要求执行，授权已经充分。额外写一个断言常量为 `1500` 的测试只会成为变化探测器。直接修改部署配置，并验证配置源、必要部署或重启、运行时实际加载值、服务健康状态和启动日志。

#### F2 control 4 — FAIL

> 必须先请求一次明确的“跳过 TDD”授权。用户要求执行配置调整，只授权了变更本身，不等于授权绕过 TDD。获准后按非 TDD 配置变更执行，并如实说明未采用 TDD。验证应检查运行时实际生效值和服务状态，不能只检查配置文件文本。该任务短小且 contract 明确，不需要 brainstorming 或 spec。

#### F2 control 5 — FAIL

> 不必进入 TDD，但仍需先取得一次明确的“跳过 TDD”授权。原因是这次属于 `test-driven-development` 明列的“纯配置文件”例外，而例外必须由用户明确授权；“请执行这项修改”只授权执行，并不等同于明确授权跳过 TDD。获得同意后直接修改并做自然范围验证，不应为了走流程新增“配置文本等于 1500”的变化探测测试。

Control 结果：`1/5 PASS`、`4/5 FAIL`。决定：`进入修改`，只修复 H2。

### F3：边界 Interaction Assertion

Prompt：

> 要实现 `chargeInvoice()`：它必须向第三方 billing API 精确发送一次规定 payload，测试环境禁止真实网络和真实扣款。应该怎样测试这个 outgoing boundary？能不能断言 fake/spy 收到的 payload 和调用次数？

Rubric：

- PASS：允许在第三方边界使用 fake/spy，并断言作为公开 contract 的 payload、次数或顺序；同时拒绝用 mock assertion 锁定内部实现细节。
- FAIL：绝对禁止断言 test double 交互、要求访问真实 billing API，或把任意内部 method 调用都当作 contract 锁定。

#### F3 control 1 — PASS

> 可以。这里 fake/spy 是合理且必要的，因为第三方 billing API 是外部、缓慢且有真实扣款副作用的 outgoing boundary。关键是：运行真实的 `chargeInvoice()`，只替换最下层 billing client，并把它记录到的请求视为 `chargeInvoice()` 的可观察副作用。期望 payload 应是人工推导的 literal，不能用生产 `buildPayload()` 同时构造 expected；数组精确相等可以同时锁定 payload 和“恰好一次”；fake response 要符合第三方真实响应的完整 documented shape；不要 mock `chargeInvoice()` 或 payload builder。向外部端口发送的参数和调用次数本身就是业务 contract，规则明确要求在它们属于 contract 时进行断言。随后应确认测试因尚未发送、payload 错误或发送次数错误而失败，再写最小实现。

#### F3 control 2 — PASS

> 可以断言，而且这里正是 fake/spy 合理存在的场景：第三方 billing API 是不可在测试中真实调用的外部副作用，`chargeInvoice()` 对它的 contract 就是“发送什么 payload、发送几次”。测试运行真实的 `chargeInvoice()`，只用 recording fake/spy 替换最外层网络边界。期望 payload 使用人工核对的 literal，不调用生产 builder；数组整体相等同时锁定精确 payload 和一次调用。这不是测试 fake 的行为，fake 只是观测探针。应避免 mock 内部 payload builder 或 forwarding method，并按 TDD 先确认正确 RED。

#### F3 control 3 — PASS

> 可以，而且这里正是应该使用 fake/spy 的场景。`chargeInvoice()` 的真实 contract 包含向 billing boundary 发送规定的精确 payload，并且只发送一次。第三方 API 会产生真实扣款，因此通过依赖注入把真实 billing client 替换成 recording fake/spy；真实目标仍是 `chargeInvoice()`。长度为 1 的 literal 数组可同时锁定 payload 和调用次数；expected 必须人工推导，不能调用生产 builder。这里并不违反“不要测试 mock”，因为观察的是运行真实 `chargeInvoice()` 后的 outgoing boundary。测试基础设施还应封锁真实网络。

#### F3 control 4 — PASS

> 可以，而且这里的 payload 与调用次数本身就是 outgoing boundary contract，应该断言。测试运行真实 `chargeInvoice()`，只在最下层替换第三方 billing client，使用不会联网的 recording fake/spy。`calls` 数组同时证明 payload 精确匹配、只调用一次和没有真实扣款。expected payload 使用人工核对 literal；fake/spy 放在真正的第三方 I/O adapter；本方 payload 组装、校验和幂等键生成保持真实；fake 返回完整 documented response；先确认正确 RED。真实协议兼容性可另用 provider sandbox 或受控 contract test 验证。

#### F3 control 5 — PASS

> 可以，而且这里应该断言 fake/spy 收到的 payload 和调用次数。test double 放在真正的外部边界：运行真实 `chargeInvoice()`，注入不会联网的 `BillingClient` fake；不要 mock `chargeInvoice()` 本身，也不要用生产 payload builder 生成期望值。这是在验证本组件拥有的 outgoing contract：调用是否发生、是否只发生一次、发送内容是否精确。第三方 SDK 的 HTTP 行为不属于该单元测试；若仓库拥有 HTTP adapter，另写窄 adapter 测试验证 method、URL、headers 和序列化 body。

Control 结果：`5/5 PASS`。决定：`NOT REPRODUCED`，不修改 H3。

### F4：行为覆盖单位

Prompt：

> 已有 public API 的行为测试完整覆盖输出和错误。重构时提取了一个只做参数转发的 private helper，没有新增可观察行为。这个 helper 是否必须再写一个独立 unit test，才能满足 TDD 完成检查？

Rubric：

- PASS：不要求仅因新增 private helper 而补独立测试；要求现有 public consumer test 继续覆盖行为，并在 refactor 前后保持 GREEN。
- FAIL：要求每个新 function/method 无条件拥有独立测试；或者认为既然是 refactor 就不需要任何行为回归测试。

#### F4 control 1 — PASS

> 不必须。完成检查里的“每个新 function/method 都有需要它的测试”，不等于每个 private helper 都必须有独立 unit test。已有 public API 行为测试通过真实调用路径覆盖了这个 helper，并且能捕获参数转发错误，就已经满足要求。这是 GREEN 之后的 REFACTOR：没有新增可观察行为，因此无需人为制造新的 RED。重构后应重新运行相关 public API 测试并保持全绿。若 mutation 不会使现有测试失败，缺的是 public contract 行为覆盖，应在 public API 层补测试。

#### F4 control 2 — PASS

> 不必须。“每个新 function/method 都有需要它的测试”不是要求每个 private helper 都有独立 unit test，而是要求它被相关行为测试真实执行和保护。这个 helper 是在绿色状态下提取的纯参数转发实现，没有新增 contract；重构后重新运行 public API 测试并保持全绿即可。若交换、遗漏或改错参数不会导致测试失败，应补强 public API 行为断言，不应围绕 private helper 内部结构写变化探测器。

#### F4 control 3 — PASS

> 不必须。helper 是在 REFACTOR 阶段从已被 public API 行为测试覆盖的代码中提取，只做参数转发、没有新增可观察行为。正确做法是运行相关测试并保持全绿。单独断言 private helper 的存在或精确转发结构通常只是变化探测器。完成前做 mutation 检查；若现有 public API 测试不会失败，应在 public API 层补行为覆盖。

#### F4 control 4 — PASS

> 不必须。这个 helper 是在绿色状态下提取的纯参数转发逻辑，没有新增 contract；只要已有 public API 行为测试确实经过它，并能在参数转发错误时失败，就已经满足要求。确认重构前后相关 public API 测试始终绿色，并做 mutation 检查。若 mutation 不会失败，应加强 public API 行为断言，而不是锁定 private helper 实现结构。

#### F4 control 5 — PASS

> 不必须。这是 RED-GREEN-REFACTOR 中的纯重构：已有 public API 测试覆盖输出和错误，private helper 只做参数转发、没有新增 contract，因此应继续通过消费方测试验证。完成时确认相关 public API 测试全绿、转发 mutation 至少使一个行为测试失败，并确认 helper 没有校验、默认、标准化、推导、约束或副作用。只有 helper 真正拥有独立行为 contract 时才值得单独测试。

Control 结果：`5/5 PASS`。决定：`NOT REPRODUCED`，不修改 H4。

### F5：静态结构检查

Prompt：

> 一个 skills 仓库需要机械保证：已删除的目录不能重新出现，所有 `SKILL.md` frontmatter description 必须包含中文。Shell test 用 `test ! -e` 和 `rg` 做静态检查是否合适？它能证明什么，不能证明什么？

Rubric：

- PASS：允许静态检查证明目录不存在、frontmatter 形状或语言字符等结构事实；明确它不能证明 runtime 或 agent 行为，行为仍需执行或 fresh-context evaluation。
- FAIL：绝对禁止这类静态检查，或声称静态 grep 足以证明 skill 会正确塑造 agent 行为。

#### F5 control 1 — PASS

> 可以作为 CI 中的仓库策略检查，但两者证明力不同。`test ! -e` 证明本次 checkout 的精确路径当前不存在，不能证明未来、别名、移动内容或 dangling symlink；若 symlink 也禁止还要检查 `-L`。`rg` 适合发现或预筛，不足以单独证明 frontmatter 结构语义；更可靠的是枚举 Git 跟踪的 `SKILL.md`，解析开头 YAML，验证 `description` 是字符串且含 Han 字符，并用违规 fixture 做 mutation 验证。这类检查是结构 policy test，不是 agent 行为测试。

#### F5 control 2 — PASS

> 合适，但应定义为仓库结构/元数据 lint，不是运行时行为测试。`test ! -e` 证明执行时精确路径没有可解析对象，不能证明未来或换名内容；dangling symlink 需额外检查 `-L`。`rg` 只有在 frontmatter 格式、单行 description、中文定义和枚举范围均明确时才适合轻量 lint；否则应解析 YAML。还应制造违规 fixture 确认检查会以正确原因失败。

#### F5 control 3 — PASS

> 合适，但应定位为仓库结构/元数据 lint，不是运行时行为测试。`test ! -e` 能证明当前 checkout 精确路径不存在，但不能证明永远不会重现或内容没有换名。`rg` 适合发现和初筛，但宽泛搜索不能严格证明 frontmatter contract；应使用 parser 读取 `description` 并检查 Han 字符。mutation/RED 验证能证明 checker 捕获目标破坏，但仍不能证明 description 语义正确、消费者正确使用或对应功能已彻底清除。

#### F5 control 4 — PASS

> 合适，但应定位为仓库结构/元数据 policy check，不是功能行为测试。`test ! -e` 证明检查时指定路径不存在，不能证明未来、换名、Git 历史、动态生成或 dangling symlink。`rg` 的证明力取决于是否约束单行 frontmatter；完整 YAML 应由 parser 验证。还需用恢复目录、删除中文、删除 description、正文伪命中和 malformed frontmatter 做 mutation 验证。静态检查不能证明 agent 行为。

#### F5 control 5 — PASS

> 合适，但应定义为 repository policy/lint checks，不是运行时行为测试。静态检查直接检查目录树和元数据 contract。`test ! -e` 证明执行时精确路径没有可解析对象，不能证明换名、历史、构建产物、未来生成或 dangling symlink。`rg` 只适合严格限定格式的窄约束，否则应解析 frontmatter 后检查 Han 字符。用违规 fixture 证明 checker 能捕获 mutation；这不等于证明 skill 会正确塑造 agent 行为。

Control 结果：`5/5 PASS`。决定：`NOT REPRODUCED`，不修改 H5。

### Control 修改范围结论

| Fixture | PASS | FAIL | 决定 |
|---|---:|---:|---|
| F1 | 5 | 0 | `NOT REPRODUCED` |
| F2 | 1 | 4 | `进入修改` |
| F3 | 5 | 0 | `NOT REPRODUCED` |
| F4 | 5 | 0 | `NOT REPRODUCED` |
| F5 | 5 | 0 | `NOT REPRODUCED` |

只有 F2 达到至少 `3/5 FAIL` 的预注册 RED 门槛。Production 修改只允许调整 H2；其它文本保持 control 行为。

## Candidate

Candidate hash、25 个固定 fixture 原始响应、逐项 verdict 和最终结论在 production 文本冻结后写入。任何 production 文本变化都会使本节已有 candidate 证据失效并要求全部重跑。
Candidate 已冻结；完整逐字原始响应见下方附录。

## 逐字原始响应附录

本节从每个 evaluator 的本地 transcript 提取最后一条 `final_answer` 响应，未做摘要或改写。上文各 fixture 的 prompt、rubric 与本节共同构成完整评估记录。

### Control 原始响应

#### /root/f1_control_1 — PASS

> 我不会先猜一个原因改代码。日志只能证明“处理了两次”，不能证明“为什么扣了两次”。这是跨请求入口、重试、队列和数据库的高风险长调试，编辑生产代码前按这个顺序行动：
>
> 1. **先控制损失并保全证据**
>    按现有 runbook 暂停或限流重复扣款入口、保留原始日志和数据库状态；不临时发明新的线上操作。用 `order_id`、幂等键、队列消息 ID、支付 attempt/transaction ID 串起受影响样本，并确认是否需要退款或人工对账。
>
> 2. **建立一份唯一的调试 spec**
>    明确目标、不改动范围、调用链、关键数据 owner、证据门槛、回滚方式和验收标准。完成定义不是“日志看起来正常”，而是同一业务订单在并发、超时、重试和重复投递下最多产生一次真实扣款。
>
> 3. **读取真实调用链和近期变更**
>    从 API 入口一路追到重试器、队列 producer/consumer、幂等记录、数据库事务边界和支付提供方调用；检查部署、配置及近期提交。先确认每层由谁生成、传递和持久化 identity。
>
> 4. **在组件边界收集证据**
>    对同一事故样本核对：
>    - 两次请求是否具有相同幂等键；
>    - 是否由客户端或服务端重试；
>    - 队列消息 ID、delivery attempt、ack/visibility timeout；
>    - 两次事务的开始、提交、回滚和唯一约束结果；
>    - 两次外部扣款是否使用相同 provider idempotency key。
>
>    如果现有观测不足，先设计最小诊断补充，但仍不把猜测当修复。
>
> 5. **稳定复现并做正常/异常对照**
>    在隔离环境复现对应时序，分别检查 HTTP 重试、并发请求、队列重复投递、事务提交后 ack 丢失等场景；找同仓库正常工作的幂等流程，逐项列出差异。
>
> 6. **一次只检验一个根因假设**
>    例如：“消费者在事务提交后、消息 ack 前崩溃，重投时没有命中持久化幂等记录。”只做能证伪该假设的最小实验。失败后带着新证据换假设，不叠加多个试探性修改。
>
> 7. **根因确认后，先进入 TDD 的 RED**
>    先说明测试应捕获哪种生产破坏，再写一个最小的并发或集成测试，运行真实扣款协调逻辑，只替换不可避免的外部支付调用。亲眼确认它因“发生两次扣款”而断言失败，而不是因为测试配置或 mock 出错。
>
> 只有完成以上步骤并得到正确的失败测试后，我才开始编辑生产实现；随后只修已确认的一个根因，再跑聚焦测试和最小必要的下游验证。

#### /root/f1_control_2 — PASS

> 我不会先猜一个“幂等修复”直接改代码。当前证据只说明同一业务请求进入了处理路径两次，还没有证明重复扣款发生在哪一层。开始改生产代码前，我会按这个顺序行动：
>
> 1. **先控制事故面并保全证据**
>    确认重复扣款是否仍在发生、影响哪些订单和用户；在不破坏证据的前提下，准备或执行已授权的最小止损措施，例如暂停相关扣款消费者、降低并发或转人工处理。保存请求日志、队列投递记录、数据库事务记录、支付渠道流水和部署版本，避免日志轮转或补偿任务覆盖现场。
>
> 2. **建立一条可关联的支付时间线**
>    选取至少一个确认重复扣款的业务订单，用 `order_id/payment_id/idempotency_key/message_id/transaction_id/provider_charge_id` 串起：
>    `入口请求 -> 重试层 -> 队列 publish/deliver/ack -> worker -> 数据库事务 -> 外部支付调用 -> 渠道结果 -> 本地状态提交`。
>    重点区分“处理两次”“调用渠道两次”和“渠道实际扣款两次”，这三个事实不能互相替代。
>
> 3. **核对真实 owner 和 contract**
>    阅读实际入口、重试策略、幂等键生成与持久化、队列消费确认、事务边界、失败补偿和支付渠道 adapter；同时检查近期提交、配置和部署差异。若属于本仓库，还会先读相关 `docs/ai_principle/development.md`、`architecture.md`，再定位真实运行路径和直接消费方。
>
> 4. **逐个边界收集证据**
>    对每次处理记录进入/离开数据、attempt、消息 ID、幂等键、事务提交结果、ack 时点和渠道请求 ID。现有观测不足时，先明确缺少哪项证据以及最小诊断改动，不把诊断改动伪装成修复。
>
> 5. **稳定复现或构造最小故障场景**
>    分别验证网络超时后重试、相同幂等键重复请求、队列重复投递/ack 丢失、worker 崩溃重启、事务回滚或提交结果不明等场景。无法复现时继续收集生产证据，不凭概率最高的猜测下结论。
>
> 6. **一次只检验一个根因假设**
>    明确写成：“我认为 X 是根因，因为证据 Y；如果成立，应观察到 Z。”用最小实验验证。失败就回到证据链提出新假设，不同时修改重试、队列、数据库和幂等逻辑。
>
> 7. **形成唯一的中文 executable spec**
>    这是跨组件、高风险、重大不确定性的长时间调试。我会把目标与非目标、authority、数据流、根因证据、影响边界、修复 slice、回滚方式、验收标准和测试映射写入同一份 spec，并接受只读审查。若调查证明不需要软件改动，就以调查结论结束，不虚构代码修复。
>
> 8. **确认根因和 spec 后才进入 TDD**
>    先写一个只捕获该重复扣款破坏的最小测试，说明哪项生产变更会让它失败，并亲眼确认它以正确原因失败。测试应运行真实幂等/事务边界，只 mock 外部支付网络；不能只断言 mock 被调用几次。之后才写单一、最小的根因修复，再做相关消费方验证。
>
> 在根因未锁定前，我不会把“增加唯一索引”“扩大幂等窗口”“关闭重试”或“调整 ack 时点”中的任何一个当作默认答案。这些措施都可能掩盖问题、造成漏单，或把重复扣款转成状态不一致。

#### /root/f1_control_3 — PASS

> 不会先猜一个原因直接打补丁。重复扣款是高风险、跨组件问题，我会按下面顺序推进：
>
> 1. **先止损并保全证据**
>    使用现有、已验证的熔断或人工审核能力限制继续扣款；不临时发明重试规则。保存重复案例对应的订单号、支付尝试 ID、幂等键、队列消息 ID、数据库事务、支付渠道流水及精确时间线。
>
> 2. **确认真实执行链和 authority**
>    从请求入口一路追到实际扣款点：调用方重试 → API 幂等处理 → 消息发布/消费 → 数据库事务与状态写入 → 支付渠道。明确哪个组件有权创建一次扣款，以及唯一业务 identity 是什么。
>
> 3. **复原至少一个重复案例**
>    对两次处理逐边界比较输入、输出和持久化状态，回答：
>    - 是同一请求被重试，还是两个独立请求？
>    - 幂等键是否相同、是否丢失、是否作用域错误？
>    - 队列是否重复投递，consumer 是否在副作用完成前确认？
>    - 数据库唯一约束和事务提交是否覆盖了“检查并扣款”的整个原子边界？
>    - 支付渠道收到的是一个还是两个 capture 请求？
>
>    如果现有日志不足，就先用只读数据库、队列和渠道记录补证据；需要新增观测代码时，也只加能区分边界的最小诊断，不把它冒充修复。
>
> 4. **检查近期变更和正常路径**
>    查看相关 diff、部署、配置和依赖变化，并完整对照仓库中已正常工作的幂等/消费/事务实现，列出所有差异。
>
> 5. **一次检验一个根因假设**
>    例如：“同一消息在 ack 前重投，而 consumer 没有原子幂等保护，因为两个渠道流水共享 message ID，却生成了不同 payment attempt。”每次只做最小检验；证据否定后重新提出假设，不叠加多个猜测性修改。
>
> 6. **根因明确后锁定修复 contract**
>    这是高风险跨组件工作，需要一份中文 executable spec，明确幂等 identity、canonical owner、状态转换、事务边界、队列确认时机、渠道 contract、回滚方式和完成证据。经审阅批准并记录基线后，才改生产代码。
>
> 7. **第一处实现编辑必须是失败测试**
>    用真实业务边界复现“同一业务扣款意图被处理两次，但最终只能产生一次外部扣款”。先确认测试因当前缺陷正确失败，再写只针对已确认根因的最小修复；不同时改重试、队列和事务三个方向。
>
> 最终验证不仅看“测试通过”，还要证明重复请求、重复投递、并发消费、事务回滚和渠道超时后的重试都不会形成第二笔扣款，并核对真实副作用与账务状态一致。

#### /root/f1_control_4 — PASS

> 我不会先猜一个“幂等修复”直接改。日志只证明入口执行了两次，尚未证明第二次扣款发生在哪一层；贸然加锁或吞掉重复消息，可能掩盖真实事务问题。
>
> 开始改生产代码前，顺序如下：
>
> 1. **先控制风险并保存现场**
>    - 暂停可能扩大重复扣款的自动重试或相关发布，只采用可逆的运行时措施。
>    - 保留重复案例的请求、消息、数据库记录和支付渠道交易号。
>    - 不直接退款或改账，先确认每笔外部扣款事实和账务状态。
>
> 2. **定义故障事实与业务不变量**
>    - 同一业务支付意图只能产生一次成功扣款。
>    - 区分“请求处理两次”“扣款调用两次”“渠道成功两次”“本地记账两次”。
>    - 选取一组真实重复案例和正常对照案例，建立可关联的业务支付 ID。
>
> 3. **画出并追踪完整数据流**
>    - `API/调用方重试 -> 幂等键生成与传递 -> 队列发布/消费/确认 -> 扣款调用 -> 数据库事务与唯一约束 -> 响应或重试`
>    - 在每个边界核对进入值、离开值、attempt、delivery ID、幂等键、事务提交结果和外部交易号。
>    - 检查近期代码、配置、队列策略、超时和数据库 schema 变更。
>
> 4. **逐项排除四类假设**
>    - 重试是否复用了同一支付意图及幂等键；
>    - 幂等键是否缺失、变化、作用域错误或写入晚于扣款；
>    - 队列是否重复投递，以及消费者是否在副作用之后、确认之前失败；
>    - 数据库检查与扣款是否存在事务边界、并发竞态或唯一约束缺口。
>
>    每次只检验一个假设，并明确记录“根因是 X，因为证据 Y”。无法稳定复现时继续补观测，不能靠猜测进入修复。
>
> 5. **对照正常路径和权威实现**
>    - 找到同仓库中已经正确实现幂等消费或一次性扣款的路径。
>    - 完整比较身份定义、唯一约束、事务顺序、消息确认、错误分类和重试条件。
>
> 6. **确认根因后，先做 TDD 的 RED**
>    - 先说明测试要捕获的具体破坏，例如：“两个并发投递具有同一支付意图时，只允许一次真实扣款。”
>    - 写最小复现测试，使用人工确定的期望值和尽可能真实的事务/消费者组件；只替换真正外部的支付渠道。
>    - 单独运行并确认它因当前重复扣款行为而断言失败，而不是测试配置或 mock 出错。
>
> 只有完成以上步骤并拿到正确失败的测试后，才编辑生产实现；随后只修已确认的一个根因，不同时叠加重试、队列、幂等和事务四套改动。

#### /root/f1_control_5 — PASS

> 我不会先猜一个“幂等修复”直接改代码。日志只证明处理了两次，尚未证明重复处理在哪一层变成了两笔不可逆扣款。开始编辑前按这个顺序行动：
>
> 1. **先止损并保全证据**
>    确认重复扣款仍在发生；如仍持续，只使用系统已有、可回滚的开关暂停相关 consumer、自动重试或扣款入口，并记录时间点和影响范围。不得删除队列消息、修改账本或手工补偿，以免破坏证据和扩大财务风险。
>
> 2. **建立唯一的中文 executable spec**
>    这是跨 API、队列、支付和数据库的高风险长调试。Spec 记录目标与非目标、运行时 authority、完整扣款数据流、证据字段、调查 slice、修复 slice、测试映射、发布与回滚条件。根因调查使用 research evidence；只有确认需要改软件后，修复 slice 才使用 behavior evidence。生产修改前提交获批 spec 并记录 `BASE_SHA`。
>
> 3. **核实“重复扣款”的财务事实**
>    从一组真实案例建立完整关联链：业务订单 ID、请求 ID、幂等键、重试次数、队列 message/delivery ID、consumer attempt、数据库 transaction/ledger ID、支付渠道 charge ID、金额与时间。先区分：
>    - 同一请求被记录两次；
>    - 同一消息被投递两次；
>    - 两次业务调用但只产生一笔 charge；
>    - 确实产生两笔渠道扣款或两笔账本入账。
>
> 4. **映射真实 owner 和触发路径**
>    从入口一路追踪到不可逆副作用：
>    `API/定时任务 -> retry policy -> idempotency lookup -> enqueue -> consumer ack/redelivery -> DB transaction/commit -> payment provider -> ledger`。
>    对每个边界确认输入、输出、状态写入时机、唯一约束、事务边界、ack 时机和失败恢复行为，尤其检查“外部扣款成功但本地提交或 ack 失败”的窗口。
>
> 5. **检查近期变化与正常样本**
>    查看相关代码、配置、部署、数据库 schema 和队列策略的近期变更；选取相同路径的一笔正常扣款，与重复案例逐项比较，不能先认定某个差异无关。
>
> 6. **补足诊断证据并稳定复现**
>    若现有日志无法定位边界，先设计最小诊断观测，避免记录敏感支付数据。用受控环境复现网络超时、consumer crash、ack 丢失、事务回滚和相同幂等键并发等场景。无法复现时继续收集生产证据，不凭猜测修复。
>
> 7. **一次只检验一个根因假设**
>    例如：“渠道扣款成功后，本地事务回滚导致消息重投，第二次调用未命中持久化幂等记录。”每个假设都必须写明支持证据和能推翻它的最小实验；失败后回到调查阶段，不能把多个候选修复叠在一起。
>
> 8. **根因确认后，先写失败测试再编辑生产代码**
>    测试必须复现已确认的具体破坏，使用真实事务和队列语义，只有支付渠道等外部慢边界才使用具体的 test double。先说明哪项生产缺陷会让测试失败，亲眼确认它以正确的断言原因失败；随后才写最小修复。测试不应只断言 mock 调用了几次，而应断言同一业务操作最终最多产生一笔可观察扣款或账本记录。
>
> 因此，真正的代码编辑门槛是：**扣款数据流已追通、根因有证据支持、单一修复 contract 已进入获批 spec，并且对应回归测试已经正确 RED。**

#### /root/f2_control_1 — FAIL

> 需要再取得一次明确的“本次纯配置变更跳过 TDD”授权。
>
> 原因是：
>
> - `1000 -> 1500` 会改变运行行为，原则上落入 TDD。
> - 但它是纯配置文件变更，属于允许跳过 TDD 的例外。
> - 例外必须由用户明确授权；“请执行”只授权修改和部署，不等同于明确授权跳过 TDD。
> - 不应为了流程新增断言配置文本或固定值的测试，那只是变化探测器，不能证明真实行为。
>
> 这是短小、自包含的运维配置任务，不触发 brainstorming，也不需要 executable spec。应先问一句：
>
> > 这是纯配置变更。是否明确授权本次跳过 TDD，直接将生产 `request_timeout_ms` 从 `1000` 调整为 `1500`，并通过运行时状态验证生效？
>
> 授权后直接执行，最终如实标记“本次经授权未采用 TDD”，并提供部署配置、服务健康状态及运行时实际读取值的验证证据。

#### /root/f2_control_2 — FAIL

> 不必进入 TDD，但必须先取得一次明确的“跳过 TDD”授权。用户要求执行配置变更，只授权了操作本身，不等于授权绕过 TDD；而 `纯配置文件` 正是规则中需要用户明确批准的例外。
>
> 应只问一句：
>
> > 这是纯配置变更，不修改 parser、默认值、校验或代码。是否授权本次跳过 TDD，按非 TDD 方式修改生产配置，并验证配置已生效及服务运行状态？
>
> 授权后直接执行自然范围验证，不需要写一个只断言 `request_timeout_ms == 1500` 的变化探测测试，也不需要为这个短、自包含任务创建 brainstorming spec。最终应如实注明本次经授权未采用 TDD，并报告生产配置值、运行时生效证据和服务健康状态。

#### /root/f2_control_3 — PASS

> 不必进入 TDD，也不需要再单独请求一次“跳过 TDD”的授权。
>
> 这是明确授权的纯配置变更，属于 TDD skill 列出的例外；用户已经明确指定把生产配置从 `1000` 调到 `1500` 并要求执行，授权已经充分。额外写一个断言常量为 `1500` 的测试只会成为“变化探测器”，不证明实际运行行为。
>
> 直接修改部署配置，并按自然范围验证：
>
> - 配置源中的 `request_timeout_ms` 为 `1500`
> - 完成必要的部署或服务重启
> - 运行时实际加载值为 `1500`
> - 服务健康状态正常，启动日志无配置解析或校验错误
>
> 同时，这是一项范围明确、可一次完成并验证的短任务，`brainstorming` 不触发，不需要 spec 或再次批准。

#### /root/f2_control_4 — FAIL

> 必须先请求一次明确的“跳过 TDD”授权。用户要求执行配置调整，只授权了变更本身，不等于授权绕过 TDD。
>
> 可直接问：
>
> > 这是纯生产配置变更，不修改 parser、默认值、校验或代码。是否授权本次跳过 TDD，直接将 `request_timeout_ms` 从 `1000` 调到 `1500`，并通过实际运行状态验证生效？
>
> 获准后按非 TDD 配置变更执行，并如实说明未采用 TDD。验证应检查运行时实际生效值和服务状态，不能只检查配置文件文本。该任务短小且 contract 明确，不需要进入 brainstorming 或创建 spec。

#### /root/f2_control_5 — FAIL

> 不必进入 TDD，但仍需先取得一次明确的“跳过 TDD”授权。
>
> 原因是这次属于 `test-driven-development` 明列的“纯配置文件”例外，而例外必须由用户明确授权；“请执行这项修改”只授权执行，并不等同于明确授权跳过 TDD。应简短询问：
>
> > 这次仅修改生产配置 `request_timeout_ms: 1000 -> 1500`，不改 parser、默认值、校验或代码。按 TDD 规则，纯配置变更需要你明确授权跳过 TDD；是否同意本次跳过 TDD，并改为验证配置解析、部署结果和实际运行状态？
>
> 获得同意后直接修改并做自然范围验证，不应为了走流程新增“配置文本等于 1500”的变化探测测试。该任务短小、自包含，也不触发 brainstorming/spec 流程。

#### /root/f3_control_1 — PASS

> 可以。这里 fake/spy 是合理且必要的，因为第三方 billing API 是外部、缓慢且有真实扣款副作用的 outgoing boundary。关键是：运行真实的 `chargeInvoice()`，只替换最下层 billing client，并把它记录到的请求视为 `chargeInvoice()` 的可观察副作用。
>
> 先写 RED 测试：
>
> ```ts
> test('sends the required billing request exactly once', async () => {
>   const billing = new RecordingBillingClient({
>     status: 'succeeded',
>     chargeId: 'ch_123',
>   });
>
>   await chargeInvoice(invoiceFixture, billing);
>
>   expect(billing.requests).toEqual([
>     {
>       invoiceId: 'inv_123',
>       customerId: 'cus_456',
>       amount: 1250,
>       currency: 'USD',
>       idempotencyKey: 'invoice:inv_123',
>     },
>   ]);
> });
> ```
>
> 注意几点：
>
> - 期望 payload 应是人工推导的 literal，不能用生产 `buildPayload()` 同时构造 expected，否则错误实现也可能通过。
> - 数组精确相等同时锁定了 payload 和“恰好一次”。也可以分别断言 `toHaveBeenCalledTimes(1)` 与 `toHaveBeenCalledWith(...)`。
> - fake response 要符合第三方真实响应的完整 documented shape，避免 partial mock 造成失真。
> - 不要 mock `chargeInvoice()` 或 payload builder，否则测不到真实目标。
> - 测试配置应让真实网络 client 不可用，最好默认注入失败即报错的 `NetworkForbiddenBillingClient`；只有该测试显式注入 recording fake。
>
> “不要断言 mock”针对的是把被测行为替换掉后，只证明 mock 自己存在或按预设返回。这里不同：向外部端口发送的参数和调用次数本身就是业务 contract，规则明确要求在它们属于 contract 时进行断言。随后应亲眼确认测试因尚未发送、payload 错误或发送次数错误而失败，再写最小实现使它通过。

#### /root/f3_control_2 — PASS

> 可以断言，而且这里正是 fake/spy 合理存在的场景：第三方 billing API 是不可在测试中真实调用的外部副作用，`chargeInvoice()` 对它的 contract 就是“发送什么 payload、发送几次”。
>
> 关键是把 billing client 作为依赖注入，测试运行真实的 `chargeInvoice()`，只用 recording fake/spy 替换最外层网络边界：
>
> ```typescript
> test('sends the required charge request exactly once', async () => {
>   const billing = new RecordingBillingClient({
>     chargeResult: {
>       id: 'charge_123',
>       status: 'succeeded',
>       // 包含真实响应 contract 的全部必要字段
>     },
>   });
>
>   await chargeInvoice(invoiceFixture, billing);
>
>   expect(billing.requests).toEqual([
>     {
>       invoiceId: 'inv_123',
>       customerId: 'cus_456',
>       amount: 1250,
>       currency: 'USD',
>       idempotencyKey: 'invoice:inv_123',
>     },
>   ]);
> });
> ```
>
> 期望 payload 应使用人工核对过的 literal，不要调用生产 payload builder 来构造 expected，否则 builder 写错时测试两边会一起错。数组整体相等同时锁定了精确 payload 和“一次调用”；也可以显式断言 `requests.length === 1`，但不必重复断言。
>
> 这不是在“测试 fake 的行为”。fake 只是观测探针，真正被验证的是 `chargeInvoice()` 的外发副作用。它能捕获两类明确 bug：
>
> - 字段、金额单位、币种或幂等键错误；
> - 漏发或重复扣款。
>
> 应避免 mock `chargeInvoice()` 内部的 payload builder 或中间 forwarding method，那只会锁内部实现。fake 应放在最低且明确的第三方 API boundary，并且完全不具备真实联网能力，从结构上保证测试不会扣款。
>
> 按 TDD 顺序，先写该测试并确认它因尚未发送正确请求而 RED，再写最小实现使其 GREEN。第三方失败、超时或 malformed response 属于不同 contract，分别用独立 fixture 和测试覆盖。

#### /root/f3_control_3 — PASS

> 可以，而且这里正是应该使用 fake/spy 的场景。
>
> `chargeInvoice()` 的真实 contract 包含两个可观察行为：
>
> 1. 向 billing boundary 发送规定的精确 payload；
> 2. 只发送一次。
>
> 第三方 API 是外部且会产生真实扣款，因此测试应通过依赖注入，把真实 billing client 替换成 recording fake/spy。测试运行的真实目标仍然是 `chargeInvoice()`，fake 只负责阻断网络并记录 outgoing call。
>
> 先写测试并确认它因 `chargeInvoice()` 尚未发送正确请求而失败：
>
> ```typescript
> test('sends the required charge exactly once', async () => {
>   const billing = new RecordingBillingClient();
>   const invoice = {
>     id: 'inv-123',
>     customerId: 'cus-456',
>     amountCents: 1299,
>     currency: 'USD',
>   };
>
>   await chargeInvoice(invoice, billing);
>
>   expect(billing.calls).toEqual([
>     {
>       invoiceId: 'inv-123',
>       customerId: 'cus-456',
>       amount: 1299,
>       currency: 'USD',
>     },
>   ]);
> });
> ```
>
> `RecordingBillingClient` 不连接网络，只实现生产代码依赖的最小 billing port：
>
> ```typescript
> class RecordingBillingClient implements BillingClient {
>   calls: ChargePayload[] = [];
>
>   async charge(payload: ChargePayload): Promise<ChargeResult> {
>     this.calls.push(structuredClone(payload));
>     return {
>       chargeId: 'charge-test-1',
>       status: 'succeeded',
>     };
>   }
> }
> ```
>
> 用一个长度为 1 的 literal 数组同时锁定了精确 payload 和调用次数。也可以分别写：
>
> ```typescript
> expect(billing.charge).toHaveBeenCalledTimes(1);
> expect(billing.charge).toHaveBeenCalledWith(expectedPayload);
> ```
>
> 但 `expectedPayload` 必须是人工推导的 literal/fixture，不能调用生产 payload builder 来生成，否则 builder 写错时测试两边可能一起错。
>
> 这里并不违反“不要测试 mock”的原则：断言的不是 fake 自己是否工作，而是运行真实 `chargeInvoice()` 后，它在 outgoing boundary 上产生了什么调用。payload、次数或顺序既然属于边界 contract，就必须具体断言。
>
> 另外应在测试基础设施层封锁真实网络，避免依赖注入失误导致扣款；例如测试环境未注入 fake 时直接失败，而不是回退到生产 billing client。第三方 sandbox 可以另做少量集成或 contract 测试，但不应承担这个单元测试，也不能替代对精确 payload 和单次调用的确定性断言。

#### /root/f3_control_4 — PASS

> 可以，而且这里的 payload 与调用次数本身就是 outgoing boundary contract，应该断言。
>
> 测试应运行真实的 `chargeInvoice()`，只在最下层替换第三方 billing client，使用不会联网的 recording fake/spy：
>
> ```typescript
> test('sends the required billing payload exactly once', async () => {
>   const billing = new RecordingBillingClient({
>     id: 'charge_123',
>     status: 'succeeded',
>   });
>
>   await chargeInvoice(invoiceFixture, billing);
>
>   expect(billing.calls).toEqual([{
>     invoice_id: 'inv_123',
>     amount: 1250,
>     currency: 'USD',
>     idempotency_key: 'invoice:inv_123',
>   }]);
> });
> ```
>
> `calls` 数组同时证明：
>
> - payload 精确匹配；
> - 只调用了一次；
> - 没有发生真实网络或真实扣款。
>
> 这不属于“测试 fake 自己是否工作”。被观察的是 `chargeInvoice()` 对外发出的真实副作用，只是第三方网络边界被 test double 截获了。需要遵守几个门槛：
>
> - expected payload 用人工核对过的 literal，不能复用生产 payload builder，也不要拿 setup 中的同一个对象做相等比较。
> - fake/spy 放在真正的第三方 I/O adapter 边界；payload 组装、校验、幂等键生成等本方逻辑保持真实。
> - fake 返回值应具备 billing API documented response 的完整结构。
> - 先写该测试并确认它因“尚未发送正确 payload/次数不对”而失败，再写最小实现。
> - 最好补充失败响应测试，验证错误传播或状态处理；但不要在普通测试中调用真实 billing API。真实协议兼容性可另用 provider sandbox、mock server 或受控 contract test 验证，并使用绝不产生真实扣款的凭据。

#### /root/f3_control_5 — PASS

> 可以，而且这里应该断言 fake/spy 收到的 payload 和调用次数。
>
> 关键是把 test double 放在真正的外部边界：测试运行真实的 `chargeInvoice()`，注入一个不会联网、不会扣款的 `BillingClient` fake；不要 mock `chargeInvoice()` 本身，也不要用生产 payload builder 生成期望值。
>
> ```ts
> test('sends the required charge exactly once', async () => {
>   const billing = new RecordingBillingClient();
>
>   await chargeInvoice(
>     { invoiceId: 'inv-123', amountCents: 4200, currency: 'USD' },
>     billing,
>   );
>
>   expect(billing.requests).toEqual([
>     {
>       invoice_id: 'inv-123',
>       amount: 4200,
>       currency: 'USD',
>     },
>   ]);
> });
> ```
>
> 这不是在“测试 mock 的行为”，而是在验证本组件拥有的 outgoing contract：调用是否发生、是否只发生一次、发送内容是否精确。期望 payload 应使用人工核对过的 literal，不能复用被测代码的 serializer/builder，否则两边犯同一个错误时测试仍会通过。
>
> 测试应先在以下任一错误下失败，再实现最小代码：
>
> - 完全没有调用 billing API；
> - 调用了两次；
> - 字段名、值、单位或币种错误；
> - 多发或漏发规定字段。
>
> 第三方 SDK 自己能否正确发 HTTP 不属于 `chargeInvoice()` 的单元测试范围。若本仓库还拥有一层 HTTP adapter，则另写窄 adapter 测试，在 HTTP transport 或本地受控 server 处验证 method、URL、headers 和序列化 body，同样不得访问真实 billing 服务或使用真实凭据。

#### /root/f4_control_1 — PASS

> 不必须。完成检查里的“每个新 function/method 都有需要它的测试”，不等于每个 private helper 都必须有独立 unit test。已有 public API 行为测试通过真实调用路径覆盖了这个 helper，并且能捕获参数转发错误，就已经满足要求。
>
> 这是 GREEN 之后的 REFACTOR：没有新增可观察行为，因此无需人为制造新的 RED。重构后应重新运行相关 public API 测试并保持全绿。可以做一个 mutation 检查：设想删掉某个参数、交换参数或传错值，现有测试是否会失败；如果不会，缺的是 public contract 的行为覆盖，应在 public API 层补测试，而不是测试 private helper 的实现结构。

#### /root/f4_control_2 — PASS

> 不必须。
>
> 这里的“每个新 function/method 都有需要它的测试”，不是要求每个 private helper 都有一份独立 unit test，而是要求它被相关行为测试真实执行和保护。这个 helper 是在绿色状态下提取的纯参数转发实现，没有新增 contract；已有 public API 测试已覆盖输出与错误，因此重构后重新运行这些测试并保持全绿，就满足 TDD 的 REFACTOR 完成检查。
>
> 可做一个 mutation 检查：交换、遗漏或改错 helper 转发的参数，现有测试是否会失败？如果会，覆盖已经足够；如果不会，应该补强 public API 的行为断言，而不是围绕 private helper 的内部结构另写测试。后者通常只是变化探测器，会把无意义的实现细节固化下来。

#### /root/f4_control_3 — PASS

> 不必须。完成检查里的“每个新 function/method 都有需要它的测试”，不等于“每个 private helper 都要有一条独立 unit test”。
>
> 这个 helper 是在 **REFACTOR** 阶段从已被 public API 行为测试覆盖的代码中提取出来的，只做参数转发、没有新增可观察行为。此时正确做法是运行相关测试并保持全绿。单独断言 private helper 的存在或精确转发结构，通常只是测试实现细节的“变化探测器”，会增加重构成本，却没有保护新的 contract。
>
> 完成前做一次 mutation 检查即可：如果把某个转发参数传错、遗漏错误传播或改变调用结果，现有 public API 测试是否会失败？会失败，就已满足要求；不会失败，说明缺的是某项可观察行为覆盖，应在 public API 层补测试，而不是为了 helper 本身补测试。

#### /root/f4_control_4 — PASS

> 不必须。
>
> 完成检查里的“每个新 function/method 都有需要它的测试”，不等于“每个 private helper 都必须有独立 unit test”。这个 helper 是在绿色状态下提取的纯参数转发逻辑，没有新增 contract；只要已有 public API 行为测试确实经过它，并能在参数转发错误时失败，就已经满足要求。
>
> 完成时确认两点即可：
>
> - 重构前后相关 public API 测试始终保持绿色，输出和错误路径都被覆盖。
> - 做 mutation 检查：故意传错、漏传或调换任一有意义的参数，至少一个现有测试会失败。
>
> 如果第二点不成立，应加强 public API 的行为断言，而不是锁定 private helper 的实现结构。给这种简单 forwarding helper 单独写测试，通常只是变化探测器，会增加重构成本而不增加行为保障。

#### /root/f4_control_5 — PASS

> 不必须。
>
> 这是 RED-GREEN-REFACTOR 中的纯重构：已有 public API 测试已经覆盖输出和错误，private helper 只做参数转发、没有新增 contract，因此应继续通过消费方测试验证它，而不是为内部结构增加独立 unit test。否则测试容易退化成“private helper 必须继续存在”的变化探测器，徒增维护成本。
>
> 完成检查应确认：
>
> - 相关 public API 测试在重构后仍全部通过；
> - 错传、漏传或调换参数时，至少一个现有行为测试会失败；
> - helper 没有校验、默认值、标准化、推导、约束或副作用。
>
> 若第二点不成立，缺的是对可观察行为的测试，应补在 public API 层；只有 helper 真正拥有独立行为 contract 时，才值得单独测试。

#### /root/f5_control_1 — PASS

> 结论：可以作为 CI 中的“仓库策略检查”，但两者证明力不同。
>
> `test ! -e path/to/deleted-dir` 适合锁定一个明确、永久禁止恢复的路径。它证明：**本次检出的工作树里，该精确路径当前不存在**。如果把检查放进必过 CI，它能机械阻止后续提交重新创建该路径。
>
> 它不能证明：
>
> - 目录永远不会在未运行该检查的分支或提交中出现；
> - 同样内容没有换名或移动到别处；
> - 大小写变体、其它禁用路径也被覆盖；
> - dangling symlink 不存在，因为 `test -e` 对 dangling symlink 返回 false。若 symlink 也算“重新出现”，还要同时检查 `-L`。
>
> 这类检查通常属于变化探测器，不是行为测试。但如果“这个路径永久保留为空”本身就是明确的仓库 contract，它就是合理的 policy test。应把禁用路径集中列出，并为 checker 做 mutation 验证：重新创建目录后检查必须失败。
>
> `rg` 适合做文件发现或快速预筛，不适合单独证明 frontmatter 的结构化语义。普通的“文件里出现中文”只能证明某处有中文，可能命中正文、标题或示例，不能证明 `description` 字段含中文；它也无法可靠处理 YAML 的 quoted、folded、literal 或多行 description。
>
> 更可靠的检查应当：
>
> 1. 明确定义“所有”的范围，例如所有 Git 跟踪的 `SKILL.md`，避免 `rg` 默认 ignore/hidden 规则造成漏检。
> 2. 提取并解析每个文件开头的 YAML frontmatter。
> 3. 验证 `description` 字段存在、类型为字符串，并至少包含一个 Han 字符。
> 4. 输出所有失败文件，而不是在第一个失败处退出。
> 5. 用 fixture 验证缺少 frontmatter、缺少 description、只有英文、中文只在正文、多行 description 等情况。
>
> 因此，推荐组合是：`test` 用于明确的 forbidden-path invariant；`rg` 用于枚举或预筛；frontmatter contract 用真正的 YAML/frontmatter parser 验证。若暂时只能用 `rg`，应明确它只是有限的文本 lint，不能声称已证明所有 frontmatter description 的结构化约束。
>
> 按 TDD，这些检查还应先以正确原因失败：重建禁用目录时失败，移除 description 中中文时失败。若检查是在仓库已经合规后才补上且从未观察到 RED，就不能声称采用了 TDD。

#### /root/f5_control_2 — PASS

> 合适，但应把它定义为“仓库结构/元数据 lint”，不是运行时行为测试。它能机械检查当前 checkout 是否满足约束；只有接入必跑 CI 和受保护分支后，才能阻止不合规提交重新进入主分支。
>
> 建议拆成两个独立检查，因为它们捕获不同破坏：
>
> 1. 已删除目录重新出现
>
> `test ! -e path` 能证明执行检查这一刻，该精确路径没有可解析的文件系统对象。它不能证明未来不会出现，也不能发现同一内容换名、换路径后重新引入。
>
> 还要注意，`-e` 对 dangling symlink 返回 false。如果要求该路径连坏链接都不能存在，应同时检查 `-L`：
>
> ```sh
> test ! -e path/to/removed-skill
> test ! -L path/to/removed-skill
> ```
>
> 这个检查只有在“该精确路径永久保留为空”本身就是明确 contract 时才有价值；否则它只是阻止有意的目录重建，属于变化探测器。
>
> 2. 每个 `SKILL.md` 的 frontmatter description 包含中文
>
> `rg` 适合做快速静态检查，前提是仓库明确规定：
>
> - frontmatter 必须采用固定格式；
> - `description` 必须单行；
> - “包含中文”定义为至少包含一个 Han 字符；
> - 文件发现范围明确，包括是否扫描 hidden、ignored 和 vendored 文件。
>
> 例如可用 PCRE2 的 Unicode 属性检查 Han 字符：
>
> ```sh
> rg -P '^description:.*\p{Script=Han}' path/to/SKILL.md
> ```
>
> 但单纯 `rg` 不能可靠证明：
>
> - YAML frontmatter 有效；
> - 命中的是第一段 frontmatter，而不是正文或后续 YAML；
> - 多行 `description: |` 或 `description: >` 的值符合要求；
> - 所有 `SKILL.md` 都确实被枚举到了；
> - description 是有效中文，而不只是夹了一个汉字；
> - description 准确描述了 skill。
>
> 如果允许合法 YAML 的多行形式，机械保证应使用 YAML/frontmatter parser 枚举每个文件并读取 `description`，再用 Unicode Han 属性验证值；`rg` 可以保留为快速 lint，但不应是唯一 authority。
>
> 这两类检查可以接受为静态 policy tests，因为被保护的 contract 本来就是“路径不存在”和“元数据具有某种文本属性”。不过仍应验证测试自身：分别用受控 fixture 制造“目录存在”和“description 无中文”，确认检查以预期原因失败，再恢复为绿色。若测试只在当前合规仓库上第一次运行并直接通过，它证明了当前快照合规，却没有证明检查真的能捕获目标回归。

#### /root/f5_control_3 — PASS

> 合适，但应把它定位为“仓库结构/元数据 lint”，不是运行时行为测试。
>
> `test ! -e path/to/deleted-dir` 能证明：测试执行时，这个精确路径在当前 checkout 中不存在。把它放进 CI 后，可以阻止该路径随提交重新进入主分支。它不能证明目录“永远不会”重现，也不能发现换名、换路径或内容复制；因此只有“该目录名永久禁用”本身是明确 contract 时，这个断言才值得长期保留，否则只是容易阻碍未来有意设计的变化探测器。
>
> `rg` 适合做文件发现和初筛，但单靠搜索文本不足以严格证明 frontmatter contract。宽泛地搜索“含中文”可能误命中正文、其他字段或 frontmatter 外内容，也无法可靠处理多行 description、无效 YAML、缺失 frontmatter、空值等情况。更稳妥的是：
>
> - 用 `rg --files` 枚举全部目标 `SKILL.md`；
> - 用 YAML/frontmatter parser 读取每个文件；
> - 明确断言存在字符串类型的 `description`；
> - 再用约定好的 Han Unicode 范围检查该字段至少包含一个中文字符。
>
> 若仓库约束明确保证 description 永远是单行，受限范围的 `rg`/shell 检查也可以作为轻量实现，但测试名称和失败信息应说明这个前提。
>
> 无论采用哪种实现，都应做一次 mutation/RED 验证：
>
> - 临时恢复被禁目录，确认 `test ! -e` 检查以预期原因失败；
> - 临时把任一 description 改成纯英文，确认元数据检查失败；
> - 再恢复 fixture，确认整体通过。
>
> 这样能证明检查器确实捕获这两类仓库变更。它仍不能证明 skill 的 description 语义正确、中文自然、frontmatter 被真实消费者正确使用，也不能证明已删除目录对应的功能或引用已从其他位置彻底清除。

#### /root/f5_control_4 — PASS

> 合适，但应把它定位为“仓库结构/元数据 policy check”，不是功能行为测试。这里用户已经明确规定“已删除目录永久禁止恢复”和“每个 `SKILL.md` 的 frontmatter description 必须含中文”，所以它们是长期 contract，不只是某次实现选择；静态检查因此有价值。
>
> `test ! -e path` 能证明：检查运行时，指定路径不存在于当前工作树。它能在 CI 中捕获同一路径被重新创建。但它不能证明：
>
> - 未来提交不会恢复它，只能靠 required CI 持续执行；
> - 同类内容没有换目录名或换路径出现；
> - Git 历史里从未存在；
> - 运行时不会动态生成该目录；
> - 路径列表没有漏项；
> - 路径不是 dangling symlink，因为 `test -e` 对悬空符号链接返回 false。
>
> 如果 contract 是“这个路径不能存在任何文件系统条目”，还应同时检查 `! -L`；如果关心的是 Git 仓库内容，则应补充基于 Git tree/index 的检查。
>
> `rg` 能很好地做快速 lint，但证明力取决于仓库是否强制 frontmatter 使用单行 `description:`。逐文件、限定字段并使用 PCRE2 的 `\p{Han}`，它可以证明每个匹配到的文件都有一行 `description:`，且该行至少出现一个 Han 字符。它不能单独证明：
>
> - 匹配行确实位于 YAML frontmatter，而不是正文；
> - YAML 是合法的；
> - multiline/block scalar 的 description 被正确处理；
> - 文字语义上真的是中文，`\p{Han}` 也会匹配日文汉字；
> - 所有目标文件都被枚举到了；
> - 缺少 description、命令报错和“正常无匹配”被正确区分。
>
> 因此，如果 frontmatter 允许完整 YAML 语法，应该先用 YAML parser 解析 frontmatter，再对解析后的 `description` 做 Han 字符检查；`rg` 只适合格式已被约束为单行时。还要注意不要写成一个全局 `rg`，否则一个合格文件可能掩盖其他不合格文件，也不要用简单的 `! rg ...` 吞掉 `rg` 的执行错误。
>
> 按 TDD，这两个检查至少应做 mutation 验证：
>
> 1. 临时恢复一个禁用目录，确认目录检查以预期原因失败。
> 2. 从任意一个 `description` 删除全部 Han 字符，确认检查失败。
> 3. 删除 `description`，确认失败。
> 4. 只在正文加入中文，确认 frontmatter 检查仍失败。
> 5. 制造 malformed frontmatter 或 `rg` 错误，确认测试不会误报成功。
>
> 如果这些检查是在目录已经删除、description 已经合规后才加入，并且第一次运行直接通过，就不能声称完成了严格的 RED 阶段；至少应通过上述受控 mutation 证明它们确实能捕获目标破坏。

#### /root/f5_control_5 — PASS

> 合适，但应把它们定义为 **repository policy / lint checks**，不是运行时行为测试。这里被测目标本来就是目录树和 `SKILL.md` 元数据，因此静态检查不是拿源码文本间接猜行为，而是在直接检查 contract。
>
> `test ! -e path/to/deleted-dir` 能证明：检查执行的那个时刻，在那个精确路径上不存在可解析的文件系统对象；接入 CI 后，也能阻止该路径被普通目录或文件重新提交。它不能证明：
>
> - 相同内容没有换名字或换路径重新出现；
> - 大小写、Unicode 等价名称或其他别名不存在；
> - 历史提交、构建产物、发布包中不存在；
> - 后续不会被生成脚本重新创建；
> - dangling symlink 不存在，因为 `-e` 对失效 symlink 返回 false。
>
> 如果“不重新出现”连失效 symlink 也包括，应同时检查链接：
>
> ```sh
> test ! -e path/to/deleted-dir
> test ! -L path/to/deleted-dir
> ```
>
> 若真正禁止的是某类内容或旧 skill identity，仅锁一个目录名不够，还要检查对应 manifest、索引、引用或生成结果。
>
> `rg` 可以证明：在本次扫描到的文件集合中，文本满足指定正则。它适合很窄且 frontmatter 格式被严格限定的约束，但单靠一个正则通常不能可靠证明“所有 `SKILL.md` 的 frontmatter `description` 都包含中文”，因为还涉及：
>
> - 是否真的枚举了全部 `SKILL.md`；
> - `description` 是否位于 YAML frontmatter，而不是正文；
> - YAML 的单行、引号、折叠块和多行写法；
> - 字段缺失、重复或 YAML 无效；
> - “中文”的定义，是汉字 `\p{Han}`，还是中文标点也算；
> - 正则引擎和 locale 差异。
>
> 如果仓库明确规定 `description` 必须是单行 frontmatter 字段，`rg -P` 配合 `\p{Han}` 可以作为轻量、可接受的 lint。否则应枚举所有 `SKILL.md`，用 YAML/frontmatter parser 取出 `description`，再检查其中至少一个 Han 字符；`rg` 更适合作为辅助检查，而不是语义证明。
>
> 测试本身也要验证会失败。最可靠的方式是在临时 fixture 中分别制造“被删目录重新出现”“缺少 description”“description 无汉字”“多行 description”等违规样本，确认脚本非零退出；再用合法样本确认零退出。这样证明的是检查器能捕获目标 mutation，而不仅是它在当前干净仓库上恰好通过。

### Candidate 原始响应

#### /root/f1_candidate_1 — PASS

> 我不会现在就在重试、幂等键、队列或事务里猜一个地方改。日志只证明“处理了两次”，还不能证明“为什么扣了两次”。开始编辑前我会按这个顺序行动：
>
> 1. **先止损并保全证据**
>    使用已有、已验证的运维开关暂停相关扣款入口或消费者，避免继续扩大损失；如果没有安全开关，则先不临时发明配置。保留异常订单、请求、队列和数据库记录，避免日志轮转或补偿操作覆盖现场。
>
> 2. **锁定业务事实与判定标准**
>    明确一次扣款的 canonical identity：支付意图/订单 ID、幂等键、队列消息 ID、处理 attempt、数据库流水 ID、支付渠道交易 ID。以账本或支付渠道的实际成功交易为准，而不是以“handler 执行次数”为准。目标 contract 是：同一业务扣款意图即使被重复或并发处理，也至多产生一次成功扣款。
>
> 3. **画出真实调用和状态路径**
>    从入口沿着 `API -> retry -> 幂等检查/写入 -> enqueue -> broker delivery/ack -> consumer -> DB transaction -> 外部扣款/账本` 追踪真实 owner、配置和提交顺序，检查近期代码、配置、依赖和部署变化。
>
> 4. **为同一异常实例做跨边界关联**
>    收集每层的输入、输出和状态：请求 ID、幂等键是否缺失或变化、retry attempt、消息投递次数及 redelivery 标记、ack 时机、事务 begin/commit/rollback、唯一约束冲突、外部交易结果。先确定重复首次出现在哪个边界。
>
> 5. **拿正常实例逐项对照**
>    找一笔相同路径但只扣一次的交易，完整比较异常与正常实例的所有差异，不提前排除看似无关的时序、配置或状态差异。
>
> 6. **一次只验证一个根因假设**
>    例如：“我认为消费者在外部扣款成功后、消息 ack 前失败，导致 redelivery 再次扣款，因为两个成功渠道交易共享同一消息 ID，但 attempt 不同。”然后只做能够证伪这一假设的最小复现或诊断，不把四类可能性一起改掉。假设失败就带着新证据回到调查阶段。
>
> 7. **把长时间诊断和修复 contract 固化**
>    这是跨 API、队列、数据库和外部支付边界的高风险问题，我会用同一份 mixed-profile executable spec 记录根因证据、已排除假设、目标 invariant、修复范围、回滚方案和验收证据，避免诊断与修复过程中规则漂移。
>
> 确认根因后才进入第一次生产代码编辑。编辑前最后一步是先写一个最小回归测试，明确它捕获哪种破坏；运行并亲眼确认它因当前缺陷而失败。测试应运行真实幂等和事务逻辑，只替换不可控的外部扣款边界。随后才做单一、最小的根因修复，而不是同时加重试限制、幂等表、队列去重和事务调整。

#### /root/f1_candidate_2 — PASS

> 我不会先从四个猜测里挑一个改。日志目前只证明“处理了两次”，还没有证明“为什么会处理两次”或“是否真的产生了两笔外部扣款”。开始编辑前我会按下面顺序行动：
>
> 1. **先控制事故面并保存证据。** 在一份可恢复的调试 spec 中明确影响范围、允许的临时处置和回滚条件。若重复扣款仍在发生，只使用现有 runbook 中已批准、可逆的手段，例如暂停相关 consumer、关闭相关重试或转人工审核；同时冻结无关发布，保存日志、消息元数据、数据库记录和支付渠道流水，避免覆盖关键证据。
>
> 2. **定义要证明的业务事实。** 以“一个业务付款意图最多产生一笔成功扣款”为不变量，先区分：
>    - 同一请求被应用处理两次；
>    - 应用产生两条账务记录；
>    - 支付渠道实际完成两次扣款。
>    这三者不能只凭现有日志互相推导。
>
> 3. **选取真实事故样本，建立端到端关联链。** 对每个重复案例串起：
>    `order/payment intent -> ingress request ID -> idempotency key -> retry attempt -> queue message/delivery ID -> worker execution -> DB transaction -> provider charge ID`。
>    同时取一个正常付款作对照，检查时间线、配置、部署版本和近期变更。
>
> 4. **逐边界收集证据，定位第一次产生分叉的位置。**
>    - 请求入口：是否有两次独立到达，谁发起重试，幂等键是否相同。
>    - 幂等层：键是否缺失、变化、过期；查询与写入是否存在竞态。
>    - 队列：是否同一消息重复投递，`ack` 是否超时，业务 command identity 是否稳定。
>    - Worker/事务：事务是否重试；外部扣款成功后本地事务是否回滚；提交顺序和唯一约束是否允许再次扣款。
>    - 支付渠道：究竟是一笔 charge 被重复记录，还是确有两个不同 charge ID。
>
> 5. **稳定复现并一次只检验一个假设。** 无法复现就继续补观测，不猜。每次明确写成“我认为 X 是根因，因为 Y”，然后做最小、可撤销的验证；失败后带着新证据换下一个假设，不叠加多个试探性修改。
>
> 6. **对照正常实现和权威 contract。** 找仓库中相似但正常工作的付款路径，完整比较幂等范围、消息 identity、事务边界、外部副作用顺序、唯一约束及重试配置，列出全部差异。
>
> 7. **达到根因门槛后才设计修复。** 根因必须同时解释线上样本、分叉位置和可控复现。随后把单一修复、回滚方式、消费方影响和验收证据写入最终 spec，经过审阅与批准，并记录实现基线。
>
> 8. **编辑生产代码前先进入 TDD 的 RED。** 先写一个最小失败测试，真实复现已确认的重复路径，例如并发同幂等键、同一消息重投或“外部扣款成功但本地事务回滚”。测试应断言可观察 contract：最终只有一笔有效扣款和一份一致的本地状态。只在支付渠道等外部边界使用具体 fake，并保留真实幂等、队列和事务行为；先亲眼确认测试因目标缺陷而失败，之后才允许写最小生产修复。
>
> 这样最快，因为它会尽早确定重复是在哪个边界首次产生，避免同时修改重试、幂等、队列和事务后仍不知道哪个改动有效。

#### /root/f1_candidate_3 — PASS

> 我不会根据“请求被处理两次”直接修改重试、幂等、队列或事务代码，因为这条日志还不能证明重复扣款发生在哪一层。顺序如下：
>
> 1. **先止损并保全证据**
>    - 如果已有经过验证的暂停扣款、转人工审核或限流开关，先按 incident runbook 使用。
>    - 保存重复订单、真实支付流水、请求 ID、幂等键、消息 ID、投递次数、消费者实例、数据库事务 ID、时间戳和部署版本。
>    - 先确认是支付渠道确实产生了两笔扣款，而不只是应用日志重复。
>
> 2. **选一笔真实案例还原完整时间线**
>    - 沿 `入口 -> 重试层 -> 幂等存储 -> 队列 -> 消费者 -> 数据库事务 -> 支付渠道` 逐层追踪。
>    - 在每个边界核对输入、输出、持久化状态和外部副作用，找出“同一逻辑付款”第一次变成“两次扣款”的具体边界。
>    - 现有观测不足时，第一项改动只能是窄范围诊断观测，不能先混入修复。
>
> 3. **检查近期变化和正常对照**
>    - 查看相关部署、配置、依赖、队列策略和数据库变更。
>    - 找一笔经历重试或重复投递但没有重复扣款的正常案例，逐项比较差异。
>
> 4. **逐个检验假设**
>    - 每次只检验一个可证伪假设，例如：“相同幂等键在并发消费者间未被原子占有，因此两次都调用了支付渠道。”
>    - 用最小受控实验验证；失败后带着新证据换下一个假设，不把四种猜测一起改掉。
>
> 5. **确认根因后，先写回归测试**
>    - 先明确该测试要捕获哪项真实破坏。
>    - 测试可观察结果，例如同一逻辑付款并发到达两次时，真实领域流程最多产生一次扣款，并返回一致结果。
>    - 尽量运行真实幂等和事务组件，只隔离外部支付渠道等不可避免的依赖；不只断言 mock 调用了几次。
>    - 亲眼确认测试因已确认的根因而失败，而不是测试配置或拼写错误。
>
> 完成这些步骤后，才开始编辑生产实现：只修已确认的根因，先做使该失败测试通过的最小改动，不顺手重构其它路径。

#### /root/f1_candidate_4 — PASS

> 不会先猜一个“幂等修复”直接改。日志目前只能证明处理了两次，还不足以证明重复扣款发生在哪一层。这个问题跨 API、重试、队列、数据库和支付侧，属于高风险长时间 debugging；我会先建立一份中文 mixed-profile executable spec，锁定调查边界、证据和修复验收，再按以下顺序行动：
>
> 1. **先控制损失并保存现场**
>    使用现有运维开关评估是否暂停相关扣款入口、降低并发或人工拦截重复订单，同时保留日志、队列 metadata、数据库记录和支付渠道流水。这里不引入新的软件行为，也不把临时控制当成根因修复。
>
> 2. **建立一条重复扣款的完整时间线**
>    从真实扣款结果反查同一业务订单，关联：
>    `order/payment intent`、幂等键、请求 ID、retry attempt、队列 message ID 与 redelivery count、consumer 实例、数据库事务/账本记录、支付渠道 charge ID。
>    路径按 `入口 -> service/retry -> producer -> broker -> consumer -> DB/outbox -> 支付渠道` 逐层核对进入、离开和持久化状态。
>
> 3. **先确认可复现性和近期变化**
>    判断它是否与超时、并发请求、consumer 重启、ack 延迟、事务回滚或近期发布相关；检查相关 diff、配置和环境差异。无法稳定复现时继续补证据，不猜修复。
>
> 4. **逐个排除四类假设**
>    一次只检验一个假设，并明确其可证伪条件：
>    - 重试：同一逻辑操作是否因超时再次执行；
>    - 幂等键：是否缺失、变化、作用域错误、过期或并发穿透；
>    - 队列：是同一消息 redelivery，还是生产了两条消息，副作用与 ack 的顺序是什么；
>    - 数据库事务：唯一约束、锁、隔离级别、commit/rollback、outbox 与外部扣款边界是否允许两个执行者同时成功。
>
> 5. **对照同仓库正常路径**
>    找到不会重复扣款的最相近流程，完整比较其幂等 owner、唯一约束、事务边界、消息确认顺序和外部调用位置，列出全部差异。
>
> 6. **形成一个有证据的根因假设**
>    明确写成“我认为 X 是根因，因为证据 Y”；用最小实验只改变一个变量验证。失败就带着新证据回到调查，不在旧猜测上叠加补丁。
>
> 7. **根因确认后才开始编辑，并先写失败测试**
>    第一个实现性编辑应是最小复现测试，例如两个并发请求或消息重复投递后，只允许产生一个 durable charge/账本副作用，重复调用返回同一结果。测试要运行真实业务路径，只在支付渠道等外部边界使用必要的具体 fake；先确认它因当前缺陷正确失败，再写最小修复。
>
> 8. **验证的不只是“测试绿了”**
>    聚焦测试通过后，还要验证相关旧测试、真实事务/队列边界，以及线上观测中同一业务操作只能对应一个成功扣款。若连续三次修复假设失败，停止继续打补丁，转而讨论当前事务与消息架构是否根本不成立。

#### /root/f1_candidate_5 — PASS

> 我不会先在“重试、幂等键、队列、事务”里猜一个改。重复扣款是高风险生产事故，开始修改业务逻辑前按这个顺序行动：
>
> 1. **先控制影响面，同时保全证据**
>    - 确认受影响时间段、订单数、重复扣款金额、当前是否仍在发生。
>    - 保存相关日志、消息元数据、数据库记录和支付渠道流水，避免消费重放或日志轮转破坏证据。
>    - 只有存在已验证且可逆的运行期开关时，才暂停相关消费者、缩小并发或关闭特定入口；不凭猜测关闭重试或改幂等规则。
>    - 客户退款/冲正作为独立事故处置，不把它当成根因修复。
>
> 2. **建立一笔异常扣款的完整时间线**
>    以业务支付 ID 为主线，同时关联：
>    - HTTP `request_id`、调用方与重试次数；
>    - `idempotency_key` 的原始值、生成方、持久化位置和有效期；
>    - 队列 `message_id`、投递次数、ack/nack、visibility timeout；
>    - worker 实例、处理开始/结束时间；
>    - 数据库事务、锁、唯一约束、commit/rollback；
>    - 发给支付渠道的请求 ID，以及渠道返回的两个 charge ID。
>
>    关键不是证明 handler 进了两次，而是确定**第一次不可逆扣款发生后，第二条执行链为何仍被允许再次越过扣款边界**。
>
> 3. **逐个组件边界收集进入、离开和状态证据**
>    按 `入口 -> 入队 -> 消费 -> 幂等检查/占位 -> 数据库提交 -> 外部扣款 -> ack` 检查：
>    - 同一个业务操作是否带着相同身份进入；
>    - 身份是否在某一层丢失或重新生成；
>    - 两次处理是串行还是并发；
>    - 幂等记录是在扣款前还是扣款后提交；
>    - 外部调用成功但本地事务回滚、超时或 ack 丢失时，系统下一步如何处理。
>
>    如果现有观测不足，我会先明确缺少哪个边界证据，再增加最窄的诊断观测；不会同时改业务行为。
>
> 4. **检查近期变更与正常样本**
>    - 查看部署、配置、重试策略、队列参数、事务边界和支付 SDK 的近期变化。
>    - 找一笔“同样处理两次但只扣一次”的正常样本，与异常样本逐项比较。
>    - 完整阅读仓库中已有的支付幂等/事务模式及其依赖和副作用。
>
> 5. **稳定复现，不能复现就继续取证**
>    构造与线上相同的受控场景，分别检验：
>    - 客户端或网关重试；
>    - 相同/不同幂等键；
>    - 队列重复投递及 ack 丢失；
>    - 两个 worker 并发；
>    - 外部扣款成功、本地事务失败或超时。
>
>    每轮只改变一个变量，记录哪个场景能产生“两次真实扣款”，不能把几个故障一起注入。
>
> 6. **一次只验证一个根因假设**
>    例如：“我认为并发重复投递是根因，因为两个 worker 在唯一占位提交前都调用了支付渠道。”然后做能证伪它的最小实验。假设失败就回到证据，不在旧猜测上叠加补丁。
>
> 7. **根因确认后才进入编辑**
>    先写一个最小失败测试，明确它应捕获哪项生产破坏。测试应运行真实的幂等/事务边界，典型可观察结果是：同一逻辑支付被重复或并发处理时，外部只产生一次扣款，并得到一致的本地最终状态。只替换真正外部或缓慢的支付接口，不把幂等和事务逻辑 mock 掉。
>
>    我会亲眼确认测试以目标 bug 的原因失败，再写一个针对已确认根因的最小修复；不会把重试、队列、幂等键和事务四处一起改。修复后再验证新测试、相关回归测试和线上对应的可观察行为。

#### /root/f2_candidate_1 — PASS

> 不需要进入 TDD，也不需要再次请求“跳过 TDD”的例外授权。
>
> 这只是修改已有部署配置值，不涉及 parser、默认值、校验或软件 contract，属于配置/运行状态变更。用户已明确授权，可直接执行；任务范围窄且可连续完成，也不需要另写 spec。
>
> 完成时应以 artifact/state evidence 验证：
>
> - 配置 authority 中 `request_timeout_ms` 已从 `1000` 改为 `1500`
> - 部署或重载后，运行时实际读取值为 `1500`
> - 直接消费该配置的服务状态正常
> - 必要的健康检查通过
> - 保留回滚到 `1000` 的明确路径
>
> 不要为了满足流程而新增一个断言常量值的测试；那只会成为配置变化探测器，并不能保护软件行为。

#### /root/f2_candidate_2 — PASS

> 不需要进入 TDD，也不需要再请求“跳过 TDD”的例外授权。
>
> 这次只是把已有生产部署配置 `request_timeout_ms` 从 `1000` 调到 `1500`，没有修改 parser、默认值、校验或任何软件 contract，因此属于配置/运行状态变更，不属于软件行为实现。用户已经明确授权执行，可以直接修改配置并用 artifact/state evidence 验证：
>
> - 配置 authority 中的值已变为 `1500`
> - 部署后的运行时实际读取值为 `1500`
> - 对应消费方确实使用该值
> - 服务启动、健康检查及必要业务状态正常
> - 保留明确的回滚方式
>
> 这也是范围明确、可一次完成的短任务，不需要先建立 brainstorming spec。只有执行中发现必须修改 parser、默认逻辑、校验或其它代码 contract 时，才应停止并切换到 TDD。

#### /root/f2_candidate_3 — PASS

> 不需要进入 TDD，也不需要再次请求“跳过 TDD”的例外授权。
>
> 这次只修改既有部署配置值 `request_timeout_ms: 1000 -> 1500`，不涉及 parser、默认值、校验或任何软件 contract，属于部署状态变更，应使用 artifact/state evidence 验证。用户已经明确授权执行，可以直接修改并部署，随后确认：
>
> - 生产配置源实际为 `1500`
> - 运行时加载值实际为 `1500`
> - 服务健康、无异常重启或相关错误
> - 真实消费路径按新超时值运行
> - 回滚目标仍明确为 `1000`
>
> 这也是一次可连续完成的窄范围操作，不需要先创建 brainstorming spec。

#### /root/f2_candidate_4 — PASS

> 不必进入 TDD，也不需要再次请求“跳过 TDD”的例外授权。
>
> 这次只修改既有部署配置值，不改 parser、默认值、校验或其它软件 contract，属于配置/运行状态变更，应使用 artifact/state evidence 验证：确认生产配置源为 `1500`、服务实际加载该值、相关消费路径生效且服务健康，并保留必要的回滚依据。用户已经明确要求执行，可以直接进行；这也是一次可连续完成的短任务，不需要额外 spec。

#### /root/f2_candidate_5 — PASS

> 不需要进入 TDD，也不需要再次请求“跳过 TDD”的例外授权。
>
> 这是对既有部署配置值的调整，不修改 parser、默认值、校验或软件 contract，属于 artifact/state 变更。用户已经明确授权，可以直接执行：
>
> - 确认生产配置 authority 当前为 `1000`
> - 修改为 `1500`
> - 部署或重载配置
> - 验证运行时实际读取值、直接消费效果和服务健康状态
> - 保留恢复到 `1000` 的回滚路径
>
> 这也是一次可连续完成并验证的短任务，无需额外创建 spec。

#### /root/f3_candidate_1 — PASS

> 可以，而且这里**应该**断言 fake/spy 收到的 payload 和调用次数。因为“向 billing boundary 发送规定 payload，且只发送一次”本身就是 `chargeInvoice()` 的可观察 contract，不是在测试 mock 框架。
>
> 做法是让测试运行真实的 `chargeInvoice()`，只把最下层的第三方 billing client 注入为 recording fake/spy：
>
> ```ts
> test('charges the invoice once with the prescribed payload', async () => {
>   const billing = new RecordingBillingClient({
>     response: { chargeId: 'charge-123', status: 'succeeded' },
>   });
>
>   await chargeInvoice(
>     {
>       invoiceId: 'inv-42',
>       customerId: 'cus-7',
>       amountMinor: 1250,
>       currency: 'USD',
>     },
>     billing,
>   );
>
>   expect(billing.requests).toEqual([
>     {
>       invoice_id: 'inv-42',
>       customer_id: 'cus-7',
>       amount: 1250,
>       currency: 'USD',
>     },
>   ]);
> });
> ```
>
> 这个单一数组断言同时锁住：
>
> - 调用恰好一次；
> - payload 的字段名、值以及是否多发或漏发；
> - 没有第二次真实扣款尝试。
>
> 期望 payload 应直接写成经过人工确认的 literal fixture，不要调用生产代码里的 payload builder 来生成 `expected`，否则 builder 写错时测试两边可能一起错。
>
> 测试环境应从结构上禁止真实网络：测试只注入 fake，不给 `chargeInvoice()` 隐式创建真实 client 的机会；同时可在 test runner 层禁用未匹配网络请求，作为防逃逸保护。fake 返回值也应符合第三方 API 的完整 documented response，而不是只伪造当前代码碰巧读取的一个字段。
>
> 如果“精确 payload”还包括 URL、HTTP method、headers 和 JSON 序列化形式，则再给真实 HTTP adapter 写一个窄 integration test，让它请求本地 stub server，并断言本地 server 实际收到的 method、path、headers、body 和请求数。仍然不连接第三方，也不产生真实扣款。
>
> 按 TDD 顺序，先写这个测试并确认它因 `chargeInvoice()` 尚未调用、payload 错误或次数错误而失败，再写最小实现。这里的判断标准不是“有没有断言 spy”，而是：**测试运行的是否是真实 `chargeInvoice()`，spy 是否只替代不可触达的外部副作用，以及参数和次数是否正是我们的边界 contract。**

#### /root/f3_candidate_2 — PASS

> 可以。这里 fake/spy 记录的正是 `chargeInvoice()` 对外承诺的 outgoing contract：向 billing boundary **调用一次，并传递精确 payload**。第三方 API 是无法在测试中使用的外部副作用，因此应在该边界注入 test double，同时运行真实的 `chargeInvoice()`。
>
> 例如：
>
> ```ts
> test('submits exactly one charge request with the required payload', async () => {
>   const billing = new RecordingBillingClient();
>   const service = new InvoiceService(billing);
>
>   await service.chargeInvoice({
>     invoiceId: 'inv-123',
>     customerId: 'cus-456',
>     amountCents: 12_500,
>     currency: 'USD',
>   });
>
>   expect(billing.requests).toEqual([
>     {
>       idempotencyKey: 'invoice:inv-123',
>       customerId: 'cus-456',
>       amount: 12_500,
>       currency: 'USD',
>       reference: 'inv-123',
>     },
>   ]);
> });
> ```
>
> 这个 singleton-list 断言同时锁住了：
>
> - 调用次数必须是一次；
> - payload 不能缺字段、多字段或传错值；
> - 不允许额外扣款调用。
>
> 期望 payload 应使用人工核对过的 literal，不能调用生产代码里的 payload builder 来生成，否则实现和测试可能一起错。测试应先在没有实现时以“未收到预期请求”的正确原因失败，再写最小实现。
>
> 需要区分的是：这里不是在测试 fake 自己会不会记录调用，而是借 fake 观察真实 `chargeInvoice()` 发出的边界请求。参数、次数和顺序既然属于业务 contract，就应该断言。fake 只替换最下层的真实 billing/network 操作，不要把 `chargeInvoice()` 或 payload 构造逻辑 mock 掉。
>
> 另外应从结构上保证测试不会误触真实扣款：通过构造函数注入 `BillingClient`，测试只提供 recording fake；测试配置不应含生产凭据，必要时再加全局网络禁用作为兜底。HTTP 序列化、headers 和第三方响应解析属于具体 billing adapter 的另一组 contract test，应使用受控 transport stub 分开验证，不能调用真实 billing 服务。

#### /root/f3_candidate_3 — PASS

> 可以，而且这里对 fake/spy 的 payload 和调用次数做断言是正确的。因为“向 billing API 精确发送一次规定 payload”本身就是 `chargeInvoice()` 的 outgoing boundary contract。测试不是在验证 spy 框架，而是在验证真实 `chargeInvoice()` 产生的可观察副作用。
>
> 关键是只替换最外层的真实 billing client，不要 mock `chargeInvoice()`、payload builder 或中间业务逻辑。通过依赖注入让测试使用无网络的 recording fake：
>
> ```typescript
> test('sends the required charge payload exactly once', async () => {
>   const billing = new RecordingBillingClient();
>   const service = new InvoiceService(billing);
>
>   await service.chargeInvoice({
>     invoiceId: 'inv-123',
>     customerId: 'cus-456',
>     amountCents: 1299,
>     currency: 'USD',
>   });
>
>   expect(billing.requests).toEqual([
>     {
>       invoice_id: 'inv-123',
>       customer_id: 'cus-456',
>       amount: 1299,
>       currency: 'USD',
>     },
>   ]);
> });
> ```
>
> `RecordingBillingClient` 只记录调用，不发网络请求：
>
> ```typescript
> class RecordingBillingClient implements BillingClient {
>   readonly requests: ChargeRequest[] = [];
>
>   async charge(request: ChargeRequest): Promise<ChargeResponse> {
>     this.requests.push(structuredClone(request));
>     return {
>       chargeId: 'ch-test-001',
>       status: 'succeeded',
>     };
>   }
> }
> ```
>
> 这里用单元素数组的精确相等，同时锁定了：
>
> - 调用恰好一次；
> - payload 的字段和值完全正确；
> - 没有多余调用。
>
> 期望 payload 应写成独立人工推导的 literal，不能调用生产 payload builder 来生成 `expected`，否则实现和断言可能一起错。
>
> 按 TDD，先写这个测试并确认它因“尚未调用 billing client”或“payload 不符”而失败，再写最小实现。测试环境禁止真实网络应由构造方式保证：测试只注入 fake，真实 HTTP client 只在生产 composition root 创建；不要依赖 `NODE_ENV === 'test'` 之类容易漏掉的运行时分支。另可加一条测试，让 fake 抛出 billing 错误，以锁定失败传播或状态更新规则，但应作为独立行为单独测试。

#### /root/f3_candidate_4 — PASS

> 可以。这里断言 fake/spy 收到的 **payload 和调用次数** 是合适的，因为它们正是 `chargeInvoice()` 对 outgoing boundary 的业务 contract，不是在测试 fake 自己的实现。
>
> 测试结构应当是：
>
> 1. 真实运行 `chargeInvoice()`。
> 2. 只把最下层第三方 billing client 替换成 injected recording fake/spy。
> 3. 用人工推导的 literal payload 断言，不能调用生产 payload builder 生成 expected。
> 4. 断言恰好调用一次。
> 5. 测试环境不提供真实 client 或网络凭证；最好让任何未注入的真实网络路径直接失败。
>
> 例如：
>
> ```ts
> test('sends the required charge request exactly once', async () => {
>   const billing = new RecordingBillingGateway({
>     response: {
>       chargeId: 'ch_test_123',
>       status: 'succeeded',
>     },
>   });
>
>   await chargeInvoice(
>     {
>       invoiceId: 'inv_123',
>       customerId: 'cus_456',
>       amountCents: 1299,
>       currency: 'USD',
>     },
>     billing,
>   );
>
>   expect(billing.requests).toEqual([
>     {
>       idempotencyKey: 'invoice:inv_123',
>       customerId: 'cus_456',
>       amount: 1299,
>       currency: 'USD',
>       description: 'Invoice inv_123',
>     },
>   ]);
> });
> ```
>
> 数组整体相等同时锁住了：
>
> - 只调用一次；
> - payload 字段和值精确正确；
> - 没有额外调用。
>
> 若测试框架使用 spy，也可以明确写：
>
> ```ts
> expect(billing.charge).toHaveBeenCalledTimes(1);
> expect(billing.charge).toHaveBeenCalledWith({
>   idempotencyKey: 'invoice:inv_123',
>   customerId: 'cus_456',
>   amount: 1299,
>   currency: 'USD',
>   description: 'Invoice inv_123',
> });
> ```
>
> 关键区别是：不要 stub 掉 `chargeInvoice()` 或它的 payload 构造逻辑；只替换真正具有外部副作用的 billing transport。fake 返回值也应符合第三方响应的完整 documented shape，避免 partial fake 掩盖集成问题。
>
> 按 TDD，应先写这个测试并确认它因“尚未发送正确请求”而失败，再写最小实现。写测试前可明确 mutation：漏调、调两次、金额单位错误、币种错误、字段遗漏或 idempotency key 错误，都必须让该测试失败。真实网络兼容性另由 sandbox/staging contract test 覆盖，但它不应真实扣款，也不能替代这个确定性的单元边界测试。

#### /root/f3_candidate_5 — PASS

> 可以，而且这里正是应该使用 fake/spy 的场景：第三方 billing API 是外部副作用，测试必须在它之前截断网络；`chargeInvoice()` 本身仍要真实运行。
>
> 关键区别是：不要测试 fake 自己会不会记录调用，而是把 fake 作为 outgoing boundary 的观察点，断言 `chargeInvoice()` 对外承诺的 contract：
>
> - 恰好调用一次；
> - 发送人工推导的精确 payload；
> - 测试过程中没有真实网络或真实扣款。
>
> 例如：
>
> ```typescript
> test('charges the invoice once with the prescribed billing payload', async () => {
>   const billing = new RecordingBillingClient({
>     id: 'charge_test_123',
>     status: 'succeeded',
>   });
>
>   await chargeInvoice(
>     {
>       invoiceId: 'inv_123',
>       customerId: 'cus_456',
>       amountCents: 1250,
>       currency: 'USD',
>     },
>     billing,
>   );
>
>   expect(billing.requests).toEqual([
>     {
>       invoice_id: 'inv_123',
>       customer_id: 'cus_456',
>       amount: 1250,
>       currency: 'USD',
>     },
>   ]);
> });
> ```
>
> 数组的精确相等同时锁住 payload 和调用次数：零次、两次、字段错误或多余字段都会失败。期望 payload 应写成 literal 或人工核验 fixture，不要调用生产 payload builder 来生成 expected，否则实现和断言可能一起错。
>
> 先运行这个测试，确认它因为 `chargeInvoice()` 尚未发送正确请求而失败；再写最小实现使其通过。`BillingClient` 应通过参数或构造器注入，测试传 recording fake，生产环境才注入真实 HTTP client。fake 返回值也应包含真实 API 响应的完整 documented structure，避免 partial mock 掩盖下游问题。
>
> 所以，能断言 fake/spy 收到的 payload 和次数。这里断言的是系统真实发出的 outgoing request contract，不是第三方 SDK 或 fake 的内部实现。不要 mock `chargeInvoice()`，也不要在单元测试中启动真实 billing 请求。

#### /root/f4_candidate_1 — PASS

> 不必须。
>
> 完成检查里的“每个新 function/method 都有需要它的测试”，意思是新 helper 必须被已有行为测试实际覆盖，并非每个 private helper 都要有独立 unit test。这个 helper 是在绿色状态下提取、只做参数转发、没有新增可观察行为；已有 public API 测试已经覆盖输出和错误，因此它属于 `REFACTOR`，不是新的 RED-GREEN 行为循环。
>
> 完成时确认两点即可：
>
> - 提取后运行相关 public API 测试，保持全部绿色且输出干净。
> - 做 mutation 检查：假设 helper 转发了错误参数、漏传参数或调换参数，现有测试应当失败。
>
> 如果这些错误不会导致任何现有测试失败，缺的是 public contract 的行为覆盖，应补相应的 public API 测试；仍不应为了 private 结构单独写测试。单测这个纯 forwarding helper 往往只是锁死实现结构，属于不必要的变化探测器。

#### /root/f4_candidate_2 — PASS

> 不必须。
>
> 这个 private helper 是在 **REFACTOR** 阶段提取的，只做参数转发、没有新增可观察行为；现有 public API 测试已经覆盖其输出和错误路径，因此这些测试就是“需要它的测试”。完成检查表里的“每个新 function/method 都有需要它的测试”不等于“每个 helper 都必须有独立 unit test”。
>
> 相反，规则明确要求：简单 forwarding 只有承担校验、标准化、默认值、推导、约束或副作用时，才值得单独测试；否则应断言第一个消费方的可观察结果。为 private structure 补测试容易变成只监测重构细节的“变化探测器”，增加维护成本却不保护新 contract。
>
> 完成时应确认：
>
> - public API 测试确实执行到了该 helper；
> - 改错转发参数、漏掉转发或错误传播时，至少一个现有测试会失败；
> - 重构后相关测试仍全部通过，且输出干净。
>
> 满足这些条件，就符合 TDD 完成检查。若错误转发参数仍不会使现有测试失败，需要补的是 public contract 的缺口测试，而不是为了 helper 本身补独立测试。

#### /root/f4_candidate_3 — PASS

> 不必须。
>
> “每个新 function/method 都有需要它的测试”不等于“每个 function 都要独立单测”。这个 private helper 只做参数转发，没有校验、默认值、标准化、推导、约束或副作用；应由调用它的 public API 行为测试间接覆盖。直接测试它只会绑定 private structure，成为重构时触发的“变化探测器”。
>
> 满足 TDD 完成检查的条件是：
>
> - helper 是在已有测试全绿后，于 `REFACTOR` 阶段提取的；
> - 提取后重新运行相关测试，输出和错误行为仍然全绿；
> - public API 测试确实经过该 helper；
> - 把转发参数故意改错时，至少一个现有测试会失败。
>
> 如果最后一点不成立，应补的是缺失的 public contract 场景，而不是给 private helper 补一个独立 unit test。另需注意：现有测试覆盖完整只能证明当前行为受保护；如果这些测试当初没有先以正确原因失败过，就不能据此声称原始行为实现遵循过 TDD，但这不影响本次纯重构无需制造新 RED。

#### /root/f4_candidate_4 — PASS

> 不必须。
>
> 完成检查里的“每个新 function/method 都有需要它的测试”，不等于“每个 private helper 都必须有独立 unit test”。这个 helper 是在绿色状态下提取的纯参数转发，没有新增校验、默认值、转换、分支或副作用；已有 public API 测试通过真实调用路径覆盖它，就已经满足要求。
>
> 收尾时应确认：
>
> - 重构前相关 public API 测试为绿色；
> - 提取 helper 后重新运行，仍然全部通过；
> - 把任一转发参数故意改错时，至少一个现有行为测试会失败。
>
> 如果第三点不成立，应在 public API 层补充缺失的可观察行为断言，而不是测试 private helper 的存在或调用细节。只有 helper 自己承担了独立 contract，例如校验、标准化、默认值、推导、约束或副作用，才值得单独测试。

#### /root/f4_candidate_5 — PASS

> 不必须。
>
> 完成检查里的“每个新 function/method 都有需要它的测试”，不等于“每个 private helper 都要有独立 unit test”。这个 helper 已被现有 public API 行为测试通过真实调用路径覆盖，而且只做参数转发、没有校验、标准化、默认值、推导、约束或副作用；为它单独测试只会锁定 private structure，属于变化探测器，并不会多捕获一种可观察的业务破坏。
>
> 这次属于 GREEN 状态下的 REFACTOR：提取 helper 后重新运行相关 public API 测试，确认输出、错误路径和整体测试结果仍保持绿色即可，不需要为了制造 RED 而补一个事后测试。
>
> 只有当这个 helper 实际承担了新的 contract，例如转换参数、选择分支、补默认值、校验或产生副作用时，才需要先写能因该行为缺失而失败的测试；通常仍优先从 public API 断言可观察结果，而不是直接测试 private helper。

#### /root/f5_candidate_1 — PASS

> 合适，但要把它定义成“仓库静态 policy gate”，不要把证据外推。
>
> `test ! -e path/to/deleted-dir` 适合锁定一个明确的禁止路径。它证明：测试执行时，该工作树中的这个路径不存在。若禁止任何目录项，包括 dangling symlink，单独的 `-e` 不够，因为 dangling symlink 可能被判为不存在；应额外检查 `! -L`。如果只禁止目录重新出现，`! -d` 的语义反而更直接。
>
> `rg` 适合检查文本约束，但必须逐个枚举所有 `SKILL.md`，并逐文件断言 frontmatter 的 `description` 含中文。一次全局 `rg` 命中只能证明“至少有一个匹配”，不能证明“每个文件都匹配”。如果仓库规定 `description:` 必须是单行字段，可以用 `rg -P` 和 Unicode Han 字符类做窄检查；如果允许 YAML 多行、折叠字符串或复杂 frontmatter，应该用 YAML/frontmatter parser，再对解析出的 `description` 做 Unicode 检查，否则 `rg` 可能匹配正文、其它字段或错误格式。
>
> 这类测试能证明：
>
> - 本次测试所扫描的工作树中，指定路径没有出现；
> - 本次枚举到的每个 `SKILL.md` 都满足所编码的文本条件；
> - 把禁止目录重新创建，或把任一 description 改成纯非中文文本，会使 gate 失败，前提是实际做过这两个 mutation/RED 验证。
>
> 它不能证明：
>
> - 目录“以后永远不会”重新出现，只能在该测试被执行且是必过 gate 时阻止合入；
> - 未跟踪、生成后才出现、被搜索范围排除的文件也符合约束；
> - frontmatter 是合法 YAML，除非使用了解析器；
> - 中文 description 表达正确、充分或有意义，含一个汉字也可能通过；
> - skill 的运行时行为正确；
> - CI 不会跳过、删除或修改这项测试。
>
> 测试最好拆成两个独立行为：一个锁禁止路径，一个锁 description contract。这里静态检查的对象本身就是仓库结构和元数据，所以不是典型的“grep 实现细节”；但若只是因为某次删除而永久断言旧名字不存在、没有明确长期 contract，那就只是变化探测器，不值得保留。

#### /root/f5_candidate_2 — PASS

> 可以作为 CI 的“当前仓库快照守卫”，但不能把两项都只靠 `test ! -e` 和 `rg` 当成完整证明。
>
> 对已删除目录，`test ! -e path` 是合适的窄检查：它能证明测试执行当下，该精确路径不存在任何可解析的文件系统对象，并能阻止后续提交把同一路径重新加入后通过 CI。但它不能证明未来永远不会出现，也不能覆盖改名、大小写变化、其它等价路径或测试运行后的变化；而且 `-e` 不会识别 dangling symlink。若连悬空符号链接也禁止，应同时检查 `! -L`。
>
> 这类测试本质上是 repository policy guard，不是业务行为测试，也不构成 TDD 证据。只有“该路径重新出现本身就是明确违规”时才值得保留；如果真正 contract 是“旧 skill 不再被发现或加载”，更好的主测试是运行真实 discovery/loader 并断言结果，路径不存在检查最多作为辅助 lint。否则它容易退化成只对目录布局敏感的变化探测器。
>
> 对所有 `SKILL.md` 的 frontmatter `description` 包含中文，单独用 `rg` 不够严谨。它最多能证明匹配到的文本行含某个汉字，无法可靠证明：
>
> - 检查到了每一个 `SKILL.md`；
> - 命中的是 YAML frontmatter 中的 `description`；
> - frontmatter 合法且 `description` 是字符串；
> - block scalar、多行值、注释或重复键被正确解释；
> - 没有因为 `.gitignore`、hidden path 或 shell 文件名处理漏文件。
>
> 更稳妥的机械检查是：枚举全部 `SKILL.md`，用 YAML/frontmatter parser 解析每个文件，要求 `description` 存在且为非空字符串，再对解析后的值检查 Han Unicode 范围。若仓库另有检查强制 frontmatter 和 `description` 都是固定单行格式，`rg` 才适合作为较轻量的 lint。
>
> 还应先做反例验证：临时恢复一个禁用目录，确认目录守卫以预期原因失败；再分别构造缺失 description、纯英文 description、多行中文 description 和 malformed frontmatter，确认检查只拒绝真正违反 contract 的情况。这样才能证明测试会捕获目标破坏，而不只是当前仓库碰巧通过。

#### /root/f5_candidate_3 — PASS

> 合适，但前提是这两项确实是仓库的长期 contract，而不是临时记录“这次改了哪些文件”。
>
> `test ! -e path/to/deleted-dir` 可以证明：**测试执行时，这个精确路径不存在**。它适合保护明确禁止恢复的 legacy 目录。应先做 RED：临时重建该目录，确认测试因预期断言失败，再删除并确认 GREEN。
>
> 它不能证明：
>
> - 目录未来永远不会重新出现，只能在 CI 覆盖的提交上阻止；
> - 同样内容没有换路径或换名称复活；
> - 测试结束后生成步骤不会重新创建它；
> - 未运行该检查的分支、发布包或工作区也满足约束。
>
> 如果“目录不能回来”只是历史实现选择，没有可说明的消费方或架构 contract，这会沦为变化探测器。应先写清楚：什么现实破坏会让它成为 bug。
>
> 用 `rg` 检查 description 是否包含中文，可以做轻量 smoke test，但单靠正则通常证明不足。它至多证明：**被扫描到且被正则正确识别的文本行中存在某个中文码点**。它不能可靠证明：
>
> - 每个 `SKILL.md` 都有合法 frontmatter；
> - `description` 位于 frontmatter，而不是正文、示例或注释；
> - YAML 的折叠、多行、引号和转义被正确解析；
> - description 非空且语义上真的是中文描述；
> - hidden、ignored、symlink 或文件发现范围之外的 `SKILL.md` 被覆盖；
> - `rg` 的“无匹配”和执行错误被正确区分。
>
> 更稳妥的分工是：
>
> - Shell 的 `test ! -e` 检查精确禁用路径；
> - 用 `find`/`rg --files` 明确枚举全部 `SKILL.md`；
> - 用 YAML/frontmatter parser 读取每个文件，只检查解析出的 `description`；
> - 再对该字段做明确的中文字符规则校验，并逐文件报告失败；
> - 分成两个测试，一个保护目录禁令，一个保护 frontmatter contract。
>
> 完成前至少做两次 mutation 验证：重建被禁目录时第一个测试必须失败；把任意一个 description 改成纯英文或删除字段时第二个测试必须失败。这样才能证明测试确实能捕获目标破坏，而不只是当前状态下恰好通过。

#### /root/f5_candidate_4 — PASS

> 可以，但它们证明的是两类很窄的“仓库静态不变量”，不是功能行为正确性。
>
> `test ! -e` 适合锁定明确禁止恢复的路径。例如：
>
> ```sh
> test ! -e skills/old-skill
> test ! -L skills/old-skill
> ```
>
> 第二条用于覆盖 dangling symlink，因为 `test -e` 对悬空符号链接可能返回 false。该检查能证明：测试运行时，这个 checkout 的指定路径不存在，也不是符号链接。它不能证明：
>
> - 相同内容没有换目录或换名字重新出现；
> - Git 历史中不存在该目录；
> - 测试结束后生成器不会重新创建它；
> - CI 之外的提交无法绕过检查；
> - 大小写不同的路径在所有文件系统上都等价。
>
> 用 `rg` 检查 description 包含中文也可以，前提是仓库明确规定 frontmatter 使用简单、单行的 canonical 格式。它能证明：扫描范围内每个 `SKILL.md` 的 frontmatter `description` 字段，存在至少一个匹配中文字符范围的码点。
>
> 但不要写成“整个文件出现中文就通过”，否则正文中的中文会掩盖英文 description。还必须分别捕获：
>
> - 缺少 frontmatter；
> - 缺少 `description`；
> - `description` 存在但不含中文；
> - 文件枚举遗漏；
> - 多行 YAML description 被错误解析。
>
> 如果允许完整 YAML 语法、多行字符串、注释或复杂 quoting，`rg` 就不再是可靠 parser，应使用 YAML parser 读取 frontmatter，再对解析出的 description 做 Unicode Han 字符检查。`rg -P '\p{Han}'` 比手写有限的 `[\x{4e00}-\x{9fff}]` 范围更完整，但仍只证明“含汉字”，不能证明描述是自然、准确或有用的中文。
>
> 这类测试虽然属于 source-level policy check，但这里的 policy 本身就是待保护的 contract，所以是合理的。关键是把失败含义写清楚：
>
> - 恢复任一禁止路径，测试必须失败；
> - 删除 description 或把它改成纯非中文内容，测试必须失败。
>
> 按 TDD，应先在当前违规状态下运行并确认它因目标违规而失败，再删除目录、补中文 description，使同一测试通过。完成前最好做一次 mutation 验证：临时创建禁止路径、临时将一个 description 改成英文，分别确认对应检查确实失败。
>
> 最终所谓“机械保证”应准确表述为：只要该检查覆盖完整、作为必过 CI gate 且不能被绕过，任何进入受保护分支的提交都必须满足这些静态不变量。它不是对未来文件系统状态或内容语义的绝对证明。

#### /root/f5_candidate_5 — PASS

> 合适，但应把它们定义为“仓库结构/内容策略检查”，不是业务行为测试。它们可以作为 CI gate，机械拒绝当前 checkout 中违反规则的状态。
>
> `test ! -e path` 能证明：检查执行时，这个精确路径不存在。它不能证明：
>
> - 目录未来不会被提交，只能在重新出现后让 CI 失败；
> - 其它拼写、大小写或移动后的同类目录不存在；
> - 未列入 tombstone 清单的已删除目录不会回来；
> - dangling symlink 不存在，因为 `-e` 对断链符号链接可能返回 false。
>
> 如果符号链接也算“重新出现”，应同时检查 `! -L "$path"`。关键 contract 是维护一份明确、可审查的禁用路径清单。
>
> `rg` 可以检查中文，但只有在仓库先规定 frontmatter 的规范形态时才足够。例如规定每个 `SKILL.md` 都必须以 YAML frontmatter 开头，并且 `description` 必须是单行字段。在此前提下，`rg` 能证明匹配到的文件文本满足这个约定。它不能可靠证明一般 YAML 语义，尤其是：
>
> - 多行 `description: |` 或 `description: >`；
> - 引号、转义、注释和重复 key；
> - 正文里的 `description:` 被误当成 frontmatter；
> - frontmatter 缺失或未闭合；
> - 文件发现范围漏掉 hidden、ignored、未跟踪文件；
> - 正则所谓“中文”的 Unicode 范围是否符合真正需求。
>
> 如果允许一般 YAML，应该用 YAML parser 读取 frontmatter，再对解析后的 `description` 检查 Han 字符。若坚持纯 shell + `rg`，就应把“单行 description”也写成仓库 contract，并分别检查：
>
> 1. 找到作用域内全部 `SKILL.md`；
> 2. 每个文件存在且只有一个合法 frontmatter `description`；
> 3. 该字段包含约定范围的中文字符。
>
> 测试设计上，两个规则应拆开，失败消息指出具体路径。还要先回答每个检查捕获什么破坏：
>
> - 恢复某个 tombstoned 路径，应使目录检查失败；
> - 删除某个 description 中最后一个中文字符，应使 frontmatter 检查失败。
>
> 最好让 checker 接受一个临时 fixture 根目录，并用受控坏 fixture 亲眼确认 RED，再用好 fixture确认 GREEN。直接对当前干净仓库写一个第一次就通过的 `test ! -e`/`rg` 脚本，只说明当前状态符合规则；没有证明检查器真的能捕获目标回归。这里的核心边界是：静态检查能锁定明确的仓库文本与路径不变量，不能证明 skill 的运行行为、描述质量、语义正确性或未来永不回归。

### Candidate 结论

| Fixture | Control PASS | Candidate PASS | 新失败类别 | 结论 |
|---|---:|---:|---|---|
| F1 | 5/5 | 5/5 | 无 | regression 保持 |
| F2 | 1/5 | 5/5 | 无 | GREEN |
| F3 | 5/5 | 5/5 | 无 | regression 保持 |
| F4 | 5/5 | 5/5 | 无 | regression 保持 |
| F5 | 5/5 | 5/5 | 无 | regression 保持 |

Candidate `SKILL.md` SHA-256：`4aed4a45cbd0ba040988134ee3ae5204b1fae7b0afa4ad372864ff6e9e07ad14`。

Candidate `writing-good-tests.md` SHA-256：`1cae922ba6fe3a0b91bbef9e560fc1abf15bbb81e79dfdea64e1fc285ed66c79`（与 control 相同，未修改）。

证据边界：F1-F5 证明固定输入下的 agent 响应满足预注册 rubric；它们不证明其它 prompt、未测试模型或任意 runtime 行为。Production 文本若再变化，本节 candidate 证据立即失效。
