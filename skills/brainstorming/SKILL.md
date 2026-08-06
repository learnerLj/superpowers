---
name: brainstorming
description: Use when a substantial task needs an executable specification before work begins or resumes, especially when the goal, authority, deliverables, evidence, boundaries, or execution stages require decisions
---

# Brainstorming Executable Specifications

## Overview

Turn substantial work into one executable spec that preserves intent, constrains execution, records progress, and defines proof of completion. Scale the spec to the decision surface rather than forcing every task into a software-development shape.

<HARD-GATE>
Do not begin a substantial task's execution until its goal, authority, deliverables, execution slices, completion evidence, and revision triggers are explicit in one spec. This gate applies only after this skill has correctly triggered; short self-contained tasks do not need a spec.
</HARD-GATE>

<LANGUAGE-HARD-GATE>
Before drafting a spec, lock one primary narrative language using this precedence: direct human-partner request, authoritative project language rule, established language of an existing spec, then Chinese by default.

If the human partner is discussing the request in Chinese and no higher-priority rule requires another language, write the entire spec in Chinese. Localize headings, prose, acceptance criteria, evidence descriptions, and slice labels. Keep only required technical literals such as identifiers, API fields, commands, paths, and exact errors in their original form. English labels in a Chinese spec are narrative-language drift, not technical literals.

Keep the entire spec in that selected language except for those required technical literals.
</LANGUAGE-HARD-GATE>

## Process

1. **Explore context** - read project authorities, existing artifacts, real entry points, consumers, and recent relevant work.
2. **Offer the visual companion just-in-time** - only when the current question would genuinely be clearer shown than described. If no visual question arises, never offer it.
3. **Find an existing spec** - revise or resume it when it still owns the same goal; do not fork a second execution outline.
4. **Resolve material decisions** - ask only questions whose answers change scope, authority, deliverables, evidence, risk, or execution order. Do not force questions when the human partner already made the choice.
5. **Compare approaches when needed** - present alternatives only for a real decision. Lead with the recommendation and trade-offs.
6. **Select completion evidence** - assign behavior evidence, research evidence, artifact or state evidence, or an explicit combination.
7. **Write the executable spec** - use the common contract and only the profile fields that apply.
8. **Self-review** - remove placeholders, contradictions, ambiguity, unsupported assumptions, scope drift, and narrative-language drift.
9. **Review substantial risk** - use a read-only reviewer for cross-component, high-risk, or downstream-critical specs.
10. **Apply the profile's execution gate** - for non-software work, follow the human partner's wait-or-continue instruction after required review. For behavior-evidence software work, begin only after written spec approval or valid complete-design pre-authorization, then create the approved-spec commit and record `BASE_SHA` before production changes.

## Executable Spec Contract

The spec is the single persistent execution outline. A capable agent with no conversation history must be able to resume it without inventing the goal, authority, next step, or definition of done.

Every substantial spec contains:

1. **Goal and non-goals** - observable outcome and explicit exclusions.
2. **Current state and authority** - actual starting state, priority rules, existing artifacts, and resume location.
3. **Deliverables** - files, reports, code, data, or external state, with their owners and consumers.
4. **Execution and data flow** - how inputs become deliverables; state explicitly when no data or state transformation exists.
5. **Execution slices** - dependency-ordered, outcome-oriented checkpoints.
6. **Completion evidence** - evidence required for every slice and final acceptance.
7. **Revision triggers** - facts or changes that invalidate the current contract.
8. **Final acceptance** - the complete set of claims that must be freshly verified before completion.

Do not create a second workflow document, implementation plan, todo ledger, or progress artifact. The spec owns progress as well as scope.

### Execution Slices

Each slice uses an unchecked Markdown progress marker in the approved baseline and contains meanings rendered in the spec's selected language:

- **Outcome:** observable result when the slice is complete.
- **Depends on:** prerequisite slice IDs, or `None`.
- **Work scope:** affected artifacts, systems, sources, or responsibility boundaries.
- **Inputs and authority:** required starting evidence and governing sources.
- **Deliverables:** exact artifacts or state produced by the slice.
- **Completion evidence:** fresh evidence that proves the outcome.
- **Verification or review gate:** required checks and read-only review, or `None`.

Mark a slice complete only after its declared evidence exists and is locatable. If later work changes its inputs, deliverables, or evidence, reopen the slice and verify it again.

## Completion Evidence Profiles

### Behavior Evidence

Use for changed software behavior. In addition to the common contract, define:

