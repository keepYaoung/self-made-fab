# Electronics

## KiCad setup

- If ERC or DRC reports "footprint library ... not in the current configuration" for every part, KiCad's global library tables are missing. The installer copies `fp-lib-table` and `sym-lib-table` from KiCad's template folder into `~/Library/Preferences/kicad/<major>.0/`.
- `kicad-cli` is on PATH. `kicad-cli pcb drc --format json -o drc.json board.kicad_pcb` is the reference check when two tools disagree.

## `kicad` MCP (mixelpixx, editing and export)

- About 240 tools. Find the right one with `search_tools` or `list_tool_categories`/`get_category_tools` instead of guessing names.
- Its Python worker starts a second or two after the server; if a first call says "Python process for KiCAD scripting is not running", wait and retry once.
- Typical release flow: `open_project` > `run_drc` > `export_gerbers` (pass `layers` for a fab set; the default plots every layer, including user and adhesive layers) > `export_drill` > `export_bom` / `export_position_file`.
- `export_gerbers` reads the saved board file; save before exporting.

## `kicad-review` MCP (kicad-mcp-pro, read-only)

- Starts in read-only mode on purpose. Use `kicad_set_project`, then `run_erc`, `run_drc`, `project_quality_gate`, `validate_footprints_vs_schematic`.
- `pcb_visual_qa` reported "extends outside the board outline" for parts on a board that passes KiCad DRC. Treat its findings as hints and confirm with DRC.

## tscircuit

- Workflow in `vendor/electronics/tscircuit-skill/SKILL.md`: `tsci check netlist` > `tsci check placement` > `tsci build` > `tsci export -f gerbers` (also `kicad_pcb`, `step`, `pcb-png`).
- Supplier-part warnings are real findings. In testing, the auto-picked JLCPCB LED had pin 1 as cathode while the circuit used pin 1 as anode; the build failed until `pinLabels` matched the part.
- The autorouter uses 0.15 mm traces and about 0.13 mm clearance. JLCPCB can make that, but KiCad's default rules flag it. Set explicit widths for power nets, then export `kicad_pcb` and run `kicad-cli pcb drc` as a second check.
- "cannot verify pick-and-place rotation" means the assembly rotation for that part needs a human look before ordering assembly.

## atopile

atopile 0.15.9 is installed (`ato`), but part picking needs `ato auth login` with an atopile account, and the project is moving to app.atopile.io. Use it when the user has an account; otherwise prefer tscircuit or KiCad. Its `.claude/skills` are written for atopile's own agent and repo; only `ato` and `ato-language` help with board design.

