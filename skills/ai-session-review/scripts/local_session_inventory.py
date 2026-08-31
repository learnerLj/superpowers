#!/usr/bin/env python3

import argparse
import base64
import calendar
import json
import os
import re
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


SOURCES = (
    "grok-build",
    "grok-bot",
    "gemini-cli",
    "antigravity-desktop",
    "antigravity-cli",
    "claude-code",
    "claude-transcripts",
)
SOURCE_ORDER = {source: index for index, source in enumerate(SOURCES)}
TABLE_FIELDS = (
    "source",
    "id",
    "last_active_at",
    "age_bucket",
    "thread_kind",
    "cwd",
    "title",
    "model",
    "evidence_status",
    "transcript_path",
)
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
GROK_BOT_KEY_RE = re.compile(
    r"^sand\.client\.slice\.account\.(.+?)\.transcript\.replicas\.(.+)$"
)
GROK_UPDATE_TYPES = {
    "user_message_chunk",
    "agent_message_chunk",
    "agent_thought_chunk",
    "tool_call",
    "tool_call_update",
    "plan",
    "turn_completed",
}
GROK_BOT_ENTRY_KINDS = {"send-message", "message", "event"}
REDACTED = "[REDACTED]"


class InventoryError(ValueError):
    pass


@dataclass
class SessionRecord:
    source: str
    id: str
    title: str | None
    cwd: str | None
    transcript_path: str
    created_at: datetime | None
    last_active_at: datetime | None
    age_bucket: str
    thread_kind: str
    model: str | None
    evidence_status: str

    def to_json(self, output_timezone: ZoneInfo) -> dict[str, Any]:
        row = asdict(self)
        row["created_at"] = format_timestamp(self.created_at, output_timezone)
        row["last_active_at"] = format_timestamp(
            self.last_active_at, output_timezone
        )
        return redact_credentials(row)


@dataclass(frozen=True)
class JsonlResult:
    records: list[dict[str, Any]]
    malformed: bool


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="只读列出 Grok Build、Grok Bot、Gemini CLI、Antigravity 和 Claude 本地会话。"
    )
    parser.add_argument(
        "--source", choices=("all", *SOURCES), default="all", help="本地会话来源"
    )
    parser.add_argument("--id", action="append", default=[], help="精确 session ID，可重复")
    parser.add_argument("--cwd", help="精确匹配 cwd")
    parser.add_argument("--older-than", help="最后活动早于 duration，如 7d、1m")
    parser.add_argument("--newer-than", help="最后活动晚于或等于 duration 起点")
    parser.add_argument("--from", dest="from_date", help="本地日期闭区间起点")
    parser.add_argument("--to", dest="to_date", help="本地日期开区间终点")
    parser.add_argument("--month", help="活动跨度相交的本地自然月 YYYY-MM")
    parser.add_argument(
        "--include-subagents", action="store_true", help="包含本地 subagent 会话"
    )
    parser.add_argument(
        "--timezone", default="Asia/Shanghai", help="输出与筛选使用的 IANA timezone"
    )
    parser.add_argument(
        "--format", choices=("table", "jsonl"), default="table", help="输出格式"
    )
    parser.add_argument("--now", help="固定当前时点，默认系统当前时间")
    parser.add_argument(
        "--grok-home",
        default=os.environ.get("GROK_HOME", "~/.grok"),
        help="Grok Build 数据根，默认读取 GROK_HOME 或 ~/.grok",
    )
    parser.add_argument(
        "--grok-bot-data",
        default="~/Library/Application Support/Grok Bot",
        help="Grok Bot Application Support 根",
    )
    parser.add_argument("--gemini-home", default="~/.gemini", help="Gemini 数据根")
    parser.add_argument("--claude-home", default="~/.claude", help="Claude / OpenCode 数据根")
    return parser.parse_args()


def timezone_from_name(name: str) -> ZoneInfo:
    try:
        return ZoneInfo(name)
    except (ZoneInfoNotFoundError, ValueError) as exc:
        raise InventoryError(f"--timezone: unknown IANA timezone {name!r}") from exc


def parse_timestamp(value: Any) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        seconds = float(value) / 1000 if value > 10_000_000_000 else float(value)
        try:
            return datetime.fromtimestamp(seconds, timezone.utc)
        except (OverflowError, OSError, ValueError):
            return None
    if not isinstance(value, str) or not value.strip():
        return None
    normalized = value.strip().replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed


