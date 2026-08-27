#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

fail() {
    echo "FAIL: $*" >&2
    exit 1
}

assert_contains() {
    local file="$1"
    local pattern="$2"
    local label="$3"

    rg -q "$pattern" "$REPO_ROOT/$file" || fail "$label ($file)"
}

assert_absent() {
    local pattern="$1"
    shift

    if rg -n -i "$pattern" "$@"; then
        fail "forbidden active-workflow reference: $pattern"
    fi
}

for removed_skill in \
    dispatching-parallel-agents \
    executing-plans \
    finishing-a-development-branch \
    subagent-driven-development \
    using-superpowers \
    using-git-worktrees \
    writing-plans; do
    [[ ! -e "$REPO_ROOT/skills/$removed_skill" ]] ||
        fail "removed development workflow still exists: skills/$removed_skill"
done

active_surfaces=(
    "$REPO_ROOT/CLAUDE.md"
    "$REPO_ROOT/README.md"
    "$REPO_ROOT/.github/PULL_REQUEST_TEMPLATE.md"
    "$REPO_ROOT/.github/ISSUE_TEMPLATE/bug_report.md"
    "$REPO_ROOT/.github/ISSUE_TEMPLATE/feature_request.md"
    "$REPO_ROOT/docs/testing.md"
    "$REPO_ROOT/skills"
)

unsupported_distribution_surfaces=(
    "$REPO_ROOT/.agents"
    "$REPO_ROOT/.claude-plugin"
    "$REPO_ROOT/.codex-plugin"
    "$REPO_ROOT/.cursor-plugin"
    "$REPO_ROOT/.kimi-plugin"
    "$REPO_ROOT/.opencode"
    "$REPO_ROOT/.pi"
    "$REPO_ROOT/assets"
    "$REPO_ROOT/hooks"
    "$REPO_ROOT/tests/explicit-skill-requests"
    "$REPO_ROOT/docs/README.kimi.md"
    "$REPO_ROOT/docs/README.opencode.md"
    "$REPO_ROOT/docs/porting-to-a-new-harness.md"
    "$REPO_ROOT/GEMINI.md"
    "$REPO_ROOT/gemini-extension.json"
    "$REPO_ROOT/package.json"
    "$REPO_ROOT/.version-bump.json"
    "$REPO_ROOT/scripts/bump-version.sh"
    "$REPO_ROOT/scripts/package-codex-plugin.sh"
    "$REPO_ROOT/scripts/sync-to-codex-plugin.sh"
    "$REPO_ROOT/skills/using-superpowers"
    "$REPO_ROOT/skills/brainstorming/visual-companion.md"
    "$REPO_ROOT/skills/brainstorming/scripts"
    "$REPO_ROOT/tests/brainstorm-server"
    "$REPO_ROOT/VERSION"
    "$REPO_ROOT/docs/plans/2026-01-17-visual-brainstorming.md"
    "$REPO_ROOT/docs/superpowers/plans/2026-02-19-visual-brainstorming-refactor.md"
    "$REPO_ROOT/docs/superpowers/plans/2026-03-11-zero-dep-brainstorm-server.md"
    "$REPO_ROOT/docs/superpowers/plans/2026-06-09-visual-companion-issues.md"
    "$REPO_ROOT/docs/superpowers/plans/2026-06-10-visual-companion-auth-hardening.md"
    "$REPO_ROOT/docs/superpowers/plans/2026-06-11-visual-companion-final-hardening-fixup.md"
    "$REPO_ROOT/docs/superpowers/specs/2026-02-19-visual-brainstorming-refactor-design.md"
    "$REPO_ROOT/docs/superpowers/specs/2026-03-11-zero-dep-brainstorm-server-design.md"
    "$REPO_ROOT/docs/superpowers/specs/2026-06-10-visual-companion-auth-hardening-design.md"
    "$REPO_ROOT/docs/superpowers/specs/2026-06-11-visual-companion-final-hardening-fixup-design.md"
)

for surface in "${unsupported_distribution_surfaces[@]}"; do
    [[ ! -e "$surface" ]] || fail "unsupported distribution surface must be absent: $surface"
