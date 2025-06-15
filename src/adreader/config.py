__all__ = ["config"]

import os
from pathlib import Path
from typing import Any

from dotenv import dotenv_values

DEFAULTS = {
    # LMT variables
    "CHOWN": (int, 0)
}

env = {
    **dotenv_values(Path(os.getenv("ENVFILE", ".env"))),
    **os.environ,
}


for k, v in DEFAULTS.items():
    if isinstance(v, tuple):
        env[k] = v[0](env.get(k, v[1]))