- **Target files** and each file's responsibility;
- **System composition and data flow**;
- **Interfaces and boundary contracts** including exact names, signatures, schemas, state transitions, validation, and errors;
- **Implementation Slices** with software-specific files and data decisions;
- **Acceptance criteria** with observable success and failure cases;
- **Test mapping** from each criterion to a test file, scenario, and focused verification command;
- migration, compatibility, rollout, and rollback, or an explicit statement that none applies.

Each software **Implementation Slice** additionally contains:

- **Files:** exact files expected to be created, modified, or deleted;
- **Data decisions:** structures and transformations owned by the slice, or an explicit no-change statement;
- **Acceptance criteria:** exact criterion IDs proved by the slice;
- **Focused verification:** exact commands for the slice's direct behavior;
- **Broader verification:** the smallest downstream or integration commands required by the changed contract;
- **Review gate:** a distinct read-only review requirement for cross-component, risky, or downstream-critical work, otherwise `None`.

Name the canonical owner and representation for every changed business fact. Describe relationships as containment, reference, derivation, projection, or justified duplication. Treat same-shape DTOs, commands, entities, models, state objects, and wrappers as one structure unless a real boundary justifies separation. For every transformation, identify source, target, owner, information added or removed, and the boundary reason.

The main agent invokes `test-driven-development` for these slices. Cross-component, risky, or downstream-critical behavior uses read-only spec/code review. Completed software behavior proceeds through `verification-before-completion` and, when branch integration applies, `finishing-a-development-branch`.

### Research Evidence

Use for analysis and research. In addition to the common contract, define:

- core questions and explicit exclusions;
- known facts, hypotheses, and unknowns;
- source and authority priority;
- evidence thresholds and coverage boundaries;
- collection, extraction, comparison, and synthesis methods;
- independent corroboration, contradiction, and counter-evidence handling;
- output labels for verified fact, inference, NOT VERIFIED, and unresolved uncertainty.

Human research and judgment do not use TDD. If a slice creates or changes reusable software behavior for collection or analysis, apply TDD to that slice only. Conclusions are complete only when the declared evidence exists and the report does not exceed it.

### Artifact or State Evidence

Use for writing, data organization, configuration, migration, operations, and other long deliverables. In addition to the common contract, define:

- target artifact or before/after state;
- allowed side effects and protected state;
- completeness, format, semantic, or consumer checks;
- rollback, recovery, or provenance evidence when relevant;
- downstream acceptance and unchanged behavior.

Only slices that change software behavior use test-driven-development. Other slices use the checks declared by their artifact or state contract.

### Mixed Work

A spec may combine profiles. Assign completion evidence per slice. Do not classify an entire analysis, migration, or writing task as software implementation merely because one slice uses code.

## Approval and Direct Execution

- If the human partner says **plan first**, **spec only**, **show me before execution**, or equivalent, wait for approval after writing and reviewing the spec.
- For non-software profiles, if the human partner authorizes direct execution, **continue**, **do not stop**, or equivalent, begin the first dependency-ready slice after spec self-review and any required independent review.
- Behavior-evidence software work requires either written spec approval or explicit implementation pre-authorization after the human partner reviewed the complete design. Before production changes, commit the final approved spec separately and record that commit as `BASE_SHA`; implementation, review, and final diff verification use this approved-spec baseline. Pre-authorization is invalid if the final spec adds a material decision that the reviewed design did not contain.
- If higher-priority project instructions require an approval or safety gate, obey them regardless of the general execution instruction.

Changing the goal, authority, deliverables, evidence profile, risk boundary, acceptance criteria, or slice outcome is a semantic spec change. Stop, revise the spec, perform the required review, and obtain approval when the governing instruction requires it.

## Visual Companion

The bundled browser companion is an optional tool for mockups, diagrams, spatial relationships, and visual comparisons. Offer it only when the current decision is materially easier to understand visually, and make that offer in its own message. Do not offer it for text-only requirements, trade-offs, or technical decisions.

If the human partner accepts, read `visual-companion.md` before starting the server or creating a screen. Decide separately for each later question whether the browser adds value; acceptance does not turn the whole session into a visual workflow.

## Review

For substantial or cross-cutting specs, dispatch a read-only reviewer using `spec-document-reviewer-prompt.md`. The reviewer reports gaps and contradictions but does not edit files, execute task slices, implement fixes, or commit changes. The main agent applies valid findings and repeats review until no blocking issue remains.

## After the Spec

- Keep the spec at the project-authorized location; otherwise default to `docs/superpowers/specs/YYYY-MM-DD-<topic>-spec.md`.
- Execute only dependency-ready slices.
- Update a progress marker only after fresh completion evidence exists.
- Use specialist skills only when their own triggers apply.
- Finish by invoking `verification-before-completion` against the spec's declared evidence.
