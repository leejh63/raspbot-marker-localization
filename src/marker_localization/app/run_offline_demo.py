from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Tuple

import cv2
import numpy as np

from marker_localization.config import (
    DEFAULT_CALIB_FILE,
    DEFAULT_GRID_COLS,
    DEFAULT_GRID_ROWS,
    DEFAULT_MARKER_MAP,
    DEFAULT_MOTOR_MODEL,
    DEFAULT_TOPVIEW_MAPX,
    DEFAULT_TOPVIEW_MAPY,
    OUTPUT_DIR,
)
from marker_localization.localization.pose_estimator import detect_marker, estimate_robot_pose
from marker_localization.navigation.motor_model import MotorRegressionModel
from marker_localization.navigation.target_planner import (
    compute_desired_yaw_deg,
    compute_target_delta,
    compute_yaw_error_deg,
)
from marker_localization.vision.calibration import (
    apply_topview_remap,
    undistort_with_calibration,
)
from marker_localization.vision.marker_decoder import draw_code_cells_on_crop
from marker_localization.vision.visualization import (
    draw_marker_detection,
    draw_pose_world,
    draw_top_view_grid,
)


def _parse_target(text: str) -> Tuple[float, float]:
    if "," in text:
        x_str, y_str = text.split(",", 1)
    else:
        x_str, y_str = text.split()
    return float(x_str), float(y_str)


def _save_image(path: Path, image) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(path), image)
    return str(path)


