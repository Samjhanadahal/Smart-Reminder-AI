import sqlite3
import os
import datetime
from models import Task

def get_db_connection(db_path="data/tasks.db"):
    """Establishes and returns a connection to the SQLite database."""
    # Ensure the parent directory of the database file exists
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
    cursor.execute("SELECT * FROM tasks")
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
