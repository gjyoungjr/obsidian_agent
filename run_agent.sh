#!/bin/bash
# Runner script for cron job

# Navigate to project directory
cd /Users/gilbertyoung/Documents/Code/obsidian_agent

# Activate virtual environment
source venv/bin/activate

# Create logs directory if it doesn't exist
mkdir -p logs

# Run the agent with timestamped logging
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
python agent.py --days 7 >> "logs/agent_${TIMESTAMP}.log" 2>&1
