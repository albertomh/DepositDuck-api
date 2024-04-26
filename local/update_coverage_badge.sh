#!/usr/bin/env bash

# Run coverage and use result to update the coverage badge in the README.
#
# Usage:
#   ./local/update_coverage_badge.sh <PERCENT_INTEGER>
#
# (c) 2024 Alberto Morón Hernández

set -ex

readme="README.md"
if [ ! -f "$readme" ]; then
    echo "Error: '$readme' not found"
    exit 1
fi


if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <PERCENT_INTEGER>"
    exit 1
fi

percentage="$1"

percentage_regex='^[0-9]{1,2}$'
if ! [[ $percentage =~ $percentage_regex ]]; then
    echo "Error: please provide percent coverage as the first and only argument"
    exit 1
fi

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
