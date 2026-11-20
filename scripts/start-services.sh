#!/usr/bin/env bash
# Starts the two Docker containers the lab needs, both bound to 127.0.0.1 only:
#   aisr-ollama   the local model server   http://127.0.0.1:18930
#   aisr-mailpit  the fake mail catcher    SMTP 127.0.0.1:18931, web page http://127.0.0.1:18932
# Then downloads the course model (about 1.4 GB, once).
set -euo pipefail

MODEL="${MODEL:-qwen3:1.7b}"

docker network inspect aisr-net >/dev/null 2>&1 || docker network create aisr-net >/dev/null

if ! docker container inspect aisr-ollama >/dev/null 2>&1; then
  docker run -d --name aisr-ollama --network aisr-net \
    -v aisr-ollama-models:/root/.ollama -p 127.0.0.1:18930:11434 ollama/ollama:latest >/dev/null
fi
docker start aisr-ollama >/dev/null

if ! docker container inspect aisr-mailpit >/dev/null 2>&1; then
  docker run -d --name aisr-mailpit --network aisr-net \
    -p 127.0.0.1:18931:1025 -p 127.0.0.1:18932:8025 axllent/mailpit:latest >/dev/null
fi
docker start aisr-mailpit >/dev/null

echo "Waiting for Ollama..."
for _ in $(seq 1 30); do
  if curl -s http://127.0.0.1:18930/api/version >/dev/null; then break; fi
  sleep 1
done
docker exec aisr-ollama ollama pull "$MODEL"
docker exec aisr-ollama ollama list
echo "Services are up: Ollama on 18930, Mailpit on 18932."
