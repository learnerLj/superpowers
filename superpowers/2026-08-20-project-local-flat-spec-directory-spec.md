# 项目本地 Superpowers Spec 平铺规范与历史迁移规格

> [!abstract] 目标
> 每个项目只使用项目根目录下的 `superpowers/` 保存 executable spec，所有 spec 直接平铺为 `superpowers/YYYY-MM-DD-<topic>-spec.md`。本轮先修改并验证 Superpowers 的 `brainstorming` skill，随后迁移 Superpowers 仓库和 Obsidian Vault 内的历史 spec、修复消费方，最后把 Superpowers 仓库的完整改进提交并推送到用户的 GitHub 远端。

## 1 目标与非目标

### 1.1 目标

1. `brainstorming` 在项目没有自定义 authority 时，把 spec 保存到 `<project-root>/superpowers/YYYY-MM-DD-<topic>-spec.md`。
2. `superpowers/` 内不再增加 `specs/`、`plans/`、日期目录或主题子目录；同一项目的 spec 平铺存放。
3. 明确定义项目根：普通仓库使用 repository/workspace root；Vault 中 `project/<project-name>/` 是该项目的根，嵌套的独立项目以其当前 spec 所在项目目录为根。
4. 现有项目 authority 显式指定其它位置时继续服从 authority，但不得仅因旧默认路径存在就把它当成自定义 authority。
5. Superpowers skill、静态 workflow contract、历史 spec 路径和真实消费方保持同步。
6. Vault 内所有真正以 `-spec.md` 结尾的项目 spec 就近迁入所属项目的 `superpowers/`，包括当前 CEX-DEX 可读性 spec。
7. Superpowers 仓库的改进经过 RED/GREEN、fresh-context control/candidate、全量相关测试、只读 review、task spec 基线提交、实现提交和 push。

### 1.2 非目标

1. 不把 `docs/superpowers/plans/`、`docs/plans/` 或 Vault 中普通项目主页、retrospective、design note 改名为 spec。
2. 不改 executable spec 的内容 contract、TDD 门槛、reviewer 权限或审批规则。
3. 不迁移 `area/`、`writing/`、Raw Reference 或项目外普通笔记。
4. 不提交或推送 Vault 仓库；只把 Superpowers Git 仓库改进推送到 `origin`。
5. 不创建第二份迁移账本、索引或兼容入口；本 spec 同时记录进度与证据。

## 2 当前状态与 Authority

### 2.1 Authority 优先级

1. 用户当前指令：项目目录下建立 `superpowers/`，spec 平铺；先改 skill，继续完成迁移并上传 GitHub，不等待逐步批准。
2. Superpowers `CLAUDE.md`、`skills/brainstorming/SKILL.md`、`skills/writing-skills/SKILL.md`。
3. Superpowers workflow tests，尤其 `tests/workflow/test-spec-to-tdd-consistency.sh` 与 `tests/workflow/run-tests.sh`。
4. Vault 根 `AGENTS.md`、`README.md`、Obsidian Markdown/写作规范。
5. 当前真实文件、Git 状态和入链消费方。

### 2.2 起点

- Superpowers `brainstorming` 当前默认写入 `docs/superpowers/specs/YYYY-MM-DD-<topic>-spec.md`。
- Superpowers 仓库当前为干净的 `main`，跟踪 `origin/main`，远端是 `https://github.com/learnerLj/superpowers.git`。
- `docs/superpowers/specs/` 当前有 19 份历史 spec/design artifact；`docs/superpowers/plans/` 与 `docs/plans/` 属于旧 plan，不在迁移范围。
- Vault 在 `2026-08-20` 当前工作树中有 11 份以 `-spec.md` 结尾的项目 spec；此前盘点的 12 份已因并发工作变化失效，迁移以这 11 份当前文件为固定集合。文件名包含 `retrospective` 但并非以 `-spec.md` 结尾的文章继续排除。
- Vault 与 Superpowers 都可能有指向旧路径的 Wikilink、Markdown path、测试 fixture 或说明文字；移动后必须逐个分类为现役引用、历史陈述或测试样例。
- 用户已明确授权直接执行、完成任务并上传 GitHub；本任务不等待逐 slice 批准。

### 2.3 项目根与目标路径

| 当前对象 | 项目根 | 目标目录 |
| :--- | :--- | :--- |
| 普通 Git/代码仓库 | repository/workspace root | `<root>/superpowers/` |
| Superpowers 仓库自身 | `/Users/mike/projects/superpowers` | `/Users/mike/projects/superpowers/superpowers/` |
| Vault 活项目 | `project/<project-name>/` | `project/<project-name>/superpowers/` |
| Vault 当前位于更深独立项目目录的 spec | spec 当前父目录 | `<current-parent>/superpowers/` |

