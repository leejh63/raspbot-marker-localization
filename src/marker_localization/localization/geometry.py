from __future__ import annotations

import math
from typing import Sequence, Tuple

import numpy as np


def norm_angle_360(angle_deg: float) -> float:
    angle_deg = angle_deg % 360.0
    if angle_deg < 0:
        angle_deg += 360.0
    return angle_deg


def norm_angle_180(angle_deg: float) -> float:
    while angle_deg > 180.0:
        angle_deg -= 360.0
    while angle_deg < -180.0:
        angle_deg += 360.0
    return angle_deg


def get_camera_yaw_from_marker(
    marker_angle_deg: float,
    marker_world_angle_deg: float = 90.0,
) -> Tuple[float, float]:
    """마커 이미지상 방향으로부터 로봇 yaw를 추정한다.

    원본 marker_utils.py의 공식과 동일하다.

        yaw = marker_world_angle + 90 - marker_angle

    반환:
    - yaw_360: 0~360도
    - yaw_180: -180~180도
    """
    yaw_360 = norm_angle_360(marker_world_angle_deg + 90.0 - marker_angle_deg)
    return yaw_360, norm_angle_180(yaw_360)


def pixel_to_world_mat(
    u: float,
    v: float,
    h_inv: Sequence[Sequence[float]],
) -> Tuple[float, float]:
    """top-view 픽셀 좌표를 로봇 기준 local 좌표로 투영한다."""
    h_inv_np = np.asarray(h_inv, dtype=np.float32)
    p_img = np.array([u, v, 1.0], dtype=np.float32)
    p_world_h = h_inv_np @ p_img

    xp, yp, w = float(p_world_h[0]), float(p_world_h[1]), float(p_world_h[2])
    if abs(w) < 1e-6:
        raise ValueError("Invalid homography projection: W is too small")

    return xp / w, yp / w


def compute_robot_world_from_marker_vec(
    marker_world: Tuple[float, float],
    robot_yaw_deg: float,
    rel_vec: Tuple[float, float],
) -> Tuple[float, float]:
    """마커 절대 좌표와 로봇 기준 마커 벡터로 로봇 절대 좌표를 계산한다.

    원본 프로젝트의 핵심 공식:

        marker_world = robot_world + R(yaw - 90) * rel_vec
        robot_world  = marker_world - R(yaw - 90) * rel_vec

    yaw 기준과 rel_vec 기준 사이의 90도 차이를 보정한다.
    """
    mx, my = marker_world
    x_rel, y_rel = rel_vec

    theta = math.radians(robot_yaw_deg - 90.0)
    c = math.cos(theta)
    s = math.sin(theta)

    wx = c * x_rel - s * y_rel
    wy = s * x_rel + c * y_rel

    return mx - wx, my - wy


def distance(x: float, y: float) -> float:
    return math.hypot(x, y)
