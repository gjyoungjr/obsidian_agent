import os
from datetime import datetime
from parser.weekly_parser import (format_weekly_daily_with_reflections,
                                  parse_weekly_notes_combined)
from pathlib import Path

from langchain_core.tools import tool

VAULT_PATH = os.getenv("OBSIDIAN_VAULT_PATH",
                       "/Users/gilbertyoung/documents/notes/Daily Actions")
REVIEW_FOLDER = "Weekly Reviews"


@tool
def get_weekly_review(days_back: int = 7) -> str:
    """
    Fetch and analyze your Obsidian daily notes for the past week.

    Args:
        days_back: Number of days to look back (default: 7 for a full week)

    Returns:
        Formatted weekly summary with habits, priorities, energy, mood, and reflections.
    """
    weekly_stats, daily_data = parse_weekly_notes_combined(
        VAULT_PATH, days_back)
    return format_weekly_daily_with_reflections(daily_data=daily_data, include_weekly_reflections=False)


@tool
def save_to_obsidian(content: str, title: str = None) -> str:
    """
    Save the weekly review to Obsidian vault.

    Args:
        content: The complete markdown content including frontmatter from agent
        title: Optional custom title for the note (defaults to current week number)

    Returns:
        Success message with file path
    """
    try:
        review_path = Path(VAULT_PATH).parent / REVIEW_FOLDER
        review_path.mkdir(exist_ok=True)

        now = datetime.now()
        iso_cal = now.isocalendar()
        year = iso_cal[0]      # ISO year (handles year boundary correctly)
        week_num = iso_cal[1]  # ISO week number

        if title is None:
            title = f"{year}-W{week_num:02d}"

        filename = f"{title}.md"
        filepath = review_path / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        return f"✅ Review saved to: {filepath}"

    except Exception as e:
        return f"❌ Error saving to Obsidian: {str(e)}"