def format_timestamp(value: datetime | None, output_timezone: ZoneInfo) -> str | None:
    if value is None:
        return None
    return value.astimezone(output_timezone).isoformat()


def parse_now(value: str | None, output_timezone: ZoneInfo) -> datetime:
    if value is None:
        return datetime.now(output_timezone)
    parsed = parse_timestamp(value)
    if parsed is None:
        raise InventoryError(f"--now: invalid ISO 8601 timestamp {value!r}")
    return parsed.astimezone(output_timezone)


def parse_local_date(value: str, option: str, output_timezone: ZoneInfo) -> datetime:
    try:
        return datetime.strptime(value, "%Y-%m-%d").replace(tzinfo=output_timezone)
    except ValueError as exc:
        raise InventoryError(f"{option}: invalid date {value!r}, expected YYYY-MM-DD") from exc


def parse_month(value: str, output_timezone: ZoneInfo) -> tuple[datetime, datetime]:
    match = MONTH_RE.fullmatch(value)
    if match is None:
        raise InventoryError(f"--month: invalid month {value!r}, expected YYYY-MM")
    year, month = (int(part) for part in match.groups())
    if not 1 <= month <= 12:
        raise InventoryError(f"--month: invalid month {value!r}, expected YYYY-MM")
    start = datetime(year, month, 1, tzinfo=output_timezone)
    end = (
        datetime(year + 1, 1, 1, tzinfo=output_timezone)
        if month == 12
        else datetime(year, month + 1, 1, tzinfo=output_timezone)
    )
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
    if unit == "m":
        return subtract_calendar_months(now, amount)
    days = amount if unit == "d" else amount * 7
    return (now.astimezone(timezone.utc) - timedelta(days=days)).astimezone(
        now.tzinfo
    )


def age_bucket(last_active_at: datetime | None, now: datetime) -> str:
    if last_active_at is None:
        return "unavailable"
    age = now.astimezone(timezone.utc) - last_active_at.astimezone(timezone.utc)
    if age < timedelta(days=7):
        return "active"
    if age < timedelta(days=30):
        return "cooling"
    return "mature"


