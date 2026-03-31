import datetime
import os
from collections import defaultdict

REFLECTION_SECTION_MAP = {
    "what did i do today?": "did_today",
    "what did i learn today?": "learned_today",
    "what stressed me today?": "stressed_today",
    "what am i excited about?": "excited_about",
    "what am i worried about?": "worried_about",
    "what would make tomorrow good?": "tomorrow_good",
    "am i moving forward or just busy?": "forward_or_busy",
    "busy with:": "busy_with",
    "moving forward because:": "moving_forward_because",
    "conclusion:": "forward_busy_conclusion",
}

REFLECTION_OUTPUT_LABELS = {
    "did_today": "What did I do today?",
    "learned_today": "What did I learn today?",
    "stressed_today": "What stressed me today?",
    "excited_about": "What am I excited about?",
    "worried_about": "What am I worried about?",
    "tomorrow_good": "What would make tomorrow good?",
    "forward_or_busy": "Am I moving forward or just busy?",
    "busy_with": "Busy with:",
    "moving_forward_because": "Moving forward because:",
    "forward_busy_conclusion": "Conclusion:",
}


def parse_weekly_notes_combined(vault_path, days_back=7):
    """
    Parse Obsidian daily notes for the last `days_back` days.

    Returns:
        weekly_stats: dict with aggregated weekly stats (habits, priorities, admin, energy, mood)
        daily_data: list of dicts with per-day stats, energy, mood, and reflections
    """
    today = datetime.date.today()
    days = [(today - datetime.timedelta(days=i)).isoformat()
            for i in range(days_back)]

    # Weekly aggregates
    weekly_stats = {
        "habits": defaultdict(lambda: {"done": 0, "total": 0}),
        "priorities": {
            "P1": {"done": 0, "total": 0},
            "P2": {"done": 0, "total": 0},
            "P3": {"done": 0, "total": 0},
        },
        "admin": {"done": 0, "total": 0},
        "energy": [],
        "mood": [],
        "daily_score": {
            "productivity": [],
            "focus": [],
            "energy": [],
            "mood": [],
            "progress": [],
        },
    }

    daily_data = []

    for day in reversed(days):  # oldest -> newest
        path = os.path.join(vault_path, f"{day}.md")
        if not os.path.exists(path):
            continue

        # Daily stats
        stats = {
            "habits": defaultdict(lambda: {"done": 0, "total": 0}),
            "priorities": {
                "P1": {"done": 0, "total": 0},
                "P2": {"done": 0, "total": 0},
                "P3": {"done": 0, "total": 0},
            },
            "admin": {"done": 0, "total": 0},
            "energy": None,
            "mood": None,
            "daily_score": {
                "productivity": None,
                "focus": None,
                "energy": None,
                "mood": None,
                "progress": None,
            },
        }
        reflections = []
        reflection_sections = defaultdict(list)

        section = None
        priority = None
        current_reflection_key = None

        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()

                # Section detection
                if line.startswith("## 🔁 Habits"):
                    section = "habits"
                    continue
                if line.startswith("### P1"):
                    section, priority = "priority", "P1"
                    continue
                if line.startswith("### P2"):
                    section, priority = "priority", "P2"
                    continue
                if line.startswith("### P3"):
                    section, priority = "priority", "P3"
                    continue
                if line.startswith("## 🧹 Life"):
                    section = "admin"
                    continue
                if line.startswith("## ⚡ Energy"):
                    section = "energy"
                    continue
                if line.startswith("## 📝 Reflection"):
                    section = "reflection"
                    current_reflection_key = None
                    continue
                if line.startswith("## 📊 Daily Score"):
                    section = "daily_score"
                    current_reflection_key = None
                    continue
                if section == "reflection" and line.startswith("###"):
                    heading = line.replace("###", "", 1).strip().lower()
                    current_reflection_key = REFLECTION_SECTION_MAP.get(heading)
                    continue
                if section == "reflection" and line.startswith("**") and line.endswith("**"):
                    heading = line.strip("*").strip().lower()
                    current_reflection_key = REFLECTION_SECTION_MAP.get(heading)
                    continue

                # Habit / Task / Admin
                if line.startswith("- ["):
                    done = line.lower().startswith("- [x]")
                    content = line[6:].strip()
                    if not content:
                        continue
                    if section == "habits":
                        stats["habits"][content]["total"] += 1
                        if done:
                            stats["habits"][content]["done"] += 1
                        weekly_stats["habits"][content]["total"] += 1
                        if done:
                            weekly_stats["habits"][content]["done"] += 1
                    elif section == "priority":
                        stats["priorities"][priority]["total"] += 1
                        if done:
                            stats["priorities"][priority]["done"] += 1
                        weekly_stats["priorities"][priority]["total"] += 1
                        if done:
                            weekly_stats["priorities"][priority]["done"] += 1
                    elif section == "admin":
                        stats["admin"]["total"] += 1
                        if done:
                            stats["admin"]["done"] += 1
                        weekly_stats["admin"]["total"] += 1
                        if done:
                            weekly_stats["admin"]["done"] += 1

                # Energy & Mood
                if section == "energy":
                    clean = line.lstrip("- ").lower().strip()
                    try:
                        # Energy
                        if clean.startswith("energy"):
                            if ":" in clean:
                                value = int(clean.split(":")[1].strip())
                            elif "-" in clean:
                                value = int(clean.split("-")[1].strip())
                            else:
                                value = int(clean.replace(
                                    "energy", "").strip())
                            stats["energy"] = value
                            weekly_stats["energy"].append(value)
                        # Mood
                        elif clean.startswith("mood"):
                            if ":" in clean:
                                value = int(clean.split(":")[1].strip())
                            elif "-" in clean:
                                value = int(clean.split("-")[1].strip())
                            else:
                                value = int(clean.replace("mood", "").strip())
                            stats["mood"] = value
                            weekly_stats["mood"].append(value)
                    except:
                        pass

                # Daily Score block
                if section == "daily_score":
                    if ":" in line:
                        label, raw_value = line.split(":", 1)
                        label = label.strip().lower()
                        raw_value = raw_value.strip()
                        if raw_value:
                            try:
                                value = int(raw_value)
                                if label in stats["daily_score"]:
                                    stats["daily_score"][label] = value
                                    weekly_stats["daily_score"][label].append(value)

                                    # Backfill energy/mood if missing in energy section
                                    if label == "energy" and stats["energy"] is None:
                                        stats["energy"] = value
                                        weekly_stats["energy"].append(value)
                                    if label == "mood" and stats["mood"] is None:
                                        stats["mood"] = value
                                        weekly_stats["mood"].append(value)
                            except ValueError:
                                pass

                # Reflection
                if section == "reflection" and line:
                    clean_line = line.lstrip("- ").strip()
                    if not clean_line:
                        continue
                    if clean_line == "-":
                        continue

                    reflections.append(clean_line)
                    if current_reflection_key:
                        reflection_sections[current_reflection_key].append(clean_line)

        daily_data.append({
            "date": day,
            "habits": stats["habits"],
            "priorities": stats["priorities"],
            "admin": stats["admin"],
            "energy": stats["energy"],
            "mood": stats["mood"],
            "daily_score": stats["daily_score"],
            "reflections": reflections,
            "reflection_sections": dict(reflection_sections),
        })

    return weekly_stats, daily_data


