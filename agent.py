import os

from deepagents import create_deep_agent
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

from prompt import OPTIMIZED_SYSTEM_PROMPT
from tools import get_raw_weekly_data, get_weekly_review, save_to_obsidian
from ui import (console, print_agent_response, print_chat_header, print_error,
                print_header, print_stats_preview, print_success,
                print_suggestions, print_user_prompt)

load_dotenv()


def create_agent():
    """Create the deep agent with tools."""
    model = init_chat_model(
        model="openai:gpt-4o",
        api_key=os.getenv("OPENAI_API_KEY"),
    )

    return create_deep_agent(
        model=model,
        system_prompt=OPTIMIZED_SYSTEM_PROMPT,
        tools=[get_weekly_review, save_to_obsidian],
    )


def generate_and_save_review(days_back: int = 7, interactive: bool = False):
    """Generate review and save to Obsidian with rich terminal UI."""

    # Print header
    print_header(days_back)

    # Show stats preview
    console.print("[muted]Fetching your notes...[/muted]")
    try:
        weekly_stats, daily_data = get_raw_weekly_data(days_back)

        if not daily_data:
            print_error(f"No daily notes found for the past {days_back} days!")
            console.print(
                "[muted]Make sure your OBSIDIAN_VAULT_PATH is set correctly.[/muted]")
            return

        print_stats_preview(daily_data, weekly_stats)
    except Exception as e:
        print_error(f"Failed to fetch notes: {e}")
        return

    # Create agent and generate review
    console.print("[cyan]🔄 Generating your weekly review...[/cyan]\n")

    agent = create_agent()

    initial_prompt = f"Please analyze my past {days_back} days, create a comprehensive Gen Z-style weekly review following the exact markdown template format, and save it to Obsidian."
    response = ""

    try:
        result = agent.invoke({
            "messages": [{
                "role": "user",
                "content": initial_prompt
            }]
        })

        # Extract the response
        messages = result.get("messages", [])
        if messages:
            last_msg = messages[-1]
            response = last_msg.content if hasattr(
                last_msg, "content") else last_msg.get("content", "")
            console.print("[bold cyan]🤖 Agent:[/bold cyan]")
            print_agent_response(response)

            if "✅" in response or "saved" in response.lower():
                print_success("Weekly review generated and saved!")

    except Exception as e:
        print_error(f"Generation failed: {e}")
        return

    # Interactive chat mode
    if interactive:
        print_chat_header()
        print_suggestions()

        # Start with context from the review
        conversation_history = [
            {"role": "user", "content": initial_prompt},
            {"role": "assistant", "content": response}
        ]

        while True:
            try:
                user_input = print_user_prompt()
            except (EOFError, KeyboardInterrupt):
                console.print(
                    "\n\n[cyan]👋 Later! Keep cooking this week.[/cyan]")
                break

            if user_input.lower() in ['exit', 'quit', 'done', 'bye', '']:
                if user_input == '':
                    continue
                console.print(
                    "\n[cyan]👋 Later! Keep cooking this week.[/cyan]")
                break

            conversation_history.append(
                {"role": "user", "content": user_input})

            try:
                chat_result = agent.invoke({"messages": conversation_history})

                # Extract response
                chat_messages = chat_result.get("messages", [])
                if chat_messages:
                    last_msg = chat_messages[-1]
                    agent_response = last_msg.content if hasattr(
                        last_msg, "content") else last_msg.get("content", "")
                    console.print("\n[bold cyan]🤖 Agent:[/bold cyan]")
                    print_agent_response(agent_response)

                    conversation_history.append(
                        {"role": "assistant", "content": agent_response})

            except Exception as e:
                print_error(f"Chat error: {e}")


def quick_recap(days_back: int = 7):
    """Get a quick 2-3 sentence recap instead of full review."""
    print_header(days_back)

    console.print("[muted]Fetching your notes...[/muted]")
    weekly_stats, daily_data = get_raw_weekly_data(days_back)

    if not daily_data:
        print_error(f"No daily notes found for the past {days_back} days!")
        return

    print_stats_preview(daily_data, weekly_stats)

    console.print("[cyan]🔄 Generating quick recap...[/cyan]\n")

    agent = create_agent()

    try:
        result = agent.invoke({
            "messages": [{
                "role": "user",
                "content": f"Give me a quick 2-3 sentence recap of my past {days_back} days. Keep it super brief and Gen Z style - just the vibes, main wins, and one thing to watch. No need to save to Obsidian."
            }]
        })

        messages = result.get("messages", [])
        if messages:
            last_msg = messages[-1]
            response = last_msg.content if hasattr(
                last_msg, "content") else last_msg.get("content", "")
            console.print("[bold cyan]🤖 Quick Recap:[/bold cyan]")
            print_agent_response(response)

    except Exception as e:
        print_error(f"Quick recap failed: {e}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate and save weekly review to Obsidian",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python agent.py                  # Full weekly review
  python agent.py --days 14        # Review past 2 weeks  
  python agent.py --chat           # Review + interactive chat
  python agent.py --quick          # Quick 2-sentence recap
        """
    )
    parser.add_argument("--days", type=int, default=7,
                        help="Number of days to analyze (default: 7)")
    parser.add_argument("--chat", action="store_true",
                        help="Enable interactive chat mode after review")
    parser.add_argument("--quick", action="store_true",
                        help="Quick recap mode (2-3 sentences, no save)")

    args = parser.parse_args()

    if args.quick:
        quick_recap(days_back=args.days)
    else:
        generate_and_save_review(days_back=args.days, interactive=args.chat)
