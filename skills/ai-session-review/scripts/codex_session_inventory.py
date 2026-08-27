#!/usr/bin/env python3

import argparse
import calendar
import contextlib
import hashlib
import json
import os
import re
import shutil
import sqlite3
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


REQUIRED_COLUMNS = {
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
}
JSON_FIELDS = [
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
]
TABLE_FIELDS = [
    "id",
    "last_active_at",
    "age_bucket",
    "archived",
    "is_pinned",
    "thread_kind",
    "cwd",
    "title",
    "rollout_path",
]
DURATION_RE = re.compile(r"^([1-9][0-9]*)([dwm])$")
MONTH_RE = re.compile(r"^([0-9]{4})-([0-9]{2})$")
WHITESPACE_RE = re.compile(r"\s+")
NON_ALNUM_RE = re.compile(r"[^a-z0-9]+")
SENSITIVE_KEY_MARKERS = (
    "apikey",
    "accesskey",
    "privatekey",
    "token",
    "oauth",
    "authorization",
    "cookie",
    "password",
    "passwd",
    "secret",
    "credential",
)
AUTH_HEADER_RE = re.compile(
    r"\b(authorization|proxy-authorization|cookie|set-cookie)(\s*:\s*)[^\r\n]+",
    re.IGNORECASE,
)
SENSITIVE_PAIR_RE = re.compile(
    r"(?<![A-Za-z0-9_-])([A-Za-z][A-Za-z0-9_-]*)(\s*[:=]\s*)"
    r"(?:\"[^\"]*\"|'[^']*'|[^\s,;&]+)",
)
BEARER_RE = re.compile(r"\bBearer\s+[^\s,;]+", re.IGNORECASE)
URI_RE = re.compile(r"\b[A-Za-z][A-Za-z0-9+.-]*://[^\s,;\"']+")
REDACTED = "[REDACTED]"
SNAPSHOT_ATTEMPTS = 3
DB_FALLBACK_HINT = (
    "Fallback: see references/codex.md section 11, "
    "Restricted JSONL fallback"
)


class InventoryError(ValueError):
    pass


class SnapshotChangedError(RuntimeError):
    pass


@dataclass(frozen=True)
class FileSignature:
    device: int
    inode: int
    size: int
    mtime_ns: int
    ctime_ns: int
    sha256: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="只读列出 Codex Desktop state DB 中的会话清单。"
    )
    parser.add_argument(
        "--db",
        default="~/.codex/state_5.sqlite",
        help="Codex Desktop state SQLite path",
    )
    parser.add_argument("--id", action="append", default=[], help="精确 session ID，可重复")
    parser.add_argument("--older-than", help="最后活动早于 duration，如 7d、1m")
    parser.add_argument("--newer-than", help="最后活动晚于或等于 duration 起点")
    parser.add_argument("--from", dest="from_date", help="本地日期闭区间起点")
    parser.add_argument("--to", dest="to_date", help="本地日期开区间终点")
    parser.add_argument("--month", help="活动跨度相交的本地自然月 YYYY-MM")
    parser.add_argument("--cwd", help="精确匹配 cwd 字符串")
    parser.add_argument(
        "--include-subagents",
        action="store_true",
        help="包含 subagent，仍排除 other",
    )
    parser.add_argument(
        "--archived",
        choices=("active", "archived", "all"),
        default="all",
        help="按 Desktop archived 状态筛选",
    )
    parser.add_argument(
        "--timezone",
        default="Asia/Shanghai",
        help="IANA timezone for output and local boundaries",
    )
    parser.add_argument(
        "--format",
        choices=("table", "jsonl"),
        default="table",
        help="输出无引号 TSV 或 JSONL",
    )
    parser.add_argument("--now", help="固定当前时点，默认系统当前时间")
    return parser.parse_args()


def timezone_from_name(name: str) -> ZoneInfo:
    try:
        return ZoneInfo(name)
    except (ZoneInfoNotFoundError, ValueError) as exc:
        raise InventoryError(f"--timezone: unknown IANA timezone {name!r}") from exc


def parse_now(value: str | None, output_timezone: ZoneInfo) -> datetime:
    if value is None:
        return datetime.now(output_timezone)
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as exc:
        raise InventoryError(f"--now: invalid ISO 8601 timestamp {value!r}") from exc
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=output_timezone)
    return parsed.astimezone(output_timezone)


