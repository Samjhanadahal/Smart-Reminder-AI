import datetime
try:
    from models import Task
    from smart_priority import calculate_smart_priority
except ImportError:
    from src.models import Task
    from src.smart_priority import calculate_smart_priority

class ReminderAlert:
    """Represents a reminder alert category with associated tasks and metadata."""
    def __init__(self, category: str, label: str, severity: str, icon: str, tasks: list[Task]):
        self.category = category  # overdue, due_today, due_soon, due_week
        self.label = label
        self.severity = severity  # danger, warning, info, success
        self.icon = icon
        self.tasks = tasks

    @property
    def count(self) -> int:
        return len(self.tasks)

    @property
    def total_hours(self) -> float:
        return round(sum(t.estimated_hours for t in self.tasks), 1)

def get_reminder_alerts(tasks: list[Task], reference_date: datetime.date = None) -> dict[str, ReminderAlert]:
    """
    Categorizes active tasks into reminder urgency categories:
    - Overdue (past deadline)
    - Due Today (deadline is today)
    - Due Soon (within next 48 hours)
    - Due This Week (within next 3-7 days)
    """
    if reference_date is None:
        reference_date = datetime.date.today()

    overdue = []
    due_today = []
    due_soon = []
    due_week = []

    for task in tasks:
        if task.status == "Completed":
            continue
            
        days = task.days_remaining(reference_date)
        if days < 0:
            overdue.append(task)
        elif days == 0:
            due_today.append(task)
        elif 1 <= days <= 2:
            due_soon.append(task)
        elif 3 <= days <= 7:
            due_week.append(task)

    # Sort each category by Smart Priority
    for group in [overdue, due_today, due_soon, due_week]:
        group.sort(key=lambda t: -calculate_smart_priority(t, reference_date)["score"])

    return {
        "overdue": ReminderAlert("overdue", "Overdue Tasks", "danger", "🚨", overdue),
        "due_today": ReminderAlert("due_today", "Due Today", "warning", "⚡", due_today),
        "due_soon": ReminderAlert("due_soon", "Due Within 48 Hours", "info", "⏰", due_soon),
        "due_week": ReminderAlert("due_week", "Due This Week", "neutral", "📅", due_week),
    }

def check_workload_overload(tasks: list[Task], max_daily_hours: float = 8.0, reference_date: datetime.date = None) -> dict:
    """
    Checks if active tasks due today + overdue exceed the recommended daily capacity.
    """
    alerts = get_reminder_alerts(tasks, reference_date)
    immediate_tasks = alerts["overdue"].tasks + alerts["due_today"].tasks
    total_immediate_hours = round(sum(t.estimated_hours for t in immediate_tasks), 1)
    
    is_overloaded = total_immediate_hours > max_daily_hours
    deficit = round(total_immediate_hours - max_daily_hours, 1) if is_overloaded else 0.0

    return {
        "is_overloaded": is_overloaded,
        "total_hours": total_immediate_hours,
        "capacity_limit": max_daily_hours,
        "hours_deficit": deficit,
        "task_count": len(immediate_tasks),
        "message": (
            f"⚠️ Workload Warning: Immediate tasks require {total_immediate_hours}h "
            f"(exceeds {max_daily_hours}h daily threshold by {deficit}h). Consider re-prioritizing."
            if is_overloaded else
            f"✅ Workload balanced: Immediate tasks require {total_immediate_hours}h of available capacity."
        )
    }

def generate_daily_digest(tasks: list[Task], reference_date: datetime.date = None) -> str:
    """
    Generates a formatted text digest of reminders, suitable for CLI display or notifications.
    """
    if reference_date is None:
        reference_date = datetime.date.today()

    alerts = get_reminder_alerts(tasks, reference_date)
    overload = check_workload_overload(tasks, reference_date=reference_date)

    lines = []
    lines.append("=" * 55)
    lines.append(f"  🔔 SMART REMINDER DAILY DIGEST - {reference_date.strftime('%A, %b %d, %Y')}")
    lines.append("=" * 55)

    total_active = sum(alert.count for alert in alerts.values())
    lines.append(
        f"Summary: {alerts['overdue'].count} Overdue | "
        f"{alerts['due_today'].count} Due Today | "
        f"{alerts['due_soon'].count} Next 48h | "
        f"{alerts['due_week'].count} This Week"
    )
    lines.append(overload["message"])
    lines.append("-" * 55)

    if total_active == 0:
        lines.append("🎉 You have no pending deadlines! All caught up.")
        lines.append("=" * 55)
        return "\n".join(lines)

    for key, alert in alerts.items():
        if alert.count == 0:
            continue
        lines.append(f"\n{alert.icon} {alert.label.upper()} ({alert.count} tasks, ~{alert.total_hours}h total):")
        for task in alert.tasks:
            days = task.days_remaining(reference_date)
            time_str = f"{-days}d overdue" if days < 0 else ("Today" if days == 0 else f"{days}d left")
            score_info = calculate_smart_priority(task, reference_date)
            lines.append(
                f"  [{task.priority}] #{task.id} {task.title} "
                f"| Est: {task.estimated_hours}h | Time: {time_str} | Smart Score: {score_info['score']}"
            )

    lines.append("\n" + "=" * 55)
    return "\n".join(lines)
