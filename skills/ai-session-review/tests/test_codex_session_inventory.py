import hashlib
import importlib.util
import json
import os
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest import mock


SKILL_DIR = Path(__file__).resolve().parents[1]
SCRIPT = SKILL_DIR / "scripts" / "codex_session_inventory.py"
NOW = "2026-03-31T12:00:00+08:00"
TABLE_HEADER = (
    "id\tlast_active_at\tage_bucket\tarchived\tis_pinned\tthread_kind\t"
    "cwd\ttitle\trollout_path"
)
REQUIRED_COLUMNS = [
    "id",
    "title",
    "cwd",
    "rollout_path",
    "created_at_ms",
    "recency_at_ms",
    "archived",
    "is_pinned",
    "thread_source",
    "source",
    "model",
]

MODULE_SPEC = importlib.util.spec_from_file_location("codex_session_inventory", SCRIPT)
assert MODULE_SPEC is not None and MODULE_SPEC.loader is not None
INVENTORY = importlib.util.module_from_spec(MODULE_SPEC)
MODULE_SPEC.loader.exec_module(INVENTORY)


def timestamp_ms(value: str) -> int:
    return int(datetime.fromisoformat(value).timestamp() * 1000)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def file_state(path: Path) -> tuple[str, int, int]:
    stat = path.stat()
    return sha256(path), stat.st_size, stat.st_mtime_ns


class CodexSessionInventoryTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.db_path = self.root / "state.sqlite"
        self.create_database()

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def create_database(self, columns: list[str] | None = None) -> None:
        selected = columns or REQUIRED_COLUMNS
        definitions = {
            "id": "TEXT PRIMARY KEY",
            "title": "TEXT",
            "cwd": "TEXT",
            "rollout_path": "TEXT",
            "created_at_ms": "INTEGER",
            "recency_at_ms": "INTEGER",
            "archived": "INTEGER",
            "is_pinned": "INTEGER",
            "thread_source": "TEXT",
            "source": "TEXT",
            "model": "TEXT",
        }
        with sqlite3.connect(self.db_path) as connection:
            schema = ", ".join(f"{name} {definitions[name]}" for name in selected)
            connection.execute(f"CREATE TABLE threads ({schema})")

    def replace_database(self, columns: list[str]) -> None:
        self.db_path.unlink()
        self.create_database(columns)

    def insert_thread(
        self,
        session_id: str,
        *,
        created_at: str = "2026-01-01T00:00:00+08:00",
        last_active_at: str = "2026-03-01T00:00:00+08:00",
        title: str = "title",
        cwd: str = "/workspace/project",
        rollout_path: str | None = None,
        archived: int = 0,
        is_pinned: int = 0,
        thread_source: str | None = "user",
        source: str = "vscode",
        model: str | None = "gpt-test",
    ) -> None:
        values = {
            "id": session_id,
            "title": title,
            "cwd": cwd,
            "rollout_path": rollout_path or f"/rollouts/{session_id}.jsonl",
            "created_at_ms": timestamp_ms(created_at),
            "recency_at_ms": timestamp_ms(last_active_at),
            "archived": archived,
            "is_pinned": is_pinned,
            "thread_source": thread_source,
            "source": source,
            "model": model,
        }
        with sqlite3.connect(self.db_path) as connection:
            columns = list(values)
            placeholders = ", ".join("?" for _ in columns)
            connection.execute(
                f"INSERT INTO threads ({', '.join(columns)}) VALUES ({placeholders})",
                [values[column] for column in columns],
            )

    def run_script(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--db",
                str(self.db_path),
                "--now",
                NOW,
                *arguments,
            ],
            capture_output=True,
            text=True,
            check=False,
        )

    def json_rows(self, result: subprocess.CompletedProcess[str]) -> list[dict]:
        self.assertEqual(result.returncode, 0, result.stderr)
        return [json.loads(line) for line in result.stdout.splitlines() if line]

    def test_jsonl_normalizes_thread_kinds_sources_and_sort_order(self) -> None:
        self.insert_thread(
            "user-cli",
            last_active_at="2026-01-01T00:00:00+08:00",
            thread_source=None,
            source="cli",
            is_pinned=1,
        )
        self.insert_thread(
            "user-explicit",
            last_active_at="2026-03-20T00:00:00+08:00",
            thread_source="user",
            source='{"surface":"desktop"}',
        )
        self.insert_thread(
            "subagent-object",
            last_active_at="2026-03-10T00:00:00+08:00",
            thread_source=None,
            source='{"subagent":{"thread_spawn":{"parent_thread_id":"user-cli"}}}',
        )
        self.insert_thread(
            "other-thread",
            last_active_at="2026-03-15T00:00:00+08:00",
            thread_source="other",
            source="exec",
        )
        self.insert_thread(
            "future-user",
            last_active_at="2026-04-01T00:00:00+08:00",
            thread_source="user",
            source="unparseable {",
            model=None,
        )

        default_result = self.run_script("--format", "jsonl")
        default_rows = self.json_rows(default_result)

        self.assertEqual(
            [row["id"] for row in default_rows],
            ["user-cli", "user-explicit", "future-user"],
        )
        self.assertEqual(default_rows[0]["source"], "cli")
        self.assertEqual(default_rows[1]["source"], {"surface": "desktop"})
        self.assertEqual(default_rows[2]["source"], "unparseable {")
        self.assertEqual(default_rows[0]["age_bucket"], "mature")
        self.assertEqual(default_rows[1]["age_bucket"], "cooling")
        self.assertEqual(default_rows[2]["age_bucket"], "active")
        self.assertIs(default_rows[0]["is_pinned"], True)
        self.assertIs(default_rows[0]["archived"], False)
        self.assertIsNone(default_rows[2]["model"])
        self.assertIn("future-user", default_result.stderr)
        self.assertIn("future", default_result.stderr.lower())

        included_result = self.run_script("--format", "jsonl", "--include-subagents")
        included_rows = self.json_rows(included_result)
        self.assertEqual(
            [row["id"] for row in included_rows],
            ["user-cli", "subagent-object", "user-explicit", "future-user"],
        )
        self.assertEqual(included_rows[1]["thread_kind"], "subagent")

    def test_jsonl_has_fixed_fields_and_offset_iso_timestamps(self) -> None:
        self.insert_thread(
            "one",
            created_at="2026-03-01T08:30:00+08:00",
            last_active_at="2026-03-02T09:45:00+08:00",
        )

        rows = self.json_rows(self.run_script("--format", "jsonl"))

        self.assertEqual(
            list(rows[0]),
            [
                "id",
                "title",
                "cwd",
                "rollout_path",
                "created_at",
                "last_active_at",
                "age_bucket",
                "archived",
                "is_pinned",
                "thread_kind",
                "model",
                "source",
            ],
        )
        self.assertEqual(rows[0]["created_at"], "2026-03-01T08:30:00+08:00")
        self.assertEqual(rows[0]["last_active_at"], "2026-03-02T09:45:00+08:00")

    def test_source_parsing_rejects_nonfinite_json_constants(self) -> None:
        self.insert_thread("nan-source", source="NaN")
        self.insert_thread(
            "infinity-source",
            last_active_at="2026-03-02T00:00:00+08:00",
            source="Infinity",
        )

        rows = self.json_rows(self.run_script("--format", "jsonl"))

        self.assertEqual(
            {row["id"]: row["source"] for row in rows},
            {"nan-source": "NaN", "infinity-source": "Infinity"},
        )

    def test_inventory_redacts_credentials_from_text_and_structured_source(self) -> None:
        self.insert_thread(
            "structured-secret",
            title="Inspect api_key=sk-title-secret",
            source=json.dumps(
                {
                    "surface": "desktop",
                    "oauth_token": "oauth-source-secret",
                    "nested": {
                        "cookie": "session=cookie-secret",
                        "visible": "keep-me",
                    },
                }
            ),
        )
        self.insert_thread(
            "plain-secret",
            last_active_at="2026-03-02T00:00:00+08:00",
            source="Authorization: Bearer plain-bearer-secret",
        )
        self.insert_thread(
            "plain-env-secret",
            last_active_at="2026-03-02T12:00:00+08:00",
            source=(
                "OPENAI_API_KEY=openai-env-secret "
                "GITHUB_TOKEN='github-env-secret'"
            ),
        )
        self.insert_thread(
            "structured-env-secret",
            last_active_at="2026-03-03T00:00:00+08:00",
            source=json.dumps(
                {
                    "environment": {
                        "AWS_SECRET_ACCESS_KEY": "aws-env-secret",
                        "PUBLIC_ENDPOINT": "https://example.invalid",
                    }
                }
            ),
        )

        json_result = self.run_script("--format", "jsonl")
        rows = {row["id"]: row for row in self.json_rows(json_result)}
        table_result = self.run_script("--format", "table")

        for secret in (
            "sk-title-secret",
            "oauth-source-secret",
            "cookie-secret",
            "plain-bearer-secret",
            "openai-env-secret",
            "github-env-secret",
            "aws-env-secret",
        ):
            self.assertNotIn(secret, json_result.stdout)
            self.assertNotIn(secret, table_result.stdout)
        self.assertIn("[REDACTED]", rows["structured-secret"]["title"])
        self.assertEqual(rows["structured-secret"]["source"]["oauth_token"], "[REDACTED]")
        self.assertEqual(
            rows["structured-secret"]["source"]["nested"]["cookie"],
            "[REDACTED]",
        )
        self.assertEqual(
            rows["structured-secret"]["source"]["nested"]["visible"],
            "keep-me",
        )
        self.assertIn("[REDACTED]", rows["plain-secret"]["source"])
        self.assertEqual(
            rows["structured-env-secret"]["source"]["environment"]
            ["AWS_SECRET_ACCESS_KEY"],
            "[REDACTED]",
        )
        self.assertEqual(
            rows["structured-env-secret"]["source"]["environment"]["PUBLIC_ENDPOINT"],
            "https://example.invalid",
        )

    def test_inventory_redacts_common_env_credentials_and_uri_secrets(self) -> None:
        self.insert_thread(
            "common-env-secrets",
            title=(
                "AWS_ACCESS_KEY_ID=aws-access-secret "
                "SSH_PRIVATE_KEY='ssh-private-secret' "
                "GITHUB_PAT=github-pat-secret "
                "APIKEY=compact-api-secret "
                "apiKey=camel-api-secret "
                "accessToken=camel-access-secret "
                "privateKey=camel-private-secret "
                "clientSecret=camel-client-secret"
            ),
            cwd=(
                "postgres://db-user:db-password@db.invalid/app"
                "?sslmode=require&access_token=query-secret"
                "&apikey=compact-query-secret"
            ),
            rollout_path="/rollouts/item?NPM_CONFIG__AUTH=npm-auth-secret",
            source=json.dumps(
                {
                    "environment": {
                        "AWS_ACCESS_KEY_ID": "structured-aws-secret",
                        "SSH_PRIVATE_KEY": "structured-ssh-secret",
                        "GITHUB_PAT": "structured-github-secret",
                        "NPM_CONFIG__AUTH": "structured-npm-secret",
                        "apiKey": "structured-camel-api-secret",
                        "accessToken": "structured-camel-access-secret",
                        "privateKey": "structured-camel-private-secret",
                        "clientSecret": "structured-camel-client-secret",
                        "DATABASE_URL": (
                            "postgres://structured-user:structured-password@"
                            "db.invalid/app?password=structured-query-secret"
                        ),
                        "PUBLIC_ENDPOINT": "https://example.invalid/public",
                    }
                }
            ),
        )

        json_result = self.run_script("--format", "jsonl")
        row = self.json_rows(json_result)[0]
        table_result = self.run_script("--format", "table")

        for secret in (
            "aws-access-secret",
            "ssh-private-secret",
            "github-pat-secret",
            "compact-api-secret",
            "camel-api-secret",
            "camel-access-secret",
            "camel-private-secret",
            "camel-client-secret",
            "db-user",
            "db-password",
            "query-secret",
            "compact-query-secret",
            "npm-auth-secret",
            "structured-aws-secret",
            "structured-ssh-secret",
            "structured-github-secret",
            "structured-npm-secret",
            "structured-camel-api-secret",
            "structured-camel-access-secret",
            "structured-camel-private-secret",
            "structured-camel-client-secret",
            "structured-user",
            "structured-password",
            "structured-query-secret",
        ):
            self.assertNotIn(secret, json_result.stdout)
            self.assertNotIn(secret, table_result.stdout)
        environment = row["source"]["environment"]
        for key in (
            "AWS_ACCESS_KEY_ID",
            "SSH_PRIVATE_KEY",
            "GITHUB_PAT",
            "NPM_CONFIG__AUTH",
            "apiKey",
            "accessToken",
            "privateKey",
            "clientSecret",
        ):
            self.assertEqual(environment[key], "[REDACTED]")
        self.assertIn("db.invalid/app", environment["DATABASE_URL"])
        self.assertEqual(
            environment["PUBLIC_ENDPOINT"],
            "https://example.invalid/public",
        )

    def test_table_is_tsv_and_collapses_all_whitespace(self) -> None:
        self.insert_thread(
            "table-row",
            title="  first\nsecond\t third   fourth  ",
            cwd="/workspace/with\tspace",
            rollout_path="/rollouts/with\nspace.jsonl",
        )

        result = self.run_script()

        self.assertEqual(result.returncode, 0, result.stderr)
        lines = result.stdout.splitlines()
        self.assertEqual(lines[0], TABLE_HEADER)
        cells = lines[1].split("\t")
        self.assertEqual(cells[6], "/workspace/with space")
        self.assertEqual(cells[7], "first second third fourth")
        self.assertEqual(cells[8], "/rollouts/with space.jsonl")
        self.assertEqual(cells[3:5], ["false", "false"])

    def test_empty_results_have_format_specific_output(self) -> None:
        table = self.run_script()
        jsonl = self.run_script("--format", "jsonl")

        self.assertEqual(table.returncode, 0, table.stderr)
        self.assertEqual(table.stdout, TABLE_HEADER + "\n")
        self.assertEqual(jsonl.returncode, 0, jsonl.stderr)
        self.assertEqual(jsonl.stdout, "")

    def test_age_bucket_boundaries_use_seven_and_thirty_days(self) -> None:
        self.insert_thread("under-seven", last_active_at="2026-03-24T12:00:00.001+08:00")
        self.insert_thread("exact-seven", last_active_at="2026-03-24T12:00:00+08:00")
        self.insert_thread("under-thirty", last_active_at="2026-03-01T12:00:00.001+08:00")
        self.insert_thread("exact-thirty", last_active_at="2026-03-01T12:00:00+08:00")

        rows = self.json_rows(self.run_script("--format", "jsonl"))
        buckets = {row["id"]: row["age_bucket"] for row in rows}

        self.assertEqual(
            buckets,
            {
                "exact-thirty": "mature",
                "under-thirty": "cooling",
                "exact-seven": "cooling",
                "under-seven": "active",
            },
        )

    def test_older_than_uses_strict_boundary_and_calendar_month(self) -> None:
        self.insert_thread("before-calendar", last_active_at="2026-02-28T11:59:59.999+08:00")
        self.insert_thread("equal-calendar", last_active_at="2026-02-28T12:00:00+08:00")
        self.insert_thread("between-cutoffs", last_active_at="2026-02-28T18:00:00+08:00")
        self.insert_thread("equal-thirty", last_active_at="2026-03-01T12:00:00+08:00")

        month_rows = self.json_rows(
            self.run_script("--format", "jsonl", "--older-than", "1m")
        )
        day_rows = self.json_rows(
            self.run_script("--format", "jsonl", "--older-than", "30d")
        )

        self.assertEqual([row["id"] for row in month_rows], ["before-calendar"])
        self.assertEqual(
            [row["id"] for row in day_rows],
            ["before-calendar", "equal-calendar", "between-cutoffs"],
        )

    def test_fixed_week_uses_elapsed_hours_across_dst(self) -> None:
        self.insert_thread(
            "before-fixed-week",
            last_active_at="2026-03-02T10:59:59-05:00",
        )
        self.insert_thread(
            "exact-fixed-week",
            last_active_at="2026-03-02T11:00:00-05:00",
        )
        self.insert_thread(
            "inside-fixed-week",
            last_active_at="2026-03-02T11:30:00-05:00",
        )

        rows = self.json_rows(
            self.run_script(
                "--format",
                "jsonl",
                "--timezone",
                "America/New_York",
                "--now",
                "2026-03-09T12:00:00-04:00",
                "--older-than",
                "1w",
            )
        )

        self.assertEqual([row["id"] for row in rows], ["before-fixed-week"])

    def test_newer_than_and_date_range_form_a_closed_open_intersection(self) -> None:
        self.insert_thread("at-from", last_active_at="2026-03-10T00:00:00+08:00")
        self.insert_thread("inside", last_active_at="2026-03-15T00:00:00+08:00")
        self.insert_thread("at-to", last_active_at="2026-03-20T00:00:00+08:00")
        self.insert_thread("recent", last_active_at="2026-03-28T00:00:00+08:00")

        rows = self.json_rows(
            self.run_script(
                "--format",
                "jsonl",
                "--newer-than",
                "30d",
                "--from",
                "2026-03-10",
                "--to",
                "2026-03-20",
            )
        )

        self.assertEqual([row["id"] for row in rows], ["at-from", "inside"])

        invalid = self.run_script(
            "--from", "2026-03-20", "--to", "2026-03-20"
        )
        self.assertNotEqual(invalid.returncode, 0)
        self.assertIn("empty", invalid.stderr.lower())
        self.assertEqual(invalid.stdout, "")

    def test_month_selects_activity_span_overlap_in_requested_timezone(self) -> None:
        self.insert_thread(
            "spans-month",
            created_at="2026-05-01T00:00:00+08:00",
            last_active_at="2026-07-02T00:00:00+08:00",
        )
        self.insert_thread(
            "ends-at-start",
            created_at="2026-05-01T00:00:00+08:00",
            last_active_at="2026-06-01T00:00:00+08:00",
        )
        self.insert_thread(
            "starts-before-end",
            created_at="2026-06-30T23:59:59.999+08:00",
            last_active_at="2026-07-01T00:00:00+08:00",
        )
        self.insert_thread(
            "starts-at-end",
            created_at="2026-07-01T00:00:00+08:00",
            last_active_at="2026-07-02T00:00:00+08:00",
        )

        rows = self.json_rows(
            self.run_script(
                "--format",
                "jsonl",
                "--month",
                "2026-06",
                "--timezone",
                "Asia/Shanghai",
            )
        )

        self.assertEqual(
            [row["id"] for row in rows],
            ["ends-at-start", "starts-before-end", "spans-month"],
        )

        conflict = self.run_script("--month", "2026-06", "--older-than", "7d")
        self.assertNotEqual(conflict.returncode, 0)
        self.assertIn("--month", conflict.stderr)
        self.assertEqual(conflict.stdout, "")

    def test_exact_ids_are_deduplicated_and_results_remain_stably_sorted(self) -> None:
        self.insert_thread("A", last_active_at="2026-03-20T00:00:00+08:00")
        self.insert_thread("B", last_active_at="2026-03-10T00:00:00+08:00")

        rows = self.json_rows(
            self.run_script(
                "--format",
                "jsonl",
                "--id",
                "A",
                "--id",
                "B",
                "--id",
                "A",
            )
        )

        self.assertEqual([row["id"] for row in rows], ["B", "A"])

    def test_exact_id_selection_fails_atomically_for_missing_or_excluded_ids(self) -> None:
        self.insert_thread("user", last_active_at="2026-03-20T00:00:00+08:00")
        self.insert_thread(
            "subagent",
            last_active_at="2026-03-10T00:00:00+08:00",
            thread_source="subagent",
            source='{"subagent":{}}',
        )
        self.insert_thread(
            "other",
            last_active_at="2026-03-05T00:00:00+08:00",
            thread_source="other",
            source="exec",
        )

        missing = self.run_script("--id", "user", "--id", "missing")
        self.assertNotEqual(missing.returncode, 0)
        self.assertIn("missing", missing.stderr)
        self.assertEqual(missing.stdout, "")

        excluded = self.run_script("--id", "user", "--id", "subagent")
        self.assertNotEqual(excluded.returncode, 0)
        self.assertIn("subagent", excluded.stderr)
        self.assertEqual(excluded.stdout, "")

        other = self.run_script("--include-subagents", "--id", "user", "--id", "other")
        self.assertNotEqual(other.returncode, 0)
        self.assertIn("other", other.stderr)
        self.assertEqual(other.stdout, "")

    def test_exact_ids_reject_discovery_filters(self) -> None:
        self.insert_thread("user")
        combinations = [
            ("--cwd", "/workspace/project"),
            ("--month", "2026-03"),
            ("--older-than", "7d"),
            ("--newer-than", "7d"),
            ("--from", "2026-03-01"),
            ("--to", "2026-04-01"),
            ("--archived", "active"),
        ]

        for option, value in combinations:
            with self.subTest(option=option):
                result = self.run_script("--id", "user", option, value)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("--id", result.stderr)
                self.assertEqual(result.stdout, "")

    def test_cwd_is_exact_and_archived_filter_is_independent(self) -> None:
        self.insert_thread("active-exact", cwd="/workspace/project", archived=0)
        self.insert_thread("archived-exact", cwd="/workspace/project", archived=1)
        self.insert_thread("child-path", cwd="/workspace/project/child", archived=0)

        active = self.json_rows(
            self.run_script(
                "--format",
                "jsonl",
                "--cwd",
                "/workspace/project",
                "--archived",
                "active",
            )
        )
        archived = self.json_rows(
            self.run_script(
                "--format",
                "jsonl",
                "--cwd",
                "/workspace/project",
                "--archived",
                "archived",
            )
        )

        self.assertEqual([row["id"] for row in active], ["active-exact"])
        self.assertEqual([row["id"] for row in archived], ["archived-exact"])

    def test_invalid_duration_date_month_timezone_and_now_are_errors(self) -> None:
        cases = [
            ("--older-than", "0d"),
            ("--older-than", "7h"),
            ("--from", "2026-02-30"),
            ("--month", "2026-13"),
            ("--timezone", "Mars/Olympus"),
            ("--now", "not-a-time"),
        ]

        for option, value in cases:
            with self.subTest(option=option, value=value):
                result = self.run_script(option, value)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(option, result.stderr)
                self.assertEqual(result.stdout, "")

    def test_schema_drift_lists_every_missing_required_field(self) -> None:
        self.replace_database(["id", "title", "cwd"])

        result = self.run_script("--format", "jsonl")

        self.assertNotEqual(result.returncode, 0)
        for column in sorted(set(REQUIRED_COLUMNS) - {"id", "title", "cwd"}):
            self.assertIn(column, result.stderr)
        self.assertIn("references/codex.md", result.stderr)
        self.assertIn("fallback", result.stderr.lower())
        self.assertEqual(result.stdout, "")

    def test_missing_database_points_to_restricted_jsonl_fallback(self) -> None:
        missing_db = self.root / "missing-state.sqlite"

        result = self.run_script("--db", str(missing_db), "--format", "jsonl")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("does not exist", result.stderr)
        self.assertIn("references/codex.md", result.stderr)
        self.assertIn("fallback", result.stderr.lower())
        self.assertEqual(result.stdout, "")

    def test_read_only_run_does_not_modify_database_or_create_sidecars(self) -> None:
        self.insert_thread("one")
        before_hash = sha256(self.db_path)
        before_stat = self.db_path.stat()
        os.chmod(self.db_path, 0o444)

        result = self.run_script("--format", "jsonl")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(sha256(self.db_path), before_hash)
        self.assertEqual(self.db_path.stat().st_size, before_stat.st_size)
        self.assertFalse(Path(str(self.db_path) + "-journal").exists())
        self.assertFalse(Path(str(self.db_path) + "-wal").exists())

    def test_read_only_run_preserves_existing_wal_database_and_sidecars(self) -> None:
        wal_path = Path(str(self.db_path) + "-wal")
        shm_path = Path(str(self.db_path) + "-shm")
        writer = sqlite3.connect(self.db_path)
        self.addCleanup(writer.close)
        self.assertEqual(writer.execute("PRAGMA journal_mode=WAL").fetchone()[0], "wal")
        writer.execute(
            "INSERT INTO threads VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                "wal-row",
                "title",
                "/workspace/project",
                "/rollouts/wal-row.jsonl",
                timestamp_ms("2026-01-01T00:00:00+08:00"),
                timestamp_ms("2026-03-01T00:00:00+08:00"),
                0,
                0,
                "user",
                "vscode",
                "gpt-test",
            ),
        )
        writer.commit()
        self.assertTrue(wal_path.is_file())
        self.assertTrue(shm_path.is_file())
        before = {
            path: file_state(path) for path in (self.db_path, wal_path, shm_path)
        }

        result = self.run_script("--format", "jsonl")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('"id":"wal-row"', result.stdout)
        self.assertEqual(
            {path: file_state(path) for path in (self.db_path, wal_path, shm_path)},
            before,
        )

    def test_snapshot_retries_when_checkpoint_occurs_during_copy(self) -> None:
        writer = sqlite3.connect(self.db_path)
        self.addCleanup(writer.close)
        self.assertEqual(writer.execute("PRAGMA journal_mode=WAL").fetchone()[0], "wal")
        real_copy = INVENTORY.shutil.copy2
        checkpointed = False

        def copy_and_checkpoint(source: Path, destination: Path):
            nonlocal checkpointed
            result = real_copy(source, destination)
            if Path(source) == self.db_path and not checkpointed:
                writer.execute(
                    "INSERT INTO threads VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        "committed-during-copy",
                        "title",
                        "/workspace/project",
                        "/rollouts/committed-during-copy.jsonl",
                        timestamp_ms("2026-01-01T00:00:00+08:00"),
                        timestamp_ms("2026-03-01T00:00:00+08:00"),
                        0,
                        0,
                        "user",
                        "vscode",
                        "gpt-test",
                    ),
                )
                writer.commit()
                writer.execute("PRAGMA wal_checkpoint(TRUNCATE)").fetchone()
                checkpointed = True
            return result

        with mock.patch.object(INVENTORY.shutil, "copy2", side_effect=copy_and_checkpoint):
            with INVENTORY.open_database(self.db_path) as connection:
                session_ids = {
                    row["id"] for row in INVENTORY.load_threads(connection)
                }

        self.assertTrue(checkpointed)
        self.assertIn("committed-during-copy", session_ids)


if __name__ == "__main__":
    unittest.main()
