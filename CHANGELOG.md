# Changelog

Notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Two separate FastAPI apps, webapp & apiapp, to keep the API separate from serving the frontend.
- A htmx frontend.
- Bootstrap 5 to style the frontend.
- Configuration to store state in a PostgreSQL database.
- SQLModel as an ORM and Alembic to manage database migrations.
- Dockerised PostgreSQL instance for local development
- A minimal Person model & table.
- A dependable that provides access to `structlog` in the FastAPI application.
- A CI pipeline using GitHub actions. Runs pre-commit hooks and tests for each commit. When
  PRs are merged, in addition to these checks a pipeline Dockerises the app and pushes it
  to the GitHub Container Registry.
- SAST scanning via `bandit` as a pre-commit hook.
