#!/bin/bash
# ── 1PAX Chatbot Startup Script ────────────────────────────────────────────
# Starts the action server + rasa shell with a single command.
# Usage: ./start.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

source .venv/bin/activate

echo ""
echo "  Starting 1PAX chatbot..."
echo ""

# Kill anything already on port 5055
lsof -ti:5055 | xargs kill -9 2>/dev/null || true

# Start the action server in the background
rasa run actions --port 5055 > /tmp/rasa_actions.log 2>&1 &
ACTION_PID=$!

# Wait for action server to be ready
echo "  Waiting for action server..."
for i in {1..15}; do
    if grep -q "Action endpoint is up and running" /tmp/rasa_actions.log 2>/dev/null; then
        echo "  Action server ready."
        break
    fi
    sleep 1
done

echo ""

# Start rasa shell in the foreground
# When user exits (Ctrl+C or /stop), kill the action server too
trap "kill $ACTION_PID 2>/dev/null; echo ''; echo '  Servers stopped.'; exit 0" INT TERM EXIT

rasa shell
