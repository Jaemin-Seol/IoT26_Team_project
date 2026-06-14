# ==================================================
# Gachon University
# Introduction to Internet of Things (13966_001)
# 2026-1 Semester Team C
#
# Firebase api
# ==================================================
from __future__ import annotations
import logging
import time
from typing import Any
import requests

logger = logging.getLogger(__name__)

class FirebaseClient:
    """Firebase Realtime Database REST API client."""

    def __init__(self, base_url: str, timeout: float = 5.0, min_interval: float = 5.0) -> None:
        self.base_url = base_url
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
                self.base_url,
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
