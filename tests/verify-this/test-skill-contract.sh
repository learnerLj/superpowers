#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
SKILL_FILE="$REPO_ROOT/skills/verify-this/SKILL.md"

fail() {
    echo "FAIL: $*" >&2
    exit 1
}

assert_contains() {
    local expected="$1"
    local description="$2"

    grep -Fq -- "$expected" "$SKILL_FILE" || fail "$description"
}

assert_absent() {
    local forbidden="$1"
    local description="$2"

    ! grep -Fq -- "$forbidden" "$SKILL_FILE" || fail "$description"
}

[[ -f "$SKILL_FILE" ]] || fail "verify-this skill entrypoint is missing"

assert_contains "用户明确要求验证" \
    "skill 必须拥有用户主动提出的 claim verification 场景"
assert_contains "verification-before-completion" \
    "skill 必须与自动完成门槛划清边界"
assert_contains "事实 authority" \
    "验证必须从拥有该事实的 authority 取证"
assert_contains "状态型声明" \
    "skill 必须支持状态验证"
assert_contains "不要求人为制造旧状态或 treatment" \
    "状态型声明不得强制 baseline/treatment"
assert_contains "因果或比较型声明" \
    "skill 必须支持因果或比较验证"
assert_contains '比较 `baseline` 与 `treatment`' \
    "只有因果或比较型声明才要求同条件对照"
assert_contains "完成型声明" \
    "skill 必须支持逐项完成验证"
assert_contains "事实型声明" \
    "skill 必须支持 owner/authority 事实验证"
assert_contains "通过条件" \
    "verdict 必须依据声明自己的通过条件"
assert_contains "VERIFIED" \
    "skill 必须保留 VERIFIED verdict"
assert_contains "NOT VERIFIED" \
    "skill 必须保留 NOT VERIFIED verdict"
assert_contains "INCONCLUSIVE" \
    "skill 必须保留 INCONCLUSIVE verdict"
assert_contains "计划、描述或文件存在" \
    "skill 必须拒绝把意图或存在性当作完成证据"

assert_absent "control-cli" \
    "skill 不得绑定不存在于所有 harness 的 CLI 工具名"
assert_absent "control-ui" \
    "skill 不得绑定不存在于所有 harness 的 UI 工具名"
assert_absent "/tmp/verify-this" \
    "skill 不得默认要求固定临时 artifact 目录"

echo "verify-this contract checks passed"
