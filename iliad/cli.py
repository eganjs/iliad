__all__ = [
    "cli",
]

from click import command, version_option

from iliad.autoload import autoloader_factory


@command(cls=autoloader_factory("iliad.commands"))
@version_option(message="%(version)s")
def cli() -> None:
    pass
