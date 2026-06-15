# ==================================================
# Gachon University
# Introduction to Internet of Things (13966_001)
# 2026-1 Semester Team C
#
# Term Project config.py
# ==================================================
from __future__ import annotations
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class AppConfig:
    output_dir: Path = Path("~/Pictures/aiot-smart-recycling").expanduser()
    log_path: Path = Path("~/aiot-smart-recycling/events.jsonl").expanduser()
    cooldown_seconds: float = 6.0
    countdown_seconds: int = 3
    stable_required_seconds: float = 1.2
    max_wait_after_motion_seconds: float = 8.0
    poll_interval_seconds: float = 0.12


@dataclass
class CameraConfig:
    enabled: bool = True
    width: int = 320
    height: int = 320
    warmup_seconds: float = 1.0


@dataclass
class YoloConfig:
    model: str = "yolo26s_Finetuned.pt"
    confidence: float = 0.35
    imgsz: int = 224


@dataclass
class DisplayConfig:
    enabled: bool = True
    kind: str = "lcd"
    fallback_console: bool = True


@dataclass
class LcdConfig:
    bus: int = 1
    addresses: list[int] = field(default_factory=lambda: [0x27, 0x3F])
    columns: int = 16
    rows: int = 2


@dataclass
class PirConfig:
    enabled: bool = True
    pin: int = 17


@dataclass
class UltrasonicConfig:
    enabled: bool = True
    trigger_pin: int = 23
    echo_pin: int = 24
    object_distance_cm: float = 35.0
    stable_tolerance_cm: float = 2.5
    samples: int = 5
    sample_delay_seconds: float = 0.06
    timeout_seconds: float = 0.04

@dataclass
class TempHumidityConfig:
    enabled: bool = True
    pin: int = 4
 
 
@dataclass
class BinUltrasonicConfig:
    enabled: bool = True
    trigger_pin: int = 27
    echo_pin: int = 22
    bin_depth_cm: float = 40.0
    full_threshold_cm: float = 10.0
    timeout_seconds: float = 0.04
    samples: int = 5
    sample_delay_seconds: float = 0.06

@dataclass
class LidConfig:
    enabled: bool = True
    pin: int = 18
 
@dataclass
class SensorsConfig:
    pir: PirConfig = field(default_factory=PirConfig)
    ultrasonic: UltrasonicConfig = field(default_factory=UltrasonicConfig)
    temp_humidity: TempHumidityConfig = field(default_factory=TempHumidityConfig)
    bin_ultrasonic: BinUltrasonicConfig = field(default_factory=BinUltrasonicConfig)
    lid: LidConfig = field(default_factory=LidConfig)


@dataclass
class FirebaseConfig:
    enabled: bool = False
    url: str = ""
    timeout_seconds: float = 5.0
    min_interval_seconds: float = 5.0

@dataclass
class Config:
    app: AppConfig = field(default_factory=AppConfig)
    camera: CameraConfig = field(default_factory=CameraConfig)
    yolo: YoloConfig = field(default_factory=YoloConfig)
    display: DisplayConfig = field(default_factory=DisplayConfig)
    lcd: LcdConfig = field(default_factory=LcdConfig)
    sensors: SensorsConfig = field(default_factory=SensorsConfig)
    firebase: FirebaseConfig = field(default_factory=FirebaseConfig)

# Convert a string or Path into an expanded Path object
def _path(value: str | Path) -> Path:
    return Path(value).expanduser()

#I2C addresses
def _int_address(value: str | int) -> int:
    if isinstance(value, int):
        return value
    return int(value, 0)


def _update_dataclass(instance: Any, values: dict[str, Any], path_fields: set[str] | None = None) -> None:
    path_fields = path_fields or set()
    for key, value in values.items():
        if not hasattr(instance, key):
            continue
        if key in path_fields:
            setattr(instance, key, _path(value))
        else:
            setattr(instance, key, value)

# Load and merge settings from a TOML configuration file
def load_config(path: str | Path = "config.toml") -> Config:
    config = Config()
    path = Path(path)
    if not path.exists():
        return config
    config_dir = path.resolve().parent

    with path.open("rb") as handle:
        data = tomllib.load(handle)

    _update_dataclass(config.app, data.get("app", {}), {"output_dir", "log_path"})
    _update_dataclass(config.camera, data.get("camera", {}))
    _update_dataclass(config.yolo, data.get("yolo", {}))
    _update_dataclass(config.display, data.get("display", {}))

    lcd_data = data.get("lcd", {})
    _update_dataclass(config.lcd, {k: v for k, v in lcd_data.items() if k != "addresses"})
    if "addresses" in lcd_data:
        config.lcd.addresses = [_int_address(item) for item in lcd_data["addresses"]]

    sensors_data = data.get("sensors", {})
    _update_dataclass(config.sensors.pir, sensors_data.get("pir", {}))
    _update_dataclass(config.sensors.ultrasonic, sensors_data.get("ultrasonic", {}))
    _update_dataclass(config.sensors.temp_humidity, sensors_data.get("temp_humidity", {}))
    _update_dataclass(config.sensors.bin_ultrasonic, sensors_data.get("bin_ultrasonic", {}))
    _update_dataclass(config.sensors.lid, sensors_data.get("lid", {}))

    _update_dataclass(config.firebase, data.get("firebase", {}))

    model_path = Path(config.yolo.model).expanduser()
    if not model_path.is_absolute():
        candidate = config_dir / model_path
        if candidate.exists():
            config.yolo.model = str(candidate)
    return config
