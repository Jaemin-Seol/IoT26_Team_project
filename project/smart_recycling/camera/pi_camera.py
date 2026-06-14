# ==================================================
# Gachon University
# Introduction to Internet of Things (13966_001)
# 2026-1 Semester Team C
#
# Camera
# ==================================================
from __future__ import annotations
import time
from pathlib import Path

class PiCamera:
    def __init__(self, width: int = 1280, height: int = 720, warmup_seconds: float = 1.0) -> None:
        self.width = width
        self.height = height
        self.warmup_seconds = warmup_seconds

    @staticmethod
    def list_cameras() -> list[dict]:
        from picamera2 import Picamera2

        return Picamera2.global_camera_info()

    # Take photo
    def capture(self, output_dir: Path):
        import cv2
        from picamera2 import Picamera2

        # Create output directory if it doesn't exist.
        output_dir.mkdir(parents=True, exist_ok=True)

        # Generate a timestamped filename.
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        image_path = output_dir / f"capture_{timestamp}.jpg"

        picam2 = Picamera2()
        config = picam2.create_still_configuration(
            main={"size": (self.width, self.height), "format": "RGB888"}
        )

        # Start the camera and allow it to warm up.
        picam2.configure(config)
        picam2.start()
        time.sleep(self.warmup_seconds)

        frame_rgb = picam2.capture_array()

        picam2.stop()
        picam2.close()

        # Convert RGB to BGR for OpenCV compatibility.
        # frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)

        # Save the captured image.
        cv2.imwrite(str(image_path), frame_rgb)

        return frame_rgb, image_path