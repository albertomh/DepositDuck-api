# DepositDuck - local development tooling
#
# dotenv defaults to `.env`. For testing run as `just dotenv=.env.test <recipe>`
#
# Some targets check the `CI` variable to modify behaviour
# if being run in a GitHub Actions pipeline.
#
# (c) 2024 Alberto Morón Hernández

dotenv := '.env'

VENV_DIR := ".venv"

default:
  @just --list

# create a virtual environment at '.venv/'
venv:
  @test -d {{VENV_DIR}} || uv venv

# Dependency management
# inspiration: https://hynek.me/til/pip-tools-and-pyproject-toml/

# sync project dependencies to virtualenv
install-deps: venv
  @uv sync

install-deps-dev: venv
  @uv sync --extra dev

install-deps-test: venv
  @uv sync --extra test

# bump dependency versions in line with constraints in pyproject.toml
update-deps:
  @just update-deps
  @just update-pre-commit

update-deps-base:
  @uv lock --upgrade

update-pre-commit:
  @pre-commit autoupdate

# start a Dockerised instance of PostgreSQL on :5432
_start_db:
  #!/usr/bin/env bash
  set -euo pipefail
  # do not run in pipelines, only locally. handled by service container in CI.
  if [ -z ${CI:-} ]; then
    . ./local/read_dotenv.sh {{dotenv}}
    ./local/database/run_postgres.sh
    # TODO: remove/improve
    sleep 1
  fi

# follow the database logs
db_logs:
  docker logs --follow depositduck_db

# start a Dockerised instance of PostgreSQL on :5432
db: _start_db
  @just db_logs

_wipe_db: _start_db
  #!/usr/bin/env bash
  set -euo pipefail
  # do not run in pipelines, only locally. handled by service container in CI.
  if [ -z ${CI:-} ]; then
    . ./local/read_dotenv.sh {{dotenv}}
    CONN_STR="postgresql://$DB_USER:$DB_PASSWORD@$DB_HOST:$DB_PORT/$DB_NAME"
    DROP_TABLES_CMD="SELECT format('DROP TABLE IF EXISTS %I CASCADE;', tablename) FROM pg_tables WHERE schemaname='public';\gexec"
    PSQL_DROP_CMD="echo \\\"$DROP_TABLES_CMD\\\" | psql -t $CONN_STR"
    DROP_CMD="docker exec depositduck_db bash -c \"$PSQL_DROP_CMD\""
    echo "[just _wipe_db] $DROP_CMD"
    eval "$DROP_CMD"
  fi

# create an Alembic migration
migration msg: venv
  #!/usr/bin/env bash
  set -euo pipefail
  . {{VENV_DIR}}/bin/activate
  if [ -z ${CI:-} ]; then . ./local/read_dotenv.sh {{dotenv}}; fi
  python -m alembic revision --autogenerate -m {{msg}}

# upgrade migrations to a revision - latest if one is not specified
migrate up="head": venv
  #!/usr/bin/env bash
  set -euo pipefail
  . {{VENV_DIR}}/bin/activate
  if [ -z ${CI:-} ]; then . ./local/read_dotenv.sh {{dotenv}}; fi
  python -m alembic upgrade {{up}}

  # run data fixtures for local development or e2e testing
  if [ -z ${E2E:-} ] || [ "$E2E" = 'false' ]; then
    FIXTURE_PATH="/docker-entrypoint-fixtures.d/dev_fixture.sql"
  else
    FIXTURE_PATH="/docker-entrypoint-fixtures.d/e2e_fixture.sql"
  fi
  printf "\n[just migrate] applying fixture '$FIXTURE_PATH'\n"
  CONN_STR="postgresql://$DB_USER:$DB_PASSWORD@$DB_HOST:$DB_PORT/$DB_NAME"
  PSQL_CMD="psql $CONN_STR -f $FIXTURE_PATH"
  CMD="docker exec depositduck_db bash -c \"$PSQL_CMD\""
  eval "$CMD"

