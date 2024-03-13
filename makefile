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
	$(REQS_DIR)/base.txt \
	$(REQS_DIR)/dev.txt

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

# bump dependency versions, following constraints in requirements/*.in files
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
	cd depositduck/ && \
	uvicorn main:app --reload
