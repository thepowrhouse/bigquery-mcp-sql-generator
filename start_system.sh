#!/usr/bin/env bash
#
# Startup script for the BigQuery MCP system
#

# Activate virtual environment
source .venv/bin/activate

echo "Starting BigQuery MCP System..."

# Start MCP Server in background
echo "Starting MCP Server..."
python src/main.py server &
MCP_PID=$!

# Wait a moment for server to start
sleep 3

# Start Streamlit UI
echo "Starting Streamlit UI..."
python src/main.py ui &
UI_PID=$!

echo "MCP Server PID: $MCP_PID"
echo "Streamlit UI PID: $UI_PID"

# Wait for both processes
wait $MCP_PID
wait $UI_PID