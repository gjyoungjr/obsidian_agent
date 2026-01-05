import os
from parser.weekly_parser import (format_weekly_daily_with_reflections,
                                  parse_weekly_notes_combined)

from deepagents import create_deep_agent
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.tools import tool

from prompt import OPTIMIZED_SYSTEM_PROMPT

load_dotenv()

# Configure your Obsidian vault path
VAULT_PATH = os.getenv("OBSIDIAN_VAULT_PATH",
                       "/Users/gilbertyoung/documents/notes/Daily Actions")


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


model = init_chat_model(
    model="openai:gpt-4o",
    api_key=os.getenv("OPENAI_API_KEY"),
)

agent = create_deep_agent(
    model=model,
    system_prompt=OPTIMIZED_SYSTEM_PROMPT,
    tools=[get_weekly_review],
)

if __name__ == "__main__":
    # Example: Ask for weekly review and planning
    result = agent.invoke({
        "messages": [{
            "role": "user",
            "content": "Please analyze my past week using the weekly review tool and help me plan for this week."
        }]
    })
    print(result["messages"][-1].content)
