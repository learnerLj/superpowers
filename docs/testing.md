# Testing Superpowers

Superpowers has two distinct kinds of verification:

- **`tests/`** — do skill contracts and bundled helper scripts work? Bash + python tests cover the workflow, debugging contracts, and shell utilities.
- **Behavior evidence** — do fresh-context read-only evaluators follow the intended skill contract? Store relevant prompts, source hashes, responses, and the evidence boundary in the task record or PR description, not as one-off files under `tests/`.

## Local tests

Live in `tests/`. Currently:

- `tests/workflow/` — static checks for short-task exit, general long-task specs, evidence profiles, main-agent TDD, and read-only-review authority boundaries. Run with `tests/workflow/run-tests.sh`.
- `tests/systematic-debugging/` — focused contract checks for the debugging Skill and its supporting methods.
- `tests/shell-lint/` — focused checks for maintained shell scripts.

Run the focused directory test for the area changed.

## Skill behavior evidence

Behavior-changing skill edits use paired no-guidance/control and candidate evaluation as required by `writing-skills`. Evaluators are read-only and receive only the task-local scenario and skill sources needed for the comparison. Their evidence does not claim plugin installation, native discovery, or end-to-end behavior for a specific harness.
