from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

import numpy as np


Point2D = Tuple[float, float]


@dataclass(frozen=True)
class MarkerDetection:
    """Top-view 이미지에서 검출한 단일 마커 정보.

    reference_px는 실제 마커 중심점이 아니라, 원본 로직에서 사용한
    마커 방향 기준 side/reference point입니다.
    """

    marker_id: int
    angle_deg: float
    reference_px: Point2D
    outer_corners: np.ndarray
    inner_corners: np.ndarray
    ordered_corners: np.ndarray
    crop: np.ndarray
    code_grid: np.ndarray
    rect_area: float


@dataclass(frozen=True)
class Pose2D:
    """월드 좌표계 기준 로봇 위치와 방향."""

    x: float
    y: float
    yaw_deg: float


@dataclass(frozen=True)
class TargetDelta:
    """현재 위치에서 목표 위치까지의 차이."""

    dx: float
    dy: float
    distance: float


@dataclass(frozen=True)
class MotorCommand:
    """ML 모델이 추천한 open-loop 이동 명령."""

    left_power: float
    right_power: float
    duration_sec: float
    heuristic_distance_estimate: float
    raw_left_power: float
    raw_right_power: float
    raw_duration_sec: float
