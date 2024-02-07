#!/usr/bin/env python
"""
A script to help with running mypy and managing the type ratchet file.

There are three commands:
    - update: Runs mypy and updates the type ratchet file with any changes.
      Prints an error if there are any changes to the ratchet file.

    - force_update: Runs mypy and updates the type ratchet file without checking for changes.

    - check: Runs mypy and checks for changes in the ratchet file without updating it.
"""

import pathlib
import subprocess
import sys
from collections.abc import Sequence

import rich
import typer


RATCHET_FILE = "mypy-ratchet.json"
PARENT_DIR = str(pathlib.Path(__file__).resolve().parent.parent)


app = typer.Typer()


@app.command()
def update() -> None:
    """
    Run mypy and update the type ratchet file with the changes, print errors if any.
    """
    rich.print(f"[bold blue]Running mypy on [white]{PARENT_DIR}[/white].")
    mypy_output = get_mypy_output(PARENT_DIR)

    rich.print(f"[bold blue]Updating type ratchet file: [white]{RATCHET_FILE}[/white].")
    flags = [
        "--color",
        "--diff-old-report",
        RATCHET_FILE,
        "--output-file",
        RATCHET_FILE,
    ]
    result = run_type_ratchet(mypy_output, PARENT_DIR, flags)

    # A return code of 0 means that the report was unchanged
    if result.returncode == 0:
        rich.print("[bold green]Type ratchet file unchanged.")
    # A return code of 3 means that the report was updated.
    elif result.returncode == 3:
        rich.print("[bold yellow]Type ratchet updated. STDOUT was:")
        print(result.stdout)
    # Any other return code is an error.
    else:
        rich.print("[bold red]mypy-json-report failed with the following output:")
        print(result.stderr)

    sys.exit(result.returncode)


@app.command(name="force_update")
def force_update() -> None:
    """
    Run mypy and update the type ratchet file without checking for changes.

    This is useful when there are merge conflicts in the ratchet file.
    """
    rich.print(f"[bold blue]Running mypy on [white]{PARENT_DIR}[/white].")
    mypy_output = get_mypy_output(PARENT_DIR)

    rich.print(
        f"[bold blue]Force-updating ratchet file: [white]{RATCHET_FILE}[/white]."
    )
    flags = ["--output-file", RATCHET_FILE]
    result = run_type_ratchet(mypy_output, PARENT_DIR, flags)

    # The return code of 0 means that the report was updated without error.
    if result.returncode == 0:
        rich.print("[bold green]Type ratchet updated.")
    else:
        rich.print("[bold red]mypy-json-report failed with the following output:")
        print(result.stderr)

    sys.exit(result.returncode)


@app.command()
def check() -> None:
    """
    Check for changing in Mypy's output without updating the ratchet file.

    This is useful for when you're running tests,
    without the intention of committing changes.
    """
    rich.print(f"[bold blue]Running mypy on [white]{PARENT_DIR}[/white].")
    mypy_output = get_mypy_output(PARENT_DIR)

    rich.print(
        f"[bold blue]Comparing against type ratchet file: [white]{RATCHET_FILE}[/white]."
    )
    flags = ["--color", "--diff-old-report", RATCHET_FILE, "--output-file", "/dev/null"]
    result = run_type_ratchet(mypy_output, PARENT_DIR, flags)

    # A return code of 0 means that there were no changes.
    if result.returncode == 0:
        rich.print("[bold green]No changes detected.")
    # A return code of 3 means that the report was updated.
    elif result.returncode == 3:
        rich.print("[bold yellow]Changes detected. STDOUT was:")
        print(result.stdout)
    else:
        rich.print("[bold red]mypy-json-report failed with the following output:")
        print(result.stderr)

    sys.exit(result.returncode)


def get_mypy_output(cwd: str) -> str:
    """Runs mypy and returns the output."""
    result = subprocess.run(
        ["mypy", "."],
        capture_output=True,
        text=True,
        cwd=cwd,
    )
    # Mypy returns 0 if no errors are found, 1 if errors are found, and 2 if it crashes.
    # Checking against 0 and 1 instead of 2 proofs us against mypy adding new exit codes.
    if result.returncode not in {0, 1}:
        rich.print("[bold red]Mypy crashed.")
        rich.print("[bold red]STDERR:")
        print(result.stderr)
        rich.print("[bold red]STDOUT:")
        print(result.stdout)
        sys.exit(result.returncode)
    return result.stdout


def run_type_ratchet(
    mypy_output: str, cwd: str, flags: Sequence[str]
) -> subprocess.CompletedProcess[str]:
    """Calls mypy-json-report with the given flags and mypy output."""
    return subprocess.run(
        ["mypy-json-report", "parse", *flags],
        input=mypy_output,
        cwd=cwd,
        capture_output=True,
        text=True,
    )


if __name__ == "__main__":
    app()
