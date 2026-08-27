#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

fail() {
    echo "FAIL: $*" >&2
    exit 1
}

model_files=()
while IFS= read -r file; do
    model_files+=("$file")
done < <(find "$REPO_ROOT/skills" -type f \( -name '*.md' -o -name '*.dot' \) \
    ! -path "$REPO_ROOT/skills/ai-session-review/tests/skill-pressure-scenarios.md" | sort)

skill_files=("$REPO_ROOT"/skills/*/SKILL.md)
[[ "${#skill_files[@]}" -eq 12 ]] ||
    fail "expected 12 SKILL.md entrypoints, found ${#skill_files[@]}"

for required_skill in traceable-explainer retro ai-session-review code-simplification-review verify-this; do
    [[ -f "$REPO_ROOT/skills/$required_skill/SKILL.md" ]] ||
        fail "required skill entrypoint is missing: $required_skill"
    rg -q "\*\*$required_skill\*\*" "$REPO_ROOT/README.md" ||
        fail "README discovery entry is missing: $required_skill"
done

retired_skill="code-path""-explainer"
[[ ! -e "$REPO_ROOT/skills/$retired_skill" ]] ||
    fail "retired skill directory remains: $retired_skill"

ai_review_dir="$REPO_ROOT/skills/ai-session-review"
[[ -d "$ai_review_dir" ]] || fail "required skill directory is missing: ai-session-review"
[[ "$(find "$ai_review_dir" -type f ! -path '*/__pycache__/*' ! -name '*.pyc' | wc -l | tr -d ' ')" == 17 ]] ||
    fail "ai-session-review must contain exactly 17 source files"
! rg -n -i '/Users/mike|users[-_]mike|obsidian[-_]vault[-_]study|nautilus[-_]trader|mantistrade|VAULT=.*obsidian_vault_study' "$ai_review_dir" ||
    fail "ai-session-review contains a private or Vault-local skill path"

for file in "${skill_files[@]}"; do
    description="$(sed -n '3p' "$file")"
    printf '%s\n' "$description" | rg -q '\p{Han}' ||
        fail "frontmatter description must be Chinese: ${file#$REPO_ROOT/}"
    [[ "$description" != description:\ Use\ when* ]] ||
        fail "English trigger description remains: ${file#$REPO_ROOT/}"
done

for file in "${model_files[@]}"; do
    rg -q '\p{Han}' "$file" ||
        fail "model-readable file contains no Chinese: ${file#$REPO_ROOT/}"

    ! rg -n '红旗' "$file" ||
        fail "literal Red Flags translation remains: ${file#$REPO_ROOT/}"

    if [[ "$file" == *.md ]]; then
        english_headings="$(awk '
            /^```/ { in_fence = !in_fence; next }
            !in_fence && /^#{1,6}[[:space:]]+/ { print FNR ":" $0 }
        ' "$file" | rg -v '\p{Han}' || true)"
        [[ -z "$english_headings" ]] || {
            printf '%s\n' "$english_headings" >&2
            fail "English-only Markdown heading remains: ${file#$REPO_ROOT/}"
        }

        english_prose="$(awk '
            /^```/ { in_fence = !in_fence; next }
            in_fence || /^[[:space:]]*$/ || /^---$/ { next }
            /^name:[[:space:]]/ { next }
            /^[-|:[:space:]]+$/ { next }
            $0 !~ /[一-龥]/ { print FNR ":" $0 }
        ' "$file" || true)"
        [[ -z "$english_prose" ]] || {
            printf '%s\n' "$english_prose" >&2
            fail "English-only prose line remains: ${file#$REPO_ROOT/}"
        }
    fi
done

echo "Chinese skill content checks passed"
