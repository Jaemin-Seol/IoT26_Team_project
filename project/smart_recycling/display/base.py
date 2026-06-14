# ==================================================
# Gachon University
# Introduction to Internet of Things (13966_001)
# 2026-1 Semester Team C
#
# Display protocol
# ==================================================
from __future__ import annotations
from typing import Protocol

class Display(Protocol):
    def show(self, line1: str, line2: str = "") -> None:
        ...

    def close(self) -> None:
        ...
