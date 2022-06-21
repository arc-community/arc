from setuptools import find_packages, setup

setup(
    name="arc",
    author="yk",
    version="0.1",
    install_requires=[
        "numpy",
        "typer[all]",
        "requests",
        "loguru",
        "tqdm",
        "pydantic",
        "filelock",
        "colored",
    ],
    extras_require={
        "dev": [
            "black",
            "pytest",
        ],
    },
    packages=["arc"] + ["arc." + pkg for pkg in find_packages("arc")],
    entry_points={
        "console_scripts": [
            "arc=arc.cli:app",
        ]
    },
)