def format_weekly_daily_with_reflections(daily_data=None, weekly_stats=None,
                                         include_weekly_reflections=True):
    """
    Formats weekly aggregates + weekly reflections + daily breakdown for AI input.
    Reflections in weekly summary are grouped by day, date appears once per day.

    Args:
        daily_data: Optional list of daily data dicts. If provided, includes 
                    daily breakdown section.
        weekly_stats: Optional dict with weekly aggregates. If provided, includes
                      weekly summary section.
        include_weekly_reflections: If True and daily_data is provided, includes
                                    the weekly reflections section. Defaults to True.
    """
    lines = []

    # --- Weekly Summary Header ---
    if weekly_stats:
        lines.append("WEEKLY SUMMARY\n")

        # Habits
        lines.append("HABITS:")
        for h, val in weekly_stats["habits"].items():
            lines.append(f"- {h}: {val['done']} / {val['total']}")

        # Priorities
        lines.append("\nPRIORITIES:")
        for p, val in weekly_stats["priorities"].items():
            rate = (val["done"] / val["total"] * 100) if val["total"] else 0
            lines.append(
                f"- {p}: {val['done']} / {val['total']} ({rate:.0f}%)")

        # Admin
        a = weekly_stats["admin"]
        rate = (a["done"] / a["total"] * 100) if a["total"] else 0
        lines.append(f"\nADMIN: {a['done']} / {a['total']} ({rate:.0f}%)")

        # Energy / Mood
        if weekly_stats["energy"]:
            avg_energy = sum(weekly_stats["energy"]) / \
                len(weekly_stats["energy"])
            lines.append(f"\nAVERAGE ENERGY: {avg_energy:.1f}")
        if weekly_stats["mood"]:
            avg_mood = sum(weekly_stats["mood"]) / len(weekly_stats["mood"])
            lines.append(f"AVERAGE MOOD: {avg_mood:.1f}")
        ds = weekly_stats.get("daily_score", {})
        if ds:
            lines.append("\nDAILY SCORE AVERAGES:")
            for metric in ["productivity", "focus", "progress"]:
                values = ds.get(metric, [])
                if values:
                    avg = sum(values) / len(values)
                    lines.append(f"- {metric.title()}: {avg:.1f}")

    # Weekly Reflections (grouped by day)
    if daily_data and include_weekly_reflections:
        lines.append("\nWEEKLY REFLECTIONS:")
        for day_data in daily_data:
            if not day_data["reflections"]:
                continue
            lines.append(f"{day_data['date']}:")
            section_data = day_data.get("reflection_sections", {})
            if section_data:
                for key, label in REFLECTION_OUTPUT_LABELS.items():
                    entries = section_data.get(key, [])
                    if not entries:
                        continue
                    lines.append(f"- {label}")
                    for entry in entries:
                        lines.append(f"  - {entry}")
            else:
                for r in day_data["reflections"]:
                    lines.append(f"- {r}")
            lines.append("")  # blank line between days

    if daily_data:
        lines.append("\n--- DAILY BREAKDOWN ---\n")

        # Daily breakdown
        for day_data in daily_data:
            lines.append(day_data["date"])
            lines.append("HABITS:")
            for habit, val in day_data["habits"].items():
                lines.append(f"- {habit}: {val['done']} / {val['total']}")
            lines.append("PRIORITIES:")
            for p, val in day_data["priorities"].items():
                rate = (val["done"] / val["total"]
                        * 100) if val["total"] else 0
                lines.append(
                    f"- {p}: {val['done']} / {val['total']} ({rate:.0f}%)")
            a = day_data["admin"]
            rate = (a["done"] / a["total"] * 100) if a["total"] else 0
            lines.append(f"ADMIN: {a['done']} / {a['total']} ({rate:.0f}%)")
            if day_data["energy"] is not None:
                lines.append(f"ENERGY: {day_data['energy']}")
            if day_data["mood"] is not None:
                lines.append(f"MOOD: {day_data['mood']}")
            day_score = day_data.get("daily_score", {})
            if any(v is not None for v in day_score.values()):
                lines.append("DAILY SCORE:")
                for metric in ["productivity", "focus", "energy", "mood", "progress"]:
                    value = day_score.get(metric)
                    if value is not None:
                        lines.append(f"- {metric.title()}: {value}")
            lines.append("REFLECTIONS:")
            section_data = day_data.get("reflection_sections", {})
            if section_data:
                for key, label in REFLECTION_OUTPUT_LABELS.items():
                    entries = section_data.get(key, [])
                    if not entries:
                        continue
                    lines.append(f"- {label}")
                    for entry in entries:
                        lines.append(f"  - {entry}")
            else:
                for r in day_data["reflections"]:
                    lines.append(f"- {r}")
            lines.append("\n")  # newline between days

    return "\n".join(lines)


if __name__ == "__main__":
    VAULT = "/Users/gilbertyoung/documents/notes/Daily Actions"
    weekly_stats, daily_data = parse_weekly_notes_combined(VAULT)
    ai_input = format_weekly_daily_with_reflections(
        daily_data=daily_data, include_weekly_reflections=False)

    print(ai_input)
