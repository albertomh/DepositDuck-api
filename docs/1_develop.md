# Develop `DepositDuck`

## Prerequisites

See [README.md#prerequisites](../README.md#prerequisites)

## Quickstart: run locally

See [README.md#quickstart-run-locally](../README.md#quickstart-run-locally)

## Environment variables / application Settings

### APP_SECRET

`APP_SECRET` must be a valid Fernet key. This is because it is used for symmetric
encryption (amongst other things). A custom validator in Settings checks this is the case
when environment variables are first loaded.

```sh
# generate a valid Fernet key for use as `APP_SECRET`
. ./.venv/bin/activate
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

## Development workflow

This repo follows trunk-based development. This means:

- the `main` branch should always be in a releasable state
- use short-lived feature branches

[wat](https://pypi.org/project/wat-inspector/) is available as a development dependency. To
inspect an object and pretty-print information about it on the console, add a line like
`import wat; wat / some_object`.

Pre-commit hooks are available to prevent common gotchas and to lint & format code.

```sh
# install pre-commit hooks
pre-commit install
```

Please follow the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/)
guidelines when writing commit messages. Where possible, scope commit types
eg. `feat(fe)` or `test(unit)`.
`commitlint` is enabled as a pre-commit hook. Valid commit types are defined in `.commitlintrc.yaml`.

## Manage requirements

Packages required by the application are defined in `pyproject.toml` and managed with `uv`.
The `uv.lock` file is used to ensure reproducible builds. Optional dev and test
dependencies can be managed with uv's `--extra` option.

```sh
# update requirements in line with constraints in pyproject.toml 'dependencies' tables
just update-deps
```

`just update-deps` will also run `just update-pre-commit`.

Dependabot is configured to run weekly and update Python packages & GitHub Actions. See
[`.github/dependabot.yaml`](.github/dependabot.yaml).
