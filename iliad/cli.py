__all__ = [
    "main",
]

import click


@click.command()
@click.version_option(prog_name="iliad")
def main() -> None:
    click.echo("Hello, World!")
