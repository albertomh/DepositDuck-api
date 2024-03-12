# DepositDuck

## Develop

### Prerequisites

To develop DepositDuck, the following must be available:

- [uv](https://github.com/astral-sh/uv)
- [pre-commit](https://pre-commit.com/)

### Dev workflow

```sh
# install pre-commit hooks
pre-commit install
```

### Manage dependencies

Dependencies are defined in `pyproject.toml`.  
Requirements files with pinned versions live in the `requirements/` directory.

```sh
# pin base dependencies
uv pip compile pyproject.toml -o requirements/base.txt

# pin development dependencies (will include base as well)
uv pip compile pyproject.toml --extra dev -o requirements/dev.txt

# update dependency versions
uv pip compile pyproject.toml --upgrade --resolver backtracking -o requirements/base.txt
uv pip compile pyproject.toml --extra dev --upgrade --resolver backtracking -o requirements/dev.txt

# inspiration: https://hynek.me/til/pip-tools-and-pyproject-toml/
```

## Test

## Deploy

---
&copy; 2024 Alberto MH  
This work is licensed under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/)
