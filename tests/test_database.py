import unittest
import sys
import os
import datetime

# Add src to python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
import database
from models import Task

class TestDatabase(unittest.TestCase):
    def setUp(self):
        # Use a temporary database file for testing
        self.db_path = "data/test_tasks.db"
        if os.path.exists(self.db_path):
            try:
                os.remove(self.db_path)
            except OSError:
                pass
        database.init_db(self.db_path)

    def tearDown(self):
        if os.path.exists(self.db_path):
            try:
                os.remove(self.db_path)
            except OSError:
                pass

    def test_init_db(self):
        # Verify the table exists
        conn = database.get_db_connection(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tasks'")
        table = cursor.fetchone()
        conn.close()
        self.assertIsNotNone(table)
        self.assertEqual(table['name'], 'tasks')

    def test_add_and_get_tasks(self):
        # Add a task
        task_id = database.add_task(
            title="Database Test",
            description="Testing DB operations",
            deadline="2026-09-10",
            priority="High",
            estimated_hours=4.5,
            db_path=self.db_path
        )
        self.assertEqual(task_id, 1)

        # Retrieve tasks
        tasks = database.get_all_tasks(self.db_path)
        self.assertEqual(len(tasks), 1)
        
        task = tasks[0]
        self.assertEqual(task.id, 1)
        self.assertEqual(task.title, "Database Test")
        self.assertEqual(task.description, "Testing DB operations")
        self.assertEqual(task.deadline, datetime.date(2026, 9, 10))
        self.assertEqual(task.priority, "High")
        self.assertEqual(task.estimated_hours, 4.5)
        self.assertEqual(task.status, "Pending")
        self.assertEqual(task.created_at, datetime.date.today())
        self.assertIsNone(task.completed_at)

    def test_update_task_status(self):
        # Add a task
        task_id = database.add_task(
            title="Database Test",
            description="Testing DB operations",
            deadline="2026-09-10",
            priority="High",
            estimated_hours=4.5,
            db_path=self.db_path
        )
        
        # Update status to In Progress
        success = database.update_task_status(task_id, "In Progress", db_path=self.db_path)
        self.assertTrue(success)
        
        tasks = database.get_all_tasks(self.db_path)
        self.assertEqual(tasks[0].status, "In Progress")
        self.assertIsNone(tasks[0].completed_at)

        # Update status to Completed
        success = database.update_task_status(task_id, "Completed", db_path=self.db_path)
        self.assertTrue(success)
        
        tasks = database.get_all_tasks(self.db_path)
        self.assertEqual(tasks[0].status, "Completed")
        self.assertEqual(tasks[0].completed_at, datetime.date.today())

        # Test updating with invalid status
        with self.assertRaises(ValueError):
            database.update_task_status(task_id, "Archived", db_path=self.db_path)

    def test_delete_task(self):
        # Add a task
        task_id = database.add_task(
            title="Database Test",
            description="Testing DB operations",
            deadline="2026-09-10",
            priority="High",
            estimated_hours=4.5,
            db_path=self.db_path
        )
        
        # Verify it exists
        tasks = database.get_all_tasks(self.db_path)
        self.assertEqual(len(tasks), 1)

        # Delete it
        success = database.delete_task(task_id, db_path=self.db_path)
        self.assertTrue(success)

        # Verify it is deleted
        tasks = database.get_all_tasks(self.db_path)
        self.assertEqual(len(tasks), 0)

        # Delete non-existent
        success = database.delete_task(999, db_path=self.db_path)
        self.assertFalse(success)

    def test_get_task_by_id(self):
        task_id = database.add_task(
            title="Fetch By ID Test",
            description="Testing get_task_by_id",
            deadline="2026-10-15",
            priority="Medium",
            estimated_hours=3.0,
            db_path=self.db_path
        )
        task = database.get_task_by_id(task_id, db_path=self.db_path)
        self.assertIsNotNone(task)
        self.assertEqual(task.id, task_id)
        self.assertEqual(task.title, "Fetch By ID Test")

        # Non-existent task returns None
        non_existent = database.get_task_by_id(9999, db_path=self.db_path)
        self.assertIsNone(non_existent)

    def test_update_task_details(self):
        task_id = database.add_task(
            title="Initial Title",
            description="Initial Desc",
            deadline="2026-10-01",
            priority="Low",
            estimated_hours=1.5,
            db_path=self.db_path
        )
        updated = database.update_task(
            task_id=task_id,
            title="Updated Title",
            description="Updated Desc",
            deadline="2026-10-05",
            priority="High",
            estimated_hours=4.0,
            db_path=self.db_path
        )
        self.assertTrue(updated)

        task = database.get_task_by_id(task_id, db_path=self.db_path)
        self.assertEqual(task.title, "Updated Title")
        self.assertEqual(task.description, "Updated Desc")
        self.assertEqual(task.deadline, datetime.date(2026, 10, 5))
        self.assertEqual(task.priority, "High")
        self.assertEqual(task.estimated_hours, 4.0)

if __name__ == "__main__":
    unittest.main()

