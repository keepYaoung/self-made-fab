# self-made-fab

[English](README.md) · 한국어

실제로 만들 제품을 AI와 함께 설계하고, 생산 파일까지 뽑기 위한 도구 모음입니다.
Fusion 360을 중심으로 코드 CAD, KiCad 회로·기판, CNC·3D 프린팅·레이저 가공 검사를 한 번에 설치하고,
Codex가 작업 단계에 맞는 도구를 고르도록 안내하는 `self-made-fab` 스킬을 함께 제공합니다.

모든 도구는 2026-10-16에 직접 시험했습니다. 결과와 근거는 [품질 점검 보고서](docs/quality-report.ko.md)에 있습니다.

## 들어 있는 것

| 단계 | 도구 | 점수 | 하는 일 |
|---|---|---|---|
| Fusion 360 | Autodesk 내장 Fusion MCP | 대기 | 열려 있는 Fusion 설계를 AI가 직접 조작 |
| Fusion 360 | [fusion360-mcp-server](https://github.com/faust-machines/fusion360-mcp-server) | 대기 | 스케치·돌출·조인트·간섭 검사 등 93개 도구 |
| 코드 CAD | [text-to-cad](https://github.com/earthtojake/text-to-cad) | 5 | 말로 설명 → STEP·STL, 도면, DFM, 외주 견적 |
| 코드 CAD | [build123d-mcp](https://github.com/pzfreo/build123d-mcp) | 5 | 치수를 재며 형상 만들기, 렌더, 내보내기 |
| 코드 CAD | [cad-drawing-to-model](https://github.com/Anson2251/cad-drawing-to-model-skill) | 참고 | 2D 도면 → 3D 모델 재구성 가이드 |
| 가공 | [AgentCADCAM](https://github.com/jeremylongworth-source/AgentCADCAM) | 4 | CNC·3D 프린팅·레이저 사전 점검, G-code 검사 |
| 회로·기판 | [KiCAD-MCP-Server](https://github.com/mixelpixx/KiCAD-MCP-Server) | 4 | KiCad 편집·배선·거버/드릴/BOM 출력 |
| 회로·기판 | [kicad-mcp-pro](https://github.com/oaslananka/kicad-mcp-pro) | 4 | 읽기 전용 ERC·DRC·품질 게이트 |
| 회로·기판 | [tscircuit](https://github.com/tscircuit/skill) | 4 | 코드로 작은 기판 설계, 생산 파일 출력 |
| 회로·기판 | [atopile](https://github.com/atopile/atopile) | 2 | 관찰 중 (부품 선택에 계정 로그인 필요) |
| 보여주기 | [mcp-for-blender](https://github.com/ahujasid/mcp-for-blender) | 선택 | Blender가 설치돼 있으면 렌더·재질 작업 |
| 보여주기 | [anatomy](https://github.com/wheresryan22/anatomy) | 참고 | 작동 원리를 보여주는 인터랙티브 그림 |
| 선택 | [freecad-mcp](https://github.com/neka-nat/freecad-mcp) | 선택 | FreeCAD가 설치돼 있으면 연결 |

원본 저장소는 `vendor/` 아래에 서브모듈로 연결되어 있고, 시험한 커밋에 고정되어 있습니다.
버전, 라이선스, 제외한 후보와 이유는 [catalog.yaml](catalog.yaml)에 있습니다.

## 설치

필요한 것: macOS, Codex, `git`, `python3`, `uv`, `node` (`brew install uv node`).
KiCad와 Fusion 360은 있으면 자동으로 연결합니다.

```bash
git clone https://github.com/keepYaoung/self-made-fab.git ~/.codex/self-made-fab
cd ~/.codex/self-made-fab
./install.sh            # 전부 설치 (관리자 비밀번호 필요 없음)
./install.sh --check    # Codex를 재시작한 뒤, 서버가 응답하는지 확인
```

일부만 설치하려면 `./install.sh --only kicad,cad`, 실행 전에 미리 보려면 `--dry-run`을 붙입니다.

설치 스크립트가 하는 일:

1. 원본 저장소를 내려받고 `self-made-fab` 스킬을 `~/.codex/skills`에 연결
2. text-to-cad 플러그인 설치, cadgen 사용 통계 끄기
3. Codex 설정(`~/.codex/config.toml`)에 MCP 서버 등록: `build123d`, `fusion`, `fusion-tools`, `kicad`, `kicad-review` (바꾸기 전에 `.bak` 백업)
4. KiCad 라이브러리 목록 설정, KiCad MCP 빌드
5. `tsci` 설치, 가공 검사 스크립트 환경 준비

### Fusion 360 연결

1. Fusion에 로그인하고 설계 하나를 엽니다.
2. **환경설정 → 일반 → API → Fusion MCP Server**를 켭니다 (포트 27182).
3. 구조화된 도구도 쓰려면 **유틸리티 → 추가 기능(Shift+S)**에서 `Fusion360MCP`를 실행합니다.

## 사용 예

```text
$self-made-fab 라즈베리파이 4가 들어갈 케이스를 Fusion에서 만들어줘. 벽 두께 2 mm, FDM 출력용.
$self-made-fab 이 KiCad 프로젝트 DRC 돌리고 JLCPCB용 거버 뽑아줘.
$self-made-fab 첨부한 도면대로 브래킷 STEP 만들고 CNC 가공 전 점검해줘.
```

## 업데이트

```bash
git pull && git submodule update --init --depth 1
./install.sh
```

원본 저장소를 새 버전으로 올릴 때는 `git submodule update --remote vendor/<단계>/<프로젝트>` 후
보고서의 시험을 다시 돌리고 `catalog.yaml`의 커밋을 갱신합니다.

## 라이선스

`vendor/` 아래 각 프로젝트는 원래 라이선스를 따릅니다. 이 저장소는 코드를 복사하지 않고 링크로만 연결합니다.

