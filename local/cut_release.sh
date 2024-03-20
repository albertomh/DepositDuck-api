#!/usr/bin/env bash

# Cut a release by stamping the CHANGELOG, committing and pushing up to GitHub.
# A GitHub Actions pipeline will detect `release-X.Y.Z` as a release branch
# and will open a PR. Merging this PR will tag main as `X.Y.Z` at the git
# head and push a container to the GitHub Container Registry.
#
# Usage:
#   ./local/cut_release.sh X.Y.Z
#
# (c) 2024 Alberto Morón Hernández

set -ex

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

git stash \
  --all \
  --include-untracked \
  --message "cut_release.sh: stash ahead of $tag"

branch_name="release-$tag"
git checkout -b $branch_name

changelog="CHANGELOG.md"
if [ ! -f "$changelog" ]; then
    echo "Error: '$changelog' not found"
    exit 1
fi

today=$(date +%F)
# NB. in the MacOS version of `sed`, `-i` requires an argument(!)
sed -i '' "s/## \[Unreleased\]/## [Unreleased]\n\n## [$tag] - $today/g" "$changelog"

git commit --all --message "chore: stamp changelog for release $tag"

git push --set-upstream origin $branch_name

git checkout main

git branch --delete $branch_name
