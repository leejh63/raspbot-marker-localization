from __future__ import annotations

import math
from typing import Tuple

import cv2
import numpy as np


def get_marker_angle_and_side_center(
    outer_contour: np.ndarray,
    inner_contour: np.ndarray,
) -> Tuple[float, np.ndarray]:
    """마커 방향 각도와 오른쪽 변 중심점을 계산한다.

    각도 기준:
    - 오른쪽: 0도
    - 위: 90도
    - 왼쪽: 180도
    - 아래: 270도

    inner contour가 outer contour 기준 어느 쪽에 붙어 있는지를 이용해
    마커의 앞 방향을 결정한다.
    """
    pts = np.asarray(outer_contour, dtype=float).reshape(-1, 2)
    if pts.shape[0] != 4:
        rect = cv2.minAreaRect(pts.astype(np.float32))
        pts = cv2.boxPoints(rect)

    edges = []
    for i in range(4):
        j = (i + 1) % 4
        edges.append(pts[j] - pts[i])
    edges = np.asarray(edges)

    lens2 = np.sum(edges**2, axis=1)
    i_long = int(np.argmax(lens2))

    v1 = edges[i_long]
    v2 = edges[(i_long + 2) % 4]
    if np.dot(v1, v2) < 0:
        v2 = -v2

    v_long = v1 + v2

    c_out = pts.mean(axis=0)
    c_in = np.asarray(inner_contour, dtype=float).reshape(-1, 2).mean(axis=0)
    to_inner = c_in - c_out

    if np.dot(v_long, to_inner) < 0:
        v_long = -v_long

    dx, dy = float(v_long[0]), float(v_long[1])
    angle = math.degrees(math.atan2(-dy, dx))
    angle = (angle + 360.0) % 360.0

    norm_f = np.linalg.norm(v_long)
    v_fwd = np.array([0.0, -1.0]) if norm_f < 1e-6 else v_long / norm_f

    # 이미지 좌표계에서 앞 방향 기준 오른쪽 벡터.
    v_right = np.array([-v_fwd[1], v_fwd[0]])
    norm_r = np.linalg.norm(v_right)
    v_right = np.array([1.0, 0.0]) if norm_r < 1e-6 else v_right / norm_r

    best_mid = None
    best_proj = -1e9
    for i in range(4):
        j = (i + 1) % 4
        mid = 0.5 * (pts[i] + pts[j])
        rel = mid - c_out
        proj = np.dot(rel, v_right)
        if proj > best_proj:
            best_proj = proj
            best_mid = mid

    return angle, best_mid


def get_ordered_corners_by_angle_center(
    outer: np.ndarray,
    angle_deg: float,
    center_pt: np.ndarray,
) -> np.ndarray:
    """마커 warp를 위해 outer corner 순서를 안정적으로 정렬한다.

    원본 노트북/marker_utils.py의 방식:
    - center_pt 기준 상대 좌표로 변환
    - 마커 앞 방향이 +Y가 되도록 회전
    - 위/아래, 왼쪽/오른쪽으로 corner 분류
    """
    pts = np.asarray(outer, dtype=np.float32).reshape(4, 2)

    cx, cy = float(center_pt[0]), float(center_pt[1])
    rel = np.empty_like(pts, dtype=np.float32)
    for i, (u, v) in enumerate(pts):
        x = u - cx
        y = -(v - cy)
        rel[i] = [x, y]

    phi = math.radians(90.0 - angle_deg)
    cos_p = math.cos(phi)
    sin_p = math.sin(phi)

    rel_rot = np.empty_like(rel, dtype=np.float32)
    for i, (x, y) in enumerate(rel):
        xr = cos_p * x - sin_p * y
        yr = sin_p * x + cos_p * y
        rel_rot[i] = [xr, yr]

    idx_sorted_by_y = np.argsort(rel_rot[:, 1])
    bottom_idx = idx_sorted_by_y[:2]
    top_idx = idx_sorted_by_y[2:]

    bottom_pts = rel_rot[bottom_idx]
    top_pts = rel_rot[top_idx]

    top_order = np.argsort(top_pts[:, 0])
    bottom_order = np.argsort(bottom_pts[:, 0])

    top_left_idx = top_idx[top_order[0]]
    top_right_idx = top_idx[top_order[1]]
    bottom_left_idx = bottom_idx[bottom_order[0]]
    bottom_right_idx = bottom_idx[bottom_order[1]]

    # 원본 코드 기준 순서: 위-오, 위-왼, 아래-왼, 아래-오
    return np.array(
        [
            pts[top_right_idx],
            pts[top_left_idx],
            pts[bottom_left_idx],
            pts[bottom_right_idx],
        ],
        dtype=np.float32,
    )


def warp_and_decode(
    gray: np.ndarray,
    binary: np.ndarray,
    corners: np.ndarray,
) -> Tuple[np.ndarray, np.ndarray, int]:
    """마커를 정면으로 펴서 4x6 code grid와 marker id를 얻는다."""
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_COUNT, 40, 0.001)
    refined = cv2.cornerSubPix(gray, corners.copy(), (5, 5), (-1, -1), criteria)

    # 원본 코드와 동일한 3x4 비율 기준 warp.
    dst_rect = np.array([[3, 0], [0, 0], [0, 4], [3, 4]], np.float32)
    dst_points = (dst_rect * 10.0).astype(np.float32)
    src_points = refined.astype(np.float32)

    mat, _ = cv2.findHomography(src_points, dst_points, cv2.RANSAC)
    crop = cv2.warpPerspective(binary, mat, (60, 40))

    small = cv2.resize(crop, (6, 4))
    code = small < 128

    bits = (~code[:, 4:]).flatten()
    weights = np.array([128, 64, 32, 16, 8, 4, 2, 1], dtype=np.int32)
    value = int((bits * weights).sum())
    return crop, code, value


def draw_code_cells_on_crop(crop: np.ndarray, code: np.ndarray) -> np.ndarray:
    """디코딩된 4x6 cell 영역을 시각화한다."""
    h, w = crop.shape[:2]
    rows, cols = code.shape

    if len(crop.shape) == 2:
        out = cv2.cvtColor(crop, cv2.COLOR_GRAY2BGR)
    else:
        out = crop.copy()

    cell_w = w / cols
    cell_h = h / rows

    for r in range(rows):
        for c in range(cols):
            x0 = int(c * cell_w)
            y0 = int(r * cell_h)
            x1 = int((c + 1) * cell_w)
            y1 = int((r + 1) * cell_h)
            cv2.rectangle(out, (x0, y0), (x1, y1), (255, 255, 255), 1)
            if c >= 4:
                cv2.rectangle(out, (x0, y0), (x1, y1), (0, 255, 255), 2)

    return out
