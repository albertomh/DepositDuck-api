# DepositDuck - local development tooling
#
# Some targets check the `CI` variable to modify behaviour
# if being run in a GitHub Actions pipeline.
#
# (c) 2024 Alberto Morón Hernández

# run all targets & commands in the same shell instance
.ONESHELL:

UV=uv
VENV_DIR=.venv
ACTIVATE_VENV=. $(VENV_DIR)/bin/activate
PYTHON=python3
APP_DIR=depositduck
REQS_DIR=requirements

.PHONY: *

# default target
all: help

# create a virtual environment in '.venv/' if one does not exist
venv:
	@test -d $(VENV_DIR) || $(UV) venv

# Dependency management
# inspiration: https://hynek.me/til/pip-tools-and-pyproject-toml/

# sync project dependencies to virtualenv
install-deps: venv
	@$(ACTIVATE_VENV)
	@$(UV) pip sync \
	$(REQS_DIR)/base.txt

install-deps-dev: venv
	@$(ACTIVATE_VENV)
	@$(UV) pip sync \
	$(REQS_DIR)/dev.txt

install-deps-test: venv
	@$(ACTIVATE_VENV)
	@$(UV) pip sync \
	$(REQS_DIR)/test.txt

# generate requirements files with pinned dependencies
pin-deps:
	@$(UV) pip compile \
	$(REQS_DIR)/base.in \
	-o $(REQS_DIR)/base.txt

pin-deps-dev:
	@$(UV) pip compile \
	$(REQS_DIR)/dev.in \
	-o $(REQS_DIR)/dev.txt

pin-deps-test:
	@$(UV) pip compile \
	$(REQS_DIR)/test.in \
	-o $(REQS_DIR)/test.txt

# bump dependency versions in line with constraints in requirements/*.in files
update-deps:
	@$(UV) pip compile \
		$(REQS_DIR)/base.in \
		--upgrade \
		-o $(REQS_DIR)/base.txt

update-deps-dev:
	@$(UV) pip compile \
		$(REQS_DIR)/dev.in \
		--upgrade \
		-o $(REQS_DIR)/dev.txt

update-deps-test:
	@$(UV) pip compile \
		$(REQS_DIR)/test.in \
		--upgrade \
		-o $(REQS_DIR)/test.txt

# run the draLLaM embeddings service in a container
# https://github.com/albertomh/draLLaM
drallam:
	@docker run \
	  --rm \
	  --publish 11434:11434 \
	  --name drallam \
	  drallam:0.1.0

# run the application locally
# stop anything already running on :8000 first
run: migrate
	@lsof -t  -i :8000 | awk '{print $2}' | xargs -I {} kill -9 {}
	@$(ACTIVATE_VENV) && \
	. ./local/read_dotenv.sh .env && \
	uvicorn depositduck.main:webapp --reload

# run tests
test: venv
# setting env vars using `.env.test` in GitHub Actions is handled in a step of the
# `test` action separate from the one that invokes `make test`. This is because
# environment variables are only available in steps following the one that sets them.
ifdef CI
	@$(ACTIVATE_VENV) && \
	$(PYTHON) -m pytest -s -vvv -W always
else
	@$(ACTIVATE_VENV) && \
	. ./local/read_dotenv.sh .env.test && \
	$(UV) pip sync $(REQS_DIR)/test.txt && \
	$(PYTHON) -m pytest -s -vvv -W always
endif

# start a Dockerised instance of PostgreSQL on :5432
db:
	./local/database/run_postgres.sh .env

# create an Alembic migration
# usage: `make migration m=<message>`
migration: venv
	@$(if $(m),,$(error please specify 'm=<message>' for the new migration))
	@$(ACTIVATE_VENV) && \
	. ./local/read_dotenv.sh .env && \
	$(PYTHON) -m alembic revision --autogenerate -m "$(m)"

# upgrade migrations to a revision - latest if one is not specified
# usage: `migrate [rev=<r>]`
rev ?= head
migrate: venv
	@$(ACTIVATE_VENV) && \
	. ./local/read_dotenv.sh .env && \
	$(PYTHON) -m alembic upgrade ${rev}

# cut a release and raise a pull request for it
release:
	@$(if $(v),,$(error please specify 'v=X.Y.Z' tag for the release))
	./local/cut_release.sh $(v)

help:
	@echo "usage: make [target]"
	@echo "  help                Show this help message\n"
	@echo "  install-deps        Sync project dependencies to virtualenv"
	@echo "  install-deps-dev    Sync dev dependencies to virtualenv"
	@echo "  install-deps-test   Sync test dependencies to virtualenv\n"
	@echo "  pin-deps            Generate base requirements file with pinned dependencies"
	@echo "  pin-deps-dev        Generate dev requirements file with pinned dependencies"
	@echo "  pin-deps-test       Generate test requirements file with pinned dependencies\n"
	@echo "  drallam             Start a Dockerised instance of the draLLaM service on :11434"
	@echo "  db                  Start a Dockerised instance of PostgreSQL on :5432"
	@echo "  migration m=\"<m>\"   Create an Alembic migration with message 'm'"
	@echo "  migrate [rev=<r>]   Upgrade migrations to a revision - latest if none given\n"
	@echo "  run                 Run the application using uvicorn. Load config from .env."
	@echo "  test                Run test suite\n"
	@echo "  release v=X.Y.Z     Cut a release and raise a pull request for it\n"
	@echo "  update-deps         Bump dependency versions in line with constraints in base.in"
	@echo "  update-deps-dev     Bump dependency versions in line with constraints in dev.in"
	@echo "  update-deps-test    Bump dependency versions in line with constraints in test.in\n"
	@echo "  venv                Create a virtual environment in '.venv/' if one does not exist\n"
