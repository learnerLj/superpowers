#!/usr/bin/env bash
# Validate the Antigravity (agy) integration. agy installs the existing plugin
# directly (`agy plugin install <repo-url>`): it loads the bundled skills and
# runs the SessionStart hook for bootstrap, so there is no agy-specific scaffold
# to test. What IS agy-specific is the tool mapping — read-only review via
# invoke_subagent (research type), with no workflow task artifact, and SKILL.md
# pointing at it.
#
# Mirrors tests/pi/test-pi-extension.mjs's "tools reference documents
# harness-specific mappings" check. CI-safe: does not require `agy` installed.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

MAPPING="$REPO_ROOT/skills/using-superpowers/references/antigravity-tools.md"
SKILL="$REPO_ROOT/skills/using-superpowers/SKILL.md"

fail() { echo "FAIL: $*" >&2; exit 1; }

echo "test-antigravity-tools: checking Antigravity tool mapping"

# --- Mapping exists ---------------------------------------------------------
[ -f "$MAPPING" ] || fail "tool mapping missing at $MAPPING"

# --- Core action→tool mappings are documented -------------------------------
for tool in invoke_subagent; do
  grep -q "$tool" "$MAPPING" \
    || fail "mapping does not document the '$tool' tool"
done

# --- Reviewer agents use only the built-in research type --------------------
grep -q 'TypeName: "research"' "$MAPPING" \
  || fail "mapping does not require the built-in 'research' reviewer type"
grep -q 'never use `self` for implementation' "$MAPPING" \
  || fail "mapping does not prohibit full-capability implementation agents"

# --- Workflow does not create task artifacts --------------------------------
if grep -qiE 'create a todo|task artifact|ArtifactType.*task' "$MAPPING"; then
  fail "mapping still requires plan-like task tracking"
fi

# --- SKILL.md Platform Adaptation links the mapping -------------------------
grep -q "antigravity-tools.md" "$SKILL" \
  || fail "SKILL.md Platform Adaptation does not reference antigravity-tools.md"

echo "PASS: Antigravity tool mapping valid (read-only review, no task artifact, SKILL.md link)"
