__all__ = [
    "cli",
]

from io import BufferedReader
from subprocess import PIPE, Popen
from typing import IO, AnyStr, Iterator, List, Optional

from click import argument, echo, get_terminal_size, group, secho, style, version_option
from reprint import output

from iliad.find import find_pyprojects


@group()
@version_option(message="%(version)s")
def cli() -> None:
    pass


@cli.command("list")
def _list() -> None:
    for pyproject in find_pyprojects():
        echo("//" + "/".join(pyproject.parent.parts))


def io_to_formatted_str(io: IO[AnyStr]) -> Iterator[str]:
    return (
        (line.decode() if isinstance(line, bytes) else line).rstrip()
        for line in io.readlines()
    )


@cli.command("run")
@argument("args", nargs=-1)
def _run(args: List[str]) -> None:
    projects = {
        "//" + "/".join(pyproject.parent.parts): pyproject
        for pyproject in find_pyprojects()
    }

    projects_index = list(enumerate(sorted(projects.keys())))

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
            for line in io_to_formatted_str(process.stdout):
                echo(f"{prefix} {style(line, fg='blue')}")

            prefix = f"[{style(project + ':stderr', fg='bright_black')}]"
            for line in io_to_formatted_str(process.stderr):
                echo(f"{prefix} {style(line, fg='red')}")