# downgrade to a given alembic revision - previous one if not specified
downgrade down="-1": venv
  #!/usr/bin/env bash
  set -euo pipefail
  . {{VENV_DIR}}/bin/activate
  if [ -z ${CI:-} ]; then . ./local/read_dotenv.sh {{dotenv}}; fi
  python -m alembic downgrade {{down}}

# build & bundle JavaScript into a single file
build_js:
  esbuild depositduck/web/static/src/js/main.js \
  --bundle \
  --minify \
  --tree-shaking=false \
  --format=iife \
  --platform=browser \
  --outfile='depositduck/web/static/dist/js/main.min.js'

# stop anything already running on :1025
_stop_mailhog:
  docker stop mailhog || true

# local mailserver to catch outgoing mail
mailhog: _stop_mailhog
  @docker run \
    --rm \
    --log-driver=none \
    --publish 8025:8025 \
    --publish 1025:1025 \
    --name mailhog \
    mailhog/mailhog:v1.0.1

# run the embeddings service in a container https://github.com/albertomh/draLLaM
drallam:
  @docker run \
    --rm \
    --publish 11434:11434 \
    --name drallam \
    drallam:0.1.0

# stop anything already running on :8000
_stop_server:
  @lsof -t -i :8000 | xargs -I {} kill -9 {}

# run the application locally, with the database in the background
run: stop && stop
  #!/usr/bin/env bash
  set -euo pipefail
  if [ -z ${CI:-} ]; then
    just dotenv={{dotenv}} mailhog &
    just db &
  fi
  sleep 3
  just dotenv={{dotenv}} migrate &
  . {{VENV_DIR}}/bin/activate
  if [ -z ${CI:-} ]; then . ./local/read_dotenv.sh {{dotenv}}; fi
  uv sync --extra=dev
  uvicorn depositduck.main:webapp --reload

# stop all running services
stop:
  #!/usr/bin/env bash
  set -euo pipefail
  if [ -z ${CI:-} ]; then
    docker stop depositduck_db || true
    docker stop drallam || true
    just dotenv={{dotenv}} _stop_mailhog
    just dotenv={{dotenv}} _stop_server
  else
    printf "\n[just stop] no-op 'stop' since executing in a pipeline [CI='$CI']\n"
  fi

# Setting env vars from a dotenv in GitHub Actions is handled in a step of the action
# separate from the one that invokes the recipe. This is because environment variables are
# only available in steps following the one that sets them. Similarly, a separate step
# installs test dependencies.

# run unit & integration tests
# !must run as `just dotenv=.env.test test`
test: venv
  #!/usr/bin/env bash
  set -euo pipefail
  . {{VENV_DIR}}/bin/activate
  if [ -z ${CI:-} ]; then . ./local/read_dotenv.sh {{dotenv}}; fi
  uv sync --extra=test
  if [ -z ${CI:-} ]; then
    python -m coverage run -m pytest tests/unit/ -s -vvv -W always --pdb
  else
    python -m pytest tests/unit/ -s -vvv -W always
  fi

# report on unit test coverage
coverage: venv
  #!/usr/bin/env bash
  set -euo pipefail
  . {{VENV_DIR}}/bin/activate
  if [ -z ${CI:-} ]; then . ./local/read_dotenv.sh {{dotenv}}; fi
  uv sync --extra=test
  report=$(python -m coverage report)
  echo "$report"
  percentage=$(echo "$report" | tail -n 1 | awk '{ print $NF }' | sed 's/\%//')
  ./local/update_coverage_badge.sh $percentage
  python -m coverage html


# run e2e Playwright tests
# !must run as `just dotenv=.env.e2e e2e`
e2e: venv _wipe_db && stop
  #!/usr/bin/env bash
  set -euo pipefail
  just dotenv={{dotenv}} run &
  . {{VENV_DIR}}/bin/activate
  if [ -z ${CI:-} ]; then . ./local/read_dotenv.sh {{dotenv}}; fi
  uv sync --extra=test
  python -m playwright install --with-deps chromium
  # TODO: remove/improve
  sleep 1
  python -m pytest tests/e2e/ -s -vvv -W always

# cut a release and raise a pull request for it
release semver:
  ./local/cut_release.sh {{semver}}
