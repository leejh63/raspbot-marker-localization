# Real Run Media Notes

이 저장소는 실제 라즈봇 구동 자료와 오프라인 데모 자료를 함께 설명하지만, 대용량 영상 파일을 저장소에 직접 포함하지 않습니다. 실제 구동 자료는 GitHub README attachment로 연결하고, 저장소에는 코드 리뷰와 문서화에 필요한 정적 이미지와 오프라인 데모 코드만 포함합니다.

## Media policy

```text
README GitHub attachments
├── target coordinate movement video
├── grid trace while moving
└── target / marker layout image

Repository files
├── assets/media/.gitkeep
├── docs/images/real_run/grid_trace_still.jpg
└── docs/images/real_run/target_move_poster.jpg
```

`assets/media/`는 로컬에서 영상 파일을 임시로 둘 수 있는 자리만 남겨둔 폴더입니다. `.gitignore`에서 `mp4`, `mov`, `webm`, `gif`, `jpg` 파일은 제외하므로, 로컬 영상 파일이 실수로 커밋되지 않습니다.

## Target coordinate movement video

라즈봇이 특정 좌표를 향해 이동하는 실제 구동 영상입니다.

이 영상은 원래 실험이 실제 하드웨어에서 진행됐다는 것을 보여주기 위한 자료입니다. 다만 영상만으로는 코드 구조, 위치 추정 계산, marker id decode 과정을 확인하기 어렵습니다.

## Grid trace while moving

라즈봇이 이동하는 동안 추정된 위치가 grid 화면에 찍히는 자료입니다.

빨간 점은 추정된 로봇 위치를 나타내고, grid는 marker map 기준 좌표계를 시각화한 것입니다. 이 자료는 실제 이동 중 위치 추정 결과가 어떻게 표시됐는지 보여줍니다.

## Why the offline demo still exists

실제 구동 영상이 있어도 GitHub에서 같은 실험을 재현하려면 다음 조건이 필요합니다.

- 동일하거나 비슷한 라즈봇 하드웨어
- 카메라 장착 위치
- 바닥 마커 배치
- 조명 조건
- 원본 런타임 제어 코드

이 조건을 모두 맞추기는 어렵습니다. 그래서 이 저장소에서는 실제 구동 자료는 맥락으로 남기고, 코드 리뷰가 가능한 부분은 오프라인 데모로 분리했습니다.

정리하면 아래와 같습니다.

```text
README attached video/image    : 실제 좌표 이동 시연과 grid trace 자료
repository fixed images        : README/docs에 사용하는 정적 이미지
offline demo code              : 저장된 이미지로 marker detection → pose estimation 흐름 재현
```
