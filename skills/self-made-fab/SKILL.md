---
name: self-made-fab
description: Design and prepare real products for fabrication — mechanical parts and enclosures in Fusion 360 or code CAD, PCBs in KiCad or tscircuit, CNC/3D-print/laser job checks, and product renders — by routing each stage to the tested tool in the self-made-fab bundle and applying its manufacturability checks. Use when the user wants something physically made or wants fabrication files (STEP, STL, DXF, Gerber, G-code) produced or reviewed. For explanatory figures of how something works, use anatomy instead.
---

# Self-made fab

This skill folder is a symlink into the self-made-fab repo. Resolve the repo root once with
`realpath ~/.codex/skills/self-made-fab/../..`. Vendored sources live in `vendor/<stage>/<project>`,
`catalog.yaml` lists pinned versions and status, and `docs/quality-report.md` holds the test evidence.

## Pick the tool for the stage

| Stage | First choice | Switch when |
| --- | --- | --- |
| Part or enclosure the user will keep editing in Fusion | `fusion` MCP (Autodesk's built-in server) | Fusion closed or signed out: use `build123d` and hand over STEP |
| Part from a text description, no GUI | `build123d` MCP | A maintained multi-part project, drawings, DFM or fab-service quotes: text-to-cad skills (`$cad`, `$dxf`, `$engineering-drawing`, `$dfm`, `$gcode`, `$sendcutsend`, `$bambu-labs`) |
| Dimensioned drawing or photo to 3D | Read `vendor/code-cad/cad-drawing-to-model/skills/cad-drawing-to-model/SKILL.md` | |
| Existing KiCad project: ERC, DRC, quality gate | `kicad-review` MCP (read-only) | |
| Edit, route or export a KiCad board | `kicad` MCP | |
| New small board written as code | tscircuit: read `vendor/electronics/tscircuit-skill/SKILL.md` | |
| CNC, FDM or laser job preflight, G-code review | AgentCADCAM: [references/cam.md](references/cam.md) | |
| Product look, materials, renders | `blender` MCP if installed | |
| Explaining how the product works | `$anatomy` | |

Read the reference for the stage before the first tool call:
[fusion.md](references/fusion.md), [code-cad.md](references/code-cad.md),
[electronics.md](references/electronics.md), [cam.md](references/cam.md).

## What every job needs

- State units (mm unless told otherwise), the material, the process and quantity before modeling; these change wall thickness, hole sizes and tolerances.
- Check geometry with numbers before trusting a picture: read volume and bounding box back from the tool and compare at least one feature with a hand calculation.
- Hand over STEP for anything going to Fusion, a machine shop or a mechanical review. STL and 3MF are only for printing.
- Fabrication outputs (Gerber, drill, BOM, pick-and-place, G-code, DXF) are drafts until a checker has run on them. Say which checks ran and which did not.
- Never call a G-code program safe to run. Static review, simulation and a human sign-off come before any machine.
- Ask before deleting bodies or components in an open Fusion design or overwriting a KiCad board, and save a version first.

## Health check

`<repo>/install.sh --check` starts each configured server and counts its tools.
For one server: `uv run --with mcp <repo>/scripts/mcp_probe.py -- <server command>`.

