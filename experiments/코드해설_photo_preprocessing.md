# 코드 해설: `photo_preprocessing_test.py` 한 줄씩

> 이 해설은 실습 중 Claude(AI)와의 대화를 바탕으로 작성됨.
>
> **학습 예정**: `photo_preprocessing_test.py`(특히 `otsu_threshold()`)는 AI 도움으로
> 구현했고, 아직 스스로 처음부터 짤 수 있는 수준은 아니다. 이 문서를 나중에 다시 읽으며
> ① numpy 배열 연산(`bincount`, `dot`, `ravel`) ② 히스토그램/임계값 개념
> ③ Otsu 알고리즘의 "그룹 간 분산 최대화" 논리를 손으로 따라 계산해보는 것을 목표로 한다.
> 관련 배경(윈도우/리눅스 터미널 차이, 학습 절차)은 `Desktop\학습용\` 문서와 연결됨.

---

## 0. 먼저 알아야 할 것: 이미지 = 숫자 격자

흑백 이미지는 **숫자가 촘촘히 박힌 표**다. 각 칸(픽셀)에 밝기 값 하나
(0 = 완전 검정 ~ 255 = 완전 흰색). 1632×1568 사진이면 숫자가 약 256만 개.
`numpy` 배열로 다루면 이 표 전체를 한 번에 계산할 수 있다.

---

## 1. `otsu_threshold()` — 경계값 자동 계산

```python
def otsu_threshold(gray):
```
`gray` = 흑백 이미지의 숫자 표(numpy 배열). 반환값은 "경계값 숫자 하나".

```python
    hist = np.bincount(gray.ravel(), minlength=256).astype(float)
```
- `gray.ravel()` : 2차원 표를 1줄로 쭉 폄 (모든 픽셀의 일렬 목록)
- `np.bincount(..., minlength=256)` : **밝기별 픽셀 개수를 셈**. 길이 256짜리 목록 →
  `hist[0]`=밝기 0인 픽셀 수, … `hist[255]`까지. 이게 히스토그램(막대 높이들).
- `.astype(float)` : 나눗셈 대비해 정수 → 소수

```python
    total = gray.size
```
전체 픽셀 개수.

```python
    sum_all = np.dot(np.arange(256), hist)
```
- `np.arange(256)` = `[0, 1, ..., 255]`
- `np.dot(A, B)` = 짝지어 곱한 뒤 전부 더함 = `0*hist[0] + 1*hist[1] + ... + 255*hist[255]`
- 결과 = **모든 픽셀 밝기의 총합** (평균 계산에 사용)

```python
    w_b = 0.0      # 배경 그룹 픽셀 수 (누적)
    sum_b = 0.0    # 배경 그룹 밝기 합 (누적)
    best_var = 0.0 # 지금까지 최고 점수
    threshold = 0  # 그 점수를 낸 경계값
```

```python
    for i in range(256):
```
경계값 후보 `i`를 **0~255 전부 시도**. "경계값이 i라면 어떻게 갈리나"를 256번 계산.

```python
        w_b += hist[i]
        if w_b == 0:
            continue
```
"밝기 i 이하 = 배경". 밝기 `i`인 픽셀들(`hist[i]`개)을 배경 그룹에 편입.
배경이 아직 비어 있으면 스킵.

```python
        w_f = total - w_b
        if w_f == 0:
            break
```
나머지 = 숫자(전경) 그룹 픽셀 수. 숫자 그룹이 비면 종료.

```python
        sum_b += i * hist[i]
        mean_b = sum_b / w_b                 # 배경 평균 밝기
        mean_f = (sum_all - sum_b) / w_f     # 숫자 평균 밝기
```

```python
        between_var = w_b * w_f * (mean_b - mean_f) ** 2
```
**핵심 점수 공식.** (배경 개수) × (숫자 개수) × (두 평균 밝기 차이)²
- 두 그룹이 밝기로 멀수록 → 점수 ↑
- 두 그룹이 골고루 나뉠수록 → 점수 ↑
- 즉 "배경 무리와 숫자 무리가 가장 깔끔하게 갈리는 지점"에서 최대

```python
        if between_var > best_var:
            best_var = between_var
            threshold = i
