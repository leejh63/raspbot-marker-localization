from __future__ import annotations

import math
from typing import Callable, Optional, Tuple

import cv2
import numpy as np

from marker_localization.types import MarkerDetection, Pose2D, TargetDelta


def draw_top_view_grid(
    image: np.ndarray,
    cols: int = 8,
    rows: int = 8,
    color=(200, 200, 200),
) -> np.ndarray:
    """top-view 이미지 위에 블록/격자 오버레이를 그린다."""
    out = image.copy()
    h, w = out.shape[:2]

    for c in range(1, cols):
        x = int(w * c / cols)
        cv2.line(out, (x, 0), (x, h), color, 1)

    for r in range(1, rows):
        y = int(h * r / rows)
        cv2.line(out, (0, y), (w, y), color, 1)

    cv2.putText(
        out,
        f"top-view grid: {cols}x{rows}",
        (15, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 0, 255),
        2,
    )
    return out


def draw_marker_detection(image: np.ndarray, marker: MarkerDetection) -> np.ndarray:
    """마커 contour, corner, reference point, 방향 화살표, id를 top-view에 표시한다."""
    out = image.copy()

    cv2.drawContours(out, [marker.outer_corners.astype(int)], -1, (0, 255, 255), 2)
    cv2.drawContours(out, [marker.inner_corners.astype(int)], -1, (0, 0, 255), 2)
    for p in marker.ordered_corners:
        cv2.circle(out, tuple(p.astype(int)), 4, (0, 255, 0), -1)

    cx, cy = marker.reference_px
    cv2.circle(out, (int(cx), int(cy)), 6, (255, 0, 0), -1)

    # yaw 방향 화살표
    angle_rad = math.radians(marker.angle_deg)
    end = (
        int(cx + math.cos(angle_rad) * 80),
        int(cy - math.sin(angle_rad) * 80),
    )
    cv2.arrowedLine(out, (int(cx), int(cy)), end, (255, 0, 0), 3, tipLength=0.25)

    cv2.putText(
        out,
        f"id={marker.marker_id}, angle={marker.angle_deg:.1f}",
        (int(cx) + 10, int(cy) - 10),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
        (0, 0, 255),
        2,
    )
    return out


def create_world_canvas(
    world_min: float = -4.0,
    world_max: float = 4.0,
    img_size: int = 700,
):
    """월드 좌표계 시각화용 빈 캔버스와 world_to_img 함수를 만든다."""
    img = np.ones((img_size, img_size, 3), dtype=np.uint8) * 255

    def world_to_img(x: float, y: float) -> Tuple[int, int]:
        nx = (x - world_min) / (world_max - world_min)
        ny = (y - world_min) / (world_max - world_min)
        u = int(nx * img_size)
        v = int((1.0 - ny) * img_size)
        return u, v

    for t in range(int(world_min), int(world_max) + 1):
        u1, v1 = world_to_img(t, world_min)
        u2, v2 = world_to_img(t, world_max)
        cv2.line(img, (u1, v1), (u2, v2), (225, 225, 225), 1)

        u3, v3 = world_to_img(world_min, t)
        u4, v4 = world_to_img(world_max, t)
        cv2.line(img, (u3, v3), (u4, v4), (225, 225, 225), 1)

    # x/y axis
    u1, v1 = world_to_img(0, world_min)
    u2, v2 = world_to_img(0, world_max)
    cv2.line(img, (u1, v1), (u2, v2), (0, 0, 0), 2)

    u3, v3 = world_to_img(world_min, 0)
    u4, v4 = world_to_img(world_max, 0)
    cv2.line(img, (u3, v3), (u4, v4), (0, 0, 0), 2)

    return img, world_to_img


def draw_pose_world(
    marker_world: Optional[Tuple[float, float]],
    pose: Optional[Pose2D],
    target: Optional[Tuple[float, float]],
    delta: Optional[TargetDelta],
) -> np.ndarray:
    """마커, 로봇 pose, 목표 지점을 월드 좌표계에 표시한다."""
    canvas, world_to_img = create_world_canvas()

    if marker_world is not None:
        mx, my = marker_world
        mu, mv = world_to_img(mx, my)
        cv2.circle(canvas, (mu, mv), 8, (0, 0, 0), -1)
        cv2.putText(
            canvas,
            f"Marker({mx:.2f},{my:.2f})",
            (mu + 10, mv - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (0, 0, 0),
            1,
        )

    if target is not None:
        tx, ty = target
        tu, tv = world_to_img(tx, ty)
        cv2.drawMarker(canvas, (tu, tv), (0, 140, 255), cv2.MARKER_CROSS, 20, 2)
        cv2.putText(
            canvas,
            f"Target({tx:.2f},{ty:.2f})",
            (tu + 10, tv + 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (0, 140, 255),
            1,
        )

    if pose is not None:
        ru, rv = world_to_img(pose.x, pose.y)
        cv2.circle(canvas, (ru, rv), 8, (0, 0, 255), -1)

        yaw_rad = math.radians(pose.yaw_deg)
        arrow_len = 0.7
        ex = pose.x + math.cos(yaw_rad) * arrow_len
        ey = pose.y + math.sin(yaw_rad) * arrow_len
        eu, ev = world_to_img(ex, ey)
        cv2.arrowedLine(canvas, (ru, rv), (eu, ev), (0, 0, 255), 2, tipLength=0.3)

        cv2.putText(
            canvas,
            f"Robot({pose.x:.2f},{pose.y:.2f},{pose.yaw_deg:.1f}deg)",
            (ru + 10, rv + 15),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (0, 0, 255),
            1,
        )

    if delta is not None:
        cv2.putText(
            canvas,
            f"dx={delta.dx:.3f}, dy={delta.dy:.3f}, dist={delta.distance:.3f}",
            (15, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (40, 40, 40),
            2,
        )

    return canvas
