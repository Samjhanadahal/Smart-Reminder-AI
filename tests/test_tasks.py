import unittest
import datetime
import sys
import os

# Add src to the Python search path so we can import models
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from models import Task

class TestTaskModel(unittest.TestCase):
    def test_task_creation_success(self):
        """Test creating a task with valid attributes."""
        task = Task(
            task_id=1,
            title="Read book",
            description="Read 2 chapters",
            deadline_str="2026-09-15",
            priority="High",
            estimated_hours=2.5
        )
        self.assertEqual(task.id, 1)
        self.assertEqual(task.title, "Read book")
        self.assertEqual(task.description, "Read 2 chapters")
        self.assertEqual(task.deadline, datetime.date(2026, 9, 15))
        self.assertEqual(task.priority, "High")
        self.assertEqual(task.estimated_hours, 2.5)
        self.assertEqual(task.status, "Pending")
        self.assertIsNone(task.completed_at)

    def test_task_creation_invalid_priority(self):
        """Test that invalid priority values raise a ValueError."""
        with self.assertRaises(ValueError):
            Task(1, "Title", "Desc", "2026-09-15", "Urgent", 1.0)

    def test_task_creation_invalid_deadline(self):
        """Test that invalid date formats raise a ValueError."""
        with self.assertRaises(ValueError):
            Task(1, "Title", "Desc", "15-09-2026", "High", 1.0)

    def test_task_creation_negative_hours(self):
        """Test that negative estimated hours raise a ValueError."""
        with self.assertRaises(ValueError):
            Task(1, "Title", "Desc", "2026-09-15", "High", -5.0)

    def test_status_updates(self):
        """Test updating task status and corresponding completion dates."""
        task = Task(1, "Title", "Desc", "2026-09-15", "Medium", 1.5)
        
        # Update to In Progress
        task.update_status("In Progress")
        self.assertEqual(task.status, "In Progress")
        self.assertIsNone(task.completed_at)
        
        # Update to Completed
        task.update_status("Completed")
        self.assertEqual(task.status, "Completed")
        self.assertEqual(task.completed_at, datetime.date.today())
        
        # Revert to Pending
        task.update_status("Pending")
        self.assertEqual(task.status, "Pending")
        self.assertIsNone(task.completed_at)

    def test_invalid_status_update(self):
        """Test that invalid status transitions raise a ValueError."""
        task = Task(1, "Title", "Desc", "2026-09-15", "Medium", 1.5)
        with self.assertRaises(ValueError):
            task.update_status("Archived")

if __name__ == "__main__":
    unittest.main()
