from click.testing import CliRunner

from iliad.cli import main


def test_hello_world() -> None:
    runner = CliRunner()
    result = runner.invoke(main)

    assert result.exit_code == 0
    assert result.output == "Hello, World!\n"
