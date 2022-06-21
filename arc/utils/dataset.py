#!/usr/bin/env python3

from typing import Optional

import itertools as itt
import random
import json
from pathlib import Path
import requests
from loguru import logger
import tqdm
from concurrent import futures
from arc.utils import cache
from arc.interface import Riddle
from arc.settings import settings

ARC_DATA_URL = "https://api.github.com/repos/fchollet/ARC/contents/data"


def download_arc_dataset(output_dir: Path):
    if not output_dir.exists():
        output_dir.mkdir(parents=True)
    elif not output_dir.is_dir():
        raise ValueError(f"{output_dir} is not a directory")

    for subdir in ["training", "evaluation"]:
        logger.info(f"Downloading {subdir} dataset")
        subdir_path = output_dir / subdir
        if not subdir_path.exists():
            subdir_path.mkdir(parents=True)
        elif not subdir_path.is_dir():
            raise ValueError(f"{subdir_path} is not a directory")

        url = f"{ARC_DATA_URL}/{subdir}"
        items = requests.get(url).json()

        def _download_item(item):
            if not (filename := item["name"]).endswith(".json"):
                logger.warning(f"Skipping {filename}")
                return
            file_path = subdir_path / filename
            logger.info(f"Downloading {file_path}")
            with open(file_path, "wb") as f:
                f.write(requests.get(item["download_url"]).content)

        with futures.ThreadPoolExecutor() as executor:
            for _ in tqdm.tqdm(executor.map(_download_item, items), total=len(items)):
                pass


def get_cached_dataset_dir() -> Path:
    cache_dir = cache.get_cache_dir() / "dataset"
    if not cache_dir.exists():
        with cache.cache_lock:
            if not cache_dir.exists():
                download_arc_dataset(cache_dir)
    return cache_dir


def get_dataset_dir(subdir: Optional[str] = None) -> Path:
    if settings.dataset_dir:
        dataset_dir = Path(settings.dataset_dir)
    else:
        dataset_dir = get_cached_dataset_dir()
    if subdir and subdir != "all":
        dataset_dir = dataset_dir / subdir
    return dataset_dir


def load_riddle_from_file(file_path: Path) -> Riddle:
    json_data = json.loads(file_path.read_text())
    riddle = Riddle(**json_data, riddle_id=file_path.stem)
    return riddle


def get_riddles(subdirs: list[str] = ["training"]) -> dict[str, Path]:
    if not subdirs:
        subdirs = ['all']
    return dict(itt.chain.from_iterable(((s.stem, s) for s in get_dataset_dir(subdir=sd).rglob("*.json")) for sd in subdirs))


def get_riddle_ids(subdirs: list[str] = ["training"]):
    return list(get_riddles(subdirs=subdirs).keys())


def get_random_riddle_id(subdirs: list[str] = ["training"]):
    return random.choice(get_riddle_ids(subdirs=subdirs))


def load_riddle_from_id(riddle_id: str) -> Riddle:
    riddles = get_riddles(subdirs=[])
    riddle_path = riddles[riddle_id]
    return load_riddle_from_file(riddle_path)
