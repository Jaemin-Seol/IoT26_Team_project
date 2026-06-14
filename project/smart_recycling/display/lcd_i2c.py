# ==================================================
# Gachon University
# Introduction to Internet of Things (13966_001)
# 2026-1 Semester Team C
#
# LCD display
# ==================================================
from __future__ import annotations
import time

class I2cLcd:
    ENABLE = 0x04             # Enable signal
    BACKLIGHT = 0x08          # Backlight enabled
    RS = 0x01                 # Register Select (data/command)

    def __init__(self, bus_id: int, address: int, columns: int = 16, rows: int = 2) -> None:
        import smbus2

        self.bus = smbus2.SMBus(bus_id)
        self.address = address
        self.columns = columns
        self.rows = rows
        self._backlight = self.BACKLIGHT
        self._init_lcd()

    def _write_byte(self, value: int) -> None:
        self.bus.write_byte(self.address, value | self._backlight)

    # Pulse the Enable pin to latch data.
    def _pulse(self, value: int) -> None:
        self._write_byte(value | self.ENABLE)
        time.sleep(0.0005)
        self._write_byte(value & ~self.ENABLE)
        time.sleep(0.0001)

    def _write4(self, value: int) -> None:
        self._write_byte(value)
        self._pulse(value)

    # Send an 8-bit value as two 4-bit transfers.
    def _send(self, value: int, mode: int = 0) -> None:
        self._write4((value & 0xF0) | mode)
        self._write4(((value << 4) & 0xF0) | mode)

    def command(self, value: int) -> None:
        self._send(value, 0)

    def write_char(self, value: str) -> None:
        self._send(ord(value), self.RS)

    # Initialize the LCD in 4-bit mode.
    def _init_lcd(self) -> None:
        time.sleep(0.05)
        for value in (0x30, 0x30, 0x30, 0x20):
            self._write4(value)
            time.sleep(0.005)

        self.command(0x28)
        self.command(0x0C)
        self.command(0x06)
        self.clear()

    def clear(self) -> None:
        self.command(0x01)
        time.sleep(0.002)

    # Display text on the LCD.
    def show(self, line1: str, line2: str = "") -> None:
        line1 = _lcd_text(line1, self.columns)
        line2 = _lcd_text(line2, self.columns)

        self.command(0x80)
        for char in line1:
            self.write_char(char)

        if self.rows > 1:
            self.command(0xC0)
            for char in line2:
                self.write_char(char)

    def close(self) -> None:
        try:
            self.clear()
            self.bus.close()
        except Exception:
            pass


# Convert text to LCD-compatible ASCII and fit it to the display width.
def _lcd_text(value: str, columns: int) -> str:
    ascii_text = value.encode("ascii", "replace").decode("ascii")
    return ascii_text[:columns].ljust(columns)