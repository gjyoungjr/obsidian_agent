# 🧠 Obsidian Weekly Review Agent

An AI-powered productivity agent that analyzes your Obsidian daily notes and generates comprehensive weekly reviews with a Gen Z vibe.

## Features

- Parses daily notes for habits, priorities (P1/P2/P3), admin tasks, energy, mood, and reflections
- Generates insightful weekly reviews with pattern recognition and actionable advice
- Saves reviews directly to your Obsidian vault
- Emails formatted weekly reviews to your inbox
- Interactive chat mode for follow-up questions

## Installation

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Configuration

Create a `.env` file:

```env
OPENAI_API_KEY=your-api-key
OBSIDIAN_VAULT_PATH=/path/to/your/vault/Daily Actions

# Email (optional - for weekly review emails via Resend)
RESEND_API_KEY=your-resend-api-key
RESEND_SOURCE_EMAIL=reviews@yourdomain.com
EMAIL_TO=your-email@example.com
```

## Usage

```bash
# Full weekly review (default)
python agent.py

# Review past 2 weeks
python agent.py --days 14

# Review + interactive chat after
python agent.py --chat

# Quick 2-sentence vibe check (no save)
python agent.py --quick

# Combine flags
python agent.py --days 14 --chat
```

## Expected Daily Note Format

Your Obsidian daily notes should follow this structure:

```markdown
## 🔁 Habits

- [ ] Gym
- [ ] Read & Research

## 🎯 Priority Tasks
### P1 — Must Do

- [ ] 

### P2 — Should Do

- [ ] 

### P3 — Nice to Have

- [ ] 

## 🧹 Life & Admin

- [ ] 

## ⚡ Energy / Mood

- Energy (1–5): 
- Mood (1–5): 

## 📝 Reflection / Journal

### What did I do today?
-

### What did I learn today?
-

### What stressed me today?
-

### What am I excited about?
-

### What am I worried about?
-

### What would make tomorrow good?
-

### Am I moving forward or just busy?
**Busy with:**
- 

**Moving forward because:**
- 
**Conclusion:** 

## 📊 Daily Score  
Productivity:  4
Focus:  4
Energy:  5
Mood:  3
Progress:4
```

## Email Reviews

To email your weekly review, use chat mode and ask the agent:

```bash
python agent.py --chat
# Then: "Email me this review"
```

Requires [Resend](https://resend.com) API key configured in `.env`.

## Output

Reviews are saved to `Weekly Reviews/` folder in your vault with filenames like `2026-W01.md`, containing stats, wins, blockers, patterns, and actionable next steps.

## Automated Scheduling (Cron Job)

Want the agent to run automatically every week? Set up a cron job:

### 1. Make the runner script executable

```bash
chmod +x run_agent.sh
```

### 2. Open your crontab

```bash
crontab -e
```

### 3. Add a schedule

Pick one of these (or customize):

| Schedule             | Cron Entry                                        |
| -------------------- | ------------------------------------------------- |
| Every Sunday at 9 AM | `0 9 * * 0 /path/to/obsidian_agent/run_agent.sh`  |
| Every Monday at 7 AM | `0 7 * * 1 /path/to/obsidian_agent/run_agent.sh`  |
| Every day at 8 PM    | `0 20 * * * /path/to/obsidian_agent/run_agent.sh` |

Replace `/path/to/obsidian_agent/` with your actual path.

### 4. Verify it's set

```bash
crontab -l
```

### Logs

Cron job output is saved to `logs/agent.log` in the project directory.

> **Note (macOS):** You may need to grant "Full Disk Access" to `/usr/sbin/cron` in **System Settings → Privacy & Security → Full Disk Access** if accessing files outside your home directory.
