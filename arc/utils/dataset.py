#!/usr/bin/env python3

import itertools as itt
import json
import os
import random
from concurrent import futures
from pathlib import Path
from typing import Optional

import requests
import tqdm
import yaml
from loguru import logger

from arc.interface import Riddle
from arc.settings import settings
from arc.utils import cache

DEFAULT_INVENTORY_FN = "default_inventory.yaml"


def download_arc_dataset(
    output_dir: Optional[os.PathLike] = None,
    inventory_path: Optional[os.PathLike] = None,
):
    if output_dir is None:
        output_dir = get_cached_dataset_dir()
    output_dir = Path(output_dir)
    if not output_dir.exists():
        output_dir.mkdir(parents=True)
    elif not output_dir.is_dir():
        raise ValueError(f"{output_dir} is not a directory")

    if inventory_path is None:
        inventory_dir = Path(__file__).parent
        while inventory_path := inventory_dir / DEFAULT_INVENTORY_FN:
            if inventory_path.exists() and inventory_path.is_file():
                break
            if inventory_dir == Path("/"):
                raise ValueError(
                    f"Could not find {DEFAULT_INVENTORY_FN=} in parents of {__file__}"
                )
            inventory_dir = inventory_dir.parent

    inventory_path = Path(inventory_path)

    with inventory_path.open() as f:
        inventory = yaml.safe_load(f)

    for subdir, subdir_data in inventory["subsets"].items():
        logger.info(f"Downloading {subdir} dataset")
        subdir_path = output_dir / subdir
        if not subdir_path.exists():
            subdir_path.mkdir(parents=True)
        elif not subdir_path.is_dir():
            raise ValueError(f"{subdir_path} is not a directory")

        url = subdir_data["github_api_url"]
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


def get_cached_dataset_dir(not_exist_ok=False) -> Path:
    cache_dir = cache.get_cache_dir() / "dataset"
    if not cache_dir.exists():
        if not_exist_ok:
            logger.warning(f"{cache_dir=} does not exist.")
        else:
            raise ValueError(
                f"{cache_dir=} does not exist."
                "maybe run arc download-arc-dataset first."
            )
    return cache_dir


def get_dataset_dir(subdir: Optional[str] = None) -> Path:
    if settings.dataset_dir:
        dataset_dir = Path(settings.dataset_dir)
    else:
        dataset_dir = get_cached_dataset_dir()
    if subdir and subdir != "all":
        dataset_dir = dataset_dir / subdir
    return dataset_dir


def load_riddle_from_file(file_path: os.PathLike) -> Riddle:
    file_path = Path(file_path)
    json_data = json.loads(file_path.read_text())
    riddle = Riddle(**json_data, riddle_id=file_path.stem, subdir=file_path.parent.name)
    return riddle


def get_riddle_paths(subdirs: list[str] = ["training"]) -> dict[str, Path]:
    if not subdirs:
        subdirs = ["all"]
    return dict(
        itt.chain.from_iterable(
            ((s.stem, s) for s in get_dataset_dir(subdir=sd).rglob("*.json"))
            for sd in subdirs
        )
    )


def get_riddle_ids(subdirs: list[str] = ["training"]):
    return list(sorted(get_riddle_paths(subdirs=subdirs).keys()))


def get_riddles(subdirs: list[str] = ["training"]) -> list[Riddle]:
    logger.info(f"Loading riddles from {subdirs}")
    return [
        load_riddle_from_file(riddle_path)
        for riddle_path in get_riddle_paths(subdirs=subdirs).values()
    ]


def get_random_riddle_id(subdirs: list[str] = ["training"]):
    return random.choice(get_riddle_ids(subdirs=subdirs))


def load_riddle_from_id(riddle_id: str) -> Riddle:
    riddles = get_riddle_paths(subdirs=[])
    riddle_path = riddles[riddle_id]
    return load_riddle_from_file(riddle_path)
