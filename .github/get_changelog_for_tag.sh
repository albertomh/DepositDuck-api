#!/usr/bin/env bash

# Given a semver tag, parse the CHANGELOG and
# return the release notes for that tag.
#
# Usage:
#   ./local/get_changelog_for_tag.sh X.Y.Z
#
# (c) 2024 Alberto Morón Hernández


if [ "$#" -ne 1 ]; then
    echo "Usage: $0 "
    exit 1
fi

tag="$1"

SEMVER_REGEX='^[0-9]+\.[0-9]+\.[0-9]+$'
if ! [[ $tag =~ $SEMVER_REGEX ]]; then
    echo "Error: $tag is not a valid semantic version"
    exit 1
fi

changelog_file="CHANGELOG.md"
changes=()

# read changelog from `## [$tag]` to next ## header
start_tag_found=false
while IFS= read -r line; do
    if [[ "$line" == "## [$tag]"* ]]; then
        start_tag_found=true
        # proceed to the next line
        continue
    fi

    if $start_tag_found; then
        # check for the next header
        if [[ "$line" == "## "* ]]; then
            break
        fi
        line="${line//###/#}"  # convert ### to #
        changes+=("$line")
    fi
done < "$changelog_file"

for change in "${changes[@]}"; do
    echo "$change"
done
