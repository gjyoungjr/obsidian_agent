import datetime
import os
from collections import defaultdict

# ===== CONFIG =====
VAULT = "/path/to/Obsidian/Vault/Daily Notes"
DAYS_BACK = 7  # last 7 days

# ===== INIT =====
today = datetime.date.today()
days = [(today - datetime.timedelta(days=i)).isoformat()
        for i in range(DAYS_BACK)]

stats = {
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

reflections = []

# ===== PARSING =====
for day in days:
    path = os.path.join(VAULT, f"{day}.md")
    if not os.path.exists(path):
        continue

    section = None
    priority = None
    current_reflection = []

    for line in open(path, encoding="utf-8"):
        line = line.strip()

        # --- Section detection ---
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

        # --- Habit / Task / Admin detection ---
        if line.startswith("- ["):
            done = line.startswith("- [x]")
            content = line[6:].strip()
            if section == "habits":
                stats["habits"][content]["total"] += 1
                if done:
                    stats["habits"][content]["done"] += 1
            elif section == "priority":
                stats["priorities"][priority]["total"] += 1
                if done:
                    stats["priorities"][priority]["done"] += 1
            elif section == "admin":
                stats["admin"]["total"] += 1
                if done:
                    stats["admin"]["done"] += 1

        # --- Energy & Mood ---
        if section == "energy":
            if line.lower().startswith("energy"):
                try:
                    stats["energy"].append(int(line.split(":")[1].strip()))
                except:
                    pass
            if line.lower().startswith("mood"):
                try:
                    stats["mood"].append(int(line.split(":")[1].strip()))
                except:
                    pass

        # --- Reflection text ---
        if section == "reflection":
            if line:  # skip empty lines
                current_reflection.append(line)

    if current_reflection:
        reflections.append(f"{day}: " + " ".join(current_reflection))

# ===== OUTPUT =====
print("\n===== WEEKLY STATS =====\n")

# Habits
print("Habits:")
for h, val in stats["habits"].items():
    print(f"- {h}: {val['done']} / {val['total']}")

# Priorities
print("\nPriorities:")
for p, val in stats["priorities"].items():
    rate = (val["done"]/val["total"]*100) if val["total"] else 0
    print(f"- {p}: {val['done']} / {val['total']} ({rate:.0f}%)")

# Admin
a = stats["admin"]
rate = (a["done"]/a["total"]*100) if a["total"] else 0
print(f"\nAdmin: {a['done']} / {a['total']} ({rate:.0f}%)")

# Energy & Mood
if stats["energy"]:
    avg_energy = sum(stats["energy"])/len(stats["energy"])
    print(f"\nAverage Energy: {avg_energy:.1f}")
if stats["mood"]:
    avg_mood = sum(stats["mood"])/len(stats["mood"])
    print(f"Average Mood: {avg_mood:.1f}")

# Reflections
print("\nReflections / Journal:")
for r in reflections:
    print("-", r)
