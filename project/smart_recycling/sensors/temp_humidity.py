from __future__ import annotations

# DHT11 Temperature and Humidity sensor class
class TempHumiditySensor:

    def __init__(self, pin: int) -> None:
        import pigpio_dht

        self.pin = pin
        self._sensor = pigpio_dht.DHT11(pin)

    def read(self) -> tuple[float, float] | None:
        # return temperature and humidity
        try:
            result = self._sensor.read()
            if not result.get("valid"):
                return None
            return float(result["temp_c"]), float(result["humidity"])
        except Exception:
            # error (sometimes)
            return None

    def close(self) -> None:
        try:
            self._sensor.close()
        except Exception:
            pass