## Read-only review and evaluation require multi-agent support

Add to your Codex config (`~/.codex/config.toml`):

```toml
[features]
multi_agent = true
```

This enables `spawn_agent`, `wait_agent`, and `close_agent` for read-only spec/code review and skill-behavior evaluation. These agents return findings or sampled responses only and must be closed when finished. Implementation remains in the main agent session.

## Codex App Finishing

When the sandbox blocks branch/push operations (detached HEAD in an
externally managed checkout), the agent commits all work and informs
the user to use the App's native controls:

- **"Create branch"** — names the branch, then commit/push/PR via App UI
- **"Hand off to local"** — transfers work to the user's local checkout

The agent can still run tests, stage files, and output suggested branch
names, commit messages, and PR descriptions for the user to copy.
