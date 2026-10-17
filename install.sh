#!/usr/bin/env bash
# self-made-fab installer for macOS + Codex.
#
#   ./install.sh                 install every group
#   ./install.sh --only kicad,cad
#   ./install.sh --dry-run       print what would run
#   ./install.sh --check         start each configured MCP server and list its tools
#
# Groups: skill cad fusion kicad tscircuit cam extras
# Nothing here needs sudo. Re-running is safe: links and MCP entries are replaced.

set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CODEX_DIR="${CODEX_HOME:-$HOME/.codex}"
FUSION_ADDINS="$HOME/Library/Application Support/Autodesk/Autodesk Fusion 360/API/AddIns"
KICAD_APP="/Applications/KiCad/KiCad.app"
KICAD_PY="$KICAD_APP/Contents/Frameworks/Python.framework/Versions/Current/bin/python3"
KICAD_TEMPLATES="$KICAD_APP/Contents/SharedSupport/template"
MX="$REPO/vendor/electronics/KiCAD-MCP-Server"
FAUST="$REPO/vendor/fusion/fusion360-mcp-server"
CAM="$REPO/vendor/cam/AgentCADCAM"
CAM_VENV="$REPO/.venv-cam"

# Versions verified in docs/quality-report.md
BUILD123D_MCP="build123d-mcp==0.3.91"
KICAD_MCP_PRO="kicad-mcp-pro==4.3.0"
CADGEN="cadgen==0.7.21"
FREECAD_MCP="freecad-mcp==0.1.27"
BLENDER_MCP="mcp-for-blender==2.1.9"

ALL_GROUPS="skill cad fusion kicad tscircuit cam extras"
ONLY=""
DRY=0
CHECK=0

usage() { sed -n '2,11p' "$0" | sed 's/^# \{0,1\}//'; }

while [[ $# -gt 0 ]]; do
  case "$1" in
    --only) ONLY="$2"; shift 2 ;;
    --dry-run) DRY=1; shift ;;
    --check) CHECK=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "unknown option: $1" >&2; usage; exit 2 ;;
  esac
done

say()  { printf '\n\033[1m== %s\033[0m\n' "$*"; }
ok()   { printf '  ok    %s\n' "$*"; }
skip() { printf '  skip  %s\n' "$*"; }
warn() { printf '  warn  %s\n' "$*" >&2; }
run()  { if [[ $DRY -eq 1 ]]; then printf '  + %s\n' "$*"; else "$@"; fi; }
want() { [[ -z "$ONLY" || ",$ONLY," == *",$1,"* ]]; }
abs()  { command -v "$1" 2>/dev/null || true; }
mcp()  { run python3 "$REPO/scripts/codex_mcp.py" "$@"; }

UV="$(abs uv)"; UVX="$(abs uvx)"; NODE="$(abs node)"; NPM="$(abs npm)"; CODEX="$(abs codex)"

require() {
  local missing=0
  for tool in git python3 uv uvx node npm; do
    if [[ -z "$(abs "$tool")" ]]; then warn "missing $tool"; missing=1; fi
  done
  if [[ $missing -eq 1 ]]; then
    echo "Install the missing tools first (brew install uv node git python)." >&2
    exit 1
  fi
}

# Link $1 to $2, replacing an older symlink but never a real folder.
link() {
  local src="$1" dst="$2"
  if [[ -e "$dst" && ! -L "$dst" ]]; then
    warn "$dst exists and is not a link; leaving it alone"
    return 0
  fi
  run mkdir -p "$(dirname "$dst")"
  run ln -sfn "$src" "$dst"
  ok "linked $(basename "$dst")"
}

group_skill() {
  say "skill: vendor sources and the self-made-fab skill"
  run git -C "$REPO" submodule update --init --depth 1
  link "$REPO/skills/self-made-fab" "$CODEX_DIR/skills/self-made-fab"
}

