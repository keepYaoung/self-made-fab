# 품질 점검 보고서

점검일: 2026-10-16 · 환경: macOS (Apple Silicon), Codex CLI 0.151.0, KiCad 10.0.6, Fusion 2704.1.23

각 도구에 같은 시험 과제를 주고 결과를 직접 확인했습니다. 도구가 "성공"이라고 답한 것만 보지 않고, 숫자는 손으로 계산한 값과 비교했고, 회로 검사는 KiCad 공식 검사기(kicad-cli)로 다시 돌렸습니다.

## 요약

| 도구 | 점수 | 시험 내용 | 결과 |
|---|---|---|---|
| text-to-cad (cadgen 0.7.21) | 5/5 | ㄱ자 브래킷 → STEP·STL·렌더 | 부피 13,638.36 mm³, 손계산과 일치 |
| build123d-mcp 0.3.91 | 5/5 | 같은 브래킷을 MCP로 | 부피·치수 일치, STEP·STL·PNG 출력 |
| AgentCADCAM | 4/5 | 자체 테스트, G-code에 결함 주입 | 657개 통과, 결함 3/3 검출 |
| KiCad MCP (mixelpixx) | 4/5 | 예제 기판 열기 → DRC → 거버 | DRC 0, 거버 21장+드릴 |
| kicad-mcp-pro 4.3.0 | 4/5 | 예제 기판 ERC·DRC·품질 게이트 | ERC/DRC 0 (kicad-cli와 일치) |
| tscircuit (tsci 0.0.2916) | 4/5 | LED 기판 설계 → 생산 파일 | 실제 극성 오류 검출, 생산 파일 완비 |
| atopile 0.15.9 | 2/5 | 공식 quickstart 빌드 | 부품 선택 단계에서 계정 로그인 요구 |
| Fusion 내장 MCP | 대기 | — | Fusion 로그인 후 시험 |
| faust fusion360-mcp-server | 대기 | 서버 기동 | 고정 버전으로 93개 도구 확인, 실연결은 로그인 후 |
| freecad-mcp, mcp-for-blender | 미평가 | 서버 기동만 | 17개 / 9개 도구, 본 프로그램 미설치 |

## 기계 설계

### build123d-mcp

![build123d 브래킷](assets/build123d-bracket.png)

- 과제: 60×40×30 mm, 두께 4 mm ㄱ자 브래킷에 지름 4.4 mm 구멍 2개.
- 손계산: 단면 344 mm² × 40 mm − 구멍 2 × π × 2.2² × 4 = 13,638.4 mm³.
- 도구 결과: 13,638.3575 mm³, 바운딩 박스 60×40×30, 면 10개, 원통면 2개(지름 4.4) 인식.
- 좋은 점: `measure`가 무게중심·관성·면 목록까지 돌려줘서 그림 없이도 결과를 검증할 수 있음. 서버 작업 폴더 밖에는 쓰지 못하게 막는 안전장치.
- 주의: 작업 폴더 밖 경로로 내보내면 거부됨. Codex에서는 프로젝트 폴더가 작업 폴더라 실사용 문제는 없음.

### text-to-cad

![text-to-cad 브래킷](assets/text-to-cad-bracket.png)

- 같은 브래킷을 모델 스크립트(`@step`, `@stl`)로 작성 → STEP 30 KB, STL 34 KB.
- 다시 읽어 측정한 부피 13,638.36 mm³로 build123d-mcp와 일치.
- 렌더 품질이 가장 좋음. 도면·DXF·DFM·G-code·외주 견적(SendCutSend, Bambu) 스킬까지 묶여 있음.
- 주의: 사용 통계 전송이 기본으로 켜져 있음 → 설치 스크립트가 끔.

## 가공

### AgentCADCAM

- 자체 검증: 기반 검사, 스키마 108건, 단위 테스트 657개 모두 통과.
- 결함 주입 시험 (예제 밀링 프로그램을 일부러 망가뜨림):

| 넣은 결함 | 검출 |
|---|---|
| 스핀들을 켜지 않고 절삭 이동 | 해당 5줄 지적 |
| 급속 이동으로 Z−5까지 하강 | "Z-5가 허용 범위 초과" |
| mm → inch 전환 (G21 → G20) | 단위 불일치·미지원 명령으로 차단 |

