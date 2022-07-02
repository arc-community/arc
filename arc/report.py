#!/usr/bin/env python3

import datetime
import os
from pathlib import Path

import pydantic

from arc.interface import EvalResultList
from arc.metrics import MetricResultDict


class Report(pydantic.BaseModel):
    eval_result_list: EvalResultList
    meric_result_dict: MetricResultDict = MetricResultDict()
    timestamp: datetime.datetime = pydantic.Field(default_factory=datetime.datetime.now)
    tags: list[str] = []
    subdirs: list[str] = []
    comment: str = ""

    def save_to_file(self, filename: os.PathLike):
        path = Path(filename)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w") as f:
            f.write(self.json())
