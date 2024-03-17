#!/usr/bin/env bash
#
# When running this script the working directory must be `local/database/`.
#
# Once the database is up, connect with:
#   docker exec -it depositduck_db psql postgresql://postgres:password@localhost:5432/depositduck
#     OR
#   PGPASSWORD=password psql -h localhost -p 5432 -U postgres -d depositduck
#
# (c) 2024 Alberto Morón Hernández

set -e

# read .env and export its contents as environment variables
# this is the source of variables prefixed with 'DB_'
set -o allexport
source ../../.env
set +o allexport

IMAGE=postgres:15-alpine
NAME=depositduck_db

docker run --rm \
  --name $NAME \
  --volume ./pgdata:/var/lib/postgresql/data \
  --volume ./mnt_data:/mnt/data \
  --volume ./pg_hba.conf:/etc/postgresql/pg_hba.conf \
  --volume ./postgresql.conf:/etc/postgresql/postgresql.conf \
  -e PGDATA=/var/lib/postgresql/data/pgdata15 \
  -e POSTGRES_INITDB_ARGS="--data-checksums --encoding=UTF8" \
  -e POSTGRES_USER=${DB_USER} \
  -e POSTGRES_PASSWORD=${DB_PASSWORD} \
  -e POSTGRES_DB=${DB_NAME} \
  -p ${DB_PORT}:5432 \
  ${IMAGE} \
  postgres \
    -c 'hba_file=/etc/postgresql/pg_hba.conf' \
    -c 'config_file=/etc/postgresql/postgresql.conf'
