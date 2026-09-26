import unittest
import datetime
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from models import Task
from analytics import (
    calculate_productivity_metrics,
    get_priority_distribution_df,
    plot_status_chart,
    plot_priority_bar_chart,
    plot_ontime_performance_chart,
    generate_cli_analytics_summary
)

class TestAnalytics(unittest.TestCase):
    def test_metrics_empty(self):
        m = calculate_productivity_metrics([])
        self.assertEqual(m["total_tasks"], 0)
        self.assertEqual(m["completion_rate"], 0.0)

    def test_metrics_populated(self):
        t1 = Task(1, "Task 1", "Desc", "2026-09-20", "High", 3.0, status="Completed", completed_at_val="2026-09-19")
        t2 = Task(2, "Task 2", "Desc", "2026-09-20", "Medium", 2.0, status="In Progress")
        t3 = Task(3, "Task 3", "Desc", "2026-09-25", "Low", 5.0, status="Pending")

        m = calculate_productivity_metrics([t1, t2, t3])
        self.assertEqual(m["total_tasks"], 3)
        self.assertEqual(m["completed_count"], 1)
        self.assertEqual(m["in_progress_count"], 1)
        self.assertEqual(m["pending_count"], 1)
        self.assertEqual(round(m["completion_rate"], 1), 33.3)
        self.assertEqual(m["on_time_rate"], 100.0)
        self.assertEqual(m["total_estimated_hours"], 10.0)

    def test_priority_dataframe(self):
        t1 = Task(1, "Task 1", "Desc", "2026-09-20", "High", 3.0)
        df = get_priority_distribution_df([t1])
        self.assertEqual(len(df), 3)
        self.assertIn("High", df["Priority"].values)

    def test_plot_generation(self):
        t1 = Task(1, "Task 1", "Desc", "2026-09-20", "High", 3.0, status="Completed")
        fig1 = plot_status_chart([t1])
        self.assertIsNotNone(fig1)

        fig2 = plot_priority_bar_chart([t1])
        self.assertIsNotNone(fig2)

        fig3 = plot_ontime_performance_chart([t1])
        self.assertIsNotNone(fig3)

    def test_cli_summary(self):
        t1 = Task(1, "Task 1", "Desc", "2026-09-20", "High", 3.0)
        summary = generate_cli_analytics_summary([t1])
        self.assertIn("SMART REMINDER PRODUCTIVITY ANALYTICS", summary)
        self.assertIn("Total Tasks:", summary)

if __name__ == "__main__":
    unittest.main()
