#!/usr/bin/env python3
from __future__ import annotations

import argparse
import time

from _bootstrap import DEFAULT_CONFIG
from smart_recycling.config import load_config
from smart_recycling.sensors.ultrasonic import UltrasonicSensor


def main() -> int:
    parser = argparse.ArgumentParser(description="Read ultrasonic distance sensor")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    parser.add_argument("--seconds", type=float, default=15)
    parser.add_argument("--trigger-pin", type=int)
    parser.add_argument("--echo-pin", type=int)
    args = parser.parse_args()

    config = load_config(args.config)
    trig = args.trigger_pin or config.sensors.ultrasonic.trigger_pin
    echo = args.echo_pin or config.sensors.ultrasonic.echo_pin
    sensor = UltrasonicSensor(
        trigger_pin=trig,
        echo_pin=echo,
        timeout_seconds=config.sensors.ultrasonic.timeout_seconds,
        samples=config.sensors.ultrasonic.samples,
        sample_delay_seconds=config.sensors.ultrasonic.sample_delay_seconds,
    )
    end = time.monotonic() + args.seconds
    try:
        while time.monotonic() < end:
            distance = sensor.read_median_cm()
            print(f"[ultrasonic] trig={trig} echo={echo} distance_cm={distance}")
            time.sleep(0.5)
    finally:
        sensor.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
