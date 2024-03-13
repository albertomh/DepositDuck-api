#
# (c) 2024 Alberto Morón Hernández

# run all targets & commands in the same shell instance
.ONESHELL:

UV=uv
VENV_DIR=.venv
ACTIVATE_VENV=. $(VENV_DIR)/bin/activate
PYTHON=python3
APP_DIR=depositduck

.PHONY: *

# create a venv if one does not exist
venv:
	@test -d $(VENV_DIR) || $(UV) venv
