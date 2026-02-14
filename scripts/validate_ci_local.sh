#!/usr/bin/env bash
set -euo pipefail

if ! command -v act >/dev/null 2>&1; then
  echo "Error: 'act' is not installed. Rebuild/open the devcontainer or install act manually."
  exit 1
fi

if [[ ! -S /var/run/docker.sock ]]; then
  echo "Error: Docker socket not available. Ensure Docker Desktop is running and devcontainer has docker access."
  exit 1
fi

echo "Running HACS validation workflow locally..."
act pull_request -W .github/workflows/validate.yml

echo "Running Hassfest workflow locally..."
act pull_request -W .github/workflows/hassfest.yml

echo "All local CI validations completed."
