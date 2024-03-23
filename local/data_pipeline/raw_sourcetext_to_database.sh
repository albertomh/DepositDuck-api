#!/bin/bash

# Insert the output of `pdf_to_raw_sourcetext.py` into the database.
#
# Usage:
#  PGPASSWORD=password ./raw_sourcetext_to_database.sh
#
# (c) 2024 Alberto Morón Hernández

set -ex

DB_NAME="depositduck"
TABLE_NAME="llm__source_text"
TEXT_FILE="$(pwd)/local/data_pipeline/sourcetext.tmp"

TEXT=$(cat $TEXT_FILE)
# escape apostrophes using parameter expansion
ESCAPED_TEXT=$(echo "$TEXT" | sed "s/'/''/g")

SQL_COMMAND="INSERT INTO $TABLE_NAME (name, description, content) VALUES ('','', '$ESCAPED_TEXT');"

psql -h localhost -p 5432 -U postgres -d $DB_NAME -c "$SQL_COMMAND"

rm $TEXT_FILE
