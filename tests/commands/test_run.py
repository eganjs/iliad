from pathlib import Path
from subprocess import PIPE, run
from uuid import uuid4

from click.testing import CliRunner

from iliad.cli import cli
from tests.conftest import mk_poetry_at


def test_run__runs_command_for_each_poetry_project(runner: CliRunner) -> None:
    (Path.cwd() / ".git").mkdir()
    mk_poetry_at(Path.cwd() / "alpha")
    mk_poetry_at(Path.cwd() / "beta" / "delta")

    result = runner.invoke(cli, ["run", "touch", "new_file"], catch_exceptions=False)

    assert result.exit_code == 0

    assert "[done] //alpha" in result.output
    assert (Path.cwd() / "alpha" / "new_file").is_file()

    assert "[done] //beta/delta" in result.output
    assert (Path.cwd() / "beta" / "delta" / "new_file").is_file()


def test_run__prints_output_for_failed_commands(runner: CliRunner) -> None:
    (Path.cwd() / ".git").mkdir()
    mk_poetry_at(Path.cwd() / "alpha")
    (Path.cwd() / "alpha" / "file_only_in_alpha").touch()
    mk_poetry_at(Path.cwd() / "beta" / "delta")

    result = runner.invoke(
        cli, ["run", "ls", "file_only_in_alpha"], catch_exceptions=False
    )

    expected_exit_code = run(["ls", str(uuid4())], stdout=PIPE, stderr=PIPE).returncode

    assert result.exit_code == 0

    assert "[done] //alpha" in result.output

    assert f"[failed({expected_exit_code})] //beta/delta" in result.output

    assert (
        f"[//beta/delta] failed with return code {expected_exit_code}" in result.output
    )
    assert (
        # linux and windows
        "[//beta/delta:stderr] ls: cannot access 'file_only_in_alpha': No such file or directory"
        in result.output
        or
        # macos
        "[//beta/delta:stderr] ls: file_only_in_alpha: No such file or directory"
        in result.output
    )


def test_run__only_runs_command_for_projects_matching_selector(
    runner: CliRunner,
) -> None:
    (Path.cwd() / ".git").mkdir()
    mk_poetry_at(Path.cwd() / "alpha")
    mk_poetry_at(Path.cwd() / "beta" / "delta")
    mk_poetry_at(Path.cwd() / "beta" / "gamma")

    result = runner.invoke(cli, ["run", "-s", "beta", "echo"], catch_exceptions=False)

    assert result.exit_code == 0

    assert "[done] //alpha" not in result.output
    assert "[done] //beta/delta" in result.output
    assert "[done] //beta/gamma" in result.output
