# DepositDuck

## Develop

### Prerequisites

To develop DepositDuck, the following must be available:

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

### Manage dependencies

Dependencies are defined by `.in` files in the `requirements/` directory.  
`.txt` files in that directory list pinned versions.

```sh
# pin dependencies
make pin-deps
make pin-deps-dev
make pin-deps-test

# update dependency versions in line with
# constraints in requirements/*.in files
make update-deps
make update-deps-dev
make update-deps-test
```

When patching dependencies remember to also run:

```sh
pre-commit autoupdate
```

## Test

### Prerequisites

The tools listed under 'Develop > Prerequisites' must be available in order to run tests.

### Run tests locally

The application picks up the `.env.test` file as config if the env var `IS_TEST=true` is
set (this is done for you when using the relevant makefile targets).

```sh
# run unit tests
make test
```

## Deploy

---
&copy; 2024 Alberto MH  
This work is licensed under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/)
