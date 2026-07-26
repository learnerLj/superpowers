---
name: finishing-a-development-branch
description: Use when implementation is complete, all tests pass, and you need to decide how to integrate the work
---

# Finishing a Development Branch

## Overview

**Core principle:** Verify tests, detect branch state, present integration choices, and execute only the user's choice.

**Announce at start:** "I'm using the finishing-a-development-branch skill to complete this work."

## Step 1: Verify Tests

Run the project's full test suite on the exact tree being integrated.

If tests fail, report the failures and stop. Do not present integration options until the suite is green.

## Step 2: Confirm The Integration Snapshot

```bash
git status --short
```

The implementation must already be committed by the main agent after final
verification. If intended implementation changes remain, stop and return to
verification and commit. Never sweep unrelated user changes into that commit.

## Step 3: Detect Branch State

```bash
BRANCH=$(git branch --show-current)
HEAD_SHA=$(git rev-parse HEAD)
```

- Named branch: all three integration options are available.
- Detached HEAD: local merge is unavailable; offer push-as-new-branch or keep as-is.

## Step 4: Confirm Base Branch

Resolve the base from the conversation, branch upstream, or merge base. If it is still ambiguous, ask the user to confirm before merging or opening a pull request.

## Step 5: Present Options

**Named branch:**

```text
Implementation complete. What would you like to do?

1. Merge back to <base-branch> locally
2. Push and create a Pull Request
3. Keep the branch as-is

Which option?
```

**Detached HEAD:**

```text
Implementation complete. You're on a detached HEAD.

1. Push as a new branch and create a Pull Request
2. Keep as-is

Which option?
```

Wait for the user's answer. Discard is never a menu option.

## Step 6: Execute The Choice

### Option 1: Merge Locally

```bash
git checkout <base-branch>
git pull --ff-only
git merge <feature-branch>
<full test command>
```

If the merged result fails, stop and report the failure. Do not delete the feature branch.

When the merged result is green:

```bash
git branch -d <feature-branch>
```

### Option 2: Push And Create A Pull Request

```bash
git push -u origin <feature-branch>
# Detached HEAD:
# git push origin HEAD:refs/heads/<new-branch>
```

Create the pull request against the confirmed base branch using the repository template and conventions. Report the URL.

### Option 3: Keep As-Is

Report the branch name and current commit. Make no repository changes.

### Explicit Discard Request

Discard only when the user explicitly asks to throw the branch away. Show the exact branch and commits, then require the exact confirmation word `discard`.

After confirmation:

```bash
git checkout <base-branch>
git branch -D <feature-branch>
```

Never delete untracked files or unrelated branches as part of branch cleanup.

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "Tests passed earlier" | Run the suite on the exact tree being integrated. |
| "They obviously want it merged" | Integration is the user's decision. Present the choices and wait. |
| "Discard would keep things tidy" | Discard is available only after an explicit request and exact confirmation. |
| "The base is obviously main" | Resolve or confirm the real base branch first. |
| "The push was rejected, so force-push" | Investigate remote movement. Force-push requires explicit authorization. |
