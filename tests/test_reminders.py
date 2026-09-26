import unittest
import datetime
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from models import Task
from reminders import get_reminder_alerts, check_workload_overload, generate_daily_digest

class TestReminders(unittest.TestCase):
    def setUp(self):
        self.ref_date = datetime.date(2026, 9, 20)

    def test_reminder_categorization(self):
        t_overdue = Task(1, "Overdue", "Desc", "2026-09-18", "High", 3.0)
        t_today = Task(2, "Due Today", "Desc", "2026-09-20", "Medium", 2.0)
        t_soon = Task(3, "Due in 2d", "Desc", "2026-09-22", "High", 4.0)
        t_week = Task(4, "Due in 5d", "Desc", "2026-09-25", "Low", 1.5)
        t_done = Task(5, "Done", "Desc", "2026-09-18", "High", 3.0, status="Completed")

        tasks = [t_overdue, t_today, t_soon, t_week, t_done]
        alerts = get_reminder_alerts(tasks, reference_date=self.ref_date)

        self.assertEqual(alerts["overdue"].count, 1)
        self.assertEqual(alerts["overdue"].tasks[0].id, 1)

        self.assertEqual(alerts["due_today"].count, 1)
        self.assertEqual(alerts["due_today"].tasks[0].id, 2)

        self.assertEqual(alerts["due_soon"].count, 1)
        self.assertEqual(alerts["due_soon"].tasks[0].id, 3)

        self.assertEqual(alerts["due_week"].count, 1)
        self.assertEqual(alerts["due_week"].tasks[0].id, 4)

    def test_workload_overload(self):
        # 6h overdue + 4h due today = 10h > 8h threshold
        t1 = Task(1, "Task 1", "Desc", "2026-09-19", "High", 6.0)
        t2 = Task(2, "Task 2", "Desc", "2026-09-20", "Medium", 4.0)
        res = check_workload_overload([t1, t2], max_daily_hours=8.0, reference_date=self.ref_date)
        
        self.assertTrue(res["is_overloaded"])
        self.assertEqual(res["total_hours"], 10.0)
        self.assertEqual(res["hours_deficit"], 2.0)

    def test_daily_digest_output(self):
        t1 = Task(1, "Task 1", "Desc", "2026-09-19", "High", 3.0)
        digest = generate_daily_digest([t1], reference_date=self.ref_date)
        self.assertIn("SMART REMINDER DAILY DIGEST", digest)
        self.assertIn("OVERDUE TASKS", digest)

if __name__ == "__main__":
    unittest.main()
