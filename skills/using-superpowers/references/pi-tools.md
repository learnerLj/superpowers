# Pi Tool Mapping

Skills speak in actions such as "dispatch a read-only reviewer or evaluator" and "read a file". On Pi these resolve to the tools below.

| Action skills request | Pi equivalent |
| --- | --- |
| Dispatch a read-only reviewer or evaluator (`Subagent (general-purpose):` template) | Use an installed subagent tool such as `subagent` from `pi-subagents` if available |

## Subagents

Pi core does not ship a standard subagent tool. If `pi-subagents` is installed, use it only for read-only spec/code review or skill-behavior evaluation. These agents return findings or sampled responses and never edit or implement. If it is unavailable, work in the main session instead of fabricating `Task` calls.
