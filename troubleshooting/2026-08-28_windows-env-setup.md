# Windows 로컬 실행 환경 구성 트러블슈팅 로그

> 이 문서는 실습 중 Claude(AI)와의 대화를 바탕으로 작성됨. 명령 실행·결과는 실제 수행값이며,
> 원인 분석과 문서 정리에 AI를 활용함.

- **날짜**: 2026-08-28
- **과제**: AI1 22/30주차 — 『모두의 딥러닝』 16장 이미지 인식(CNN)
- **목표**: Colab에서 학습·저장한 `MNIST_CNN.keras` 모델을 Windows 로컬 Python 환경으로 옮겨 실행
- **최종 결과**: 환경 구성 성공 (`tensorflow 2.16.1` + `keras 3.15.1`, Python 3.11.9, venv)
- **이 문서의 목적**: 겪은 문제를 나중에 심화 분석할 수 있도록 증상·원인·해결·분석 포인트를 그대로 남긴다.

---

## 환경 요약

| 항목 | 값 |
|---|---|
| OS | Windows 11 Home (10.0.26200) |
| Colab TensorFlow | 2.20.0 |
| 로컬 Python | 3.11.9 (`py -3.11`) — 3.12 미설치, 3.14는 TF 미지원 |
| 로컬 TensorFlow | 2.16.1 (`requirements.txt` 고정) |
| 로컬 Keras | 3.15.1 (TF 2.16.1의 의존성으로 자동 설치) |
| 최종 프로젝트 경로 | `C:\ir\windows` (원래 `C:\Users\user\Downloads\image_recognition_practice_files\image_recognition_colab_windows_assignment\windows`에서 이동) |

---

## 문제 목록

### P1. `Set-Location -LinteraPath` — 매개변수 이름 오타

- **증상**
  ```
  Set-Location : 매개 변수 이름 'LinteraPath'과(와) 일치하는 매개 변수를 찾을 수 없습니다.
  ```
- **원인**: `-LiteralPath`를 `-LinteraPath`로 오타 (`n` 삽입, `l` 누락). PowerShell은 매개변수 이름 일부만 맞아도 자동완성하지만, 철자가 어긋나면 "일치하는 매개변수 없음" 에러.
- **해결**: `-LiteralPath`로 정정.
- **심화 분석 포인트**
  - `-LiteralPath` vs `-Path`의 차이: `-Path`는 와일드카드(`*`, `?`, `[]`)를 해석하고, `-LiteralPath`는 경로를 글자 그대로 취급. 한글/공백/대괄호가 들어간 경로에서 `-LiteralPath`가 안전.
  - PowerShell의 매개변수 이름 부분 일치(prefix matching) 규칙 — 어디까지 줄여 써도 되는가.

### P2. 압축파일(.zip) 내부 경로로 이동 시도

