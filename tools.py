import os
from datetime import datetime
from parser.weekly_parser import (format_weekly_daily_with_reflections,
                                  parse_weekly_notes_combined)
from pathlib import Path

from langchain_core.tools import tool

from mailer import send_weekly_email

VAULT_PATH = Path(os.getenv("OBSIDIAN_VAULT_PATH", ""))
REVIEW_FOLDER = "Weekly Reviews"


def get_raw_weekly_data(days_back: int = 7) -> tuple:
    """Get raw weekly data for stats preview (not an agent tool)."""
    return parse_weekly_notes_combined(str(VAULT_PATH), days_back)


@tool
def get_weekly_review(days_back: int = 7) -> str:
    """
    Fetch and analyze your Obsidian daily notes for the past week.

    Args:
        days_back: Number of days to look back (default: 7 for a full week)

    Returns:
        Formatted weekly summary with habits, priorities, energy, mood, and reflections.
    """
    _, daily_data = parse_weekly_notes_combined(str(VAULT_PATH), days_back)
    return format_weekly_daily_with_reflections(
        daily_data=daily_data,
        include_weekly_reflections=False
    )


@tool
def save_to_obsidian(content: str, title: str | None = None) -> str:
    """
    Save the weekly review to Obsidian vault.

    Args:
        content: The complete markdown content including frontmatter from agent
        title: Optional custom title for the note (defaults to current week number)

    Returns:
        Success message with file path
    """
    try:
        review_path = VAULT_PATH.parent / REVIEW_FOLDER
        review_path.mkdir(exist_ok=True)

        if title is None:
            year, week_num, _ = datetime.now().isocalendar()
            title = f"{year}-W{week_num:02d}"

        filepath = review_path / f"{title}.md"
        filepath.write_text(content, encoding="utf-8")

        return f"✅ Review saved to: {filepath}"

    except Exception as e:
        return f"❌ Error saving to Obsidian: {str(e)}"


@tool
def email_weekly_review(review_content: str, week_label: str) -> str:
    """
    Email the weekly review to yourself.

    Args:
        review_content: The weekly review content to email
        week_label: Label for the week (e.g., "Week 3, 2026")

    Returns:
        Success message with email ID or error message
    """
    try:
        to_email = os.getenv("EMAIL_TO", "gilbertjyoungjr@gmail.com")
        result = send_weekly_email(
            to=to_email, review_content=review_content, week_label=week_label)
        return f"✅ Email sent! ID: {result['id']}"
    except Exception as e:
        return f"❌ Error sending email: {str(e)}"
