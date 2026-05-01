from __future__ import annotations

import math
from typing import Tuple

from marker_localization.localization.geometry import norm_angle_180, norm_angle_360
from marker_localization.types import Pose2D, TargetDelta


def compute_target_delta(pose: Pose2D, target: Tuple[float, float]) -> TargetDelta:
    """현재 pose에서 목표 좌표까지의 dx/dy/distance를 계산한다."""
    tx, ty = target
    dx = tx - pose.x
    dy = ty - pose.y
    return TargetDelta(dx=dx, dy=dy, distance=math.hypot(dx, dy))


def compute_desired_yaw_deg(pose: Pose2D, target: Tuple[float, float]) -> float:
    """목표 좌표를 바라보기 위한 yaw를 계산한다.

    좌표계 기준:
    - +X 방향: 0도
    - +Y 방향: 90도
    """
    tx, ty = target
    dx = tx - pose.x
    dy = ty - pose.y
    return norm_angle_360(math.degrees(math.atan2(dy, dx)))


def compute_yaw_error_deg(pose: Pose2D, target: Tuple[float, float]) -> float:
    """현재 yaw와 목표 yaw의 차이를 -180~180도로 반환한다."""
    desired = compute_desired_yaw_deg(pose, target)
    return norm_angle_180(desired - pose.yaw_deg)
