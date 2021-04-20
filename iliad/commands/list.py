__all__ = [
    "_list",
]

from click import command, echo

from iliad.find import find_projects


@command("list")
def _list() -> None:
    """
    Lists the detected projects.

    Uses // to denote the root of the repo.

    Attempts to respect gitignore files.
    """
    for project in find_projects():
        echo(project.label)
