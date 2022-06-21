#!/usr/bin/env python3

from pathlib import Path
from typing import Optional

import typer

from arc.utils import dataset

app = typer.Typer()


@app.command()
def main(name: str):
    typer.echo(f"Hello {name}")


@app.command()
def download_arc_dataset(output_dir: Path):
    typer.echo(f"Downloading arc dataset to {output_dir}")
    dataset.download_arc_dataset(output_dir)


@app.command()
def show(
    file: Optional[Path] = typer.Option(None),
    riddle_id: Optional[str] = typer.Option(None),
    random_id: bool = typer.Option(False),
    colored: bool = typer.Option(True),
    solution: bool = typer.Option(False),
    subdir: str = typer.Option("training"),
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
    typer.echo(riddle.fmt(colored=colored, with_test_outputs=solution))


@app.command()
def list():
    typer.echo("\n".join(dataset.get_riddle_ids()))


if __name__ == "__main__":
    app()
