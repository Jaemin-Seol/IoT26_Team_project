#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from _bootstrap import DEFAULT_CONFIG
from smart_recycling.config import load_config
from smart_recycling.vision import YoloClassifier


def main() -> int:
    parser = argparse.ArgumentParser(description="Run YOLO on an image or a blank test frame")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    parser.add_argument("--image")
    parser.add_argument("--model")
    args = parser.parse_args()

    import cv2
    import numpy as np

    config = load_config(args.config)
    model_path = args.model or config.yolo.model
    if args.image:
        image = cv2.imread(str(Path(args.image).expanduser()))
        if image is None:
            raise RuntimeError(f"Could not read image: {args.image}")
    else:
        image = np.zeros((480, 640, 3), dtype=np.uint8)

    classifier = YoloClassifier(model_path, config.yolo.confidence, config.yolo.imgsz, config.yolo.top_k)
    result = classifier.classify(image, config.app.output_dir)
    print(f"[model] matched: {result.matched_label}")
    print(f"[model] advice: {result.advice.line1} / {result.advice.line2}")
    print(f"[model] annotated: {result.annotated_path}")
    for detection in result.detections:
        print(f"[detect] {detection.label} {detection.confidence:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
