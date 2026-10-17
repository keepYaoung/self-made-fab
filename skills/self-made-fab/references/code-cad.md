# Code CAD

## build123d MCP (`build123d`)

- Loop: `execute` (build123d code, `show(part, "name")`) > `measure` > `render_view` > `export`. Call `workflow_hints` once per session for the server's own guidance.
- After every boolean, check that the face count changed; a failed cut leaves topology unchanged.
- `export` and `render_view(save_to=...)` write only inside the server's working directory or the temp folder. Export into the project folder Codex is working in; absolute paths elsewhere are rejected.
- `bd_warehouse` ships with the server: use it for threads, fasteners, bearings and gears.
- `save_snapshot`/`restore_snapshot` let you try a change and roll it back without touching the source.

## text-to-cad plugin

- Installed as the Codex plugin `text-to-cad@earthtojake`; it brings skills (`cad`, `dxf`, `engineering-drawing`, `step-parts`, `dfm`, `dfam-check`, `gcode`, `bambu-labs`, `sendcutsend`) and the CAD viewer.
- A model is a Python script with a decorated function (`@step`, `@stl`) that returns a build123d shape; run the script to regenerate outputs. Output paths are relative to the script.
- `cadgen step snapshot STEP/part.step out.png` renders a saved STEP. The first run downloads a headless browser.
- cadgen telemetry is on by default upstream; the installer turns it off. `cadgen telemetry status` shows the state.

## Drawing to model

`vendor/code-cad/cad-drawing-to-model` covers reading multi-view drawings: reconstruct first, then modify through the source. Record every dimension you inferred rather than read.

## FreeCAD

`freecad` MCP is registered only when FreeCAD is installed. It needs the FreeCADMCP add-on running inside FreeCAD.

