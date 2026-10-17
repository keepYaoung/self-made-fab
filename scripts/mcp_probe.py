#!/usr/bin/env python3
"""Check that an MCP server starts, list its tools, and optionally call one.

Run through uv so the MCP client library is available:

  uv run --with mcp scripts/mcp_probe.py -- uvx kicad-mcp-pro
  uv run --with mcp scripts/mcp_probe.py --url http://localhost:9100/
  uv run --with mcp scripts/mcp_probe.py --url http://localhost:9100/ \
      --call get_screenshot '{"view":"iso-top-right"}' --save-images /tmp/shots

Exit code 0 means the server answered initialize and tools/list, and the call,
if any, did not report an error.
"""

from __future__ import annotations

import argparse
import asyncio
import base64
import json
import sys
import functools
print = functools.partial(print, flush=True)
from contextlib import AsyncExitStack
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def open_session(stack: AsyncExitStack, args: argparse.Namespace) -> ClientSession:
    if args.url:
        from mcp.client.streamable_http import streamablehttp_client

        read, write, _ = await stack.enter_async_context(streamablehttp_client(args.url))
    else:
        if not args.command:
            sys.exit("give a server command after --, or --url")
        env = None
        if args.env:
            import os

            env = dict(os.environ)
            env.update(pair.split("=", 1) for pair in args.env)
        params = StdioServerParameters(command=args.command[0], args=args.command[1:], cwd=args.cwd, env=env)
        read, write = await stack.enter_async_context(stdio_client(params))
    session = await stack.enter_async_context(ClientSession(read, write))
    await asyncio.wait_for(session.initialize(), args.timeout)
    return session


async def run(args: argparse.Namespace) -> int:
    async with AsyncExitStack() as stack:
        session = await open_session(stack, args)
        tools = (await session.list_tools()).tools
        print(f"tools: {len(tools)}")
        shown = [] if args.quiet else tools if args.verbose else tools[:40]
        for tool in shown:
            print(f"  - {tool.name}")
        if not args.quiet and len(shown) < len(tools):
            print(f"  ... {len(tools) - len(shown)} more (use -v)")
        for tool in tools:
            if tool.name in (args.schema or []):
                print(f"\n== schema {tool.name}\n{(tool.description or '')[:600]}")
                schema = getattr(tool, "input_schema", None) or getattr(tool, "inputSchema", None)
                print(json.dumps(schema, indent=1)[: args.max_chars])
        status = 0
        if args.call and args.delay:
            await asyncio.sleep(args.delay)
        for step, (name, raw) in enumerate(args.call or []):
            print(f"\n== {name}")
            result = await asyncio.wait_for(session.call_tool(name, json.loads(raw)), args.timeout)
            for i, item in enumerate(result.content):
                if item.type == "text":
                    print(item.text[: args.max_chars])
                elif item.type == "image" and args.save_images:
                    out = Path(args.save_images)
                    out.mkdir(parents=True, exist_ok=True)
                    path = out / f"{step:02d}-{name}-{i}.png"
                    path.write_bytes(base64.b64decode(item.data))
                    print(f"image saved: {path}")
                else:
                    print(f"[{item.type} content]")
            if getattr(result, "is_error", None) or getattr(result, "isError", False):
                print(f"{name} reported an error", file=sys.stderr)
                status = 1
        return status


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--url", help="streamable HTTP endpoint instead of a stdio command")
    parser.add_argument(
        "--call",
        nargs=2,
        action="append",
        metavar=("TOOL", "JSON_ARGS"),
        help="call a tool after listing; repeat to run several calls in one session",
    )
    parser.add_argument("--save-images", metavar="DIR", help="write image results to this folder")
    parser.add_argument("--timeout", type=float, default=300, help="seconds for startup and for the call")
    parser.add_argument("--max-chars", type=int, default=4000, help="truncate text results")
    parser.add_argument("-v", "--verbose", action="store_true", help="list every tool")
    parser.add_argument("-q", "--quiet", action="store_true", help="print only the tool count")
    parser.add_argument("--schema", action="append", metavar="TOOL", help="print a tool's input schema; repeatable")
    parser.add_argument("--cwd", help="working directory for a stdio server (some servers only write inside it)")
    parser.add_argument("--env", action="append", metavar="KEY=VALUE", help="environment for the stdio server only")
    parser.add_argument("--delay", type=float, default=0, help="seconds to wait after startup before the first call")
    parser.add_argument("command", nargs=argparse.REMAINDER, help="server command after --")
    args = parser.parse_args()
    if args.command and args.command[0] == "--":
        args.command = args.command[1:]
    sys.exit(asyncio.run(run(args)))


if __name__ == "__main__":
    main()

