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
    'GIT_COMMON|git-common-dir' \
    "$REPO_ROOT/skills/using-superpowers/references/codex-tools.md"

assert_contains \
    "skills/using-superpowers/SKILL.md" \
    '^description: Use when starting or resuming a substantial task' \
    "using-superpowers must trigger only for substantial tasks"

for required_trigger in \
    'dependent stages' \
    'persistent progress' \
    'context boundary' \
    'explicitly requests a plan or specification' \
    'completed and verified in one pass'; do
    assert_contains \
        "skills/using-superpowers/SKILL.md" \
        "$required_trigger" \
        "long-task trigger contract is missing: $required_trigger"
done

assert_absent \
    'starting any conversation|even a 1% chance|simple question.*task|before any response or action' \
    "$REPO_ROOT/skills/using-superpowers/SKILL.md"

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
    'dispatched as a read-only reviewer or skill-behavior evaluator' \
    'Do not create, revise, approve, or advance an executable spec'; do
    assert_contains \
        "skills/using-superpowers/SKILL.md" \
        "$reviewer_escape" \
        "read-only reviewer/evaluator escape is missing: $reviewer_escape"
done

for required_routing in \
    '^## Short Tasks$' \
    '^## Long Tasks$' \
    '^## Resuming Work$' \
    'one executable spec' \
    'behavior evidence' \
    'research evidence' \
    'artifact or state evidence'; do
    assert_contains \
        "skills/using-superpowers/SKILL.md" \
        "$required_routing" \
        "long-task routing contract is missing: $required_routing"
done

for software_slice_field in \
    '^Each software \*\*Implementation Slice\*\* additionally contains:$' \
    '\*\*Files:\*\* exact files' \
    '\*\*Data decisions:\*\* structures and transformations' \
    '\*\*Acceptance criteria:\*\* exact criterion IDs' \
    '\*\*Focused verification:\*\* exact commands' \
    '\*\*Broader verification:\*\*' \
    '\*\*Review gate:\*\* a distinct read-only review requirement'; do
    assert_contains \
        "skills/brainstorming/SKILL.md" \
        "$software_slice_field" \
        "software implementation-slice contract is missing: $software_slice_field"
done

for debugging_contract in \
    'long debugging task' \
    'systematic-debugging' \
    'root-cause slice.*research evidence' \
    'fix slice.*behavior evidence' \
    'only the fix slice.*test-driven-development'; do
    assert_contains \
        "skills/using-superpowers/SKILL.md" \
        "$debugging_contract" \
        "long debugging mixed-profile contract is missing: $debugging_contract"
done

assert_contains \
    "skills/brainstorming/SKILL.md" \
    '^## Executable Spec Contract$' \
    "brainstorming must define the executable spec contract"
assert_contains \
    "skills/brainstorming/SKILL.md" \
    'visual-companion\.md' \
    "brainstorming must keep its bundled visual companion reachable"

for required_section in \
    'Goal and non-goals' \
    'Current state and authority' \
    'Deliverables' \
    'Execution slices' \
    'Completion evidence' \
    'Revision triggers' \
    'Final acceptance'; do
    assert_contains \
        "skills/brainstorming/SKILL.md" \
        "$required_section" \
        "common executable spec is missing: $required_section"
done

for required_common_contract in \
    'single persistent execution outline' \
    'Outcome' \
    'Depends on' \
    'Work scope' \
    'Inputs and authority' \
    'Deliverables' \
    'Completion evidence' \
    'Verification or review gate' \
    'reopen'; do
    assert_contains \
        "skills/brainstorming/SKILL.md" \
        "$required_common_contract" \
        "common executable spec contract is missing: $required_common_contract"
done

for required_profile in \
    '^### Behavior Evidence$' \
    '^### Research Evidence$' \
    '^### Artifact or State Evidence$' \
    '[Hh]uman research and judgment do not use TDD' \
    '[Oo]nly slices that change software behavior use test-driven-development'; do
    assert_contains \
        "skills/brainstorming/SKILL.md" \
        "$required_profile" \
        "completion-evidence profile is missing: $required_profile"
done

for required_software_contract in \
    'Target files' \
    'System composition and data flow' \
    'Interfaces and boundary contracts' \
    'Implementation Slices' \
    'Acceptance criteria' \
    'Test mapping' \
    'canonical owner' \
    'containment' \
    'same-shape' \
    'transformation' \
    'LANGUAGE-HARD-GATE' \
    'discussing the request in Chinese' \
    'entire spec in that selected language' \
    'English labels in a Chinese spec' \
    'narrative-language drift' \
    'technical literal'; do
    assert_contains \
        "skills/brainstorming/SKILL.md" \
        "$required_software_contract" \
        "software evidence profile is missing: $required_software_contract"
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
    'read-only reviewer subagent' \
    "code review must use a read-only reviewer"
assert_contains \
    "skills/requesting-code-review/SKILL.md" \
    'MUST NOT edit files, run implementation tasks, or commit changes' \
    "reviewer must be prohibited from implementation"
assert_contains \
    "skills/requesting-code-review/SKILL.md" \
    'git diff.*BASE_SHA' \
    "code review must cover the current working tree from the approved-spec baseline"
assert_contains \
    "skills/requesting-code-review/SKILL.md" \
    'pre-review verification' \
    "code review must receive fresh pre-review verification evidence"
assert_contains \
    "skills/requesting-code-review/SKILL.md" \
    'repeat.*review' \
    "important review fixes must be reviewed again"

assert_contains \
    "skills/verification-before-completion/SKILL.md" \
    'declared completion evidence' \
    "completion verification must follow the spec evidence contract"
for evidence_profile in \
    'Behavior evidence' \
    'Research evidence' \
    'Artifact or state evidence'; do
    assert_contains \
        "skills/verification-before-completion/SKILL.md" \
        "$evidence_profile" \
        "verification profile is missing: $evidence_profile"
done
assert_contains \
    "skills/verification-before-completion/SKILL.md" \
    'Only behavior-evidence software work continues to finishing-a-development-branch' \
    "branch finishing must remain conditional on software behavior work"
assert_contains \
    "skills/finishing-a-development-branch/SKILL.md" \
    'git status --short' \
    "branch finishing must check for uncommitted implementation changes"

assert_contains \
    "skills/brainstorming/SKILL.md" \
    'non-software.*direct execution.*first dependency-ready slice' \
    "an explicit continue instruction must allow non-software execution after spec self-review"
assert_contains \
    "skills/brainstorming/SKILL.md" \
    'plan first.*wait for approval' \
    "an explicit plan-first instruction must retain the approval gate"
assert_contains \
    "skills/brainstorming/SKILL.md" \
    'Behavior-evidence software.*written spec approval' \
    "software behavior work must retain written approval and a separate baseline"
assert_contains \
    "skills/brainstorming/SKILL.md" \
    'commit the final approved spec separately and record that commit as `BASE_SHA`' \
    "software behavior work must hand the approved-spec commit to review"
assert_contains \
    "skills/brainstorming/SKILL.md" \
    'explicit implementation pre-authorization after the human partner reviewed the complete design' \
    "software behavior work must preserve the complete-design pre-authorization path"
assert_contains \
    "skills/brainstorming/SKILL.md" \
    'Pre-authorization is invalid if the final spec adds a material decision' \
    "material decisions in the final spec must invalidate pre-authorization"
assert_contains \
    "skills/brainstorming/SKILL.md" \
    'Apply the profile.s execution gate.*non-software.*wait-or-continue.*behavior-evidence software work.*written spec approval.*complete-design pre-authorization.*approved-spec commit.*`BASE_SHA`' \
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
