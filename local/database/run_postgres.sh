#!/usr/bin/env bash

# Boilerplate to initialise the Postgres container.
# Will create as many databases as there are scripts for in the `local/database/init_scripts/`
# directory. Should be at least two: one for development, another for testing.
#
# Once the database is up, connect with:
#   docker exec -it depositduck_db psql postgresql://postgres:password@localhost:5432/depositduck
#     OR
#   PGPASSWORD=password psql -h localhost -p 5432 -U postgres -d depositduck
#
# (c) 2024 Alberto Morón Hernández

set -evx

script_dir=$(dirname "$0")
PG_VERSION=15
IMAGE="pgvector/pgvector:pg$PG_VERSION"
CONTAINER_NAME=depositduck_db

docker stop $CONTAINER_NAME || true

docker run \
  --rm \
  --detach \
  --name $CONTAINER_NAME \
  --volume $script_dir/pgdata:/var/lib/postgresql/data \
  --volume $script_dir/mnt_data:/mnt/data \
  --volume $script_dir/pg_hba.conf:/etc/postgresql/pg_hba.conf \
  --volume $script_dir/postgresql.conf:/etc/postgresql/postgresql.conf \
  --volume $script_dir/init_scripts:/docker-entrypoint-initdb.d \
  -e PGDATA=/var/lib/postgresql/data/pgdata15 \
  -e POSTGRES_INITDB_ARGS="--data-checksums --encoding=UTF8" \
  -e POSTGRES_PASSWORD=${DB_PASSWORD} \
  -p ${DB_PORT}:5432 \
  ${IMAGE} \
  postgres \
    -c 'hba_file=/etc/postgresql/pg_hba.conf' \
    -c 'config_file=/etc/postgresql/postgresql.conf'

