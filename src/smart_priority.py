import datetime
try:
    from models import Task
except ImportError:
    from src.models import Task

def calculate_smart_priority(task: Task, reference_date: datetime.date = None) -> dict:
    """
    Calculates dynamic Smart Priority Score (0-100) based on:
    1. Days remaining until deadline (Urgency Factor)
    2. Base task priority weight (Priority Factor)
    3. Estimated hours and workload pressure (Effort Factor)
    4. Current status (completed tasks receive 0)
    
    Returns a dictionary with score, tier band, component factors, and explanation.
    """
    if reference_date is None:
        reference_date = datetime.date.today()

    if task.status == "Completed":
        return {
            "score": 0.0,
            "band": "Completed",
            "urgency_factor": 0.0,
            "priority_factor": 0.0,
            "effort_factor": 0.0,
            "explanation": "Task is completed."
        }

    days_left = task.days_remaining(reference_date)
    
    # 1. Base Priority Factor (Max 30 points)
    priority_weights = {"High": 30.0, "Medium": 20.0, "Low": 10.0}
    priority_score = priority_weights.get(task.priority, 10.0)

    # 2. Urgency Factor based on deadline proximity (Max 45-50 points)
    if days_left < 0:
        # Overdue: High baseline + extra urgency for each day overdue (capped)
        urgency_score = 45.0 + min(abs(days_left) * 2.0, 15.0)
        urgency_desc = f"Overdue by {abs(days_left)} day(s)"
    elif days_left == 0:
        urgency_score = 42.0
        urgency_desc = "Due today"
    elif days_left == 1:
        urgency_score = 35.0
        urgency_desc = "Due tomorrow"
    elif days_left <= 3:
        urgency_score = 26.0
        urgency_desc = f"Due in {days_left} days"
    elif days_left <= 7:
        urgency_score = 16.0
        urgency_desc = f"Due in {days_left} days (this week)"
    elif days_left <= 14:
        urgency_score = 8.0
        urgency_desc = f"Due in {days_left} days"
    else:
        urgency_score = 4.0
        urgency_desc = f"Due in {days_left} days (future)"

    # 3. Effort & Workload Intensity Factor (Max 20 points)
    # Higher hours need more lead time. If time is short and hours are high, boost effort score.
    effort_base = min(task.estimated_hours * 1.5, 12.0)
    workload_pressure = 0.0
    if days_left <= 2 and task.estimated_hours >= 4.0:
        workload_pressure = 8.0
    elif days_left <= 1 and task.estimated_hours >= 2.0:
        workload_pressure = 5.0
    effort_score = min(effort_base + workload_pressure, 20.0)

    # 4. Status bonus: In-progress tasks receive small focus continuity bonus
    status_bonus = 4.0 if task.status == "In Progress" else 0.0

    raw_score = priority_score + urgency_score + effort_score + status_bonus
    final_score = min(max(raw_score, 1.0), 100.0)
    final_score = round(final_score, 1)

    # Determine priority tier band
    if final_score >= 80.0:
        band = "Critical"
    elif final_score >= 60.0:
        band = "High"
    elif final_score >= 40.0:
        band = "Medium"
    else:
        band = "Low"

    explanation = (
        f"{task.priority} priority (+{priority_score:.0f}), {urgency_desc} (+{urgency_score:.0f}), "
        f"{task.estimated_hours}h estimated effort (+{effort_score:.0f})"
    )
    if status_bonus > 0:
        explanation += f", In Progress momentum (+{status_bonus:.0f})"

    return {
        "score": final_score,
        "band": band,
        "urgency_factor": round(urgency_score, 1),
        "priority_factor": round(priority_score, 1),
        "effort_factor": round(effort_score, 1),
        "explanation": explanation
    }

def rank_tasks(tasks: list[Task], reference_date: datetime.date = None, include_completed: bool = False) -> list[tuple[Task, dict]]:
    """
    Ranks a list of tasks by their Smart Priority Score in descending order.
    Returns list of tuples: (Task, score_metadata_dict).
    """
    if reference_date is None:
        reference_date = datetime.date.today()
        
    scored_tasks = []
    for task in tasks:
        if not include_completed and task.status == "Completed":
            continue
        meta = calculate_smart_priority(task, reference_date)
        scored_tasks.append((task, meta))

    # Sort primarily by score descending, then by deadline ascending
    scored_tasks.sort(key=lambda item: (-item[1]["score"], item[0].deadline))
    return scored_tasks
