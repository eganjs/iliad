from click.testing import CliRunner
from iliad.cli import cli
from textwrap import dedent

def test_hello_world():
    runner = CliRunner()
    result = runner.invoke(cli)
    assert result.exit_code == 0
    assert result.output == dedent("""\
    Hello, World!
    """)
