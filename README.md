# Raspbot Marker Localization Offline Demo

실제 라즈봇 좌표 이동 실험에서 사용했던 마커 기반 위치 추정 흐름을,
하드웨어 없이 재현 가능한 오프라인 데모로 분리한 저장소입니다.

이 프로젝트는 저장된 이미지에서 바닥 마커를 검출하고,
마커 ID와 방향을 이용해 로봇의 pose를 추정한 뒤,
목표 좌표까지의 delta를 계산하고 open-loop 모터 명령을 추천합니다.

> This repository does not include the full real-time robot runtime.  
> It focuses on the reproducible perception/localization pipeline extracted from the original Raspbot experiment.

```text
image input
→ optional camera/top-view remap
→ marker detection
→ marker ID / angle decoding
→ robot pose estimation
→ target delta calculation
→ open-loop motor command recommendation
```
## Original real robot experiment

원래 라즈봇 프로젝트는 이미지 한 장만 분석하는 오프라인 데모가 아니라, 실제 로봇이 목표 좌표를 입력받고 현재 위치를 반복적으로 추정하면서 목표 지점까지 이동하는 방식으로 진행되었습니다.

실험 당시의 동작 흐름은 아래와 같았습니다.

```text
1. 사용자가 목표 좌표를 입력한다.
2. 카메라 프레임에서 바닥 마커를 검출한다.
3. 마커 ID와 방향을 이용해 로봇의 현재 pose를 추정한다.
4. 현재 pose와 목표 좌표의 차이를 계산한다.
5. 목표까지의 거리가 threshold보다 크면 모터 명령을 생성해 이동한다.
6. 이동 후 다시 카메라 프레임을 읽어 현재 위치를 재추정한다.
7. 목표 근처에 도달할 때까지 2~6 과정을 반복한다.
```

다만 각 모터 명령은 엔코더 피드백을 사용하는 정밀 제어기가 아니라, 기존 실험 데이터로 학습한 open-loop command recommendation에 가까웠습니다. 즉, 한 번의 이동 명령으로 끝내는 구조가 아니라 이동 후 다시 마커를 인식해 pose를 갱신하는 방식으로 진행했습니다.

이 저장소는 위 전체 루프 중에서 아래 계산 흐름을 오프라인으로 분리한 버전입니다.

```text
camera/top-view image
→ marker detection
→ marker id / angle decoding
→ robot pose estimation
→ target delta calculation
→ motor command recommendation
```

## Real robot demo material

실제 좌표 이동 실험에서 사용한 영상 자료입니다.

<table>
  <tr>
    <td align="center" valign="top">
      <strong>Grid trace while moving</strong><br><br>
      <img width="300" height="364" alt="real_raspbot_grid_trace" src="https://github.com/user-attachments/assets/792291b8-e072-4ac0-b727-376303f18c1c" />
      <br><br>
      이동시, 추정 위치가 실시간으로 화면에 표시
      <br>
    </td>
    <td align="center" valign="top">
      <strong>Target / marker layout</strong><br><br>
        <img width="725" height="364" alt="real_raspbot_target_move_poster" src="https://github.com/user-attachments/assets/96e99b1d-f8be-4d1f-a9ec-42c0c17d6940" />
      <br><br>
      영상에서 사용한 마커 좌표와 이동 목표 좌표 순서
    </td>
  </tr>
</table>

### Target coordinate movement

라즈봇이 목표 좌표를 향해 이동하는 실제 구동 영상입니다.


https://github.com/user-attachments/assets/66352bb0-e060-425c-8fd8-5ef561f5db8d


위 자료는 실제 라즈봇에서 작동 여부를 보여주기 위한 것입니다. 아래 오프라인 데모는 같은 하드웨어가 없어도 마커 인식과 위치 추정 흐름을 확인할 수 있도록 분리한 버전입니다.

## Offline demo result