```
역대 최고 점수면 기록 갱신.

```python
    return threshold
```
256번 다 돌고 가장 점수 높았던 경계값 반환. (이번 사진들: 158~166)

---

## 2. `preprocess_improved()` — 그 경계값으로 숫자 오려내기

```python
    image = Image.open(path).convert("L")
```
파일 열고 `"L"`(흑백) 모드로 변환.

```python
    pixels = np.asarray(image, dtype=np.uint8)
    if float(pixels.mean()) > 127.0:
        image = ImageOps.invert(image)
```
전체 평균 밝기가 127보다 크면(흰 배경 우세) **색 반전**:
흰 배경+검은 글씨 → 검은 배경+흰 글씨 (MNIST 방향). 사진은 평균 ~140이라 여기 걸림.

```python
    gray = np.asarray(image, dtype=np.uint8)
    thr = otsu_threshold(gray)
```
반전된 이미지로 1번 함수 호출 → **이 사진 전용 경계값**.

```python
    mask = image.point(lambda v: 255 if v > thr else 0)
```
- `.point(함수)` : 모든 픽셀에 함수를 하나씩 적용
- `lambda v: 255 if v > thr else 0` : "경계값보다 밝으면 흰(255), 아니면 검정(0)"
- 결과 `mask` = **숫자만 흰색인 흑백 도장** (위치 찾기용)

```python
    bbox = mask.getbbox()
```
흰 픽셀이 존재하는 **최소 사각형 좌표** (왼, 위, 오른, 아래) = 숫자를 감싸는 네모.

```python
    digit = image.crop(bbox)
```
그 네모대로 원본(반전된 회색조)을 잘라냄 → 여백 없이 숫자만.

```python
    digit_mask = mask.crop(bbox)
    digit = Image.composite(digit, Image.new("L", digit.size, 0), digit_mask)
```
`Image.composite(A, B, mask)` = mask 흰 곳은 A, 검은 곳은 B.
A=잘라낸 숫자, B=완전 검정, mask=숫자 도장 →
**숫자 획은 유지, 그 사이 남은 회색 배경 얼룩은 검정(0)으로 제거** (사진 잡음 제거).

```python
    digit.thumbnail((20, 20), Image.Resampling.LANCZOS)
```
숫자를 20×20 안에 들어가게 축소(비율 유지). `LANCZOS` = 축소 화질 좋은 방식.
(MNIST 숫자가 28칸 중 20칸 정도 차지하는 것을 흉내)

```python
    canvas = Image.new("L", (28, 28), color=0)
    canvas.paste(digit, ((28 - digit.width) // 2, (28 - digit.height) // 2))
```
28×28 검정 도화지에 축소한 숫자를 **정중앙 배치** (남는 공간을 2로 나눠 균등 여백).

```python
    normalized = np.asarray(canvas, dtype=np.float32) / 255.0
    return normalized.reshape(1, 28, 28, 1), normalized
```
- `/ 255.0` : 0~255 → **0~1** (모델이 학습한 형식)
- `.reshape(1, 28, 28, 1)` : 모델이 요구하는 4차원 모양 (사진1장, 세로28, 가로28, 채널1)

---

## 3. `preprocess_guide()`와의 차이 — 딱 한 줄

가이드 원본:
```python
    bbox = image.point(lambda v: 255 if v > 20 else 0).getbbox()   # 경계값 20 고정
```
개선 버전:
```python
    thr = otsu_threshold(gray)                          # 경계값 자동 계산
    mask = image.point(lambda v: 255 if v > thr else 0)
    bbox = mask.getbbox()
```
`20` → `thr` 교체 + 잡음 제거 한 단계 추가.
나머지(흑백변환·반전·축소·중앙배치·정규화)는 완전히 동일.
