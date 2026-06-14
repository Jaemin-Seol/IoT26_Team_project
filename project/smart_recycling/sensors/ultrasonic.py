# ==================================================
# Gachon University
# Introduction to Internet of Things (13966_001)
# 2026-1 Semester Team C
#
# Ultrasonic sencor (detecction)
# ==================================================
from __future__ import annotations
import statistics
import time

# Ultrasonic distance sensor control class
class UltrasonicSensor:
    """HC-SR04 distance sensor using BCM pin numbering.

    Echo must be level shifted to 3.3V before reaching Raspberry Pi GPIO.
    """

    def __init__(
        self,
        trigger_pin: int,
        echo_pin: int,
        timeout_seconds: float = 0.04,
        samples: int = 5,
        sample_delay_seconds: float = 0.06,
    ) -> None:
        import RPi.GPIO as GPIO

        self.GPIO = GPIO
        self.trigger_pin = trigger_pin
        self.echo_pin = echo_pin
        self.timeout_seconds = timeout_seconds
        self.samples = max(1, samples)
        self.sample_delay_seconds = sample_delay_seconds

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(trigger_pin, GPIO.OUT)
        GPIO.setup(echo_pin, GPIO.IN)
        GPIO.output(trigger_pin, False)
        time.sleep(0.05)

    # Measure distance in centimeters
    def read_cm(self) -> float | None:
        GPIO = self.GPIO

        GPIO.output(self.trigger_pin, False)
        time.sleep(0.00002)

        GPIO.output(self.trigger_pin, True)
        time.sleep(0.00001)
        GPIO.output(self.trigger_pin, False)

        pulse_start = time.monotonic()
        deadline = time.monotonic() + self.timeout_seconds
        while GPIO.input(self.echo_pin) == 0:
            pulse_start = time.monotonic()
            if pulse_start > deadline:
                return None

        pulse_end = time.monotonic()
        deadline = time.monotonic() + self.timeout_seconds
        while GPIO.input(self.echo_pin) == 1:
            pulse_end = time.monotonic()
            if pulse_end > deadline:
                return None

        duration = pulse_end - pulse_start
        return (duration * 34300.0) / 2.0

    # Return the median of multiple measurements
    def read_median_cm(self) -> float | None:
        values: list[float] = []

        for _ in range(self.samples):
            value = self.read_cm()

            # Keep only valid measurement values
            if value is not None and 1.0 <= value <= 400.0:
                values.append(value)

            time.sleep(self.sample_delay_seconds)

        if not values:
            return None

        return float(statistics.median(values))

    def close(self) -> None:
        try:
            self.GPIO.cleanup((self.trigger_pin, self.echo_pin))
        except Exception:
            pass