import base64
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from urllib.parse import quote


SKILL_DIR = Path(__file__).resolve().parents[1]
SCRIPT = SKILL_DIR / "scripts" / "local_session_inventory.py"
NOW = "2026-08-19T12:00:00+08:00"


def write_jsonl(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(record, ensure_ascii=False) + "\n" for record in records),
        encoding="utf-8",
    )


class LocalSessionInventoryTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.grok_home = self.root / ".grok"
        self.grok_bot_data = self.root / "Grok Bot"
        self.gemini_home = self.root / ".gemini"
        self.claude_home = self.root / ".claude"

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def run_script(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--grok-home",
                str(self.grok_home),
                "--grok-bot-data",
                str(self.grok_bot_data),
                "--gemini-home",
                str(self.gemini_home),
                "--claude-home",
                str(self.claude_home),
                "--now",
                NOW,
                "--format",
                "jsonl",
                *arguments,
            ],
            capture_output=True,
            text=True,
            check=False,
        )

    def run_script_with_environment(
        self, *arguments: str, environment: dict[str, str]
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--grok-bot-data",
                str(self.grok_bot_data),
                "--gemini-home",
                str(self.gemini_home),
                "--claude-home",
                str(self.claude_home),
                "--now",
                NOW,
                "--format",
                "jsonl",
                *arguments,
            ],
            capture_output=True,
            text=True,
            check=False,
            env={**os.environ, **environment},
        )

    def rows(self, result: subprocess.CompletedProcess[str]) -> list[dict]:
        self.assertEqual(result.returncode, 0, result.stderr)
        return [json.loads(line) for line in result.stdout.splitlines() if line]

    def add_grok_build_session(
        self,
        session_id: str,
        *,
        cwd: str,
        title: str,
        session_kind: str | None = None,
        created_at: str = "2026-08-01T00:00:00Z",
        last_active_at: str = "2026-08-02T00:00:00Z",
    ) -> None:
        session_dir = self.grok_home / "sessions" / quote(cwd, safe="") / session_id
        session_dir.mkdir(parents=True)
        summary = {
            "info": {"id": session_id, "cwd": cwd},
            "created_at": created_at,
            "last_active_at": last_active_at,
            "generated_title": title,
            "current_model_id": "grok-test",
        }
        if session_kind is not None:
            summary["session_kind"] = session_kind
        (session_dir / "summary.json").write_text(json.dumps(summary), encoding="utf-8")
        write_jsonl(
            session_dir / "updates.jsonl",
            [
                {
                    "timestamp": created_at,
                    "method": "session/update",
                    "params": {
                        "sessionId": session_id,
                        "update": {
                            "sessionUpdate": "user_message_chunk",
                            "content": {"type": "text", "text": title},
                        },
                    },
                }
            ],
        )

    def add_grok_bot_replica(self, conversation_id: str) -> None:
        account_scope = "google-oauth2|private-account"
        key = (
            "sand.client.slice.account."
            f"{account_scope}.transcript.replicas.{conversation_id}"
        )
        filename = base64.b32encode(key.encode()).decode().rstrip("=").lower() + ".blob"
        path = self.grok_bot_data / "sand-client-persistence" / filename
        path.parent.mkdir(parents=True)
        path.write_text(
            json.dumps(
                {
                    "schemaVersion": 1,
                    "value": {
                        "entries": [
                            {
                                "kind": "send-message",
                                "id": "send-1",
                                "message": {"type": "text", "content": "本地 Grok Bot 会话"},
                                "timestampMs": 1785542400000,
                            },
                            {
                                "kind": "message",
                                "id": "reply-1",
                                "role": "user",
                                "content": "回复",
                                "timestampMs": 1785542460000,
                            },
                        ],
                        "persistedAt": 1785542460000,
                    },
                }
            ),
            encoding="utf-8",
        )
        (path.parent / "not-a-transcript.blob").write_text("{}", encoding="utf-8")

    def add_gemini_session(self, *, session_id: str, kind: str = "main") -> None:
        project = "/workspace/gemini-project"
        project_id = "gemini-project-ab12cd34"
        self.gemini_home.mkdir(parents=True, exist_ok=True)
        (self.gemini_home / "projects.json").write_text(
            json.dumps({"projects": {project: project_id}}), encoding="utf-8"
        )
        chats = self.gemini_home / "tmp" / project_id / "chats"
        filename = (
            f"session-2026-08-03T00-00-{session_id[:8]}.jsonl"
            if kind == "main"
            else f"parent-session/{session_id}.jsonl"
        )
        write_jsonl(
            chats / filename,
            [
                {
                    "sessionId": session_id,
                    "projectHash": "hash",
                    "startTime": "2026-08-03T00:00:00Z",
                    "lastUpdated": "2026-08-03T00:10:00Z",
                    "kind": kind,
                },
                {
                    "id": "ignored",
                    "timestamp": "2026-08-03T00:01:00Z",
                    "type": "user",
                    "content": "/help",
                },
                {
                    "id": "real-user",
                    "timestamp": "2026-08-03T00:02:00Z",
                    "type": "user",
                    "content": [{"text": "Gemini 本地会话"}],
                },
            ],
        )

    def add_antigravity_session(self, *, cli: bool) -> None:
        source_dir = "antigravity-cli" if cli else "antigravity"
        session_id = "22222222-2222-4222-8222-222222222222" if cli else "11111111-1111-4111-8111-111111111111"
        transcript = (
            self.gemini_home
            / source_dir
            / "brain"
            / session_id
            / ".system_generated"
            / "logs"
            / "transcript.jsonl"
        )
        write_jsonl(
            transcript,
            [
                {
                    "step_index": 0,
                    "source": "user",
                    "type": "USER_INPUT",
                    "status": "done",
                    "created_at": "2026-08-04T00:00:00Z",
                    "content": "Antigravity CLI" if cli else "Antigravity Desktop",
                },
                {
                    "step_index": 1,
                    "source": "agent",
                    "type": "PLANNER_RESPONSE",
                    "status": "done",
                    "created_at": "2026-08-04T00:05:00Z",
                    "thinking": "hidden",
                },
            ],
        )

    def add_claude_code_session(self) -> None:
        session_id = "55555555-5555-4555-8555-555555555555"
        project = self.claude_home / "projects" / "-Users-mike-Documents-vault"
        write_jsonl(
            project / f"{session_id}.jsonl",
            [
                {
                    "type": "user",
                    "timestamp": "2026-08-05T00:00:00Z",
                    "cwd": "/Users/mike/Documents/vault",
                    "sessionId": session_id,
                    "message": {"role": "user", "content": "扫描本地 demo"},
                },
                {
                    "type": "assistant",
                    "timestamp": "2026-08-05T00:05:00Z",
                    "message": {"role": "assistant", "content": "开始"},
                },
            ],
        )
        write_jsonl(
            project / session_id / "subagents" / "agent-sub-1.jsonl",
            [
                {
                    "type": "user",
                    "timestamp": "2026-08-05T00:02:00Z",
                    "cwd": "/Users/mike/Documents/vault",
                    "sessionId": session_id,
                    "message": {"role": "user", "content": "子代理任务"},
                }
            ],
        )

    def add_claude_transcript(self) -> None:
        write_jsonl(
            self.claude_home / "transcripts" / "ses_opencode_parent.jsonl",
            [
                {
                    "type": "user",
                    "timestamp": "2026-01-12T08:00:00Z",
                    "content": "你来设置opencode，默认用antigravity的 opus 4.6",
                },
                {
                    "type": "tool_use",
                    "timestamp": "2026-01-12T08:01:00Z",
                    "content": "read",
                },
            ],
        )

    def test_all_sources_use_local_transcript_authorities(self) -> None:
        self.add_grok_build_session(
            "11111111-aaaa-4aaa-8aaa-111111111111",
            cwd="/workspace/grok-project",
            title="Grok Build 本地会话 api_key=secret-value",
        )
        self.add_grok_bot_replica("33333333-3333-4333-8333-333333333333")
        self.add_gemini_session(session_id="44444444-4444-4444-8444-444444444444")
        self.add_antigravity_session(cli=False)
        self.add_antigravity_session(cli=True)
        write_jsonl(
            self.gemini_home / "antigravity-cli" / "history.jsonl",
            [{"display": "不是 canonical conversation", "timestamp": 1}],
        )
        self.add_claude_code_session()
        self.add_claude_transcript()

        rows = self.rows(self.run_script("--source", "all"))

        self.assertEqual(
            [row["source"] for row in rows],
            [
                "grok-build",
                "grok-bot",
                "gemini-cli",
                "antigravity-desktop",
                "antigravity-cli",
                "claude-code",
                "claude-transcripts",
            ],
        )
        self.assertTrue(all(row["evidence_status"] == "available" for row in rows))
        self.assertNotIn("private-account", json.dumps(rows))
        self.assertNotIn("secret-value", json.dumps(rows))
        self.assertFalse(any(row["transcript_path"].endswith("history.jsonl") for row in rows))

    def test_claude_transcripts_are_inventoried_without_include_subagents(self) -> None:
        self.add_claude_code_session()
        self.add_claude_transcript()
        write_jsonl(
            self.claude_home / "transcripts" / "ses_hello_only.jsonl",
            [
                {
                    "type": "user",
                    "timestamp": "2026-01-13T14:06:18.786Z",
                    "content": "你好",
                }
            ],
        )

        default_rows = self.rows(self.run_script("--source", "all"))
        included_rows = self.rows(
            self.run_script("--source", "all", "--include-subagents")
        )

        default_ids = {row["id"] for row in default_rows}
        self.assertIn("55555555-5555-4555-8555-555555555555", default_ids)
        self.assertIn("ses_opencode_parent", default_ids)
        self.assertIn("ses_hello_only", default_ids)
        self.assertNotIn("agent-sub-1", default_ids)
        self.assertEqual(
            {row["id"] for row in default_rows if row["source"] == "claude-transcripts"},
            {"ses_opencode_parent", "ses_hello_only"},
        )

        code_row = next(row for row in default_rows if row["source"] == "claude-code")
        self.assertEqual(code_row["cwd"], "/Users/mike/Documents/vault")
        self.assertEqual(code_row["title"], "扫描本地 demo")
        self.assertEqual(code_row["last_active_at"], "2026-08-05T08:05:00+08:00")
        self.assertNotIn("mtime", json.dumps(code_row))

        transcript_row = next(
            row for row in default_rows if row["id"] == "ses_opencode_parent"
        )
        self.assertEqual(
            transcript_row["title"],
            "你来设置opencode，默认用antigravity的 opus 4.6",
        )
        self.assertEqual(transcript_row["thread_kind"], "user")

        included_ids = {row["id"] for row in included_rows}
        self.assertIn("agent-sub-1", included_ids)

    def test_grok_bot_locator_does_not_expose_reversible_blob_key(self) -> None:
        conversation_id = "33333333-3333-4333-8333-333333333333"
        self.add_grok_bot_replica(conversation_id)

        row = self.rows(self.run_script("--source", "grok-bot"))[0]

        self.assertEqual(
            row["transcript_path"], f"grok-bot://transcript/{conversation_id}"
        )
        self.assertFalse(Path(row["transcript_path"]).name.endswith(".blob"))

    def test_all_output_string_fields_are_credential_redacted(self) -> None:
        session_id = "98989898-9898-4898-8898-989898989898"
        group = self.grok_home / "sessions" / "oauthToken=path-secret"
        session_dir = group / session_id
        session_dir.mkdir(parents=True)
        (session_dir / "summary.json").write_text(
            json.dumps(
                {
                    "info": {
                        "id": session_id,
                        "cwd": "https://user:pass@example.com/work?access_token=query-secret",
                    },
                    "created_at": "2026-08-01T00:00:00Z",
                    "last_active_at": "2026-08-02T00:00:00Z",
                    "generated_title": (
                        "oauthToken=camel-secret Authorization: Basic basic-secret"
                    ),
                    "current_model_id": "model password=model-secret",
                }
            ),
            encoding="utf-8",
        )
        write_jsonl(
            session_dir / "updates.jsonl",
            [
                {
                    "method": "session/update",
                    "params": {
                        "update": {"sessionUpdate": "user_message_chunk"}
                    },
                }
            ],
        )

        rendered = json.dumps(
            self.rows(self.run_script("--source", "grok-build")), ensure_ascii=False
        )

        for secret in (
            "path-secret",
            "user:pass",
            "query-secret",
            "camel-secret",
            "basic-secret",
            "model-secret",
        ):
            self.assertNotIn(secret, rendered)

    def test_grok_home_environment_variable_is_the_default_root(self) -> None:
        self.add_grok_build_session(
            "91919191-9191-4191-8191-919191919191",
            cwd="/workspace/environment-root",
            title="environment root",
        )

        result = self.run_script_with_environment(
            "--source",
            "grok-build",
            environment={"GROK_HOME": str(self.grok_home)},
        )

        self.assertEqual(
            [row["id"] for row in self.rows(result)],
            ["91919191-9191-4191-8191-919191919191"],
        )

    def test_exact_id_fails_when_multiple_sources_have_the_same_id(self) -> None:
        shared_id = "92929292-9292-4292-8292-929292929292"
        self.add_grok_build_session(
            shared_id, cwd="/workspace/shared-id", title="Grok Build"
        )
        self.add_grok_bot_replica(shared_id)

        result = self.run_script("--source", "all", "--id", shared_id)

        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn("ambiguous", result.stderr)
        self.assertIn("--source", result.stderr)

    def test_duplicate_gemini_session_id_is_one_unavailable_record(self) -> None:
        session_id = "93939393-9393-4393-8393-939393939393"
        self.add_gemini_session(session_id=session_id)
        project_id = "gemini-project-ab12cd34"
        write_jsonl(
            self.gemini_home
            / "tmp"
            / project_id
            / "chats"
            / "resumed"
            / "resume.jsonl",
            [
                {
                    "sessionId": session_id,
                    "projectHash": "hash",
                    "startTime": "2026-08-03T00:00:00Z",
                    "lastUpdated": "2026-08-03T01:00:00Z",
                    "kind": "main",
                },
                {"id": "user-2", "type": "user", "content": "resumed"},
            ],
        )

        rows = self.rows(self.run_script("--source", "gemini-cli"))

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["id"], session_id)
        self.assertEqual(rows[0]["evidence_status"], "unavailable")

    def test_empty_grok_build_transcript_is_unavailable(self) -> None:
        session_id = "94949494-9494-4494-8494-949494949494"
        self.add_grok_build_session(
            session_id, cwd="/workspace/empty", title="empty"
        )
        transcript = next(self.grok_home.glob(f"sessions/*/{session_id}/updates.jsonl"))
        transcript.write_text("", encoding="utf-8")

        row = self.rows(self.run_script("--source", "grok-build"))[0]

        self.assertEqual(row["evidence_status"], "unavailable")

    def test_invalid_only_grok_build_transcript_is_unavailable(self) -> None:
        session_id = "95959595-9595-4595-8595-959595959595"
        self.add_grok_build_session(
            session_id, cwd="/workspace/invalid", title="invalid"
        )
        transcript = next(self.grok_home.glob(f"sessions/*/{session_id}/updates.jsonl"))
        transcript.write_text("not-json\n", encoding="utf-8")

        row = self.rows(self.run_script("--source", "grok-build"))[0]

        self.assertEqual(row["evidence_status"], "unavailable")

    def test_mixed_valid_and_invalid_grok_build_transcript_is_unavailable(self) -> None:
        session_id = "96969696-9696-4696-8696-969696969696"
        self.add_grok_build_session(
            session_id, cwd="/workspace/mixed", title="mixed"
        )
        transcript = next(self.grok_home.glob(f"sessions/*/{session_id}/updates.jsonl"))
        with transcript.open("a", encoding="utf-8") as handle:
            handle.write("not-json\n")

        row = self.rows(self.run_script("--source", "grok-build"))[0]

        self.assertEqual(row["evidence_status"], "unavailable")

    def test_unrecognized_grok_bot_entries_are_unavailable(self) -> None:
        conversation_id = "97979797-9797-4797-8797-979797979797"
        self.add_grok_bot_replica(conversation_id)
        replica = next(
            (self.grok_bot_data / "sand-client-persistence").glob("*.blob")
        )
        replica.write_text(
            json.dumps({"schemaVersion": 1, "value": {"entries": [{}]}}),
            encoding="utf-8",
        )

        row = self.rows(self.run_script("--source", "grok-bot"))[0]

        self.assertEqual(row["evidence_status"], "unavailable")

    def test_unrecognized_antigravity_records_are_unavailable(self) -> None:
        self.add_antigravity_session(cli=False)
        transcript = next(
            self.gemini_home.glob(
                "antigravity/brain/*/.system_generated/logs/transcript.jsonl"
            )
        )
        write_jsonl(transcript, [{}])

        row = self.rows(self.run_script("--source", "antigravity-desktop"))[0]

        self.assertEqual(row["evidence_status"], "unavailable")

    def test_mixed_valid_and_invalid_gemini_transcript_is_unavailable(self) -> None:
        session_id = "89898989-8989-4898-8898-898989898989"
        self.add_gemini_session(session_id=session_id)
        transcript = next(
            self.gemini_home.glob("tmp/*/chats/session-*.jsonl")
        )
        with transcript.open("a", encoding="utf-8") as handle:
            handle.write("not-json\n")

        row = self.rows(self.run_script("--source", "gemini-cli"))[0]

        self.assertEqual(row["evidence_status"], "unavailable")

    def test_reverse_date_window_fails_atomically(self) -> None:
        result = self.run_script(
            "--source",
            "all",
            "--from",
            "2026-09-01",
            "--to",
            "2026-08-01",
        )

        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn("empty or reversed", result.stderr)

    def test_conflicting_duration_window_fails_atomically(self) -> None:
        result = self.run_script(
            "--source",
            "all",
            "--newer-than",
            "7d",
            "--older-than",
            "30d",
        )

        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn("empty or reversed", result.stderr)

    def test_grok_bot_key_must_match_the_anchored_account_slice(self) -> None:
        marker_only_key = (
            "other.slice.private.transcript.replicas."
            "90909090-9090-4090-8090-909090909090"
        )
        filename = (
            base64.b32encode(marker_only_key.encode()).decode().rstrip("=").lower()
            + ".blob"
        )
        path = self.grok_bot_data / "sand-client-persistence" / filename
        path.parent.mkdir(parents=True)
        path.write_text(
            json.dumps(
                {
                    "schemaVersion": 1,
                    "value": {
                        "entries": [
                            {
                                "kind": "send-message",
                                "message": {"type": "text", "content": "wrong slice"},
                            }
                        ]
                    },
                }
            ),
            encoding="utf-8",
        )

        rows = self.rows(self.run_script("--source", "grok-bot"))

        self.assertEqual(rows, [])

    def test_subagents_are_excluded_by_default_and_included_explicitly(self) -> None:
        self.add_grok_build_session(
            "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
            cwd="/workspace/project",
            title="main",
        )
        self.add_grok_build_session(
            "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb",
            cwd="/workspace/project",
            title="child",
            session_kind="subagent_resume",
        )
        self.add_gemini_session(
            session_id="cccccccc-cccc-4ccc-8ccc-cccccccccccc", kind="subagent"
        )

        default_rows = self.rows(self.run_script("--source", "all"))
        included_rows = self.rows(
            self.run_script("--source", "all", "--include-subagents")
        )

        self.assertEqual([row["id"] for row in default_rows], ["aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"])
        self.assertEqual(
            {row["id"] for row in included_rows},
            {
                "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
                "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb",
                "cccccccc-cccc-4ccc-8ccc-cccccccccccc",
            },
        )
        self.assertEqual(
            {row["thread_kind"] for row in included_rows}, {"user", "subagent"}
        )

    def test_exact_id_selection_is_atomic_and_cwd_month_filters_are_exact(self) -> None:
        self.add_grok_build_session(
            "dddddddd-dddd-4ddd-8ddd-dddddddddddd",
            cwd="/workspace/target",
            title="target",
            created_at="2026-07-31T23:30:00Z",
            last_active_at="2026-08-01T00:30:00Z",
        )
        self.add_grok_build_session(
            "eeeeeeee-eeee-4eee-8eee-eeeeeeeeeeee",
            cwd="/workspace/other",
            title="other",
        )

        rows = self.rows(
            self.run_script(
                "--source",
                "grok-build",
                "--cwd",
                "/workspace/target",
                "--month",
                "2026-08",
            )
        )
        missing = self.run_script(
            "--source",
            "grok-build",
            "--id",
            "dddddddd-dddd-4ddd-8ddd-dddddddddddd",
            "--id",
            "missing",
        )

        self.assertEqual([row["id"] for row in rows], ["dddddddd-dddd-4ddd-8ddd-dddddddddddd"])
        self.assertNotEqual(missing.returncode, 0)
        self.assertEqual(missing.stdout, "")
        self.assertIn("missing", missing.stderr)

    def test_grok_build_id_conflict_is_unavailable_and_group_marker_supplies_cwd(self) -> None:
        group = self.grok_home / "sessions" / "project-slug-ab12cd34"
        session_dir = group / "directory-session-id"
        session_dir.mkdir(parents=True)
        (group / ".cwd").write_text("/workspace/from-marker\n", encoding="utf-8")
        (session_dir / "summary.json").write_text(
            json.dumps(
                {
                    "info": {"id": "metadata-session-id"},
                    "created_at": "2026-08-05T00:00:00Z",
                    "last_active_at": "2026-08-05T00:01:00Z",
                    "generated_title": "conflict",
                }
            ),
            encoding="utf-8",
        )
        write_jsonl(session_dir / "updates.jsonl", [{"method": "session/update"}])

        rows = self.rows(self.run_script("--source", "grok-build"))

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["cwd"], "/workspace/from-marker")
        self.assertEqual(rows[0]["evidence_status"], "unavailable")

    def test_gemini_rewind_removes_old_prompt_before_title_selection(self) -> None:
        project = "/workspace/rewind-project"
        project_id = "rewind-project-ab12cd34"
        self.gemini_home.mkdir(parents=True)
        (self.gemini_home / "projects.json").write_text(
            json.dumps({"projects": {project: project_id}}), encoding="utf-8"
        )
        transcript = self.gemini_home / "tmp" / project_id / "chats" / "session-rewind.jsonl"
        write_jsonl(
            transcript,
            [
                {
                    "sessionId": "ffffffff-ffff-4fff-8fff-ffffffffffff",
                    "projectHash": "hash",
                    "startTime": "2026-08-06T00:00:00Z",
                    "lastUpdated": "2026-08-06T00:05:00Z",
                    "kind": "main",
                },
                {"id": "old", "type": "user", "content": "已经 rewind 的 prompt"},
                {"$rewindTo": "old"},
                {"id": "new", "type": "user", "content": "保留的 prompt"},
            ],
        )

        rows = self.rows(self.run_script("--source", "gemini-cli"))

        self.assertEqual(rows[0]["title"], "保留的 prompt")


if __name__ == "__main__":
    unittest.main()
