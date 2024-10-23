# Test

Tests live in `tests/`, which contains two sub-directories:

- `unit/` pytest unit tests.
- `e2e/` end-to-end Playwright tests.

## Prerequisites

The tools listed under [README.md#prerequisites](../README.md#prerequisites) must be
available in order to run tests.

## Unit tests

```sh
# !important: remember to specify `dotenv=.env.test` when running the test recipe.

# run unit tests and show coverage report
# writes HTML report to `htmlcov/index.html`
just dotenv=.env.test test coverage
```

Unit tests have the `--pdb` flag when run locally, so will drop you into an interactive
debugger at the first failure.

[wat](https://pypi.org/project/wat-inspector/) is available in the debugger. To inspect an
object and pretty-print information about it on the console, add a line like
`import wat; wat / some_object`.

Follow the [Arrange Act Assert](https://wiki.c2.com/?ArrangeActAssert) pattern as much as
possible when writing unit tests.

## E2E tests

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

To run only specific tests, append the `-k` flag along with an appropriate selector to the
pytest invocation at the end of the `e2e` recipe in the justfile.

### Generate e2e tests

The Playwright Inspector can be used to record tests by interacting with the webapp
running locally.

```sh
# run the application in the background
just run &

# activate virtual env and launch Playwright Inspector
. ./.venv/bin/activate
playwright codegen 0.0.0.0:8000/
```

### E2E users

The `e2e_fixture.sql` generates the following users, which are available to test code from
an enum in `e2e/conftest` and can be used with the utility methods to eg. log in as a
specific user in an e2e scenario. All e2e users should use the `E2E_USER_PASSWORD`, also
defined in `conftest`.

The e2e fixture creates the following users:

| email                          | is_superuser | is_active | is_verified | completed_onboarding_at |
|--------------------------------|--------------|-----------|-------------|-------------------------|
| <active_verified@example.com>  |              |     ✔️     |      ✔️      |           now()         |
| <needs_onboarding@example.com> |              |     ✔️     |      ✔️      |           NULL          |

All users have the password `password`.
