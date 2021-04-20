__all__ = [
    "autoloader_factory",
]

import importlib
import inspect
from functools import cached_property
from pathlib import Path
from types import ModuleType
from typing import Any, Dict, Iterator, List, Type, TypeVar

from click import Command, Context, MultiCommand


def load(module: str, recurse: bool = True) -> Iterator[Any]:
    module_instance: ModuleType = importlib.import_module(module)

    for _, member in inspect.getmembers(module_instance):
        yield member

    if not recurse:
        return

    module_path: Path = Path(module_instance.__file__)

    if module_path.name == "__init__.py":
        module_dir: Path = module_path.parent

        for candidate in module_dir.glob("*.py"):
            if candidate.is_file():
                yield from load(f"{module}.{candidate.stem}", recurse=False)

        for candidate in module_dir.glob("*/__init__.py"):
            yield from load(f"{module}.{candidate.parent.name}", recurse=True)


T = TypeVar("T")


def load_instances(t: Type[T], module: str) -> Iterator[T]:
    yield from (candidate for candidate in load(module) if isinstance(candidate, t))


def autoloader_factory(module: str) -> Type[MultiCommand]:
    class CliAutoLoader(MultiCommand):
        @cached_property
        def commands(self) -> Dict[str, Command]:
            return {
                command.name: command for command in load_instances(Command, module)
            }

        def list_commands(self, ctx: Context) -> List[str]:
            return sorted(self.commands.keys())

        def get_command(self, ctx: Context, cmd_name: str) -> Command:
            return self.commands[cmd_name]

    return CliAutoLoader