- **증상**: `Set-Location`이 `...image_recognition_practice_files.zip\...` 경로를 찾지 못함.
- **원인**: 경로 문자열에 `.zip`이 포함됨. zip은 **압축된 단일 파일**이지 폴더가 아니므로 그 내부로는 `cd` 불가. (Windows 탐색기가 zip을 폴더처럼 "미리보기"해줘서 생기는 착각)
- **실제 상태**: zip은 이미 `C:\Users\user\Downloads\image_recognition_practice_files\`(`.zip` 없는 폴더)로 압축 해제돼 있었음.
- **해결**: 경로에서 `.zip` 제거 → `...\image_recognition_practice_files\image_recognition_colab_windows_assignment\windows`.
- **심화 분석 포인트**
  - Windows 탐색기의 "압축 폴더(compressed folder)" 기능이 왜 경로 혼동을 유발하는가.
  - 압축 해제 시 폴더 구조: `<zip이름>\<zip 내부 최상위 폴더>\...` 로 한 단계 더 들어가는 패턴.

### P3. `py -3.11-m venv .venv` — 토큰 사이 공백 누락

- **증상**
  ```
  No suitable Python runtime found
  ```
- **원인**: `-3.11`과 `-m` 사이에 공백이 없어 `py`가 `-3.11-m`을 하나의 버전 지정자로 해석 → 그런 런타임 없음.
- **해결**: `py -3.11 -m venv .venv` (공백 삽입). 다음 시도에서 스스로 정정함.
- **심화 분석 포인트**
  - Windows `py` 런처의 인자 파싱: `-3.11`은 런처 옵션, `-m`부터는 파이썬 인터프리터로 전달.

### P4. Python 3.12 미설치 → 3.11로 대체 가능한가

- **증상**
  ```
  py -3.12 -m venv .venv
  No suitable Python runtime found
  ```
- **원인**: 실습 가이드는 3.12를 권장하나 PC에는 3.11과 3.14만 설치됨.
- **판단**: `requirements.txt`의 모든 패키지(tensorflow 2.16.1 / numpy 1.26.4 / Pillow 10.4.0 / matplotlib 3.9.2)가 **Python 3.9~3.12**를 지원 → 3.11이 범위 안이라 문제없음. 3.14는 TF가 아직 미지원이라 불가.
- **해결**: `py -3.11`로 진행. 가이드의 "3.12.x로 표시되어야 한다"는 문구는 무시(3.11.9로 표시되는 게 정상).
- **심화 분석 포인트**
  - 파이썬 버전 ↔ 패키지 wheel 태그(`cp311`, `cp312`)의 관계 — 왜 마이너 버전마다 별도 빌드가 필요한가.
  - TensorFlow의 파이썬 버전 지원 정책(릴리스별 지원 범위).

### P5. ⭐ TensorFlow 설치 실패 — Windows 경로 길이 260자 제한 (핵심 문제)

- **증상**: 46개 패키지 중 44번째(`tensorflow-intel`)에서 중단
  ```
  ERROR: Could not install packages due to an OSError: [Errno 2] No such file or directory:
  'C:\Users\user\Downloads\image_recognition_practice_files\image_recognition_colab_windows_assignment\windows\.venv\Lib\site-packages\tensorflow\include\external\com_github_grpc_grpc\src\core\ext\filters\client_channel\lb_policy\grpclb\client_load_reporting_filter.h'
  HINT: this system does not have Windows Long Path support enabled
  ```
- **원인**: Windows 기본 `MAX_PATH` = 260자. TensorFlow 패키지는 gRPC C++ 헤더 등 매우 깊게 중첩된 내부 파일을 포함하는데(이 파일 하나만 상대경로 ~160자), 프로젝트 base 경로가 이미 ~95자(`C:\Users\user\Downloads\image_recognition_practice_files\image_recognition_colab_windows_assignment\windows\`)여서 합산 260자 초과 → 파일 생성 실패.
- **해결**: 프로젝트 폴더를 짧은 경로로 이동.
  ```powershell
  Set-Location "C:\"
  Move-Item "C:\Users\user\Downloads\image_recognition_practice_files\image_recognition_colab_windows_assignment" "C:\ir"
  Set-Location "C:\ir\windows"
  # .venv 재생성 후 재설치 → 성공
  ```
  `C:\ir\windows\` 는 ~14자로 약 80자 절약 → 설치 통과.
- **대안 (미채택)**: 레지스트리/그룹정책으로 Long Path 지원 활성화
  - `HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem` 의 `LongPathsEnabled` = 1 (관리자 권한 필요, 재부팅 권장)
  - 채택 안 한 이유: 관리자 권한 필요 + 시스템 전역 설정 변경이라, 폴더 이동이 더 간단하고 부작용 없음.
- **심화 분석 포인트**
  - `MAX_PATH` 260 제한의 역사적 배경(Win32 API `CreateFileW`), `\\?\` 접두사 우회.
  - Windows 10 1607+ 의 `LongPathsEnabled` opt-in — 왜 기본값이 여전히 꺼져 있는가(구형 앱 호환성).
  - Python/pip이 long path를 다루는 방식, `venv` 안에 헤더 파일까지 통째로 설치하는 이유.
  - 애초에 딥러닝 프로젝트는 **얕은 경로(`C:\dev\...` 등)에 두는 것이 관례** — 이번 실수의 교훈.

### P6. `Move-Item` 실패 — 대상 폴더가 "사용 중"

- **증상**
  ```
  Move-Item : '...image_recognition_colab_windows_assignment'의 항목이 사용 중이므로 항목을 이동할 수 없습니다.
  ```
- **원인**: 이동하려는 폴더의 하위(`...\windows`)에 **현재 PowerShell 세션의 작업 디렉터리(CWD)가 위치**해 있었음. 프로세스가 CWD로 잡고 있는 폴더 및 그 상위는 이동/삭제 불가(Windows 파일 잠금).
- **해결**: `Set-Location "C:\"` 로 먼저 폴더 밖으로 나온 뒤 `Move-Item` 실행 → 성공.
- **추가 확인 사항**: 해당 폴더를 열어둔 파일 탐색기 창, 에디터 등도 같은 잠금을 유발.
- **심화 분석 포인트**
  - Windows의 파일 잠금(mandatory locking) vs Linux(inode 기반, 사용 중에도 rename/삭제 가능) 차이.
  - `handle.exe`(Sysinternals)로 어떤 프로세스가 폴더를 잡고 있는지 확인하는 법.

