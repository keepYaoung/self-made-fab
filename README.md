# self-made-fab

English · [한국어](README.ko.md)

A tested toolkit for designing real products with an AI coding agent and getting files a shop can make:
Fusion 360, code CAD, KiCad and tscircuit for boards, and CNC / 3D-print / laser checks.
One installer wires everything into [Codex](https://openai.com/codex), and the `self-made-fab` skill tells the agent
which tool fits each stage and which checks to run before anything goes to a machine.

Every tool here was run hands-on with the same tasks, and numbers were checked by hand or against KiCad's own checker.
The evidence is in the [quality report](docs/quality-report.md).

## What's inside

| Stage | Tool | Score | What it does |
|---|---|---|---|
| Fusion 360 | Autodesk Fusion MCP (built into Fusion) | pending | Lets the agent work in your open Fusion design |
| Fusion 360 | [fusion360-mcp-server](https://github.com/faust-machines/fusion360-mcp-server) | pending | 93 structured tools: sketches, features, joints, interference, export |
| Code CAD | [text-to-cad](https://github.com/earthtojake/text-to-cad) | 5 | Text to STEP/STL, drawings, DFM, slicing, fab-service checks |
| Code CAD | [build123d-mcp](https://github.com/pzfreo/build123d-mcp) | 5 | Build, measure, render and export build123d parts |
| Code CAD | [cad-drawing-to-model](https://github.com/Anson2251/cad-drawing-to-model-skill) | reference | Rebuild a part from a dimensioned 2D drawing |
| CAM | [AgentCADCAM](https://github.com/jeremylongworth-source/AgentCADCAM) | 4 | CNC, additive and laser preflight; static G-code review |
| Electronics | [KiCAD-MCP-Server](https://github.com/mixelpixx/KiCAD-MCP-Server) | 4 | Edit and route KiCad boards; Gerber, drill, BOM export |
| Electronics | [kicad-mcp-pro](https://github.com/oaslananka/kicad-mcp-pro) | 4 | Read-only ERC, DRC and project quality gate |
| Electronics | [tscircuit](https://github.com/tscircuit/skill) | 4 | Small boards written as code, with fab exports |
| Electronics | [atopile](https://github.com/atopile/atopile) | 2 | Watching: part picking needs an atopile account |
| Presentation | [mcp-for-blender](https://github.com/ahujasid/mcp-for-blender) | optional | Renders and materials, when Blender is installed |
| Presentation | [anatomy](https://github.com/wheresryan22/anatomy) | reference | Interactive figures that explain how a product works |
| Optional | [freecad-mcp](https://github.com/neka-nat/freecad-mcp) | optional | FreeCAD, when installed |

Each project is a shallow git submodule under `vendor/`, pinned to the commit we tested.
Versions, licenses, test notes and the candidates we left out (with reasons) are in [catalog.yaml](catalog.yaml).

## Install

Requirements: macOS, Codex, `git`, `python3`, `uv` and `node` (`brew install uv node`).
KiCad and Fusion 360 are connected when they are present. No step needs `sudo`.

```bash
git clone https://github.com/keepYaoung/self-made-fab.git ~/.codex/self-made-fab
cd ~/.codex/self-made-fab
./install.sh            # everything
./install.sh --check    # after restarting Codex: start each server and count its tools
```

Use `--only kicad,cad` to install some groups and `--dry-run` to print the commands first.

The installer:

1. fetches the pinned submodules and links the `self-made-fab` skill into `~/.codex/skills`;
2. installs the text-to-cad plugin and turns cadgen's usage telemetry off;
3. adds MCP servers to `~/.codex/config.toml` (`build123d`, `fusion`, `fusion-tools`, `kicad`, `kicad-review`), keeping a `.bak` copy before each change;
4. installs KiCad's global library tables if missing and builds the KiCad MCP server;
5. installs the `tsci` CLI and a virtualenv for the CAM review scripts.

### Connecting Fusion 360

1. Sign in to Fusion and open a design.
2. Turn on **Preferences → General → API → Fusion MCP Server** (it listens on `127.0.0.1:27182`).
3. For the structured tools, run the `Fusion360MCP` add-in from **Utilities → Add-Ins** (Shift+S).

### Other agents

The skill is a plain `SKILL.md` and the servers are standard MCP, so they work with other MCP clients.
Only `install.sh` is Codex-specific: it writes Codex's config file. Use `catalog.yaml` and the
commands in `install.sh` to register the same servers elsewhere.

## Usage

```text
$self-made-fab Design a Raspberry Pi 4 case in Fusion, 2 mm walls, for FDM printing.
$self-made-fab Run DRC on this KiCad project and export Gerbers for JLCPCB.
$self-made-fab Model this bracket from the attached drawing as STEP and preflight it for CNC.
```

## Health checks

```bash
./install.sh --check
uv run --with mcp scripts/mcp_probe.py -v -- uvx kicad-mcp-pro==4.3.0
```

`scripts/mcp_probe.py` starts any MCP server, lists its tools and can chain tool calls in one session
(`--call TOOL JSON`, repeatable). It is how the quality report was produced.

## Updating a tool

```bash
git submodule update --remote vendor/<stage>/<project>
```

Then rerun that tool's test from the quality report, update its commit and notes in `catalog.yaml`,
and open a pull request. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

The scripts, skill and docs in this repository are MIT licensed ([LICENSE](LICENSE)).
Projects under `vendor/` are linked as submodules and keep their own licenses; no third-party code is copied here.
Fusion 360, KiCad, Blender and FreeCAD are separate products under their own terms.

