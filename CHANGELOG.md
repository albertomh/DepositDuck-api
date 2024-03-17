# Changelog

Notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Two separate FastAPI apps, webapp & apiapp, to keep the API separate from serving the frontend.
- A htmx frontend.
- A dependable that provides access to `structlog` in the FastAPI application.
- A CI pipeline using GitHub actions. Runs pre-commit hooks and tests.
- SAST scanning by adding `bandit` as a pre-commit hook.