### P7. (해결·비이슈로 판명) Colab TF 2.20.0 ↔ 로컬 TF 2.16.1 버전 불일치

- **상황**: 모델은 Colab TF 2.20.0에서 `.keras`로 저장, 로컬은 TF 2.16.1 / Keras 3.15.1.
- **리스크(사전 우려)**: `.keras`(Keras 3 zip 포맷)는 대체로 하위호환되지만, 상위 버전에서 저장한 파일을 하위 버전에서 로드할 때 레이어 직렬화 스펙 차이로 실패 가능(가이드 4.3에서 경고).
- **실제 결과**: `tf.keras.models.load_model()` **정상 로드 성공.** 로컬 TF 2.16.1에서 예측까지 완료(본인 손글씨 "2" → 2, 85.96%). 이번 모델은 표준 레이어(Conv2D/MaxPooling2D/Dropout/Flatten/Dense)만 써서 두 Keras 3 버전 간 직렬화 스펙이 동일했던 것으로 보임.
- **대응 계획(미발동)**: 만약 실패했다면 Colab 노트북 상단에 `!pip install tensorflow==2.16.1` 추가 후 런타임 재시작 → 재학습·재저장 → 새 `.keras` 다운로드.
- **심화 분석 포인트**
  - Keras 3의 `.keras` 파일 내부 구조(`config.json` + `model.weights.h5` + `metadata.json`).
  - TF/Keras 버전과 직렬화 호환성 매트릭스 — 어느 정도 범위까지 안전한가.
  - Colab 런타임의 TF 버전을 고정하는 방법과 그 트레이드오프.

---

## 시간순 요약 (원인 → 판단 → 조치 흐름)

1. zip을 풀지 않았다고 착각 → 실제로는 풀려 있었고 경로에 `.zip`만 잘못 포함 (P2)
2. 명령어 오타 연속 (P1 `-LinteraPath`, P3 `-3.11-m`) → PowerShell 문법 특유의 함정, 정정하며 진행
3. 3.12 없음 확인 → 패키지 지원 범위 근거로 3.11 채택 결정 (P4)
4. venv 생성 성공, pip 설치가 **막판 44/46에서 경로 길이로 실패** (P5) ← 오늘의 핵심
5. 해결 위해 폴더 이동하려 했으나 CWD 잠금으로 또 실패 (P6) → 폴더 밖으로 나온 뒤 이동
6. `C:\ir\windows`에서 venv 재생성 → 설치 전 과정 성공
7. 남은 리스크: TF 버전 불일치는 모델 로드 시점에 판명 (P7)

---

## 다음 단계

- [x] `Copy-Item` 으로 `MNIST_CNN.keras` → `C:\ir\windows\models\`
- [x] `check_environment.py` 실행 (모델/이미지 `[있음]` 확인)
- [x] 본인이 만든 손글씨 PNG로 예측 (과제 필수) — `my_digit.png` "2" → 예측 2 (85.96%)
- [ ] 과제 1 제출: 캡처 4개(Colab 학습·저장 / 손글씨 이미지 / Windows 터미널 출력 / 결과 그래프) → 네이버 카페
- [ ] 팀과제 2: `task2_mobilenetv2_practice.ipynb` + 서술 항목(모델/입력/예상출력) → Windows `task2_predict_imagenet.py`

## 최종 확인 (2026-08-28)

- 과제 1 실행 파이프라인 **전 구간 성공**: Colab 학습·저장·재로드(정확도 0.9909) → Windows 이전 → 로컬 예측(본인 손글씨 인식)
- 환경: `C:\ir\windows` / Python 3.11.9 / TensorFlow 2.16.1 / Keras 3.15.1 / numpy 1.26.4
- 남은 리스크 없음. P1~P7 전부 해결.
