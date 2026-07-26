#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

for test_file in "$SCRIPT_DIR"/test-*.sh; do
    echo ">>> $test_file"
    bash "$test_file"
done
