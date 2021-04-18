__all__ = [
    "cli",
]

from subprocess import PIPE, Popen
from typing import IO, AnyStr, Iterator, List, Optional

from click import argument, echo, group, option, secho, style, version_option
from reprint import output

from iliad.find import find_pyprojects


@group()
@version_option(message="%(version)s")
def cli() -> None:
    pass


@cli.command("list")
def _list() -> None:
    """
    Lists the detected projects.

    Uses // to denote the root of the repo.

    Attempts to respect gitignore files.
    """
    for pyproject in find_pyprojects():
        echo("//" + "/".join(pyproject.parent.parts))


def io_to_formatted_str(io: IO[AnyStr]) -> Iterator[str]:
    for line in io.readlines():
        if isinstance(line, bytes):
            yield line.decode().rstrip()
        else:
            yield line.rstrip()


@cli.command("run")
@argument("args", nargs=-1)
@option(
    "--selector",
    "-s",
    default="",
    help="Filter the projects to run the command against using string contains",
)
def _run(args: List[str], selector: str) -> None:
    """
    Runs a command using `poetry run` in each project.

    Supports -- for escaping flags.

    Commands are run in parallel, concurrency is not limited.
    """

    projects = {
        "//" + "/".join(pyproject.parent.parts): pyproject
        for pyproject in find_pyprojects()
    }

    projects_index = list(
        enumerate(sorted(key for key in projects.keys() if selector in key))
    )

    failed_processes = dict()

    with output(initial_len=len(projects_index)) as output_lines:

        for idx, project in projects_index:
            output_lines[
                idx
            ] = f"[{style('initializing', fg='bright_black')}] {project}"

        processes = dict()

        for idx, project in projects_index:
            processes[project] = Popen(
                ["poetry", "run", *args],
                cwd=projects[project].parent,
                stdout=PIPE,
                stderr=PIPE,
            )
            output_lines[idx] = f"[{style('in progress', fg='blue')}] {project}"

        while processes:
            remaining_processes = dict()

            for idx, project in projects_index:
                if project not in processes:
                    continue

                process = processes[project]

                return_code: Optional[int] = process.poll()
                if return_code is not None:

                    if return_code == 0:
                        output_lines[idx] = f"[{style('done', fg='green')}] {project}"
                    else:
                        output_lines[
                            idx
                        ] = f"[{style(f'failed({return_code})', fg='red')}] {project}"
                        failed_processes[project] = process

                else:
                    remaining_processes[project] = process

            processes = remaining_processes

    if failed_processes:
        secho("\nfailures:", bold=True)

        for project, process in failed_processes.items():
            prefix = f"[{style(project, fg='bright_black')}]"

            echo(f"{prefix} failed with return code {process.returncode}")

            prefix = f"[{style(project + ':stdout', fg='bright_black')}]"
            assert process.stdout is not None
            for line in io_to_formatted_str(process.stdout):
                echo(f"{prefix} {style(line, fg='blue')}")

            prefix = f"[{style(project + ':stderr', fg='bright_black')}]"
            assert process.stderr is not None
            for line in io_to_formatted_str(process.stderr):
                echo(f"{prefix} {style(line, fg='red')}")
