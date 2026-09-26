import datetime
try:
    from models import Task
    from smart_priority import calculate_smart_priority, rank_tasks
    from ml_predictor import predict_task_completion
except ImportError:
    from src.models import Task
    from src.smart_priority import calculate_smart_priority, rank_tasks
    from src.ml_predictor import predict_task_completion

def generate_task_explanation(task: Task, reference_date: datetime.date = None) -> dict:
    """
    Produces Explainable AI (XAI) analysis for why a task was scored/ranked,
    including key risk drivers and tailored productivity advice.
    """
    if reference_date is None:
        reference_date = datetime.date.today()

    smart_meta = calculate_smart_priority(task, reference_date)
    ml_meta = predict_task_completion(task, reference_date)
    days_left = task.days_remaining(reference_date)

    drivers = []
    actions = []

    # Driver 1: Deadline Urgency
    if days_left < 0:
        drivers.append(f"Overdue by {-days_left} day(s)")
        actions.append("🚨 Immediate triage needed: Re-estimate remaining scope and set a recovery deadline.")
    elif days_left == 0:
        drivers.append("Due today")
        actions.append("⚡ Commit to finishing this today; avoid context switching.")
    elif days_left <= 2:
        drivers.append(f"Only {days_left} day(s) until deadline")
        actions.append("⏰ Prioritize this in your morning work block.")
    else:
        drivers.append(f"{days_left} days remaining")

    # Driver 2: Priority
    if task.priority == "High":
        drivers.append("High strategic priority")
    elif task.priority == "Medium":
        drivers.append("Medium operational priority")
    else:
        drivers.append("Low priority maintenance task")

    # Driver 3: Effort & Complexity
    if task.estimated_hours >= 5.0:
        drivers.append(f"Substantial effort required ({task.estimated_hours}h)")
        actions.append(f"🧩 Large task detected: Break down into {int(task.estimated_hours // 2)} smaller focus sessions.")
    elif task.estimated_hours <= 1.5 and task.priority in ["High", "Medium"] and days_left >= 0:
        drivers.append(f"Quick win effort ({task.estimated_hours}h)")
        actions.append("🎯 Quick Win: Finish this early to build momentum.")

    # Driver 4: ML Risk Factor
    if ml_meta["probability"] < 50.0 and task.status != "Completed":
        actions.append("🤖 AI Risk Flag: High statistical probability of deadline slip. Consider delegating or deselecting non-essential deliverables.")

    return {
        "task_id": task.id,
        "title": task.title,
        "smart_score": smart_meta["score"],
        "priority_band": smart_meta["band"],
        "on_time_probability": ml_meta["probability"],
        "risk_level": ml_meta["risk_level"],
        "primary_drivers": drivers,
        "actionable_tips": actions,
        "summary": f"Ranked '{smart_meta['band']}' ({smart_meta['score']}/100) due to {', '.join(drivers)}."
    }

def generate_daily_schedule_agenda(tasks: list[Task], max_hours: float = 6.5, reference_date: datetime.date = None) -> dict:
    """
    Optimizes a realistic, ordered work agenda for today based on
    Smart Priority, effort estimations, and daily focus capacity.
    """
    if reference_date is None:
        reference_date = datetime.date.today()

    active_tasks = [t for t in tasks if t.status != "Completed"]
    if not active_tasks:
        return {
            "schedule": [],
            "total_allocated_hours": 0.0,
            "capacity_limit": max_hours,
            "deferred_tasks_count": 0,
            "notes": "No pending tasks! Enjoy your free time or plan ahead."
        }

    # Rank by smart priority
    ranked = rank_tasks(active_tasks, reference_date=reference_date, include_completed=False)

    scheduled = []
    allocated_hours = 0.0
    deferred_count = 0

    # Categorize schedule into focus blocks
    time_slots = [
        ("09:00 - 11:00", "Morning Deep Work", "Primary high-impact priority"),
        ("11:15 - 12:30", "Pre-Noon Sprint", "High/medium priority focus"),
        ("13:30 - 15:30", "Afternoon Execution", "Focused continuation"),
        ("15:45 - 17:00", "Wrap-up & Review", "Review and quick wins"),
    ]
    slot_idx = 0

    for task, meta in ranked:
        if allocated_hours + task.estimated_hours <= max_hours:
            slot_time, slot_name, slot_desc = time_slots[slot_idx % len(time_slots)]
            slot_idx += 1
            allocated_hours += task.estimated_hours
            explanation = generate_task_explanation(task, reference_date)

            scheduled.append({
                "time_slot": slot_time,
                "block_name": slot_name,
                "task": task,
                "smart_score": meta["score"],
                "smart_band": meta["band"],
                "hours": task.estimated_hours,
                "tips": explanation["actionable_tips"]
            })
        else:
            deferred_count += 1

    return {
        "schedule": scheduled,
        "total_allocated_hours": round(allocated_hours, 1),
        "capacity_limit": max_hours,
        "deferred_tasks_count": deferred_count,
        "notes": (
            f"Optimized {len(scheduled)} tasks totaling {allocated_hours:.1f}h work today. "
            f"{deferred_count} tasks scheduled for upcoming sessions to prevent burnout."
            if deferred_count > 0 else
            f"All active tasks fit within your {max_hours}h focus capacity today!"
        )
    }
