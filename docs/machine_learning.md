# Machine Learning Part

이 프로젝트에서 ML은 마커를 찾거나 위치를 추정하는 데 사용하지 않습니다.

```text
위치 인식      : OpenCV + geometry
이동 명령 추정 : scikit-learn regression model
```

## Model

원본 실험 노트북에서 사용한 모델은 scikit-learn 기반 회귀 모델입니다.

```python
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import make_pipeline

reg = make_pipeline(PolynomialFeatures(3), LinearRegression())
reg.fit(X, Y)
```

현재 저장소에는 학습된 모델이 `models/model2.pkl`로 포함되어 있습니다.

## Input / output

학습 방향은 아래와 같습니다.

```text
input  X = [dx, dy]
output Y = [left_power, right_power, duration]
```

즉, 목표 위치까지의 이동 벡터를 넣으면 좌/우 모터 출력과 구동 시간을 추정합니다.

## Why this model was used

당시 라즈봇 환경에는 엔코더 기반 피드백이 없었습니다. 같은 모터 출력을 줘도 실제 이동량은 여러 조건에 따라 달라질 수 있었습니다.

- 좌/우 모터 출력 편차
- 배터리 상태
- 바닥 마찰
- 바퀴 상태
- 조립 오차

그래서 여러 이동 명령을 실제로 실행해보고, 목표 이동 벡터에 대해 어떤 명령이 적당한지 회귀 모델로 근사했습니다.

## Model scope

이 모델은 closed-loop controller가 아닙니다. 단일 목표 이동 벡터 `dx`, `dy`에 대해 한 번의 모터 명령 추정값을 반환하는 회귀 모델입니다.

실제 라즈봇 실험에서의 보정은 모델 내부가 아니라 상위 실행 루프에서 이루어졌습니다. 로봇이 이동한 뒤 카메라 프레임을 다시 읽고, 마커를 재검출하고, 현재 pose를 다시 계산한 다음 다음 명령을 결정하는 방식입니다. 이 저장소에는 해당 실시간 카메라 입력 루프와 하드웨어 제어 루프가 포함되어 있지 않습니다.

따라서 이 저장소의 ML 모델은 아래 범위로 해석해야 합니다.

```text
marker-based pose estimation result
→ target delta dx, dy
→ regression-based open-loop motor command estimate
```

## Reproducibility note

`model2.pkl`은 scikit-learn 1.6.1 환경에서 만들어진 파일입니다. pickle 모델은 라이브러리 버전에 민감할 수 있으므로 `requirements.txt`에서는 scikit-learn 버전을 고정했습니다.

```text
scikit-learn==1.6.1
```

또한 pickle은 임의 코드 실행 위험이 있으므로, 신뢰할 수 있는 로컬 모델 파일만 로드해야 합니다.