def run_demo(
    image_path: Path,
    target: Tuple[float, float],
    *,
    input_stage: str,
    output_dir: Path,
    use_calibration: bool = True,
    use_topview_remap: bool = True,
):
    """오프라인 이미지 1장으로 전체 파이프라인을 실행한다."""
    output_dir.mkdir(parents=True, exist_ok=True)

    image = cv2.imread(str(image_path))
    if image is None:
        raise FileNotFoundError(f"Cannot read image: {image_path}")

    saved = {}
    saved["00_input"] = _save_image(output_dir / "00_input.jpg", image)

    if input_stage == "raw":
        undistorted = undistort_with_calibration(
            image,
            DEFAULT_CALIB_FILE if use_calibration else None,
        )
        top_view = apply_topview_remap(
            undistorted,
            DEFAULT_TOPVIEW_MAPX if use_topview_remap else None,
            DEFAULT_TOPVIEW_MAPY if use_topview_remap else None,
        )
    elif input_stage == "undistorted":
        undistorted = image.copy()
        top_view = apply_topview_remap(
            undistorted,
            DEFAULT_TOPVIEW_MAPX if use_topview_remap else None,
            DEFAULT_TOPVIEW_MAPY if use_topview_remap else None,
        )
    elif input_stage == "top":
        undistorted = image.copy()
        top_view = image.copy()
    else:
        raise ValueError(f"Unknown input_stage: {input_stage}")

    saved["01_undistorted"] = _save_image(output_dir / "01_undistorted.jpg", undistorted)
    saved["02_top_view"] = _save_image(output_dir / "02_top_view.jpg", top_view)

    top_grid = draw_top_view_grid(top_view, cols=DEFAULT_GRID_COLS, rows=DEFAULT_GRID_ROWS)
    saved["03_top_view_grid"] = _save_image(output_dir / "03_top_view_grid.jpg", top_grid)

    marker = detect_marker(top_view)
    marker_world = None
    pose = None
    rel_vec = None
    delta = None
    motor_command = None
    desired_yaw = None
    yaw_error = None

    if marker is not None:
        marker_img = draw_marker_detection(top_view, marker)
        saved["04_marker_detected"] = _save_image(output_dir / "04_marker_detected.jpg", marker_img)

        crop_debug = draw_code_cells_on_crop(marker.crop, marker.code_grid)
        saved["05_marker_crop_code"] = _save_image(output_dir / "05_marker_crop_code.jpg", crop_debug)

        marker_world, pose, rel_vec = estimate_robot_pose(marker, DEFAULT_MARKER_MAP)

        if pose is not None:
            delta = compute_target_delta(pose, target)
            desired_yaw = compute_desired_yaw_deg(pose, target)
            yaw_error = compute_yaw_error_deg(pose, target)

            model = MotorRegressionModel(DEFAULT_MOTOR_MODEL)
            motor_command = model.predict(delta.dx, delta.dy)

        world_img = draw_pose_world(marker_world, pose, target, delta)
        saved["06_pose_world"] = _save_image(output_dir / "06_pose_world.jpg", world_img)

    result = {
        "input_image": str(image_path),
        "input_stage": input_stage,
        "target": {"x": target[0], "y": target[1]},
        "outputs": saved,
        "marker": None,
        "marker_world": None,
        "robot_pose": None,
        "relative_marker_vector": None,
        "target_delta": None,
        "navigation": None,
        "motor_command": None,
        "notes": [
            "This repository keeps the image-based pipeline separate from the physical Raspbot runtime.",
            "A real Raspbot driving demo exists separately, but this offline path is used so the core logic can be reviewed without the hardware setup.",
            "Marker id 181 is restored from old project comments for sample reproducibility; verify it against the real marker map before reuse.",
            "reference_px is a marker-side reference point used by the original pose logic, not the geometric center of the marker.",
        ],
    }

    if marker is not None:
        result["marker"] = {
            "id": marker.marker_id,
            "angle_deg": marker.angle_deg,
            "reference_px": {"u": marker.reference_px[0], "v": marker.reference_px[1]},
            "rect_area": marker.rect_area,
            "code_grid": marker.code_grid.astype(int).tolist(),
        }

    if marker_world is not None:
        result["marker_world"] = {"x": marker_world[0], "y": marker_world[1]}

    if rel_vec is not None:
        result["relative_marker_vector"] = {"x_rel": rel_vec[0], "y_rel": rel_vec[1]}

    if pose is not None:
        result["robot_pose"] = {"x": pose.x, "y": pose.y, "yaw_deg": pose.yaw_deg}

    if delta is not None:
        result["target_delta"] = {
            "dx": delta.dx,
            "dy": delta.dy,
            "distance": delta.distance,
        }
        result["navigation"] = {
            "desired_yaw_deg": desired_yaw,
            "yaw_error_deg": yaw_error,
        }

    if motor_command is not None:
        result["motor_command"] = {
            "left_power": motor_command.left_power,
            "right_power": motor_command.right_power,
            "duration_sec": motor_command.duration_sec,
            "heuristic_distance_estimate": motor_command.heuristic_distance_estimate,
            "raw_left_power": motor_command.raw_left_power,
            "raw_right_power": motor_command.raw_right_power,
            "raw_duration_sec": motor_command.raw_duration_sec,
        }

    json_path = output_dir / "result.json"
    json_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run offline marker localization demo from one image."
    )
    parser.add_argument("--image", required=True, type=Path, help="Input image path")
    parser.add_argument(
        "--target",
        default="0,2",
        help="Target coordinate. Examples: '0,2' or '0 2'",
    )
    parser.add_argument(
        "--input-stage",
        choices=["raw", "undistorted", "top"],
        default="top",
        help=(
            "raw: input camera image -> undistort -> top-view remap; "
            "undistorted: input is already undistorted -> top-view remap; "
            "top: input is already top-view."
        ),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=OUTPUT_DIR / "offline_demo",
        help="Directory to store generated images and result.json",
    )
    parser.add_argument(
        "--no-calibration",
        action="store_true",
        help="Disable camera undistortion for raw input.",
    )
    parser.add_argument(
        "--no-topview-remap",
        action="store_true",
        help="Disable top-view remap for raw/undistorted input.",
    )

    args = parser.parse_args()
    result = run_demo(
        image_path=args.image,
        target=_parse_target(args.target),
        input_stage=args.input_stage,
        output_dir=args.output_dir,
        use_calibration=not args.no_calibration,
        use_topview_remap=not args.no_topview_remap,
    )

    print("\n=== Offline Marker Localization Result ===")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
