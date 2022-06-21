from typing import Optional

import os.path
import pydantic

ARC_DATA_URL = "https://api.github.com/repos/fchollet/ARC/contents/data"


class Settings(pydantic.BaseSettings):
    cache_path: str = os.path.expanduser("~/.arc/cache")
    dataset_dir: Optional[str] = None
    cell_padding: int = 1
    board_gap: int = 5
    pair_gap: int = 1

settings = Settings()

CELL_PADDING_STR = " " * settings.cell_padding
BOARD_GAP_STR = " " * settings.board_gap
PAIR_GAP_STR = "\n" + " " * settings.pair_gap + "\n"
DATASET_DIR = settings.dataset_dir
CACHE_PATH = settings.cache_path
