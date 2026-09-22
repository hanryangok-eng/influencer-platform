# GLOEUM 글로이음 v2.24.1

기존 해외 바이어 발굴 기능과 공개 검색결과 기반 Instagram 인플루언서 후보 발굴 기능을 함께 제공하는 Streamlit 개발본입니다.

> 이 버전은 v2.23.14 운영본과 분리된 신규 개발선입니다. 운영 Render 서비스에 바로 덮어쓰지 말고 별도 브랜치·미리보기 서비스에서 먼저 검수하십시오.

## 운영 진입점

- 웹앱: `app.py`
- 기업 바이어 수집·판정: `buyer_core.py`
- Instagram 후보 수집·판정: `influencer_core.py`
- Instagram 화면: `influencer_app.py`
- Instagram Excel: `influencer_exporter.py`
- 기업 바이어 Excel: `excel_exporter.py`
- 버전 상수: `version.py`
- 배포: `Dockerfile`, `render.yaml`

## v2.24.0 신규 기능(누적 유지)

- 화면 상단에서 `기업 바이어 / Instagram 인플루언서` 검색 모드를 선택합니다.
- 국가·분야·키워드·팔로워 범위·후보 수를 설정합니다.
- Brave 또는 Tavily 공개 검색결과에서 Instagram 프로필 후보만 분리합니다.
- 게시물·릴스·로그인 페이지와 명확한 기업·공식상점 계정을 제외합니다.
- 계정명, 표시명, 유형, 팔로워 공개표시, 공개 이메일, 적합도 등급, 검색근거를 정리합니다.
- 후보별 영문 DM·이메일 초안을 생성합니다.
- `Instagram 프로필 열기`, `DM 복사`, `이메일 작성창 열기`를 제공합니다.
- DM·이메일 연락 상태를 기록하고 Excel에 반영합니다.
- Instagram 결과 Excel을 `인플루언서결과 / DM초안 / 이메일연락 / 검색근거` 4개 시트로 생성합니다.

## v2.24.1 변경사항

- `campaign_runner.py`의 다업종 동시 수집 체크포인트에 버전이 `2.23.9`로 고정 기록되던 결함을 수정했습니다(이제 `version.py`의 현재 버전을 그대로 씁니다).
- Instagram 인플루언서 판정에서 "국가명이 본문 어딘가에 있으면 가점"하던 방식을 없애고, **국기 이모지·도시명 같은 명시적 위치 신호로만 위치를 판단**하도록 바꿨습니다. 대상국이 아닌 다른 나라의 국기·도시명이 확인되면 등급을 낮추고 `위치확인=불일치`로 표시합니다(자동 제외는 아님 — 최종 판단은 사람이 하도록 남겨둡니다).
- 기업·미디어 계정 제외 키워드에 매거진·에디토리얼·오피셜 계정류 용어를 추가했습니다.
- 팔로워 5만 이상이면서 1인칭 표현이 없는 계정은 `브랜드·미디어 의심(수동확인)`으로 별도 표시합니다.
- Instagram 결과 Excel에 `위치확인`, `위치근거` 컬럼이 추가됐습니다.

## 안전 범위

- Instagram에 로그인하지 않습니다.
- 비공개 계정 정보, 팔로워 목록, 쿠키, 세션 정보를 수집하지 않습니다.
- 검색결과에 공개된 정보만 사용하며 이메일을 추정 생성하지 않습니다.
- 임의 계정에 DM이나 이메일을 자동 발송하지 않습니다.
- 초안을 담당자가 검수한 뒤 Instagram 또는 기본 메일 앱에서 직접 발송합니다.
- 팔로워 수와 이메일은 연락 전 원본 프로필에서 다시 확인해야 합니다.

## 로컬 확인

Python 3.12 권장:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run_offline_tests.py
streamlit run app.py
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

정상 기준은 `85/85 passed`이며 화면 상단에 `v2.24.1`이 표시되어야 합니다. (이번 버전은 테스트 파일이 포함되지 않은 배포용 최소 ZIP이라 발신 측에서 직접 재실행해 확인해야 합니다.)

## 미리보기 배포 순서

1. v2.23.14 운영 브랜치와 별도의 `develop-v2.24.x` 브랜치를 만듭니다.
2. 이 폴더의 파일을 새 브랜치에 업로드합니다.
3. API 키는 파일에 넣지 말고 Render 환경변수로만 설정합니다.
4. 기존 운영 서비스가 아닌 별도 Preview Web Service를 만듭니다.
5. 베트남·뷰티·20개 조건으로 시험수집합니다.
6. Instagram 원본 프로필과 Excel의 계정명·팔로워·공개 이메일·DM 문구를 검수합니다.
7. 결과가 안정적일 때만 100개로 확대합니다.

필수 환경변수는 `BRAVE_SEARCH_API_KEY`이며, `TAVILY_API_KEY`는 선택입니다. 기업 바이어 모드에서만 `HUNTER_API_KEY`를 선택적으로 사용합니다.

상세 검수 기준은 `UPDATE_GUIDE_v2.24.0.md`(최초 도입)와 `UPDATE_GUIDE_v2.24.1.md`(이번 수정)를 함께 참고하십시오.
