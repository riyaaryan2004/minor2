from features.predict_day import predict_day
from features.routine_engine import get_task_recommendation, print_recommendation
from features.activity_suggestion import get_activity_suggestions


# -----------------------------------
# 🎓 USER INPUT (TASKS ONLY)
# -----------------------------------
tasks = []

n = int(input("Enter number of tasks: "))

for i in range(n):
    print(f"\nTask {i+1}:")
    name = input("Task name: ")
    priority = int(input("Priority (1-5): "))
    duration = int(input("Duration (mins): "))
    ttype = input("Type (deep/light/passive): ")

    tasks.append({
        "task": name,
        "priority": priority,
        "duration": duration,
        "type": ttype
    })


# -----------------------------------
# 📊 SYSTEM DATA (AUTO / FROM DATASET)
# -----------------------------------
row = {
    "sleep_hours": 6,
    "total_sleep": 360,
    "sleep_deficit": 30,
    "total_steps": 5000,
    "avg_hr_day": 85,
    "resting_hr": 70,
    "stress_index": 0.14,
    "activity_load": 3
}


# -----------------------------------
# 🤖 STEP 1: PREDICTION
# -----------------------------------
mood, productivity = predict_day(row)
stress = row["stress_index"]


# -----------------------------------
# ⚙️ STEP 2: TASK RECOMMENDATION
# -----------------------------------
result = get_task_recommendation(
    row=row,
    mood=mood,
    productivity=productivity,
    stress=stress,
    tasks=tasks,
    get_activity_suggestions=get_activity_suggestions
)


# -----------------------------------
# 🧾 FINAL OUTPUT
# -----------------------------------
print("\n📊 FINAL SYSTEM OUTPUT")
print("Mood:", round(mood, 2))
print("Productivity:", round(productivity, 2))

print_recommendation(result)