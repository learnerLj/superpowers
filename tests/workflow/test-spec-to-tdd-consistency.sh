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
    'executing-plans|subagent-driven-development|using-git-worktrees|writing-plans' \
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

assert_absent \
    'starting any conversation|even a 1% chance|simple question.*task|before any response or action' \
    "$REPO_ROOT/skills/brainstorming/SKILL.md"

assert_absent \
    'using-superpowers' \
    "${active_surfaces[@]}"

assert_absent \
    'SessionStart|sessionStart|loads? the `using-superpowers` bootstrap|auto-triggers? the `brainstorming` skill|including[^\n]*hooks' \
    "${active_surfaces[@]}"

assert_absent \
    '/plugin install|plugin marketplace|/add-plugin|agy plugin install|pi install|opencode plugin|\.codex-plugin|\.claude-plugin' \
    "$REPO_ROOT/README.md"

assert_absent \
    'Gemini|Kimi|Antigravity|OpenCode|Copilot|Cursor|Pi extension' \
    "$REPO_ROOT/README.md" \
    "$REPO_ROOT/CLAUDE.md" \
    "$REPO_ROOT/docs/testing.md" \
    "$REPO_ROOT"/skills/*/SKILL.md

assert_contains \
    "README.md" \
    'Superpowers is a skills library, not a plugin' \
    "README must define the skills-only distribution boundary"
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

for software_slice_field in \
    '^每个软件 \*\*Implementation Slice\*\* 还包含：$' \
    '\*\*文件\*\*：预计创建、修改或删除的精确文件' \
    '\*\*数据决策\*\*：引用上面的结构定义和转换条目' \
    '\*\*验收标准\*\*：该 slice 证明的精确 criterion ID' \
    '\*\*聚焦验证\*\*：针对直接行为的精确命令' \
    '\*\*扩展验证\*\*：' \
    '\*\*审查门槛\*\*：.*单独只读审查'; do
    assert_contains \
        "skills/brainstorming/SKILL.md" \
        "$software_slice_field" \
        "software implementation-slice contract is missing: $software_slice_field"
done

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
    '验证或审查门槛' \
    '重新打开'; do
    assert_contains \
        "skills/brainstorming/SKILL.md" \
        "$required_common_contract" \
        "common executable spec contract is missing: $required_common_contract"
done

for required_profile in \
    '^### Behavior Evidence（软件行为证据）$' \
    '^### Research Evidence（研究证据）$' \
    '^### Artifact or State Evidence（产物或状态证据）$' \
    '人工研究和判断不使用 TDD' \
    '只有改变软件行为的 slice 使用 `test-driven-development`'; do
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
    '测试映射' \
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

eval_evidence="tests/workflow/evidence/2026-08-06-general-long-task-routing-evals.md"
for eval_contract in \
    'Control source: committed baseline' \
    'Candidate source: the content-addressed working-tree skill snapshot' \
    'Candidate snapshot SHA-256 values used by the final recheck' \
    '^## E1: Short Read-Only Lookup$' \
    '^## E2: Long Research$' \
    '^## E3: Configuration Migration$' \
    '^## E4: Cross-Module Software Change$' \
    '^## E5: Long Intermittent Debugging$' \
    '^## Evidence Boundary$'; do
    assert_contains \
        "$eval_evidence" \
        "$eval_contract" \
        "paired behavior-eval evidence is missing: $eval_contract"
done

assert_contains \
    "skills/requesting-code-review/SKILL.md" \
    '只读 reviewer subagent' \
    "code review must use a read-only reviewer"
assert_contains \
    "skills/requesting-code-review/SKILL.md" \
    '不得编辑文件、运行实现任务或提交' \
    "reviewer must be prohibited from implementation"
assert_contains \
    "skills/requesting-code-review/SKILL.md" \
    'git diff.*BASE_SHA' \
    "code review must cover the current working tree from the approved-spec baseline"
assert_contains \
    "skills/requesting-code-review/SKILL.md" \
    '审查前验证' \
    "code review must receive fresh pre-review verification evidence"
assert_contains \
    "skills/requesting-code-review/SKILL.md" \
    '重复审查' \
    "important review fixes must be reviewed again"

assert_contains \
    "skills/verification-before-completion/SKILL.md" \
    '声明的完成证据' \
    "completion verification must follow the spec evidence contract"
for evidence_profile in \
    'Behavior Evidence' \
    'Research Evidence' \
    'Artifact or State Evidence'; do
    assert_contains \
        "skills/verification-before-completion/SKILL.md" \
        "$evidence_profile" \
        "verification profile is missing: $evidence_profile"
done
assert_contains \
    "skills/verification-before-completion/SKILL.md" \
    '只有 behavior-evidence 软件工作.*finishing-a-development-branch' \
    "branch finishing must remain conditional on software behavior work"
assert_contains \
    "skills/finishing-a-development-branch/SKILL.md" \
    'git status --short' \
    "branch finishing must check for uncommitted implementation changes"

assert_contains \
    "skills/brainstorming/SKILL.md" \
    '非软件 profile.*授权直接执行.*第一个依赖就绪的 slice' \
    "an explicit continue instruction must allow non-software execution after spec self-review"
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
    '单独提交最终已批准 spec，并把该提交记录为 `BASE_SHA`' \
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
    '应用 profile 的执行门槛.*非软件工作.*等待或继续指令.*Behavior-evidence 软件工作.*书面 spec 获批.*明确实现预授权.*提交已批准 spec.*`BASE_SHA`' \
    "the common process must not bypass the software approval and baseline gate"
assert_absent \
    'Spec written and committed' \
    "$REPO_ROOT/skills/brainstorming/SKILL.md"

assert_absent \
    'preferred baseline|exact requirements|Spec / Requirements|SPEC_OR_REQUIREMENTS' \
    "$REPO_ROOT/skills/requesting-code-review/SKILL.md" \
    "$REPO_ROOT/skills/requesting-code-review/code-reviewer.md"
assert_contains \
    "skills/requesting-code-review/SKILL.md" \
    'APPROVED_SPEC' \
    "code review must use the approved executable spec as its sole authority"

echo "General long-task spec workflow consistency checks passed"
