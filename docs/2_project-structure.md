# `DepositDuck` project structure

## Packages and modules

DepositDuck is a monolithic FastAPI webapp with a `htmx` frontend generated server-side
via Jinja2 templates.

The project is split into the following packages:

- `api`: operations endpoints that return JSON.
- `auth`: authentication backend (database strategy + cookie transport) and UserManager.
- `dashboard`: dashboard and onboarding
- `email`: email templates and utilities to render and send HTML emails.
- `forms`: Pydantic-powered forms with ergonomic validation and state handling.
- `llm`: language agent functionality eg. ingest data, generate embeddings, etc.
- `models`: Pydantic schemas, SQLModel table definitions and Alembic migrations.
- `people`: track prospects and humans linked to auth users.
- `web`: core FastAPI app on which everything else hangs off. Serves the htmx frontend.

And the following top-level modules:

- `dependables`: callables to be used with FastAPI's dependency injection system.
- `main`: application entrypoint, defines FastAPI apps and attaches routers to these.
- `settings`: application configuration driven by environment variables from a dotenv file.
- `utils`: functions with limited scope that are useful throughout the application.

## Dependables

Callables for use with FastAPI's dependency injection system are made available in the
`dependables` module. These include:

- utilities to access the `structlog` logger
- a configured settings object
- a database session factory
- a Jinja fragments context. Jinja environment config, such as extensions, must be set here.

Packages may contain domain-specific dependables, such as the `auth.dependables` module.

### Router dependables & protected routes

The default assumption for all routes is that they require a logged-in user to be attached
to the request.  
This restriction may be lifted for routes that must be accessible to unauthenticated users
by adding the relevant paths to `FRONTEND_MUST_BE_LOGGED_OUT_PATHS` or `OPERATIONS_MUST_BE_LOGGED_OUT_PATHS`
in the `middleware` module. These lists are used by the auth middlewares, which are included
as router-level dependables and used to filter every request.
