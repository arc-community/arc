#!/usr/bin/env python3

from typing import Optional

import os.path
import pydantic


class Settings(pydantic.BaseSettings):
    cache_path: str = os.path.expanduser("~/.arc/cache")
    dataset_dir: Optional[str] = None
    cell_padding: int = 1
    board_gap: int = 5
    pair_gap: int = 1


settings = Settings()
