#!/usr/bin/env python3

from arc import TaskData, evaluate_and_report
from arc.agents.cheating_agent import CheatingAgent
from arc.metrics import get_default_metrics
from arc.utils import dataset


def main():
    agent = CheatingAgent()
    metrics = get_default_metrics()
    riddles = dataset.get_riddles(subdirs=["training"])
    task_data = TaskData(topk=3)
    report = evaluate_and_report(agent, riddles, task_data, metrics=metrics)
    print("Correct fraction: ", report.metric_results["correct"].aggregate_result)


if __name__ == "__main__":
    main()
