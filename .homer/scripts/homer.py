#!/usr/bin/env python3
"""Mechanical state helper for Homer projects."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
STATE_PATH = ROOT / ".homer" / "state" / "chapters.json"
AUTHOR_DIRS = [ROOT / "设定", ROOT / "大纲", ROOT / "正文"]
HOMER_DIRS = [
    ROOT / ".homer" / "spec",
    ROOT / ".homer" / "state",
    ROOT / ".homer" / "knowledge" / "author-lore",
    ROOT / ".homer" / "knowledge" / "public-lore",
    ROOT / ".homer" / "knowledge" / "tracking",
    ROOT / ".homer" / "cache" / "context-packs",
    ROOT / ".homer" / "scripts",
    ROOT / ".homer" / "adapters",
]
VALID_STATUSES = {"planned", "draft", "accepted"}
VALID_KNOWLEDGE_STATUSES = {"none", "current", "stale"}


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return f"sha256:{h.hexdigest()}"


def ensure_dirs() -> None:
    for path in AUTHOR_DIRS + HOMER_DIRS:
        path.mkdir(parents=True, exist_ok=True)


def empty_state() -> dict[str, Any]:
    return {"schema_version": 1, "chapters": []}


def load_state() -> dict[str, Any]:
    if not STATE_PATH.is_file():
        return empty_state()
    try:
        data = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON: {STATE_PATH}: {exc}") from exc
    if not isinstance(data, dict):
        raise SystemExit(f"Invalid state object: {STATE_PATH}")
    chapters = data.setdefault("chapters", [])
    if not isinstance(chapters, list):
        raise SystemExit(f"Invalid chapters array: {STATE_PATH}")
    data.setdefault("schema_version", 1)
    return data


def save_state(data: dict[str, Any]) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def chapter_files() -> list[Path]:
    body = ROOT / "正文"
    if not body.is_dir():
        return []
    files = [
        p
        for p in body.rglob("*")
        if p.is_file() and p.suffix.lower() in {".md", ".txt"}
    ]
    return sorted(
        files,
        key=lambda p: (
            infer_number(p) is None,
            infer_number(p) or 10**9,
            rel(p),
        ),
    )


def infer_number(path: Path) -> int | None:
    name = path.stem
    patterns = [
        r"第\s*0*(\d+)\s*[章节章回]",
        r"chapter[-_\s]*0*(\d+)",
        r"ch[-_\s]*0*(\d+)",
        r"^0*(\d+)[-_\s]",
        r"^0*(\d+)$",
    ]
    for pattern in patterns:
        match = re.search(pattern, name, re.IGNORECASE)
        if match:
            return int(match.group(1))
    return None


def infer_title(path: Path, number: int | None) -> str:
    title = path.stem.strip()
    if number is not None:
        title = re.sub(rf"^第\s*0*{number}\s*[章节章回][_ -]*", "", title)
        title = re.sub(rf"^(chapter|ch)[-_\s]*0*{number}[_ -]*", "", title, flags=re.I)
        title = re.sub(rf"^0*{number}[_ -]*", "", title)
    return title.strip("_- ") or path.stem


def normalize_chapter(entry: dict[str, Any]) -> dict[str, Any]:
    status = entry.get("status", "draft")
    if status not in VALID_STATUSES:
        status = "draft"
    knowledge_status = entry.get("knowledge_status")
    if knowledge_status not in VALID_KNOWLEDGE_STATUSES:
        knowledge_status = "current" if status == "accepted" else "none"
    return {
        "number": entry.get("number"),
        "title": entry.get("title") or "",
        "file": entry.get("file") or "",
        "status": status,
        "content_hash": entry.get("content_hash") or "",
        "knowledge_status": knowledge_status,
    }


def next_available_number(existing: set[int]) -> int:
    number = 1
    while number in existing:
        number += 1
    existing.add(number)
    return number


def scan_chapters(default_status: str = "draft", keep_existing: bool = True) -> dict[str, Any]:
    if default_status not in VALID_STATUSES:
        raise SystemExit(f"Invalid status: {default_status}")

    state = load_state()
    existing_by_file = {
        item.get("file"): normalize_chapter(item)
        for item in state.get("chapters", [])
        if isinstance(item, dict) and item.get("file")
    }
    used_numbers: set[int] = set()
    scanned: list[dict[str, Any]] = []

    for path in chapter_files():
        file_rel = rel(path)
        old = existing_by_file.get(file_rel) if keep_existing else None
        old_number = old.get("number") if old else None
        if isinstance(old_number, int) and old_number not in used_numbers:
            number = old_number
            used_numbers.add(number)
        else:
            number = infer_number(path)
            if number is None or number in used_numbers:
                number = next_available_number(used_numbers)
            else:
                used_numbers.add(number)

        status = old["status"] if old else default_status
        knowledge_status = old["knowledge_status"] if old else (
            "current" if status == "accepted" else "none"
        )
        scanned.append(
            {
                "number": number,
                "title": old["title"] if old and old["title"] else infer_title(path, number),
                "file": file_rel,
                "status": status,
                "content_hash": sha256_file(path),
                "knowledge_status": knowledge_status,
            }
        )

    state["chapters"] = sorted(scanned, key=lambda c: (c["number"], c["file"]))
    return state


def find_chapter(state: dict[str, Any], target: str) -> dict[str, Any]:
    normalized = target.strip()
    if not normalized:
        raise SystemExit("Missing chapter target")

    for item in state.get("chapters", []):
        if not isinstance(item, dict):
            continue
        chapter = normalize_chapter(item)
        number = chapter.get("number")
        file_name = chapter.get("file", "")
        title = chapter.get("title", "")
        if str(number) == normalized or file_name == normalized or Path(file_name).name == normalized or title == normalized:
            return item
    raise SystemExit(f"Chapter not found: {target}")


def cmd_init(args: argparse.Namespace) -> int:
    ensure_dirs()
    if args.scan:
        state = scan_chapters(default_status=args.status, keep_existing=True)
    else:
        state = load_state()
    save_state(state)
    print_status(state)
    return 0


def cmd_scan(args: argparse.Namespace) -> int:
    ensure_dirs()
    state = scan_chapters(default_status=args.status, keep_existing=not args.reset_status)
    save_state(state)
    print_status(state)
    return 0


def cmd_status(_: argparse.Namespace) -> int:
    state = load_state()
    print_status(state)
    return 0


def cmd_check(_: argparse.Namespace) -> int:
    state = load_state()
    changed = False
    for item in state.get("chapters", []):
        if not isinstance(item, dict):
            continue
        chapter = normalize_chapter(item)
        path = ROOT / chapter["file"]
        if not path.is_file():
            continue
        current_hash = sha256_file(path)
        if chapter["content_hash"] != current_hash:
            item["content_hash"] = current_hash
            if chapter["status"] == "accepted":
                item["knowledge_status"] = "stale"
            changed = True
    if changed:
        save_state(state)
    print_status(state)
    return 0


def cmd_accept(args: argparse.Namespace) -> int:
    state = load_state()
    item = find_chapter(state, args.chapter)
    chapter = normalize_chapter(item)
    path = ROOT / chapter["file"]
    if not path.is_file():
        raise SystemExit(f"Chapter file not found: {chapter['file']}")
    item["status"] = "accepted"
    item["content_hash"] = sha256_file(path)
    item["knowledge_status"] = "stale"
    save_state(state)
    print(f"Accepted chapter {item.get('number')}: {item.get('file')}")
    return 0


def cmd_mark_current(_: argparse.Namespace) -> int:
    state = load_state()
    for item in state.get("chapters", []):
        if not isinstance(item, dict):
            continue
        chapter = normalize_chapter(item)
        if chapter["status"] == "accepted":
            item["knowledge_status"] = "current"
    save_state(state)
    print_status(state)
    return 0


def copy_tree_contents(src: Path, dst: Path) -> list[str]:
    copied: list[str] = []
    if not src.is_dir():
        return copied
    for path in sorted(src.rglob("*")):
        if not path.is_file():
            continue
        if "__pycache__" in path.parts or path.suffix == ".pyc":
            continue
        rel_path = path.relative_to(src)
        target = dst / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
        copied.append(rel(target))
    return copied


def cmd_generate_adapters(_: argparse.Namespace) -> int:
    adapters = ROOT / ".homer" / "adapters"
    copied: list[str] = []
    copied.extend(copy_tree_contents(adapters / "agents", ROOT / ".agents"))
    copied.extend(copy_tree_contents(adapters / "codex", ROOT / ".codex"))
    for path in copied:
        print(f"generated {path}")
    if not copied:
        print("No adapter files generated")
    return 0


def cmd_hook_state(_: argparse.Namespace) -> int:
    state = load_state()
    counts = count_statuses(state)
    stale = [
        normalize_chapter(item)
        for item in state.get("chapters", [])
        if isinstance(item, dict)
        and normalize_chapter(item)["status"] == "accepted"
        and normalize_chapter(item)["knowledge_status"] == "stale"
    ]
    print("<homer-state>")
    print(f"Project: {'initialized' if STATE_PATH.is_file() else 'not initialized'}")
    print(
        "Chapters: "
        f"planned={counts['planned']} draft={counts['draft']} accepted={counts['accepted']}"
    )
    if stale:
        refs = ", ".join(str(item.get("number")) for item in stale[:8])
        suffix = "..." if len(stale) > 8 else ""
        print(f"Knowledge stale for accepted chapters: {refs}{suffix}")
    print("Route: setup/import -> homer-setup; write/polish -> homer-write; accept/rebuild -> homer-sync.")
    print("</homer-state>")
    return 0


def count_statuses(state: dict[str, Any]) -> dict[str, int]:
    counts = {"planned": 0, "draft": 0, "accepted": 0}
    for item in state.get("chapters", []):
        if isinstance(item, dict):
            status = normalize_chapter(item)["status"]
            counts[status] += 1
    return counts


def print_status(state: dict[str, Any]) -> None:
    counts = count_statuses(state)
    print("Homer project status")
    print(f"Root: {ROOT}")
    print(
        "Chapters: "
        f"planned={counts['planned']} draft={counts['draft']} accepted={counts['accepted']}"
    )
    for item in state.get("chapters", []):
        if not isinstance(item, dict):
            continue
        chapter = normalize_chapter(item)
        print(
            f"- {chapter['number']:03d} "
            f"[{chapter['status']}/{chapter['knowledge_status']}] "
            f"{chapter['file']}"
        )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage Homer project state.")
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init", help="Initialize Homer directories and state.")
    init.add_argument("--scan", action="store_true", help="Scan existing chapter files.")
    init.add_argument(
        "--status",
        choices=sorted(VALID_STATUSES),
        default="draft",
        help="Default status for newly scanned chapters.",
    )
    init.set_defaults(func=cmd_init)

    scan = sub.add_parser("scan", help="Scan chapter files under 正文/.")
    scan.add_argument(
        "--status",
        choices=sorted(VALID_STATUSES),
        default="draft",
        help="Default status for newly scanned chapters.",
    )
    scan.add_argument(
        "--reset-status",
        action="store_true",
        help="Apply --status to all scanned chapters instead of preserving existing statuses.",
    )
    scan.set_defaults(func=cmd_scan)

    status = sub.add_parser("status", help="Show Homer state.")
    status.set_defaults(func=cmd_status)

    check = sub.add_parser("check", help="Update content hashes and mark edited accepted chapters stale.")
    check.set_defaults(func=cmd_check)

    accept = sub.add_parser("accept", help="Mark a chapter accepted and stale until knowledge rebuild.")
    accept.add_argument("chapter", help="Chapter number, title, file path, or basename.")
    accept.set_defaults(func=cmd_accept)

    mark_current = sub.add_parser("mark-current", help="Mark accepted chapters knowledge_status=current.")
    mark_current.set_defaults(func=cmd_mark_current)

    generate_adapters = sub.add_parser("generate-adapters", help="Generate .agents/.codex files from .homer/adapters.")
    generate_adapters.set_defaults(func=cmd_generate_adapters)

    hook_state = sub.add_parser("hook-state", help="Emit compact state for Codex hooks.")
    hook_state.set_defaults(func=cmd_hook_state)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
