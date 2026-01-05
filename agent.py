# agent.py - Cleaned up version
import os
from datetime import datetime
from parser.weekly_parser import (format_weekly_daily_with_reflections,
                                  parse_weekly_notes_combined)
from pathlib import Path

from deepagents import create_deep_agent
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.tools import tool

from prompt import OPTIMIZED_SYSTEM_PROMPT

load_dotenv()

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


model = init_chat_model(
    model="openai:gpt-4o",
    api_key=os.getenv("OPENAI_API_KEY"),
)

agent = create_deep_agent(
    model=model,
    system_prompt=OPTIMIZED_SYSTEM_PROMPT,
    tools=[get_weekly_review, save_to_obsidian],
)


def generate_and_save_review(days_back: int = 7, interactive: bool = False):
    """Generate review and save to Obsidian"""
    print("🔄 Generating your weekly review...\n")

    result = agent.invoke({
        "messages": [{
            "role": "user",
            "content": f"Please analyze my past {days_back} days, create a comprehensive Gen Z-style weekly review following the exact markdown template format, and save it to Obsidian. Yes generate it only if its two days."
        }]
    })

    response = result["messages"][-1].content
    print(response)

    if interactive:
        print("\n" + "="*60)
        print("💬 Chat Mode: Ask follow-up questions (type 'exit' to quit)")
        print("="*60 + "\n")

        conversation_history = result["messages"]

        while True:
            user_input = input("\n🗣️  You: ").strip()

            if user_input.lower() in ['exit', 'quit', 'done', 'bye']:
                print("\n👋 Later! Keep cooking this week.")
                break

            if not user_input:
                continue

            conversation_history.append({
                "role": "user",
                "content": user_input
            })

            result = agent.invoke({"messages": conversation_history})
            agent_response = result["messages"][-1].content
            conversation_history = result["messages"]

            print(f"\n🤖 Agent: {agent_response}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate and save weekly review to Obsidian")
    parser.add_argument("--days", type=int, default=7,
                        help="Number of days to analyze (default: 7)")
    parser.add_argument("--chat", action="store_true",
                        help="Enable interactive chat mode after review")

    args = parser.parse_args()

    generate_and_save_review(days_back=args.days, interactive=args.chat)
