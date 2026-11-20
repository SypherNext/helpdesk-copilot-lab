#!/usr/bin/env bash
# Stops and removes the lab containers. The downloaded model stays in the
# aisr-ollama-models volume; delete it with: docker volume rm aisr-ollama-models
set -uo pipefail
docker rm -f aisr-ollama aisr-mailpit >/dev/null 2>&1
docker network rm aisr-net >/dev/null 2>&1
echo "Lab containers removed."
