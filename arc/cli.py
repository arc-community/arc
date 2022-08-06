#!/usr/bin/env python3

import webbrowser
from importlib import import_module
from pathlib import Path
from typing import Optional

import typer
from matplotlib import pyplot as plt

from arc import TaskData, evaluate_and_report
from arc.metrics import get_all_metrics, get_default_metrics
from arc.settings import settings
from arc.utils import dataset

app = typer.Typer()


@app.command()
def main(name: str):
    typer.echo(f"Hello {name}")


@app.command()
def download_arc_dataset(
    output_dir: Optional[Path] = typer.Option(None),
    inventory_path: Optional[Path] = typer.Option(None),
):
    typer.echo(f"Downloading arc dataset to {output_dir=} from {inventory_path=}")
    dataset.download_arc_dataset(output_dir=output_dir, inventory_path=inventory_path)


@app.command()
def show(
    file: Optional[Path] = typer.Option(None),
    riddle_id: Optional[str] = typer.Option(None),
    random_id: bool = typer.Option(False),
    colored: bool = typer.Option(True),
    solution: bool = typer.Option(False),
    subdir: str = typer.Option("training"),
    output_format: str = typer.Option("term", help="['term', 'arc-game', 'pyplot']"),
    output_path: Optional[Path] = typer.Option(None),
):
    if file:
        riddle = dataset.load_riddle_from_file(file)
    elif riddle_id:
        riddle = dataset.load_riddle_from_id(riddle_id)
    elif random_id:
        riddle = dataset.load_riddle_from_id(
            dataset.get_random_riddle_id(subdirs=[subdir])
        )
    else:
        raise ValueError("Not enough parameters")
    if output_format == "arc-game":
        url = f"https://volotat.github.io/ARC-Game/?task={subdir}%2F{riddle.riddle_id}.json"  # noqa: E501
        webbrowser.open(url)
    elif output_format == "pyplot":
        riddle.fmt_plt(with_test_outputs=solution)
        plt.show()
    elif output_format == "image":
        riddle.fmt_plt(with_test_outputs=solution)
        if output_path is None:
            raise ValueError("Must provide --output-path when saving to image")
        plt.savefig(str(output_path))
    elif output_format == "term":
        typer.echo(riddle.fmt(colored=colored, with_test_outputs=solution))
    else:
        raise ValueError(f"Unknown output format: {output_format}")


@app.command()
def list(
    subdir=typer.Option("training"),
):
    typer.echo("\n".join(dataset.get_riddle_ids(subdirs=[subdir])))


@app.command()
def eval(
    agent_path: str,
    topk: int = typer.Option(settings.default_topk),
    default_metrics: bool = typer.Option(True),
    all_metrics: bool = typer.Option(False),
    subdir: str = typer.Option("training"),
):
    typer.echo(f"Evaluating {agent_path} on {subdir}")
    agent_module_name, agent_classname = agent_path.split(":")
    module = import_module(agent_module_name)
    agent_class = getattr(module, agent_classname)
    agent = agent_class()

    riddles = dataset.get_riddles(subdirs=[subdir])
    task_data = TaskData(topk=topk)
    metrics = get_default_metrics() if default_metrics else []
    if all_metrics:
        metrics = get_all_metrics()
    report = evaluate_and_report(agent, riddles, task_data, metrics)
    print(report.fmt_txt())


if __name__ == "__main__":
    app()
