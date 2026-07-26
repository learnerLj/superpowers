# Gemini CLI Tool Mapping

Skills speak in actions such as "dispatch a read-only reviewer or evaluator" and "read a file". On Gemini CLI these resolve to the tools below.

| Action skills request | Gemini CLI equivalent |
|----------------------|----------------------|
| Read a file | `read_file` |
| Read multiple files at once | `read_many_files` |
| Create a new file | `write_file` |
| Edit a file | `replace` |
| Run a shell command | `run_shell_command` |
| Search file contents | `grep_search` |
| Find files by name | `glob` |
| List files and subdirectories | `list_directory` |
| Fetch a URL | `web_fetch` |
| Search the web | `google_web_search` |
| Invoke a skill | `activate_skill` |
| Dispatch a read-only reviewer or evaluator (`Subagent (general-purpose):` template) | `invoke_agent` with `agent_name: "generalist"` (invocable via `@generalist` chat syntax — see [Reviewer support](#reviewer-support)) |

## Instructions file

When a skill mentions "your instructions file", on Gemini CLI this is **`GEMINI.md`**. Gemini CLI loads `GEMINI.md` hierarchically: global at `~/.gemini/GEMINI.md`, project-level files in workspace directories and their ancestors, and sub-directory `GEMINI.md` files when a tool accesses files in those directories.

## Personal skills directory

User-level skills live at **`~/.gemini/skills/`**, with **`~/.agents/skills/`** as a cross-runtime alias (shared with Codex and Copilot CLI). When both directories exist at the same scope, `.agents/skills/` takes precedence. Each skill is a subdirectory containing a `SKILL.md` (with `name` and `description` frontmatter).

## Reviewer support

Gemini CLI dispatches reviewer agents through the `invoke_agent` tool, which takes `agent_name` and `prompt` parameters. The same dispatch is also surfaced as a chat-syntax shortcut: typing `@generalist <prompt>` is equivalent to calling `invoke_agent` with `agent_name: "generalist"`.

Superpowers uses this dispatch only with read-only spec/code review or skill-behavior evaluation prompts:

| Skill dispatch form | Gemini CLI equivalent |
|---------------------|----------------------|
| References a spec or code reviewer prompt | Fill the template, then `invoke_agent` with `agent_name: "generalist"` and the filled prompt |
| Inline read-only review or evaluation prompt | `invoke_agent` with `agent_name: "generalist"` and explicit mutation prohibitions |

### Prompt filling

Fill all placeholders before passing the complete prompt to `invoke_agent`. Reviewer agents return findings only. They must not edit files, write implementation code, run implementation tasks, or commit changes.

## Additional Gemini CLI tools

These tools are unique to Gemini CLI:

| Tool | Purpose |
|------|---------|
| `save_memory` (legacy) | Persist facts across sessions when `experimental.memoryV2 = false` |
| `get_internal_docs` | Look up Gemini CLI's bundled documentation |
| `ask_user` | Pose structured questions to the user (text / single-select / multi-select) |
| `update_topic` | Update the current conversation's topic / strategic-intent metadata |
| `complete_task` | Signal that a Gemini reviewer has completed and return its result to the main agent |
| `read_mcp_resource`, `list_mcp_resources` | MCP resource access |
