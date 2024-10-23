# Models and database

## The 'models' package

The `models` package defines physical and virtual models for entities used in the application.
It contains the following modules:

- `auth`: user authentication.
- `common`: mixins to help build base models and tables elsewhere.
- `deposit`: track deposit recovery cases linked to users.
- `email`: templates and utilities to render and send HTML emails.
- `llm`: models used when interacting with LLMs and storing their output (embeddings, etc.)
- `people`: prospects funnelled away during signup.

And these packages:

- `dto`: Data Transfer Objects building on base models.
- `migrations` (Alembic migrations, see below)
- `sql`: table models inheriting the models defined elsewhere. Uses SQLModel.

Table models are exported in `sql.tables` for convenience.

## Database

The web service is backed by a PostgreSQL instance. Use v15 since this is the latest version
supported by GCP Cloud SQL ([docs](https://cloud.google.com/sql/docs/postgres/db-versions)).
Use the [pgvector](https://hub.docker.com/r/ankane/pgvector/tags) base image to avoid having
to manually install the package in the image every time.

Locally the database is made available via a container. Inspired by the approach described
in [perrygeo.com/dont-install-postgresql-using-containers-for-local-development](https://www.perrygeo.com/dont-install-postgresql-using-containers-for-local-development).

```sh
# follow logs for the containerised PostgreSQL database
just db_logs

# delete the volume backing the local database
# (prefer using `just _wipe_db` followed by `just migrate`)
rm -rf local/database/pgdata/pgdata15
```

The initialisation script for the database is located at `local/database/init-scripts/init.sql`.
It creates a `depositduck` user and two databases:

- `depositduck`: for local development
- `depositduck_test`: for use during integration & e2e tests

### Migrations

Migrations are provided by Alembic. Alembic was initialised with the `async` template to
enable it to use a SQLAlchemy async engine.  
The migrations directory is `depositduck/models/migrations/`.

```sh
# create a migration with the message 'add_person'
just migration "add Person"

# apply the latest migration
# (optionally specify a revision `just migrate <id>`)
just migrate

# revert to the previous migration
# (optionally specify a revision `just downgrade <id>`)
just downgrade
```

### Fixtures

Fixtures with data needed during development and e2e tests can be found in `local/database/init-scripts/`.
These are applied as part of the `just migrate` script.  
The development fixture creates the following users:

| email                          | is_superuser | is_active | is_verified | completed_onboarding_at |
|--------------------------------|--------------|-----------|-------------|-------------------------|
| <admin@example.com>            |       ✔️      |     ✔️     |      ✔️      |           N/A           |
| <active_verified@example.com>  |              |     ✔️     |      ✔️      |           now()         |
| <needs_onboarding@example.com> |              |     ✔️     |      ✔️      |           NULL          |

All users have the password `password`.

See [E2E users](docs/5_test.md#e2e-users) in `docs/5_test.md` for information on users
available during e2e scenarios and how to use these.
