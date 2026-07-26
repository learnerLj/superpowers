---
name: requesting-code-review
description: Use when completing tasks, implementing major features, or before merging to verify work meets requirements
---

# Requesting Code Review

Dispatch a read-only reviewer subagent to catch issues without delegating implementation. The reviewer gets the approved executable spec and diff — never your session's history.

**Core principle:** Review early, review often.

## When to Request Review

**Mandatory:**
- After completing major feature
- Before merge to main

**Optional but valuable:**
- When stuck (fresh perspective)
- Before refactoring (baseline check)
- After fixing complex bug

## How to Request

**1. Establish the review baseline:**

The approved spec commit is the required baseline. Review the full current
working tree from that commit so committed, staged, and unstaged implementation
changes are all in scope.

```bash
BASE_SHA=<approved-spec-commit>
git status --short
git diff --stat "$BASE_SHA"
git diff "$BASE_SHA"
```

List untracked implementation files explicitly in the reviewer context because
Git does not include their contents in a normal diff.

**2. Run pre-review verification:**

Run the focused tests for the changed behavior plus the relevant broader suite.
Record the exact commands, exit codes, and failure counts as verification
evidence. Do not ask the reviewer to infer test status or mutate the checkout by
running the implementation workflow.

**3. Dispatch a read-only reviewer subagent:**

Dispatch a `general-purpose` subagent, filling the template at [code-reviewer.md](code-reviewer.md)

The reviewer MUST NOT edit files, run implementation tasks, or commit changes. It returns findings only; the main agent evaluates and implements valid fixes through TDD.

**Placeholders:**
- `{DESCRIPTION}` - Brief summary of what you built
- `{APPROVED_SPEC}` - The approved executable spec path and content
- `{BASE_SHA}` - Approved-spec baseline commit
- `{UNTRACKED_FILES}` - Untracked implementation files, or `None`
- `{VERIFICATION_EVIDENCE}` - Exact commands and fresh results

**4. Act on feedback:**
- Fix Critical issues immediately
- Fix Important issues before proceeding
- Note Minor issues for later
- Push back if reviewer is wrong (with reasoning)
- For every valid code finding, reproduce it with a failing test and fix it in the main session
- Re-run verification after fixes and repeat the review until no Critical or Important issues remain

## Example

```
[Just completed the approved spec in the working tree]

You: Let me request code review before proceeding.

BASE_SHA=$(git rev-parse HEAD) # approved spec was committed here
git status --short
git diff "$BASE_SHA"

[Run focused tests and the relevant broader suite]

[Dispatch read-only code reviewer subagent]
  DESCRIPTION: Added verifyIndex() and repairIndex() with 4 issue types
  APPROVED_SPEC: docs/superpowers/specs/deployment-spec.md at BASE_SHA
  BASE_SHA: a7981ec
  UNTRACKED_FILES: None
  VERIFICATION_EVIDENCE: npm test -- indexer.test.ts (18 passed); npm test (142 passed)

[Read-only reviewer returns]:
  Strengths: Clean architecture, real tests
  Issues:
    Important: Missing progress indicators
    Minor: Magic number (100) for reporting interval
  Assessment: Ready to proceed

You: [Evaluate the finding, add a failing test, fix it in the main session, verify, and repeat review]
```

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "I'll just review the diff myself instead of dispatching a reviewer" | Independent review catches assumptions the implementing session may miss. Dispatch a read-only reviewer and keep all edits in the main session. |
| "The reviewer needs my whole session history to understand the change" | Hand it precisely crafted context, never your session's history. That keeps the reviewer on the work product, not your thought process. |
| "The reviewer can fix this small issue directly" | Review and implementation have separate authority. The reviewer reports; the main agent reproduces the issue with a failing test and fixes it. |

## Red Flags

**Never:**
- Skip review because "it's simple"
- Ignore Critical issues
- Proceed with unfixed Important issues
- Argue with valid technical feedback
- Let a reviewer edit files, implement fixes, or commit changes

**If reviewer wrong:**
- Push back with technical reasoning
- Show code/tests that prove it works
- Request clarification

See template at: [code-reviewer.md](code-reviewer.md)
