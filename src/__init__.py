"""
Smart Reminder AI Package
Intelligent task management, AI-driven priority scoring, risk prediction, and schedule optimization.
"""

from .models import Task
from .database import (
    init_db,
    add_task,
    get_all_tasks,
    get_task_by_id,
    update_task,
    update_task_status,
    delete_task,
    get_tasks_as_dataframe,
    seed_sample_tasks
)
from .smart_priority import calculate_smart_priority, rank_tasks
from .reminders import get_reminder_alerts, check_workload_overload, generate_daily_digest
from .analytics import (
    calculate_productivity_metrics,
    get_priority_distribution_df,
    plot_status_chart,
    plot_priority_bar_chart,
    plot_ontime_performance_chart,
    generate_cli_analytics_summary
)
from .ml_predictor import predict_task_completion, predict_hypothetical
from .recommendations import generate_task_explanation, generate_daily_schedule_agenda

__all__ = [
    "Task",
    "init_db",
    "add_task",
    "get_all_tasks",
    "get_task_by_id",
    "update_task",
    "update_task_status",
    "delete_task",
    "get_tasks_as_dataframe",
    "seed_sample_tasks",
    "calculate_smart_priority",
    "rank_tasks",
    "get_reminder_alerts",
    "check_workload_overload",
    "generate_daily_digest",
    "calculate_productivity_metrics",
    "get_priority_distribution_df",
    "plot_status_chart",
    "plot_priority_bar_chart",
    "plot_ontime_performance_chart",
    "generate_cli_analytics_summary",
    "predict_task_completion",
    "predict_hypothetical",
    "generate_task_explanation",
    "generate_daily_schedule_agenda"
]
