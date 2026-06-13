from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

# event log file save class
class EventLogger:
    def __init__(self, path: Path) -> None:
        # file path
        self.path = path
        # if no path, create
        self.path.parent.mkdir(parents=True, exist_ok=True)

    # record event
    def write(self, event: dict[str, Any]) -> None:
        # save timestamp with event log
        payload = {"timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"), **event}
        # Save line by line
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=False) + "\n")
