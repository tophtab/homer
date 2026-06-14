#!/usr/bin/env python3
"""Install Homer project infrastructure into a book directory."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


SOURCE_ROOT = Path(__file__).resolve().parents[1]
SOURCE_HOMER = SOURCE_ROOT / ".homer"
SKIPPED_PARTS = {"__pycache__", "cache"}
SKIPPED_SUFFIXES = {".pyc", ".pyo"}
VALID_STATUSES = ("planned", "draft", "accepted")


@dataclass(frozen=True)
class CopyPlan:
    to_copy: list[tuple[Path, Path]]
    unchanged: list[Path]
    skipped: list[Path]


def posix(path: Path) -> str:
    return path.as_posix()


def iter_template_files(root: Path) -> Iterable[Path]:
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        rel_parts = path.relative_to(root).parts
        if any(part in SKIPPED_PARTS for part in rel_parts):
            continue
        if path.suffix in SKIPPED_SUFFIXES:
            continue
        yield path


def same_bytes(left: Path, right: Path) -> bool:
    if left.stat().st_size != right.stat().st_size:
        return False
    return left.read_bytes() == right.read_bytes()


def plan_copy_tree(
    src_root: Path,
    dst_root: Path,
    *,
    force: bool,
    skip_existing: bool,
) -> CopyPlan:
    conflicts: list[Path] = []
    to_copy: list[tuple[Path, Path]] = []
    unchanged: list[Path] = []
    skipped: list[Path] = []

    for src in iter_template_files(src_root):
        rel = src.relative_to(src_root)
        dst = dst_root / rel

        if dst.exists():
            if not dst.is_file():
                conflicts.append(dst)
                continue
            if same_bytes(src, dst):
                unchanged.append(dst)
                continue
            if skip_existing:
                skipped.append(dst)
                continue
            if not force:
                conflicts.append(dst)
                continue

        to_copy.append((src, dst))

    if conflicts:
        rel_conflicts = "\n".join(f"  - {posix(path)}" for path in conflicts[:20])
        suffix = "\n  ..." if len(conflicts) > 20 else ""
        raise SystemExit(
            "Refusing to overwrite existing Homer files. "
            "Re-run with --force to overwrite or --skip-existing to preserve them.\n"
            f"{rel_conflicts}{suffix}"
        )

    return CopyPlan(to_copy=to_copy, unchanged=unchanged, skipped=skipped)


def apply_copy_plan(plan: CopyPlan) -> None:
    for src, dst in plan.to_copy:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


def run_homer(target: Path, *args: str) -> None:
    script = target / ".homer" / "scripts" / "homer.py"
    if not script.is_file():
        raise SystemExit(f"Homer helper not found after install: {script}")
    subprocess.run([sys.executable, str(script), *args], cwd=target, check=True)


def cmd_init(args: argparse.Namespace) -> int:
    if not SOURCE_HOMER.is_dir():
        raise SystemExit(f"Source Homer template not found: {SOURCE_HOMER}")

    target = Path(args.project_dir).expanduser().resolve()
    target.mkdir(parents=True, exist_ok=True)

    plan = plan_copy_tree(
        SOURCE_HOMER,
        target / ".homer",
        force=args.force,
        skip_existing=args.skip_existing,
    )
    apply_copy_plan(plan)

    run_homer(target, "init", "--scan", "--status", args.status)
    run_homer(target, "generate-adapters")

    print()
    print(f"Homer installed in {target}")
    print(
        "Template files: "
        f"copied={len(plan.to_copy)} "
        f"unchanged={len(plan.unchanged)} "
        f"skipped={len(plan.skipped)}"
    )
    print("Next:")
    print(f"  cd {target}")
    print("  python3 .homer/scripts/homer.py status")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="homer",
        description="Install Homer into a single-book novel project.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init", help="Create or update a Homer book project.")
    init.add_argument(
        "project_dir",
        nargs="?",
        default=".",
        help="Book project directory. Defaults to the current directory.",
    )
    init.add_argument(
        "--status",
        choices=VALID_STATUSES,
        default="draft",
        help="Default status for newly scanned chapter files.",
    )
    init.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Overwrite existing Homer template files.",
    )
    init.add_argument(
        "--skip-existing",
        action="store_true",
        help="Preserve existing Homer template files that differ from the source.",
    )
    init.set_defaults(func=cmd_init)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.force and args.skip_existing:
        parser.error("--force and --skip-existing cannot be used together")
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
