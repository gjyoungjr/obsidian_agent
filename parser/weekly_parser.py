import datetime
import os
from collections import defaultdict


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
        }
        reflections = []

        section = None
        priority = None

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
                    continue

                # Habit / Task / Admin
                if line.startswith("- ["):
                    done = line.startswith("- [x]")
                    content = line[6:].strip()
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

                # Reflection
                if section == "reflection" and line:
                    reflections.append(line)

        daily_data.append({
            "date": day,
            "habits": stats["habits"],
            "priorities": stats["priorities"],
            "admin": stats["admin"],
            "energy": stats["energy"],
            "mood": stats["mood"],
            "reflections": reflections
        })

    return weekly_stats, daily_data
    """
    Parse Obsidian daily notes for last `days_back` days.
    Returns:
        weekly_stats: aggregated stats for the week
        daily_data: list of per-day stats and reflections
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
    }

    daily_data = []

    for day in reversed(days):  # oldest → newest
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
        }
        reflections = []

        section = None
        priority = None

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
                    continue

                # Habit / Task / Admin
                if line.startswith("- ["):
                    done = line.startswith("- [x]")
                    content = line[6:].strip()
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
                    # remove bullet points & extra spaces
                    clean = line.lstrip("- ").lower().replace(" ", "")
                    if clean.startswith("energy"):
                        try:
                            value = int(''.join(filter(str.isdigit, clean)))
                            stats["energy"] = value
                            weekly_stats["energy"].append(value)
                        except:
                            pass
                    elif clean.startswith("mood"):
                        try:
                            value = int(''.join(filter(str.isdigit, clean)))
                            stats["mood"] = value
                            weekly_stats["mood"].append(value)
                        except:
                            pass

                # Reflection
                if section == "reflection" and line:
                    reflections.append(line)

        daily_data.append({
            "date": day,
            "habits": stats["habits"],
            "priorities": stats["priorities"],
            "admin": stats["admin"],
            "energy": stats["energy"],
            "mood": stats["mood"],
            "reflections": reflections
        })

    return weekly_stats, daily_data
    """
    Parse Obsidian daily notes for last `days_back` days.

    Returns:
        weekly_stats: aggregated stats for the week
        daily_data: list of per-day stats and reflections
    """
    today = datetime.date.today()
    days = [
        (today - datetime.timedelta(days=i)).isoformat()
        for i in range(days_back)
    ]

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
    }

    daily_data = []

    for day in days:
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
        }

        reflections = []
        section = None
        priority = None

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
                    continue

                # Habit / Priority / Admin tasks
                if line.startswith("- ["):
                    done = line.startswith("- [x]")
                    content = line[6:].strip()

                    if section == "habits":
                        stats["habits"][content]["total"] += 1
                        weekly_stats["habits"][content]["total"] += 1
                        if done:
                            stats["habits"][content]["done"] += 1
                            weekly_stats["habits"][content]["done"] += 1

                    elif section == "priority":
                        stats["priorities"][priority]["total"] += 1
                        weekly_stats["priorities"][priority]["total"] += 1
                        if done:
                            stats["priorities"][priority]["done"] += 1
                            weekly_stats["priorities"][priority]["done"] += 1

                    elif section == "admin":
                        stats["admin"]["total"] += 1
                        weekly_stats["admin"]["total"] += 1
                        if done:
                            stats["admin"]["done"] += 1
                            weekly_stats["admin"]["done"] += 1

                # Energy & Mood
                if section == "energy" and line:
                    clean = line.lstrip("- ").lower()

                    if clean.startswith("energy"):
                        try:
                            value = int(
                                clean.replace("energy", "")
                                .replace(":", "")
                                .replace("-", "")
                                .strip()
                            )
                            stats["energy"] = value
                            weekly_stats["energy"].append(value)
                        except ValueError:
                            pass

                    if clean.startswith("mood"):
                        try:
                            value = int(
                                clean.replace("mood", "")
                                .replace(":", "")
                                .replace("-", "")
                                .strip()
                            )
                            stats["mood"] = value
                            weekly_stats["mood"].append(value)
                        except ValueError:
                            pass

                # Reflection
                if section == "reflection" and line:
                    reflections.append(line)

        daily_data.append({
            "date": day,
            "habits": stats["habits"],
            "priorities": stats["priorities"],
            "admin": stats["admin"],
            "energy": stats["energy"],
            "mood": stats["mood"],
            "reflections": reflections,
        })

    return weekly_stats, daily_data


def format_weekly_daily_with_reflections(daily_data, weekly_stats):
    """
    Formats weekly aggregates + weekly reflections + daily breakdown for AI input.
    Reflections in weekly summary are grouped by day, date appears once per day.
    """
    lines = []

    # --- Weekly Summary Header ---
    lines.append("WEEKLY SUMMARY\n")

    # Habits
    lines.append("HABITS:")
    for h, val in weekly_stats["habits"].items():
        lines.append(f"- {h}: {val['done']} / {val['total']}")

    # Priorities
    lines.append("\nPRIORITIES:")
    for p, val in weekly_stats["priorities"].items():
        rate = (val["done"] / val["total"] * 100) if val["total"] else 0
        lines.append(f"- {p}: {val['done']} / {val['total']} ({rate:.0f}%)")

    # Admin
    a = weekly_stats["admin"]
    rate = (a["done"] / a["total"] * 100) if a["total"] else 0
    lines.append(f"\nADMIN: {a['done']} / {a['total']} ({rate:.0f}%)")

    # Energy / Mood
    if weekly_stats["energy"]:
        avg_energy = sum(weekly_stats["energy"]) / len(weekly_stats["energy"])
        lines.append(f"\nAVERAGE ENERGY: {avg_energy:.1f}")
    if weekly_stats["mood"]:
        avg_mood = sum(weekly_stats["mood"]) / len(weekly_stats["mood"])
        lines.append(f"AVERAGE MOOD: {avg_mood:.1f}")

    # Weekly Reflections (grouped by day)
    lines.append("\nWEEKLY REFLECTIONS:")
    for day_data in daily_data:
        if not day_data["reflections"]:
            continue
        lines.append(f"{day_data['date']}:")
        for r in day_data["reflections"]:
            clean_r = r.replace("###", "").strip()
            lines.append(f"- {clean_r}")
        lines.append("")  # blank line between days

    lines.append("\n--- DAILY BREAKDOWN ---\n")

    # Daily breakdown
    for day_data in daily_data:
        lines.append(day_data["date"])
        lines.append("HABITS:")
        for habit, val in day_data["habits"].items():
            lines.append(f"- {habit}: {val['done']} / {val['total']}")
        lines.append("PRIORITIES:")
        for p, val in day_data["priorities"].items():
            rate = (val["done"] / val["total"] * 100) if val["total"] else 0
            lines.append(
                f"- {p}: {val['done']} / {val['total']} ({rate:.0f}%)")
        a = day_data["admin"]
        rate = (a["done"] / a["total"] * 100) if a["total"] else 0
        lines.append(f"ADMIN: {a['done']} / {a['total']} ({rate:.0f}%)")
        if day_data["energy"] is not None:
            lines.append(f"ENERGY: {day_data['energy']}")
        if day_data["mood"] is not None:
            lines.append(f"MOOD: {day_data['mood']}")
        lines.append("REFLECTIONS:")
        for r in day_data["reflections"]:
            clean_r = r.replace("###", "").strip()
            lines.append(f"- {clean_r}")
        lines.append("\n")  # newline between days

    return "\n".join(lines)


if __name__ == "__main__":
    VAULT = "/Users/gilbertyoung/documents/notes/Daily Actions"
    weekly_stats, daily_data = parse_weekly_notes_combined(VAULT)
    ai_input = format_weekly_daily_with_reflections(daily_data, weekly_stats)

    print(ai_input)
