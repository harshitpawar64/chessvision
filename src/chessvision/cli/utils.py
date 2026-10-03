import logging

import typer


def setup_logging(verbose: bool = False) -> None:
    if not verbose:
        return

    logger = logging.getLogger("chessvision")
    logger.setLevel(logging.DEBUG)

    if any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
        return

    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(logging.Formatter("%(levelname)s [%(name)s]: %(message)s"))

    logger.addHandler(handler)


def report_validation_errors(errors: dict[str, list[str]], total_boards: int) -> None:
    if not errors:
        return

    if total_boards == 1:
        board_errors = next(iter(errors.values()))
        typer.secho(
            f"Illegal position detected: {', '.join(board_errors)}.",
            fg=typer.colors.YELLOW,
            err=True,
        )
        return

    count = len(errors)
    max_display = 10

    typer.secho(
        f"\nIllegal position{'s' if count > 1 else ''} detected:",
        fg=typer.colors.YELLOW,
        err=True,
    )
    for label, validation_errors in list(errors.items())[:max_display]:
        typer.secho(
            f"  - {label}: {', '.join(validation_errors)}",
            fg=typer.colors.YELLOW,
            err=True,
        )
    if count > max_display:
        typer.secho(
            f"  ... and {count - max_display} more.", fg=typer.colors.YELLOW, err=True
        )
