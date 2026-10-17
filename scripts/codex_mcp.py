#!/usr/bin/env python3
"""Add, replace, or remove one MCP server entry in Codex's config.toml.

  codex_mcp.py add NAME --command /abs/cmd [--env K=V] [--cwd DIR] [--disabled]
                        [--startup-timeout 60] [--tool-timeout 300] -- arg1 --arg2 ...
  codex_mcp.py add NAME --url http://localhost:9100/
  codex_mcp.py remove NAME
  codex_mcp.py show NAME

The entry's [mcp_servers.NAME] and [mcp_servers.NAME.env] tables are replaced as
a unit; everything else in the file is kept byte for byte. A .bak copy is written
before each change, and the result must parse as TOML or the change is rolled back.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
import tomllib
from pathlib import Path

CONFIG = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")) / "config.toml"
HEADER = re.compile(r"^\s*\[\[?\s*([^\]]+?)\s*\]\]?\s*(#.*)?$")


def toml_str(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def split_sections(text: str) -> list[tuple[str | None, list[str]]]:
    sections: list[tuple[str | None, list[str]]] = [(None, [])]
    for line in text.splitlines(keepends=True):
        match = HEADER.match(line)
        if match:
            sections.append((match.group(1).replace('"', ""), [line]))
        else:
            sections[-1][1].append(line)
    return sections


def without_server(text: str, name: str) -> str:
    own = {f"mcp_servers.{name}", f"mcp_servers.{name}.env"}
    kept = [lines for header, lines in split_sections(text) if header not in own]
    return "".join("".join(lines) for lines in kept)


def render(name: str, args: argparse.Namespace) -> str:
    out = [f"\n[mcp_servers.{name}]\n"]
    if args.url:
        out.append(f"url = {toml_str(args.url)}\n")
    else:
        out.append(f"command = {toml_str(args.command)}\n")
        out.append("args = [" + ", ".join(toml_str(a) for a in args.arg or []) + "]\n")
        if args.cwd:
            out.append(f"cwd = {toml_str(args.cwd)}\n")
    out.append(f"enabled = {'false' if args.disabled else 'true'}\n")
    if args.startup_timeout:
        out.append(f"startup_timeout_sec = {args.startup_timeout}\n")
    if args.tool_timeout:
        out.append(f"tool_timeout_sec = {args.tool_timeout}\n")
    if args.env:
        out.append(f"\n[mcp_servers.{name}.env]\n")
        for pair in args.env:
            key, _, value = pair.partition("=")
            out.append(f"{key} = {toml_str(value)}\n")
    return "".join(out)


def write_checked(text: str) -> None:
    tomllib.loads(text)
    if CONFIG.exists():
        shutil.copy2(CONFIG, CONFIG.with_suffix(".toml.bak"))
    CONFIG.parent.mkdir(parents=True, exist_ok=True)
    CONFIG.write_text(text, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("action", choices=["add", "remove", "show"])
    parser.add_argument("name")
    parser.add_argument("--command")
    parser.add_argument("--url")
    parser.add_argument("--env", action="append", metavar="KEY=VALUE")
    parser.add_argument("--cwd")
    parser.add_argument("--disabled", action="store_true")
    parser.add_argument("--startup-timeout", type=int)
    parser.add_argument("--tool-timeout", type=int)
    argv = sys.argv[1:]
    server_args: list[str] = []
    if "--" in argv:
        cut = argv.index("--")
        argv, server_args = argv[:cut], argv[cut + 1 :]
    args = parser.parse_args(argv)
    args.arg = server_args

    if not re.fullmatch(r"[A-Za-z0-9_-]+", args.name):
        sys.exit(f"invalid server name: {args.name}")
    text = CONFIG.read_text(encoding="utf-8") if CONFIG.exists() else ""

    if args.action == "show":
        entry = tomllib.loads(text).get("mcp_servers", {}).get(args.name)
        print(json.dumps(entry, indent=2) if entry else f"{args.name}: not configured")
        return
    base = without_server(text, args.name)
    if args.action == "remove":
        write_checked(base.rstrip("\n") + "\n" if base.strip() else "")
        print(f"removed {args.name}")
        return
    if bool(args.url) == bool(args.command):
        sys.exit("add needs exactly one of --command or --url")
    write_checked(base.rstrip("\n") + "\n" + render(args.name, args))
    state = "disabled" if args.disabled else "enabled"
    print(f"configured {args.name} ({state})")


if __name__ == "__main__":
    main()

