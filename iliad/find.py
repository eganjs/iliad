__all__ = [
    "find_root",
    "PoetryProject",
    "find_projects",
]

from fnmatch import fnmatch
from functools import lru_cache
from pathlib import Path
from typing import Callable, Dict, Iterator, List

from click import ClickException
from tomlkit import parse
from typing_extensions import Final


@lru_cache(maxsize=1)
def find_root() -> Path:
    candidate = Path.cwd()
    while not (candidate / ".git").is_dir():
        if not candidate.parents:
            raise ClickException(
                "Could not find project root (containing .git directory)"
            )

        candidate = candidate.parent

    return candidate


PathPredicate = Callable[[Path], bool]


def gitignore_rule_to_glob(rule: str) -> PathPredicate:
    if "/" not in rule and "**" not in rule:
        if "*" in rule:
            return lambda p: fnmatch(p.name, rule)
        else:
            return lambda p: p.name == rule

    if rule[0] == "/":
        rule = rule[1:]
    else:
        rule = f"**/{rule}"

    if rule[-1] == "/":
        rule = rule[:-1]
        return lambda p: p.is_dir() and fnmatch(str(p), rule)
    else:
        return lambda p: fnmatch(str(p), rule)


def has_poetry_config(file: Path) -> bool:
    pyproject = parse(file.read_text())
    return (
        "tool" in pyproject
        and isinstance(pyproject["tool"], dict)
        and "poetry" in pyproject["tool"]
    )


class PoetryProject:
    label: Final[str]
    dir: Final[Path]

    def __init__(self, root: Path, pyproject: Path):
        self.label = "//" + "/".join(pyproject.parent.relative_to(root).parts)
        self.dir = pyproject.parent.absolute()

    def __lt__(self, other: "PoetryProject") -> bool:
        return self.label < other.label


def crawl(root: Path) -> Iterator[PoetryProject]:
    def _crawl(
        candidate: Path, ignore_rules: Dict[str, PathPredicate]
    ) -> Iterator[PoetryProject]:
        if any(
            rule_matcher(candidate.relative_to(root))
            for rule_matcher in ignore_rules.values()
        ):
            return
        elif (
            candidate.is_file()
            and candidate.name == "pyproject.toml"
            and has_poetry_config(candidate)
        ):
            yield PoetryProject(root, candidate)
        elif candidate.is_dir():
            gitignore = candidate / ".gitignore"
            if gitignore.is_file():
                ignore_rules = {
                    **ignore_rules,
                    **{
                        line: gitignore_rule_to_glob(line)
                        for line in gitignore.read_text().splitlines()
                        if line and line[0] != "!"
                    },
                }

            for c in candidate.iterdir():
                yield from _crawl(c, ignore_rules)

    yield from _crawl(root, dict())


@lru_cache(maxsize=1)
def find_projects() -> List[PoetryProject]:
    root = find_root()
    return sorted(crawl(root))