目标文件名保留现有 basename；未来新 spec 使用 `YYYY-MM-DD-<topic>-spec.md`。迁移不得因补日期或改题名制造链接风险。

## 3 交付物与受保护状态

### 3.1 Superpowers 仓库

- 修改 `skills/brainstorming/SKILL.md`：新增项目根解析、唯一平铺位置、现有 spec 恢复和旧默认不构成 authority 的规则。
- 修改 `tests/workflow/test-spec-to-tdd-consistency.sh`：先以 RED contract 锁定新路径和禁止旧默认。
- 必要时修改直接消费旧默认路径的现役 skill/example；历史发布说明只在仍承担现役指令时更新。
- 把 `docs/superpowers/specs/*.md` 迁入根 `superpowers/`，并修复明确指向这些文件的路径。
- 保留 `docs/superpowers/plans/` 与 `docs/plans/`。
- 先单独提交本 task spec 形成 `FULL_BASE_SHA`，再产生一个只含本任务其余 Superpowers 改动的实现 commit，并把两者推送到 `origin/main`。

### 3.2 Vault

- 把当前固定集合中的 11 份 `*-spec.md` 移到各自项目的 `superpowers/`。
- 修复所有受影响 Wikilink、Markdown path、README 表格和 spec 内自引用。
- 当前 spec：
  `project/asset-opportunity-graph/cex-dex-basis-readable-rewrite-spec.md`
  迁移为：
  `project/asset-opportunity-graph/superpowers/cex-dex-basis-readable-rewrite-spec.md`。
- 不手动编辑自动生成的 `vault_structure.md`。

### 3.3 受保护状态

- Vault 中与本任务无关的 dirty/untracked 文件全部保护。
- Superpowers 仓库在任务开始时干净；若出现非本任务并发修改，停止对应 commit 并分类。
- 不删除历史 spec 内容；移动前后逐字节一致，除非精确路径自引用必须更新。
- 不改 `plans/`、Raw、外部仓库或用户未授权远端。

## 4 执行与数据流

```text
真实失败：当前 spec 落在 project/<name>/ 根和 docs/superpowers/specs/
-> RED 静态 contract 锁定 <project-root>/superpowers/*.md
-> 修改 brainstorming 最小路径规则
-> GREEN 静态测试 + fresh-context candidate
-> 迁移 Superpowers 历史 spec 并修明确消费方
-> workflow 全量测试 + 只读 review
-> commit/push Superpowers origin/main
-> 迁移 Vault 11 份项目 spec
-> 修 Wikilink/Markdown path
-> Vault 标题、链接、Manifest 和 Git 副作用验证
```

历史迁移使用结构化路径集合，不按正文关键字猜测。Vault 的迁移集合固定为 `2026-08-20` 恢复执行时 `find project -type f -name '*-spec.md'` 的 11 个结果；Superpowers 集合固定为任务开始时 `docs/superpowers/specs/*.md` 的 19 个结果。

## 5 验证合同

### 5.1 C0：迁移集合和基线可恢复

- **要证明的事实**：两端迁移前的路径、字节和 Git 状态可以定位。
- **Oracle**：记录 Superpowers `git status --short --branch`、19 个源路径与 SHA-256；记录 Vault 11 个源路径与 SHA-256、`git status --short`。
- **通过条件**：集合数量分别为 19 和 11；Superpowers 的 Git 基线可定位且任务外干净；每个文件有旧路径和 SHA-256；Vault staged path 为 0。
- **完成证据**：`2026-08-20`，Superpowers `HEAD` 与 `origin/main` 均为 `274adc5976c5bd571e43e4a27c6b8cf0a0ebaa92`，创建本 task spec 前工作树干净，当前仅有任务内未跟踪 `superpowers/`；19 个源文件均已记录旧路径和 SHA-256。Vault `HEAD=343b3956967a8c20b776295fe4b8166ab40f3769`，staged path 为 0；当前 11 个源文件均已记录旧路径和 SHA-256。完整集合如下：

