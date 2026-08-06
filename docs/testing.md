# Testing Superpowers

Superpowers has two distinct kinds of verification:

- **`tests/`** — do skill contracts and bundled helper scripts work? Bash + node + python tests cover the workflow, brainstorm companion, debugging helpers, and shell utilities.
- **Behavior evidence** — do fresh-context read-only evaluators follow the intended skill contract? Store the relevant prompts, source hashes, responses, and evidence boundary with the workflow test evidence.

## Local tests

Live in `tests/`. Currently:

- `tests/brainstorm-server/` — node test suite for the brainstorm server JS code.
- `tests/workflow/` — static checks for short-task exit, general long-task specs, evidence profiles, main-agent TDD, and read-only-review authority boundaries. Run with `tests/workflow/run-tests.sh`.
- `tests/systematic-debugging/` and `tests/shell-lint/` — focused helper-script tests.

Run the focused directory test for the area changed. The brainstorm companion has its own Node package under `tests/brainstorm-server/`.

## Skill behavior evidence

Behavior-changing skill edits use paired no-guidance/control and candidate evaluation as required by `writing-skills`. Evaluators are read-only and receive only the task-local scenario and skill sources needed for the comparison. Their evidence does not claim plugin installation, native discovery, or end-to-end behavior for a specific harness.
