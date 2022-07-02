#!/usr/bin/env python3

from arc import TaskData, evaluate_and_report, get_default_metrics
from arc.agents.dummy_agents import CheatingAgent
from arc.metrics import InverseRankOfCorrectMetric
from arc.utils import dataset


def main():
    agent = CheatingAgent()
    metrics = [*get_default_metrics(), InverseRankOfCorrectMetric()]
    riddles = dataset.get_riddles(subdirs=["training"])
    task_data = TaskData()
    report = evaluate_and_report(agent, riddles, task_data, metrics=metrics)
    print(report.fmt_txt())


if __name__ == "__main__":
    main()
