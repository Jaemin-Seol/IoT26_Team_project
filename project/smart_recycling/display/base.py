from __future__ import annotations

from typing import Protocol


class Display(Protocol):
    def show(self, line1: str, line2: str = "") -> None:
        ...

    def close(self) -> None:
        ...
