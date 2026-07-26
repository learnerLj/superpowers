# Antigravity CLI (`agy`) Tool Mapping

Skills speak in actions such as "dispatch a read-only reviewer or evaluator" and "read a file". On the Antigravity CLI (`agy`) these resolve to the tools below.

| Action skills request | Antigravity CLI equivalent |
|----------------------|----------------------|
| Dispatch a read-only reviewer or evaluator (`Subagent (general-purpose):` template) | `invoke_subagent` with `TypeName: "research"`; never use `self` for implementation |
