from __future__ import annotations

# Pir Control Class
class PirSensor:
    def __init__(self, pin: int) -> None:
        from gpiozero import MotionSensor
        
        # save pin number 
        self.pin = pin
        self._sensor = MotionSensor(pin)
    
    # detection
    def is_motion_detected(self) -> bool:
        return bool(self._sensor.motion_detected)
    
    def close(self) -> None:
        self._sensor.close()
