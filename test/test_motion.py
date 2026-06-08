#!/usr/bin/env python3
from __future__ import annotations

import argparse
import time

from _bootstrap import DEFAULT_CONFIG
from smart_recycling.config import load_config
from smart_recycling.sensors.pir import PirSensor


def main() -> int:
    parser = argparse.ArgumentParser(description="Read PIR motion sensor")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    parser.add_argument("--seconds", type=float, default=15)
    parser.add_argument("--pin", type=int)
    args = parser.parse_args()

    config = load_config(args.config)
    pin = args.pin or config.sensors.pir.pin
    sensor = PirSensor(pin)
    end = time.monotonic() + args.seconds
    try:
        while time.monotonic() < end:
            print(f"[pir] GPIO{pin} motion={int(sensor.is_motion_detected())}")
            time.sleep(0.5)
    finally:
        sensor.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
