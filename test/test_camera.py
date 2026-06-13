#!/usr/bin/env python3
from __future__ import annotations

import argparse

from _bootstrap import DEFAULT_CONFIG
from smart_recycling.camera import PiCamera
from smart_recycling.config import load_config


def main() -> int:
    parser = argparse.ArgumentParser(description="Capture one image with Pi Camera")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    args = parser.parse_args()

    config = load_config(args.config)
    cameras = PiCamera.list_cameras()
    print(f"[camera] available: {cameras}")
    if not cameras:
        print("[camera] no camera detected")
        return 1

    camera = PiCamera(config.camera.width, config.camera.height, config.camera.warmup_seconds)
    frame, path = camera.capture(config.app.output_dir)
    print(f"[camera] saved: {path}")
    print(f"[camera] shape: {getattr(frame, 'shape', None)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
