# Manufacturing checks (AgentCADCAM)

Skills live in `vendor/cam/AgentCADCAM/skills/<name>/SKILL.md`. Read only the one that matches the job:

| Job | Skill |
| --- | --- |
| Scope and missing inputs for any CAD/CAM request | `cadcam-intake-and-scope` |
| Is this part makeable as drawn | `cad-manufacturability-review` |
| CNC setup, workholding, tools, toolpaths | `cnc-setup-planner`, `tooling-plan-review`, `toolpath-strategy-planner` |
| G-code or NC program review | `nc-static-safety-review`, `postprocessor-readiness-review`, `simulation-readiness-review` |
| 3D printing | `additive-job-preflight` |
| Laser cutting (DXF/SVG) | `laser-job-preflight` |
| Drawing, PMI and file handover | `drawing-pmi-handoff-review`, `file-format-interoperability-plan`, `design-file-provenance-review` |

## Scripts

Run them with `<repo>/.venv-cam/bin/python` from `vendor/cam/AgentCADCAM`.

- `scripts/nc_static_checks.py <dir>/programs/<file>.nc` reads machine, controller, tool, setup and job context from `<dir>/contexts/*.json` (copy `fixtures/cnc/mill-bracket/contexts` as a template and fill in the real machine). In testing it caught feed moves without spindle-on, a rapid move below the declared Z bound, and an inch/mm switch.
- `laser_dxf_review.py`, `laser_svg_review.py`, `stl_mesh_review.py`, `three_mf_review.py`, `additive_preflight.py` cover the other processes.
- Every result ends in `review_required` or `blocked` with `HUMAN_APPROVAL_REQUIRED` and `SIMULATION_REQUIRED`. Report those blockers as they are; they are the intended outcome.

Simulate toolpaths in CAMotics or the CAM package's own simulator before a machine run.

