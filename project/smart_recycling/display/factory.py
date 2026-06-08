from __future__ import annotations

from pathlib import Path

from smart_recycling.config import Config
from smart_recycling.display.console_display import ConsoleDisplay
from smart_recycling.display.lcd_i2c import I2cLcd


def build_display(config: Config, force_console: bool = False):
    if force_console or not config.display.enabled or config.display.kind == "console":
        return ConsoleDisplay()

    if config.display.kind != "lcd":
        print(f"[WARN] Unknown display kind '{config.display.kind}'. Using console.")
        return ConsoleDisplay()

    bus_path = Path(f"/dev/i2c-{config.lcd.bus}")
    if not bus_path.exists():
        print(f"[WARN] {bus_path} not found. Using console display.")
        return ConsoleDisplay()

    for address in config.lcd.addresses:
        try:
            lcd = I2cLcd(config.lcd.bus, address, config.lcd.columns, config.lcd.rows)
            print(f"[INFO] LCD ready on i2c-{config.lcd.bus} address 0x{address:02x}")
            return lcd
        except Exception as exc:
            print(f"[WARN] LCD address 0x{address:02x} failed: {exc}")

    if config.display.fallback_console:
        print("[WARN] LCD unavailable. Using console display.")
        return ConsoleDisplay()
    raise RuntimeError("LCD unavailable and console fallback disabled")
