#!/usr/bin/env bash
# ==============================================================================
# play.sh - One-click launcher for Git Workshop Day 2 Games (Linux & macOS)
# Zero external packages required.
# ==============================================================================

set -e

# Resolve directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check Python 3 availability
if command -v python3 &>/dev/null; then
    exec python3 game.py "$@"
elif command -v python &>/dev/null; then
    exec python game.py "$@"
else
    echo "Error: Python 3 is required to run the Git Workshop Games."
    echo "Please verify Python 3 is installed and added to your PATH."
    exit 1
fi
