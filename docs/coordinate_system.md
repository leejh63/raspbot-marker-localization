# Coordinate System Notes

마커 기반 위치 추정에서 가장 헷갈리기 쉬운 부분은 좌표계입니다. 이 프로젝트에서는 이미지 좌표, 마커 방향, 월드 좌표, 로봇 yaw가 서로 다른 기준을 가집니다.

## Image coordinate

OpenCV 이미지 좌표는 아래 기준입니다.

```text
u: 오른쪽 +
v: 아래 +
```

즉, 화면 위쪽으로 갈수록 `v` 값은 작아집니다.

## Marker angle

마커 방향은 이미지 평면에서 아래 기준으로 해석합니다.

```text
오른쪽: 0 deg
위쪽  : 90 deg
왼쪽  : 180 deg
아래쪽: 270 deg
```

마커 내부 사각형이 외부 사각형의 어느 쪽에 붙어 있는지를 이용해 방향을 추정합니다.

## Marker reference point

이 프로젝트의 `reference_px`는 실제 마커의 기하학적 중심점이 아닙니다. 원본 로직에서 마커 방향과 corner ordering을 안정적으로 맞추기 위해 사용한 마커 방향 기준 side/reference point입니다.

따라서 문서나 JSON 결과에서 `reference_px`를 볼 때는 “마커 중심 좌표”가 아니라 “pose 계산에 사용한 기준 픽셀”로 해석해야 합니다.

## Robot yaw

원본 실험 코드에서 사용하던 yaw 계산식은 아래와 같습니다.

```python
yaw = marker_world_angle + 90 - marker_angle
```

현재 기본값은 다음과 같습니다.

```text
marker_world_angle = 90 deg
```

최종 yaw는 0~360도 범위로 정규화합니다.

## Pose estimation formula

마커의 월드 좌표를 `M`, 로봇 기준 마커 상대 벡터를 `v_rel`, 로봇 yaw 회전을 `R`이라고 하면 관계식은 다음과 같습니다.

```text
M = Robot + R(yaw - 90 deg) * v_rel
```

따라서 로봇 위치는 아래처럼 계산합니다.

```text
Robot = M - R(yaw - 90 deg) * v_rel
```

`yaw - 90 deg` 보정은 원본 실험 코드의 좌표 기준과 이미지에서 얻은 마커 방향 기준을 맞추기 위한 처리입니다.
