# Superpowers

Superpowers is a composable execution methodology for coding agents. It keeps substantial, multi-stage work aligned through one executable spec while letting short tasks finish without process overhead.


## We're Hiring!

We're hiring someone to help out full time with Superpowers community and code work. 
You can read about the job at https://primeradiant.com/jobs/superpowers-community-engineer/
If this sounds like someone you know, definitely send them our way.

## Quickstart

Use the skills directly with [Claude Code](#claude-code) or [Codex](#codex).

## How it works

Short, self-contained work that can be completed and verified in one pass proceeds directly. Substantial work — dependent stages, persistent progress, material uncertainty or risk, cross-context execution, or an explicit request for a plan/spec — uses `using-superpowers` and one executable spec.

The spec owns goal, authority, deliverables, dependency-ordered slices, progress, revision triggers, and completion evidence. It is both the execution constraint and the resume point; no second workflow document is created.

Completion evidence matches the task: research evidence for analysis, artifact or state evidence for writing/migration/operations, and behavior evidence for software changes. Only changed software behavior enters red/green TDD, code review, and branch finishing. Subagents may perform read-only review or evaluation, but they never implement changes.

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

1. **using-superpowers** - Activates for substantial or resumable work, not for short one-pass tasks. It finds or creates the task's single executable spec and routes each slice by its completion evidence.

2. **brainstorming** - Creates the executable spec. Common fields constrain every long task; research evidence, artifact or state evidence, and behavior evidence add only the fields their deliverables require.

3. **execution** - The main agent completes dependency-ready slices. Software behavior uses `test-driven-development`; analysis and other deliverables use the evidence declared by their spec.

4. **verification-before-completion** - Re-checks every slice and final claim against fresh behavior, research, artifact, or state evidence.

5. **software-only completion** - `requesting-code-review` and `finishing-a-development-branch` apply only when software behavior and branch integration require them.

Skills are discovered natively from the linked directories and trigger from their descriptions or explicit invocation. There is no plugin, hook, or session-start bootstrap.

## What's Inside

### Skills Library

**Testing**
- **test-driven-development** - RED-GREEN-REFACTOR cycle (includes testing anti-patterns reference)

**Debugging**
- **systematic-debugging** - 4-phase root cause process (includes root-cause-tracing, defense-in-depth, condition-based-waiting techniques)
- **verification-before-completion** - Verify software, research, artifacts, and state against declared evidence

**Collaboration** 
- **brainstorming** - Executable specifications for substantial work
- **requesting-code-review** - Read-only independent review
- **receiving-code-review** - Responding to feedback
- **finishing-a-development-branch** - Merge/PR decision workflow

**Meta**
- **writing-skills** - Create new skills following best practices (includes testing methodology)
- **using-superpowers** - Long-task routing, execution constraints, and resume workflow

## Philosophy

- **Test-Driven Development** - Write tests first, always
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

## Visual companion telemetry

Because skills don't provide any feedback to creators, we have no idea how many of you are using Superpowers. By default, the Prime Radiant logo on brainstorming's optional visual companion feature is loaded from our website. It includes the version of Superpowers in use. It does not include any details about your project, prompt, or coding agent. We don't see your clicks or anything about what you're building. This helps us have a rough idea of how many folks are using Superpowers and which version of Superpowers they're using. It's 100% optional. To disable this, set the environment variable `SUPERPOWERS_DISABLE_TELEMETRY` to any true value. Superpowers also honors Claude Code's `DISABLE_TELEMETRY` and `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` opt-outs.

## Community

Superpowers is built by [Jesse Vincent](https://blog.fsck.com) and the rest of the folks at [Prime Radiant](https://primeradiant.com).

- **Discord**: [Join us](https://discord.gg/35wsABTejz) for community support, questions, and sharing what you're building with Superpowers
- **Issues**: https://github.com/obra/superpowers/issues
- **Release announcements**: [Sign up](https://primeradiant.com/superpowers/) to get notified about new versions
