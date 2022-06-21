#!/usr/bin/env python3

from pathlib import Path

import filelock

from arc.settings import settings


def get_cache_dir(subdir: str = None) -> Path:
    """
    Get the cache directory.

    :param subdir: Subdirectory to create.
    :return: Path to the cache directory.
    """
    cache_dir = Path(settings.cache_path)
    if subdir:
        cache_dir = cache_dir / subdir
    if not cache_dir.exists():
        cache_dir.mkdir(parents=True)
    elif cache_dir.is_file():
        raise FileExistsError(f"{cache_dir} is a file.")
    return cache_dir


cache_lock = filelock.FileLock(str(get_cache_dir() / "lock"))
