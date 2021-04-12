__all__ = [
    "main",
]

import click


@click.command()
@click.version_option(message="%(version)s")
def main() -> None:
    click.echo("Hello, World!")
