# Superpowers

Superpowers is a composable execution methodology for coding agents. It keeps substantial, multi-stage work aligned through one executable spec while letting short tasks finish without process overhead.


## We're Hiring!

We're hiring someone to help out full time with Superpowers community and code work. 
You can read about the job at https://primeradiant.com/jobs/superpowers-community-engineer/
If this sounds like someone you know, definitely send them our way.

## Quickstart

Use the skills directly with [Claude Code](#claude-code) or [Codex](#codex).

## How it works

Short, self-contained work that can be completed and verified in one pass proceeds directly. Substantial work — dependent stages, persistent progress, material uncertainty or risk, cross-context execution, or an explicit request for brainstorming or a plan/spec — invokes `brainstorming` to create or resume one executable spec.

The spec owns goal, authority, deliverables, dependency-ordered slices, progress, revision triggers, a criterion-to-Oracle verification contract, and completion evidence. It is both the execution constraint and the resume point; no second workflow document is created.

Completion evidence matches the task: research evidence for analysis, artifact or state evidence for writing/migration/operations, and behavior evidence for software changes. Changed software behavior enters red/green TDD; code review is mandatory for major or high-risk changes and before merging software changes, and optional when its expected value exceeds its cost. Subagents may perform read-only review or evaluation, but they never implement changes.

## Commercial Services

If you're using Superpowers in enterprise and could benefit from commercial support, additional tooling, or managed spending, please don't hesitate to drop us a line at sales@primeradiant.com.

## Installation

Superpowers is a skills library, not a plugin. Clone the repository, then link each skill into the native user-level skills directory of the harness you use.

### Claude Code

Link the repository's skill directories into Claude Code's native user skills directory:

```bash
mkdir -p "$HOME/.claude/skills"
for skill in /absolute/path/to/superpowers/skills/*; do
  [ -d "$skill" ] || continue
  ln -sfn "$skill" "$HOME/.claude/skills/$(basename "$skill")"
done
```

Restart Claude Code after adding or updating links.

### Codex

Link the same skill directories into Codex's native shared skills directory:

```bash
mkdir -p "$HOME/.agents/skills"
for skill in /absolute/path/to/superpowers/skills/*; do
  [ -d "$skill" ] || continue
  ln -sfn "$skill" "$HOME/.agents/skills/$(basename "$skill")"
done
```

Restart Codex after adding or updating links. No session hook or startup prompt is installed.

## The Basic Workflow

1. **brainstorming** - Activates for substantial or resumable work and creates or resumes the single executable spec. Common fields constrain every long task; research evidence, artifact or state evidence, and behavior evidence add only the fields their deliverables require.

2. **execution** - The main agent completes dependency-ready slices. Software behavior uses `test-driven-development` and risk-based read-only code review; analysis and other deliverables use the evidence declared by their spec.

3. **verification-before-completion** - Re-checks every slice and final claim against fresh behavior, research, artifact, or state evidence.

Skills are discovered natively from the linked directories and trigger from their descriptions or explicit invocation. There is no plugin, hook, or session-start bootstrap.

## What's Inside

### Skills Library

**Testing**
- **test-driven-development** - RED-GREEN-REFACTOR cycle (includes testing anti-patterns reference)

**Debugging**
- **systematic-debugging** - 4-phase root cause process (includes root-cause-tracing, defense-in-depth, condition-based-waiting techniques)
- **verification-before-completion** - Verify software, research, artifacts, and state against declared evidence
- **verify-this** - Verify a user-specified claim against fresh authority evidence and return an explicit verdict

**Code Quality**
- **code-simplification-review** - Evidence-based review for deletable complexity, ownership mistakes, wrapper/layer sprawl, and maintainability regressions

**Code Understanding**
- **code-path-explainer** - Trace a line or execution path through callers, state changes, side effects, owners, and consumers with file-line evidence

**Collaboration** 
- **brainstorming** - Long-task routing, executable specifications, and resume workflow
- **requesting-code-review** - Read-only independent review
- **receiving-code-review** - Responding to feedback

**Meta**
- **writing-skills** - Create new skills following best practices (includes testing methodology)

## Philosophy

- **Test-Driven Development** - Write tests first for changed software behavior
- **Systematic over ad-hoc** - Process over guessing
- **Complexity reduction** - Simplicity as primary goal
- **Evidence over claims** - Verify before declaring success

Read [the original release announcement](https://blog.fsck.com/2025/10/09/superpowers/).

## Contributing

The general contribution process for Superpowers is below. Keep in mind that we don't generally accept contributions of new skills and that updates must preserve the documented skill contracts in Claude Code and Codex.

1. Fork the repository
2. Switch to the 'dev' branch
3. Create a branch for your work
4. Follow the `writing-skills` skill for creating and testing new and modified skills
5. Submit a PR, being sure to fill in the pull request template.

Skill-behavior changes require paired control/candidate evidence from fresh-context read-only evaluators. Local skill and helper tests live at `tests/`.

See `skills/writing-skills/SKILL.md` for the complete guide.

## Updating

Superpowers updates are somewhat coding-agent dependent, but are often automatic.

## License

MIT License - see LICENSE file for details

## Community

Superpowers is built by [Jesse Vincent](https://blog.fsck.com) and the rest of the folks at [Prime Radiant](https://primeradiant.com).

- **Discord**: [Join us](https://discord.gg/35wsABTejz) for community support, questions, and sharing what you're building with Superpowers
- **Issues**: https://github.com/obra/superpowers/issues
- **Release announcements**: [Sign up](https://primeradiant.com/superpowers/) to get notified about new versions
