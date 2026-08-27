import importlib.util
import sqlite3
import sys
import time
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
SCRIPT = SKILL_DIR / "scripts" / "codex_runtime_hygiene.py"

MODULE_SPEC = importlib.util.spec_from_file_location("codex_runtime_hygiene", SCRIPT)
assert MODULE_SPEC is not None and MODULE_SPEC.loader is not None
HYGIENE = importlib.util.module_from_spec(MODULE_SPEC)
sys.modules["codex_runtime_hygiene"] = HYGIENE
MODULE_SPEC.loader.exec_module(HYGIENE)


def create_mock_logs_db(db_path: Path, num_rows: int = 1000, create_freelist: bool = True):
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts INTEGER NOT NULL,
            ts_nanos INTEGER NOT NULL,
            level TEXT NOT NULL,
            target TEXT NOT NULL,
            feedback_log_body TEXT,
            module_path TEXT,
            file TEXT,
            line INTEGER,
            thread_id TEXT,
            process_uuid TEXT,
            estimated_bytes INTEGER DEFAULT 0
        );
    """)

    now = int(time.time())
    data = []
    for i in range(num_rows):
        ts = now - (10 * 86400) if i < num_rows // 2 else now - (1 * 86400)
        data.append((
            ts, 0, "INFO", "test_target", "A" * 1024, "mod", "file.rs", 100, "t1", "p1", 1024
        ))
    cursor.executemany("""
        INSERT INTO logs (ts, ts_nanos, level, target, feedback_log_body, module_path, file, line, thread_id, process_uuid, estimated_bytes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, data)
    conn.commit()

    if create_freelist:
        cursor.execute("DELETE FROM logs WHERE id <= ?", (num_rows // 4,))
        conn.commit()

    conn.close()


def test_format_bytes():
    assert HYGIENE.format_bytes(500) == "500.00 B"
    assert HYGIENE.format_bytes(1024) == "1.00 KB"
    assert HYGIENE.format_bytes(1024 * 1024 * 5) == "5.00 MB"
    assert HYGIENE.format_bytes(1024 * 1024 * 1024 * 3) == "3.00 GB"


def test_inspect_sqlite_db(tmp_path):
    db_path = tmp_path / "logs_2.sqlite"
    create_mock_logs_db(db_path, num_rows=200, create_freelist=True)

    stats = HYGIENE.inspect_sqlite_db(db_path, table_name="logs", ts_col="ts")
    assert stats is not None
    assert stats.row_count == 150
    assert stats.freelist_count > 0
    assert stats.freelist_bytes > 0


def test_prune_and_vacuum_logs_dry_run(tmp_path):
    db_path = tmp_path / "logs_2.sqlite"
    create_mock_logs_db(db_path, num_rows=500, create_freelist=True)

    initial_stats = HYGIENE.inspect_sqlite_db(db_path, table_name="logs", ts_col="ts")
    assert initial_stats is not None
    assert initial_stats.row_count == 375

    # Dry-run should not change database
    success, msg = HYGIENE.prune_and_vacuum_logs(db_path, keep_days=5, dry_run=True, force=True)
    assert success is True
    assert "[Dry-run]" in msg

    after_stats = HYGIENE.inspect_sqlite_db(db_path, table_name="logs", ts_col="ts")
    assert after_stats is not None
    assert after_stats.row_count == 375


def test_prune_and_vacuum_logs(tmp_path):
    db_path = tmp_path / "logs_2.sqlite"
    create_mock_logs_db(db_path, num_rows=500, create_freelist=True)

    initial_stats = HYGIENE.inspect_sqlite_db(db_path, table_name="logs", ts_col="ts")
    assert initial_stats is not None
    assert initial_stats.row_count == 375

    success, msg = HYGIENE.prune_and_vacuum_logs(db_path, keep_days=5, vacuum=True, force=True)
    assert success is True

    after_stats = HYGIENE.inspect_sqlite_db(db_path, table_name="logs", ts_col="ts")
    assert after_stats is not None
    assert after_stats.row_count == 250
    assert after_stats.freelist_count == 0
    assert after_stats.total_bytes < initial_stats.total_bytes


def test_inspect_codex_runtime(tmp_path):
    codex_dir = tmp_path / ".codex"
    codex_dir.mkdir()
    logs_db = codex_dir / "logs_2.sqlite"
    create_mock_logs_db(logs_db, num_rows=100, create_freelist=False)

    sess_dir = codex_dir / "sessions"
    sess_dir.mkdir()
    (sess_dir / "s1.jsonl").write_text('{"type":"session_meta"}\n')

    arch_dir = codex_dir / "archived_sessions"
    arch_dir.mkdir()
    (arch_dir / "a1.jsonl").write_text('{"type":"session_meta"}\n')

    report = HYGIENE.inspect_codex_runtime(codex_dir)
    assert report["logs_db"] is not None
    assert report["sessions"]["count"] == 1
    assert report["archived_sessions"]["count"] == 1
