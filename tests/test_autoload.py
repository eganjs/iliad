from click import command
from click.testing import CliRunner

from iliad.autoload import autoloader_factory


def test_autoloader_factory(runner: CliRunner) -> None:
    multicommand_type = autoloader_factory("tests.autoload")

    @command(cls=multicommand_type)
    def cli() -> None:
        pass

    result = runner.invoke(cli)

    assert "module-a-command" in result.output
    assert "module-b-command" in result.output
