def get_activity_suggestions(row, mood, productivity):

    suggestions = []

    # ---- SLEEP ANALYSIS ----
    if row["sleep_hours"] < 4:
        suggestions.append(
            f"Severe sleep deprivation ({row['sleep_hours']} hrs). "
            "Prioritize recovery sleep today. Avoid caffeine late evening and take proper rest."
        )

    elif row["sleep_hours"] < 6:
        suggestions.append(
            f"Sleep deficit detected ({row['sleep_hours']} hrs). "
            "Aim for 7–8 hours tonight. Avoid screens 30 mins before bed and maintain fixed sleep timing."
        )

    elif row["sleep_deficit"] > 90:
        suggestions.append(
            f"High sleep debt ({row['sleep_deficit']} mins). "
            "Take a short 20–30 min nap or recover with longer sleep tonight."
        )


    # ---- STRESS ANALYSIS ----
    if row["stress_index"] > 0.18:
        suggestions.append(
            f"High stress level ({row['stress_index']}). "
            "Take a break and do 5–10 minutes of deep breathing or meditation."
        )

    elif row["stress_index"] > 0.15:
        suggestions.append(
            f"Moderate stress detected ({row['stress_index']}). "
            "Avoid multitasking and focus on one task at a time."
        )


    # ---- COMBINED CONDITION (IMPORTANT) ----
    if row["stress_index"] > 0.16 and row["sleep_hours"] < 6:
        suggestions.append(
            "High stress combined with low sleep detected. "
            "Avoid heavy workload today and prioritize recovery."
        )


    # ---- PHYSICAL ACTIVITY ----
    if row["total_steps"] < 4000:
        suggestions.append(
            f"Low activity detected ({row['total_steps']} steps). "
            "Take a 15–20 min walk or do light stretching to boost energy."
        )

    elif row["total_steps"] > 9000:
        suggestions.append(
            f"High activity load ({row['total_steps']} steps). "
            "Ensure recovery: hydrate well and avoid overexertion."
        )


    # ---- HEART RATE / FATIGUE ----
    if row["avg_hr_day"] > row["resting_hr"] + 15:
        suggestions.append(
            "Elevated heart rate compared to baseline. "
            "Possible fatigue or stress—take breaks and avoid intense activity."
        )


    # ---- PRODUCTIVITY-SPECIFIC ----
    if productivity < 4:
        suggestions.append(
            "Very low productivity detected. "
            "Start with small tasks and use Pomodoro technique (25 min work + 5 min break)."
        )

    elif productivity < 5:
        suggestions.append(
            "Slightly low productivity. "
            "Break tasks into smaller chunks and reduce distractions."
        )


    # ---- MOOD-SPECIFIC ----
    if mood < 4:
        suggestions.append(
            "Low mood detected. "
            "Take a break and engage in relaxing activities like music or a short walk."
        )

    elif mood < 5:
        suggestions.append(
            "Mildly low mood. "
            "Try light social interaction or a refreshing activity."
        )


    # ---- DEFAULT ----
    if not suggestions:
        suggestions.append(
            "Your metrics look balanced. Maintain current routine and consistency."
        )

    return suggestions