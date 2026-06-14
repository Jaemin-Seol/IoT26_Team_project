from __future__ import annotations

import time

# 가짜 센서 코드 (테스트용)
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

class MockTempHumiditySensor:
 
    def __init__(self, temperature: float = 25.0, humidity: float = 60.0) -> None:
        self.temperature = temperature
        self.humidity = humidity
 
    def read(self) -> tuple[float, float]:
        return (self.temperature, self.humidity)
 
    def close(self) -> None:
        pass
 
 
class MockBinUltrasonicSensor:
 
    def __init__(
        self,
        fill_percent: float = 45.0,
        bin_depth_cm: float = 40.0,
        full_threshold_cm: float = 10.0,
    ) -> None:
        self.fill_percent = fill_percent
        self.bin_depth_cm = bin_depth_cm
        self.full_threshold_cm = full_threshold_cm
 
    def read_fill_percent(self) -> float:
        return self.fill_percent
 
    def read_median_cm(self) -> float:
        return self.bin_depth_cm * (1 - self.fill_percent / 100.0)
 
    def is_full(self) -> bool:
        return self.fill_percent >= (
            (1 - self.full_threshold_cm / self.bin_depth_cm) * 100.0
        )
 
    def close(self) -> None:
        pass
