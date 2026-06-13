from __future__ import annotations

import argparse
import sys
import time
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

from smart_recycling.camera import PiCamera
from smart_recycling.config import Config, load_config
from smart_recycling.display import build_display
from smart_recycling.sensors import SensorSuite, build_sensors
from smart_recycling.storage import EventLogger, FirebaseClient
from smart_recycling.vision import YoloClassifier


class RecyclingApp:
    def __init__(
        self,
        config: Config,
        no_lcd: bool = False,
        mock_sensors: bool = False,
        enable_sensors: bool = True,
    ) -> None:
        self.config = config
        self.display = build_display(config, force_console=no_lcd)
        self.sensors = build_sensors(config, mock=mock_sensors) if enable_sensors else SensorSuite()
        self.camera = PiCamera(
            width=config.camera.width,
            height=config.camera.height,
            warmup_seconds=config.camera.warmup_seconds,
        )
        self.classifier = YoloClassifier(
            model_path=config.yolo.model,
            confidence=config.yolo.confidence,
            imgsz=config.yolo.imgsz,
            top_k=config.yolo.top_k,
        )
        self.logger = EventLogger(config.app.log_path)
        # firebase
        self.firebase: FirebaseClient | None = (
            FirebaseClient(
                config.firebase.url,
                config.firebase.timeout_seconds,
                config.firebase.min_interval_seconds,
            )
            if config.firebase.enabled and config.firebase.url
            else None
        )
        self._waste_counts: dict[str, int] = {}
        self._total_count: int = 0

    def close(self) -> None:
        self.sensors.close()
        self.display.close()

    def run_once(self, image_path: str | None = None) -> None:
        if image_path:
            image, raw_path = self._load_image(Path(image_path).expanduser())
        else:
            self.display.show("Capturing", "Please wait")
            image, raw_path = self.camera.capture(self.config.app.output_dir)
        self._classify_and_report(image, raw_path, sensor_snapshot={})

    # Main runtime loop for sensor-driven classification
    def run_forever(self) -> None:
        if not self.sensors.pir and not self.sensors.ultrasonic:
            raise RuntimeError("No sensors enabled. Use --once or --mock-sensors, or enable sensors in config.toml.")

        self.display.show("Ready", "Place item")
        print("[INFO] System ready. Press Ctrl-C to stop.")
        try:
            while True:
                candidate = self._wait_for_candidate()
                if candidate is None:
                    continue
                if not self._countdown_with_recheck():
                    self.display.show("Cancelled", "Item moved")
                    print("[INFO] Capture cancelled because the item moved.")
                    time.sleep(1.0)
                    self.display.show("Ready", "Place item")
                    continue

                image, raw_path = self.camera.capture(self.config.app.output_dir)
                self._classify_and_report(image, raw_path, sensor_snapshot=candidate)
                time.sleep(self.config.app.cooldown_seconds)
                self.display.show("Ready", "Place item")
        except KeyboardInterrupt:
            print("\n[INFO] stopped")

    # Wait until motion and a valid target object are detected
    def _wait_for_candidate(self) -> dict | None:
        pir = self.sensors.pir
        ultrasonic = self.sensors.ultrasonic
        config = self.config

        while True:
            if pir is not None and not pir.is_motion_detected():
                time.sleep(config.app.poll_interval_seconds)
                continue

            if pir is not None:
                print("[INFO] Motion detected. Checking target area.")
                self.display.show("Motion", "Checking area")

            if ultrasonic is None:
                return {"pir_motion": True, "distance_cm": None, "stable": True}

            stable = self._wait_for_stable_object()
            if stable is not None and stable.get("stable"):
                return stable

            print("[INFO] Motion seen, but no stable object in target area.")
            self.display.show("No item", "Try again")
            time.sleep(1.0)
            self.display.show("Ready", "Place item")
    
    # Verify that the object remains stable before capture
    def _wait_for_stable_object(self) -> dict | None:
        cfg = self.config.sensors.ultrasonic
        deadline = time.monotonic() + self.config.app.max_wait_after_motion_seconds
        stable_since: float | None = None
        last_distance: float | None = None
        stable_distance: float | None = None

        while time.monotonic() < deadline:
            distance = self.sensors.ultrasonic.read_median_cm()
            if distance is None:
                stable_since = None
                time.sleep(self.config.app.poll_interval_seconds)
                continue

            object_near = distance <= cfg.object_distance_cm
            steady = last_distance is None or abs(distance - last_distance) <= cfg.stable_tolerance_cm
            print(f"[SENSOR] distance={distance:.1f}cm near={object_near} steady={steady}")

            if object_near and steady:
                if stable_since is None:
                    stable_since = time.monotonic()
                stable_distance = distance
                if time.monotonic() - stable_since >= self.config.app.stable_required_seconds:
                    self.display.show("Item detected", f"{distance:.1f} cm")
                    return {
                        "pir_motion": self.sensors.pir.is_motion_detected() if self.sensors.pir else None,
                        "distance_cm": round(distance, 2),
                        "stable": True,
                    }
            else:
                stable_since = None

            last_distance = distance
            time.sleep(self.config.app.poll_interval_seconds)

        return {
            "pir_motion": self.sensors.pir.is_motion_detected() if self.sensors.pir else None,
            "distance_cm": round(stable_distance, 2) if stable_distance else None,
            "stable": False,
        } if stable_distance is not None else None
    
    # Recheck object presence during the capture countdown
    def _countdown_with_recheck(self) -> bool:
        ultrasonic = self.sensors.ultrasonic
        threshold = self.config.sensors.ultrasonic.object_distance_cm
        for number in range(self.config.app.countdown_seconds, 0, -1):
            self.display.show("Hold still", f"Capture in {number}")
            print(f"[INFO] Capture in {number}")
            time.sleep(1.0)
            if ultrasonic is not None:
                distance = ultrasonic.read_median_cm()
                if distance is None or distance > threshold:
                    return False
        self.display.show("Capturing", "Do not move")
        return True
    
    # Read temp/humidity and bin fill level at the moment of classification
    def _read_environment_snapshot(self) -> dict:
        snapshot = {}
 
        if self.sensors.temp_humidity is not None:
            reading = self.sensors.temp_humidity.read()
            if reading is not None:
                temp, humidity = reading
                snapshot["temperature_c"] = temp
                snapshot["humidity_pct"] = humidity
                print(f"[SENSOR] temp={temp}°C humidity={humidity}%")
            else:
                print("[SENSOR] temp_humidity read failed")
 
        if self.sensors.bin_ultrasonic is not None:
            fill = self.sensors.bin_ultrasonic.read_fill_percent()
            is_full = self.sensors.bin_ultrasonic.is_full()
            snapshot["bin_fill_pct"] = fill
            snapshot["bin_is_full"] = is_full
            print(f"[SENSOR] bin_fill={fill}% full={is_full}")
 
        return snapshot
 

    # Run inference, display the result, and save an event log
    def _classify_and_report(self, image, raw_path: Path, sensor_snapshot: dict) -> None:
        self.display.show("AI checking", "Please wait")
        result = self.classifier.classify(image, self.config.app.output_dir)
        env = self._read_environment_snapshot()
        # if bin is full print it on lcd
        if env.get("bin_is_full"):
            self.display.show("Bin is FULL", "Please empty!")
            print("[WARN] Bin is full!")
            time.sleep(2.0)
        self.display.show(result.advice.line1, result.advice.line2)
        print(f"[RESULT] {result.advice.line1} / {result.advice.line2}")
        print(f"[INFO] image: {raw_path}")
        print(f"[INFO] annotated: {result.annotated_path}")
        for detection in result.detections:
            print(f"[DETECT] {detection.label} {detection.confidence:.2f}")

        self.logger.write(
            {
                "image_path": str(raw_path),
                "annotated_path": str(result.annotated_path),
                "matched_label": result.matched_label,
                "advice": asdict(result.advice),
                "detections": [asdict(item) for item in result.detections],
                "sensors": sensor_snapshot,
                "environment": env,
            }
        )

        if result.matched_label:
            key = result.advice.line1
            self._waste_counts[key] = self._waste_counts.get(key, 0) + 1
            self._total_count += 1
        
        # send data
        if self.firebase is not None:
            record = {
                "timestamp": datetime.now().isoformat(timespec="seconds"),
                "temperature": env.get("temperature_c"),
                "humidity": env.get("humidity_pct"),
                "capacity": env.get("bin_fill_pct"),
                "total_count": self._total_count,
                "waste_types": dict(self._waste_counts),
            }
            self.firebase.push_record(record)
    # Load an existing image from disk
    @staticmethod
    def _load_image(path: Path):
        import cv2

        image = cv2.imread(str(path))
        if image is None:
            raise RuntimeError(f"Could not read image: {path}")
        return image, path


