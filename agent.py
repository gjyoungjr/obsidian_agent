import os

from deepagents import create_deep_agent
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

from prompt import OPTIMIZED_SYSTEM_PROMPT
from tools import get_raw_weekly_data, get_weekly_review, save_to_obsidian
from ui import (StreamingCallback, console, print_agent_response,
                print_chat_header, print_error, print_header,
                print_stats_preview, print_success, print_suggestions,
                print_user_prompt)

load_dotenv()


def create_agent(streaming: bool = False):
    """Create the agent with optional streaming support."""
    model_kwargs = {}

    if streaming:
        model_kwargs["streaming"] = True

    model = init_chat_model(
        model="openai:gpt-4o",
        api_key=os.getenv("OPENAI_API_KEY"),
        **model_kwargs
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

    # Create agent and generate review with streaming
    console.print("[cyan]🔄 Generating your weekly review...[/cyan]\n")

    streaming_callback = StreamingCallback()
    agent = create_agent(streaming=True)

    try:
        # Try streaming first
        result = None
        full_response = ""

        # Use stream if available
        try:
            stream = agent.stream({
                "messages": [{
                    "role": "user",
                    "content": f"Please analyze my past {days_back} days, create a comprehensive Gen Z-style weekly review following the exact markdown template format, and save it to Obsidian."
                }]
            })

            console.print("[bold cyan]🤖 Agent:[/bold cyan]")

            for chunk in stream:
                # Handle different chunk formats from the agent
                if isinstance(chunk, dict):
                    messages = chunk.get("messages", [])
                    for msg in messages:
                        if hasattr(msg, "content") and msg.content:
                            # Check if this is new content
                            content = msg.content
                            if content and not content.startswith(full_response):
                                # New content to print
                                new_content = content[len(full_response):] if content.startswith(
                                    full_response[:10]) else content
                                if new_content:
                                    console.print(
                                        new_content, end="", highlight=False)
                                    full_response = content

            console.print()  # Final newline

            # Get final result
            result = chunk if isinstance(chunk, dict) else {"messages": []}

        except (AttributeError, TypeError):
            # Fall back to non-streaming invoke
            console.print(
                "[muted](Streaming not available, using standard generation...)[/muted]\n")
            result = agent.invoke({
                "messages": [{
                    "role": "user",
                    "content": f"Please analyze my past {days_back} days, create a comprehensive Gen Z-style weekly review following the exact markdown template format, and save it to Obsidian."
                }]
            })

            response = result["messages"][-1].content
            print_agent_response(response)

        # Check for success message in the response
        if result and "messages" in result:
            final_msg = result["messages"][-1].content if result["messages"] else ""
            if "✅" in final_msg or "saved" in final_msg.lower():
                console.print()
                print_success("Weekly review generated and saved!")

    except Exception as e:
        print_error(f"Generation failed: {e}")
        return

    # Interactive chat mode
    if interactive:
        print_chat_header()
        print_suggestions()

        conversation_history = result["messages"] if result else []

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

            conversation_history.append({
                "role": "user",
                "content": user_input
            })

            try:
                # Try streaming for chat responses too
                try:
                    stream = agent.stream({"messages": conversation_history})
                    console.print("\n[bold cyan]🤖 Agent:[/bold cyan]")

                    chat_response = ""
                    for chunk in stream:
                        if isinstance(chunk, dict):
                            messages = chunk.get("messages", [])
                            for msg in messages:
                                if hasattr(msg, "content") and msg.content:
                                    content = msg.content
                                    if content and len(content) > len(chat_response):
                                        new_content = content[len(
                                            chat_response):]
                                        console.print(
                                            new_content, end="", highlight=False)
                                        chat_response = content

                    console.print("\n")
                    conversation_history = chunk.get(
                        "messages", conversation_history)

                except (AttributeError, TypeError):
                    result = agent.invoke({"messages": conversation_history})
                    agent_response = result["messages"][-1].content
                    conversation_history = result["messages"]
                    print_agent_response(agent_response)

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

    agent = create_agent(streaming=True)

    try:
        stream = agent.stream({
            "messages": [{
                "role": "user",
                "content": f"Give me a quick 2-3 sentence recap of my past {days_back} days. Keep it super brief and Gen Z style - just the vibes, main wins, and one thing to watch. No need to save to Obsidian."
            }]
        })

        console.print("[bold cyan]🤖 Quick Recap:[/bold cyan]")

        recap = ""
        for chunk in stream:
            if isinstance(chunk, dict):
                messages = chunk.get("messages", [])
                for msg in messages:
                    if hasattr(msg, "content") and msg.content:
                        content = msg.content
                        if len(content) > len(recap):
                            console.print(
                                content[len(recap):], end="", highlight=False)
                            recap = content

        console.print("\n")

    except Exception as e:
        # Fallback
        result = agent.invoke({
            "messages": [{
                "role": "user",
                "content": f"Give me a quick 2-3 sentence recap of my past {days_back} days. Keep it super brief and Gen Z style."
            }]
        })
        print_agent_response(result["messages"][-1].content)


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
