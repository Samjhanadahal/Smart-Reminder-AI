import datetime
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for server / script safety
import matplotlib.pyplot as plt

try:
    from models import Task
except ImportError:
    from src.models import Task

def calculate_productivity_metrics(tasks: list[Task]) -> dict:
    """
    Computes key productivity and performance metrics across all tasks.
    """
    if not tasks:
        return {
            "total_tasks": 0,
            "completed_count": 0,
            "in_progress_count": 0,
            "pending_count": 0,
            "overdue_count": 0,
            "completion_rate": 0.0,
            "on_time_rate": 0.0,
            "total_estimated_hours": 0.0,
            "completed_hours": 0.0,
            "pending_hours": 0.0,
            "avg_task_hours": 0.0,
        }

    total = len(tasks)
    completed = [t for t in tasks if t.status == "Completed"]
    in_progress = [t for t in tasks if t.status == "In Progress"]
    pending = [t for t in tasks if t.status == "Pending"]
    overdue = [t for t in tasks if t.is_overdue()]

    completion_rate = round((len(completed) / total) * 100.0, 1)

    # On-time rate: completed tasks where completed_at <= deadline
    on_time_count = 0
    for t in completed:
        if t.completed_at and t.completed_at <= t.deadline:
            on_time_count += 1
        elif not t.completed_at:  # Default to on-time if marked completed without date
            on_time_count += 1
    on_time_rate = round((on_time_count / len(completed)) * 100.0, 1) if completed else 0.0

    total_est_hours = round(sum(t.estimated_hours for t in tasks), 1)
    completed_hours = round(sum(t.estimated_hours for t in completed), 1)
    pending_hours = round(sum(t.estimated_hours for t in (pending + in_progress)), 1)
    avg_hours = round(total_est_hours / total, 1) if total else 0.0

    return {
        "total_tasks": total,
        "completed_count": len(completed),
        "in_progress_count": len(in_progress),
        "pending_count": len(pending),
        "overdue_count": len(overdue),
        "completion_rate": completion_rate,
        "on_time_count": on_time_count,
        "late_completed_count": len(completed) - on_time_count,
        "on_time_rate": on_time_rate,
        "total_estimated_hours": total_est_hours,
        "completed_hours": completed_hours,
        "pending_hours": pending_hours,
        "avg_task_hours": avg_hours
    }

def get_priority_distribution_df(tasks: list[Task]) -> pd.DataFrame:
    """Returns a pandas DataFrame summarizing tasks by priority."""
    if not tasks:
        return pd.DataFrame(columns=["Priority", "Total", "Completed", "Pending", "Total Hours"])

    records = []
    for priority in ["High", "Medium", "Low"]:
        p_tasks = [t for t in tasks if t.priority == priority]
        completed = [t for t in p_tasks if t.status == "Completed"]
        active = [t for t in p_tasks if t.status != "Completed"]
        records.append({
            "Priority": priority,
            "Total": len(p_tasks),
            "Completed": len(completed),
            "Pending": len(active),
            "Total Hours": round(sum(t.estimated_hours for t in p_tasks), 1)
        })
    return pd.DataFrame(records)

# --- Matplotlib Plot Generators for Dashboard and Reports ---

def plot_status_chart(tasks: list[Task]) -> plt.Figure:
    """Generates a sleek Donut Chart showing task status breakdown."""
    fig, ax = plt.subplots(figsize=(4.5, 4.5), facecolor="#111827")
    ax.set_facecolor("#111827")

    counts = {
        "Completed": len([t for t in tasks if t.status == "Completed"]),
        "In Progress": len([t for t in tasks if t.status == "In Progress"]),
        "Pending": len([t for t in tasks if t.status == "Pending"]),
    }
    # Filter out zeros
    filtered = {k: v for k, v in counts.items() if v > 0}
    if not filtered:
        filtered = {"No Tasks": 1}

    colors = {
        "Completed": "#22C55E",    # Success Green
        "In Progress": "#38BDF8",  # Sky Blue
        "Pending": "#64748B",      # Slate / Neutral Gray
        "No Tasks": "#475569"
    }
    wedge_colors = [colors.get(k, "#94A3B8") for k in filtered.keys()]

    wedges, texts, autotexts = ax.pie(
        filtered.values(),
        labels=filtered.keys(),
        autopct="%1.0f%%" if any(counts.values()) else "",
        startangle=140,
        colors=wedge_colors,
        textprops=dict(color="#F8FAFC", fontsize=10, weight="bold"),
        wedgeprops=dict(width=0.42, edgecolor="#0B1120", linewidth=2)
    )
    for at in autotexts:
        at.set_color("#FFFFFF")
        at.set_fontsize(10.5)
        at.set_weight("bold")

    ax.set_title("Task Status Breakdown", color="#F8FAFC", fontsize=12, weight="bold", pad=12)
    plt.tight_layout()
    return fig

