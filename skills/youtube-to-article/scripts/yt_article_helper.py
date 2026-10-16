#!/usr/bin/env python3
"""Small utilities for YouTube-to-article workflows."""

from __future__ import annotations

import argparse
import html
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.parse import parse_qs, urlparse


VIDEO_ID_RE = re.compile(r"^[A-Za-z0-9_-]{11}$")
CHINESE_RE = re.compile(r"[\u4e00-\u9fff]")
TIMESTAMP_RE = re.compile(
    r"^\s*(?:\d{1,2}:)?\d{1,2}:\d{2}(?:[.,]\d{1,3})?\s*-->\s*"
    r"(?:\d{1,2}:)?\d{1,2}:\d{2}(?:[.,]\d{1,3})?.*$"
)
TAG_RE = re.compile(r"<[^>]+>")
VTT_SETTING_RE = re.compile(r"\s+(?:align|position|line|size|vertical):\S+")


def parse_video_id(value: str) -> str:
    value = value.strip()
    if VIDEO_ID_RE.match(value):
        return value

    parsed = urlparse(value)
    host = parsed.netloc.lower().removeprefix("www.")
    path_parts = [part for part in parsed.path.split("/") if part]

    if host in {"youtube.com", "m.youtube.com", "music.youtube.com"}:
        query_id = parse_qs(parsed.query).get("v", [""])[0]
        if VIDEO_ID_RE.match(query_id):
            return query_id
        if path_parts and path_parts[0] in {"shorts", "embed", "live"} and len(path_parts) > 1:
            candidate = path_parts[1]
            if VIDEO_ID_RE.match(candidate):
                return candidate

    if host == "youtu.be" and path_parts:
        candidate = path_parts[0]
        if VIDEO_ID_RE.match(candidate):
            return candidate

    raise ValueError(f"Could not parse a YouTube video ID from: {value}")


def clean_transcript_text(text: str) -> str:
    lines: list[str] = []
    previous = ""

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line in {"WEBVTT", "Kind: captions", "Language: en"}:
            continue
        if line.isdigit() or TIMESTAMP_RE.match(line):
            continue
        line = VTT_SETTING_RE.sub("", line)
        line = TAG_RE.sub("", line)
        line = html.unescape(line)
        line = re.sub(r"\[(?:Music|Applause|Laughter|音乐|掌声|笑声)\]", "", line, flags=re.I)
        line = re.sub(r"\s+", " ", line).strip()
        if not line or line == previous:
            continue
        lines.append(line)
        previous = line

    merged: list[str] = []
    buffer = ""
    sentence_end = re.compile(r'[.!?。！？]"?$')
    for line in lines:
        if not buffer:
            buffer = line
            continue
        if sentence_end.search(buffer):
            merged.append(buffer)
            buffer = line
        else:
            buffer = f"{buffer} {line}"
    if buffer:
        merged.append(buffer)

    return "\n".join(merged) + ("\n" if merged else "")


def count_chinese_chars(text: str) -> int:
    return len(CHINESE_RE.findall(text))


def article_body_text(text: str) -> str:
    lines = text.splitlines()
    in_code = False
    in_toc = False
    body: list[str] = []

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        if stripped.startswith("## Table of Contents"):
            in_toc = True
            continue
        if in_toc:
            if stripped.startswith("## "):
                in_toc = False
            else:
                continue
        if not stripped:
            continue
        if (
            stripped.startswith("#")
            or stripped.startswith(">")
            or stripped.startswith("-")
            or stripped.startswith("|")
        ):
            continue
        body.append(stripped)

    return "\n".join(body)


def format_size(num_bytes: int) -> str:
    size = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size < 1024 or unit == "TB":
            if unit == "B":
                return f"{int(size)} {unit}"
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{num_bytes} B"


def media_info(path: Path) -> dict[str, str]:
    stat = path.stat()
    info = {
        "path": str(path),
        "size": format_size(stat.st_size),
        "resolution": "unknown",
        "clarity": "unknown",
    }

    ffprobe = shutil.which("ffprobe")
    if not ffprobe:
        return info

    result = subprocess.run(
        [
            ffprobe,
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=width,height",
            "-of",
            "json",
            str(path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return info

    try:
        data = json.loads(result.stdout)
        stream = data.get("streams", [{}])[0]
        width = int(stream.get("width") or 0)
        height = int(stream.get("height") or 0)
    except (ValueError, TypeError, IndexError, KeyError, json.JSONDecodeError):
        return info

    if width > 0 and height > 0:
        info["resolution"] = f"{width}x{height}"
        info["clarity"] = f"{height}p"
    return info


def cmd_parse_url(args: argparse.Namespace) -> int:
    print(parse_video_id(args.value))
    return 0


def cmd_clean_transcript(args: argparse.Namespace) -> int:
    text = Path(args.input).read_text(encoding=args.encoding)
    cleaned = clean_transcript_text(text)
    if args.output:
        Path(args.output).write_text(cleaned, encoding="utf-8")
    else:
        sys.stdout.write(cleaned)
    return 0


def cmd_count_source(args: argparse.Namespace) -> int:
    text = Path(args.input).read_text(encoding=args.encoding)
    print(count_chinese_chars(text))
    return 0


def cmd_count_article_body(args: argparse.Namespace) -> int:
    text = Path(args.input).read_text(encoding=args.encoding)
    print(count_chinese_chars(article_body_text(text)))
    return 0


def cmd_media_info(args: argparse.Namespace) -> int:
    path = Path(args.path)
    info = media_info(path)
    print(f"path: {info['path']}")
    print(f"size: {info['size']}")
    print(f"resolution: {info['resolution']}")
    print(f"clarity: {info['clarity']}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Utilities for YouTube-to-article workflows.")
    subparsers = parser.add_subparsers(required=True)

    parse_url = subparsers.add_parser("parse-url", help="Extract a YouTube video ID from a URL or ID.")
    parse_url.add_argument("value")
    parse_url.set_defaults(func=cmd_parse_url)

    clean = subparsers.add_parser("clean-transcript", help="Clean WebVTT/SRT/plain transcript text.")
    clean.add_argument("input")
    clean.add_argument("--output", "-o")
    clean.add_argument("--encoding", default="utf-8")
    clean.set_defaults(func=cmd_clean_transcript)

    count_source = subparsers.add_parser(
        "count-source",
        help="Count Chinese characters in cleaned source information.",
    )
    count_source.add_argument("input")
    count_source.add_argument("--encoding", default="utf-8")
    count_source.set_defaults(func=cmd_count_source)

    count_body = subparsers.add_parser(
        "count-article-body",
        help="Count Chinese characters in article body prose by the skill's rules.",
    )
    count_body.add_argument("input")
    count_body.add_argument("--encoding", default="utf-8")
    count_body.set_defaults(func=cmd_count_article_body)

    media = subparsers.add_parser("media-info", help="Report file size and video resolution if available.")
    media.add_argument("path")
    media.set_defaults(func=cmd_media_info)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        return args.func(args)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
