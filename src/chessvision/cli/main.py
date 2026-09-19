from typing import Annotated

import typer

from chessvision import __version__
from chessvision.cli.board import board
from chessvision.cli.pdf import pdf
from chessvision.cli.square import square

app = typer.Typer()

app.command()(square)
app.command()(board)
app.command()(pdf)


def version_callback(value: bool) -> None:
    if value:
        print(f"chessvision {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        bool,
        typer.Option(
            "--version",
            "-V",
            callback=version_callback,
            is_eager=True,
            help="Show version and exit.",
        ),
    ] = False,
) -> None: ...
