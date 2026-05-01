from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

from marker_localization.types import MotorCommand


class MotorRegressionModel:
    """엔코더 없는 Raspbot open-loop 이동 보정용 회귀 모델.

    원본 MOVE_leaning.ipynb에서 학습한 모델은 다음 구조입니다.

        PolynomialFeatures(3) + LinearRegression

    학습 방향:
        입력  X = 실제/목표 이동 벡터 (x, y)
        출력  Y = 모터 명령 (left_power, right_power, duration)

    즉, dx/dy를 넣으면 왼쪽/오른쪽 모터 파워와 구동 시간을 예측합니다.
    이 모델은 closed-loop controller가 아니라 기존 실험 환경에서의
    open-loop command recommendation에 가깝습니다.
    """

    def __init__(
        self,
        model_path: Path,
        *,
        speed_gain: float = 1.3,
        min_power: float = 25.0,
        max_power: float = 60.0,
        min_duration: float = 0.35,
        max_duration: float = 0.50,
        base_speed: float = 30.0,
        base_duration: float = 0.2,
        dist_per_base: float = 1.0 / 7.0,
    ):
        self.model_path = Path(model_path)
        self.speed_gain = speed_gain
        self.min_power = min_power
        self.max_power = max_power
        self.min_duration = min_duration
        self.max_duration = max_duration
        self.base_speed = base_speed
        self.base_duration = base_duration
        self.dist_per_base = dist_per_base
        self.model = self._load_model(self.model_path)

    @staticmethod
    def _load_model(model_path: Path) -> Any:
        """pickle 기반 scikit-learn 모델을 로드합니다.

        주의: pickle은 신뢰할 수 있는 로컬 파일만 로드해야 합니다.
        """
        import pickle

        with Path(model_path).open("rb") as f:
            return pickle.load(f)

    def _clip_signed_power(self, value: float) -> float:
        """모터 출력의 부호를 보존하면서 최소/최대 절댓값을 제한합니다.

        기존 단순 clip은 음수 예측값도 양수 min_power로 바꿀 수 있으므로,
        회전/후진 방향 정보를 보존하기 위해 signed clipping을 사용합니다.
        """
        if abs(value) < 1e-9:
            return 0.0

        sign = 1.0 if value > 0.0 else -1.0
        magnitude = float(np.clip(abs(value), self.min_power, self.max_power))
        return sign * magnitude

    def predict(self, dx: float, dy: float) -> MotorCommand:
        """목표 이동 벡터 dx/dy에 대한 모터 명령을 예측합니다."""
        feat = np.array([[dx, dy]], dtype=float)
        raw_left, raw_right, raw_duration = self.model.predict(feat)[0]

        left = self._clip_signed_power(float(raw_left) * self.speed_gain)
        right = self._clip_signed_power(float(raw_right) * self.speed_gain)
        duration = float(np.clip(raw_duration, self.min_duration, self.max_duration))

        avg_speed = (abs(left) + abs(right)) / 2.0
        speed_ratio = avg_speed / self.base_speed
        time_ratio = duration / self.base_duration
        heuristic_distance_estimate = self.dist_per_base * speed_ratio * time_ratio

        return MotorCommand(
            left_power=left,
            right_power=right,
            duration_sec=duration,
            heuristic_distance_estimate=float(heuristic_distance_estimate),
            raw_left_power=float(raw_left),
            raw_right_power=float(raw_right),
            raw_duration_sec=float(raw_duration),
        )
