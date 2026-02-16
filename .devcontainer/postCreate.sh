#!/usr/bin/env bash
set -euo pipefail

sudo apt-get update
sudo apt-get install -y --no-install-recommends curl ca-certificates

if ! command -v act >/dev/null 2>&1; then
  ACT_VERSION="v0.2.82"
  curl -sSL "https://github.com/nektos/act/releases/download/${ACT_VERSION}/act_Linux_x86_64.tar.gz" \
    | sudo tar -xz -C /usr/local/bin act
fi

python -m pip install --upgrade pip
python -m pip install pre-commit

pre-commit install || true

echo "Devcontainer setup completed."
echo "Run: ./scripts/validate_ci_local.sh"
