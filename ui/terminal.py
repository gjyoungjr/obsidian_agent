"""Rich terminal UI utilities for the Obsidian Agent."""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown
from rich.text import Text
from rich.live import Live
from rich.spinner import Spinner
from rich.style import Style
from rich.theme import Theme
from langchain_core.callbacks import BaseCallbackHandler
from typing import Any

# Custom theme for consistent styling
custom_theme = Theme({
    "info": "cyan",
    "success": "green",
    "warning": "yellow",
    "error": "red bold",
    "highlight": "magenta",
    "muted": "dim white",
})

console = Console(theme=custom_theme)


def print_header(days: int = 7):
    """Print the app header with branding."""
    header = Text()
    header.append("✨ ", style="yellow")
    header.append("Obsidian Weekly Review Agent", style="bold cyan")
    header.append(" ✨", style="yellow")
    
    console.print()
    console.print(Panel(
        header,
        subtitle=f"[muted]Analyzing your past {days} days[/muted]",
        border_style="cyan",
        padding=(0, 2),
    ))
    console.print()


def print_stats_preview(daily_data: list, weekly_stats: dict = None):
    """Print a quick stats preview panel before full generation."""
    
    # Calculate stats from daily_data
    days_found = len(daily_data)
    
    # Habits
    total_habits_done = 0
    total_habits_total = 0
    habit_names = set()
    
    for day in daily_data:
        for habit, val in day.get("habits", {}).items():
            habit_names.add(habit)
            total_habits_done += val.get("done", 0)
            total_habits_total += val.get("total", 0)
    
    habit_rate = (total_habits_done / total_habits_total * 100) if total_habits_total else 0
    
    # Priorities
    p1_done, p1_total = 0, 0
    p2_done, p2_total = 0, 0
    p3_done, p3_total = 0, 0
    
    for day in daily_data:
        priorities = day.get("priorities", {})
        p1_done += priorities.get("P1", {}).get("done", 0)
        p1_total += priorities.get("P1", {}).get("total", 0)
        p2_done += priorities.get("P2", {}).get("done", 0)
        p2_total += priorities.get("P2", {}).get("total", 0)
        p3_done += priorities.get("P3", {}).get("done", 0)
        p3_total += priorities.get("P3", {}).get("total", 0)
    
    p1_rate = (p1_done / p1_total * 100) if p1_total else 0
    
    # Energy & Mood
    energies = [d["energy"] for d in daily_data if d.get("energy") is not None]
    moods = [d["mood"] for d in daily_data if d.get("mood") is not None]
    
    avg_energy = sum(energies) / len(energies) if energies else 0
    avg_mood = sum(moods) / len(moods) if moods else 0
    
    # Reflections count
    total_reflections = sum(len(d.get("reflections", [])) for d in daily_data)
    
    # Build the table
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Label", style="muted")
    table.add_column("Value", style="bold")
    table.add_column("Visual", style="cyan")
    
    # Days found
    days_emoji = "✅" if days_found >= 5 else "⚠️" if days_found >= 3 else "❌"
    table.add_row("Days Found", f"{days_found}/7", days_emoji)
    
    # Habits
    habit_bar = _progress_bar(habit_rate)
    habit_style = "green" if habit_rate >= 70 else "yellow" if habit_rate >= 50 else "red"
    table.add_row("Habits", f"[{habit_style}]{habit_rate:.0f}%[/{habit_style}]", habit_bar)
    
    # P1 Tasks
    p1_bar = _progress_bar(p1_rate)
    p1_style = "green" if p1_rate >= 80 else "yellow" if p1_rate >= 60 else "red"
    table.add_row("P1 Tasks", f"[{p1_style}]{p1_rate:.0f}%[/{p1_style}]", p1_bar)
    
    # Energy
    energy_bar = _rating_bar(avg_energy, 10)
    energy_style = "green" if avg_energy >= 7 else "yellow" if avg_energy >= 5 else "red"
    table.add_row("Avg Energy", f"[{energy_style}]{avg_energy:.1f}/10[/{energy_style}]", energy_bar)
    
    # Mood
    mood_bar = _rating_bar(avg_mood, 10)
    mood_style = "green" if avg_mood >= 7 else "yellow" if avg_mood >= 5 else "red"
    table.add_row("Avg Mood", f"[{mood_style}]{avg_mood:.1f}/10[/{mood_style}]", mood_bar)
    
    # Reflections
    table.add_row("Reflections", str(total_reflections), "📝")
    
    console.print(Panel(
        table,
        title="[bold cyan]📊 Quick Stats Preview[/bold cyan]",
        border_style="cyan",
        padding=(1, 2),
    ))
    console.print()


