from __future__ import annotations

from typing import Dict, Optional, Sequence, Tuple

from marker_localization.config import DEFAULT_H_INV, DEFAULT_MARKER_WORLD_ANGLE_DEG
from marker_localization.types import MarkerDetection, Pose2D
from marker_localization.vision.marker_decoder import (
    get_marker_angle_and_side_center,
    get_ordered_corners_by_angle_center,
    warp_and_decode,
)
from marker_localization.vision.marker_detector import find_biggest_marker
from marker_localization.localization.geometry import (
    compute_robot_world_from_marker_vec,
    get_camera_yaw_from_marker,
    pixel_to_world_mat,
)


def detect_marker(top_view_bgr) -> Optional[MarkerDetection]:
    """top-view 이미지에서 하나의 마커를 검출하고 decode한다."""
    pair = find_biggest_marker(top_view_bgr)
    if pair is None:
        return None

    angle, reference = get_marker_angle_and_side_center(pair.outer, pair.inner)
    ordered = get_ordered_corners_by_angle_center(pair.outer, angle, reference)
    crop, code, marker_id = warp_and_decode(pair.gray, pair.binary, ordered)

    return MarkerDetection(
        marker_id=marker_id,
        angle_deg=angle,
        reference_px=(float(reference[0]), float(reference[1])),
        outer_corners=pair.outer,
        inner_corners=pair.inner,
        ordered_corners=ordered,
        crop=crop,
        code_grid=code,
        rect_area=pair.rect_area,
    )


def estimate_robot_pose(
    marker: MarkerDetection,
    marker_map: Dict[int, Tuple[float, float]],
    *,
    h_inv: Sequence[Sequence[float]] = DEFAULT_H_INV,
    marker_world_angle_deg: float = DEFAULT_MARKER_WORLD_ANGLE_DEG,
) -> Tuple[Optional[Tuple[float, float]], Optional[Pose2D], Optional[Tuple[float, float]]]:
    """마커 검출 결과로부터 로봇 pose를 계산한다.

    반환:
    - marker_world: marker id에 해당하는 절대 좌표. map에 없으면 None
    - pose: 로봇 절대 좌표와 yaw. marker_world가 없으면 None
    - rel_vec: 로봇 기준 마커 reference point 벡터
    """
    marker_world = marker_map.get(marker.marker_id)
    u, v = marker.reference_px
    rel_vec = pixel_to_world_mat(u, v, h_inv)

    if marker_world is None:
        return None, None, rel_vec

    yaw_360, _ = get_camera_yaw_from_marker(
        marker.angle_deg,
        marker_world_angle_deg=marker_world_angle_deg,
    )

    rx, ry = compute_robot_world_from_marker_vec(
        marker_world=marker_world,
        robot_yaw_deg=yaw_360,
        rel_vec=rel_vec,
    )
    return marker_world, Pose2D(rx, ry, yaw_360), rel_vec
