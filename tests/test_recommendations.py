import unittest
import datetime
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from models import Task
from recommendations import generate_task_explanation, generate_daily_schedule_agenda

class TestRecommendations(unittest.TestCase):
    def setUp(self):
        self.ref_date = datetime.date(2026, 9, 20)

    def test_task_explanation_overdue_and_large(self):
        task = Task(1, "Deep Refactoring", "Large refactor", "2026-09-18", "High", 6.0)
        exp = generate_task_explanation(task, reference_date=self.ref_date)
        
        self.assertEqual(exp["task_id"], 1)
        self.assertEqual(exp["title"], "Deep Refactoring")
        self.assertIn("Overdue by 2 day(s)", exp["primary_drivers"])
        self.assertIn("Substantial effort required (6.0h)", exp["primary_drivers"])
        self.assertTrue(any("Immediate triage" in tip for tip in exp["actionable_tips"]))
        self.assertTrue(any("Large task detected" in tip for tip in exp["actionable_tips"]))

    def test_task_explanation_quick_win(self):
        task = Task(2, "Fix Typo", "Small typo fix", "2026-09-22", "High", 0.5)
        exp = generate_task_explanation(task, reference_date=self.ref_date)
        
        self.assertIn("Quick win effort (0.5h)", exp["primary_drivers"])
        self.assertTrue(any("Quick Win" in tip for tip in exp["actionable_tips"]))

    def test_task_explanation_due_today(self):
        task = Task(3, "Submit Report", "Final report", "2026-09-20", "Medium", 2.0)
        exp = generate_task_explanation(task, reference_date=self.ref_date)
        
        self.assertIn("Due today", exp["primary_drivers"])
        self.assertTrue(any("Commit to finishing this today" in tip for tip in exp["actionable_tips"]))

    def test_schedule_agenda_empty(self):
        agenda = generate_daily_schedule_agenda([], max_hours=7.0, reference_date=self.ref_date)
        self.assertEqual(len(agenda["schedule"]), 0)
        self.assertEqual(agenda["total_allocated_hours"], 0.0)
        self.assertEqual(agenda["deferred_tasks_count"], 0)
        self.assertIn("No pending tasks", agenda["notes"])

    def test_schedule_agenda_all_completed(self):
        t1 = Task(1, "Done 1", "Desc", "2026-09-20", "High", 3.0, status="Completed")
        agenda = generate_daily_schedule_agenda([t1], max_hours=7.0, reference_date=self.ref_date)
        self.assertEqual(len(agenda["schedule"]), 0)

    def test_schedule_agenda_capacity_and_prioritization(self):
        t_high_urgent = Task(1, "Urgent Task", "Desc", "2026-09-20", "High", 4.0)
        t_med_soon = Task(2, "Soon Task", "Desc", "2026-09-21", "Medium", 2.0)
        t_low_future = Task(3, "Future Task", "Desc", "2026-09-30", "Low", 3.0)

        tasks = [t_low_future, t_med_soon, t_high_urgent]
        agenda = generate_daily_schedule_agenda(tasks, max_hours=6.5, reference_date=self.ref_date)

        # 4.0h + 2.0h = 6.0h <= 6.5h. The 3.0h task exceeds 6.5h so it should be deferred.
        self.assertEqual(len(agenda["schedule"]), 2)
        self.assertEqual(agenda["schedule"][0]["task"].id, 1)  # Highest priority first
        self.assertEqual(agenda["schedule"][1]["task"].id, 2)
        self.assertEqual(agenda["total_allocated_hours"], 6.0)
        self.assertEqual(agenda["deferred_tasks_count"], 1)
        self.assertIn("Morning Deep Work", agenda["schedule"][0]["block_name"])

if __name__ == "__main__":
    unittest.main()
