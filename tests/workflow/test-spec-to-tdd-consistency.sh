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
    "$REPO_ROOT/README.md"
    "$REPO_ROOT/.codex-plugin/plugin.json"
    "$REPO_ROOT/.kimi-plugin/plugin.json"
    "$REPO_ROOT/.opencode/INSTALL.md"
    "$REPO_ROOT/.opencode/plugins/superpowers.js"
    "$REPO_ROOT/.pi/extensions/superpowers.ts"
    "$REPO_ROOT/docs/README.kimi.md"
    "$REPO_ROOT/docs/README.opencode.md"
    "$REPO_ROOT/docs/porting-to-a-new-harness.md"
    "$REPO_ROOT/docs/testing.md"
    "$REPO_ROOT/skills"
)

assert_absent \
    'executing-plans|subagent-driven-development|using-git-worktrees|writing-plans' \
    "${active_surfaces[@]}"

if rg -n \
    --glob '!test-spec-to-tdd-consistency.sh' \
    --glob '!test-package-codex-plugin.sh' \
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
    '\bplans?\b|\bplanning\b' \
    "$REPO_ROOT/README.md" \
    "$REPO_ROOT/.codex-plugin/plugin.json" \
    "$REPO_ROOT/.kimi-plugin/plugin.json" \
    "$REPO_ROOT/skills/brainstorming/SKILL.md" \
    "$REPO_ROOT/skills/using-superpowers/SKILL.md" \
    "$REPO_ROOT/skills/requesting-code-review/SKILL.md" \
    "$REPO_ROOT/skills/verification-before-completion/SKILL.md"

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
    "skills/brainstorming/SKILL.md" \
    '^## Executable Spec Contract$' \
    "brainstorming must define the executable spec contract"

for required_section in \
    'Target files' \
    'System composition and data flow' \
    'Interfaces and boundary contracts' \
    'Implementation Slices' \
    'Acceptance criteria' \
    'Test mapping' \
    'Non-goals'; do
    assert_contains \
        "skills/brainstorming/SKILL.md" \
        "$required_section" \
        "executable spec is missing: $required_section"
done

for required_contract in \
    'canonical owner' \
    'containment' \
    'same-shape' \
    'transformation' \
    'dependency order' \
    'progress marker' \
    'LANGUAGE-HARD-GATE' \
    'discussing the request in Chinese' \
    'entire spec in that selected language' \
    'English labels in a Chinese spec' \
    'narrative-language drift' \
    'technical literal'; do
    assert_contains \
        "skills/brainstorming/SKILL.md" \
        "$required_contract" \
        "executable spec contract is missing: $required_contract"
done

for exact_contract_line in \
    '^this precedence: direct user request, authoritative project language rule,$' \
    '^established language of an existing spec, then Chinese by default\.$' \
    '^fixed English output strings\. Localize `Outcome`, `Depends on`, `System scope`,$' \
    '^Each production implementation slice uses an unchecked Markdown progress marker in the approved baseline\.' \
    '^evidence was collected, recorded, reviewed, and disclosed to the user before approval\.$' \
    '^This exception never applies to production implementation work\.' \
    '^- \*\*Outcome:\*\* observable result when complete\.$' \
    '^- \*\*Depends on:\*\* prerequisite slice IDs, or `None`\.$' \
    '^- \*\*System scope:\*\* affected components and responsibility boundaries\.$' \
    '^- \*\*Data decisions:\*\* structure and transformation decisions, or an explicit no-change statement\.$' \
    '^- \*\*Files:\*\* exact files expected to be created, modified, or deleted\.$' \
    '^- \*\*Acceptance criteria:\*\* IDs proved by the slice\.$' \
    '^- \*\*Verification:\*\* focused and broader commands\.$' \
    '^- \*\*Review gate:\*\* read-only review required for cross-component, risky, or downstream-critical work; otherwise `None`\.$'; do
    assert_contains \
        "skills/brainstorming/SKILL.md" \
        "$exact_contract_line" \
        "executable spec contract line is missing: $exact_contract_line"
done

assert_contains \
    "README.md" \
    'embedded.*dependency-ordered implementation slices' \
    "README must describe the embedded execution outline"

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
    "README.md" \
    'verification.*read-only reviewer.*verification' \
    "README must show verification on both sides of read-only review"
assert_contains \
    "skills/verification-before-completion/SKILL.md" \
    'main agent commits the verified implementation' \
    "final verification must hand a committed implementation to branch finishing"
assert_contains \
    "skills/finishing-a-development-branch/SKILL.md" \
    'git status --short' \
    "branch finishing must check for uncommitted implementation changes"

assert_contains \
    "skills/brainstorming/SKILL.md" \
    'approved spec.*test-driven-development' \
    "brainstorming must hand the approved spec directly to TDD"
assert_contains \
    "skills/brainstorming/SKILL.md" \
    '"User reviews spec\?" -> "Commit approved spec"' \
    "the final spec must be approved before its baseline commit"
assert_contains \
    "skills/brainstorming/SKILL.md" \
    '"Commit approved spec" -> "Main agent invokes TDD"' \
    "the approved-spec commit must be the direct TDD baseline"
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

assert_absent \
    'docs/superpowers/plans|Implementation Plan|planning is ok' \
    "$REPO_ROOT/tests/explicit-skill-requests/run-test.sh"

echo "Spec-to-TDD workflow consistency checks passed"
