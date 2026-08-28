"""손글씨 '사진'(카메라 촬영) 입력 실험.

가이드의 task1_predict_digit.py 전처리는 '깨끗한 디지털 이미지(그림판 등)'를 가정한다.
카메라로 찍은 사진은 배경이 완전한 검정/흰색이 아니라 회색이라, 가이드 전처리의
`point(lambda v: 255 if v > 20 else 0)` 이진화가 배경까지 전경으로 잡아버려
숫자 크롭(중앙 정렬·크기 정규화)이 통째로 실패한다.

이 스크립트는:
  1) 가이드 방식 전처리 (고정 임계값 20)
  2) 개선 방식 전처리 (Otsu 자동 임계값 + 여백 패딩)
두 가지로 각각 예측하고, 28x28 전처리 결과를 나란히 저장해 비교한다.

사용법:
  python photo_preprocessing_test.py 이미지경로 [이미지경로 ...]
"""

import sys
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
from PIL import Image, ImageOps

MODEL_PATH = Path(r"C:\ir\windows\models\MNIST_CNN.keras")


def otsu_threshold(gray: np.ndarray) -> int:
    """이미지 히스토그램에서 전경/배경을 가장 잘 가르는 임계값을 자동 계산."""
    hist = np.bincount(gray.ravel(), minlength=256).astype(float)
    total = gray.size
    sum_all = np.dot(np.arange(256), hist)
    w_b = 0.0
    sum_b = 0.0
    best_var = 0.0
    threshold = 0
    for i in range(256):
        w_b += hist[i]
        if w_b == 0:
            continue
        w_f = total - w_b
        if w_f == 0:
            break
        sum_b += i * hist[i]
        mean_b = sum_b / w_b
        mean_f = (sum_all - sum_b) / w_f
        between_var = w_b * w_f * (mean_b - mean_f) ** 2
        if between_var > best_var:
            best_var = between_var
            threshold = i
    return threshold


def to_mnist(canvas28: Image.Image) -> tuple[np.ndarray, np.ndarray]:
    normalized = np.asarray(canvas28, dtype=np.float32) / 255.0
    return normalized.reshape(1, 28, 28, 1), normalized


def preprocess_guide(path: Path) -> tuple[np.ndarray, np.ndarray]:
    """가이드 task1_predict_digit.py 와 동일한 전처리 (고정 임계값 20)."""
    image = Image.open(path).convert("L")
    pixels = np.asarray(image, dtype=np.uint8)
    if float(pixels.mean()) > 127.0:
        image = ImageOps.invert(image)
    bbox = image.point(lambda v: 255 if v > 20 else 0).getbbox()
    if bbox is None:
        raise ValueError("획을 찾지 못함")
    digit = image.crop(bbox)
    digit.thumbnail((20, 20), Image.Resampling.LANCZOS)
    canvas = Image.new("L", (28, 28), color=0)
    canvas.paste(digit, ((28 - digit.width) // 2, (28 - digit.height) // 2))
    return to_mnist(canvas)


def preprocess_improved(path: Path) -> tuple[np.ndarray, np.ndarray]:
    """사진용 개선 전처리: Otsu 자동 임계값으로 이진화 후 크롭."""
    image = Image.open(path).convert("L")
    pixels = np.asarray(image, dtype=np.uint8)
    if float(pixels.mean()) > 127.0:
        image = ImageOps.invert(image)          # 배경 어둡게, 숫자 밝게 (MNIST 방향)
    gray = np.asarray(image, dtype=np.uint8)

    thr = otsu_threshold(gray)
    mask = image.point(lambda v: 255 if v > thr else 0)  # 숫자만 흰색인 흑백 마스크
    bbox = mask.getbbox()
    if bbox is None:
        raise ValueError("획을 찾지 못함")

    digit = image.crop(bbox)
    # 사진 잡음 제거를 위해 마스크로 한 번 걸러줌 (배경 회색 → 0)
    digit_mask = mask.crop(bbox)
    digit = Image.composite(digit, Image.new("L", digit.size, 0), digit_mask)

    digit.thumbnail((20, 20), Image.Resampling.LANCZOS)
    canvas = Image.new("L", (28, 28), color=0)
    canvas.paste(digit, ((28 - digit.width) // 2, (28 - digit.height) // 2))
    return to_mnist(canvas)


def top3(probs: np.ndarray) -> str:
    idx = np.argsort(probs)[::-1][:3]
    return ", ".join(f"{i}:{probs[i] * 100:.1f}%" for i in idx)


def main() -> None:
    paths = [Path(p) for p in sys.argv[1:]]
    if not paths:
        print(__doc__)
        return

    model = tf.keras.models.load_model(MODEL_PATH)
    n = len(paths)
    fig, axes = plt.subplots(n, 2, figsize=(4, 2 * n))
    if n == 1:
        axes = axes.reshape(1, 2)

    for row, path in enumerate(paths):
        gi, gimg = preprocess_guide(path)
        ii, iimg = preprocess_improved(path)
        gp = model.predict(gi, verbose=0)[0]
        ip = model.predict(ii, verbose=0)[0]

        print(f"\n[{path.name}]")
        print(f"  가이드 전처리 → 예측 {int(np.argmax(gp))}  ({top3(gp)})")
        print(f"  개선 전처리   → 예측 {int(np.argmax(ip))}  ({top3(ip)})")

        axes[row, 0].imshow(gimg, cmap="gray", vmin=0, vmax=1)
        axes[row, 0].set_title(f"guide → {int(np.argmax(gp))}", fontsize=9)
        axes[row, 0].axis("off")
        axes[row, 1].imshow(iimg, cmap="gray", vmin=0, vmax=1)
        axes[row, 1].set_title(f"improved → {int(np.argmax(ip))}", fontsize=9)
        axes[row, 1].axis("off")

    fig.tight_layout()
    out = Path(__file__).parent / "photo_preprocessing_compare.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    print(f"\n비교 이미지 저장: {out}")


if __name__ == "__main__":
    main()