```text
Superpowers 19:
19dd839168b9e4a072985e8941aa3ae7cf9101357111620755d50dbeb1bea04b  docs/superpowers/specs/2026-01-22-document-review-system-design.md
f351216f0b8abb5f08a9209d71ec3c218c79b1ba9d6a1c68aec990ef00e31a53  docs/superpowers/specs/2026-03-23-codex-app-compatibility-design.md
757ce61bbcd16dcb8f61fa69778ca7a3b1d26f7a11a0fcea3d302fd99a52ebae  docs/superpowers/specs/2026-04-06-worktree-rototill-design.md
7a3c5e5fb77a3f8a500e9406283653cfee5edf1b98e58d5f267c5f21905eee19  docs/superpowers/specs/2026-05-05-platform-neutral-config-refs-design.md
d55fa30a3b1422f8364a81f49c755ada9cc792b2cc10193b1dbd43c551918c19  docs/superpowers/specs/2026-05-05-platform-neutral-prose-design.md
63eb346415386c6850832f4b7414d03570a033eaf37de0b60d2ec4834169896e  docs/superpowers/specs/2026-05-05-platform-neutral-readme-design.md
fac3785f6f779bd899a6e93bcd60a934b4946ce4f7e8b6129d7910979650a6a1  docs/superpowers/specs/2026-05-06-lift-drill-into-evals-design.md
08b6b77be0d3b95e1d19a3dc320b93bba52917ca9beb0084fd74ecd75c015b59  docs/superpowers/specs/2026-06-09-sdd-task-scoped-review-dispatch-design.md
3a87b9e873728a3a4331437eb90f9fc5f4c9d7d0b88a931cce2bc3bda041b68b  docs/superpowers/specs/2026-06-10-positive-instruction-redesign-design.md
e8865d184479ffd4f2fe2c3072bf6a2b70179bbb4565cd6cefcbcb127c9f9b28  docs/superpowers/specs/2026-06-10-strict-cost-sdd-design.md
c4d2f3f086648ee6b949fd0ed999dd7b0a3a8d45ba290b2024389c66b2ed95b7  docs/superpowers/specs/2026-07-06-sdd-plan-scoped-workspace-eval-results.md
301328cb8dec833dc35e05e90b4c10a6e67ebd915b33a3a5d34f83927094815d  docs/superpowers/specs/2026-07-06-sdd-plan-scoped-workspace.md
9ed33fe2821fd9d61e198c03e0377a9151294737a6ea34074637c1eef98c1a06  docs/superpowers/specs/2026-07-15-sdd-fix-loop-redesign-design.md
48d6dc4985a00898c7b1c61a92f83af1c34c4323abf8ff3ff79518847a017c77  docs/superpowers/specs/2026-07-26-system-composition-and-implementation-slices-spec.md
74e38add056115742a2ba17818101c343f49153ba9abca479d128f73291c0960  docs/superpowers/specs/2026-08-06-all-skills-chinese-localization-spec.md
5ed687444226cb1bdbf6fe301b8abe0ff0eca76caa3b5d5ab4d4d7ea3714dfc2  docs/superpowers/specs/2026-08-06-general-long-task-execution-spec.md
da5673b541890aca6528ee560895ce15f6cbd38e975b67618935652353715827  docs/superpowers/specs/2026-08-06-skill-composition-consistency-spec.md
73e3448ee2a4411c4439276b1020107921f0c63bd5d8fe090f618e46836e628f  docs/superpowers/specs/2026-08-06-tdd-boundary-alignment-spec.md
a98b244c946580abeb57007e0c325bf8e37924edfa99f3ccfc57f4a946b951c1  docs/superpowers/specs/2026-08-13-long-task-review-convergence-spec.md

Vault 11:
f59d188913b87d5dfbbc01996f2dd11e52bea4576e8295610e1a70b64e0ee85c  project/arbitrum-cyclic-arbitrage-research/arbitrum-cyclic-arbitrage-research-spec.md
59f6aa55c07fba2f6a2ba57cb156519e96cbfd16bdeb00c066657680d0dc681a  project/asset-opportunity-graph/cex-dex-basis-readable-rewrite-spec.md
0b6fa7d2c27c979c7dd92c4ec93ad3a530de3cbbe00d5d55fb1ff68596ea4ac6  project/base-cyclic-arbitrage-research/base-cyclic-arbitrage-research-spec.md
2cd568a98e2b04b4ef15c7c8afc4775612a271930bbf81b9f516bea3422d83e4  project/blockchain-indexing-infrastructure-research/blockchain-indexing-infrastructure-research-spec.md
bada7fb2a341c1d202cc81378da744debb7bd562a4da4e2cfde4980c2c8065ef  project/bsc-mev-research/active-liquidity-management/bsc-active-lp-market-opportunity-spec.md
ff26fa616e31c237cda34ad09568054400f9d58f81340469b217890e498a9bdb  project/bsc-mev-research/bsc-cyclic-arbitrage-research-spec.md
9987e96a7083e3c2cf0ce822fb59a021f2a1d6dfb7927541b3c335aeb991789f  project/crypto-data/vault-crypto-data-skill-disk-spec.md
d2d1818a157672ec36315e764de3ee8324ebb38dce2e4f5e81361095414c7f81  project/ethereum-cyclic-arbitrage-research/ethereum-cyclic-arbitrage-research-spec.md
c17f739b3dd91709a5a52b08a3d8b1d321499d265c9e3df181d82206ecd9fb0d  project/monad-cyclic-arbitrage-research/monad-cyclic-arbitrage-research-spec.md
9b100e16941f9605d6804b6b1d57e5ab56a0f66a2c21672995438a6dbab767e4  project/polygon-cyclic-arbitrage-research/polygon-cyclic-arbitrage-research-spec.md
d7652a367408d1514890e48024c3c72d6630d7024e85bb756c68979f08785936  project/solana-mev-research/solana-smb-discord-evolution-analysis-spec.md
```
- **覆盖边界**：不恢复任务外并发变化。

