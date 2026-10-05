"""Command-line interface."""

from pathlib import Path

import typer

from .pipeline import run_pipeline
from .settings import Settings


app = typer.Typer(help="Build and validate the CMS hospital benchmark warehouse.")


@app.command()
def refresh(
    skip_extract: bool = typer.Option(False, help="Reuse existing raw Parquet snapshots."),
) -> None:
    project_root = Path.cwd()
    summary = run_pipeline(Settings(), project_root, extract=not skip_extract)
    typer.echo(
        f"Completed in {summary['duration_seconds']}s; "
        f"hospital mart rows={summary['mart_rows']['mart_hospital_benchmark']}"
    )


if __name__ == "__main__":
    app()

