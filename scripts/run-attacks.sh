#!/usr/bin/env bash
# Runs every attack in the catalog against one app and prints the success rates.
# Usage: bash scripts/run-attacks.sh vulnerable 10
set -euo pipefail
APP="${1:-vulnerable}"
TRIES="${2:-5}"
PYTHON="${PYTHON:-python}"
for attack in $("$PYTHON" -c "from attacks.catalog import ATTACKS; print(' '.join(a.name for a in ATTACKS))"); do
  "$PYTHON" -m attacks.run "$attack" --app "$APP" --tries "$TRIES" | tail -1 | sed "s/^/$attack: /"
done