### 5.2 C1：Skill 默认位置唯一且可执行

- **要证明的事实**：无项目自定义 authority 时，agent 能唯一解析到 `<project-root>/superpowers/YYYY-MM-DD-<topic>-spec.md`，不会再生成 `docs/superpowers/specs/` 或嵌套目录。
- **Oracle**：先新增并运行静态 RED contract；修改 skill 后重跑；检查旧默认路径从现役 contract 消失。
- **通过条件**：RED 在旧 skill 上失败；GREEN 后新路径、平铺、项目根和 authority override 四项均通过。
- **完成证据**：`2026-08-20`，先修改 `tests/workflow/test-spec-to-tdd-consistency.sh`，新增默认路径、项目根、平铺、authority override 和旧目录非 authority 五项 contract；第一次执行以 `exit 1` 失败，精确消息为 `project-local flat spec location contract is missing: 未指定时默认使用 <project-root>/superpowers/...`。随后只修改 `skills/brainstorming/SKILL.md` 的「Spec 完成后」四条路径规则，再执行同一命令以 `exit 0` 输出 `General long-task spec workflow consistency checks passed`。旧 skill SHA-256 为 `68401a0353f98217c6a8563cc2e4489f92d36503b1c0ad4a36e321785e5cdcb0`，首次 GREEN skill SHA-256 为 `265120afd0309f2dfe08fad36b49dc8079377cc1c321c29873ed5aee3be9592c`。Reviewer `IM-001` 触发第二轮 RED：精确旧路径映射 contract 首次以缺少 `` `docs/superpowers/specs/` 是已退役的旧默认目录 `` 失败；补入该映射后再次 GREEN。Closure 时 skill SHA-256 为 `94c45fa86011eec999809dd2b3f941aa64d3f961ab3af68545595d1751d2601f`，测试 SHA-256 为 `bf9ee20d09b0bcd3942bbc8ea3ecf125c4c0bf18885aa022a75f853f2a0d5d17`。
- **覆盖边界**：静态 contract 不证明模型在真实语境中采用规则。

### 5.3 C2：Fresh-context 行为采用新位置

- **要证明的事实**：面对「仓库没有 spec 位置 authority，请给长任务创建 spec」的同一场景，旧 skill/control 会采用旧位置或无法给出新 contract，新 skill/candidate 会选择项目根 `superpowers/` 并拒绝额外 `specs/` 层。
- **Oracle**：按 `writing-skills` 运行一对只读 fresh-context control/candidate，保留 prompt、skill source/hash、原始响应和判定。
- **通过条件**：control 暴露目标缺口；candidate 同时命中项目根、`superpowers/` 平铺、日期命名、authority override，不编辑任何文件。
- **完成证据**：`2026-08-20`，按 `writing-skills` 预算运行一对 `fork_turns=none` 的只读 evaluator。Control 读取 `git show HEAD:skills/brainstorming/SKILL.md`；candidate 读取当前工作树 skill。第一对的逐字场景 prompt 如下：

```text
当前目录是一个普通 Git 仓库 `/work/acme`，项目 authority 没有指定 executable spec 的保存位置。用户用中文要求：`请为这个跨多个阶段、需要恢复进度的长任务创建一份 executable spec；只告诉我你会把它保存到哪个精确路径，以及目录层级规则。如果旧版默认目录已经存在，也说明它是否构成项目自定义 authority。不要创建或修改任何文件。`
```

第一对原始回答如下：

