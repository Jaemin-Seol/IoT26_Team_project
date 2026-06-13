from __future__ import annotations


class ConsoleDisplay:
    def show(self, line1: str, line2: str = "") -> None:
        print(f"[DISPLAY] {line1} | {line2}")

    def close(self) -> None:
        pass
