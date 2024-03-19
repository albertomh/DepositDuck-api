# DepositDuck - local development tooling
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

# re-usable function to load the contents of a
# .env file as environment variables
# usage: `$(call load_env,.env)`
define load_env
	set -o allexport; \
	source $(1); \
	set +o allexport;
endef

# create a venv if one does not exist
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
		--resolver backtracking \
		-o $(REQS_DIR)/base.txt

update-deps-dev:
	@$(UV) pip compile \
		$(REQS_DIR)/dev.in \
		--upgrade \
		--resolver backtracking \
		-o $(REQS_DIR)/dev.txt

update-deps-test:
	@$(UV) pip compile \
		$(REQS_DIR)/test.in \
		--upgrade \
		--resolver backtracking \
		-o $(REQS_DIR)/test.txt

# run the application locally
run: venv
	@$(ACTIVATE_VENV) && \
	$(call load_env,.env) \
	uvicorn depositduck.main:webapp --reload

# run tests
test: venv
	@$(ACTIVATE_VENV) && \
	$(call load_env,.env.test) \
	$(UV) pip sync $(REQS_DIR)/test.txt && \
	$(PYTHON) -m pytest -s -vvv -W always

# start a Dockerised instance of PostgreSQL on :5432
db:
	cd local/database/ && \
	./run_postgres.sh

help:
	@echo "usage: make [target]"
	@echo "  help              Show this help message\n"
	@echo "  install-deps      Sync project dependencies to virtualenv"
	@echo "  install-deps-dev  Sync dev dependencies to virtualenv"
	@echo "  install-deps-test Sync test dependencies to virtualenv\n"
	@echo "  pin-deps          Generate base requirements file with pinned dependencies"
	@echo "  pin-deps-dev      Generate dev requirements file with pinned dependencies"
	@echo "  pin-deps-test     Generate test requirements file with pinned dependencies\n"
	@echo "  db                start a Dockerised instance of PostgreSQL on :5432"
	@echo "  run               Run the application using uvicorn. Load config from .env."
	@echo "  test              Run test suite\n"
	@echo "  update-deps       Bump dependency versions in line with constraints in base.in"
	@echo "  update-deps-dev   Bump dependency versions in line with constraints in dev.in"
	@echo "  update-deps-test  Bump dependency versions in line with constraints in test.in\n"
	@echo "  venv              Create a venv if one does not exist\n"
