/*
 * Initialisation script for the containerised Postgres instance.
 * For use during development and testing. Also used ahead of running e2e tests in CI.
 * Keep values in sync with `.env`, `.env.test` & `.env.e2e`.
 *
 * (c) 2024 Alberto Morón Hernández
 */

CREATE USER depositduck WITH PASSWORD 'password';
-- needed for user to be able to create extensions (eg. pgvector)
ALTER USER depositduck WITH SUPERUSER;
GRANT ALL ON SCHEMA public TO depositduck;

CREATE DATABASE depositduck;
GRANT ALL PRIVILEGES ON DATABASE depositduck TO depositduck;
ALTER DATABASE depositduck OWNER TO depositduck;

CREATE DATABASE depositduck_test;
GRANT ALL PRIVILEGES ON DATABASE depositduck_test TO depositduck;
ALTER DATABASE depositduck_test OWNER TO depositduck;
