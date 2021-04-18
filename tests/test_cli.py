from pathlib import Path
from textwrap import dedent
from time import sleep
from typing import Iterator

from click import style
from click.testing import CliRunner
from pytest import fixture

from iliad.cli import cli
from iliad.find import find_root


@fixture
def runner() -> Iterator[CliRunner]:
    find_root.cache_clear()

    cli_runner = CliRunner()
    with cli_runner.isolated_filesystem():
        yield cli_runner


def test_version(runner: CliRunner) -> None:
    result = runner.invoke(cli, ["--version"], catch_exceptions=False)

    assert result.exit_code == 0
    assert result.output == dedent(
        """\
        0.4.0
        """
    )


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


def test_list__lists_only_poetry_projects(runner: CliRunner) -> None:
    (Path.cwd() / ".git").mkdir()
    mk_poetry_at(Path.cwd() / "alpha")
    mk_poetry_at(Path.cwd() / "project" / "beta")
    mk_pyproject_at(Path.cwd() / "project" / "epsilon")
    mk_poetry_at(Path.cwd() / "project" / "lib" / "delta")
    mk_pyproject_at(Path.cwd() / "project" / "lib" / "eta")
    mk_poetry_at(Path.cwd() / "project" / "lib" / "gamma")
    mk_pyproject_at(Path.cwd() / "project" / "lib" / "zeta")

    result = runner.invoke(cli, ["list"], catch_exceptions=False)

    assert result.exit_code == 0
    assert result.output == dedent(
        """\
        //alpha
        //project/beta
        //project/lib/delta
        //project/lib/gamma
        """
    )


def test_list__only_finds_poetry_projects_that_are_not_gitignored(
    runner: CliRunner,
) -> None:
    (Path.cwd() / ".git").mkdir()
    (Path.cwd() / ".gitignore").write_text(".venv\n")
    mk_poetry_at(Path.cwd() / "theta")
    mk_poetry_at(Path.cwd() / ".venv" / "iota")
    mk_poetry_at(Path.cwd() / "project" / "kappa")
    mk_poetry_at(Path.cwd() / "project" / ".venv" / "lambda")

    result = runner.invoke(cli, ["list"], catch_exceptions=False)

    assert result.exit_code == 0
    assert result.output == dedent(
        """\
        //project/kappa
        //theta
        """
    )


def test_list__cant_find_root_when_not_in_git_repo(runner: CliRunner) -> None:
    mk_poetry_at(Path.cwd() / "alpha")
    mk_poetry_at(Path.cwd() / "project" / "beta")
    mk_poetry_at(Path.cwd() / "project" / "lib" / "gamma")
    mk_poetry_at(Path.cwd() / "project" / "lib" / "delta")

    result = runner.invoke(cli, ["list"], catch_exceptions=False)

    assert result.exit_code == 1
    assert result.output == dedent(
        """\
        Error: Could not find project root (containing .git directory)
        """
    )


def test_run__runs_command_for_each_poetry_project(runner: CliRunner) -> None:
    (Path.cwd() / ".git").mkdir()
    mk_poetry_at(Path.cwd() / "alpha")
    mk_poetry_at(Path.cwd() / "beta" / "delta")

    result = runner.invoke(cli, ["run", "touch", "new_file"], catch_exceptions=False)

    assert result.exit_code == 0

    assert f"[{style('done', fg='green')}] //alpha" in result.output
    assert (Path.cwd() / "alpha" / "new_file").is_file()

    assert f"[{style('done', fg='green')}] //beta/delta" in result.output
    assert (Path.cwd() / "beta" / "delta" / "new_file").is_file()


def test_run__prints_output_for_failed_commands(runner: CliRunner) -> None:
    (Path.cwd() / ".git").mkdir()
    mk_poetry_at(Path.cwd() / "alpha")
    (Path.cwd() / "alpha" / "file_only_in_alpha").touch()
    mk_poetry_at(Path.cwd() / "beta" / "delta")

    result = runner.invoke(
        cli, ["run", "ls", "file_only_in_alpha"], catch_exceptions=False
    )

    assert result.exit_code == 0

    assert f"[{style('done', fg='green')}] //alpha" in result.output

    assert f"[{style('failed(2)', fg='red')}] //beta/delta" in result.output

    assert (
        dedent(
            """\
        [//beta/delta] failed with return code 2
        [//beta/delta:stderr] ls: cannot access 'file_only_in_alpha': No such file or directory
        """
        )
        in result.output
    )
