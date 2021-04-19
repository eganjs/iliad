# iliad
A monorepo tool for [Poetry](https://github.com/python-poetry/poetry)

The intention is to make a tool that makes working with poetry in monorepos more convenient.

## Install
```shell
$ pip install iliad
```

## Quirks
- Expects to run within a git repo, uses the `.git` directory to detect the root of the monorepo.

## Usage
### List
List the poetry projects detected.
```shell
$ iliad list
//deployment
//lambdas/alpha
//lambdas/beta
//lambdas/delta
```

### Run
Runs a command (using `poetry run`) for each of the poetry projects, where the path matches the selector.

Prints out errors for commands that fail.
```shell
$ iliad run --selector lambdas -- pytest -v --capture=no
[done] //lambdas/alpha
[failed(2)] //lambdas/beta
[done] //lambdas/delta

failures:
[//lambdas/beta] failed with return code 2
[//lambdas/beta:stdout] ...
[//lambdas/beta:stderr] ...
```
