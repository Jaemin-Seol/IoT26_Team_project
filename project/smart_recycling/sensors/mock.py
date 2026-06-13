from __future__ import annotations

import time


class MockPirSensor:
    def __init__(self, active_every_seconds: float = 10.0) -> None:
        self.started = time.monotonic()
        self.active_every_seconds = active_every_seconds

    def is_motion_detected(self) -> bool:
        phase = (time.monotonic() - self.started) % self.active_every_seconds
        return phase < 8.0

    def close(self) -> None:
        pass


class MockUltrasonicSensor:
    def __init__(self, near_cm: float = 12.0, far_cm: float = 80.0, active_every_seconds: float = 10.0) -> None:
        self.started = time.monotonic()
        self.near_cm = near_cm
        self.far_cm = far_cm
        self.active_every_seconds = active_every_seconds

    def read_median_cm(self) -> float:
        phase = (time.monotonic() - self.started) % self.active_every_seconds
        if 1.0 <= phase <= 9.0:
            return self.near_cm
        return self.far_cm

    def close(self) -> None:
        pass