```text
CONTROL
精确保存路径：
`/work/acme/docs/superpowers/specs/2026-08-20-multi-stage-long-task-spec.md`

目录层级规则：
- 固定使用 `docs/superpowers/specs/`。
- 不允许再在该目录下新增 `specs/`、`plans/`、日期目录或主题目录。
- 日期和主题只进入文件名，格式为 `YYYY-MM-DD-<topic>-spec.md`。

旧默认目录 `docs/superpowers/specs/` 即使已经存在，也不构成项目自定义 authority。只有用户直接指令或 `AGENTS.md`、`CLAUDE.md` 等项目 authority 明确指定保存位置，才能覆盖默认路径；目录单纯存在只说明默认结构已经落地。

依据是旧版 skill 的「Spec 完成后」段落：未指定时默认使用 `docs/superpowers/specs/YYYY-MM-DD-<topic>-spec.md`。

CANDIDATE
保存路径：`/work/acme/superpowers/2026-08-20-<topic>-spec.md`，其中 `<topic>` 替换为该长任务的主题标识；当前场景未提供具体主题，因此不能无依据虚构唯一文件名。

目录层级规则：spec 必须直接平铺在 `/work/acme/superpowers/` 下，不允许再新增 `specs/`、`plans/`、日期目录或主题目录。

旧版默认目录即使已经存在，或其中遗留了 spec，也不构成项目自定义 authority。只有项目 authority 明确指定其他位置时，才服从该位置。

依据是当前 skill 的「Spec 完成后」段落：默认使用 `<project-root>/superpowers/YYYY-MM-DD-<topic>-spec.md`；普通 Git 仓库或 workspace 使用 repository/workspace root；`superpowers/` 内直接平铺；旧默认目录不构成自定义 authority。
```

S2 reviewer 指出第一对 prompt 把现存目录预先称为「旧版默认目录」，不能证明 agent 能把具体的 `docs/superpowers/specs/` 映射到退役默认。这个已观察歧义会改变 skill 是否需要写出旧路径，因此将 evaluator 总预算从 2 次增加到 4 次，只追加一对受影响场景，不扩展其它维度。第二对共同使用的逐字场景 prompt 如下；control 读取 `git show 4bb0805:skills/brainstorming/SKILL.md`，candidate 读取加入精确旧路径映射后的当前 skill：

```text
当前目录是普通 Git 仓库 /work/acme。项目 authority 没有指定 executable spec 的保存位置。仓库中已经存在 /work/acme/docs/superpowers/specs/2026-07-01-legacy-task-spec.md，它拥有我现在要恢复的同一目标；仓库中没有其它 spec。请只告诉我：你会从哪个精确路径继续维护这份 spec，是否会先移动它，以及这个已存在目录是否构成项目自定义 authority。不要创建、修改或移动任何文件。
```

```text
CONTROL
1. 最终精确路径：`/work/acme/docs/superpowers/specs/2026-07-01-legacy-task-spec.md`
2. 是否先移动：否，直接在原文件继续维护。
3. 该目录是否构成项目自定义 authority：否。它只是 skill 在项目 authority 未指定位置时规定的默认目录；目录已经存在，不会因此升级为项目 authority。
4. 依据：「查找现有 spec：如果现有 spec 仍拥有同一目标，修改或恢复它」以及旧版「未指定时默认使用 `docs/superpowers/specs/YYYY-MM-DD-<topic>-spec.md`」。

CANDIDATE
1. 最终精确路径：`/work/acme/superpowers/2026-07-01-legacy-task-spec.md`
2. 是否先移动：是。先将现有 spec 从 `/work/acme/docs/superpowers/specs/2026-07-01-legacy-task-spec.md` 移入上述当前默认路径，再从同一份 spec 恢复维护。
3. `docs/superpowers/specs/` 是否构成项目自定义 authority：否。
4. 依据：当前默认为 `<project-root>/superpowers/YYYY-MM-DD-<topic>-spec.md`；`docs/superpowers/specs/` 是已退役的旧默认目录，它或其中遗留的 spec 不构成自定义 authority；同一目标的现有 spec 先迁入当前默认目录。
```
- **覆盖边界**：一对样本不证明所有模型和项目形状。

### 5.4 C3：Superpowers 历史 spec 迁移与引用闭合

- **要证明的事实**：19 份历史 artifact 全部位于根 `superpowers/`，旧目录不再拥有 spec 文件，内容和明确消费方有效。
- **Oracle**：迁移前后 basename 集合、SHA-256/必要路径 diff、`rg` 旧路径、workflow tests、Git rename 状态。
- **通过条件**：19 个 basename 一一对应；无丢失或冲突；现役引用不指向不存在路径；plans 保留。
- **完成证据**：`2026-08-20`，19 个 basename 全部位于仓库根 `superpowers/`，连同本 task spec 该目录共 20 个 Markdown 文件，且无二级文件；`docs/superpowers/specs/` 中 Markdown 数为 0。迁移后 19 份 source 的 SHA-256 与 C0 基线完全一致，随后只对 `2026-07-06-sdd-plan-scoped-workspace.md` 和 `2026-07-26-system-composition-and-implementation-slices-spec.md` 各更新一处迁移后的自引用。七份保留的历史 plan 及 `skills/requesting-code-review/SKILL.md` 中指向真实现存 artifact 的路径已改到 `superpowers/`。旧路径剩余命中已分类为 task spec 中的迁移前 provenance、`RELEASE-NOTES.md` 的历史发布事实、测试中必须不存在的 retired fixture、旧 plan 中已删除的临时 `eval-notes-red.md`，以及一份明确禁止重写历史 artifact 的历史说明。`docs/superpowers/plans/` 与 `docs/plans/` 均保留；聚焦 workflow、全量 workflow、writing-skills budget test 和 `git diff 4bb0805 --check` 均通过。一个 fresh-context 只读 reviewer 完成 full review，提出 `IM-001`、`IM-002` 两个 Important；主 agent 按 RED/GREEN 和事实证据修复后，原 reviewer 定点 closure 为两个 `CLOSED`，reviewer session 已结束。C3 与 S2 accepted。
- **覆盖边界**：历史发布说明中描述当时旧默认的文字可保留，并不构成现役入口。

