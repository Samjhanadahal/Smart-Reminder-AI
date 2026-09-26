import unittest
import datetime
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from models import Task
from smart_priority import calculate_smart_priority, rank_tasks

class TestSmartPriority(unittest.TestCase):
    def setUp(self):
        self.ref_date = datetime.date(2026, 9, 20)

    def test_completed_task_score_zero(self):
        task = Task(1, "Done task", "Desc", "2026-09-20", "High", 3.0, status="Completed")
        res = calculate_smart_priority(task, reference_date=self.ref_date)
        self.assertEqual(res["score"], 0.0)
        self.assertEqual(res["band"], "Completed")

    def test_overdue_task_high_score(self):
        # 3 days overdue
        task = Task(2, "Overdue task", "Desc", "2026-09-17", "High", 4.0)
        res = calculate_smart_priority(task, reference_date=self.ref_date)
        self.assertGreaterEqual(res["score"], 80.0)
        self.assertEqual(res["band"], "Critical")

    def test_due_today_task(self):
        task = Task(3, "Due today", "Desc", "2026-09-20", "High", 2.0)
        res = calculate_smart_priority(task, reference_date=self.ref_date)
        self.assertGreaterEqual(res["score"], 70.0)

    def test_low_priority_future_task(self):
        # 14 days in future, low priority, low effort
        task = Task(4, "Future task", "Desc", "2026-10-04", "Low", 1.0)
        res = calculate_smart_priority(task, reference_date=self.ref_date)
        self.assertLess(res["score"], 40.0)
        self.assertEqual(res["band"], "Low")

    def test_rank_tasks(self):
        t1 = Task(1, "Low future", "Desc", "2026-10-10", "Low", 1.0)
        t2 = Task(2, "High overdue", "Desc", "2026-09-18", "High", 5.0)
        t3 = Task(3, "Medium today", "Desc", "2026-09-20", "Medium", 2.0)

        ranked = rank_tasks([t1, t2, t3], reference_date=self.ref_date)
        # t2 should be rank 1, followed by t3, then t1
        self.assertEqual(ranked[0][0].id, 2)
        self.assertEqual(ranked[1][0].id, 3)
        self.assertEqual(ranked[2][0].id, 1)

if __name__ == "__main__":
    unittest.main()
