# ==================================================
# Gachon University
# Introduction to Internet of Things (13966_001)
# 2026-1 Semester Team C
#
# Trashbin ultrasonic sensor (capacity)
# ==================================================
from __future__ import annotations
from smart_recycling.sensors.ultrasonic import UltrasonicSensor

# measure bin dept for capacity
class BinUltrasonicSensor(UltrasonicSensor):

    def __init__(
        self,
        trigger_pin: int,
        echo_pin: int,
        bin_depth_cm: float = 40.0,     # full bin depth
        full_threshold_cm: float = 10.0, # threshold distance
        **kwargs,
    ) -> None:
        super().__init__(trigger_pin=trigger_pin, echo_pin=echo_pin, **kwargs)
        self.bin_depth_cm = bin_depth_cm
        self.full_threshold_cm = full_threshold_cm

    # return estimated fill percentage (0.0 ~ 100.0)
    def read_fill_percent(self) -> float | None:
        """Return fill percentage (0.0 ~ 100.0) or None on failure."""
        distance = self.read_median_cm()
        if distance is None:
            return -1
        filled = self.bin_depth_cm - distance
        percent = (filled / self.bin_depth_cm) * 100.0
        return max(0.0, min(100.0, round(percent, 1)))

    # check whether the bin is considered full
    def is_full(self) -> bool:
        """Return True if bin is considered full."""
        distance = self.read_median_cm()
        if distance is None:
            return False
        return distance <= self.full_threshold_cm