done

assert_absent \
    'executing-plans|finishing-a-development-branch|subagent-driven-development|using-git-worktrees|writing-plans' \
    "${active_surfaces[@]}"

if rg -n \
    --glob '!test-spec-to-tdd-consistency.sh' \
    'executing-plans|subagent-driven-development|using-git-worktrees|writing-plans' \
    "$REPO_ROOT/tests"; then
    fail "tests still target a removed workflow"
fi

if rg -n -i \
    --glob '!test-spec-to-tdd-consistency.sh' \
    'dispatch[^\n]*(implementer|developer)|fresh subagent|subagent per|Subagent[^\n]*:[[:space:]]*"Fix|use[^\n]*Agent[^\n]*for implementation' \
    "${active_surfaces[@]}"; then
    fail "active surface delegates implementation to another agent"
fi

assert_absent \
    'plan-validate-execute|create a plan|plan file|reversible planning' \
    "$REPO_ROOT/skills/writing-skills/anthropic-best-practices.md"

assert_absent \
    'create (a )?(todo|task)|todo per|task for each|task artifact|write_todos|TODO\.md|TodoWrite|TodoList|todowrite|create or update todos|create / update todos|Todo / task tracking' \
    "${active_surfaces[@]}"

assert_absent \
    '\bworktrees?\b' \
    "$REPO_ROOT/README.md" \
    "$REPO_ROOT/skills"

assert_absent \
    'Codex 工具映射|codex-tools\.md' \
    "$REPO_ROOT/skills/writing-skills/SKILL.md"

assert_absent \
    '```dot|Graphviz|graphviz|render-graphs' \
    "$REPO_ROOT/skills"

assert_contains \
    "skills/brainstorming/SKILL.md" \
    '^description: 用于开始或恢复.*长任务' \
    "brainstorming must trigger for substantial tasks"

for required_trigger in \
    '相互依赖的阶段' \
    '持久保存进度' \
    '跨越上下文边界' \
    '用户明确要求.*plan 或 specification' \
    '一次连续处理中完成和验证'; do
    assert_contains \
        "skills/brainstorming/SKILL.md" \
        "$required_trigger" \
        "long-task trigger contract is missing: $required_trigger"
done

for spec_location_contract in \
    '未指定时默认使用 `<project-root>/superpowers/YYYY-MM-DD-<topic>-spec.md`' \
    '项目根.*普通 Git 仓库或 workspace.*repository/workspace root' \
    '`superpowers/` 内.*直接平铺' \
    '不得再增加 `specs/`、`plans/`、日期目录或主题子目录' \
    '项目 authority.*显式指定其它位置.*继续服从' \
    '`docs/superpowers/specs/` 是已退役的旧默认目录' \
    '旧默认目录.*不构成.*自定义 authority'; do
    assert_contains \
        "skills/brainstorming/SKILL.md" \
        "$spec_location_contract" \
        "project-local flat spec location contract is missing: $spec_location_contract"
done

assert_absent \
    '默认使用 `docs/superpowers/specs/' \
    "$REPO_ROOT/skills/brainstorming/SKILL.md"

assert_absent \
    'starting any conversation|even a 1% chance|simple question.*task|before any response or action' \
    "$REPO_ROOT/skills/brainstorming/SKILL.md"

assert_absent \
    'using-superpowers' \
    "${active_surfaces[@]}"

assert_absent \
    'superpowers:' \
    "${active_surfaces[@]}"

assert_absent \
    'SessionStart|sessionStart|loads? the `using-superpowers` bootstrap|auto-triggers? the `brainstorming` skill|including[^\n]*hooks' \
    "${active_surfaces[@]}"

assert_absent \
    '/plugin install|plugin marketplace|/add-plugin|agy plugin install|pi install|opencode plugin|\.codex-plugin|\.claude-plugin' \
    "$REPO_ROOT/README.md"

