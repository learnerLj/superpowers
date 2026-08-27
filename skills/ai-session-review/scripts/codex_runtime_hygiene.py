#!/usr/bin/env python3
"""
Codex runtime hygiene tool: inspects and compacts Codex runtime databases,
especially logs_2.sqlite freelist bloat, while leaving session evidence untouched.
"""

from __future__ import annotations

import argparse
import os
import shutil
import sqlite3
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple


@dataclass
class ProcessHolder:
    pid: int
    command: str
    fd: str


@dataclass
class SqliteDbStats:
    path: Path
    total_bytes: int
    page_size: int
    page_count: int
    freelist_count: int
    freelist_bytes: int
    wal_bytes: int
    row_count: Optional[int] = None
    min_ts: Optional[int] = None
    max_ts: Optional[int] = None


def format_bytes(num_bytes: int) -> str:
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if num_bytes < 1024.0:
            return f"{num_bytes:.2f} {unit}"
        num_bytes /= 1024.0
    return f"{num_bytes:.2f} PB"


def get_active_process_holders(file_path: Path) -> List[ProcessHolder]:
    """Inspect if any process is actively holding open file descriptors on file_path."""
    holders = []
    if not file_path.exists():
        return holders
    try:
        res = subprocess.run(
            ["lsof", "-F", "pcf", str(file_path)],
            capture_output=True,
            text=True,
            check=False,
        )
        if res.returncode == 0 and res.stdout.strip():
            cur_pid = 0
            cur_cmd = ""
            for line in res.stdout.splitlines():
                if line.startswith("p"):
                    cur_pid = int(line[1:])
                elif line.startswith("c"):
                    cur_cmd = line[1:]
                elif line.startswith("f"):
                    holders.append(
                        ProcessHolder(pid=cur_pid, command=cur_cmd, fd=line[1:])
                    )
    except Exception:
        pass
    return holders


def inspect_sqlite_db(db_path: Path, table_name: Optional[str] = None, ts_col: str = "ts") -> Optional[SqliteDbStats]:
    if not db_path.exists():
        return None
    total_bytes = db_path.stat().st_size
    wal_path = Path(f"{db_path}-wal")
    wal_bytes = wal_path.stat().st_size if wal_path.exists() else 0

    try:
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        cursor = conn.cursor()
        cursor.execute("PRAGMA page_size;")
        page_size = cursor.fetchone()[0]
        cursor.execute("PRAGMA page_count;")
        page_count = cursor.fetchone()[0]
        cursor.execute("PRAGMA freelist_count;")
        freelist_count = cursor.fetchone()[0]
        freelist_bytes = freelist_count * page_size

        row_count = None
        min_ts = None
        max_ts = None

        if table_name:
            try:
                cursor.execute(f"SELECT count(*), min({ts_col}), max({ts_col}) FROM {table_name};")
                row = cursor.fetchone()
                if row:
                    row_count, min_ts, max_ts = row
            except Exception:
                pass

        conn.close()
        return SqliteDbStats(
            path=db_path,
            total_bytes=total_bytes,
            page_size=page_size,
            page_count=page_count,
            freelist_count=freelist_count,
            freelist_bytes=freelist_bytes,
            wal_bytes=wal_bytes,
            row_count=row_count,
            min_ts=min_ts,
            max_ts=max_ts,
        )
    except Exception:
        return None


def get_dir_stats(dir_path: Path) -> Tuple[int, int]:
    """Returns (total_bytes, file_count) for a directory."""
    if not dir_path.exists():
        return 0, 0
    total_bytes = 0
    file_count = 0
    for root, _, files in os.walk(dir_path):
        for f in files:
            fp = Path(root) / f
            try:
                if not fp.is_symlink():
                    total_bytes += fp.stat().st_size
                    file_count += 1
            except Exception:
                pass
    return total_bytes, file_count


def inspect_codex_runtime(codex_dir: Path) -> Dict:
    logs_db = codex_dir / "logs_2.sqlite"
    state_db = codex_dir / "state_5.sqlite"
    sessions_dir = codex_dir / "sessions"
    archived_dir = codex_dir / "archived_sessions"

    logs_stats = inspect_sqlite_db(logs_db, table_name="logs", ts_col="ts")
    state_stats = inspect_sqlite_db(state_db, table_name="threads", ts_col="recency_at_ms")
    sessions_bytes, sessions_count = get_dir_stats(sessions_dir)
    archived_bytes, archived_count = get_dir_stats(archived_dir)
    holders = get_active_process_holders(logs_db)

    return {
        "codex_dir": str(codex_dir),
        "logs_db": logs_stats,
        "state_db": state_stats,
        "sessions": {"bytes": sessions_bytes, "count": sessions_count},
        "archived_sessions": {"bytes": archived_bytes, "count": archived_count},
        "process_holders": holders,
    }


