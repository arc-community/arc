#!/usr/bin/env python3

import datetime
import os
from pathlib import Path

import pydantic
import tabulate

from arc.interface import EvalResultList
from arc.metrics import MetricResultDict


class Report(pydantic.BaseModel):
    eval_results: EvalResultList
    metric_results: MetricResultDict = MetricResultDict()
    timestamp: datetime.datetime = pydantic.Field(default_factory=datetime.datetime.now)
    tags: list[str] = []
    subdirs: list[str] = []
    comment: str = ""

    def save_to_file(self, filename: os.PathLike):
        path = Path(filename)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w") as f:
            f.write(self.json())

    def fmt_txt(self):
        lines = []
        aggregation_rows = [
            [k, v.aggregate_result]
            for k, v in self.metric_results.items()
            if v.aggregate_result is not None
        ]
        aggragation_table = tabulate.tabulate(
            aggregation_rows, headers=["Metric", "Value"]
        )
        lines.append("Aggregation results:")
        lines.append(aggragation_table)
        return "\n".join(lines)
