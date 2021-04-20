__all__ = [
    "_run",
]

from subprocess import PIPE, Popen
from typing import IO, AnyStr, Iterator, List, Optional

from click import argument, command, echo, option, secho, style

from iliad.find import find_projects


def io_to_formatted_str(io: IO[AnyStr]) -> Iterator[str]:
    for line in io.readlines():
        if isinstance(line, bytes):
            yield line.decode().rstrip()
        else:
            yield line.rstrip()


class EchoList:
    def __init__(self, n: int):
        self.lines: List[str] = [""] * n
        self.first_time: bool = True

    def reecho(self) -> None:
        if not self.first_time:
            # move cursor to top of lines to be updated
            echo(f"\033[{len(self.lines) + 1}A")
        else:
            self.first_time = False

        for item in self.lines:
            # clear line and print updated text
            echo(f"\r\033[K{item}")

    def __setitem__(self, key: int, value: str) -> None:
        self.lines[key] = value
        self.reecho()


@command("run")
@argument("args", nargs=-1)
@option(
    "--selector",
    "-s",
    default="",
    help="Filter the projects to run the command against using string contains",
)
def _run(args: List[str], selector: str) -> None:
    """
    Runs submodule command using `poetry run` in each project.

    Supports -- for escaping flags.

    Commands are run in parallel, concurrency is not limited.
    """

    projects = {project.label: project.dir for project in find_projects()}

    projects_index = list(
        enumerate(sorted(key for key in projects.keys() if selector in key))
    )

    failed_processes = dict()

    output_lines = EchoList(len(projects_index))

    for idx, project in projects_index:
        output_lines[idx] = f"[{style('initializing', fg='bright_black')}] {project}"

    processes = dict()

    for idx, project in projects_index:
        processes[project] = Popen(
            ["poetry", "run", *args], cwd=projects[project], stdout=PIPE, stderr=PIPE,
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

    del output_lines

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
