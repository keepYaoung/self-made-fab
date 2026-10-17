# Fusion 360

## Servers

- `fusion` is Autodesk's built-in MCP server at `http://127.0.0.1:27182/mcp`. Turn it on in Fusion: Preferences > General > API > "Fusion MCP Server (runs locally on this device)". Fusion must be running, signed in, with a design open.
- `fusion-tools` is the faust-machines server (about 90 structured tools: sketches, extrude, fillet, joints, parameters, interference, STEP/F3D export). It talks to the Fusion360MCP add-in over a local socket; start the add-in from Utilities > Add-Ins (Shift+S). It runs from the pinned checkout because the PyPI release 0.1.0 crashes with `mcp>=2`.
- `fusion-sample` (disabled) is Autodesk's older sample add-in on port 9100 with three tools: `execute_api_script`, `get_screenshot`, `get_api_documentation`. Enable it only if the built-in server is unavailable.

## Working in a live design

- Read the design first (components, bodies, user parameters) and drive dimensions through named user parameters so the user can change them later in Fusion.
- Take a screenshot or a measurement after each feature; a script that ran without error can still produce the wrong body.
- Save a version before large edits and ask before deleting bodies, components or timeline features.
- Export STEP for handover and F3D when the user wants the editable Fusion file.

## When it does not connect

- Port 27182 refused: the preference is off, or Fusion is not running or not signed in.
- `fusion-tools` times out: the Fusion360MCP add-in is not running.
- Fusion shows a sign-in window: the user must sign in; do not type credentials.

