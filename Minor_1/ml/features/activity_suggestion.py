
def get_activity_suggestions(row, mood, productivity, raw_stress):

    suggestions = []

    sleep = row["sleep_hours"]
    stress = raw_stress   # ✅ FIXED (was row["stress_index"])
    steps = row["total_steps"]

    # ---- SLEEP ANALYSIS (student realistic) ----
    if sleep < 4:
        suggestions.append(
            f"Sleep is quite low ({sleep} hrs). Keep workload light and try to recover tonight."
        )

    elif sleep < 5:
        suggestions.append(
            f"Sleep is slightly low ({sleep} hrs) but manageable. Avoid overloading yourself."
        )

    elif sleep < 6:
        suggestions.append(
            f"Decent sleep ({sleep} hrs). You can function normally but aim for consistency."
        )

    elif row["sleep_deficit"] > 90:
        suggestions.append(
            f"Some sleep debt ({row['sleep_deficit']} mins). A short nap or good sleep tonight will help."
        )


    # ---- STRESS ANALYSIS ----
    if stress > 0.18:
        suggestions.append(
            f"Stress is high ({round(stress,3)}). Focus on one task at a time and avoid overload."
        )

    elif stress > 0.15:
        suggestions.append(
            f"Moderate stress ({round(stress,3)}). Take short breaks to stay focused."
        )


    # ---- COMBINED CONDITION (fixed threshold) ----
    if stress > 0.18 and sleep < 5:
        suggestions.append(
            "Low sleep combined with high stress — take it slightly easy today."
        )


    # ---- PHYSICAL ACTIVITY ----
    if steps < 2000:
        suggestions.append(
            f"Very low activity ({steps} steps). Even a short walk will help boost energy."
        )

    elif steps < 4000:
        suggestions.append(
            f"Low activity ({steps} steps). Light movement can improve focus."
        )

    elif steps > 8000:
        suggestions.append(
            f"Good activity level ({steps} steps). Keep it up."
        )


    # ---- HEART RATE / FATIGUE ----
    if row["avg_hr_day"] > row["resting_hr"] + 15:
        suggestions.append(
            "Heart rate is elevated compared to baseline. Take breaks and avoid intense activity."
        )


    # ---- PRODUCTIVITY-SPECIFIC ----
    if productivity < 4:
        suggestions.append(
            "Productivity is quite low. Start with small tasks and build momentum (Pomodoro works well)."
        )

    elif productivity < 5:
        suggestions.append(
            "Productivity slightly low. Break tasks into smaller chunks and reduce distractions."
        )


    # ---- MOOD-SPECIFIC ----
    if mood < 4:
        suggestions.append(
            "Mood is low. Try a small refreshing activity like music or a short walk."
        )

    elif mood < 5:
        suggestions.append(
            "Mood slightly low. Light interaction or a quick break may help."
        )


    # ---- BALANCED STATE (NEW - IMPORTANT) ----
    if sleep >= 5 and steps >= 6000 and stress < 0.16:
        suggestions.append(
            "Overall balance looks good. Maintain this routine."
        )


    # ---- DEFAULT ----
    if not suggestions:
        suggestions.append(
            "Everything looks stable. Keep following your current routine."
        )

    return suggestions[:3]