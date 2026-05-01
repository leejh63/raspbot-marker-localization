from __future__ import annotations

from pathlib import Path
from typing import Optional, Tuple

import cv2
import numpy as np


def load_remap_pair(path: Path) -> Tuple[np.ndarray, np.ndarray]:
    """calib.dat처럼 np.save가 연속으로 저장된 remap pair를 읽는다.

    원본 코드에서는 다음처럼 읽었다.

        f = open('/home/.../calib.dat', 'rb')
        map1 = np.load(f)
        map2 = np.load(f)

    이 함수는 그 흐름을 프로젝트 상대 경로 기반으로 감싼 것이다.
    """
    path = Path(path)
    with path.open("rb") as f:
        map1 = np.load(f)
        map2 = np.load(f)
    return map1, map2


def remap_image(image: np.ndarray, mapx: np.ndarray, mapy: np.ndarray) -> np.ndarray:
    """OpenCV remap을 적용한다."""
    return cv2.remap(image, mapx, mapy, cv2.INTER_LINEAR)


def undistort_with_calibration(image: np.ndarray, calib_file: Optional[Path]) -> np.ndarray:
    """카메라 왜곡 보정을 적용한다.

    calib_file이 없으면 입력 이미지를 그대로 반환한다. 이미 top-view 또는 보정된
    이미지를 넣는 경우를 고려한 처리다.
    """
    if calib_file is None:
        return image.copy()

    calib_file = Path(calib_file)
    if not calib_file.exists():
        return image.copy()

    map1, map2 = load_remap_pair(calib_file)
    return remap_image(image, map1, map2)


def load_topview_maps(mapx_file: Path, mapy_file: Path) -> Tuple[np.ndarray, np.ndarray]:
    """Top-view 변환용 remap mapx/mapy를 읽는다."""
    return np.load(Path(mapx_file)), np.load(Path(mapy_file))


def apply_topview_remap(
    image: np.ndarray,
    mapx_file: Optional[Path],
    mapy_file: Optional[Path],
) -> np.ndarray:
    """원본 videos.py에서 쓰던 top-view remap을 적용한다.

    mapx/mapy가 없으면 입력 이미지를 그대로 반환한다.
    """
    if mapx_file is None or mapy_file is None:
        return image.copy()

    mapx_file = Path(mapx_file)
    mapy_file = Path(mapy_file)
    if not mapx_file.exists() or not mapy_file.exists():
        return image.copy()

    mapx, mapy = load_topview_maps(mapx_file, mapy_file)
    return remap_image(image, mapx, mapy)
