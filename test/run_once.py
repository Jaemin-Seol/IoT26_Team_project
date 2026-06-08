#!/usr/bin/env python3
from __future__ import annotations

from _bootstrap import DEFAULT_CONFIG
from smart_recycling.app import main


if __name__ == "__main__":
    raise SystemExit(main(["--config", str(DEFAULT_CONFIG), "--once", "--no-lcd"]))
