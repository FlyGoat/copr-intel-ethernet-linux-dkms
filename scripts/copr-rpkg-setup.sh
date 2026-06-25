#!/usr/bin/env bash
set -euo pipefail

repo="${COPR_REPO:-flygoat/intel-ethernet-linux-dkms}"
clone_url="${CLONE_URL:-https://github.com/FlyGoat/copr-intel-ethernet-linux-dkms.git}"
branch="${BRANCH:-main}"

packages=(
  "ice-dkms:ice-dkms.spec"
  "iavf-dkms:iavf-dkms.spec"
)

for item in "${packages[@]}"; do
  name="${item%%:*}"
  spec="${item##*:}"

  if copr-cli get-package "$repo" --name "$name" >/dev/null 2>&1; then
    copr-cli edit-package-scm "$repo" \
      --name "$name" \
      --clone-url "$clone_url" \
      --commit "$branch" \
      --spec "$spec" \
      --type git \
      --method rpkg
  else
    copr-cli add-package-scm "$repo" \
      --name "$name" \
      --clone-url "$clone_url" \
      --commit "$branch" \
      --spec "$spec" \
      --type git \
      --method rpkg
  fi
done
