from datetime import datetime, timedelta

def parse_hour(time_str):
    try:
        hour, minute = map(int, time_str.split(":"))
        return hour + minute / 60
    except:
        return 7

def hour_to_label(hour_float):
    hour = int(hour_float)
    minute = int((hour_float - hour) * 60)
    suffix = "AM"
    display_hour = hour

    if hour == 0:
        display_hour = 12
        suffix = "AM"
    elif 1 <= hour < 12:
        display_hour = hour
        suffix = "AM"
    elif hour == 12:
        display_hour = 12
        suffix = "PM"
    else:
        display_hour = hour - 12
        suffix = "PM"

    return f"{display_hour}:{minute:02d} {suffix}"

def profession_task_templates(profession):
    profession = profession.lower()

    if profession == "student":
        return [
            "Deep study session",
            "Revision / notes making",
            "Practice questions",
            "Assignment / project work",
            "Reading / concept clarity"
        ]
    elif profession == "employee":
        return [
            "Deep work / important project",
            "Emails and communication",
            "Meetings / coordination",
            "Execution tasks",
            "Review and planning"
        ]
    elif profession == "teacher":
        return [
            "Lecture preparation",
            "Teaching session planning",
            "Checking assignments",
            "Student support / doubt solving",
            "Administrative work"
        ]
    elif profession == "freelancer":
        return [
            "Client work",
            "Creative production",
            "Communication / proposals",
            "Skill improvement",
            "Planning and delivery"
        ]
    else:
        return [
            "Important work block",
            "Light work block",
            "Learning / growth",
            "Planning / admin",
            "Review block"
        ]

def get_energy_profile(sleep_hours, energy_level, stress_level, focus_level):
    """
    24-hour score map generate karta hai.
    """
    scores = []

    for hour in range(24):
        score = 40

        # Natural productivity windows
        if 6 <= hour <= 9:
            score += 18
        if 10 <= hour <= 12:
            score += 28
        if 14 <= hour <= 16:
            score += 18
        if 20 <= hour <= 22:
            score += 8

        # Low productivity zones
        if 0 <= hour <= 5:
            score -= 35
        if 13 <= hour <= 14:
            score -= 10

        # User factors
        score += (energy_level - 5) * 5
        score += (focus_level - 5) * 5
        score -= (stress_level - 5) * 4
        score += (sleep_hours - 7) * 4

        # Clamp
        score = max(0, min(100, score))
        scores.append({"hour": hour, "score": round(score, 1)})

    return scores

def get_best_hours(profile, wake_hour, work_start, work_end):
    valid = []
    for p in profile:
        h = p["hour"]
        if h >= int(wake_hour) and h >= int(work_start) and h <= int(work_end):
            valid.append(p)

    if not valid:
        valid = profile

    sorted_hours = sorted(valid, key=lambda x: x["score"], reverse=True)
    return sorted_hours[:3]

def classify_task(task):
    text = task.lower()

    deep_keywords = ["study", "exam", "coding", "project", "research", "analysis", "write", "preparation"]
    light_keywords = ["email", "meeting", "admin", "call", "checking", "review", "message"]
    creative_keywords = ["design", "creative", "content", "idea", "brainstorm", "presentation"]

    if any(k in text for k in deep_keywords):
        return "deep"
    elif any(k in text for k in creative_keywords):
        return "creative"
    elif any(k in text for k in light_keywords):
        return "light"
    else:
        return "general"

def priority_score(task, deadline_pressure):
    text = task.lower()
    score = 50 + (deadline_pressure * 5)

    urgent_words = ["urgent", "exam", "deadline", "submission", "important", "project"]
    easy_words = ["review", "email", "light", "small", "simple"]

    if any(w in text for w in urgent_words):
        score += 20
    if any(w in text for w in easy_words):
        score -= 5

    return score

def recommend_block(task_type, best_hours, work_start, work_end):
    top_hour = best_hours[0]["hour"]
    second_hour = best_hours[1]["hour"] if len(best_hours) > 1 else top_hour + 2
    third_hour = best_hours[2]["hour"] if len(best_hours) > 2 else second_hour + 2

    if task_type == "deep":
        chosen = top_hour
    elif task_type == "creative":
        chosen = second_hour
    elif task_type == "light":
        chosen = third_hour
    else:
        chosen = second_hour

    chosen = max(int(work_start), min(int(work_end) - 1, int(chosen)))
    return f"{hour_to_label(chosen)} - {hour_to_label(chosen + 1)}"

def generate_today_plan(tasks_list, best_hours, work_start, work_end, deadline_pressure):
    scored_tasks = []
    for t in tasks_list:
        task_type = classify_task(t)
        score = priority_score(t, deadline_pressure)
        scored_tasks.append((t, task_type, score))

    scored_tasks.sort(key=lambda x: x[2], reverse=True)

    today_plan = []
    for task, task_type, score in scored_tasks[:5]:
        block = recommend_block(task_type, best_hours, work_start, work_end)
        today_plan.append({
            "task": task,
            "task_type": task_type,
            "priority_score": score,
            "recommended_time": block
        })

    return today_plan