def parse_local_date(value: str, option: str, output_timezone: ZoneInfo) -> datetime:
    try:
        parsed = datetime.strptime(value, "%Y-%m-%d")
    except ValueError as exc:
        raise InventoryError(f"{option}: invalid date {value!r}, expected YYYY-MM-DD") from exc
    return parsed.replace(tzinfo=output_timezone)


def parse_month(value: str, output_timezone: ZoneInfo) -> tuple[datetime, datetime]:
    match = MONTH_RE.fullmatch(value)
    if match is None:
        raise InventoryError(f"--month: invalid month {value!r}, expected YYYY-MM")
    year, month = (int(part) for part in match.groups())
    if not 1 <= month <= 12:
        raise InventoryError(f"--month: invalid month {value!r}, expected YYYY-MM")
    start = datetime(year, month, 1, tzinfo=output_timezone)
    if month == 12:
        end = datetime(year + 1, 1, 1, tzinfo=output_timezone)
    else:
        end = datetime(year, month + 1, 1, tzinfo=output_timezone)
    return start, end


def subtract_calendar_months(value: datetime, months: int) -> datetime:
    month_index = value.year * 12 + value.month - 1 - months
    year, zero_based_month = divmod(month_index, 12)
    month = zero_based_month + 1
    day = min(value.day, calendar.monthrange(year, month)[1])
    return value.replace(year=year, month=month, day=day)


def duration_cutoff(value: str, option: str, now: datetime) -> datetime:
    match = DURATION_RE.fullmatch(value)
    if match is None:
        raise InventoryError(
            f"{option}: duration must be a positive integer followed by d, w, or m"
        )
    amount = int(match.group(1))
    unit = match.group(2)
    if unit == "d":
        delta = timedelta(days=amount)
        return (now.astimezone(timezone.utc) - delta).astimezone(now.tzinfo)
    if unit == "w":
        delta = timedelta(days=amount * 7)
        return (now.astimezone(timezone.utc) - delta).astimezone(now.tzinfo)
    return subtract_calendar_months(now, amount)


def to_epoch_ms(value: datetime) -> int:
    return int(value.timestamp() * 1000)


def validate_filter_combinations(args: argparse.Namespace) -> None:
    recency_options = {
        "--older-than": args.older_than,
        "--newer-than": args.newer_than,
        "--from": args.from_date,
        "--to": args.to_date,
    }
    active_recency = [name for name, value in recency_options.items() if value is not None]
    if args.month is not None and active_recency:
        raise InventoryError(
            f"--month cannot be combined with recency filters: {', '.join(active_recency)}"
        )

    if args.id:
        conflicts = []
        if args.cwd is not None:
            conflicts.append("--cwd")
        if args.month is not None:
            conflicts.append("--month")
        conflicts.extend(active_recency)
        if args.archived != "all":
            conflicts.append("--archived")
        if conflicts:
            raise InventoryError(
                f"--id cannot be combined with discovery filters: {', '.join(conflicts)}"
            )


def build_recency_window(
    args: argparse.Namespace,
    now: datetime,
    output_timezone: ZoneInfo,
) -> tuple[int | None, int | None]:
    lower_bounds: list[datetime] = []
    upper_bounds: list[datetime] = []
    if args.newer_than is not None:
        lower_bounds.append(duration_cutoff(args.newer_than, "--newer-than", now))
    if args.from_date is not None:
        lower_bounds.append(parse_local_date(args.from_date, "--from", output_timezone))
    if args.older_than is not None:
        upper_bounds.append(duration_cutoff(args.older_than, "--older-than", now))
    if args.to_date is not None:
        upper_bounds.append(parse_local_date(args.to_date, "--to", output_timezone))

    lower = max(lower_bounds) if lower_bounds else None
    upper = min(upper_bounds) if upper_bounds else None
    if lower is not None and upper is not None and lower >= upper:
        raise InventoryError("recency window is empty or reversed after intersecting filters")
    return (
        to_epoch_ms(lower) if lower is not None else None,
        to_epoch_ms(upper) if upper is not None else None,
    )


def normalize_db_path(raw_path: str) -> Path:
    expanded = os.path.expanduser(raw_path)
    return Path(os.path.abspath(expanded))


def with_db_fallback(message: str) -> InventoryError:
    return InventoryError(f"{message}. {DB_FALLBACK_HINT}")


def stat_identity(stat: os.stat_result) -> tuple[int, int, int, int, int]:
    return (
        stat.st_dev,
        stat.st_ino,
        stat.st_size,
        stat.st_mtime_ns,
        stat.st_ctime_ns,
    )