distribution_skill_entrypoints=()
for skill_entrypoint in "$REPO_ROOT"/skills/*/SKILL.md; do
    [[ "$skill_entrypoint" == "$REPO_ROOT/skills/ai-session-review/SKILL.md" ]] ||
        distribution_skill_entrypoints+=("$skill_entrypoint")
done

assert_absent \
    'Gemini|Kimi|Antigravity|OpenCode|Copilot|Cursor|Pi extension' \
    "$REPO_ROOT/README.md" \
    "$REPO_ROOT/CLAUDE.md" \
    "$REPO_ROOT/docs/testing.md" \
    "${distribution_skill_entrypoints[@]}"

assert_contains \
    "README.md" \
    'Superpowers is a skills library, not a plugin' \
    "README must define the skills-only distribution boundary"
assert_contains \
    "README.md" \
    'criterion-to-Oracle verification contract' \
    "README must expose the verification contract"
assert_contains \
    "README.md" \
    'Write tests first for changed software behavior' \
    "README TDD philosophy must match the software-behavior boundary"
assert_absent \
    'Write tests first, always' \
    "$REPO_ROOT/README.md"
assert_contains \
    "README.md" \
    '\.claude/skills' \
    "README must document Claude native skill discovery"
assert_contains \
    "README.md" \
    '\.agents/skills' \
    "README must document Codex native skill discovery"

for reviewer_escape in \
    'READ-ONLY-REVIEWER-STOP' \
    '派遣为只读 reviewer 或 skill 行为 evaluator' \
    '不要创建、修改、批准或推进 executable spec'; do
    assert_contains \
        "skills/brainstorming/SKILL.md" \
        "$reviewer_escape" \
        "read-only reviewer/evaluator escape is missing: $reviewer_escape"
done

for required_routing in \
    '^## 短任务$' \
    '^## 长任务$' \
    '^## 恢复工作$' \
    '一份 executable spec' \
    'behavior evidence' \
    'research evidence' \
    'artifact or state evidence'; do
    assert_contains \
        "skills/brainstorming/SKILL.md" \
        "$required_routing" \
        "long-task routing contract is missing: $required_routing"
done

for verification_contract in \
    '^### 验证合同$' \
    '每个会影响 slice 或最终完成判断的.*criterion ID' \
    '\*\*要证明的事实\*\*：可观察、可证伪' \
    '\*\*Oracle\*\*：能够区分该事实成立与不成立' \
    '软件 Oracle.*测试文件.*场景.*命令.*聚焦.*扩展' \
    '\*\*通过条件\*\*：执行验证前确定' \
    '\*\*完成证据\*\*：执行后填写.*执行前写 `待执行`' \
    '\*\*覆盖边界\*\*：该 Oracle 没有证明的范围' \
    '需要证明.*发生了改变.*前后比较.*修改前基线'; do
    assert_contains \
        "skills/brainstorming/SKILL.md" \
        "$verification_contract" \
        "verification contract is missing: $verification_contract"
done

assert_absent \
    '^\- \*\*完成证据\*\*：执行后回填' \
    "$REPO_ROOT/skills/brainstorming/SKILL.md"

assert_contains \
    "skills/brainstorming/spec-document-reviewer-prompt.md" \
    '验证闭环.*criterion.*Oracle.*通过条件.*覆盖边界.*待执行.*实际结果.*位置' \
    "spec reviewer must check the verification contract"
assert_contains \
    "skills/brainstorming/spec-document-reviewer-prompt.md" \
    '软件 contract.*验收标准.*验证合同.*迁移和兼容' \
    "spec reviewer must treat the verification contract as the software verification owner"
assert_contains \
    "skills/brainstorming/spec-document-reviewer-prompt.md" \
    'Slice 完整性.*验收 criterion ID.*审查门槛' \
    "spec reviewer must keep evidence out of implementation slices"
assert_absent \
    '测试映射|Slice 完整性.*证据' \
    "$REPO_ROOT/skills/brainstorming/spec-document-reviewer-prompt.md"

for software_slice_field in \
    '^每个软件 \*\*Implementation Slice\*\* 还包含：$' \
    '\*\*文件\*\*：预计创建、修改或删除的精确文件.*owner.*production files/shared crate.*concurrency/lifecycle.*failure modes.*blast radius' \
    '\*\*数据决策\*\*：引用上面的结构定义和转换条目' \
    '\*\*验收标准\*\*：该 slice 证明的精确 criterion ID.*criterion -> runtime owner -> mutation/publication point -> RED test.*不是新表格或第二份计划' \
    '\*\*审查门槛\*\*：.*单独只读审查'; do
    assert_contains \
        "skills/brainstorming/SKILL.md" \
        "$software_slice_field" \
        "software implementation-slice contract is missing: $software_slice_field"
done

assert_absent \
    '^\- \*\*验证合同\*\*：|^\- \*\*聚焦验证\*\*：|^\- \*\*扩展验证\*\*：|\*\*测试映射\*\*' \
    "$REPO_ROOT/skills/brainstorming/SKILL.md"

for debugging_contract in \
    '长时间 debugging' \
    'systematic-debugging' \
    '根因调查 slice.*research evidence' \
    '修复 slice.*behavior evidence' \
    '只有修复 slice.*test-driven-development'; do
    assert_contains \
        "skills/brainstorming/SKILL.md" \
        "$debugging_contract" \
        "long debugging mixed-profile contract is missing: $debugging_contract"
done

assert_contains \
    "skills/brainstorming/SKILL.md" \
    '^## Executable Spec Contract 结构$' \
    "brainstorming must define the executable spec contract"
assert_absent \
    'visual companion|visual-companion|brainstorm-server|BRAINSTORM_' \
    "$REPO_ROOT/README.md" \
    "$REPO_ROOT/docs/testing.md" \
    "$REPO_ROOT/skills/brainstorming/SKILL.md"

for required_section in \
    '目标与非目标' \
    '当前状态与 Authority' \
    '交付物' \
    '执行 Slice' \
    '完成证据' \
    '修订条件' \
    '最终验收'; do
    assert_contains \
        "skills/brainstorming/SKILL.md" \
        "$required_section" \
        "common executable spec is missing: $required_section"
done

for required_common_contract in \
    '唯一持久的执行大纲' \
    '结果' \
    '依赖' \
    '工作范围' \
    '输入与 Authority' \
    '交付物' \
    '完成证据' \
    '审查门槛' \
    '重新打开' \
    'Evidence update' \
    'Recovery metadata' \
    'Semantic revision' \
    '实现遗漏违反已有 criterion.*不得为同一要求新增 criterion' \
    '进度标记.*slice accepted.*完成证据.*审查门槛.*关闭' \
    '依赖.*前置 slice.*accepted'; do
    assert_contains \
        "skills/brainstorming/SKILL.md" \
        "$required_common_contract" \
        "common executable spec contract is missing: $required_common_contract"
done

assert_contains \
    "skills/brainstorming/SKILL.md" \
    '软件 Implementation Slice 只引用 criterion ID.*Oracle.*验证合同' \
    "software slices must not duplicate verification-contract details"
assert_absent \
    '验证或审查门槛|简单 criterion 可以直接写在 slice' \
    "$REPO_ROOT/skills/brainstorming/SKILL.md"

for required_profile in \
    '^### Behavior Evidence（软件行为证据）$' \
    '^### Research Evidence（研究证据）$' \
    '^### Artifact or State Evidence（产物或状态证据）$' \
    '人工研究和判断不使用 TDD' \
    '软件行为变化或纯行为保持型重构的 slice 使用 `test-driven-development`'; do
    assert_contains \
        "skills/brainstorming/SKILL.md" \
        "$required_profile" \
        "completion-evidence profile is missing: $required_profile"
done

for required_software_contract in \
    '目标文件' \
    '系统组成与数据流' \
    '接口与边界 contract' \
    'Implementation Slice' \
    '验收标准' \
    '验证合同' \
    'canonical owner' \
    'containment' \
    '相同形状' \
    '转换表' \
    'LANGUAGE-HARD-GATE' \
    '使用中文讨论需求' \
    '整份 spec 必须使用中文' \
    '中文 spec 中的英文叙述标签' \
    '叙述语言漂移' \
    '技术字面量'; do
    assert_contains \
        "skills/brainstorming/SKILL.md" \
        "$required_software_contract" \
        "software evidence profile is missing: $required_software_contract"
done

for required_structure_contract in \
    '^#### 关键数据结构与 SSOT$' \
    '逐个列出所有关键结构' \
    '完整字段与类型' \
    '所属层级' \
    '嵌套、包含或引用关系' \
    '唯一 canonical owner' \
    'projection 不得成为第二个 authority' \
    '仅重命名、逐字段复制、包装或格式转换' \
    '不能证明新结构合理' \
    'source -> target' \
    '增加、删除、重命名、校验或编码' \
    '无法复用 canonical type 的边界理由'; do
    assert_contains \
        "skills/brainstorming/SKILL.md" \
        "$required_structure_contract" \
        "key data-structure and SSOT contract is missing: $required_structure_contract"
done

assert_contains \
    "README.md" \
    '[Ss]hort.*one pass' \
    "README must describe the short-task exit"
assert_contains \
    "README.md" \
    'research evidence.*artifact or state evidence.*behavior evidence' \
    "README must describe all completion-evidence profiles"

[[ ! -e "$REPO_ROOT/tests/workflow/evidence" ]] ||
    fail "one-off evaluator evidence must stay in task records, not the active test tree"

for retired_artifact in \
    skills/systematic-debugging/CREATION-LOG.md \
    skills/systematic-debugging/test-academic.md \
    skills/systematic-debugging/test-pressure-1.md \
    skills/systematic-debugging/test-pressure-2.md \
    skills/systematic-debugging/test-pressure-3.md \
    skills/writing-skills/graphviz-conventions.dot \
    skills/writing-skills/render-graphs.js \
    skills/writing-skills/examples/CLAUDE_MD_TESTING.md; do
    [[ ! -e "$REPO_ROOT/$retired_artifact" ]] ||
        fail "retired skill-development artifact remains: $retired_artifact"
done

assert_absent \
    'CREATION-LOG|test-academic|test-pressure-[123]|CLAUDE_MD_TESTING|tests/workflow/evidence' \
    "${active_surfaces[@]}"

for review_entry in \
    skills/brainstorming/SKILL.md \
    skills/systematic-debugging/SKILL.md \
    skills/test-driven-development/SKILL.md; do
    assert_contains \
        "$review_entry" \
        'requesting-code-review' \
        "software workflow must name the code-review entrypoint"
done

for completion_entry in \
    skills/systematic-debugging/SKILL.md \
    skills/test-driven-development/SKILL.md; do
    assert_contains \
        "$completion_entry" \
        'receiving-code-review.*verification-before-completion' \
        "software workflow must name the review-feedback and verification route"
done

for tdd_refactor_contract in \
    '^description: .*新增或修改软件行为.*bugfix.*行为保持型重构' \
    '核心原则：行为变化没有先看到测试失败' \
    '纯行为保持型重构' \
    '先运行现有相关测试.*GREEN' \
    'characterization test.*旧行为' \
    '不要为了制造 RED' \
    '需要改变行为.*回到 RED' \
    '新行为或 bugfix.*实现前以正确原因失败'; do
    assert_contains \
        "skills/test-driven-development/SKILL.md" \
        "$tdd_refactor_contract" \
        "TDD refactor boundary is missing: $tdd_refactor_contract"
done

assert_absent \
    '^没有先失败的测试，就不能写生产代码$' \
    "$REPO_ROOT/skills/test-driven-development/SKILL.md"

assert_contains \
    "skills/requesting-code-review/SKILL.md" \
    '^description: 完成软件实现' \
    "code review trigger must be limited to software implementation"
assert_contains \
    "skills/receiving-code-review/SKILL.md" \
    '^description: 收到 code review 反馈，需要验证、回应或准备实施建议时使用' \
    "receiving review must cover validation and response without requiring implementation"
assert_contains \
    "skills/receiving-code-review/SKILL.md" \
    '用户只要求 review.*返回核查结果.*等待确认' \
    "review-only feedback must stop before implementation"
assert_contains \
    "skills/receiving-code-review/SKILL.md" \
    '已有 criterion.*implementation omission.*原实现授权.*owner.*架构.*scope.*业务目标.*Semantic revision' \
    "review handling must distinguish implementation omissions from semantic revisions"
for receiving_contract in \
    '完整核查所有 finding.*finding ledger.*`ID`.*`verdict`.*`criterion/authority`.*`RED 或事实证据`.*`fix/diff`.*`verification`.*`closure`.*不是第二份计划' \
    '代码 finding.*`test-driven-development`.*实施路径' \
    '新行为、行为修改或 bugfix.*RED-GREEN' \
    '纯行为保持型重构.*GREEN 基线' \
    '测试不足.*characterization test' \
    '改变行为.*回到 RED'; do
    assert_contains \
        "skills/receiving-code-review/SKILL.md" \
        "$receiving_contract" \
        "receiving review contract is missing: $receiving_contract"
done
assert_contains \
    "skills/requesting-code-review/SKILL.md" \
    '影响.*触发频率.*修复成本' \
    "code review must use an explicit ROI gate"
assert_contains \
    "skills/requesting-code-review/code-reviewer.md" \
    '触发路径.*发生概率或频率.*影响范围' \
    "review findings must include likelihood and impact evidence"

assert_contains \
    "skills/requesting-code-review/SKILL.md" \
    '只读 reviewer subagent' \
    "code review must use a read-only reviewer"
assert_contains \
    "skills/requesting-code-review/SKILL.md" \
    '当前 harness 的原生 agent 工具.*fresh-context.*只读 reviewer' \
    "code review dispatch must be harness-neutral and fresh-context"
assert_contains \
    "skills/requesting-code-review/code-reviewer.md" \
    '当前 harness 的原生 agent 工具.*fresh-context.*只读 reviewer' \
    "code reviewer template must be harness-neutral and fresh-context"
assert_absent \
    'general-purpose' \
    "$REPO_ROOT/skills/requesting-code-review/SKILL.md" \
    "$REPO_ROOT/skills/requesting-code-review/code-reviewer.md"
assert_contains \
    "skills/requesting-code-review/SKILL.md" \
    '不得编辑文件、运行实现任务或提交' \
    "reviewer must be prohibited from implementation"
for review_scope_field in \
    'REVIEW_SUBJECT' \
    'FULL_BASE_SHA' \
    'DIFF_BASE_SHA'; do
    assert_contains \
        "skills/requesting-code-review/SKILL.md" \
        "$review_scope_field" \
        "code review scope field is missing: $review_scope_field"
done
assert_contains \
    "skills/requesting-code-review/SKILL.md" \
    '当前 slice.*criterion.*`DIFF_BASE_SHA`.*最终集成审查.*FULL_BASE_SHA' \
    "successive slice reviews must not repeatedly scan the accumulated task diff"
assert_contains \
    "skills/requesting-code-review/SKILL.md" \
    '独立 review.*可用 checkpoint.*一次性.*授权.*未获授权.*停止.*不能.*累计 diff' \
    "an independent slice review must stop when no authorized checkpoint can isolate its diff"
assert_absent \
    '就把这些变更合并为同一个 review subject' \
    "$REPO_ROOT/skills/requesting-code-review/SKILL.md"
assert_contains \
    "skills/requesting-code-review/SKILL.md" \
    '审查前验证' \
    "code review must receive fresh pre-review verification evidence"
assert_contains \
    "skills/requesting-code-review/SKILL.md" \
    '原 reviewer 定点 closure' \
    "important review fixes must receive targeted closure from the original reviewer"
for review_lifecycle_contract in \
    '同一 review subject.*一个.*reviewer 完整审查' \
    '不要启动 fresh full reviewer' \
    '同一 subject.*最多替换一次.*不得并行' \
    '最多两轮 closure' \
    '检查 reviewer.*结束'; do
    assert_contains \
        "skills/requesting-code-review/SKILL.md" \
        "$review_lifecycle_contract" \
        "code review lifecycle is missing: $review_lifecycle_contract"
done
for reviewer_scope_contract in \
    'REVIEW_SUBJECT' \
    'FULL_BASE_SHA' \
    'DIFF_BASE_SHA' \
    'git diff.*DIFF_BASE_SHA' \
    'final integration.*DIFF_BASE_SHA.*FULL_BASE_SHA'; do
    assert_contains \
        "skills/requesting-code-review/code-reviewer.md" \
        "$reviewer_scope_contract" \
        "reviewer scope contract is missing: $reviewer_scope_contract"
done
for reviewer_mode_contract in \
    'REVIEW_MODE.*full.*closure' \
    'stable finding ID' \
    'closure.*只复查' \
    '`closure` 模式只按 stable finding ID' \
    '不输出优点' \
    '新建议或合并判断'; do
    assert_contains \
        "skills/requesting-code-review/code-reviewer.md" \
        "$reviewer_mode_contract" \
        "reviewer mode contract is missing: $reviewer_mode_contract"
done
assert_contains \
    "skills/requesting-code-review/SKILL.md" \
    '^\- reviewer 返回 findings 后，必须先加载 `receiving-code-review`，不能把 finding 直接当成修改指令。$' \
    "review findings must route explicitly to receiving-code-review"
for review_fix_tdd_contract in \
    '新行为、行为修改或 bugfix finding.*失败测试' \
    '纯行为保持型重构 finding.*GREEN 基线' \
    '测试不足.*characterization test.*旧行为'; do
    assert_contains \
        "skills/requesting-code-review/SKILL.md" \
        "$review_fix_tdd_contract" \
        "review fix must preserve the TDD behavior/refactor boundary: $review_fix_tdd_contract"
done
assert_absent \
    '每个有效代码 finding.*先用失败测试复现' \
    "$REPO_ROOT/skills/requesting-code-review/SKILL.md"

assert_contains \
    "skills/verification-before-completion/SKILL.md" \
    '声明的完成证据' \
    "completion verification must follow the spec evidence contract"
assert_contains \
    "skills/verification-before-completion/SKILL.md" \
    '逐项执行.*criterion.*Oracle.*通过条件.*原位回填.*Evidence.*覆盖边界' \
    "completion verification must execute and fill the criterion evidence contract"
for completion_contract in \
    'Behavior Evidence' \
    'Research Evidence' \
    'Artifact or State Evidence' \
    '最高、适用且有新鲜证据支持的层级' \
    '仍未完成的适用上层' \
    'implementation green.*review closed.*spec complete.*local runtime accepted.*external/testnet/remote accepted.*overall goal complete' \
    '活跃 reviewer.*session' \
    '完成声明.*subject.*S2.*spec path.*overall goal'; do
    assert_contains \
        "skills/verification-before-completion/SKILL.md" \
        "$completion_contract" \
        "verification completion contract is missing: $completion_contract"
done
for spec_review_lifecycle in \
    '同一 spec review subject.*一个.*reviewer' \
    'stable finding ID' \
    '原 reviewer.*closure' \
    '同一 subject.*最多替换一次.*不得并行' \
    '最多两轮 closure' \
    '结束.*reviewer.*session'; do
    assert_contains \
        "skills/brainstorming/SKILL.md" \
        "$spec_review_lifecycle" \
        "spec review lifecycle is missing: $spec_review_lifecycle"
done
for spec_reviewer_mode in \
    'REVIEW_MODE.*full.*closure' \
    'FINDING_LEDGER' \
    'stable finding ID' \
    'closure.*只复查' \
    '`CLOSED`.*`OPEN`.*`NOT VERIFIED`'; do
    assert_contains \
        "skills/brainstorming/spec-document-reviewer-prompt.md" \
        "$spec_reviewer_mode" \
        "spec reviewer closure contract is missing: $spec_reviewer_mode"
done
assert_contains \
    "skills/brainstorming/SKILL.md" \
    '非软件 profile.*授权直接执行.*第一个依赖就绪的 slice' \
    "an explicit continue instruction must allow non-software execution after spec self-review"
assert_contains \
    "skills/brainstorming/SKILL.md" \
    'implementation omission.*更新原 criterion 的完成证据和 closure.*不得改变 criterion 定义' \
    "implementation omissions must update evidence without redefining the criterion"
assert_contains \
    "README.md" \
    'prerequisites are accepted.*current slice or checkpoint.*full integration review' \
    "README workflow summary must match successive-slice review semantics"
assert_contains \
    "skills/brainstorming/SKILL.md" \
    '先规划.*等待批准' \
    "an explicit plan-first instruction must retain the approval gate"
assert_contains \
    "skills/brainstorming/SKILL.md" \
    'Behavior-evidence 软件工作必须获得书面 spec 批准' \
    "software behavior work must retain written approval and a separate baseline"
assert_contains \
    "skills/brainstorming/SKILL.md" \
    '用户或治理流程授权.*单独提交最终已批准 spec.*`FULL_BASE_SHA`.*未获授权.*生产修改前停止' \
    "software behavior work must hand the approved-spec commit to review"
assert_contains \
    "skills/brainstorming/SKILL.md" \
    '用户审阅完整设计后获得明确实现预授权' \
    "software behavior work must preserve the complete-design pre-authorization path"
assert_contains \
    "skills/brainstorming/SKILL.md" \
    '最终 spec 加入了已审阅设计中不存在的实质决策，预授权立即失效' \
    "material decisions in the final spec must invalidate pre-authorization"
assert_contains \
    "skills/brainstorming/SKILL.md" \
    '现有系统融入检查' \
    "mature-system specs must include the integration check"
for integration_field in \
    '现有 owner' \
    '复用入口' \
    '新增责任' \
    '平行系统检查'; do
    assert_contains \
        "skills/brainstorming/SKILL.md" \
        "$integration_field" \
        "mature-system integration check is missing: $integration_field"
done
assert_contains \
    "skills/brainstorming/spec-document-reviewer-prompt.md" \
    '成熟系统.*现有 owner.*复用入口.*新增责任.*平行系统' \
    "spec review must check mature-system integration boundaries"
assert_contains \
    "skills/test-driven-development/SKILL.md" \
    '未批准的状态 owner.*状态机.*重试.*缓存.*生命周期.*停止 TDD.*修订 spec' \
    "TDD must stop when implementation crosses the approved integration boundary"
assert_contains \
    "skills/brainstorming/SKILL.md" \
    '应用 profile 的执行门槛.*非软件工作.*等待或继续指令.*Behavior-evidence 软件工作.*书面 spec 获批.*明确实现预授权.*授权.*提交已批准 spec.*`FULL_BASE_SHA`' \
    "the common process must not bypass the software approval and baseline gate"
assert_absent \
    'Spec written and committed' \
    "$REPO_ROOT/skills/brainstorming/SKILL.md"

assert_absent \
    'preferred baseline|Spec / Requirements|SPEC_OR_REQUIREMENTS' \
    "$REPO_ROOT/skills/requesting-code-review/SKILL.md" \
    "$REPO_ROOT/skills/requesting-code-review/code-reviewer.md"
assert_contains \
    "skills/requesting-code-review/SKILL.md" \
    'REVIEW_AUTHORITY' \
    "code review must receive the task's governing authority"

assert_contains \
    "skills/requesting-code-review/SKILL.md" \
    '没有独立 spec 的短软件任务.*用户原始要求.*项目 authority.*验收条件' \
    "spec-less short software work must have a valid review authority"
assert_contains \
    "skills/requesting-code-review/SKILL.md" \
    '不得为了 review 事后补写 spec' \
    "short-task review must not force a retroactive spec"
assert_contains \
    "skills/requesting-code-review/code-reviewer.md" \
    'REVIEW_AUTHORITY' \
    "review template must accept the governing authority for both long and short work"
assert_absent \
    '证明 spec|对照已批准 executable spec' \
    "$REPO_ROOT/skills/requesting-code-review/code-reviewer.md"

echo "General long-task spec workflow consistency checks passed"
