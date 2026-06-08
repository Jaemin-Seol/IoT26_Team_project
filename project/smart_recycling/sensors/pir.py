from __future__ import annotations


class PirSensor:
    def __init__(self, pin: int) -> None:
        from gpiozero import MotionSensor

        self.pin = pin
        self._sensor = MotionSensor(pin)

    def is_motion_detected(self) -> bool:
        return bool(self._sensor.motion_detected)

    def close(self) -> None:
        self._sensor.close()