def plot_priority_bar_chart(tasks: list[Task]) -> plt.Figure:
    """Generates a modern horizontal bar chart comparing effort and counts across priorities."""
    fig, ax = plt.subplots(figsize=(5.5, 3.8), facecolor="#111827")
    ax.set_facecolor("#111827")

    priorities = ["High", "Medium", "Low"]
    colors = ["#EF4444", "#F59E0B", "#38BDF8"]
    
    counts = [len([t for t in tasks if t.priority == p]) for p in priorities]
    hours = [sum(t.estimated_hours for t in tasks if t.priority == p) for p in priorities]

    y = range(len(priorities))
    bars = ax.barh(y, counts, color=colors, height=0.5, edgecolor="#0B1120", linewidth=1.5)

    ax.set_yticks(y)
    ax.set_yticklabels(priorities, color="#F8FAFC", fontsize=10.5, weight="bold")
    ax.invert_yaxis()  # High priority on top
    ax.tick_params(colors="#94A3B8")
    ax.grid(axis="x", linestyle="--", alpha=0.3, color="#1E293B")
    for spine in ax.spines.values():
        spine.set_color("#1E293B")

    # Add data annotations on bars
    for bar, count, hr in zip(bars, counts, hours):
        ax.text(
            bar.get_width() + 0.1,
            bar.get_y() + bar.get_height() / 2,
            f"{count} tasks ({hr:.1f}h)",
            va="center",
            ha="left",
            color="#F8FAFC",
            fontsize=9.5,
            weight="bold"
        )

    ax.set_title("Workload by Priority", color="#F8FAFC", fontsize=12, weight="bold", pad=12)
    ax.set_xlabel("Number of Tasks", color="#94A3B8", fontsize=9.5)
    plt.tight_layout()
    return fig

def plot_ontime_performance_chart(tasks: list[Task]) -> plt.Figure:
    """Generates a gauge-style stacked bar chart for On-Time vs Late task completions."""
    fig, ax = plt.subplots(figsize=(5.5, 2.2), facecolor="#111827")
    ax.set_facecolor("#111827")

    completed = [t for t in tasks if t.status == "Completed"]
    if not completed:
        ax.text(0.5, 0.5, "No completed tasks yet to evaluate.", ha="center", va="center", color="#94A3B8", fontsize=10.5)
        ax.axis("off")
        return fig

    on_time = sum(1 for t in completed if not t.completed_at or t.completed_at <= t.deadline)
    late = len(completed) - on_time

    on_time_pct = (on_time / len(completed)) * 100
    late_pct = (late / len(completed)) * 100

    ax.barh(0, on_time_pct, color="#22C55E", height=0.38, label=f"On-Time: {on_time} ({on_time_pct:.0f}%)")
    ax.barh(0, late_pct, left=on_time_pct, color="#EF4444", height=0.38, label=f"Late: {late} ({late_pct:.0f}%)")

    ax.set_xlim(0, 100)
    ax.set_yticks([])
    ax.tick_params(colors="#94A3B8")
    ax.set_xlabel("Percentage (%)", color="#94A3B8", fontsize=9)
    ax.set_title("Historical Delivery Reliability (On-Time %)", color="#F8FAFC", fontsize=11.5, weight="bold", pad=10)
    for spine in ax.spines.values():
        spine.set_color("#1E293B")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.35), ncol=2, frameon=False, labelcolor="#F8FAFC", fontsize=9.5)
    plt.tight_layout()
    return fig

def generate_cli_analytics_summary(tasks: list[Task]) -> str:
    """Formats an ASCII analytics report suitable for the CLI interface."""
    m = calculate_productivity_metrics(tasks)
    lines = []
    lines.append("=" * 55)
    lines.append("        📊 SMART REMINDER PRODUCTIVITY ANALYTICS")
    lines.append("=" * 55)
    lines.append(f"• Total Tasks:             {m['total_tasks']}")
    lines.append(f"• Completed:               {m['completed_count']} ({m['completion_rate']}%)")
    lines.append(f"• In Progress:             {m['in_progress_count']}")
    lines.append(f"• Pending:                 {m['pending_count']}")
    lines.append(f"• Overdue:                 {m['overdue_count']}")
    lines.append("-" * 55)
    lines.append(f"• On-Time Delivery Rate:   {m['on_time_rate']}% ({m.get('on_time_count', 0)} of {m['completed_count']} done on-time)")
    lines.append(f"• Total Estimated Work:    {m['total_estimated_hours']} hours")
    lines.append(f"• Completed Work:          {m['completed_hours']} hours")
    lines.append(f"• Remaining Workload:      {m['pending_hours']} hours")
    lines.append(f"• Average Task Duration:   {m['avg_task_hours']} hours")
    lines.append("=" * 55)
    return "\n".join(lines)
