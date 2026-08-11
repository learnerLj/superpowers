#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
SKILL_FILE="$REPO_ROOT/skills/writing-skills/SKILL.md"
REVIEWER_GUIDE="$REPO_ROOT/skills/writing-skills/testing-skills-with-reviewers.md"
ANTHROPIC_GUIDE="$REPO_ROOT/skills/writing-skills/anthropic-best-practices.md"
PERSUASION_GUIDE="$REPO_ROOT/skills/writing-skills/persuasion-principles.md"
CONTRIBUTOR_GUIDE="$REPO_ROOT/CLAUDE.md"
PR_TEMPLATE="$REPO_ROOT/.github/PULL_REQUEST_TEMPLATE.md"

fail() {
    echo "FAIL: $*" >&2
    exit 1
}

assert_contains() {
    local file="$1"
    local expected="$2"
    local description="$3"

    grep -Fq -- "$expected" "$file" || fail "$description"
}

assert_absent() {
    local file="$1"
    local forbidden="$2"
    local description="$3"

    ! grep -Fq -- "$forbidden" "$file" || fail "$description"
}

assert_file_absent() {
    local file="$1"
    local description="$2"

    [[ ! -e "$file" ]] || fail "$description"
}

assert_max_lines() {
    local file="$1"
    local maximum="$2"
    local description="$3"
    local actual

    actual="$(wc -l < "$file")"
    (( actual <= maximum )) || fail "$description: expected <= $maximum, got $actual"
}

assert_max_lines "$SKILL_FILE" 160 \
    "writing-skills 入口必须保持为少量方向和高频错误"
assert_file_absent "$PERSUASION_GUIDE" \
    "writing-skills 不应保留与核心 authoring 无关的说服原则文章"
assert_absent "$SKILL_FILE" \
    "persuasion-principles.md" \
    "writing-skills 入口不应引用说服原则旁支"
assert_contains "$SKILL_FILE" \
    "默认 agent 已经足够聪明" \
    "writing-skills 必须明确只补充非显然指导"

assert_contains "$SKILL_FILE" \
    "默认只运行一对 fresh-context 样本：1 次 RED control + 1 次 GREEN candidate" \
    "writing-skills 必须把一对 RED/GREEN 样本设为默认验证范围"
assert_contains "$SKILL_FILE" \
    "只有观察到实际输出方差" \
    "writing-skills 必须以实际方差作为增加重复次数的前提"
assert_contains "$SKILL_FILE" \
    '不得展开 `fixture × candidate × wording × repeat` 全矩阵' \
    "writing-skills 必须禁止未经裁剪的组合评测矩阵"
assert_contains "$SKILL_FILE" \
    "总 evaluator 调用预算" \
    "writing-skills 必须要求多 skill 或多候选任务预设总调用预算"
assert_contains "$SKILL_FILE" \
    "新增调用会改变哪个具体决策" \
    "writing-skills 必须用决策价值约束评测扩展"
assert_contains "$SKILL_FILE" \
    "只重跑被修改规则直接影响的场景" \
    "writing-skills 必须限制回归重跑范围"
assert_absent "$SKILL_FILE" \
    "每个措辞变体至少 5 次" \
    "writing-skills 不得再把五次重复设为所有措辞变体的默认要求"
assert_absent "$SKILL_FILE" \
    "5+ 次微测" \
    "writing-skills checklist 不得保留无条件五次微测"
assert_absent "$SKILL_FILE" \
    "先写测试场景，让 fresh-context 只读 evaluator" \
    "writing-skills 概述不得把 evaluator 场景设为所有修改的通用入口"
assert_contains "$SKILL_FILE" \
    "若修改行为塑造措辞，已完成默认的 1 次 control + 1 次 candidate" \
    "writing-skills 只应对行为塑造修改要求 paired evaluator"
assert_contains "$CONTRIBUTOR_GUIDE" \
    'Run one fresh-context control/candidate pair; add adversarial pressure only when `writing-skills` requires more samples' \
    "contributor evaluation policy must match the writing-skills budget"
assert_absent "$CONTRIBUTOR_GUIDE" \
    "Run adversarial pressure testing across multiple sessions" \
    "contributor guide must not require unconditional pressure testing"
assert_contains "$PR_TEMPLATE" \
    'completed one fresh-context control/candidate pair' \
    "PR template must require the default paired evaluation"
assert_contains "$PR_TEMPLATE" \
    'added adversarial pressure only when `writing-skills` required more samples' \
    "PR template pressure testing must follow the writing-skills expansion gate"
assert_contains "$REVIEWER_GUIDE" \
    "GREEN 已通过且没有观察到新违规时停止" \
    "reviewer 指南必须在没有新失败时停止继续迭代"

assert_absent "$SKILL_FILE" \
    'frontmatter 必须包含 `name` 与 `description`，总长度不超过 1024 字符' \
    "writing-skills 不得把 name 与 description 的长度限制错误合并"
assert_contains "$SKILL_FILE" \
    '`name` 为 1-64 字符' \
    "writing-skills 必须记录 name 的独立长度约束"
assert_contains "$SKILL_FILE" \
    '`description` 为 1-1024 字符' \
    "writing-skills 必须记录 description 的独立长度约束"
assert_contains "$SKILL_FILE" \
    "说明 skill 做什么以及何时使用" \
    "writing-skills 必须让 description 同时拥有能力与触发范围"
assert_contains "$SKILL_FILE" \
    "审计 skill 目录中的全部文件" \
    "writing-skills 必须覆盖 bundled files 的安全审计"

assert_contains "$ANTHROPIC_GUIDE" \
    "最后核对：2026-08-08" \
    "Anthropic 最佳实践摘要必须标记核对日期"
assert_contains "$ANTHROPIC_GUIDE" \
    "Agent Skills 开放规范" \
    "Anthropic 最佳实践摘要必须区分可移植规范 authority"
assert_contains "$ANTHROPIC_GUIDE" \
    "Codex 专属" \
    "Anthropic 最佳实践摘要必须区分 Codex 专属字段"
assert_contains "$ANTHROPIC_GUIDE" \
    "像安装软件一样" \
    "Anthropic 最佳实践摘要必须包含当前安全边界"
assert_absent "$ANTHROPIC_GUIDE" \
    "至少建立三个 evaluation" \
    "Anthropic 最佳实践摘要不得无条件要求三个 evaluation"

assert_contains "$REVIEWER_GUIDE" \
    "可观察缺口" \
    "reviewer 指南必须从可观察缺口选择评测方法"
assert_contains "$REVIEWER_GUIDE" \
    "INCONCLUSIVE" \
    "reviewer 指南必须允许证据不足时停止"
assert_contains "$REVIEWER_GUIDE" \
    "Meta-test 只提供诊断线索" \
    "reviewer 指南不得把 meta-test 当作完成证据"
assert_absent "$REVIEWER_GUIDE" \
    "最佳测试至少叠加三类压力" \
    "reviewer 指南不得把三重压力设为通用要求"
assert_absent "$REVIEWER_GUIDE" \
    "最大压力下 agent 仍选择正确选项" \
    "reviewer 指南不得把最大压力设为通用完成标准"

echo "writing-skills evaluation budget contract checks passed"
