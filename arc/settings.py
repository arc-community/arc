#!/usr/bin/env python3

import os.path
import pydantic


class Settings(pydantic.BaseSettings):
    cache_path: str = os.path.expanduser("~/.arc/cache")
    cell_padding: int = 1
    board_gap: int = 5
    pair_gap: int = 1


settings = Settings()
