# Sample Offline Demo Result

아래 명령은 저장소에 포함된 샘플 이미지로 오프라인 데모를 실행합니다.

```bash
PYTHONPATH=src python -m marker_localization.app.run_offline_demo \
  --image assets/samples/test.jpg \
  --input-stage undistorted \
  --target 0,2 \
  --output-dir assets/outputs/offline_demo
```

## Result summary

```text
marker id       : 181
marker angle    : 80.888 deg
reference px    : (642.0, 628.5)
robot pose      : x=0.086, y=1.506, yaw=99.111 deg
target          : x=0.000, y=2.000
dx, dy          : -0.086, 0.494
distance        : 0.502
motor command   : left=60.0, right=60.0, duration=0.35 sec
```

`reference px`는 실제 마커 중심점이 아니라, 원본 pose 계산 로직에서 사용한 마커 방향 기준 side/reference point입니다.

## Relation to real run videos

실제 라즈봇 주행 자료는 저장소에 직접 포함하지 않고 README의 GitHub attachment 링크로 연결합니다. 저장소에는 문서에서 사용할 고정 이미지와 오프라인 데모 코드만 포함합니다.

오프라인 샘플 결과는 실제 로봇을 다시 움직이는 것이 아니라, 저장된 이미지로 아래 흐름을 재현하는 것입니다.

```text
marker detection
→ marker id / angle decoding
→ robot pose estimation
→ target delta calculation
→ motor command recommendation
```

## Generated files

```text
assets/outputs/offline_demo/
├── 00_input.jpg
├── 01_undistorted.jpg
├── 02_top_view.jpg
├── 03_top_view_grid.jpg
├── 04_marker_detected.jpg
├── 05_marker_crop_code.jpg
├── 06_pose_world.jpg
└── result.json
```

## Fixed images for README

`assets/outputs/`는 실행 결과 폴더이므로 git에서 제외합니다. README와 문서에 고정으로 보여줄 이미지는 아래 위치에 복사해두었습니다.

```text
docs/images/offline_demo/
├── 00_input.jpg
├── 04_marker_detected.jpg
├── 05_marker_crop_code.jpg
└── 06_pose_world.jpg
```