def file_signature(path: Path) -> FileSignature | None:
    try:
        with path.open("rb") as source:
            before = os.fstat(source.fileno())
            digest = hashlib.sha256()
            while chunk := source.read(1024 * 1024):
                digest.update(chunk)
            after = os.fstat(source.fileno())
    except FileNotFoundError:
        return None

    try:
        current = path.stat()
    except FileNotFoundError as exc:
        raise SnapshotChangedError(f"{path.name} disappeared") from exc
    if stat_identity(before) != stat_identity(after):
        raise SnapshotChangedError(f"{path.name} changed while hashing")
    if stat_identity(after) != stat_identity(current):
        raise SnapshotChangedError(f"{path.name} was replaced while hashing")
    return FileSignature(*stat_identity(after), digest.hexdigest())


def sqlite_file_state(db_path: Path) -> dict[str, FileSignature | None]:
    state = {
        suffix: file_signature(Path(str(db_path) + suffix))
        for suffix in ("", "-wal", "-shm")
    }
    if state[""] is None:
        raise SnapshotChangedError(f"{db_path.name} disappeared")
    return state


def same_content(left: FileSignature | None, right: FileSignature | None) -> bool:
    if left is None or right is None:
        return left is right
    return (left.size, left.sha256) == (right.size, right.sha256)


def create_stable_snapshot(db_path: Path, temp_root: Path) -> Path:
    last_change = "source files changed"
    for attempt in range(1, SNAPSHOT_ATTEMPTS + 1):
        attempt_dir = temp_root / f"attempt-{attempt}"
        attempt_dir.mkdir()
        snapshot_path = attempt_dir / db_path.name
        try:
            before = sqlite_file_state(db_path)
            shutil.copy2(db_path, snapshot_path)
            if before["-wal"] is not None:
                shutil.copy2(
                    Path(str(db_path) + "-wal"),
                    Path(str(snapshot_path) + "-wal"),
                )
            after = sqlite_file_state(db_path)
            copied_db = file_signature(snapshot_path)
            copied_wal = file_signature(Path(str(snapshot_path) + "-wal"))
        except (OSError, SnapshotChangedError) as exc:
            last_change = str(exc)
            continue

        if before != after:
            last_change = "DB, WAL, or SHM changed during copy"
            continue
        if not same_content(copied_db, after[""]) or not same_content(
            copied_wal, after["-wal"]
        ):
            last_change = "copied DB or WAL does not match the stable source"
            continue
        return snapshot_path

    raise with_db_fallback(
        f"--db: cannot obtain a stable SQLite snapshot after "
        f"{SNAPSHOT_ATTEMPTS} attempts: {last_change}"
    )


@contextlib.contextmanager
def open_database(db_path: Path):
    if not db_path.is_file():
        raise with_db_fallback(f"--db: SQLite file does not exist: {db_path}")
    with tempfile.TemporaryDirectory(prefix="codex-session-inventory-") as temp_dir:
        snapshot_path = create_stable_snapshot(db_path, Path(temp_dir))

        uri = snapshot_path.as_uri() + "?mode=ro"
        try:
            connection = sqlite3.connect(uri, uri=True)
        except sqlite3.Error as exc:
            raise with_db_fallback(f"--db: cannot open SQLite read-only: {exc}") from exc
        connection.row_factory = sqlite3.Row
        try:
            yield connection
        finally:
            connection.close()


def validate_schema(connection: sqlite3.Connection) -> None:
    try:
        rows = connection.execute("PRAGMA table_info(threads)").fetchall()
    except sqlite3.Error as exc:
        raise InventoryError(f"--db: cannot inspect threads schema: {exc}") from exc
    available = {row["name"] for row in rows}
    missing = sorted(REQUIRED_COLUMNS - available)
    if missing:
        raise with_db_fallback(
            "--db: threads schema missing required columns: " + ", ".join(missing)
        )


