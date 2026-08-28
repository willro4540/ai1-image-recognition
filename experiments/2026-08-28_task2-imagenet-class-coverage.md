# 실험: 사전 학습 모델은 "학습된 클래스" 안에서만 인식한다 (과제 2)

> 이 문서는 실습 중 Claude(AI)와의 대화를 바탕으로 작성됨. 실행·결과는 실제 수행값이며,
> 분석·문서화에 AI를 활용함.

- **날짜**: 2026-08-28
- **모델**: MobileNetV2 (ImageNet 사전 학습). Colab에서 저장한 `MobileNetV2_ImageNet.keras`를
  Windows(`C:\ir\windows`, TF 2.16.1)로 옮겨 `task2_predict_imagenet.py`로 추론.
- **질문**: 같은 "사과"라도 색이 다르면 어떻게 분류될까?

## 배경

MobileNetV2는 직접 학습하지 않고 ImageNet 1000개 클래스로 미리 학습된 가중치를 불러와
추론만 한다. **ImageNet의 사과 관련 클래스는 `Granny Smith`(청사과 품종) 하나뿐이다.**
(빨간 사과, "apple" 통칭 클래스는 없음)

전처리: 이미지를 224×224로 조정 → `preprocess_input`으로 픽셀을 -1~1로 스케일 → 모델 입력.
(과제 1 MNIST의 28×28×1 / `/255` 와 완전히 다름)

## 결과

| 입력 이미지 | 1위 예측 | 확신도 | 2~5위 |
|---|---|---|---|
| 바나나 (예제) | `banana` | 96.75% | slug, lemon, hook, flatworm (전부 <0.1%) |
| **빨간 사과** | `pomegranate` (석류) | **38.40%** | hip 6.8%, Granny_Smith 5.5%, strawberry 4.8%, buckeye 2.6% |
| **청사과** | `Granny_Smith` | **92.77%** | orange 0.18%, lemon 0.15%, bell_pepper 0.12%, banana 0.09% |

## 해석

- **청사과**: ImageNet의 `Granny Smith` 클래스와 정확히 일치 → 92.77%로 확실하게 맞힘.
  2위(orange)와 격차가 500배 이상.
- **빨간 사과**: 대응하는 클래스가 없음 → 모델이 아는 것 중 "빨갛고 둥근 과일"
  (석류, 들장미 열매, 딸기)로 확률이 분산됨. 1위 확신도도 38%에 그쳐 **모델 자체가 불확실**.
- **바나나**: 클래스가 명확히 존재 → 96.75%.

## 소견

사전 학습 모델은 **학습된 분류 체계 안에서만** 인식한다. 대상이 그 체계에 포함되면
(청사과, 바나나) 높은 확신도로 맞히지만, 포함되지 않으면(빨간 사과) 비슷한 클래스로
분산되고 확신도가 떨어진다. "무엇을 인식할 수 있는가"는 모델의 성능이 아니라
**학습 데이터의 클래스 목록**이 결정한다. (가이드 4.5: "MobileNetV2는 ImageNet의
1,000개 분류 항목만 출력한다"의 구체적 사례)

## 재현 방법

```powershell
cd C:\ir\windows
.\.venv\Scripts\python.exe task2_predict_imagenet.py "이미지경로.jpg"
# 결과 그래프를 파일로 저장하려면:
.\.venv\Scripts\python.exe task2_predict_imagenet.py "이미지경로.jpg" --save-result "결과.png"
```

입력 이미지(사과 사진)는 웹 스톡 이미지라 저장소에 포함하지 않음 — 과제 제출 시 별도 첨부.