group_cad() {
  say "cad: text-to-cad plugin and build123d MCP"
  if [[ -n "$CODEX" ]]; then
    run "$CODEX" plugin marketplace add earthtojake/text-to-cad --ref latest || true
    run "$CODEX" plugin add text-to-cad@earthtojake || true
    ok "text-to-cad plugin (restart Codex to load it)"
  else
    skip "codex CLI not on PATH; install text-to-cad from the Codex plugin directory"
  fi
  # cadgen sends usage stats by default; turn them off. Re-enable with: cadgen telemetry on
  run "$UVX" --no-config --managed-python --python 3.13 --from "$CADGEN" cadgen telemetry off >/dev/null || true
  ok "cadgen telemetry off"
  mcp add build123d --command "$UV" --arg tool --arg run --arg --python --arg 3.12 --arg "$BUILD123D_MCP" \
    --startup-timeout 180 --tool-timeout 300
}

group_fusion() {
  say "fusion: add-ins and MCP entries"
  if [[ ! -d "$(dirname "$FUSION_ADDINS")" ]]; then
    skip "Fusion 360 not found (open Fusion once, then re-run with --only fusion)"
    return 0
  fi
  # Autodesk's built-in server: Fusion > Preferences > General > API > "Fusion MCP Server".
  mcp add fusion --url "http://127.0.0.1:27182/mcp" --tool-timeout 300
  # faust-machines server from the pinned checkout (its PyPI 0.1.0 breaks on mcp>=2).
  link "$FAUST/addon" "$FUSION_ADDINS/Fusion360MCP"
  mcp add fusion-tools --command "$UV" --arg run --arg --frozen --arg --directory --arg "$FAUST" \
    --arg fusion360-mcp-server --arg --mode --arg socket --startup-timeout 180 --tool-timeout 300
  # Autodesk's older sample add-in (HTTP on port 9100); kept as a disabled fallback.
  link "$REPO/vendor/fusion/FusionMCPSample/Fusion MCP Addin" "$FUSION_ADDINS/Fusion MCP Addin"
  mcp add fusion-sample --url "http://localhost:9100/" --tool-timeout 300 --disabled
  echo "  next  in Fusion: Preferences > General > API > enable 'Fusion MCP Server' (port 27182)"
  echo "  next  in Fusion: Utilities > Add-Ins (Shift+S) > run 'Fusion360MCP' for the fusion-tools server"
}

group_kicad() {
  say "kicad: library tables and two KiCad MCP servers"
  if [[ ! -x "$KICAD_PY" ]]; then
    skip "KiCad not found in /Applications/KiCad (brew install --cask kicad)"
    return 0
  fi
  local version prefs
  version="$("$KICAD_APP/Contents/MacOS/kicad-cli" version | cut -d. -f1).0"
  prefs="$HOME/Library/Preferences/kicad/$version"
  run mkdir -p "$prefs"
  for table in fp-lib-table sym-lib-table; do
    if [[ -f "$prefs/$table" ]]; then
      ok "$table already present"
    else
      run cp "$KICAD_TEMPLATES/$table" "$prefs/$table"
      ok "$table installed (without it ERC/DRC report missing footprint libraries)"
    fi
  done

  # mixelpixx/KiCAD-MCP-Server: editing, routing, Gerber/drill/BOM export.
  if [[ ! -x "$MX/venv/bin/python3" ]]; then
    run "$KICAD_PY" -m venv --system-site-packages "$MX/venv"
  fi
  run "$MX/venv/bin/python3" -m pip install -q -r "$MX/requirements.txt"
  run "$NPM" --prefix "$MX" ci --silent --no-audit --no-fund
  run "$NPM" --prefix "$MX" run -s build
  local site
  site="$("$MX/venv/bin/python3" -c 'import sysconfig; print(sysconfig.get_paths()["purelib"])' 2>/dev/null || echo "$MX/venv/lib/python3.9/site-packages")"
  mcp add kicad --command "$NODE" --arg "$MX/dist/index.js" \
    --env "KICAD_PYTHON=$MX/venv/bin/python3" --env "PYTHONPATH=$site" --env LOG_LEVEL=info \
    --startup-timeout 120 --tool-timeout 300

  # kicad-mcp-pro: read-only review, ERC/DRC and the project quality gate.
  mcp add kicad-review --command "$UVX" --arg "$KICAD_MCP_PRO" --arg --transport --arg stdio \
    --env KICAD_MCP_PROFILE=default --env KICAD_MCP_OPERATING_MODE=readonly \
    --startup-timeout 120 --tool-timeout 300
}

