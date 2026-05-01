# Refactor Notes

이 저장소는 원본 라즈봇 실험 코드를 그대로 공개한 것이 아닙니다. 실제 구동 자료는 영상으로 남기고, 코드 리뷰가 가능한 핵심 흐름만 오프라인 데모로 다시 정리했습니다.

## Original context

원래 실험에서는 라즈봇이 바닥 마커를 기준으로 자신의 위치를 추정하고, 특정 좌표로 이동하는 흐름을 테스트했습니다.

실제 실험 흐름은 아래와 같았습니다.

```text
1. 사용자가 목표 좌표를 입력합니다.
2. 카메라 프레임에서 바닥 마커를 검출합니다.
3. 마커 ID와 방향을 이용해 로봇의 현재 pose를 추정합니다.
4. 현재 pose와 목표 좌표의 차이를 계산합니다.
5. 목표까지의 거리가 threshold보다 크면 모터 명령을 생성해 이동합니다.
6. 이동 후 다시 카메라 프레임을 읽어 현재 위치를 재추정합니다.
7. 목표 근처에 도달할 때까지 2~6 과정을 반복합니다.
```

현재 저장소는 대용량 영상을 직접 포함하지 않습니다. 실제 라즈봇 특정 좌표 이동 영상과 grid trace 자료는 README의 GitHub attachment 링크로 연결하고, 저장소에는 문서용 정적 이미지와 오프라인 데모 코드만 포함합니다.

이 영상 자료들은 실험이 실제 하드웨어에서 진행됐다는 맥락을 보여줍니다. 하지만 같은 로봇과 바닥 세팅이 없으면 GitHub에서 바로 재현하기 어렵습니다.

## Removed from the public core

아래 항목은 이번 오프라인 데모의 핵심이 아니어서 제외했습니다.

- 실시간 라즈봇 I2C 제어 코드
- 실험용 `main_*` 실행 파일들
- YOLO / hand detection / lane detection 실험 코드
- 로컬 경로에 강하게 묶인 코드
- 실행 중 생성되는 cache 파일
- `__pycache__`, `*.pyc`

## Preserved core ideas

아래 흐름은 유지했습니다.

- adaptive threshold + contour hierarchy 기반 마커 검출
- outer/inner contour 상대 위치 기반 마커 방향 추정
- homography warp 기반 marker id decode
- marker id → world coordinate lookup
- marker 기준 robot pose 계산
- `model2.pkl` 기반 open-loop motor command prediction

## Why this refactor was needed

실제 라즈봇 구동 영상은 있지만, 로봇이 없는 환경에서는 같은 실험을 다시 보여주기 어렵습니다. 그래서 하드웨어가 필요한 부분과 이미지 한 장으로 검증 가능한 부분을 나눴습니다.

이렇게 분리하면 다음 장점이 있습니다.

- 리뷰어가 로봇 없이도 결과를 확인할 수 있습니다.
- 코드 흐름을 단계별로 설명하기 쉽습니다.
- 실패 지점을 image processing, pose estimation, motor model 중 어디인지 나눠서 볼 수 있습니다.
- 나중에 실제 라즈봇 제어 계층을 다시 붙이기 쉽습니다.

## Current output-first goal

현재 목표는 아래 결과물을 안정적으로 생성하는 것입니다.

```text
00_input.jpg
01_undistorted.jpg
02_top_view.jpg
03_top_view_grid.jpg
04_marker_detected.jpg
05_marker_crop_code.jpg
06_pose_world.jpg
result.json
```
