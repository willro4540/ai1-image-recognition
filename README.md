# ai1-image-recognition

『모두의 딥러닝』 16장(이미지 인식, CNN) 실습 과제 기록.

- Colab에서 CNN/사전학습 모델을 학습·저장 → Windows 로컬 Python으로 옮겨 실행하는 과정
- 실습 중 겪은 환경 구성 문제와 그 원인·해결을 기록해 나중에 심화 분석

## 구성

| 폴더/파일 | 내용 |
|---|---|
| `troubleshooting/` | 날짜별 트러블슈팅 로그 (증상 → 원인 → 해결 → 심화 분석 포인트) |
| `experiments/` | 손글씨 사진 입력 실험 + 전처리 개선(Otsu) + 코드 한 줄씩 해설 (학습 예정 표시) |

## 진행 상황

| 항목 | 상태 |
|---|---|
| 과제 1 — Colab: MNIST CNN 학습·저장·재로드 | ✅ 완료 (예제 이미지 예측까지) |
| 과제 1 — 본인 손글씨 PNG 예측 | ⬜ 예정 |
| 과제 1 — Windows 환경 구성 | ✅ 완료 (`C:\ir\windows`, TF 2.16.1 / Py 3.11) |
| 과제 1 — Windows에서 예측 | ⬜ 예정 |
| 과제 2 — 팀 사전학습 모델 분류 | ⬜ 예정 |

## 관련 기록

- 학습 절차 상세: `Desktop\학습용\python_study_procedure.md` (238단계~)

## 작성 방식 명시

이 저장소의 문서(`troubleshooting/`, `experiments/`의 `.md`)와 분석 스크립트
(`experiments/photo_preprocessing_test.py`)는 **실습을 진행하면서 Claude(AI)와 나눈
대화를 바탕으로 작성**되었다.

- 실습 수행·명령 실행·이미지 촬영·결과 확인은 직접 한 것이며, 결과 수치는 실제 실행값이다.
- 문제 원인 분석, 문서 정리, Otsu 이진화 스크립트 구현에는 AI를 활용했다.
