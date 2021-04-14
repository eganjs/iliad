__all__ = [
    "find_root",
    "find_pyprojects",
]

from fnmatch import fnmatch
from functools import lru_cache
from pathlib import Path
from typing import Callable, Dict, Iterator, List

from click import ClickException
from tomlkit import parse


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


def crawl(root: Path) -> Iterator[Path]:
    def _crawl(
        candidate: Path, ignore_rules: Dict[str, PathPredicate]
    ) -> Iterator[Path]:
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
            yield candidate.relative_to(root)
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


def find_pyprojects() -> List[Path]:
    root = find_root()
    return sorted(crawl(root))
