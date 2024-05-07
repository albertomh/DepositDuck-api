# Changelog

Notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

This Changelog is automatically stamped when the `just release <semver>` recipe is invoked
to create a new release.

## [Unreleased]

### Added

- `forms` package to create generic form models powered by Pydantic.

### Changed

- Reject prospect if today is too close to the end of their dispute window.
- Refactor prospect suitability checks to be more composable & reusable.
- Refactor onboarding form to use a Pydantic-based form model.

## [0.5.0] - 2024-05-02

### Added

- Router-level middlewares that redirect users based on their authentication status as
  appropriate.
- Onboarding flow & middleware redirect to onboarding page for users where `completed_onboarding_at`
  is not set.
- Alpine.js to the frontend for light-touch interactivity and client-side validation.
- esbuild to bundle and minify JavaScript scripts into a `main.min.js` file.
- Apply a fixture to the database after running migrations for local development or e2e
  tests as appropriate.

### Changed

- Authentication redirects set 'next' query parameter post-login navigation.
- Prospects are rejected if their tenancy end date is longer than six months away.
- Use speculum@1.5.0 as the frontend toolkit, pulling in Alpine.js.
- Abstract parts of the e2e tests for greater code re-use.
- Routine dependency updates.

## [0.4.0] - 2024-04-25

### Added

- Models and tables to hold data on Prospects, Tenancies.
- Record skeletal Tenancy object for user as part of sign-up flow.
- Form to collect details from currently unsuitable prospects as part of the sign-up
  rejection flow.
- Utilities for date manipulation and comparison.
- Produce coverage reports when unit tests run and display badge in README.

### Changed

- Flesh out prospect filtering on sign-up screen.
- Use speculum@1.4.0 to style the frontend.
- Use MailHog to catch email during development.

## [0.3.0] - 2024-04-18

### Added

- Email-based sign-up and log-in flows.
- fastapi-users as the authentication library.
- An auth__user table to hold user data.
- An auth__access_token table to enable an authentication backend using the database
  strategy and cookie-based transport.
- A UserManager class to centralize authentication logic.
- An auth router for tasks related to authentication.
- `AuthenticatedJinjaBlocks` class to ensure the TemplateResponse context has a request
  and user passed to it. Even if the user is None to denote an unauthenticated request.
- Email templates and utilities to render and send HTML emails.
- An email__email table to track sent emails.
- `/api/healthz/` application & service status endpoint.
- Endpoint to retrieve the n most relevant snippets for a user query.
- [speculum@1.3.0](https://github.com/albertomh/speculum) (re-skinned Bootstrap 5) to style
   the frontend.
- Settings to make static origin & speculum release configurable.
- Playwright for UI end-to-end testing, locally and in merge (CI) pipelines.

### Fixed

- `cut_release.sh` script updates the globals in `depositduck/__init__.py`.

### Changed

- Make the db_session dependable a factory for ease of overriding in tests.
- Refactor the FastAPI app getters in the main module to accept a Settings object for
  flexibility and ease of testing.
- Serve static assets (`speculum`) from a Cloudflare R2 bucket.

###  Removed

- Static assets are no longer tracked in this repo.

## [0.2.0] - 2024-04-03

### Added

- Install the `pgvector` extension in the local Postgres container.
- Another FastAPI app - llmapp - to house generative functionality.
- Models and tables to track:
  - Source texts - full material used as part of Retrieval Augmented Generation.
  - Snippets - small amount of text used for embeddings or included in a prompt context window.
  - Embeddings generated with the Nomic:v1.5 BERT model.
- PoC text extraction pipeline to ingest PDF material for RAG purposes.
- Endpoint to process a SourceText and split into Snippets, storing these in the database.
- Endpoint to generate embeddings for snippets by calling the draLLaM service.

## [0.1.0] - 2024-03-21

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
