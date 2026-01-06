#!/bin/bash
# Auto-start script for Fractal Trader bot
# Runs bot in background when container starts

set -e

echo "======================================"
echo "🤖 Fractal Trader Auto-Start"
echo "======================================"

# Wait a few seconds for container to fully initialize
echo "⏳ Waiting for container initialization..."
sleep 5

# Start the bot in the background
echo "🚀 Starting trading bot..."
nohup python3 -m live.cli start --strategy liquidity_sweep > /tmp/bot_autostart.log 2>&1 &

# Give it a moment to start
sleep 3

# Check if bot started successfully
if python3 -m live.cli status > /dev/null 2>&1; then
    echo "✅ Bot started successfully!"
    echo "📊 View logs: tail -f /tmp/bot_v2.log"
else
    echo "⚠️  Bot may not have started. Check logs: cat /tmp/bot_autostart.log"
fi

echo "======================================"
echo "Container ready. Type 'exit' to stop."
echo "======================================"

# Keep container running with interactive bash
exec bash
