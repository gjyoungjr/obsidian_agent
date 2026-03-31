#!/bin/bash
# Runner script for cron job

# Set PATH explicitly for cron environment
export PATH="/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"

# Navigate to project directory
cd /Users/gilbertyoung/Documents/code/personal/obsidian_agent || exit 1


# Create logs directory if it doesn't exist
mkdir -p logs

# Debug log to capture any startup errors
TIMESTAMP=$(/bin/date +"%Y-%m-%d_%H-%M-%S")
DEBUG_LOG="logs/cron_debug_${TIMESTAMP}.log"

{
    echo "=== Cron job started at $(date) ==="
    echo "PWD: $(pwd)"
    echo "PATH: $PATH"
    
    # Activate virtual environment
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
        echo "Venv activated, Python: $(which python)"
    else
        echo "ERROR: venv/bin/activate not found!"
        exit 1
    fi
    
    # Run the agent
    echo "Starting agent..."
    python agent.py --days 7
    echo "=== Cron job finished at $(date) ==="
} >> "$DEBUG_LOG" 2>&1
