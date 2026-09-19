#!/usr/bin/env bash
# Buduje obrazy fabryki i ładuje je do kind. Bez rejestru: obrazy żyją w Twoim Dockerze i w klastrze.
#   fabryka-toolbox   kroki linii (java, maven, python, git, gitleaks, cosign)
#   fabryka-warsztat  serwer MCP dla agenta (toolbox + mcp)
set -euo pipefail
cd "$(dirname "$0")/.."
. scripts/workshop.env
arch=$(uname -m); [ "$arch" = "x86_64" ] && arch=amd64; [ "$arch" = "aarch64" ] && arch=arm64
docker build -q --build-arg TARGETARCH="$arch" -t "fabryka-toolbox:$IMAGE_TAG" platforma/toolbox
docker build -q --build-arg BASE="fabryka-toolbox:$IMAGE_TAG" -t "fabryka-warsztat:$IMAGE_TAG" platforma/warsztat
kind load docker-image --name "$KIND_CLUSTER" "fabryka-toolbox:$IMAGE_TAG" "fabryka-warsztat:$IMAGE_TAG"
echo "obrazy w klastrze: fabryka-toolbox:$IMAGE_TAG fabryka-warsztat:$IMAGE_TAG"
