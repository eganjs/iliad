from pathlib import Path
from textwrap import dedent

from click.testing import CliRunner

from iliad.cli import cli
from iliad.find import find_root


def test_version() -> None:
    runner = CliRunner()
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


def test_list__success__lists_only_poetry_projects() -> None:
    find_root.cache_clear()

    runner = CliRunner()
    with runner.isolated_filesystem():
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
        alpha
        project/beta
        project/lib/delta
        project/lib/gamma
        """
    )


def test_list__success__respect_gitignore() -> None:
    find_root.cache_clear()

    runner = CliRunner()
    with runner.isolated_filesystem():
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
        project/kappa
        theta
        """
    )


def test_list__fail__cant_find_root() -> None:
    find_root.cache_clear()

    runner = CliRunner()
    with runner.isolated_filesystem():
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
