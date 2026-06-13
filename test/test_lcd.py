#!/usr/bin/env python3
from __future__ import annotations

import argparse
import time

from _bootstrap import DEFAULT_CONFIG
from smart_recycling.config import load_config
from smart_recycling.display import build_display


def main() -> int:
    parser = argparse.ArgumentParser(description="Show a message on LCD")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    parser.add_argument("--message", default="AIoT Ready")
    parser.add_argument("--line2", default="LCD test")
    parser.add_argument("--console", action="store_true")
    args = parser.parse_args()

    display = build_display(load_config(args.config), force_console=args.console)
    try:
        display.show(args.message, args.line2)
        time.sleep(3)
    finally:
        display.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
