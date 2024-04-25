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

if (( percentage >= 0 && percentage < 50 )); then
    colour="F24F4F" # red
elif (( percentage >= 50 && percentage < 70 )); then
    colour="EF8354" # orange
elif (( percentage >= 70 && percentage < 85 )); then
    colour="EADF6C" # yellow
elif (( percentage >= 85 && percentage <= 100 )); then
    colour="29AB47" # green
fi

sed -i '' -E "s/coverage-[0-9]+%25.+\?/coverage-$percentage%25-$colour?/" $readme