def generate_weekly_plan(tasks_list, best_hours, profession, deadline_pressure):
    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    templates = profession_task_templates(profession)

    weekly_plan = []
    task_index = 0

    for i, day in enumerate(day_names):
        day_tasks = []

        if task_index < len(tasks_list):
            main_task = tasks_list[task_index]
            main_type = classify_task(main_task)
            main_block = recommend_block(main_type, best_hours, 6, 22)

            day_tasks.append({
                "title": main_task,
                "time": main_block,
                "type": main_type
            })
            task_index += 1

        extra_template = templates[i % len(templates)]
        extra_type = "light" if i % 2 == 0 else "general"
        extra_block = recommend_block(extra_type, best_hours, 6, 22)

        day_tasks.append({
            "title": extra_template,
            "time": extra_block,
            "type": extra_type
        })

        if deadline_pressure >= 7:
            revision_time = recommend_block("deep", best_hours, 6, 22)
            day_tasks.append({
                "title": "High-priority review / catch-up",
                "time": revision_time,
                "type": "deep"
            })

        weekly_plan.append({
            "day": day,
            "tasks": day_tasks
        })

    return weekly_plan

def build_ai_advice(user_data, best_hours, profile, tasks_count):
    advice = []

    sleep_hours = user_data["sleep_hours"]
    stress_level = user_data["stress_level"]
    energy_level = user_data["energy_level"]
    focus_level = user_data["focus_level"]
    profession = user_data["profession"]
    break_pref = user_data["break_preference"]

    best_time_labels = [hour_to_label(x["hour"]) for x in best_hours]

    advice.append(
        f"Your strongest work window is around {best_time_labels[0]}. Put your hardest task there."
    )

    if len(best_time_labels) > 1:
        advice.append(
            f"Your next useful windows are {', '.join(best_time_labels[1:])}. Use them for secondary work."
        )

    if sleep_hours < 6:
        advice.append("You are sleeping less than ideal. Reduce heavy work late at night and protect morning energy.")

    if stress_level >= 8:
        advice.append("Stress is high. Keep only 2-3 major tasks per day and add short breaks after each deep session.")

    if focus_level >= 8 and energy_level >= 7:
        advice.append("You currently have strong focus potential. Use 60-90 minute deep work blocks.")

    if tasks_count > 8:
        advice.append("You have many tasks. Do not try everything in one day. Split them into essential, important, and optional.")

    if profession.lower() == "student":
        advice.append("As a student, keep concept-heavy study in your best hours and revision in lower-energy hours.")
    elif profession.lower() == "employee":
        advice.append("As an employee, keep deep project work in prime hours and meetings/emails in lighter hours.")
    elif profession.lower() == "teacher":
        advice.append("As a teacher, use high-energy time for lecture planning and low-energy time for checking/admin work.")

    if break_pref == "short":
        advice.append("Use a 50-10 routine: 50 minutes work, 10 minutes break.")
    elif break_pref == "medium":
        advice.append("Use a 75-15 routine for balanced productivity.")
    else:
        advice.append("Use longer work cycles like 90-20 only for deep focus blocks.")

    low_hours = sorted(profile, key=lambda x: x["score"])[:3]
    low_labels = [hour_to_label(x["hour"]) for x in low_hours]
    advice.append(f"Avoid difficult work around {', '.join(low_labels)} because your predicted productivity is low there.")

    return advice

def generate_plan(user_data):
    wake_hour = parse_hour(user_data["wake_time"])
    work_start = parse_hour(user_data["work_start"])
    work_end = parse_hour(user_data["work_end"])

    tasks_raw = user_data["tasks"]
    tasks_list = [t.strip() for t in tasks_raw.split(",") if t.strip()]

    if not tasks_list:
        tasks_list = profession_task_templates(user_data["profession"])[:4]

    profile = get_energy_profile(
        user_data["sleep_hours"],
        user_data["energy_level"],
        user_data["stress_level"],
        user_data["focus_level"]
    )

    best_hours = get_best_hours(profile, wake_hour, work_start, work_end)

    today_plan = generate_today_plan(
        tasks_list,
        best_hours,
        work_start,
        work_end,
        user_data["deadline_pressure"]
    )

    weekly_plan = generate_weekly_plan(
        tasks_list,
        best_hours,
        user_data["profession"],
        user_data["deadline_pressure"]
    )

    ai_advice = build_ai_advice(
        user_data,
        best_hours,
        profile,
        len(tasks_list)
    )

    top_hours = [hour_to_label(x["hour"]) for x in best_hours]
    productivity_chart = [
        {"label": hour_to_label(item["hour"]), "score": item["score"]}
        for item in profile
    ]

    summary = {
        "name": user_data["name"] if user_data["name"] else "User",
        "profession": user_data["profession"],
        "goals": user_data["goals"],
        "top_hours": top_hours,
        "today_plan": today_plan,
        "weekly_plan": weekly_plan,
        "ai_advice": ai_advice,
        "productivity_chart": productivity_chart
    }

    return summary