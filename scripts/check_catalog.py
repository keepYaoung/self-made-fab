#!/usr/bin/env python3
"""Check that catalog.yaml agrees with .gitmodules and the pinned submodule commits.

Needs no network and no submodule checkout: commits are read from the git tree.
"""

from __future__ import annotations

import configparser
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATUSES = {"core", "optional", "fallback", "reference", "watch"}


def load_catalog() -> list[dict[str, str]]:
    """Read the flat project entries without a YAML dependency."""
    projects: list[dict[str, str]] = []
    section = None
    for line in (ROOT / "catalog.yaml").read_text(encoding="utf-8").splitlines():
        if re.match(r"^\w", line):
            section = line.split(":")[0]
            continue
        if section != "projects":
            continue
        item = re.match(r"^  - (\w+): (.*)$", line)
        field = re.match(r"^    (\w+): (.*)$", line)
        if item:
            projects.append({item.group(1): item.group(2).strip()})
        elif field and projects:
            projects[-1][field.group(1)] = field.group(2).strip()
    return projects


def submodules() -> dict[str, str]:
    parser = configparser.ConfigParser()
    parser.read(ROOT / ".gitmodules")
    return {parser[s]["path"]: parser[s]["url"] for s in parser.sections()}


def pinned(path: str) -> str | None:
    out = subprocess.run(["git", "-C", str(ROOT), "ls-tree", "HEAD", path], capture_output=True, text=True).stdout
    parts = out.split()
    return parts[2] if len(parts) >= 3 and parts[1] == "commit" else None


def main() -> int:
    errors: list[str] = []
    mods = submodules()
    seen: set[str] = set()
    for p in load_catalog():
        pid = p.get("id", "?")
        if p.get("status") not in STATUSES:
            errors.append(f"{pid}: unknown status {p.get('status')!r}")
        score = p.get("score")
        if score not in {"null", "1", "2", "3", "4", "5"}:
            errors.append(f"{pid}: score must be 1-5 or null")
        if not p.get("tested"):
            errors.append(f"{pid}: missing tested note")
        path = p.get("path")
        if not path:
            continue
        seen.add(path)
        if path not in mods:
            errors.append(f"{pid}: {path} is not a submodule")
            continue
        repo = p.get("repo", "")
        if repo and repo.lower() not in mods[path].lower():
            errors.append(f"{pid}: repo {repo} does not match {mods[path]}")
        commit = p.get("commit", "")
        actual = pinned(path)
        if commit and actual and not actual.startswith(commit):
            errors.append(f"{pid}: catalog commit {commit} but submodule is pinned at {actual[:7]}")
    for path in sorted(set(mods) - seen):
        errors.append(f"{path}: submodule missing from catalog.yaml")
    for e in errors:
        print("error:", e)
    print(f"catalog: {len(seen)} submodules checked, {len(errors)} problems")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())

