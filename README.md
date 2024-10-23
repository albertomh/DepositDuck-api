<!-- markdownlint-disable MD033 -->
# DepositDuck

_Get what's yours_ <!-- markdownlint-disable-line MD036 -->

|              |   |
|--------------|---|
| stack        | [![python: 3.12](https://img.shields.io/badge/3.12-4584b6?logo=python&logoColor=ffde57)](https://docs.python.org/3.12/whatsnew/3.12.html) [![fastapi](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)](https://github.com/tiangolo/fastapi) [![postgres](https://img.shields.io/badge/Postgres-4169E1?logo=postgresql&logoColor=white)](https://github.com/tiangolo/fastapi) [![htmx](https://img.shields.io/badge/htmx-white?logo=htmx&logoColor=3366CC)](https://github.com/bigskysoftware/htmx) [![Alpine.js](https://img.shields.io/badge/Alpine.js-2D3442?logo=alpinedotjs&logoColor=#8BC0D0)](https://alpinejs.dev/) [![speculum](https://img.shields.io/badge/speculum-9f71ff?logo=apache&logoColor=ffffff)](https://github.com/albertomh/speculum/) <tr></tr> |
| dev tooling  | [![justfile](https://img.shields.io/badge/🤖_justfile-EFF1F3)](https://github.com/casey/just) [![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json&labelColor=261230&color=de60e9)](https://github.com/astral-sh/uv) [![MailHog](https://img.shields.io/badge/🐽_MailHog-952225)](https://github.com/mailhog/MailHog) [![pre-commit](https://img.shields.io/badge/pre--commit-FAB040?logo=pre-commit&logoColor=1f2d23)](https://github.com/pre-commit/pre-commit) [![ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json&labelColor=261230&color=d8ff64)](https://github.com/astral-sh/ruff) [![esbuild](https://img.shields.io/badge/esbuild-FFCF00?logo=esbuild&logoColor=000000)](https://esbuild.github.io/) <tr></tr> |
| tests        | [![pytest](https://img.shields.io/badge/pytest-0A9EDC?logo=pytest&logoColor=white)](https://github.com/pytest-dev/pytest) [![playwright](https://img.shields.io/badge/playwright-2ead34?logo=playwright&logoColor=e2584c)](https://playwright.dev/docs/intro) ![coverage](https://img.shields.io/badge/coverage-81%25-EADF6C?labelColor=2b3036) [![CI](https://github.com/albertomh/DepositDuck/actions/workflows/ci.yaml/badge.svg)](https://github.com/albertomh/DepositDuck/actions/workflows/ci.yaml) [![security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit) <tr></tr> |

## Prerequisites

To develop DepositDuck the following must be available locally:

- [just](https://github.com/casey/just)
- [uv](https://github.com/astral-sh/uv)
- [pre-commit](https://pre-commit.com/)
- [esbuild](https://formulae.brew.sh/formula/esbuild)
- [Docker](https://docs.docker.com/)
- [Python 3.12](https://docs.python.org/3/whatsnew/3.12.html)

## Quickstart: run locally

A `justfile` defines common development tasks. Run `just` to show all available recipes.

```sh
# install base + dev dependencies in a virtualenv
just install-deps

# create a .env file and populate as needed
# (see `Settings` class in `depositduck/settings.py`)
cp .env.in .env

# start the containerised LLM service on :11434
# see 'Embeddings Service' in docs/7_data-pipeline.md
# and https://github.com/albertomh/draLLaM
just drallam &

# start database, local email server on :1025/:8025,
# run migrations and start webapp server on :8000
just run

# stop all local services, including: database container,
# draLLaM container, SMTP server, webapp server.
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

See [Fixtures](docs/3_models-and-database.md#fixtures) in `docs/3_models-and-database.md`
for a list of ready-to-use credentials.

## Develop

[docs/1_develop.md](docs/1_develop.md) covers:

- [Environment variables / application Settings](docs/1_develop.md#environment-variables--application-settings)
- [Development workflow](docs/1_develop.md#development-workflow)
- [Dependency management](docs/1_develop.md#dependency-management)

## Project structure

[docs/2_project-structure.md](docs/2_project-structure.md) covers:

- [Packages and modules](docs/2_project-structure.md#packages-and-modules)
- [Dependables](docs/2_project-structure.md#dependables)
  - [Router dependables & protected routes](docs/2_project-structure.md#router-dependables--protected-routes)

## Models and database

[docs/3_models-and-database.md](docs/3_models-and-database.md) covers:

- [The 'models' package](docs/3_models-and-database.md#the-models-package)
- [Database](docs/3_models-and-database.md#database)
  - [Migrations](docs/3_models-and-database.md#migrations)
  - [Fixtures](docs/3_models-and-database.md#fixtures)

## Frontend

[docs/4_frontend.md](docs/4_frontend.md) covers:

- [Bootstrap & 'speculum'](docs/4_frontend.md#bootstrap--speculum)
- [Jinja2](docs/4_frontend.md#jinja2)
- [Naming conventions](docs/4_frontend.md#naming-conventions)
- [JavaScript](docs/4_frontend.md#javascript)

## Test

[docs/5_test.md](docs/5_test.md) covers:

- [Prerequisites](docs/5_test.md#prerequisites)
- [Unit tests](docs/5_test.md#unit-tests)
- [E2E tests](docs/5_test.md#e2e-tests)
  - [Generate e2e tests](docs/5_test.md#generate-e2e-tests)
  - [E2E users](docs/5_test.md#e2e-users)

## Continuous Integration

[docs/6_ci-cd.md](docs/6_ci-cd.md) covers:

- [GitHub Actions CI](docs/6_ci-cd.md#github-actions-ci)
- [Continuous Delivery](docs/6_ci-cd.md#continuous-delivery)  
  ⚠️ This section is WIP
  - [Cut a release and push to Container Registry](docs/6_ci-cd.md#cut-a-release-and-push-to-container-registry)
- [Run a Container Registry image locally](docs/6_ci-cd.md#run-a-container-registry-image-locally)

## Data pipeline

[docs/7_data-pipeline.md](docs/7_data-pipeline.md) covers:

- [Load data for RAG](docs/7_data-pipeline.md#load-data-for-rag)
- [Embeddings service](docs/7_data-pipeline.md#embeddings-service)

---

&copy; 2024 Alberto MH  
This work is licensed under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/)
