"""
Minimalist public dashboard for FractalTrader bot monitoring.

Exposes live status on port 8080 for public viewing.
"""

import json
import logging
import subprocess
from datetime import datetime
from pathlib import Path

from flask import Flask, jsonify, render_template_string

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

STATE_FILE = Path("/app/.testnet_state.json")
LOG_FILE = Path("/tmp/bot_v2.log")

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>FractalTrader Monitor</title>
    <meta http-equiv="refresh" content="5">
    <style>
        body {
            font-family: 'Courier New', monospace;
            background: #0a0e27;
            color: #00ff41;
            padding: 20px;
            margin: 0;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        h1 {
            color: #00ff41;
            text-align: center;
            font-size: 2em;
            margin-bottom: 10px;
        }
        .status {
            font-size: 1.2em;
            text-align: center;
            margin-bottom: 20px;
            padding: 10px;
            background: rgba(0,255,65,0.1);
            border-radius: 5px;
        }
        .section {
            background: rgba(255,255,255,0.05);
            padding: 15px;
            margin: 15px 0;
            border-radius: 5px;
            border-left: 3px solid #00ff41;
        }
        .section h2 {
            margin-top: 0;
            color: #00d4ff;
            font-size: 1.3em;
        }
        .metric {
            display: grid;
            grid-template-columns: 200px 1fr;
            margin: 5px 0;
            padding: 5px 0;
        }
        .metric-label {
            color: #888;
        }
        .metric-value {
            color: #00ff41;
            font-weight: bold;
        }
        .log-line {
            font-size: 0.85em;
            padding: 2px 0;
            border-bottom: 1px solid rgba(255,255,255,0.05);
        }
        .log-time {
            color: #00d4ff;
        }
        .log-level-INFO {
            color: #00ff41;
        }
        .log-level-ERROR {
            color: #ff4444;
        }
        .log-level-WARNING {
            color: #ffaa00;
        }
        .footer {
            text-align: center;
            margin-top: 30px;
            color: #555;
            font-size: 0.9em;
        }
        .running {
            color: #00ff41;
        }
        .stopped {
            color: #ff4444;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 FractalTrader Live Monitor</h1>

        <div class="status">
            Status: <span class="{{ status_class }}">{{ status }}</span> |
            Uptime: {{ uptime }} |
            Last Update: {{ timestamp }}
        </div>

        <div class="section">
            <h2>📊 Session Info</h2>
            <div class="metric">
                <span class="metric-label">Started:</span>
                <span class="metric-value">{{ session_start }}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Starting Balance:</span>
                <span class="metric-value">${{ starting_balance }}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Open Positions:</span>
                <span class="metric-value">{{ open_positions }}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Total Trades:</span>
                <span class="metric-value">{{ total_trades }}</span>
            </div>
        </div>

        <div class="section">
            <h2>📈 Recent Activity (Last 50 lines)</h2>
            <div style="max-height: 400px; overflow-y: auto;">
                {% for line in logs %}
                <div class="log-line">{{ line | safe }}</div>
                {% endfor %}
            </div>
        </div>

        <div class="footer">
            Auto-refreshes every 5 seconds | Branch: {{ branch }} | Mode: Simulation
        </div>
    </div>
</body>
</html>
"""


def get_bot_status():
    """Read bot status from state file."""
    if not STATE_FILE.exists():
        return {
            "status": "STOPPED",
            "status_class": "stopped",
            "uptime": "N/A",
            "session_start": "N/A",
            "starting_balance": "0.00",
            "open_positions": 0,
            "total_trades": 0,
        }

    try:
        with open(STATE_FILE) as f:
            state = json.load(f)

        session_start = state.get("session_start", "N/A")
        uptime = "N/A"

        if session_start != "N/A":
            try:
                start_time = datetime.fromisoformat(session_start)
                now = datetime.now()
                delta = now - start_time
                hours = delta.total_seconds() / 3600
                uptime = f"{hours:.1f}h"
            except Exception:
                pass

        return {
            "status": "RUNNING",
            "status_class": "running",
            "uptime": uptime,
            "session_start": session_start,
            "starting_balance": f"{state.get('starting_balance', 0):.2f}",
            "open_positions": len(state.get("open_positions", {})),
            "total_trades": len(state.get("trade_history", [])),
        }
    except Exception as e:
        logger.error(f"Error reading state: {e}")
        return {
            "status": "ERROR",
            "status_class": "stopped",
            "uptime": "N/A",
            "session_start": "N/A",
            "starting_balance": "0.00",
            "open_positions": 0,
            "total_trades": 0,
        }


def get_recent_logs(num_lines=50):
    """Get recent log lines."""
    if not LOG_FILE.exists():
        return ["No logs available"]

    try:
        result = subprocess.run(
            ["tail", f"-{num_lines}", str(LOG_FILE)],
            capture_output=True,
            text=True,
            timeout=5,
        )
        lines = result.stdout.strip().split("\n")

        # Simple formatting
        formatted = []
        for line in lines:
            if not line.strip():
                continue

            # Highlight log levels
            if " - ERROR - " in line:
                formatted.append(f'<span class="log-level-ERROR">{line}</span>')
            elif " - WARNING - " in line:
                formatted.append(f'<span class="log-level-WARNING">{line}</span>')
            else:
                formatted.append(f'<span class="log-level-INFO">{line}</span>')

        return formatted if formatted else ["No recent logs"]
    except Exception as e:
        logger.error(f"Error reading logs: {e}")
        return [f"Error reading logs: {e}"]


def get_current_branch():
    """Get current git branch."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
            cwd="/app",
        )
        return result.stdout.strip()
    except Exception:
        return "unknown"


@app.route("/")
def index():
    """Main dashboard page."""
    status = get_bot_status()
    logs = get_recent_logs()
    branch = get_current_branch()

    return render_template_string(
        HTML_TEMPLATE,
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
        branch=branch,
        logs=logs,
        **status,
    )


@app.route("/api/status")
def api_status():
    """JSON API endpoint."""
    status = get_bot_status()
    return jsonify(status)


if __name__ == "__main__":
    logger.info("Starting FractalTrader dashboard on port 8080...")
    app.run(host="0.0.0.0", port=8080, debug=False)
