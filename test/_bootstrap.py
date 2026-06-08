from __future__ import annotations

import sys
from pathlib import Path


TEST_DIR = Path(__file__).resolve().parent
REPO_ROOT = TEST_DIR.parent

if (REPO_ROOT / "project").is_dir():
    PROJECT_ROOT = REPO_ROOT / "project"
else:
    PROJECT_ROOT = REPO_ROOT

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

DEFAULT_CONFIG = PROJECT_ROOT / "config.toml"
