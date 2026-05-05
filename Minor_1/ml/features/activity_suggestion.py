def get_activity_suggestions(row, mood, productivity, raw_stress):

    suggestions = []

    sleep = row["sleep_hours"]
    stress = raw_stress
    steps = row["total_steps"]

    # ---- SLEEP ANALYSIS (student realistic) ----
    if sleep < 4:
        suggestions.append(
            f"Sleep is quite low ({sleep} hrs). Keep workload light, finish the most important task first, and avoid late caffeine so recovery is easier tonight."
        )

    elif sleep < 5:
        suggestions.append(
            f"Sleep is slightly low ({sleep} hrs) but manageable. Use shorter focus blocks, avoid overloading your schedule, and plan an earlier wind-down."
        )

    elif sleep < 6:
        suggestions.append(
            f"Decent sleep ({sleep} hrs). You can function normally, but keep breaks consistent and try to protect a similar bedtime tonight."
        )

    elif row["sleep_deficit"] > 90:
        suggestions.append(
            f"Some sleep debt ({row['sleep_deficit']} mins). A 15-20 minute nap or a calmer evening routine can help reduce fatigue."
        )


    # ---- STRESS ANALYSIS ----
    if stress > 0.18:
        suggestions.append(
            f"Stress is high ({round(stress,3)}). Focus on one task at a time, pause between tasks, and avoid adding extra deadlines today."
        )

    elif stress > 0.15:
        suggestions.append(
            f"Moderate stress ({round(stress,3)}). Take a short reset break every 60-90 minutes to keep focus steady."
        )


    # ---- COMBINED CONDITION (fixed threshold) ----
    if stress > 0.18 and sleep < 5:
        suggestions.append(
            "Low sleep combined with high stress can drain energy quickly. Keep the day simple: essential tasks first, lighter tasks later."
        )


    # ---- PHYSICAL ACTIVITY ----
    if steps < 2000:
        suggestions.append(
            f"Very low activity ({steps} steps). Add a 10-minute easy walk or two short movement breaks to lift energy without forcing intensity."
        )

    elif steps < 4000:
        suggestions.append(
            f"Low activity ({steps} steps). Try adding 1500-2500 steps through light walking to improve focus and reduce stiffness."
        )

    elif steps > 8000:
        suggestions.append(
            f"Good activity level ({steps} steps). Keep it steady with hydration and avoid pushing extra intensity if you feel tired."
        )


    # ---- HEART RATE / FATIGUE ----
    if row["avg_hr_day"] > row["resting_hr"] + 15:
        suggestions.append(
            "Heart rate is elevated compared to baseline. Keep exercise light, take recovery breaks, and avoid intense activity until it settles."
        )


    # ---- PRODUCTIVITY-SPECIFIC ----
    if productivity < 4:
        suggestions.append(
            "Productivity is quite low. Start with a 20-25 minute task, keep the target small, and build momentum before attempting deeper work."
        )

    elif productivity < 5:
        suggestions.append(
            "Productivity is slightly low. Break work into smaller chunks, silence avoidable distractions, and review progress after each block."
        )


    # ---- MOOD-SPECIFIC ----
    if mood < 4:
        suggestions.append(
            "Mood is low. Try a small refreshing activity such as music, sunlight, or a short walk before starting demanding work."
        )

    elif mood < 5:
        suggestions.append(
            "Mood is slightly low. A quick break, light interaction, or a simple completed task may help reset the tone of the day."
        )


    # ---- BALANCED STATE (NEW - IMPORTANT) ----
    if sleep >= 5 and steps >= 6000 and stress < 0.16:
        suggestions.append(
            "Overall balance looks good. Maintain the routine with regular breaks, steady hydration, and one planned movement window."
        )


    # ---- DEFAULT ----
    if not suggestions:
        suggestions.append(
            "Everything looks stable. Keep following your current routine, protect your breaks, and avoid unnecessary late-day overload."
        )

    return suggestions[:3]
