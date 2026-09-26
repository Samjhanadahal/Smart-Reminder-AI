import sqlite3
import os
import datetime
try:
    from models import Task
except ImportError:
    from src.models import Task

def get_db_connection(db_path="data/tasks.db"):
    """Establishes and returns a connection to the SQLite database."""
    dir_name = os.path.dirname(db_path)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(db_path="data/tasks.db"):
    """Initializes the database and creates the tasks table if it does not exist."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            deadline TEXT NOT NULL,
            priority TEXT NOT NULL,
            estimated_hours REAL NOT NULL,
            status TEXT NOT NULL DEFAULT 'Pending',
            created_at TEXT NOT NULL,
            completed_at TEXT
        )
    """)
    conn.commit()
    conn.close()

def add_task(title: str, description: str, deadline: str, priority: str, estimated_hours: float, db_path="data/tasks.db") -> int:
    """Inserts a new task into the database and returns its auto-generated ID."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    created_at = datetime.date.today().isoformat()
    cursor.execute("""
        INSERT INTO tasks (title, description, deadline, priority, estimated_hours, status, created_at, completed_at)
        VALUES (?, ?, ?, ?, ?, 'Pending', ?, NULL)
    """, (title, description, deadline, priority.capitalize(), float(estimated_hours), created_at))
    conn.commit()
    task_id = cursor.lastrowid
    conn.close()
    return task_id

def get_all_tasks(db_path="data/tasks.db") -> list:
    """Retrieves all tasks from the database and returns them as a list of Task objects."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks ORDER BY id ASC")
    rows = cursor.fetchall()
    conn.close()
    
    tasks = []
    for row in rows:
        task = Task(
            task_id=row['id'],
            title=row['title'],
            description=row['description'],
            deadline_str=row['deadline'],
            priority=row['priority'],
            estimated_hours=row['estimated_hours'],
            status=row['status'],
            created_at_val=row['created_at'],
            completed_at_val=row['completed_at']
        )
        tasks.append(task)
    return tasks

def get_task_by_id(task_id: int, db_path="data/tasks.db"):
    """Fetches a single task by ID."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    return Task(
        task_id=row['id'],
        title=row['title'],
        description=row['description'],
        deadline_str=row['deadline'],
        priority=row['priority'],
        estimated_hours=row['estimated_hours'],
        status=row['status'],
        created_at_val=row['created_at'],
        completed_at_val=row['completed_at']
    )

def update_task(task_id: int, title: str, description: str, deadline: str, priority: str, estimated_hours: float, db_path="data/tasks.db") -> bool:
    """Updates all details of an existing task."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE tasks
        SET title = ?, description = ?, deadline = ?, priority = ?, estimated_hours = ?
        WHERE id = ?
    """, (title, description, deadline, priority.capitalize(), float(estimated_hours), task_id))
    rows_affected = cursor.rowcount
    conn.commit()
    conn.close()
    return rows_affected > 0

def update_task_status(task_id: int, new_status: str, db_path="data/tasks.db") -> bool:
    """Updates the status and completed_at values of a task in the database."""
    cleaned_status = new_status.title()
    if cleaned_status not in ["Pending", "In Progress", "Completed"]:
        raise ValueError("Status must be one of: Pending, In Progress, Completed")
        
    completed_at = datetime.date.today().isoformat() if cleaned_status == "Completed" else None
    
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE tasks
        SET status = ?, completed_at = ?
        WHERE id = ?
    """, (cleaned_status, completed_at, task_id))
    rows_affected = cursor.rowcount
    conn.commit()
    conn.close()
    return rows_affected > 0

def delete_task(task_id: int, db_path="data/tasks.db") -> bool:
    """Deletes a task from the database by its ID."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    rows_affected = cursor.rowcount
    conn.commit()
    conn.close()
    return rows_affected > 0

def get_tasks_as_dataframe(db_path="data/tasks.db"):
    """Returns all tasks as a pandas DataFrame with enriched computed columns."""
    import pandas as pd
    tasks = get_all_tasks(db_path)
    if not tasks:
        return pd.DataFrame(columns=[
            "id", "title", "description", "deadline", "priority", "priority_weight",
            "estimated_hours", "status", "created_at", "completed_at",
            "days_remaining", "is_overdue", "is_due_today"
        ])
    data = [t.to_dict() for t in tasks]
    return pd.DataFrame(data)

def seed_sample_tasks(db_path="data/tasks.db", clear_existing: bool = False):
    """Populates the database with realistic sample tasks across multiple priorities and statuses."""
    init_db(db_path)
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    if clear_existing:
        cursor.execute("DELETE FROM tasks")
        conn.commit()
    
    today = datetime.date.today()
    sample_data = [
        ("Finalize Q3 Budget & Expenses", "Review financial sheets, receipts, and submit to accounting.", (today - datetime.timedelta(days=2)).isoformat(), "High", 4.0, "Pending", (today - datetime.timedelta(days=7)).isoformat(), None),
        ("Client Project Presentation", "Prepare executive slide deck and rehearse demo walkthrough.", today.isoformat(), "High", 3.5, "In Progress", (today - datetime.timedelta(days=4)).isoformat(), None),
        ("Code Review for Security Patch", "Review PR #142 for OWASP compliance and authentication fixes.", (today + datetime.timedelta(days=1)).isoformat(), "High", 2.0, "Pending", (today - datetime.timedelta(days=2)).isoformat(), None),
        ("Update API Documentation Wiki", "Document new REST endpoints and authentication tokens for developers.", (today + datetime.timedelta(days=3)).isoformat(), "Medium", 5.0, "In Progress", (today - datetime.timedelta(days=5)).isoformat(), None),
        ("Organize Team Backlog Grooming", "Triage open Jira tickets, estimate story points, and assign sprint goals.", (today + datetime.timedelta(days=5)).isoformat(), "Medium", 2.5, "Pending", (today - datetime.timedelta(days=1)).isoformat(), None),
        ("Weekly Server Backup Check", "Verify cloud snapshot integrity and check automated backup logs.", (today + datetime.timedelta(days=7)).isoformat(), "Low", 1.0, "Pending", today.isoformat(), None),
        ("Design System Architecture Draft", "Create system block diagram and database schema models.", (today - datetime.timedelta(days=3)).isoformat(), "High", 6.0, "Completed", (today - datetime.timedelta(days=8)).isoformat(), (today - datetime.timedelta(days=4)).isoformat()),
        ("Setup Continuous Integration Pipeline", "Configure GitHub actions for automated linting and unit tests.", (today - datetime.timedelta(days=1)).isoformat(), "Medium", 3.0, "Completed", (today - datetime.timedelta(days=5)).isoformat(), (today - datetime.timedelta(days=1)).isoformat()),
    ]
    
    for item in sample_data:
        cursor.execute("""
            INSERT INTO tasks (title, description, deadline, priority, estimated_hours, status, created_at, completed_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, item)
    conn.commit()
    conn.close()
