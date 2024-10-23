# Continuous Integration

## GitHub Actions CI

Continuous Integration pipelines run via GitHub Actions on push.  
Pipelines are defined by YAML files in the `.github/workflows/` directory.
There are two workflows:

- `pr.yaml`: when a commit on a feature branch is pushed up to GitHub.
- `ci.yaml`: when a Pull Request is merged into the 'main' branch.

They both run pre-commit hooks and unit tests against the codebase.

## Continuous Delivery

⚠️ This section is WIP.

### Cut a release and push to Container Registry

1. Check out the `main` branch.
1. Pick the semantic version (`M.m.p`) for the release.
1. Run `just release M.m.p`  
   This stamps the changelog & updates the semver globals in `depositduck/__init__.py`.
   It also triggers a GitHub pipeline that automates the rest of the release.
1. Wait for the pipeline to succeed. It will have raised a PR for this release.
1. Review and merge (merge-and-rebase) the PR.
1. This will trigger a pipeline that tags the `main` branch, creates a GitHub release,
   builds a container and pushes it to the GitHub Container Registry.
1. Wait for the pipeline to succeed and check a new tagged Docker container is available
   in the project's [container registry](https://github.com/albertomh/DepositDuck/pkgs/container/depositduck%2Fmain).

`ci.yaml` additionally
runs end-to-end Playwright tests, Dockerises the app and pushes the image to the GitHub
Container Registry. The build artefact is a multi-arch Docker image to ensure compatibility
with both Apple Silicon (ARM64) and GCP Cloud Run (x86_64).

## Run a Container Registry image locally

To run a Docker image from the Container Registry locally:

```sh
# 1. Visit https://github.com/settings/tokens/new?scopes=write:packages

# 2. Select all relevant `packages` scopes and create
#    a new Personal Access Token (PAT).

# 3. Save the PAT as an environment variable:
export GHCR_PAT=YOUR_TOKEN

# 4. Sign in to the Container Registry:
echo $GHCR_PAT | docker login ghcr.io -u USERNAME --password-stdin

# 5. Pull the latest image
docker pull ghcr.io/albertomh/depositduck/main:latest

# 6. Run the webapp on port 80
docker run \
  --rm \
  --detach \
  --read-only \
  --volume ./.env:/app/.env \
  --publish 80:80 \
  --name depositduck_web \
  ghcr.io/albertomh/depositduck/main

# 7. Stop the container
docker stop depositduck_web
```
