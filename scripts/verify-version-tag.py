#!/usr/bin/env python
"""
A script to help with making a new release.

This script verifies that the current commit has a tag,
that the tag matches the version in the `pyproject.toml` file,
and that the tag is in the CHANGELOG.
"""

import pathlib
import subprocess
import sys

import rich
import typer
from packaging.version import InvalidVersion, Version


if sys.version_info >= (3, 11):
    import tomllib
else:
    # We can remove this when we drop support for Python 3.10.
    import tomli as tomllib


PYPROJECT_FILE = pathlib.Path(__file__).resolve().parent.parent / "pyproject.toml"
CHANGELOG_FILE = pathlib.Path(__file__).resolve().parent.parent / "CHANGELOG.md"
app = typer.Typer()


@app.command()
def main() -> None:
    # Get the tags on the current commit.
    tags = (
        subprocess.check_output(["git", "tag", "--points-at", "HEAD"]).decode().split()
    )

    # Find a tag that looks like a version.
    versions: list[Version] = []
    for tag in tags:
        try:
            version = Version(tag)
        except InvalidVersion:
            rich.print(f"[yellow]Skipping non-version tag:[/] {tag}")
        else:
            versions.append(version)

    if not versions:
        rich.print("[red]No version tags found.")
        raise typer.Abort()
    elif len(versions) > 1:
        rich.print(f"[red]Multiple version tags found:[/] {versions}.")
        raise typer.Abort()

    (tag_version,) = versions

    # Get the version from the pyproject.toml file.
    pyproject_content = PYPROJECT_FILE.read_text()
    project_config = tomllib.loads(pyproject_content)
    project_version_str = project_config["project"]["version"]
    project_version = Version(project_version_str)

    # Check that the tag matches the version.
    if tag_version == project_version:
        rich.print("[green]Tag matches version in pyproject.toml.")
    else:
        rich.print("[red]Versions do not match:")
        rich.print(f"  Git tag: {tag_version}")
        rich.print(f"  Package: {project_version}")
        raise typer.Abort()

    # Check that the tag is in the CHANGELOG.
    return_code = subprocess.run(
        ["git", "grep", rf"\bv{tag_version}\b", "HEAD", "--", str(CHANGELOG_FILE)],
    ).returncode
    if return_code == 0:
        rich.print("[green]Tag found in CHANGELOG.")
    else:
        rich.print(f"[red]Tag not committed to CHANGELOG:[/] {tag_version}.")
        raise typer.Abort()


if __name__ == "__main__":
    app()
