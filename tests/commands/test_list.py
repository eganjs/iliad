from pathlib import Path
from textwrap import dedent

from click.testing import CliRunner

from iliad.cli import cli
from tests.conftest import mk_poetry_at, mk_pyproject_at


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
