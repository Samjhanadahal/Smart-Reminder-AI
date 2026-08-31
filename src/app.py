import sys
from models import Task
import database

def print_menu():
    """Prints the application menu options."""
    print("\n" + "=" * 40)
    print("      SMART REMINDER AI - CLI MENU")
    print("=" * 40)
    print("1. Add a Task")
    print("2. View All Tasks")
    print("3. Update Task Status")
    print("4. Delete a Task")
    print("5. Exit")
    print("=" * 40)

def add_task_flow():
    """Guide the user through adding a task with validation."""
    print("\n--- Add a New Task ---")
    title = input("Enter task name: ").strip()
    if not title:
        print("Error: Task name cannot be empty.")
        return
        
    description = input("Enter description: ").strip()
    deadline_str = input("Enter deadline (YYYY-MM-DD): ").strip()
    priority = input("Enter priority (Low, Medium, High): ").strip()
    
    try:
        estimated_hours_input = input("Enter estimated completion hours: ").strip()
        estimated_hours = float(estimated_hours_input)
    except ValueError:
        print("Error: Estimated hours must be a valid number.")
        return

    try:
        # Validate task parameters by instantiating Task with dummy ID
        # Validation logic is handled inside Task.__init__
        dummy_task = Task(
            task_id=0,
            title=title,
            description=description,
            deadline_str=deadline_str,
            priority=priority,
            estimated_hours=estimated_hours
        )
        
        # Save to SQLite
        task_id = database.add_task(
            title=dummy_task.title,
            description=dummy_task.description,
            deadline=dummy_task.deadline.isoformat(),
            priority=dummy_task.priority,
            estimated_hours=dummy_task.estimated_hours
        )
        print(f"\nSuccess: Task '{title}' added successfully with ID {task_id}!")
    except ValueError as e:
        print(f"\nError creating task: {e}")

def view_tasks_flow():
    """Display all tasks in the system."""
    print("\n--- All Tasks ---")
    tasks = database.get_all_tasks()
    if not tasks:
        print("No tasks found. Try adding some!")
        return
        
    for task in tasks:
        print("-" * 40)
        print(task)
    print("-" * 40)

def update_status_flow():
    """Update status of a specific task by ID."""
    print("\n--- Update Task Status ---")
    tasks = database.get_all_tasks()
    if not tasks:
        print("No tasks available to update.")
        return
        
    try:
        task_id = int(input("Enter Task ID to update: ").strip())
    except ValueError:
        print("Error: ID must be a number.")
        return

    # Find the task with the matching ID
    task_to_update = next((t for t in tasks if t.id == task_id), None)
    if not task_to_update:
        print(f"Error: Task with ID {task_id} not found.")
        return

    print(f"Current status: [{task_to_update.status}]")
    print("Choose new status:")
    print("1. Pending")
    print("2. In Progress")
    print("3. Completed")
    choice = input("Enter choice (1-3): ").strip()

    status_map = {"1": "Pending", "2": "In Progress", "3": "Completed"}
    if choice in status_map:
        new_status = status_map[choice]
        try:
            database.update_task_status(task_id, new_status)
            print(f"Success: Task {task_id} status updated to [{new_status}]!")
        except ValueError as e:
            print(f"Error: {e}")
    else:
        print("Error: Invalid choice.")

def delete_task_flow():
    """Delete a task by ID."""
    print("\n--- Delete a Task ---")
    tasks = database.get_all_tasks()
    if not tasks:
        print("No tasks to delete.")
        return

    try:
        task_id = int(input("Enter Task ID to delete: ").strip())
    except ValueError:
        print("Error: ID must be a number.")
        return

    # Find the task
    task_to_delete = next((t for t in tasks if t.id == task_id), None)
    if not task_to_delete:
        print(f"Error: Task with ID {task_id} not found.")
        return

    database.delete_task(task_id)
    print(f"Success: Task ID {task_id} ('{task_to_delete.title}') deleted.")

def main():
    database.init_db()
    
    while True:
        print_menu()
        choice = input("Select an option (1-5): ").strip()
        
        if choice == "1":
            add_task_flow()
        elif choice == "2":
            view_tasks_flow()
        elif choice == "3":
            update_status_flow()
        elif choice == "4":
            delete_task_flow()
        elif choice == "5":
            print("\nThank you for using Smart Reminder AI. Goodbye!")
            sys.exit(0)
        else:
            print("\nError: Invalid choice. Please enter a number between 1 and 5.")

if __name__ == "__main__":
    main()