def prune_and_vacuum_logs(
    logs_db: Path,
    keep_days: int = 7,
    vacuum: bool = True,
    force: bool = False,
    dry_run: bool = False,
) -> Tuple[bool, str]:
    """Safely prunes old log entries from logs_2.sqlite and vacuums."""
    if not logs_db.exists():
        return False, f"Log database not found at {logs_db}"

    holders = get_active_process_holders(logs_db)
    if holders and not force:
        pids = ", ".join(f"{h.command} (PID {h.pid})" for h in holders)
        return (
            False,
            f"Active process holding locks on log database: {pids}. "
            "Please close Codex processes or pass --force.",
        )

    before_size = logs_db.stat().st_size
    wal_path = Path(f"{logs_db}-wal")
    before_wal = wal_path.stat().st_size if wal_path.exists() else 0

    try:
        conn = sqlite3.connect(str(logs_db), timeout=10.0)
        cursor = conn.cursor()
        cursor.execute("PRAGMA busy_timeout = 5000;")
        cursor.execute("PRAGMA quick_check;")
        check_result = cursor.fetchone()[0]
        if check_result != "ok":
            conn.close()
            return False, f"SQLite integrity check failed before clean: {check_result}"

        deleted_rows = 0
        cutoff_ts = int(time.time()) - (keep_days * 86400) if keep_days >= 0 else None
        if cutoff_ts is not None:
            cursor.execute("SELECT count(*) FROM logs WHERE ts < ?", (cutoff_ts,))
            deleted_rows = cursor.fetchone()[0]

        if dry_run:
            conn.close()
            return (
                True,
                f"[Dry-run] Would prune {deleted_rows:,} log rows older than {keep_days} days. "
                f"Current DB size: {format_bytes(before_size + before_wal)}. No changes applied.",
            )

        if deleted_rows > 0:
            cursor.execute("DELETE FROM logs WHERE ts < ?", (cutoff_ts,))
            conn.commit()

        if vacuum:
            cursor.execute("VACUUM;")

        try:
            cursor.execute("PRAGMA wal_checkpoint(TRUNCATE);")
        except Exception:
            pass

        cursor.execute("PRAGMA quick_check;")
        post_check = cursor.fetchone()[0]
        conn.close()

        if post_check != "ok":
            return False, f"SQLite integrity check failed after vacuum: {post_check}"

        after_size = logs_db.stat().st_size
        after_wal = wal_path.stat().st_size if wal_path.exists() else 0
        freed = (before_size + before_wal) - (after_size + after_wal)

        return (
            True,
            f"Pruned {deleted_rows:,} old log rows (retained last {keep_days} days). "
            f"Database size: {format_bytes(before_size + before_wal)} -> {format_bytes(after_size + after_wal)} "
            f"(Freed: {format_bytes(max(0, freed))})",
        )
    except Exception as e:
        return False, f"Failed to clean log database: {e}"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Inspect and compact Codex runtime logs & SQLite bloat"
    )
    parser.add_argument(
        "--codex-dir",
        default=os.path.expanduser("~/.codex"),
        help="Path to ~/.codex directory",
    )
    parser.add_argument(
        "--inspect",
        action="store_true",
        help="Display size inspection and freelist report",
    )
    parser.add_argument(
        "--clean-logs",
        action="store_true",
        help="Prune old logs in logs_2.sqlite and execute vacuum",
    )
    parser.add_argument(
        "--keep-days",
        type=int,
        default=7,
        help="Number of days of logs to retain when cleaning (default: 7)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate cleanup without modifying database",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force clean even if active processes are detected",
    )

    args = parser.parse_args()
    codex_dir = Path(args.codex_dir)

    if not args.inspect and not args.clean_logs:
        args.inspect = True

    if args.inspect:
        report = inspect_codex_runtime(codex_dir)
        print("=== Codex Storage & Runtime Hygiene Inspection ===")
        print(f"Directory: {report['codex_dir']}")

        logs = report["logs_db"]
        if logs:
            print("\n[Runtime Logs DB - logs_2.sqlite]")
            print(f"  Total Size:       {format_bytes(logs.total_bytes)}")
            print(f"  WAL Size:         {format_bytes(logs.wal_bytes)}")
            print(f"  Freelist Bloat:   {format_bytes(logs.freelist_bytes)} ({logs.freelist_count} empty pages)")
            if logs.row_count is not None:
                print(f"  Total Log Rows:   {logs.row_count:,}")
        else:
            print("\n[Runtime Logs DB] None found")

        state = report["state_db"]
        if state:
            print("\n[State DB - state_5.sqlite]")
            print(f"  Total Size:       {format_bytes(state.total_bytes)}")
            print(f"  WAL Size:         {format_bytes(state.wal_bytes)}")
            if state.row_count is not None:
                print(f"  Total Threads:    {state.row_count:,}")

        sess = report["sessions"]
        arch = report["archived_sessions"]
        print("\n[Session Evidence (Protected Assets)]")
        print(f"  Active Sessions:   {format_bytes(sess['bytes'])} ({sess['count']} files)")
        print(f"  Archived Sessions: {format_bytes(arch['bytes'])} ({arch['count']} files)")

        holders = report["process_holders"]
        if holders:
            print(f"\n[Active Processes Holding Locks: {len(holders)}]")
            for h in holders:
                print(f"  - {h.command} (PID {h.pid}, FD {h.fd})")
        else:
            print("\n[Active Processes Holding Locks] None (Safe to vacuum / checkpoint)")

    if args.clean_logs:
        logs_db = codex_dir / "logs_2.sqlite"
        print(f"\n=== Executing Log Cleanup & VACUUM on {logs_db} ===")
        success, msg = prune_and_vacuum_logs(
            logs_db,
            keep_days=args.keep_days,
            vacuum=True,
            force=args.force,
            dry_run=args.dry_run,
        )
        if success:
            print(f"✓ Success: {msg}")
        else:
            print(f"✗ Failed: {msg}", file=sys.stderr)
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
