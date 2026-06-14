# ==================================================
# Gachon University
# Introduction to Internet of Things (13966_001)
# 2026-1 Semester Team C
#
# Temperatur and Humidity sensor
# ==================================================
from __future__ import annotations

# DHT11 Temperature and Humidity sensor class
class TempHumiditySensor:
    def __init__(self, pin: int) -> None:
        import adafruit_dht
        import board

        self.pin = pin
        board_pin = getattr(board, f"D{pin}")
        self._sensor = adafruit_dht.DHT11(board_pin)

    def read(self) -> tuple[float, float] | None:
        # return temperature and humidity
        try:
            temp = self._sensor.temperature
            humidity = self._sensor.humidity
            if temp is None or humidity is None:
                return None
            return float(temp), float(humidity)
        
        except Exception as e:
            print(f"[DHT11] Error: {type(e).__name__}: {e}")
            return None

    def close(self) -> None:
        try:
            self._sensor.close()
        except Exception:
            pass