# Parse command-line options
def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="AIoT Smart Recycling System")
    parser.add_argument("--config", default="config.toml")
    parser.add_argument("--once", action="store_true", help="Capture and classify once now")
    parser.add_argument("--image", help="Classify an existing image instead of using the camera")
    parser.add_argument("--no-lcd", action="store_true", help="Use console display instead of I2C LCD")
    parser.add_argument("--mock-sensors", action="store_true", help="Use simulated PIR and ultrasonic sensors")
    parser.add_argument("--model", help="Override YOLO model path")
    parser.add_argument("--confidence", type=float, help="Override YOLO confidence threshold")
    parser.add_argument("--disable-pir", action="store_true")
    parser.add_argument("--disable-ultrasonic", action="store_true")
    parser.add_argument("--disable-temp-humidity", action="store_true")
    parser.add_argument("--disable-bin-ultrasonic", action="store_true")
    return parser.parse_args(argv)

# Application entry point
def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    config = load_config(args.config)
    if args.model:
        config.yolo.model = args.model
    if args.confidence is not None:
        config.yolo.confidence = args.confidence
    if args.disable_pir:
        config.sensors.pir.enabled = False
    if args.disable_ultrasonic:
        config.sensors.ultrasonic.enabled = False
    if args.disable_temp_humidity:
        config.sensors.temp_humidity.enabled = False
    if args.disable_bin_ultrasonic:
        config.sensors.bin_ultrasonic.enabled = False

    enable_sensors = not (args.once or args.image) or args.mock_sensors
    app = RecyclingApp(
        config,
        no_lcd=args.no_lcd,
        mock_sensors=args.mock_sensors,
        enable_sensors=enable_sensors,
    )
    try:
        if args.once or args.image:
            app.run_once(args.image)
        else:
            app.run_forever()
    except Exception as exc:
        print(f"[ERROR] {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    finally:
        app.close()
    return 0
