# DepositDuck

_Get what's yours_ <!-- markdownlint-disable-line MD036 -->  

## Develop

[![python: 3.12](https://img.shields.io/badge/3.12-4584b6?logo=python&logoColor=ffde57)](https://docs.python.org/3.12/whatsnew/3.12.html)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json&labelColor=261230&color=de60e9)](https://github.com/astral-sh/uv)
[![fastapi](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)](https://github.com/tiangolo/fastapi)
[![htmx](https://img.shields.io/badge/htmx-3366CC?logo=htmx&logoColor=white)](https://github.com/bigskysoftware/htmx)
[![bootstrap](https://img.shields.io/badge/5-7952B3?logo=bootstrap&logoColor=white)](https://github.com/twbs/bootstrap)
[![pytest](https://img.shields.io/badge/pytest-0A9EDC?logo=pytest&logoColor=white)](https://github.com/pytest-dev/pytest)
[![pre-commit](https://img.shields.io/badge/pre--commit-FAB040?logo=pre-commit&logoColor=1f2d23)](https://github.com/pre-commit/pre-commit)
[![ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json&labelColor=261230&color=d8ff64)](https://github.com/astral-sh/ruff)
[![CI](https://github.com/albertomh/DepositDuck/actions/workflows/ci.yaml/badge.svg)](https://github.com/albertomh/DepositDuck/actions/workflows/ci.yaml)

### Prerequisites

To develop DepositDuck, the following must be available locally:

- [make](https://www.gnu.org/software/make/)
- [uv](https://github.com/astral-sh/uv)
- [pre-commit](https://pre-commit.com/)
- [Docker](https://docs.docker.com/)

### Quickstart: run locally

A `makefile` defines common development tasks. Run `make` or `make help` to show all
available targets.

```sh
# install base + dev dependencies in a virtualenv
make install-deps-dev

# create a .env file and populate as needed
# (see `Settings` class in `config.py`)
cp .env.in .env

# start database in a container
make db

# run server on port 8000
make run
```

After doing the above the following are now available:

- [0.0.0.0:8000](http://0.0.0.0:8000) - web frontend
- [0.0.0.0:8000/docs](http://0.0.0.0:8000/docs) - interactive docs for the `webapp`
- [0.0.0.0:8000/api/docs](http://0.0.0.0:8000/api/docs) - interactive docs for the `apiapp`

### Development workflow

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

## Project structure

The project is split into two packages, `web` & `api`. Each corresponds to a separate FastAPI
app defined in the `main` module. `apiapp` is mounted on `webapp` under the `/api` path.

### Dependables

Callables for use with FastAPI's dependency injection system are made available in the
`dependables` module. These include utilities to access the `structlog` logger, a configured
settings object and a Jinja fragments context.

### Models

The `models` package defines physical and virtual models for entities used in the application.
It contains two modules:

- `sql`: SQLModel classes defining base and table models. Base models are stored here for
  convenience, immediately before each model that defines a database table.
- `dto`: Data Transfer Objects building on base models.

Table models are exported in `tables.__init__.py` so can be imported as
`from depositduck import tables`.

### Database

The web service is backed by a PostgreSQL instance. Use v15 since this is the latest version
supported by GCP Cloud SQL ([docs](https://cloud.google.com/sql/docs/postgres/db-versions)).

Locally the database is made available via a container. Inspired by the approach described
in [perrygeo.com/dont-install-postgresql-using-containers-for-local-development](https://www.perrygeo.com/dont-install-postgresql-using-containers-for-local-development).

```sh
# start the containerised postgres database
make db

# delete the local database
rm -rf local/database/pgdata/pgdata15
```

### Migrations

Migrations are provided by Alembic. Alembic was initialised with the `async` template to
enable it to use a SQLAlchemy async engine.  
The migrations directory is `depositduck/models/migrations/`.

```sh
# make a migration with the message 'add_person'
make migration m="add Person"

# apply the latest migration
# (optionally specify a revision with `rev=<id>`)
make migrate
```

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

Continuous Integration pipelines run via GitHub Actions on push.  
Pipelines are defined by YAML files in the `.github/workflows/` directory.
There are two workflows:

- When a commit on a feature branch is pushed up to GitHub - `pr.yaml`
- When a Pull Request is merged into the 'main' branch - `ci.yaml`

They both run pre-commit hooks and tests against the codebase. `ci.yaml` additionally
Dockerises the app and pushes the image to the GitHub Container Registry.  
The build artefact is a multi-arch Docker image to ensure compatibility with both
Apple Silicon (ARM64) and GCP Cloud Run (x86_64).

To run a Docker image locally:

```sh
# 1. Visit https://github.com/settings/tokens/new?scopes=write:packages

# 2. Select all relevant `packages` scopes and create a new Personal Access Token (PAT).

# 3. Save the PAT as an environment variable:
export GHCR_PAT=YOUR_TOKEN

# 4. Sign in to the Container Registry:
echo $GHCR_PAT | docker login ghcr.io -u USERNAME --password-stdin

# 5. Pull the latest image
docker pull ghcr.io/albertomh/depositduck/main:latest

# 6. Run the webapp on port 80
docker run \
 --rm \
 --detach \
 --read-only \
 --volume ./.env:/app/.env \
 --publish 80:80 \
 --name depositduck_web \
 ghcr.io/albertomh/depositduck/main

# 7. Stop the container
docker stop depositduck_web
```

## Deploy

### Cut a release

1. Pick the semver number (`X.Y.Z`) for the release.
1. Run `make release v=X.Y.Z`  
   This stamps the changelog and triggers a GitHub pipeline.
1. Wait for the pipeline to succeed. It will have raised a PR for this release.
1. Review and merge (merge-and-rebase) the PR.
1. This will trigger a pipeline to tag the `main` branch, create a GitHub release, build
   a container and push it to the GitHub Container Registry.
1. Wait for the pipeline to succeed and check a new tagged Docker container is available
   in the project's [container registry](https://github.com/albertomh/DepositDuck/pkgs/container/depositduck%2Fmain).

---
&copy; 2024 Alberto MH  
This work is licensed under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/)