def clean_title(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    title = WHITESPACE_RE.sub(" ", value).strip()
    if not title:
        return None
    return title[:240]


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

    redacted_query: list[tuple[str, str]] = []
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

    redacted = AUTH_HEADER_RE.sub(
        lambda match: match.group(1) + match.group(2) + REDACTED, value
    )
    redacted = URI_RE.sub(redact_uri, redacted)
    redacted = SENSITIVE_PAIR_RE.sub(redact_sensitive_pair, redacted)
    return BEARER_RE.sub("Bearer " + REDACTED, redacted)


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return None


def read_jsonl(path: Path) -> JsonlResult:
    records: list[dict[str, Any]] = []
    malformed = False
    try:
        with path.open(encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    malformed = True
                    continue
                if isinstance(record, dict):
                    records.append(record)
                else:
                    malformed = True
    except (OSError, UnicodeDecodeError):
        return JsonlResult([], True)
    return JsonlResult(records, malformed)


def build_record(
    *,
    source: str,
    session_id: str,
    title: Any,
    cwd: Any,
    transcript_path: Path | str,
    created_at: datetime | None,
    last_active_at: datetime | None,
    now: datetime,
    thread_kind: str = "user",
    model: Any = None,
    available: bool = True,
) -> SessionRecord:
    return SessionRecord(
        source=source,
        id=session_id,
        title=clean_title(title),
        cwd=cwd if isinstance(cwd, str) and cwd else None,
        transcript_path=(
            str(transcript_path.resolve())
            if isinstance(transcript_path, Path)
            else transcript_path
        ),
        created_at=created_at,
        last_active_at=last_active_at,
        age_bucket=age_bucket(last_active_at, now),
        thread_kind=thread_kind,
        model=model if isinstance(model, str) and model else None,
        evidence_status="available" if available else "unavailable",
    )


CLAUDE_TITLE_SKIP_PREFIXES = (
    "[search-mode]",
    "[analyze-mode]",
    "[BACKGROUND TASK",
    "[SYSTEM REMINDER",
    "<command-instruction>",
    "<command-name>",
    "<local-command",
    "1. TASK:",
    "Caveat: The messages below",
)


def flatten_claude_content(value: Any, depth: int = 0) -> str:
    if depth > 6 or value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return "\n".join(
            part
            for item in value
            for part in [flatten_claude_content(item, depth + 1)]
            if part
        )
    if isinstance(value, dict):
        item_type = value.get("type")
        if item_type in {"tool_result", "tool_use", "image", "thinking"}:
            return ""
        if isinstance(value.get("text"), str):
            return value["text"]
        if "content" in value:
            return flatten_claude_content(value.get("content"), depth + 1)
        return ""
    return ""


def claude_user_text(record: dict[str, Any]) -> str | None:
    if record.get("type") not in {"user", "human"}:
        return None
    if record.get("isSidechain"):
        return None
    message = record.get("message")
    if isinstance(message, dict):
        content = message.get("content")
    elif isinstance(message, str):
        content = message
    else:
        content = record.get("content")
    if (
        isinstance(content, list)
        and content
        and isinstance(content[0], dict)
        and content[0].get("type") == "tool_result"
    ):
        return None
    text = flatten_claude_content(content).strip()
    return text or None


def claude_title(records: list[dict[str, Any]]) -> str | None:
    for record in records:
        text = claude_user_text(record)
        if not text:
            continue
        if text.startswith(CLAUDE_TITLE_SKIP_PREFIXES):
            continue
        return clean_title(text)
    return None


def claude_timestamps(records: list[dict[str, Any]]) -> list[datetime]:
    timestamps: list[datetime] = []
    for record in records:
        parsed = parse_timestamp(record.get("timestamp"))
        if parsed is not None:
            timestamps.append(parsed)
    return timestamps


def claude_cwd(records: list[dict[str, Any]]) -> str | None:
    for record in records:
        cwd = record.get("cwd")
        if isinstance(cwd, str) and cwd:
            return cwd
    return None


def claude_record_available(result: JsonlResult) -> bool:
    if result.malformed or not result.records:
        return False
    return any(
        isinstance(record.get("type"), str) and bool(record["type"])
        for record in result.records
    )


def discover_claude_code(root: Path, now: datetime) -> Iterable[SessionRecord]:
    projects = root / "projects"
    if not projects.is_dir():
        return
    for path in sorted(projects.rglob("*.jsonl")):
        if not path.is_file():
            continue
        result = read_jsonl(path)
        timestamps = claude_timestamps(result.records)
        thread_kind = "subagent" if "subagents" in path.parts else "user"
        yield build_record(
            source="claude-code",
            session_id=path.stem,
            title=claude_title(result.records),
            cwd=claude_cwd(result.records),
            transcript_path=path,
            created_at=min(timestamps, default=None),
            last_active_at=max(timestamps, default=None),
            now=now,
            thread_kind=thread_kind,
            available=claude_record_available(result),
        )


def discover_claude_transcripts(root: Path, now: datetime) -> Iterable[SessionRecord]:
    transcripts = root / "transcripts"
    if not transcripts.is_dir():
        return
    for path in sorted(transcripts.glob("*.jsonl")):
        if not path.is_file():
            continue
        result = read_jsonl(path)
        timestamps = claude_timestamps(result.records)
        yield build_record(
            source="claude-transcripts",
            session_id=path.stem,
            title=claude_title(result.records),
            cwd=claude_cwd(result.records),
            transcript_path=path,
            created_at=min(timestamps, default=None),
            last_active_at=max(timestamps, default=None),
            now=now,
            thread_kind="user",
            available=claude_record_available(result),
        )


def discover_grok_build(root: Path, now: datetime) -> Iterable[SessionRecord]:
    sessions_root = root / "sessions"
    if not sessions_root.is_dir():
        return
    for summary_path in sorted(sessions_root.glob("*/*/summary.json")):
        summary = read_json(summary_path)
        if not isinstance(summary, dict):
            continue
        info = summary.get("info") if isinstance(summary.get("info"), dict) else {}
        directory_id = summary_path.parent.name
        metadata_id = info.get("id")
        session_id = metadata_id or directory_id
        if not isinstance(session_id, str) or not session_id:
            continue
        session_kind = summary.get("session_kind")
        thread_kind = (
            "subagent"
            if session_kind in {"subagent", "subagent_resume"}
            else "user"
        )
        transcript = summary_path.parent / "updates.jsonl"
        transcript_result = read_jsonl(transcript)
        recognized_update = any(
            record.get("method") == "session/update"
            and isinstance(record.get("params"), dict)
            and isinstance(record["params"].get("update"), dict)
            and record["params"]["update"].get("sessionUpdate")
            in GROK_UPDATE_TYPES
            for record in transcript_result.records
        )
        cwd = info.get("cwd")
        if not isinstance(cwd, str) or not cwd:
            try:
                cwd = (summary_path.parent.parent / ".cwd").read_text(
                    encoding="utf-8"
                ).strip() or None
            except OSError:
                cwd = None
        created = parse_timestamp(summary.get("created_at"))
        last_active = parse_timestamp(
            summary.get("last_active_at") or summary.get("updated_at")
        )
        yield build_record(
            source="grok-build",
            session_id=session_id,
            title=summary.get("generated_title") or summary.get("session_summary"),
            cwd=cwd,
            transcript_path=transcript,
            created_at=created,
            last_active_at=last_active,
            now=now,
            thread_kind=thread_kind,
            model=summary.get("current_model_id"),
            available=(
                transcript.is_file()
                and metadata_id == directory_id
                and recognized_update
                and not transcript_result.malformed
            ),
        )


def decode_grok_bot_key(path: Path) -> str | None:
    encoded = path.stem.upper()
    encoded += "=" * ((8 - len(encoded) % 8) % 8)
    try:
        return base64.b32decode(encoded).decode("utf-8")
    except (ValueError, UnicodeDecodeError):
        return None


def discover_grok_bot(root: Path, now: datetime) -> Iterable[SessionRecord]:
    persistence = root / "sand-client-persistence"
    if not persistence.is_dir():
        return
    for path in sorted(persistence.glob("*.blob")):
        key = decode_grok_bot_key(path)
        match = GROK_BOT_KEY_RE.fullmatch(key or "")
        if match is None:
            continue
        session_id = match.group(2)
        document = read_json(path)
        value = document.get("value") if isinstance(document, dict) else None
        entries = value.get("entries") if isinstance(value, dict) else None
        if not isinstance(entries, list):
            entries = []
        timestamps = [
            timestamp
            for entry in entries
            if isinstance(entry, dict)
            for timestamp in [parse_timestamp(entry.get("timestampMs"))]
            if timestamp is not None
        ]
        title = None
        for entry in entries:
            if not isinstance(entry, dict) or entry.get("kind") != "send-message":
                continue
            message = entry.get("message")
            if isinstance(message, dict) and message.get("type") == "text":
                title = message.get("content")
                if clean_title(title):
                    break
        persisted = parse_timestamp(value.get("persistedAt")) if isinstance(value, dict) else None
        last_active = max([*timestamps, *([persisted] if persisted else [])], default=None)
        yield build_record(
            source="grok-bot",
            session_id=session_id,
            title=title,
            cwd=None,
            transcript_path=f"grok-bot://transcript/{session_id}",
            created_at=min(timestamps, default=last_active),
            last_active_at=last_active,
            now=now,
            available=any(
                isinstance(entry, dict)
                and entry.get("kind") in GROK_BOT_ENTRY_KINDS
                for entry in entries
            ),
        )


def content_to_text(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return "".join(
            part.get("text", "")
            for part in value
            if isinstance(part, dict) and isinstance(part.get("text"), str)
        )
    if isinstance(value, dict) and isinstance(value.get("text"), str):
        return value["text"]
    return ""


def is_resumable_gemini_user(text: str) -> bool:
    stripped = text.strip()
    return bool(stripped) and not stripped.startswith(
        ("/", "?", "<session_context>", "<hook_context>")
    )


def gemini_project_map(root: Path) -> dict[str, str]:
    registry = read_json(root / "projects.json")
    projects = registry.get("projects") if isinstance(registry, dict) else None
    if not isinstance(projects, dict):
        return {}
    return {
        project_id: cwd
        for cwd, project_id in projects.items()
        if isinstance(cwd, str) and isinstance(project_id, str)
    }


def parse_gemini_session(
    path: Path,
) -> tuple[dict[str, Any], list[dict[str, Any]], bool]:
    metadata: dict[str, Any] = {}
    messages: dict[str, dict[str, Any]] = {}
    order: list[str] = []
    transcript_result = read_jsonl(path)
    for record in transcript_result.records:
        if isinstance(record.get("$rewindTo"), str):
            rewind_id = record["$rewindTo"]
            if rewind_id in order:
                index = order.index(rewind_id)
                for message_id in order[index:]:
                    messages.pop(message_id, None)
                del order[index:]
            else:
                messages.clear()
                order.clear()
            continue
        update = record.get("$set")
        if isinstance(update, dict):
            metadata.update(update)
            checkpoint = update.get("messages")
            if isinstance(checkpoint, list):
                messages.clear()
                order.clear()
                for message in checkpoint:
                    if isinstance(message, dict) and isinstance(message.get("id"), str):
                        messages[message["id"]] = message
                        order.append(message["id"])
            continue
        if isinstance(record.get("sessionId"), str) and isinstance(
            record.get("projectHash"), str
        ):
            metadata.update(record)
        if isinstance(record.get("id"), str):
            message_id = record["id"]
            if message_id not in messages:
                order.append(message_id)
            messages[message_id] = record
    return (
        metadata,
        [messages[message_id] for message_id in order],
        not transcript_result.malformed,
    )


def discover_gemini_cli(root: Path, now: datetime) -> Iterable[SessionRecord]:
    temp_root = root / "tmp"
    if not temp_root.is_dir():
        return
    projects = gemini_project_map(root)
    for path in sorted(temp_root.glob("*/chats/**/*.jsonl")):
        metadata, messages, transcript_is_complete = parse_gemini_session(path)
        session_id = metadata.get("sessionId")
        if not isinstance(session_id, str) or not session_id:
            continue
        project_id = path.relative_to(temp_root).parts[0]
        cwd = projects.get(project_id)
        if cwd is None:
            marker = temp_root / project_id / ".project_root"
            try:
                cwd = marker.read_text(encoding="utf-8").strip() or None
            except OSError:
                cwd = None
        title = None
        for message in messages:
            if message.get("type") != "user":
                continue
            text = content_to_text(message.get("content"))
            if is_resumable_gemini_user(text):
                title = text
                break
        kind = metadata.get("kind")
        thread_kind = "subagent" if kind == "subagent" else "user"
        message_times = [
            timestamp
            for message in messages
            for timestamp in [parse_timestamp(message.get("timestamp"))]
            if timestamp is not None
        ]
        created = parse_timestamp(metadata.get("startTime"))
        last_active = parse_timestamp(metadata.get("lastUpdated")) or max(
            message_times, default=created
        )
        yield build_record(
            source="gemini-cli",
            session_id=session_id,
            title=title or metadata.get("summary"),
            cwd=cwd,
            transcript_path=path,
            created_at=created,
            last_active_at=last_active,
            now=now,
            thread_kind=thread_kind,
            model=None,
            available=bool(messages) and transcript_is_complete,
        )


def discover_antigravity(
    root: Path, source: str, now: datetime
) -> Iterable[SessionRecord]:
    brain = root / ("antigravity" if source == "antigravity-desktop" else "antigravity-cli") / "brain"
    if not brain.is_dir():
        return
    for path in sorted(brain.glob("*/.system_generated/logs/transcript.jsonl")):
        transcript_result = read_jsonl(path)
        records = transcript_result.records
        session_id = path.parents[2].name
        timestamps = [
            timestamp
            for record in records
            for timestamp in [parse_timestamp(record.get("created_at"))]
            if timestamp is not None
        ]
        title = next(
            (
                record.get("content")
                for record in records
                if record.get("type") == "USER_INPUT"
                and clean_title(record.get("content"))
            ),
            None,
        )
        yield build_record(
            source=source,
            session_id=session_id,
            title=title,
            cwd=None,
            transcript_path=path,
            created_at=min(timestamps, default=None),
            last_active_at=max(timestamps, default=None),
            now=now,
            available=(
                not transcript_result.malformed
                and any(
                    isinstance(record.get("step_index"), int)
                    and isinstance(record.get("source"), str)
                    and isinstance(record.get("type"), str)
                    and bool(record["type"])
                    for record in records
                )
            ),
        )


def collapse_same_source_duplicates(
    records: list[SessionRecord],
) -> list[SessionRecord]:
    grouped: dict[tuple[str, str], list[SessionRecord]] = {}
    for record in records:
        grouped.setdefault((record.source, record.id), []).append(record)

    collapsed: list[SessionRecord] = []
    minimum = datetime.min.replace(tzinfo=timezone.utc)
    for group in grouped.values():
        selected = max(group, key=lambda record: record.last_active_at or minimum)
        if len(group) > 1:
            selected.evidence_status = "unavailable"
        collapsed.append(selected)
    return collapsed


def discover(args: argparse.Namespace, now: datetime) -> list[SessionRecord]:
    grok_home = Path(args.grok_home).expanduser()
    grok_bot_data = Path(args.grok_bot_data).expanduser()
    gemini_home = Path(args.gemini_home).expanduser()
    claude_home = Path(args.claude_home).expanduser()
    selected = SOURCES if args.source == "all" else (args.source,)
    records: list[SessionRecord] = []
    for source in selected:
        if source == "grok-build":
            records.extend(discover_grok_build(grok_home, now))
        elif source == "grok-bot":
            records.extend(discover_grok_bot(grok_bot_data, now))
        elif source == "gemini-cli":
            records.extend(discover_gemini_cli(gemini_home, now))
        elif source == "claude-code":
            records.extend(discover_claude_code(claude_home, now))
        elif source == "claude-transcripts":
            records.extend(discover_claude_transcripts(claude_home, now))
        else:
            records.extend(discover_antigravity(gemini_home, source, now))
    return records


def validate_filter_combinations(args: argparse.Namespace) -> None:
    discovery_filters = (
        args.cwd,
        args.older_than,
        args.newer_than,
        args.from_date,
        args.to_date,
        args.month,
    )
    if args.id and any(value is not None for value in discovery_filters):
        raise InventoryError("--id cannot be combined with discovery filters")


def filter_records(
    records: list[SessionRecord], args: argparse.Namespace, now: datetime, tz: ZoneInfo
) -> list[SessionRecord]:
    validate_filter_combinations(args)
    eligible = collapse_same_source_duplicates([
        record
        for record in records
        if args.include_subagents or record.thread_kind != "subagent"
    ])
    if args.id:
        selected_ids = list(dict.fromkeys(args.id))
        by_id: dict[str, list[SessionRecord]] = {}
        for record in eligible:
            by_id.setdefault(record.id, []).append(record)
        missing = [session_id for session_id in selected_ids if session_id not in by_id]
        if missing:
            raise InventoryError("--id unavailable: " + ", ".join(missing))
        ambiguous = [
            session_id
            for session_id in selected_ids
            if len({record.source for record in by_id[session_id]}) > 1
        ]
        if ambiguous:
            raise InventoryError(
                "--id ambiguous across sources; pass --source: "
                + ", ".join(ambiguous)
            )
        return [by_id[session_id][0] for session_id in selected_ids]

    older = duration_cutoff(args.older_than, "--older-than", now) if args.older_than else None
    newer = duration_cutoff(args.newer_than, "--newer-than", now) if args.newer_than else None
    from_date = parse_local_date(args.from_date, "--from", tz) if args.from_date else None
    to_date = parse_local_date(args.to_date, "--to", tz) if args.to_date else None
    month = parse_month(args.month, tz) if args.month else None
    lower_bounds = [bound for bound in (newer, from_date) if bound is not None]
    upper_bounds = [bound for bound in (older, to_date) if bound is not None]
    if lower_bounds and upper_bounds and max(lower_bounds) >= min(upper_bounds):
        raise InventoryError("recency window is empty or reversed")
    filtered: list[SessionRecord] = []
    for record in eligible:
        if args.cwd is not None and record.cwd != args.cwd:
            continue
        last_active = record.last_active_at
        if older and (last_active is None or last_active >= older):
            continue
        if newer and (last_active is None or last_active < newer):
            continue
        if from_date and (last_active is None or last_active < from_date):
            continue
        if to_date and (last_active is None or last_active >= to_date):
            continue
        if month:
            month_start, month_end = month
            created = record.created_at or last_active
            if created is None or last_active is None:
                continue
            if not (created < month_end and last_active >= month_start):
                continue
        filtered.append(record)
    return filtered


def output(records: list[SessionRecord], output_format: str, tz: ZoneInfo) -> None:
    if output_format == "jsonl":
        for record in records:
            print(json.dumps(record.to_json(tz), ensure_ascii=False))
        return
    print("\t".join(TABLE_FIELDS))
    for record in records:
        row = record.to_json(tz)
        print(
            "\t".join(
                WHITESPACE_RE.sub(" ", str(row.get(field) or "")).strip()
                for field in TABLE_FIELDS
            )
        )


def main() -> int:
    args = parse_args()
    try:
        output_timezone = timezone_from_name(args.timezone)
        now = parse_now(args.now, output_timezone)
        records = discover(args, now)
        records = filter_records(records, args, now, output_timezone)
        records.sort(
            key=lambda record: (
                SOURCE_ORDER[record.source],
                record.last_active_at or datetime.min.replace(tzinfo=timezone.utc),
                record.id,
            )
        )
        output(records, args.format, output_timezone)
        return 0
    except InventoryError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
