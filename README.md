# DepositDuck

[![python: 3.12](https://img.shields.io/badge/3.12-4584b6?logo=python&logoColor=ffde57)](https://docs.python.org/3.12/whatsnew/3.12.html)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json&labelColor=261230&color=de60e9)](https://github.com/astral-sh/uv)
[![fastapi](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)](https://github.com/tiangolo/fastapi)
[![htmx](https://img.shields.io/badge/htmx-3366CC?logo=htmx&logoColor=white)](https://github.com/bigskysoftware/htmx)
[![bootstrap](https://img.shields.io/badge/5-7952B3?logo=bootstrap&logoColor=white)](https://github.com/twbs/bootstrap)
[![pytest](https://img.shields.io/badge/pytest-0A9EDC?logo=pytest&logoColor=white)](https://github.com/pytest-dev/pytest)
[![pre-commit](https://img.shields.io/badge/pre--commit-FAB040?logo=pre-commit&logoColor=1f2d23)](https://github.com/pre-commit/pre-commit)
[![ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json&labelColor=261230&color=d8ff64)](https://github.com/astral-sh/ruff)
[![CI](https://github.com/albertomh/DepositDuck/actions/workflows/ci.yaml/badge.svg)](https://github.com/albertomh/DepositDuck/actions/workflows/ci.yaml)

## Develop

### Prerequisites

To develop DepositDuck, the following must be available locally:

- [make](https://www.gnu.org/software/make/)
- [uv](https://github.com/astral-sh/uv)
- [pre-commit](https://pre-commit.com/)

### Run locally

A `makefile` defines common development tasks. Run `make` or `make help` to show all
available targets.

```sh
# install base + dev dependencies in a virtualenv
make install-deps-dev

# create a .env file and populate as needed
# (see `Settings` class in `config.py`)
cp .env.in .env

# run server on port 8000
make run
```

The following are now available:

- [0.0.0.0:8000/docs](http://0.0.0.0:8000/docs) - interactive API docs

### Dev workflow

This repo follows trunk-based development. This means:

- the `main` branch should always be in a releasable state
- use short-lived feature branches

Pre-commit hooks are available to prevent common gotchas and to lint & format code.

```sh
# install pre-commit hooks
pre-commit install
```

Please follow the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/)
guidelines when writing commit messages.
`commitlint` is enabled as a pre-commit hook. Valid commit types are defined in `.commitlintrc.yaml`.

### Project structure

The project is split into two packages, `web` & `api`. Each corresponds to a separate FastAPI
app defined in the `main` module. `apiapp` is mounted on `webapp` under the `/api` path.

### Dependables

Callables for use with FastAPI's dependency injection system are made available in the
`dependables` module. These include utilities to access the `structlog` logger, a configured
settings object and a Jinja fragments context.

### Manage requirements

Packages required by the application are defined by `.in` files in the `requirements/`
directory. `.txt` files in that directory list pinned versions.

```sh
# pin dependencies
make [ pin-deps | pin-deps-dev | pin-deps-test ]

# update dependency versions in line with
# constraints in requirements/*.in files
make [ update-deps | update-deps-dev | update-deps-test ]
```

When patching dependencies remember to also run:

```sh
pre-commit autoupdate
```

Dependabot is configured to run weekly and update Python packages & GitHub Actions. See
`.github/dependabot.yaml`.

## Test

### Prerequisites

The tools listed under 'Develop > Prerequisites' must be available in order to run tests.

### Run tests locally

The application picks up the `.env.test` file as config if the env var `IS_TEST=true` is
set. This is done for you when using `make test`.

```sh
make install-deps-test

# run unit tests
make test
```

##  Continuous Integration

A Continuous Integration pipeline runs via GitHub Actions on push.  
This pipeline is defined by the YAML in the `.github/workflows/` directory.

## Deploy

---
&copy; 2024 Alberto MH  
This work is licensed under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/)
