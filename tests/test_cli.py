from textwrap import dedent

from click.testing import CliRunner

from iliad.cli import cli


def test_version(runner: CliRunner) -> None:
    result = runner.invoke(cli, ["--version"], catch_exceptions=False)

    assert result.exit_code == 0
    assert result.output == dedent(
        """\
        0.5.1
        """
    )
