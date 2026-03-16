#!/bin/bash
# ── 1PAX Chatbot Startup Script ────────────────────────────────────────────
# Starts the action server + rasa API + local UI server.
# Usage: ./start.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Load environment variables from .env if present
if [ -f "$SCRIPT_DIR/.env" ]; then
    set -a
    source "$SCRIPT_DIR/.env"
    set +a
fi

PYTHON="$SCRIPT_DIR/.venv/bin/python3"

echo ""
echo "  Starting 1PAX chatbot..."
echo ""

# Kill anything already on relevant ports
lsof -ti:5055 | xargs kill -9 2>/dev/null || true
lsof -ti:5005 | xargs kill -9 2>/dev/null || true
lsof -ti:8080 | xargs kill -9 2>/dev/null || true
sleep 1

# Start the action server in the background
"$PYTHON" -m rasa run actions --port 5055 > /tmp/rasa_actions.log 2>&1 &
ACTION_PID=$!

# Wait for action server to be ready
echo "  Waiting for action server..."
for i in {1..20}; do
    if grep -q "Action endpoint is up and running" /tmp/rasa_actions.log 2>/dev/null; then
        echo "  Action server ready."
        break
    fi
    sleep 1
done

# Serve the chat UI on port 8080
"$PYTHON" -m http.server 8080 --directory "$SCRIPT_DIR/ui" > /tmp/rasa_ui.log 2>&1 &
UI_PID=$!

echo ""
echo "  ✅ Chat UI → http://localhost:8080"
echo "  ✅ API     → http://localhost:5005"
echo ""

# Kill all servers on exit
trap "kill $ACTION_PID $UI_PID 2>/dev/null; echo ''; echo '  Servers stopped.'; exit 0" INT TERM EXIT

# Start Rasa API in the foreground
"$PYTHON" -m rasa run --enable-api --cors "*" --port 5005 --endpoints endpoints.yml
