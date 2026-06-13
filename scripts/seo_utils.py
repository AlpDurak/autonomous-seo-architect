#!/usr/bin/env python3
"""Shared helpers for Autonomous SEO Architect evidence scripts."""

from __future__ import annotations

import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse, urlunparse


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def read_json(path: Path, default: Any = None) -> Any:
    if not path.is_file():
        return default
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, payload: Any) -> None:
    ensure_parent(path)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def write_markdown(path: Path, content: str) -> None:
    ensure_parent(path)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def normalize_url(raw_url: str, base_url: str | None = None) -> str:
    raw_url = (raw_url or "").strip()
    if not raw_url:
        return ""
    if base_url:
        raw_url = urljoin(base_url, raw_url)
    parsed = urlparse(raw_url)
    if not parsed.scheme and parsed.netloc:
        parsed = parsed._replace(scheme="https")
    if not parsed.scheme or not parsed.netloc:
        return ""
    parsed = parsed._replace(fragment="")
    return urlunparse(parsed)


def same_origin(left: str, right: str) -> bool:
    a = urlparse(left)
    b = urlparse(right)
    return (a.scheme, a.netloc.lower()) == (b.scheme, b.netloc.lower())


def domain_of(value: str) -> str:
    parsed = urlparse(value if "://" in value else f"https://{value}")
    return parsed.netloc.lower().removeprefix("www.")


def parse_float(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().replace(",", "")
    if not text:
        return None
    if text.endswith("%"):
        text = text[:-1]
        try:
            return float(text) / 100.0
        except ValueError:
            return None
    try:
        return float(text)
    except ValueError:
        return None


def parse_int(value: Any) -> int | None:
    parsed = parse_float(value)
    return None if parsed is None else int(round(parsed))


def canonical_header(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", name.strip().lower()).strip("_")


def first_value(row: dict[str, Any], *headers: str) -> Any:
    normalized = {canonical_header(k): v for k, v in row.items()}
    for header in headers:
        value = normalized.get(canonical_header(header))
        if value not in (None, ""):
            return value
    return None


def load_records(path: Path) -> list[dict[str, Any]]:
    suffix = path.suffix.lower()
    if suffix == ".json":
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
        if isinstance(payload, list):
            return [item for item in payload if isinstance(item, dict)]
        if isinstance(payload, dict):
            for key in ("rows", "records", "data", "items", "imports"):
                value = payload.get(key)
                if isinstance(value, list):
                    return [item for item in value if isinstance(item, dict)]
            return [payload]
        return []
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def load_urls(values: list[str], files: list[Path] | None = None) -> list[str]:
    urls: list[str] = []
    for value in values:
        if value.strip():
            urls.append(value.strip())
    for path in files or []:
        if not path.is_file():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                urls.append(line)
    seen: set[str] = set()
    unique: list[str] = []
    for url in urls:
        normalized = normalize_url(url)
        if normalized and normalized not in seen:
            seen.add(normalized)
            unique.append(normalized)
    return unique


def severity_weight(severity: str) -> int:
    return {
        "critical": 100,
        "high": 75,
        "medium": 45,
        "low": 20,
    }.get((severity or "").lower(), 20)


def confidence_weight(confidence: str) -> int:
    return {
        "observed": 100,
        "provided": 85,
        "inferred": 55,
        "unverified": 25,
    }.get((confidence or "").lower(), 40)


def markdown_table(headers: list[str], rows: list[list[Any]]) -> str:
    escaped_rows = [[escape_md_cell(value) for value in row] for row in rows]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in escaped_rows)
    return "\n".join(lines)


def escape_md_cell(value: Any) -> str:
    text = "" if value is None else str(value)
    return text.replace("|", "\\|").replace("\n", " ").strip()
