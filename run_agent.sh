#!/bin/bash
# Runner script for cron job

# Navigate to project directory
cd /Users/gilbertyoung/Documents/Code/obsidian_agent

# Activate virtual environment
source venv/bin/activate

# Run the agent (non-interactive mode)
python agent.py --days 7

# Optional: Log output with timestamp
# python agent.py --days 7 >> /tmp/obsidian_agent.log 2>&1
