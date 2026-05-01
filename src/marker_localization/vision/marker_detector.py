from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple

import cv2
import numpy as np


@dataclass(frozen=True)
class MarkerContourPair:
    """마커의 외부 사각형과 내부 사각형 contour 쌍."""

    outer: np.ndarray
    inner: np.ndarray
    binary: np.ndarray
    gray: np.ndarray
    rect_area: float


def find_biggest_marker(
    img_bgr: np.ndarray,
    *,
    min_contour_area: float = 100.0,
    max_arc_len: float = 500.0,
    min_arc_len: float = 10.0,
    max_aspect: float = 1.7,
    rect_area_min: float = 1500.0,
    rect_area_max: float = 5000.0,
    min_center_y: Optional[float] = 270.0,
) -> Optional[MarkerContourPair]:
    """이미지에서 가장 큰 사각형 마커 후보를 찾는다.

    원본 marker_utils.py의 find_biggest_marker()를 import-safe 형태로 정리했다.

    처리 흐름:
    1. BGR → gray
    2. adaptive threshold
    3. morphology open으로 작은 잡티 제거
    4. RETR_TREE contour hierarchy에서 outer/inner 사각형 쌍 찾기
    5. 가장 큰 outer contour 선택

    min_center_y는 원본 코드의 "화면 위쪽 오검출 제거" 필터다.
    샘플/카메라 각도에 따라 필요 없으면 None으로 끌 수 있다.
    """
    if img_bgr is None:
        return None

    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

    binary = cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_MEAN_C,
        cv2.THRESH_BINARY,
        41,
        8.0,
    )

    kernel = np.ones((3, 3), np.uint8)
    binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations=1)

    contours, hierarchy = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    if hierarchy is None or len(contours) == 0:
        return None

    contours = list(contours)
    hierarchy = hierarchy[0]

    filtered_indices = []
    for index, contour in enumerate(contours):
        area = cv2.contourArea(contour)
        if area < min_contour_area:
            continue

        arc_len = cv2.arcLength(contour, True)
        if arc_len > max_arc_len or arc_len < min_arc_len:
            continue

        epsilon = arc_len * 0.05
        contours[index] = cv2.approxPolyDP(contour, epsilon, True)
        filtered_indices.append(index)

    best_outer = None
    best_inner = None
    best_area = 0.0
    best_rect_area = 0.0

    for i in filtered_indices:
        contour = contours[i]
        if len(contour) != 4:
            continue

        rect = cv2.minAreaRect(contour)
        width, height = rect[1]
        if width < 1 or height < 1:
            continue

        aspect = max(width, height) / min(width, height)
        if aspect > max_aspect:
            continue

        rect_area = width * height
        if not (rect_area_min <= rect_area <= rect_area_max):
            continue

        pts = contour.reshape(4, 2).astype(np.float32)
        center_x, center_y = pts.mean(axis=0)
        if min_center_y is not None and center_y < min_center_y:
            continue

        child_index = hierarchy[i][2]
        if child_index == -1:
            continue

        inner = contours[child_index]
        if len(inner) != 4:
            continue

        area = cv2.contourArea(contour)
        if area > best_area:
            best_area = area
            best_outer = pts
            best_inner = inner.reshape(4, 2).astype(np.float32)
            best_rect_area = float(rect_area)

    if best_outer is None or best_inner is None:
        return None

    return MarkerContourPair(
        outer=best_outer,
        inner=best_inner,
        binary=binary,
        gray=gray,
        rect_area=best_rect_area,
    )
