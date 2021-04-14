__all__ = [
    "cli",
]

from click import echo, group, version_option

from iliad.find import find_pyprojects


@group()
@version_option(message="%(version)s")
def cli() -> None:
    pass


@cli.command("list")
def _list() -> None:
    for pyproject in find_pyprojects():
        echo("/".join(pyproject.parent.parts))
