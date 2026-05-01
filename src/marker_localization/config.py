from __future__ import annotations

from pathlib import Path

# Project root = repository root when running from source checkout.
PROJECT_ROOT = Path(__file__).resolve().parents[2]

ASSET_DIR = PROJECT_ROOT / "assets"
CALIBRATION_DIR = ASSET_DIR / "calibration"
SAMPLE_DIR = ASSET_DIR / "samples"
OUTPUT_DIR = ASSET_DIR / "outputs"
MODEL_DIR = PROJECT_ROOT / "models"

DEFAULT_CALIB_FILE = CALIBRATION_DIR / "calib.dat"
DEFAULT_TOPVIEW_MAPX = CALIBRATION_DIR / "mapx.npy"
DEFAULT_TOPVIEW_MAPY = CALIBRATION_DIR / "mapy.npy"
DEFAULT_MOTOR_MODEL = MODEL_DIR / "model2.pkl"

# 원본 프로젝트에서 사용하던 마커 좌표표.
# 181은 원본 주석에 "181: (0, 2)"로 남아 있어 오프라인 데모가 돌아가도록 포함했다.
# 실제 공개 전에 marker_definition.md와 실제 바닥 배치 기준으로 최종 검증해야 한다.
DEFAULT_MARKER_MAP = {
    163: (-0.5, 0.0),
    217: (0.0, 1.0),
    219: (0.5, 0.0),
    158: (1.0, 1.0),
    121: (-1.0, 1.0),
    186: (-1.0, 3.0),
    122: (1.0, 3.0),
    57: (0.5, 2.0),
    71: (-0.5, 2.0),
    234: (0.0, 3.0),
    181: (0.0, 2.0),  # inferred from old notebook/code comments
}

# 마커의 월드 기준 방향.
# 원본 코드의 get_camera_yaw_from_marker() 기본값과 동일하게 90도 사용.
DEFAULT_MARKER_WORLD_ANGLE_DEG = 90.0

# Top-view 결과를 사람이 보기 쉽게 나누는 격자 수.
DEFAULT_GRID_COLS = 8
DEFAULT_GRID_ROWS = 8

# 원본 marker_utils.py의 pixel_to_world_mat()에서 쓰던 Homography inverse.
# top-view 이미지 픽셀 좌표를 로봇 기준 local 좌표로 투영하는 실험값이다.
DEFAULT_H_INV = [
    [1.57550828e-03, 4.23889210e-05, -1.04527664e00],
    [2.06584266e-05, -1.56875324e-03, 1.48552640e00],
    [6.82991287e-07, 3.46551356e-05, 1.00000000e00],
]
