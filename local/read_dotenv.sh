#!/usr/bin/env bash

# Read a dotenv file and export all variables.
#
# Usage:
#   . ./read_dotenv.sh .env
# !important: prefix with 'source' or '.'
#
# (c) 2024 Alberto Morón Hernández

if [ $# -eq 0 ]; then
    echo "Usage: . $0 <dotenv_file>"
    exit 1
fi

dotenv_file="$1"

if [ ! -f "$dotenv_file" ]; then
    echo "Error: file $dotenv_file not found"
    exit 1
fi

if [ -z $CI ]; then
    set -o allexport
    source $dotenv_file
    set +o allexport

else
    env_var_strings=()

    # read the dotenv file line by line
    while IFS= read -r line; do
        # ignore empty lines and comments starting with #
        if [[ -n $line && ! $line =~ ^# ]]; then
            env_var_strings+=("$line")
        fi
    done < $dotenv_file

    # loop over env vars and export to the GitHub Actions context
    for env_var in "${env_var_strings[@]}"; do
        echo "$env_var" >> $GITHUB_ENV
    done
fi
