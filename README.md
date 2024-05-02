<!-- markdownlint-disable MD033 -->
# DepositDuck

_Get what's yours_ <!-- markdownlint-disable-line MD036 -->

## Develop

|              |   |
|--------------|---|
| stack        | [![python: 3.12](https://img.shields.io/badge/3.12-4584b6?logo=python&logoColor=ffde57)](https://docs.python.org/3.12/whatsnew/3.12.html) [![fastapi](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)](https://github.com/tiangolo/fastapi) [![postgres](https://img.shields.io/badge/Postgres-4169E1?logo=postgresql&logoColor=white)](https://github.com/tiangolo/fastapi) [![htmx](https://img.shields.io/badge/htmx-white?logo=htmx&logoColor=3366CC)](https://github.com/bigskysoftware/htmx) [![Alpine.js](https://img.shields.io/badge/Alpine.js-2D3442?logo=alpinedotjs&logoColor=#8BC0D0)](https://alpinejs.dev/) [![speculum](https://img.shields.io/badge/speculum-9f71ff?logo=apache&logoColor=ffffff)](https://github.com/albertomh/speculum/) <tr></tr> |
| dev tooling  | [![justfile](https://img.shields.io/badge/🤖_justfile-EFF1F3)](https://github.com/casey/just) [![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json&labelColor=261230&color=de60e9)](https://github.com/astral-sh/uv) [![MailHog](https://img.shields.io/badge/🐽_MailHog-952225)](https://github.com/mailhog/MailHog) [![pre-commit](https://img.shields.io/badge/pre--commit-FAB040?logo=pre-commit&logoColor=1f2d23)](https://github.com/pre-commit/pre-commit) [![ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json&labelColor=261230&color=d8ff64)](https://github.com/astral-sh/ruff) [![esbuild](https://img.shields.io/badge/esbuild-FFCF00?logo=esbuild&logoColor=000000)](https://esbuild.github.io/) <tr></tr> |
| tests        | [![pytest](https://img.shields.io/badge/pytest-0A9EDC?logo=pytest&logoColor=white)](https://github.com/pytest-dev/pytest) [![playwright](https://img.shields.io/badge/playwright-2ead34?logo=playwright&logoColor=e2584c)](https://playwright.dev/docs/intro) ![coverage](https://img.shields.io/badge/coverage-78%25-EADF6C?labelColor=2b3036) [![CI](https://github.com/albertomh/DepositDuck/actions/workflows/ci.yaml/badge.svg)](https://github.com/albertomh/DepositDuck/actions/workflows/ci.yaml) <tr></tr> |

### Prerequisites

To develop DepositDuck the following must be available locally:

- [just](https://github.com/casey/just)
- [uv](https://github.com/astral-sh/uv)
- [pre-commit](https://pre-commit.com/)
- [esbuild](https://formulae.brew.sh/formula/esbuild)
- [Docker](https://docs.docker.com/)
- [Python 3.12](https://docs.python.org/3/whatsnew/3.12.html)

### Quickstart: run locally

A `justfile` defines common development tasks. Run `just` to show all available recipes.

```sh
# install base + dev dependencies in a virtualenv
just install-deps

# create a .env file and populate as needed
# (see `Settings` class in `depositduck/settings.py`)
cp .env.in .env

# start the containerised LLM service on :11434
# see 'Embeddings Service' below and https://github.com/albertomh/draLLaM
just drallam &

# start database, local email server on :1025,
# run migrations and start server on :8000
just run

# stop all local services, including: database container,
# draLLaM container, SMTP server, app server.
just stop
```

NB. `just` will default to using the `.env` file. An alternative dotenv can be specified
eg. `just dotenv=.env.test test`.

After invoking `just run` the following are available:

- [0.0.0.0:8000/](http://0.0.0.0:8000/) - web frontend
- [0.0.0.0:8000/docs](http://0.0.0.0:8000/docs) - interactive `webapp` API docs.  
  Serves the htmx frontend, responses are HTML pages & fragments.
- [0.0.0.0:8000/api/docs](http://0.0.0.0:8000/api/docs) - interactive `apiapp` docs.  
  Endpoints for operational tasks eg. healthchecks - responses are JSON.
- [0.0.0.0:8000/llm/docs](http://0.0.0.0:8000/llm/docs) - interactive `llmapp` API docs.
  Large language model & embeddings service.
- [0.0.0.0:8025/](http://0.0.0.0:8025/) - Mailhog UI

### Environment variables / application Settings

#### APP_SECRET

`APP_SECRET` must be a valid Fernet key. This is because it is used for symmetric
encryption (amongst other things). A custom validator in Settings checks this is the case
when environment variables are first loaded.

```sh
# generate a valid Fernet key for use as `APP_SECRET`
. ./.venv/bin/activate
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

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
just [ pin-deps | pin-deps-base | pin-deps-dev | pin-deps-test ]

# update dependencies in line with requirements/*.in files
just [ update-deps | update-deps-base | update-deps-dev | update-deps-test ]
```

`just update-deps` will also run `just update-pre-commit`.

Dependabot is configured to run weekly and update Python packages & GitHub Actions. See
[`.github/dependabot.yaml`](.github/dependabot.yaml).

## Project structure

DepositDuck is a monolithic FastAPI webapp with a `htmx` frontend generated server-side
via Jinja2 templates.

The project is split into the following packages:

- `api`: operations endpoints that return JSON.
- `auth`: authentication backend (database strategy + cookie transport) and UserManager.
- `dashboard`: dashboard and onboarding
- `email`: email templates and utilities to render and send HTML emails.
- `llm`: language agent functionality eg. ingest data, generate embeddings, etc.
- `models`: Pydantic schemas, SQLModel table definitions and Alembic migrations.
- `people`: track prospects and humans linked to auth users.
- `web`: core FastAPI app on which everything else hangs off. Serves the htmx frontend.

And the following top-level modules:

- `dependables`: callables to be used with FastAPI's dependency injection system.
- `main`: application entrypoint, defines FastAPI apps and attaches routers to these.
- `settings`: application configuration driven by environment variables from a dotenv file.
- `utils`: functions with limited scope that are useful throughout the application.

### Dependables

Callables for use with FastAPI's dependency injection system are made available in the
`dependables` module. These include utilities to access the `structlog` logger, a configured
settings object, a database session factory and a Jinja fragments context.

Packages may contain domain-specific dependables, such as the `auth.dependables` module.

#### Router dependables & protected routes

The default assumption for all routes is that they require a logged-in user to be attached
to the request.  
This restriction may be lifted for routes that must be accessible to unauthenticated users
by adding the relevant paths to `FRONTEND_MUST_BE_LOGGED_OUT_PATHS` or `OPERATIONS_MUST_BE_LOGGED_OUT_PATHS`
in the `middleware` module. These lists are used by the auth middlewares, which are included
as router-level dependables and used to filter every request.

### Models

The `models` package defines physical and virtual models for entities used in the application.
It contains:

- the `auth` module - user authentication.
- the `common` module - mixins to help build base models and tables elsewhere.
- the `deposit` module - track deposit recovery cases linked to users.
- the `email` module - templates and utilities to render and send HTML emails.
- the `llm` module - models used when interacting with LLMs and storing their output
  (embeddings, etc.)
- the `dto` package: Data Transfer Objects building on base models.
- the `migrations` package (Alembic migrations, see below)
- the `sql` package - table models inheriting the models defined elsewhere. Uses SQLModel.

Table models are exported in `sql.tables` for convenience.

### Database

The web service is backed by a PostgreSQL instance. Use v15 since this is the latest version
supported by GCP Cloud SQL ([docs](https://cloud.google.com/sql/docs/postgres/db-versions)).
Use the [pgvector](https://hub.docker.com/r/ankane/pgvector/tags) base image to avoid having
to manually install the package in the image every time.

Locally the database is made available via a container. Inspired by the approach described
in [perrygeo.com/dont-install-postgresql-using-containers-for-local-development](https://www.perrygeo.com/dont-install-postgresql-using-containers-for-local-development).

```sh
# follow logs for the containerised PostgreSQL database
just db_logs

# delete the volume backing the local database
# (prefer using `just _wipe_db` followed by `just migrate`)
rm -rf local/database/pgdata/pgdata15
```

The initialisation script for the database is located at `local/database/init-scripts/init.sql`.
It creates a `depositduck` user and two databases:

- `depositduck`: for local development
- `depositduck_test`: for use during integration & e2e tests

### Migrations

Migrations are provided by Alembic. Alembic was initialised with the `async` template to
enable it to use a SQLAlchemy async engine.  
The migrations directory is `depositduck/models/migrations/`.

```sh
# create a migration with the message 'add_person'
just migration "add Person"

# apply the latest migration
# (optionally specify a revision `just migrate <id>`)
just migrate

# revert to the previous migration
# (optionally specify a revision `just downgrade <id>`)
just downgrade
```

### Fixtures

Fixtures with data needed during development and e2e tests can be found in `local/database/init-scripts/`.
These are applied as part of the `just migrate` script.  
The development fixture creates the following users:

| email                          | is_superuser | is_active | is_verified | completed_onboarding_at |
|--------------------------------|--------------|-----------|-------------|-------------------------|
| <admin@example.com>            |       ✔️      |     ✔️     |      ✔️      |           N/A           |
| <active_verified@example.com>  |              |     ✔️     |      ✔️      |           now()         |
| <needs_onboarding@example.com> |              |     ✔️     |      ✔️      |           NULL          |

All users have the password `password`.

See [E2E users](#e2e-users) below for information on users available during e2e scenarios
and how to use these.

### Frontend

DepositDuck uses the `speculum` frontend toolkit. This is a distribution of Bootstrap 5
customised to use the project's palette which lives at [albertomh/speculum](https://github.com/albertomh/speculum).
`speculum` also includes ready-to-use minified versions of Bootstrap Icons, htmx and Alpine.js.

`speculum` static assets are hosted in a public Cloudflare R2 bucket with CORS enabled to
allow GET from `localhost:8000`.

#### JavaScript

Pages should be built in a HTML-first way, progressively enhanced with CSS and JavaScript.
Small scripts are defined in `depositduck/web/static/src/js/`. Run the `just build_js`
recipe to have `esbuild` bundle all files into `depositduck/web/static/dist/js/main.min.js`.
Namespace custom functionality under the `window.depositduck` object, eg. `window.depositduck.dashboard.welcome`

## Test

Tests live in `tests/`, which contains two sub-directories:

- `unit/` pytest unit tests.
- `e2e/` end-to-end Playwright tests.

### Prerequisites

The tools listed under [Develop > Prerequisites](#prerequisites) must be available in
order to run tests.

### Unit tests

```sh
# !important: remember to specify `dotenv=.env.test` when running the test recipe.

# run unit tests and show coverage report
# writes HTML report to `htmlcov/index.html`
just dotenv=.env.test test coverage
```

Unit tests have the `--pdb` flag when run locally, so will drop you into an interactive
debugger at the first failure.

### E2E tests

```sh
# !important: remember to specify `dotenv=.env.e2e` when running the e2e tests recipe.

# run end-to-end Playwright tests
# will wipe test database, then restart the smtp
# service & app server in the background
just dotenv=.env.e2e e2e
```

Playwright tests run in headless mode by default. To run them in a visible browser window
and/or slow them down, set `E2E_HEADLESS` and `E2E_SLOW_MO` (in milliseconds) accordingly
in `.env.e2e`.

#### Generate e2e tests

The Playwright Inspector can be used to record tests by interacting with the webapp
running locally.

```sh
# run the application in the background
just run &

# activate virtual env and launch Playwright Inspector
. ./.venv/bin/activate
playwright codegen 0.0.0.0:8000/
```

#### E2E users

The `e2e_fixture.sql` generates the following users, which are available to test code from
an enum in `e2e/conftest` and can be used with the utility methods to eg. log in as a
specific user in an e2e scenario. All e2e users should use the `E2E_USER_PASSWORD`, also
defined in `conftest`.

The e2e fixture creates the following users:

| email                          | is_superuser | is_active | is_verified | completed_onboarding_at |
|--------------------------------|--------------|-----------|-------------|-------------------------|
| <active_verified@example.com>  |              |     ✔️     |      ✔️      |           now()         |
| <needs_onboarding@example.com> |              |     ✔️     |      ✔️      |           NULL          |

## Continuous Integration

Continuous Integration pipelines run via GitHub Actions on push.  
Pipelines are defined by YAML files in the `.github/workflows/` directory.
There are two workflows:

- `pr.yaml`: when a commit on a feature branch is pushed up to GitHub.
- `ci.yaml`: when a Pull Request is merged into the 'main' branch.

They both run pre-commit hooks and unit tests against the codebase.

`ci.yaml` additionally
runs end-to-end Playwright tests, Dockerises the app and pushes the image to the GitHub
Container Registry. The build artefact is a multi-arch Docker image to ensure compatibility
with both Apple Silicon (ARM64) and GCP Cloud Run (x86_64).

To run a Docker image locally:

```sh
# 1. Visit https://github.com/settings/tokens/new?scopes=write:packages

# 2. Select all relevant `packages` scopes and create
#    a new Personal Access Token (PAT).

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

## Data pipeline

⚠️ This workflow is in flux and subject to change.

To load a PDF as a source of data for Retrieval Augmented Generation:

```sh
# place the source PDF in the data_pipeline directory
cp source.pdf ./local/data_pipeline/

# run a script to extract text from the PDF and save
# to `sourcetext.tmp` in the data_pipeline directory
python ./local/data_pipeline/pdf_to_raw_sourcetext.py source.pdf

# run the database in the background and ensure all migrations have run
just db &
just migrate

# insert extracted data as a SourceText record in the database
# - assumes a previous step wrote to `sourcetext.tmp`
PGPASSWORD=password ./local/data_pipeline/raw_sourcetext_to_database.sh
```

### Embeddings service

[draLLaM](https://github.com/albertomh/draLLaM) is DepositDuck's dedicated LLM service.
As of draLLaM@0.1.0 the service focuses on generating text embeddings.  
Invoke `just drallam` to run it locally - containerised and available on `:11434` - ready
to respond to queries from the main DepositDuck webapp. There are draLLaM-specific settings
in `.env` that can be used to specify host and port.

## Deploy

### Cut a release

1. Pick the semantic version (`M.m.p`) for the release.
1. Run `just release M.m.p`  
   This stamps the changelog & updates the semver globals in `depositduck/__init__.py`.
   It also triggers a GitHub pipeline that automates the rest of the release.
1. Wait for the pipeline to succeed. It will have raised a PR for this release.
1. Review and merge (merge-and-rebase) the PR.
1. This will trigger a pipeline that tags the `main` branch, creates a GitHub release,
   builds a container and pushes it to the GitHub Container Registry.
1. Wait for the pipeline to succeed and check a new tagged Docker container is available
   in the project's [container registry](https://github.com/albertomh/DepositDuck/pkgs/container/depositduck%2Fmain).

---

&copy; 2024 Alberto MH  
This work is licensed under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/)
