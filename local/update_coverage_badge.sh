#!/usr/bin/env bash

# Run coverage and use result to update the coverage badge in the README.
#
# Usage:
#   ./local/update_coverage_badge.sh
#
# (c) 2024 Alberto Morón Hernández

set -ex

readme="README.md"
if [ ! -f "$readme" ]; then
    echo "Error: '$readme' not found"
    exit 1
fi

percentage=$(just coverage | tail -n 1 | awk '{ print $NF }' | sed 's/\%//')

sed -i '' -E "s/coverage-[0-9]+/coverage-$percentage/" $readme
