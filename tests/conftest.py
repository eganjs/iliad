from pathlib import Path
from textwrap import dedent
from typing import Iterator

from click.testing import CliRunner
from pytest import fixture

from iliad.find import find_projects, find_root


@fixture
def runner() -> Iterator[CliRunner]:
    find_root.cache_clear()
    find_projects.cache_clear()

    cli_runner = CliRunner()
    with cli_runner.isolated_filesystem():
        yield cli_runner


def mk_pyproject_at(path: Path) -> Path:
    path.mkdir(parents=True)
    pyprojroot = path / "pyproject.toml"
    pyprojroot.touch()
    return pyprojroot


def mk_poetry_at(path: Path) -> None:
    package_name = path.stem
    mk_pyproject_at(path).write_text(
        dedent(
            f"""\
            [tool.poetry]
            name = "{package_name}"
            version = "0.1.0"
            description = "A package"
            authors = ["A B <a.b@email.com>"]
            license = "MIT"

            [build-system]
            requires = ["poetry-core>=1.0.0"]
            build-backend = "poetry.core.masonry.api"
            """
        )
    )
