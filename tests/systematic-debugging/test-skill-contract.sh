#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
SKILL_DIR="$REPO_ROOT/skills/systematic-debugging"
SKILL_FILE="$SKILL_DIR/SKILL.md"

fail() {
  echo "[FAIL] $1" >&2
  exit 1
}

assert_contains() {
  local file="$1"
  local expected="$2"
  local description="$3"

  grep -Fq -- "$expected" "$file" || fail "$description"
}

assert_not_present() {
  local path="$1"
  local description="$2"

  [ ! -e "$path" ] || fail "$description"
}

assert_no_match() {
  local pattern="$1"
  local description="$2"

  if grep -RInE -- "$pattern" "$SKILL_DIR"; then
    fail "$description"
  fi
}

assert_not_present "$SKILL_DIR/find-polluter.sh" \
  "systematic-debugging 不应携带绑定 npm 的测试扫描脚本"
assert_not_present "$SKILL_DIR/condition-based-waiting-example.ts" \
  "systematic-debugging 不应携带 Lace 项目的 TypeScript 示例"

assert_no_match 'ThreadManager|LaceEvent|npm test|codesign|Project\.create|git init' \
  "systematic-debugging 不应保留原项目专属实现或命令"

assert_contains "$SKILL_FILE" "test-driven-development" \
  "入口必须链接软件修复流程"
assert_contains "$SKILL_FILE" "requesting-code-review" \
  "入口必须链接代码审查流程"
assert_contains "$SKILL_FILE" "receiving-code-review" \
  "入口必须链接 review 反馈处理流程"
assert_contains "$SKILL_FILE" "verification-before-completion" \
  "入口必须链接完成前验证流程"
assert_contains "$SKILL_FILE" "root-cause-tracing.md" \
  "入口必须链接根因追踪方法"
assert_contains "$SKILL_FILE" "defense-in-depth.md" \
  "入口必须链接纵深防御方法"
assert_contains "$SKILL_FILE" "condition-based-waiting.md" \
  "入口必须链接条件等待方法"

echo "systematic-debugging contract checks passed"
