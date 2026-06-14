from __future__ import annotations

import logging
import time
from typing import Any

import requests

logger = logging.getLogger(__name__)


class FirebaseClient:
    """Firebase Realtime Database REST API client."""

    def __init__(self, base_url: str, timeout: float = 5.0, min_interval: float = 5.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.min_interval = min_interval
        self._last_push: float = 0.0

    def push_record(self, record: dict[str, Any]) -> bool:
        """POST to /dashboard/records.json — Firebase assigns an auto-generated key."""
        now = time.monotonic()
        if now - self._last_push < self.min_interval:
            logger.debug("[Firebase] skipped — %.1fs since last push", now - self._last_push)
            return False

        try:
            resp = requests.post(
                f"{self.base_url}/dashboard/records.json",
                json=record,
                timeout=self.timeout,
            )
            resp.raise_for_status()
            self._last_push = now
            logger.info("[Firebase] record pushed: %s", resp.json().get("name"))
            return True
        except requests.RequestException as exc:
            logger.warning("[Firebase] push_record failed: %s", exc)
            return False

    def update_summary(self, data: dict[str, Any]) -> bool:
        """PATCH /dashboard/summary.json with latest aggregate stats."""
        try:
            resp = requests.patch(
                f"{self.base_url}/dashboard/summary.json",
                json=data,
                timeout=self.timeout,
            )
            resp.raise_for_status()
            return True
        except requests.RequestException as exc:
            logger.warning("[Firebase] update_summary failed: %s", exc)
            return False