#### 5.4.1 S2 Review Finding Ledger

| ID | Verdict | Criterion / Authority | RED 或事实证据 | Fix / Diff | Verification | Closure |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `IM-001` | `VERIFIED` | C1：旧默认不得继续拥有当前 spec | 原 skill 只写抽象的「旧默认目录」；新增精确静态 contract 首次运行以缺少 `` `docs/superpowers/specs/` 是已退役的旧默认目录 `` 失败 | `brainstorming` 显式映射退役路径；测试锁定该映射 | 聚焦测试 GREEN；第二对 control 原地维护旧路径，candidate 迁入根 `superpowers/` | `CLOSED`：原 reviewer 确认精确映射、静态 contract、非诱导 candidate 和 workflow tests 闭合 |
| `IM-002` | `VERIFIED` | C2 Oracle：保留 prompt、source/hash 和原始响应 | task spec 原来只有第一对 prompt 摘要，没有逐字文本 | C2 原位补入两对逐字 prompt、读取版本、原始响应与增加预算理由 | task spec 可独立复核 prompt 是否同场景、是否诱导 | `CLOSED`：原 reviewer 确认两对逐字 prompt、原始回答、读取版本和增样理由齐全 |

### 5.5 C4：Superpowers 改进通过 review、两次内聚 commit 与 GitHub push

- **要证明的事实**：task spec baseline 与通过审查的 skill、测试、历史迁移分别形成两个内聚 commit，并存在于 `origin/main`。
- **Oracle**：相关聚焦测试、`tests/workflow/run-tests.sh`、`git diff --check`、只读 code/spec review、`git status`、commit SHA、`git push origin main`、`git rev-parse origin/main`。
- **通过条件**：测试全绿；Critical/Important finding 关闭；两个 commit 都只含本任务，且实现 diff 以 task spec commit 为 `FULL_BASE_SHA`；push 成功；本地 HEAD 等于 `origin/main`。
- **完成证据**：`2026-08-20`，task spec baseline commit 为 `4bb08050aafeeaf9012fa150f6b5dc947f772b07`，只新增本 task spec；实现 commit 为 `9633b9b0942266098e4bfab1151ca1e8832297cb`，以 `4bb0805` 为 `FULL_BASE_SHA`，包含 `brainstorming` 路径 contract、静态测试、19 份历史 artifact 迁移及其明确消费方修复。`tests/workflow/test-spec-to-tdd-consistency.sh`、`tests/workflow/run-tests.sh`、`tests/writing-skills/test-evaluation-budget-contract.sh` 与 `git diff 4bb0805 --check` 在最终实现树上均通过。只读 reviewer 的 `IM-001`、`IM-002` 已由原 reviewer 定点关闭；最终 agent 状态显示 reviewer 与四个 evaluator 均已结束。实现 commit 已推送到 `origin/main`，Evidence update 前读回 `HEAD` 与 `origin/main` 均为 `9633b9b0942266098e4bfab1151ca1e8832297cb`。本次完成证据回填单独形成第三个 documentation-only commit；其最终 SHA 由提交后的远端读回提供，不改写前两个核心 commit 或实现内容。
- **覆盖边界**：不创建 upstream PR，不代表上游项目接受该个人 fork 约定。

### 5.6 C5：Vault 11 份项目 spec 完成就近平铺迁移

