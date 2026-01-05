# 🧠 Obsidian Weekly Review Agent

An AI-powered productivity agent that analyzes your Obsidian daily notes and generates comprehensive weekly reviews with a Gen Z vibe.

## Features

- Parses daily notes for habits, priorities (P1/P2/P3), admin tasks, energy, mood, and reflections
- Generates insightful weekly reviews with pattern recognition and actionable advice
- Saves reviews directly to your Obsidian vault
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
```

## Usage

```bash
# Generate a 7-day review
python agent.py

# Custom number of days
python agent.py --days 14

# Enable interactive chat after review
python agent.py --chat
```

## Expected Daily Note Format

Your Obsidian daily notes should follow this structure:

```markdown
## 🔁 Habits

- [x] Exercise
- [ ] Read

### P1

- [x] Important task

### P2

- [ ] Medium priority

### P3

- [ ] Low priority

## 🧹 Life Admin

- [x] Pay bills

## ⚡ Energy & Mood

- Energy: 7
- Mood: 8

## 📝 Reflection

Your daily thoughts here...
```

## Output

Reviews are saved to `Weekly Reviews/` folder in your vault with filenames like `2026-W01.md`, containing stats, wins, blockers, patterns, and actionable next steps.