| Input | Marker detection | Pose / target |
|---|---|---|
| <img height="498" alt="00_input" src="https://github.com/user-attachments/assets/695368b3-ec61-47b7-a3c6-cb6d5e1c421f" /> | <img width="264" height="316" alt="04_marker_detected" src="https://github.com/user-attachments/assets/9e7fc957-0a5c-42af-8f29-0cca707930ef" /> | <img height="498" alt="06_pose_world" src="https://github.com/user-attachments/assets/0ab6af21-afd9-4e0b-8bc4-ce48b94c9a3b" /> |





샘플 실행 결과:

```text
marker id       : 181
marker angle    : 80.888 deg
robot pose      : x=0.086, y=1.506, yaw=99.111 deg
target          : x=0.000, y=2.000
target distance : 0.502
motor command   : left=60.0, right=60.0, duration=0.35 sec
```

## What this repository shows

이 저장소에서 확인할 수 있는 부분은 아래입니다.

- 저장된 이미지에서 바닥 마커 검출
- 마커 ID와 마커 각도 해석
- 마커 맵 기준의 로봇 위치와 yaw 계산
- 목표 좌표까지의 `dx`, `dy`, distance 계산
- 기존 실험에서 만든 회귀 모델을 이용한 open-loop 모터 명령 추천

## Project scope

이 저장소는 원본 라즈봇 실험 전체를 그대로 공개한 것이 아니라, 하드웨어 없이 재현 가능한 핵심 알고리즘 흐름만 분리한 오프라인 데모입니다.

포함한 부분:

- 저장 이미지 기반 marker detection
- marker id / angle decoding
- marker map 기반 robot pose estimation
- target coordinate 기준 delta 계산
- 기존 실험 데이터로 학습한 open-loop motor command recommendation

제외한 부분:

- 실시간 카메라 입력 루프
- 라즈봇 하드웨어 제어 코드
- I2C 기반 모터 제어 runtime
- YOLO / line tracing / hand detection 등 다른 실험 코드
- 실제 로봇 주행에 필요한 runtime loop와 하드웨어 adapter

이렇게 분리한 이유는 같은 라즈봇 하드웨어와 바닥 마커 환경이 없어도 GitHub에서 핵심 계산 흐름을 재현할 수 있게 하기 위함입니다.

## Repository structure

```text
src/marker_localization/
├── app/               # CLI entry point
├── vision/            # calibration, marker detection, decoding, visualization
├── localization/      # geometry and robot pose estimation
├── navigation/        # target delta and motor command model
├── config.py          # asset paths, marker map, calibration constants
└── types.py           # shared dataclasses

assets/
├── media/             # .gitkeep only; demo media is attached through GitHub README
├── samples/           # sample image for the offline demo
├── calibration/       # remap/calibration data restored from the original project
└── outputs/           # generated outputs, ignored by git except .gitkeep

docs/
├── architecture.md
├── coordinate_system.md
├── machine_learning.md
├── marker_definition.md
├── media_notes.md
├── refactor_notes.md
└── sample_result.md
```

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

PYTHONPATH=src python -m marker_localization.app.run_offline_demo \
  --image assets/samples/test.jpg \
  --input-stage undistorted \
  --target 0,2 \
  --output-dir assets/outputs/offline_demo
```

Windows PowerShell에서는 `PYTHONPATH=src` 대신 아래처럼 실행할 수 있습니다.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

$env:PYTHONPATH="src"
python -m marker_localization.app.run_offline_demo `
  --image assets/samples/test.jpg `
  --input-stage undistorted `
  --target 0,2 `
  --output-dir assets/outputs/offline_demo
```

실행 후 아래 파일들이 생성됩니다.

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

## CLI options

| Option | Description |
|---|---|
| `--image` | 입력 이미지 경로 |
| `--input-stage raw` | 카메라 원본 이미지로 보고 왜곡 보정과 top-view remap을 모두 적용 |
| `--input-stage undistorted` | 왜곡 보정은 끝났고 top-view remap만 필요한 이미지 |
| `--input-stage top` | 이미 top-view 상태인 이미지 |
| `--target x,y` | 목표 좌표. 예: `0,2` |
| `--output-dir` | 결과 이미지와 `result.json` 저장 위치 |
| `--no-calibration` | raw 입력에서 카메라 왜곡 보정 생략 |
| `--no-topview-remap` | raw/undistorted 입력에서 top-view remap 생략 |

