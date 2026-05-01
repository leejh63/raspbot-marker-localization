# Architecture

이 저장소는 실제 라즈봇을 바로 움직이는 런타임 코드가 아니라, 원본 실험에서 오프라인으로 확인 가능한 부분을 분리한 구조입니다.

실제 라즈봇 구동 영상은 저장소에 직접 포함하지 않고 GitHub README attachment로 연결합니다. 코드 쪽은 그 실험에서 사용한 마커 인식과 위치 추정 흐름을 이미지 한 장으로 다시 확인할 수 있게 만든 버전입니다.

핵심 기준은 다음 세 가지입니다.

1. 로봇이 없어도 이미지 한 장으로 결과를 확인할 수 있어야 합니다.
2. 마커 검출, 위치 추정, 이동 명령 추천 단계를 따로 설명할 수 있어야 합니다.
3. 나중에 실제 라즈봇 제어 코드를 다시 붙일 수 있어야 합니다.

## Overall split

```text
Real robot demo material
├── target movement video, linked from README attachment
├── grid trace material, linked from README attachment
└── fixed still images under docs/images/real_run/

Offline repository code
├── marker detection
├── marker id / angle decoding
├── pose estimation
└── open-loop motor command recommendation
```

## Pipeline

```text
Input image
  ↓
Optional calibration / top-view remap
  ↓
Marker detection
  ↓
Marker direction + marker id decoding
  ↓
Marker id → world coordinate lookup
  ↓
Robot pose estimation
  ↓
Target delta calculation
  ↓
Motor command recommendation
```

## Module layout

```text
src/marker_localization/
├── app/
│   └── run_offline_demo.py
├── vision/
│   ├── calibration.py
│   ├── marker_detector.py
│   ├── marker_decoder.py
│   └── visualization.py
├── localization/
│   ├── geometry.py
│   └── pose_estimator.py
├── navigation/
│   ├── target_planner.py
│   └── motor_model.py
├── config.py
└── types.py
```

## Responsibilities

### `app/`

CLI 실행 진입점입니다. 입력 이미지, target, input stage, output directory를 받아 전체 파이프라인을 순서대로 실행합니다.

### `vision/`

이미지 처리와 디버그 시각화를 담당합니다.

- `calibration.py`: `calib.dat`, `mapx.npy`, `mapy.npy` 기반 remap 처리
- `marker_detector.py`: contour hierarchy 기반 마커 후보 검출
- `marker_decoder.py`: 마커 방향 계산, corner ordering, marker id decode
- `visualization.py`: grid, marker detection, world pose 결과 이미지 생성

### `localization/`

검출된 마커 정보를 로봇 위치로 변환합니다.

- marker id로 월드 좌표 조회
- marker reference point pixel을 로봇 기준 상대 벡터로 변환
- marker world coordinate와 relative vector로 robot pose 계산

여기서 `reference_px`는 실제 마커 중심점이 아니라, 원본 pose 계산 로직에서 사용한 마커 방향 기준 side/reference point입니다.

### `navigation/`

현재 위치에서 목표 좌표까지의 차이를 계산하고, 기존 실험에서 만든 회귀 모델로 open-loop 이동 명령을 추천합니다.

## Why hardware code is not here

원본 프로젝트에는 카메라 입력, 라즈봇 I2C 제어, 마커 인식, 이동 제어가 한 흐름에 같이 있었습니다. 실제 구동 영상은 있지만, 같은 로봇 세팅을 다시 준비하지 않으면 런타임 전체를 재현하기 어렵습니다.

그래서 이 저장소에서는 하드웨어 의존 코드를 제외하고 아래 부분만 남겼습니다.

- 이미지 기반 마커 인식
- marker id / angle decode
- marker map 기반 pose estimation
- target delta 계산
- 기존 모델 기반 motor command recommendation

실제 주행 코드를 다시 붙인다면 `hardware/` 또는 `runtime/` 계층을 따로 두고, 현재 `navigation` 결과를 라즈봇 I2C 명령으로 변환하는 adapter를 추가하는 방식이 적절합니다.