- **要证明的事实**：11 个旧路径均不存在，11 个 basename 均在对应项目的 `superpowers/`，内容除必要路径自引用外无损。
- **Oracle**：迁移映射、SHA-256/精确 diff、`find project -type f -name '*-spec.md'`、旧路径存在性检查。
- **通过条件**：11 对 11 一一映射；没有误迁 retrospective、项目主页或 plan；没有 basename 冲突。
- **完成证据**：`2026-08-20`，`find project -type f -name '*-spec.md'` 只返回 11 份文件，全部直接位于各自项目的 `superpowers/`，11 个固定旧路径逐项检查均不存在，且没有 basename 冲突。Base、Asset Opportunity Graph、BSC Active LP、BSC Cyclic、Ethereum、Monad、Polygon 七份当前 SHA-256 与 C0 基线逐字节一致。Arbitrum、Blockchain Indexing Infrastructure、Crypto Data、Solana SMB 四份只发生迁移所需的路径修复：Arbitrum 把移动后会误解析的 `[[README]]` 改为项目显式链接；Blockchain Indexing Infrastructure 与 Crypto Data 更新自身 spec 路径；Solana SMB 把两处移动后歧义的 `[[README]]` 改为项目显式链接。没有迁移 plan、retrospective、项目主页或 Raw。
- **覆盖边界**：只迁移当前 Vault 中以 `-spec.md` 结尾的文件。

### 5.7 C6：Vault 消费方和结构继续有效

- **要证明的事实**：移动后的 Wikilink、Markdown path、标题和 Manifest 均有效。
- **Oracle**：运行标题、Vault link、Topic Manifest validator；`rg` 旧路径；人工检查各项目 README 的 spec 入口。
- **通过条件**：标题 0 错误、Vault link 0 错误、Topic Manifest 0 新增错误；旧路径无现役引用。
- **完成证据**：`2026-08-20`，11 份迁移 spec 的标题校验输出为「检查 11 个路径」且通过；`validate_vault_links.py --root .` 索引并检查 1,591 个来源，0 错误；`validate_topic_manifests.py --vault-root .` 验证 251 个 Manifest，跳过 0；`validate_project_data_layout.py` 输出 `Validated current project evidence layout.`。排除自动生成的 `vault_structure.md` 后，11 个旧完整路径只剩 `project/person-canonical-readability-maintenance/person-canonical-readability-maintenance.md:150` 的历史 `git status` 记录，不承担现役入口。`vault_structure.md` 仍有 7 条提交前生成的旧 basename 路径缓存；根 `AGENTS.md` 禁止手改该文件，`.githooks/pre-commit` 会在未来 Vault commit 时运行 `scripts/generate_vault_index.py` 重建。由于本任务明确不提交 Vault，没有为了刷新该缓存制造跨并发资产的生成 diff；现役链接解析和三个结构 validator 均已通过。
- **覆盖边界**：不验证外部 URL 或项目业务结论。

### 5.8 C7：副作用受控

- **要证明的事实**：Superpowers 的 task spec 与实现两个 commit 只提交并推送本任务；Vault 只移动 spec 和修消费方，不覆盖既有 dirty 资产。
- **Oracle**：两端执行前后 `git status`、Superpowers staged/committed diff、Vault status 与目标路径映射。
- **通过条件**：Superpowers 两个 commit scope 精确；Vault staged path 为 0；任务外 dirty 文件未被本任务修改。
- **完成证据**：`2026-08-20`，Superpowers 的 baseline 与实现 commit 均只包含本任务；完成证据回填也只修改本 task spec。Vault `git diff --cached --name-only` 为空，`git diff --check` 通过；11 份迁移、直接消费方、registry 和 CEX-DEX 正文改写保持在未提交工作树中。`.agents/skills/telegram-information-retrieval/`、`area/self/`、`area/society/`、`project/person-canonical-readability-maintenance/` 及其它执行前或并发 dirty/untracked 资产未被 stage、commit、删除或覆盖。Vault 未 push，Superpowers 未创建 upstream PR。
- **覆盖边界**：并发任务产生的变化只记录，不归因。

## 6 执行 Slice

### 6.1 S0：冻结迁移基线

- [x] **结果**：19 份 Superpowers artifact 与 11 份 Vault spec 的路径、SHA-256 和 Git 起点已记录。
- **依赖**：无。
- **工作范围**：两个工作区只读盘点。
- **输入与 Authority**：§2 当前状态、C0。
- **交付物**：本 spec 的 C0 完成证据。
- **验收标准**：C0。
- **审查门槛**：无。

### 6.2 S1：用 TDD 改进 Brainstorming 路径 Contract

- [x] **结果**：静态测试先证明旧默认不符合新规范，再由最小 skill 修改使测试通过。
- **依赖**：S0。
- **工作范围**：`skills/brainstorming/SKILL.md`、`tests/workflow/test-spec-to-tdd-consistency.sh`。
- **输入与 Authority**：用户路径规范、writing-skills、C1。
- **交付物**：RED/GREEN 测试证据与新路径 contract。
- **验收标准**：C1。
- **审查门槛**：无。

