import unittest
import datetime
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from models import Task
from ml_predictor import predict_task_completion, predict_hypothetical, extract_features_from_values

class TestMLPredictor(unittest.TestCase):
    def setUp(self):
        self.ref_date = datetime.date(2026, 9, 20)

    def test_feature_extraction(self):
        features = extract_features_from_values(4.0, 5, "High", "In Progress")
        self.assertEqual(features.shape, (1, 5))
        self.assertEqual(features[0][0], 4.0)
        self.assertEqual(features[0][1], 5.0)
        self.assertEqual(features[0][2], 3.0)  # High = 3.0
        self.assertEqual(features[0][4], 1.0)  # In progress = 1.0

    def test_predict_task_completion_healthy(self):
        # 10 days remaining with only 2 hours effort -> high probability
        task = Task(1, "Healthy task", "Desc", "2026-09-30", "Medium", 2.0)
        res = predict_task_completion(task, reference_date=self.ref_date)
        self.assertIn("probability", res)
        self.assertIn("risk_level", res)
        self.assertGreater(res["probability"], 60.0)

    def test_predict_task_completion_overdue(self):
        task = Task(2, "Overdue task", "Desc", "2026-09-15", "High", 5.0)
        res = predict_task_completion(task, reference_date=self.ref_date)
        self.assertLess(res["probability"], 20.0)
        self.assertIn("High Risk", res["risk_level"])

    def test_predict_hypothetical(self):
        res = predict_hypothetical(
            estimated_hours=3.0,
            deadline_str="2026-09-28",
            priority="High",
            reference_date=self.ref_date
        )
        self.assertIn("probability", res)
        self.assertIn("risk_level", res)

if __name__ == "__main__":
    unittest.main()