- 좋은 점: 어떤 경우에도 "사람 승인·시뮬레이션 필요"를 붙여 실행 허가를 내주지 않음. 확인 못 한 범위를 결과에 그대로 적음.
- 주의: 기계·공구·컨트롤러 정보를 JSON으로 먼저 채워야 의미 있는 검사가 됨. 별 1개의 신생 프로젝트라 4점.

## 회로·기판

### KiCad MCP (mixelpixx)

- KiCad 예제 `pic_programmer`(부품 63개, 배선 370개)로 시험.
- 프로젝트 열기 → 기판 정보(160×99 mm) → DRC 0건 → 거버 21장 + 드릴 파일 생성.
- 좋은 점: 편집·배선·자동 배선·부품 검색(JLCPCB, DigiKey)·생산 파일까지 전부 가능.
- 주의: 도구가 244개라 이름으로 찾기보다 `search_tools`로 찾아야 함. 서버가 켜진 직후 1초 안에 호출하면 "Python process is not running" 오류 → 잠시 후 재시도. 거버 기본값이 모든 레이어를 출력하므로 생산용은 레이어 지정 필요.

### kicad-mcp-pro

- 같은 예제로 ERC 0건, DRC 0건. kicad-cli 직접 검사와 같은 결과.
- 좋은 점: 기본이 읽기 전용이라 실수로 설계를 바꿀 위험이 없음. 결과마다 PASS/WARN/FAIL과 다음 행동을 알려줌.
- 주의: 시각 검사(`pcb_visual_qa`)가 정상 부품 5개를 "기판 밖"이라고 잘못 경고함.

### KiCad 첫 설정에서 발견한 문제

KiCad를 한 번도 열지 않은 상태에서는 전역 라이브러리 목록이 없어서 ERC 44건, DRC 41건이 전부 "라이브러리 없음" 경고로 나옴. 템플릿의 `fp-lib-table`, `sym-lib-table`을 복사하자 0건이 됨. 설치 스크립트가 자동 처리.

### tscircuit

![tscircuit LED 기판](assets/tscircuit-led.png)

- 과제: 2핀 전원 헤더 + 330Ω 저항 + 빨간 LED, 20×15 mm 기판.
- 생산 파일: 거버 10장, 드릴, BOM(JLCPCB 부품번호 포함), 부품 배치 파일, STEP.
- 실제 오류 검출: 자동 선택된 JLCPCB LED(C3030991)는 1번 핀이 음극인데 회로는 1번 핀을 양극으로 사용 → 빌드 실패로 막아줌. 그대로 만들었다면 LED가 켜지지 않았을 것.
- 교차 검증: KiCad 형식으로 내보내 kicad-cli로 검사 → 위반 26건. 원인은 자동 배선 폭 0.15 mm, 간격 0.13 mm로 KiCad 기본 규칙(0.2 mm)보다 좁기 때문. JLCPCB 표준 공정으로는 제작 가능한 수치지만 여유가 적음.

### atopile

- 설치(0.15.9)와 컴파일 단계는 통과, 부품 자동 선택 단계에서 "Sign-in required"로 중단.
- atopile이 웹 서비스(app.atopile.io)로 옮겨 가는 중이라 오프라인 개인 작업에는 불리함.
- 저장소의 스킬 대부분이 atopile 자체 에이전트·개발자용(컴파일러, LSP, Zig 바인딩 등).

## 연결 확인만 한 도구

| 도구 | 결과 | 이유 |
|---|---|---|
| faust fusion360-mcp-server | PyPI 0.1.0은 `mcp>=2`에서 즉시 종료. 저장소 고정 버전으로 실행하면 93개 도구 | Fusion 로그인 대기 |
| freecad-mcp 0.1.27 | 17개 도구로 기동 | FreeCAD 미설치 |
| mcp-for-blender 2.1.9 | 9개 도구로 기동, 기본 익명 통계 전송 | Blender 미설치 |

## 다시 점검하는 방법

```bash
./install.sh --check
uv run --with mcp scripts/mcp_probe.py -v -- uvx kicad-mcp-pro==4.3.0
```