def _progress_bar(percentage: float, width: int = 10) -> str:
    """Create a simple progress bar."""
    filled = int(percentage / 100 * width)
    empty = width - filled
    return f"[green]{'█' * filled}[/green][dim]{'░' * empty}[/dim]"


def _rating_bar(value: float, max_val: int = 10, width: int = 10) -> str:
    """Create a rating bar for scores like energy/mood."""
    filled = int(value / max_val * width)
    empty = width - filled
    return f"[cyan]{'●' * filled}[/cyan][dim]{'○' * empty}[/dim]"


def print_generating_spinner():
    """Return a Live context manager with a spinner for generation."""
    return Live(
        Spinner("dots", text="[cyan] Generating your weekly review...[/cyan]"),
        console=console,
        refresh_per_second=10,
    )


def print_success(message: str, filepath: str = None):
    """Print a success message."""
    if filepath:
        console.print(Panel(
            f"[green]{message}[/green]\n\n[muted]📁 {filepath}[/muted]",
            title="[bold green]✅ Success[/bold green]",
            border_style="green",
        ))
    else:
        console.print(f"[success]✅ {message}[/success]")


def print_error(message: str):
    """Print an error message."""
    console.print(Panel(
        f"[red]{message}[/red]",
        title="[bold red]❌ Error[/bold red]",
        border_style="red",
    ))


def print_chat_header():
    """Print the interactive chat mode header."""
    console.print()
    console.rule("[bold cyan]💬 Chat Mode[/bold cyan]", style="cyan")
    console.print("[muted]Ask follow-up questions about your review (type 'exit' to quit)[/muted]")
    console.print()


def print_suggestions():
    """Print suggested follow-up questions."""
    suggestions = [
        "Why was my energy low on [day]?",
        "What habit should I prioritize next week?",
        "Give me a pep talk based on this week",
        "What patterns do you see in my reflections?",
    ]
    
    console.print("\n[bold cyan]💡 Try asking:[/bold cyan]")
    for i, suggestion in enumerate(suggestions, 1):
        console.print(f"  [muted]{i}.[/muted] [italic]{suggestion}[/italic]")
    console.print()


def print_agent_response(response: str):
    """Print the agent's response with nice formatting."""
    console.print()
    # Try to render as markdown if it looks like markdown
    if any(marker in response for marker in ['#', '**', '- ', '> ']):
        console.print(Markdown(response))
    else:
        console.print(response)
    console.print()


def print_user_prompt() -> str:
    """Print the user input prompt and get input."""
    console.print("[bold green]🗣️  You:[/bold green] ", end="")
    return input().strip()


class StreamingCallback(BaseCallbackHandler):
    """Callback handler for streaming LLM responses to terminal."""
    
    def __init__(self):
        self.text = ""
        self.live = None
        self._started = False
    
    def on_llm_start(self, *args, **kwargs):
        """Called when LLM starts generating."""
        self._started = True
        console.print("\n[bold cyan]🤖 Agent:[/bold cyan]")
    
    def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        """Called for each new token from the LLM."""
        self.text += token
        console.print(token, end="", highlight=False)
    
    def on_llm_end(self, *args, **kwargs):
        """Called when LLM finishes generating."""
        if self._started:
            console.print()  # New line after streaming
            self._started = False
    
    def on_llm_error(self, error: Exception, **kwargs: Any) -> None:
        """Called if LLM errors."""
        console.print(f"\n[error]Error: {error}[/error]")


class SimpleStreamPrinter:
    """Simple streaming printer that works with any agent."""
    
    def __init__(self):
        self.buffer = ""
    
    def start(self):
        """Start streaming output."""
        console.print("\n[bold cyan]🤖 Agent:[/bold cyan]")
    
    def print_token(self, token: str):
        """Print a single token."""
        console.print(token, end="", highlight=False)
        self.buffer += token
    
    def end(self):
        """End streaming output."""
        console.print()  # Final newline
        return self.buffer


