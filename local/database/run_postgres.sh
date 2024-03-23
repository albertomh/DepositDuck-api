#!/usr/bin/env bash

# Usage:
# ```
# ./local/database/run_postgres.sh .env
# ```
#
# Once the database is up, connect with:
#   docker exec -it depositduck_db psql postgresql://postgres:password@localhost:5432/depositduck
#     OR
#   PGPASSWORD=password psql -h localhost -p 5432 -U postgres -d depositduck
#
# (c) 2024 Alberto Morón Hernández

set -e

if [ $# -eq 0 ]; then
    echo "Usage: $0 <dotenv_file>"
    exit 1
fi

script_dir=$(dirname "$0")
dotenv_file="$1"

if [ ! -f "$dotenv_file" ]; then
    echo "Error: file $dotenv_file not found"
    exit 1
fi

# read .env and export its contents as environment variables
# this is the source of variables prefixed with 'DB_'
. $script_dir/../read_dotenv.sh $dotenv_file

PG_VERSION=15
IMAGE="postgres:$PG_VERSION-bookworm"
NAME=depositduck_db

docker stop $NAME || true

docker run --rm \
  --detach \
  --name $NAME \
  --volume $script_dir/pgdata:/var/lib/postgresql/data \
  --volume $script_dir/mnt_data:/mnt/data \
  --volume $script_dir/pg_hba.conf:/etc/postgresql/pg_hba.conf \
  --volume $script_dir/postgresql.conf:/etc/postgresql/postgresql.conf \
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

PGVECTOR="postgresql-$PG_VERSION-pgvector"
docker exec $NAME apt-get update
docker exec $NAME apt-get install $PGVECTOR

docker logs --follow $NAME
