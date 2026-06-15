#!/usr/bin/env python3
"""Inject a compact Homer state block for Codex turns."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def find_root(start: Path) -> Path | None:
    current = start.resolve()
    while current != current.parent:
        if (current / ".homer").is_dir():
            return current
        current = current.parent
    return None


def main() -> int:
    root = find_root(Path.cwd())
    if root is None:
        return 0
    script = root / ".homer" / "scripts" / "homer.py"
    if not script.is_file():
        return 0
    try:
        result = subprocess.run(
            [sys.executable, str(script), "hook-state"],
            cwd=root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            timeout=2,
            check=False,
        )
    except Exception:
        return 0
    if result.stdout.strip():
        print(result.stdout.rstrip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
