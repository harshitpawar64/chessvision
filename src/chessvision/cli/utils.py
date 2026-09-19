import typer


def report_illegal_positions(errors: dict[int, list[str]], total_boards: int) -> None:
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
    for board_num, validation_errors in list(errors.items())[:max_display]:
        typer.secho(
            f"  - Board #{board_num}: {', '.join(validation_errors)}",
            fg=typer.colors.YELLOW,
            err=True,
        )
    if count > max_display:
        typer.secho(
            f"  ... and {count - max_display} more.", fg=typer.colors.YELLOW, err=True
        )
