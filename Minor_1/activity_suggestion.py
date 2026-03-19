def get_activity_suggestions(row, mood, productivity):

    suggestions = []

    # ---- SLEEP ANALYSIS ----
    if row["sleep_hours"] < 6:
        suggestions.append(
            f"Sleep deficit detected ({row['sleep_hours']} hrs). "
            "Recommendation: sleep at least 7–8 hours tonight. "
            "Avoid screens 30 mins before bed and maintain fixed sleep timing."
        )

    elif row["sleep_deficit"] > 90:
        suggestions.append(
            f"High sleep debt ({row['sleep_deficit']} mins). "
            "Take a short 20–30 min nap during the day or recover with longer sleep tonight."
        )

    # ---- STRESS ANALYSIS ----
    if row["stress_index"] > 0.16:
        suggestions.append(
            f"Elevated stress level ({row['stress_index']}). "
            "Do 5–10 minutes of deep breathing or meditation. "
            "Avoid high-intensity tasks immediately."
        )

    # ---- PHYSICAL ACTIVITY ----
    if row["total_steps"] < 4000:
        suggestions.append(
            f"Low activity detected ({row['total_steps']} steps). "
            "Take a 15-20 min walk or do light stretching to boost energy levels."
        )

    elif row["total_steps"] > 9000:
        suggestions.append(
            f"High activity load ({row['total_steps']} steps). "
            "Ensure proper recovery: hydrate well and avoid overexertion."
        )

    # ---- HEART RATE / FATIGUE ----
    if row["avg_hr_day"] > row["resting_hr"] + 15:
        suggestions.append(
            "Elevated heart rate compared to baseline. "
            "Possible fatigue or stress. Reduce workload and take breaks."
        )

    # ---- PRODUCTIVITY-SPECIFIC ----
    if productivity < 5:
        suggestions.append(
            "Low productivity detected. "
            "Break tasks into smaller chunks (Pomodoro: 25 min work + 5 min break)."
        )

    # ---- MOOD-SPECIFIC ----
    if mood < 5:
        suggestions.append(
            "Low mood detected. "
            "Engage in relaxing or enjoyable activities (music, light walk, social interaction)."
        )

    # ---- DEFAULT ----
    if not suggestions:
        suggestions.append(
            "Your metrics look balanced. Maintain current routine and consistency."
        )

    return suggestions