현재 저장소에 포함된 기본 샘플은 `assets/samples/test.jpg`입니다. 이 샘플은 `--input-stage undistorted` 기준으로 동작하도록 맞춰두었습니다.

> Note  
> `--input-stage`의 코드 기본값은 `top`이지만, 현재 저장소에 포함된 샘플 이미지 `assets/samples/test.jpg`는 `undistorted` 기준으로 실행하도록 맞춰두었습니다.  
> 따라서 샘플 재현 시에는 README의 Quick start처럼 `--input-stage undistorted`를 명시하는 것을 권장합니다.

## Pipeline

### 1. Marker detection

OpenCV 기반으로 adaptive threshold와 contour hierarchy를 사용해 바닥 마커 후보를 찾습니다. 외곽 사각형과 내부 사각형의 상대 위치를 이용해 마커 방향을 계산합니다.

관련 코드:

```text
src/marker_localization/vision/marker_detector.py
src/marker_localization/vision/marker_decoder.py
```

### 2. Marker ID / angle decoding

마커 영역을 정면에서 본 형태로 warp한 뒤, 4x6 cell 구조로 나누어 마커 ID를 읽습니다.

디버그 이미지는 아래 파일로 저장됩니다.

```text
assets/outputs/offline_demo/05_marker_crop_code.jpg
```

### 3. Robot pose estimation

검출된 마커 ID를 월드 좌표 테이블에서 찾고, top-view 이미지상의 마커 기준점을 로봇 기준 상대 벡터로 변환합니다. 여기서 기준점은 실제 마커의 기하학적 중심이 아니라, 원본 로직에서 사용한 마커 방향 기준 side/reference point입니다. 이후 마커의 월드 좌표와 상대 벡터를 이용해 로봇의 위치와 yaw를 계산합니다.

관련 문서:

```text
docs/coordinate_system.md
docs/marker_definition.md
```

### 4. Motor command recommendation

이 프로젝트에서 ML 모델은 위치 인식에 사용하지 않았습니다. 위치 인식은 OpenCV와 geometry 기반 계산으로 처리하고, ML 모델은 목표 이동 벡터 `dx`, `dy`에 대한 open-loop 모터 명령을 추천하는 데 사용했습니다.

```text
input : dx, dy
output: left_power, right_power, duration
```

관련 문서:

```text
docs/machine_learning.md
```

## Why it is separated as an offline demo

원래 실험은 실제 라즈봇, 카메라, 바닥 마커, 조명 조건이 모두 맞아야 재현할 수 있습니다. 실제 구동 영상은 남아 있지만, GitHub를 보는 사람이 같은 하드웨어 환경을 가지고 있을 가능성은 낮습니다.

그래서 이 저장소에서는 실제 구동 자료와 오프라인 코드 데모를 분리했습니다.

```text
실제 구동 자료      : 라즈봇이 목표 좌표로 이동하는 영상
오프라인 코드 데모  : 이미지 한 장으로 위치 추정 흐름을 재현하는 코드
```

라즈봇이 없어도 아래 항목을 확인할 수 있습니다.

- 저장된 이미지에서 마커를 검출할 수 있는가
- 마커 ID와 각도를 읽을 수 있는가
- 마커 맵 기준으로 로봇 위치를 계산할 수 있는가
- 목표 좌표까지의 delta를 계산할 수 있는가
- 기존 실험에서 학습한 모델로 이동 명령을 추천할 수 있는가

## Documentation

- [Architecture](docs/architecture.md)
- [Coordinate system](docs/coordinate_system.md)
- [Marker definition](docs/marker_definition.md)
- [Machine learning part](docs/machine_learning.md)
- [Real run media notes](docs/media_notes.md)
- [Sample result](docs/sample_result.md)
- [Refactor notes](docs/refactor_notes.md)
