# routine_engine.py

import datetime


# -------------------------------
# 1. Normalize Tasks
# -------------------------------
def normalize_tasks(tasks):
    for t in tasks:
        t.setdefault("priority", 3)
        t.setdefault("duration", 60)
        t.setdefault("type", "medium")  # deep / light / passive
    return tasks


# -------------------------------
# 2. Time Context
# -------------------------------
def get_time_context():
    hour = datetime.datetime.now().hour

    if 9 <= hour <= 11:
        return "Peak focus window (best for deep work)"
    elif 14 <= hour <= 16:
        return "Post-lunch dip (keep tasks light)"
    elif hour >= 21:
        return "Late hours (avoid heavy work)"
    return "Normal working hours"


# -------------------------------
# 3. Task Selection Logic
# -------------------------------
def select_task(tasks, mood, productivity, stress):
    tasks = sorted(tasks, key=lambda x: x["priority"], reverse=True)

    # 🔥 HIGH PERFORMANCE
    if mood >= 7 and productivity >= 7 and stress < 0.15:
        for t in tasks:
            if t["type"] == "deep":
                return t, "High focus detected → best time for deep work"

    # ⚠️ LOW ENERGY / HIGH STRESS
    if mood < 4 or stress > 0.18:
        for t in tasks:
            if t["type"] in ["light", "passive"]:
                return t, "Low mental energy → switching to lighter task"

    # 🐢 LOW PRODUCTIVITY
    if productivity < 4:
        for t in tasks:
            if t["duration"] <= 45:
                return t, "Low productivity → starting with small task"

    # ⚖️ BALANCED STATE
    return tasks[0], "Balanced state → working on highest priority task"


# -------------------------------
# 4. Confidence Score
# -------------------------------
def get_confidence(mood, productivity):
    return round(((mood + productivity) / 2) * 10, 1)  # out of 100


# -------------------------------
# 5. Final Recommendation Engine
# -------------------------------
def get_task_recommendation(row, mood, productivity, stress, tasks, get_activity_suggestions):

    # Step 1: normalize tasks
    tasks = normalize_tasks(tasks)

    # Step 2: get activity insights (your existing function)
    insights = get_activity_suggestions(row, mood, productivity, stress)

    # Step 3: select best task
    task, reason = select_task(tasks, mood, productivity, stress)

    # Step 4: time awareness
    time_context = get_time_context()

    # Step 5: confidence
    confidence = get_confidence(mood, productivity)

    # Final Output
    return {
        "task": task["task"],
        "reason": reason,
        "time_context": time_context,
        "confidence": confidence,
        "insights": insights
    }


# -------------------------------
# 6. Pretty Output (Optional)
# -------------------------------
def print_recommendation(result):
    print("\n🟢 Suggested Task:", result["task"])
    print("\n⚡ Reason:", result["reason"])
    print("\n🕒 Context:", result["time_context"])
    print("\n📊 Confidence:", result["confidence"], "%")

    print("\n💡 Insights:")
    for s in result["insights"]:
        print("-", s)