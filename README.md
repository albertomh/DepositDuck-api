# DepositDuck

## Develop

### Prerequisites

To develop DepositDuck, the following must be available:

- [make](https://www.gnu.org/software/make/)
- [uv](https://github.com/astral-sh/uv)
- [pre-commit](https://pre-commit.com/)

### Run locally

A `makefile` defines common development tasks.

```sh
# install dependencies in a virtualenv
make install-deps-dev
```

### Dev workflow

```sh
# install pre-commit hooks
pre-commit install
```

### Manage dependencies

Dependencies are defined in `.in` files in the `requirements/` directory.  
`.txt` files in that directory list pinned versions.

```sh
# pin base dependencies
make pin-deps

# pin development dependencies (will include base as well)
make pin-deps-dev

# update dependency versions
make update-deps
make update-deps-dev
```

## Test

## Deploy

---
&copy; 2024 Alberto MH  
This work is licensed under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/)
