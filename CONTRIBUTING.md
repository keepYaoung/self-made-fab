# Contributing

Thanks for helping. This repo is a curated, tested list, so every change to a tool needs evidence.

## Proposing a tool

Open an issue with the "Propose a tool" template. A tool is a good fit when it:

- produces or checks something a shop or machine uses (STEP, DXF, Gerber, drill, BOM, G-code, 3MF);
- runs locally, or degrades clearly when an account is required;
- has a license that allows use, and recent activity.

## Adding or updating a tool

1. Add it as a shallow submodule: `git submodule add --depth 1 <url> vendor/<stage>/<name>`, then set `shallow = true` in `.gitmodules`.
2. Run a real task, not just start-up. Use `scripts/mcp_probe.py` for MCP servers; chain calls with repeated `--call TOOL JSON` in one session.
3. Check the result independently: a hand calculation for geometry, `kicad-cli` for boards, an injected fault for checkers.
4. Record what you ran and saw in `docs/quality-report.md` (and the Korean copy if you can), and add the entry to `catalog.yaml` with the commit, license, score and a one-line `tested` note.
5. If the tool needs an MCP entry, add it to `install.sh` with a pinned version, and to `skills/self-made-fab` only when it changes which tool an agent should pick.
6. Run the local checks below and open a pull request.

## Scores

- 5: real task done, output verified independently, no workaround needed.
- 4: real task done and verified, with a known caveat that the skill documents.
- 3: works for part of the task or needs a workaround.
- 2: blocked for typical users (account, missing feature) but worth watching.
- 1: does not work as published.

## Local checks

```bash
shellcheck -S warning install.sh
python3 -m unittest discover -s tests -v
python3 scripts/check_catalog.py
./install.sh --dry-run
```

## Style

Keep the skill short: put tool-specific detail in `skills/self-made-fab/references/`.
Write what you observed, with numbers, and say what you did not test.

