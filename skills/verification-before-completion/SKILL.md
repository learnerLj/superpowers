---
name: verification-before-completion
description: Use when about to claim a task, fix, analysis, deliverable, migration, or implementation is complete, correct, or passing, before committing, publishing, handing off, or ending the work
---

# Verification Before Completion

## Overview

**Core principle:** Evidence before claims, always.

## The Iron Law

```
NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE
```

The approved spec owns the declared completion evidence. For a short task without a spec, identify the direct observation or command that proves the claim.

## Gate Function

Before claiming completion:

1. **IDENTIFY** the exact claim and its required evidence.
2. **RUN or INSPECT** the complete verification now.
3. **READ** the full result, including exit status, failure count, missing coverage, and unresolved uncertainty.
4. **COMPARE** the evidence with the spec, not with confidence or prior output.
5. **REPORT** the verified result and any remaining gap.

If evidence is stale, partial, indirect, or missing, the claim is not verified.

## Declared Completion Evidence

### Behavior evidence

For changed software behavior:

- map every acceptance criterion to a fresh test or direct behavioral check;
- run the relevant test, build, lint, format, and integration commands declared by the spec;
- inspect the final diff and intended unchanged behavior;
- verify important review fixes again;
- do not substitute compilation for semantic contract coverage.

### Research evidence

For analysis and research:

- verify required source coverage and authority priority;
- inspect the actual collected artifacts, not a summary of them;
- check corroboration, contradictory evidence, and evidence boundaries;
- distinguish verified fact, inference, NOT VERIFIED, and unresolved uncertainty;
- confirm the final report does not claim more than the evidence supports.

### Artifact or state evidence

For writing, data work, configuration, migration, operations, or other deliverables:

- inspect the target artifact or before/after state;
- run declared format, completeness, semantic, consumer, and provenance checks;
- verify protected or unchanged state remains intact;
- exercise rollback or recovery when the spec requires it;
- confirm every downstream acceptance condition.

For mixed work, verify each slice using its assigned evidence profile.

## Requirements Verification

Re-read the approved spec line by line. A checked progress marker is not evidence by itself. Confirm that each slice has fresh, locatable evidence and reopen any slice affected by later work.

Reviewer findings are evidence inputs, not authority:

```
Reviewer reports issue -> reproduce against spec/artifact -> verify -> main agent fixes
```

Never let a reviewer implement changes or trust an unsupported finding.

## Completion Handoff

Only behavior-evidence software work continues to finishing-a-development-branch. Before that handoff:

1. Re-read the approved software spec and verify every acceptance criterion.
2. Run the full relevant verification on the current tree.
3. Inspect the final diff and confirm only intended changes remain.
4. Commit only when the human partner or governing workflow authorizes it.
5. Invoke `finishing-a-development-branch` only for an actual branch-integration decision.

Research evidence and artifact or state evidence end with their declared report, artifact, state, or handoff. They do not require a code commit or development-branch workflow unless a software slice independently requires one.

Any change after verification invalidates the affected evidence. Re-run the relevant checks before claiming completion.

## Red Flags

- “should”, “probably”, or “seems to” used as a success claim;
- relying on a previous run;
- treating a reviewer or subagent report as proof;
- extrapolating a partial check to the whole task;
- treating source count as research quality without inspecting coverage;
- treating file existence as semantic correctness;
- treating tests as proof of analysis conclusions;
- ending because the task is long or the context is nearly full.

When any red flag appears, identify the missing evidence and verify it before proceeding.
