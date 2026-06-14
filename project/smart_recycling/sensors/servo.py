# ==================================================
# Gachon University
# Introduction to Internet of Things (13966_001)
# 2026-1 Semester Team C
#
# Servo motor
# ==================================================

from gpiozero import AngularServo
import time

class ServoLid:
    def __init__(self, pin: int) -> None:
        self._servo = AngularServo(
            pin,
            min_angle=0,
            max_angle=180,
        )

        self.close()

    # Open lid
    def open(self) -> None:
        self._servo.angle = 180
        time.sleep(0.5)
        self._servo.detach()

    # Close lid
    def close(self) -> None:
        self._servo.angle = 0
        time.sleep(0.5)
        self._servo.detach()