### 6.3 S2：验证 Skill 行为并迁移 Superpowers 历史 Spec

- [x] **结果**：fresh-context candidate 采用新位置；19 份历史 artifact 和明确消费方迁入根 `superpowers/`。
- **依赖**：S1。
- **工作范围**：C2/C3 的 evaluator、`docs/superpowers/specs/`、根 `superpowers/`、直接引用。
- **输入与 Authority**：迁移基线、新 skill、历史文档。
- **交付物**：行为评测证据、19 份迁移文件、引用修复。
- **验收标准**：C2、C3。
- **审查门槛**：一个只读 reviewer 检查 skill contract、测试、迁移集合和引用边界。

### 6.4 S3：提交并推送 Superpowers

- [x] **结果**：task spec baseline 与完整实现以两个内聚 commit 存在于 `origin/main`。
- **依赖**：S2。
- **工作范围**：Superpowers 仓库本任务 diff。
- **输入与 Authority**：C4、用户 push 授权。
- **交付物**：`FULL_BASE_SHA`、实现 commit SHA 和远端状态。
- **验收标准**：C4。
- **审查门槛**：S2 reviewer 的 Critical/Important finding 已关闭。

### 6.5 S4：迁移 Vault 历史 Spec 并修消费方

- [x] **结果**：11 份 Vault spec 在所属项目 `superpowers/` 平铺，旧路径与失效引用清零。
- **依赖**：S3。
- **工作范围**：固定 11 份 spec 及直接消费方。
- **输入与 Authority**：C5/C6、Vault AGENTS/README。
- **交付物**：迁移后的 Vault 文件与链接修复。
- **验收标准**：C5、C6。
- **审查门槛**：无；机械迁移由 validator 和逐项映射闭合。

### 6.6 S5：最终验收

- [x] **结果**：两个工作区都满足新规范，Superpowers 已推送，Vault 无结构或链接回归。
- **依赖**：S4。
- **工作范围**：C0-C7、review closure、两个 Git 状态。
- **输入与 Authority**：最终工作树和远端状态。
- **交付物**：本 spec 完成证据与最终交接。
- **验收标准**：C0-C7。
- **审查门槛**：完成前调用 `verification-before-completion`。

## 7 回滚、恢复与修订条件

### 7.1 恢复信息

- **当前停点**：S0-S5 已 accepted；两个 Important finding 已由原 reviewer 关闭，Superpowers 核心提交已推送，Vault 迁移与最终 validator 已通过。
- **下一个阶段**：无；只需提交并远端读回本次 documentation-only Evidence update。
- **实现与推送授权**：用户已明确要求直接执行完并上传 GitHub。
- **治理恢复**：恢复执行时发现原 spec 的“单一 commit”与 `brainstorming` 的 behavior-work baseline 门槛冲突；改为 task spec baseline + 实现 commit。生产文件已开始修改，因此该 baseline 晚于首次 RED/GREEN，但它仍真实隔离后续完整实现 diff；最终证据必须如实保留这个边界，不能把它描述成修改前基线。

### 7.2 回滚

- Superpowers 在 commit 前使用 Git rename/diff 恢复；commit 后保留 commit SHA，不使用 destructive reset。
- Vault 移动前记录旧路径和 SHA-256；回滚时逐项移回对应旧路径并重新跑链接校验。
- 任何 basename 冲突、项目归属不清或 authority 冲突都停止受影响文件，不猜测覆盖。

### 7.3 语义修订条件

1. 用户要求 `docs/superpowers/` 而非项目根 `superpowers/`；
2. 某项目 authority 显式要求另一 SSOT；
3. 历史文件同时属于两个项目或发生 basename 冲突；
4. 必须迁移 plan、普通 design note、Raw 或项目主页；
5. GitHub push 目标不是当前 `origin/main`；
6. 迁移会覆盖并发修改。

## 8 最终验收

完成前必须使用新鲜证据证明：

1. C0-C7 全部有完成证据，S0-S5 均 accepted。
2. `brainstorming` 的唯一默认是项目根 `superpowers/YYYY-MM-DD-<topic>-spec.md`，并保留 authority override。
3. RED/GREEN 与 fresh-context control/candidate 都能定位。
4. Superpowers 19 份历史 artifact 和 Vault 11 份 spec 一一迁移，无误删、冲突或内容丢失。
5. 两端旧现役路径引用清零；历史陈述若保留，明确不承担现役指令。
6. Superpowers workflow tests、diff check、review、task spec baseline commit、实现 commit、push 和远端 SHA 全部通过。
7. Vault 标题、链接、Manifest 和 staged 状态通过。
8. reviewer session 已结束，Superpowers 与 Vault 的任务外状态均被保护。