def load_threads(connection: sqlite3.Connection) -> list[dict[str, Any]]:
    columns = [
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
    try:
        rows = connection.execute(
            f"SELECT {', '.join(columns)} FROM threads"
        ).fetchall()
    except sqlite3.Error as exc:
        raise InventoryError(f"--db: cannot read threads: {exc}") from exc
    return [dict(row) for row in rows]


def parse_source(raw_source: Any) -> Any:
    if not isinstance(raw_source, str):
        return raw_source

    def reject_constant(_: str) -> None:
        raise ValueError

    try:
        return json.loads(raw_source, parse_constant=reject_constant)
    except (json.JSONDecodeError, ValueError):
        return raw_source


def classify_thread(thread_source: Any, source: Any) -> str:
    if thread_source == "subagent" or (
        isinstance(source, dict) and "subagent" in source
    ):
        return "subagent"
    if thread_source == "user" or source in ("cli", "vscode"):
        return "user"
    return "other"


def require_epoch_ms(row: dict[str, Any], field: str) -> int:
    value = row[field]
    if isinstance(value, bool) or not isinstance(value, int):
        raise InventoryError(
            f"--db: thread {row.get('id')!r} has invalid integer {field}: {value!r}"
        )
    return value


def prepare_threads(raw_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    prepared = []
    for row in raw_rows:
        source = parse_source(row["source"])
        row["source"] = source
        row["thread_kind"] = classify_thread(row["thread_source"], source)
        row["created_at_ms"] = require_epoch_ms(row, "created_at_ms")
        row["recency_at_ms"] = require_epoch_ms(row, "recency_at_ms")
        prepared.append(row)
    return prepared


def deduplicate(values: list[str]) -> list[str]:
    return list(dict.fromkeys(values))


def select_exact_ids(
    rows: list[dict[str, Any]],
    requested_ids: list[str],
    include_subagents: bool,
) -> list[dict[str, Any]]:
    unique_ids = deduplicate(requested_ids)
    by_id = {row["id"]: row for row in rows}
    missing = [session_id for session_id in unique_ids if session_id not in by_id]
    other = [
        session_id
        for session_id in unique_ids
        if session_id in by_id and by_id[session_id]["thread_kind"] == "other"
    ]
    excluded_subagents = [
        session_id
        for session_id in unique_ids
        if session_id in by_id
        and by_id[session_id]["thread_kind"] == "subagent"
        and not include_subagents
    ]
    failures = []
    if missing:
        failures.append("missing=" + ",".join(missing))
    if other:
        failures.append("other=" + ",".join(other))
    if excluded_subagents:
        failures.append("subagent_requires_--include-subagents=" + ",".join(excluded_subagents))
    if failures:
        raise InventoryError("--id selection failed: " + "; ".join(failures))
    return [by_id[session_id] for session_id in unique_ids]


def filter_discovery(
    rows: list[dict[str, Any]],
    args: argparse.Namespace,
    lower_ms: int | None,
    upper_ms: int | None,
    month_window: tuple[int, int] | None,
) -> list[dict[str, Any]]:
    allowed_kinds = {"user", "subagent"} if args.include_subagents else {"user"}
    selected = []
    for row in rows:
        if row["thread_kind"] not in allowed_kinds:
            continue
        if args.cwd is not None and row["cwd"] != args.cwd:
            continue
        archived = bool(row["archived"])
        if args.archived == "active" and archived:
            continue
        if args.archived == "archived" and not archived:
            continue
        recency_ms = row["recency_at_ms"]
        if lower_ms is not None and recency_ms < lower_ms:
            continue
        if upper_ms is not None and recency_ms >= upper_ms:
            continue
        if month_window is not None:
            month_start_ms, month_end_ms = month_window
            if not (
                row["created_at_ms"] < month_end_ms
                and recency_ms >= month_start_ms
            ):
                continue
        selected.append(row)
    return selected


def age_bucket(recency_ms: int, now_ms: int) -> str:
    age_ms = now_ms - recency_ms
    if age_ms < 7 * 24 * 60 * 60 * 1000:
        return "active"
    if age_ms < 30 * 24 * 60 * 60 * 1000:
        return "cooling"
    return "mature"


def iso_timestamp(epoch_ms: int, output_timezone: ZoneInfo) -> str:
    value = datetime.fromtimestamp(epoch_ms / 1000, tz=timezone.utc)
    return value.astimezone(output_timezone).isoformat()


def is_sensitive_key(key: Any) -> bool:
    canonical = NON_ALNUM_RE.sub("", str(key).casefold())
    if any(marker in canonical for marker in SENSITIVE_KEY_MARKERS):
        return True
    return (
        canonical == "auth"
        or canonical.startswith("auth")
        or canonical.endswith("auth")
        or canonical == "pat"
        or canonical.endswith("pat")
    )


def redact_uri(match: re.Match[str]) -> str:
    raw_uri = match.group(0)
    try:
        parts = urlsplit(raw_uri)
        netloc = parts.netloc
        query = parse_qsl(parts.query, keep_blank_values=True)
    except ValueError:
        return raw_uri

    changed = False
    if "@" in netloc:
        netloc = REDACTED + "@" + netloc.rsplit("@", 1)[1]
        changed = True

    redacted_query = []
    for key, item in query:
        if is_sensitive_key(key):
            redacted_query.append((key, REDACTED))
            changed = True
        else:
            redacted_query.append((key, item))
    if not changed:
        return raw_uri
    return urlunsplit(
        (
            parts.scheme,
            netloc,
            parts.path,
            urlencode(redacted_query, doseq=True, safe="[]"),
            parts.fragment,
        )
    )


def redact_sensitive_pair(match: re.Match[str]) -> str:
    if not is_sensitive_key(match.group(1)):
        return match.group(0)
    return match.group(1) + match.group(2) + REDACTED


def redact_credentials(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: REDACTED if is_sensitive_key(key) else redact_credentials(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [redact_credentials(item) for item in value]
    if not isinstance(value, str):
        return value

    redacted = AUTH_HEADER_RE.sub(lambda match: match.group(1) + match.group(2) + REDACTED, value)
    redacted = URI_RE.sub(redact_uri, redacted)
    redacted = SENSITIVE_PAIR_RE.sub(
        redact_sensitive_pair,
        redacted,
    )
    return BEARER_RE.sub("Bearer " + REDACTED, redacted)


def output_record(
    row: dict[str, Any],
    now_ms: int,
    output_timezone: ZoneInfo,
) -> dict[str, Any]:
    record = {
        "id": row["id"],
        "title": redact_credentials(row["title"] if row["title"] is not None else ""),
        "cwd": redact_credentials(row["cwd"] if row["cwd"] is not None else ""),
        "rollout_path": redact_credentials(
            row["rollout_path"] if row["rollout_path"] is not None else ""
        ),
        "created_at": iso_timestamp(row["created_at_ms"], output_timezone),
        "last_active_at": iso_timestamp(row["recency_at_ms"], output_timezone),
        "age_bucket": age_bucket(row["recency_at_ms"], now_ms),
        "archived": bool(row["archived"]),
        "is_pinned": bool(row["is_pinned"]),
        "thread_kind": row["thread_kind"],
        "model": redact_credentials(row["model"]),
        "source": redact_credentials(row["source"]),
    }
    return {field: record[field] for field in JSON_FIELDS}


def table_cell(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        rendered = json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
    else:
        rendered = str(value)
    return WHITESPACE_RE.sub(" ", rendered).strip()


def write_output(records: list[dict[str, Any]], output_format: str) -> None:
    if output_format == "jsonl":
        for record in records:
            print(json.dumps(record, ensure_ascii=False, separators=(",", ":")))
        return
    print("\t".join(TABLE_FIELDS))
    for record in records:
        print("\t".join(table_cell(record[field]) for field in TABLE_FIELDS))


def run(args: argparse.Namespace) -> None:
    validate_filter_combinations(args)
    output_timezone = timezone_from_name(args.timezone)
    now = parse_now(args.now, output_timezone)
    now_ms = to_epoch_ms(now)
    lower_ms, upper_ms = build_recency_window(args, now, output_timezone)

    month_window = None
    if args.month is not None:
        month_start, month_end = parse_month(args.month, output_timezone)
        month_window = (to_epoch_ms(month_start), to_epoch_ms(month_end))

    db_path = normalize_db_path(args.db)
    with open_database(db_path) as connection:
        validate_schema(connection)
        rows = prepare_threads(load_threads(connection))

    if args.id:
        selected = select_exact_ids(rows, args.id, args.include_subagents)
    else:
        selected = filter_discovery(
            rows,
            args,
            lower_ms,
            upper_ms,
            month_window,
        )

    selected.sort(key=lambda row: (row["recency_at_ms"], row["id"]))
    records = []
    for row in selected:
        if row["recency_at_ms"] > now_ms:
            print(
                f"warning: session {row['id']} has future last activity "
                f"{iso_timestamp(row['recency_at_ms'], output_timezone)}",
                file=sys.stderr,
            )
        records.append(output_record(row, now_ms, output_timezone))
    write_output(records, args.format)


def main() -> int:
    args = parse_args()
    try:
        run(args)
    except (InventoryError, sqlite3.Error, OSError, OverflowError) as exc:
        print(f"codex_session_inventory.py: error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
