__all__ = [
    "cli",
]

from pathlib import Path
from typing import Iterator

import click
from click import ClickException
from tomlkit import parse


@click.group()
@click.version_option(message="%(version)s")
def cli() -> None:
    pass


@cli.command("list")
def _list() -> None:
    def project_root() -> Path:
        cwd = Path.cwd()
        while not (cwd / ".git").is_dir():
            if cwd == Path("/"):
                raise ClickException(
                    "Could not find project root (containing .git directory)"
                )

            cwd = cwd.parent

        return cwd

    root = project_root()

    def find_pyprojects() -> Iterator[Path]:
        for match in root.glob("**/pyproject.toml"):
            pyproject = parse(match.read_text())

            if (
                "tool" in pyproject
                and isinstance(pyproject["tool"], dict)
                and "poetry" in pyproject["tool"]
            ):
                yield match

    pyprojects = sorted(list(find_pyprojects()))

    for pyproject in pyprojects:
        click.echo(pyproject.parent.relative_to(root))
