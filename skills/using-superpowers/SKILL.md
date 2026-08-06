---
name: using-superpowers
description: Use when starting or resuming a substantial task with dependent stages, material uncertainty or risk, persistent progress, likely context boundary crossings, or when the human partner explicitly requests a plan or specification; not for short one-pass tasks or dispatched read-only reviews and evaluations
---

# Using Superpowers

<READ-ONLY-REVIEWER-STOP>
If you were dispatched as a read-only reviewer or skill-behavior evaluator, perform only the assigned review or evaluation. Do not create, revise, approve, or advance an executable spec; do not edit files, implement fixes, run implementation tasks, or commit changes.
</READ-ONLY-REVIEWER-STOP>

## Overview

Use one executable spec to keep substantial work aligned, resumable, and provable. Let short tasks and narrowly applicable skills proceed without this workflow.

## Short Tasks

A task is short only when it is self-contained, has no material branch decisions, and can be completed and verified in one pass.

For a short task:

- do not invoke `brainstorming` merely to create process;
- do not create a spec, plan, or progress artifact;
- use any directly applicable specialist skill;
- complete the task and verify the result at the task's natural scope.

Examples include a factual answer, one read-only lookup, a simple explanation, or a narrow action whose contract is already explicit. A small software behavior change may still require `test-driven-development`, but it does not automatically require a separate spec.

## Long Tasks

Use this workflow when any observable condition applies:

- the task has dependent stages;
- work needs persistent progress or is likely to cross a context boundary;
- material uncertainty or a later decision can change direction;
- execution combines multiple authorities, sources, datasets, components, or systems;
- side effects, cost, migration, rollback, or other risk require explicit control;
- the human partner explicitly requests a plan or specification.

Before executing a long task:

1. Read the human partner's instructions and the project's authoritative files.
2. Look for an existing approved spec before creating another one.
3. If no usable spec exists, invoke `brainstorming` to create one executable spec.
4. Classify each execution slice by the evidence that proves it complete:
   - **behavior evidence** for changed software behavior;
   - **research evidence** for analysis and research conclusions;
   - **artifact or state evidence** for writing, data work, configuration, migration, operations, and other deliverables.
5. Invoke specialist skills only for the slices where their trigger applies. TDD applies to changed software behavior, not to an entire mixed task merely because one slice uses code.

The executable spec is the single persistent execution outline and progress authority. Do not create a second implementation plan, todo ledger, or parallel status document.

## Resuming Work

On a resumed long task:

1. Re-read the authoritative project instructions and the existing spec.
2. Inspect the declared deliverables and completion evidence instead of trusting conversation memory or checked boxes alone.
3. Reopen any completed slice whose inputs, deliverables, or evidence are stale.
4. Continue from the next dependency-ready slice.
5. Revise the spec before continuing if the goal, authority, deliverables, evidence profile, or risk boundary changed materially.

## Skill Boundaries

- `brainstorming` creates or revises the executable spec for a substantial task.
- `systematic-debugging` diagnoses bugs, test failures, and unexpected behavior whether or not a larger spec exists.
- `test-driven-development` governs slices that change software behavior.
- `requesting-code-review` and `finishing-a-development-branch` remain software-specific.
- `verification-before-completion` checks the completion evidence declared by the spec or, for a short task, the direct claim being made.

### Long Debugging Tasks

A long debugging task uses one mixed-profile spec. Invoke `systematic-debugging` for the diagnostic method. The root-cause slice uses research evidence to preserve reproduction, boundary observations, eliminated hypotheses, and the supported cause; it does not use TDD. If a software fix is required, the fix slice uses behavior evidence and only the fix slice invokes `test-driven-development`. If the evidence shows that no software change is needed, finish with research evidence instead of inventing an implementation slice.

Implementation stays in the main agent's session. Subagents may perform read-only spec/code review or skill-behavior evaluation; they never edit files, implement fixes, run implementation tasks, or commit changes.

## Platform Adaptation

If the current harness needs tool-name mapping, read its reference only when this skill is invoked:

- Codex: `references/codex-tools.md`

## Instruction Priority

Direct human-partner instructions and project authorities such as `AGENTS.md` and `CLAUDE.md` override a task spec. A spec must cite those authorities; it never replaces them.