group_tscircuit() {
  say "tscircuit: tsci CLI"
  if [[ -n "$(abs tsci)" ]]; then
    ok "tsci $(tsci --version 2>/dev/null)"
  else
    run "$NPM" install -g tscircuit --silent --no-audit --no-fund
    ok "tsci installed"
  fi
}

group_cam() {
  say "cam: AgentCADCAM review scripts"
  [[ -x "$CAM_VENV/bin/python" ]] || run python3 -m venv "$CAM_VENV"
  run "$CAM_VENV/bin/python" -m pip install -q -r "$CAM/requirements-test.txt"
  ok "run checks with $CAM_VENV/bin/python $CAM/scripts/nc_static_checks.py <program.nc>"
}

group_extras() {
  say "extras: FreeCAD and Blender (only when installed)"
  if [[ -d /Applications/FreeCAD.app ]]; then
    mcp add freecad --command "$UVX" --arg "$FREECAD_MCP" --startup-timeout 120 --tool-timeout 300
    echo "  next  copy vendor/code-cad/freecad-mcp/addon/FreeCADMCP into FreeCAD's Mod folder and start its RPC server"
  else
    skip "FreeCAD not installed"
  fi
  if [[ -d /Applications/Blender.app ]]; then
    mcp add blender --command "$UVX" --arg "$BLENDER_MCP" --env DISABLE_TELEMETRY=true \
      --startup-timeout 120 --tool-timeout 300
    echo "  next  install the Blender add-on: $UVX $BLENDER_MCP setup (or vendor/presentation/mcp-for-blender/addon.py)"
  else
    skip "Blender not installed"
  fi
}

check() {
  say "check: start each configured server and count its tools"
  local name args
  while IFS= read -r line; do
    name="${line%%$'\t'*}"
    args="${line#*$'\t'}"
    # args is a NUL-free, shell-quoted argument list produced by Python's shlex.
    if out="$(eval "\"$UV\" run -q --with mcp \"$REPO/scripts/mcp_probe.py\" -q --timeout 120 --delay 0 $args" 2>/dev/null | head -1)" && [[ -n "$out" ]]; then
      ok "$name: $out"
    else
      warn "$name: did not answer (Fusion: is it open with the add-in running?)"
    fi
  done < <(python3 - "$CODEX_DIR/config.toml" <<'PY'
import shlex, sys, tomllib
cfg = tomllib.load(open(sys.argv[1], "rb")).get("mcp_servers", {})
for name in ["build123d", "kicad", "kicad-review", "fusion", "fusion-tools", "fusion-sample", "freecad", "blender"]:
    s = cfg.get(name)
    if not s or not s.get("enabled", True):
        continue
    if "url" in s:
        args = "--url " + shlex.quote(s["url"])
    else:
        env = " ".join("--env " + shlex.quote(f"{k}={v}") for k, v in s.get("env", {}).items())
        cmd = " ".join(shlex.quote(x) for x in [s["command"], *s.get("args", [])])
        args = f"{env} -- {cmd}".strip()
    print(f"{name}\t{args}")
PY
)
}

require
if [[ $CHECK -eq 1 ]]; then check; exit 0; fi
for group in $ALL_GROUPS; do
  if want "$group"; then "group_$group"; fi
done
say "done. Restart Codex so it picks up the skill, plugin and MCP servers, then run ./install.sh --check"

