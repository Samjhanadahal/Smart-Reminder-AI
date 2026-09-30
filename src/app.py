import sys
import os
import subprocess
import datetime

# Ensure src directory is in sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

try:
    from models import Task
    import database
    from smart_priority import calculate_smart_priority, rank_tasks
    from reminders import generate_daily_digest, get_reminder_alerts
    from analytics import generate_cli_analytics_summary
    from ml_predictor import predict_task_completion, predict_hypothetical
    from recommendations import generate_task_explanation, generate_daily_schedule_agenda
except ImportError:
    from src.models import Task
    from src import database
    from src.smart_priority import calculate_smart_priority, rank_tasks
    from src.reminders import generate_daily_digest, get_reminder_alerts
    from src.analytics import generate_cli_analytics_summary
    from src.ml_predictor import predict_task_completion, predict_hypothetical
    from src.recommendations import generate_task_explanation, generate_daily_schedule_agenda

def print_menu():
    """Prints the application menu options."""
    print("\n" + "=" * 55)
    print("         ⚡ SMART REMINDER AI - MASTER MENU")
    print("=" * 55)
    print(" 1. Add a New Task (with AI Feasibility Forecast)")
    print(" 2. View All Tasks (Standard View)")
    print(" 3. View Smart Priority AI Ranked Tasks (Phase 3)")
    print(" 4. View Reminder Alerts & Daily Digest (Phase 4)")
    print(" 5. View Productivity Analytics Summary (Phase 5)")
    print(" 6. AI Completion Predictions & Explanations (Phase 6 & 7)")
    print(" 7. Generate Optimized Daily Work Schedule (Phase 7)")
    print(" 8. Update Task Status")
    print(" 9. Edit Task Details (Title, Deadline, Priority, Effort)")
    print("10. Delete a Task")
    print("11. Seed Realistic Sample Tasks (Demo Data)")
    print("12. Launch Streamlit Web Dashboard (Phase 8)")
    print("13. Exit")
    print("=" * 55)

def add_task_flow():
    """Guide the user through adding a task with live AI predictions."""
    print("\n--- ➕ Add a New Task ---")
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

    # Live ML forecast before saving
    pred = predict_hypothetical(estimated_hours, deadline_str, priority)
    print(f"\n[AI Forecast] On-Time Probability: {pred['probability']}% ({pred['risk_level']})")
    print(f"             Guidance: {pred['explanation']}")

    confirm = input("Confirm and save task? (Y/n): ").strip().lower()
    if confirm in ["n", "no"]:
        print("Task creation cancelled.")
        return

    try:
        dummy_task = Task(
            task_id=0,
            title=title,
            description=description,
            deadline_str=deadline_str,
            priority=priority,
            estimated_hours=estimated_hours
        )
        
        task_id = database.add_task(
            title=dummy_task.title,
            description=dummy_task.description,
            deadline=dummy_task.deadline.isoformat(),
            priority=dummy_task.priority,
            estimated_hours=dummy_task.estimated_hours
        )
        print(f"\n✅ Success: Task '{title}' added successfully with ID #{task_id}!")
    except ValueError as e:
        print(f"\n❌ Error creating task: {e}")

def view_tasks_flow():
    """Display all tasks in the system."""
    print("\n--- 📋 All Tasks (Standard View) ---")
    tasks = database.get_all_tasks()
    if not tasks:
        print("No tasks found. Try adding some or seeding sample tasks!")
        return
        
    for task in tasks:
        print("-" * 50)
        print(task)
    print("-" * 50)

def view_smart_priority_flow():
    """Display tasks ranked by Smart Priority Score."""
    print("\n--- 🎯 Tasks Ranked by Smart Priority (Phase 3) ---")
    tasks = database.get_all_tasks()
    if not tasks:
        print("No tasks found.")
        return

    ranked = rank_tasks(tasks, include_completed=True)
    for rank, (task, meta) in enumerate(ranked, start=1):
        status_flag = f"[{task.status}]"
        print(f"\nRank #{rank} | Score: {meta['score']}/100 [{meta['band']}] {status_flag}")
        print(f"  Title: #{task.id} - {task.title}")
        print(f"  Deadline: {task.deadline} (Days: {task.days_remaining()}) | Priority: {task.priority} | Est: {task.estimated_hours}h")
        print(f"  Factors: {meta['explanation']}")

def view_reminders_flow():
    """Display reminder digest and alerts."""
    print("\n--- 🔔 Reminder Alerts & Daily Digest (Phase 4) ---")
    tasks = database.get_all_tasks()
    if not tasks:
        print("No tasks found.")
        return
    digest = generate_daily_digest(tasks)
    print(digest)

def view_analytics_flow():
    """Display productivity analytics summary."""
    print("\n--- 📊 Productivity Analytics (Phase 5) ---")
    tasks = database.get_all_tasks()
    summary = generate_cli_analytics_summary(tasks)
    print(summary)

def view_ml_predictions_flow():
    """Display ML completion predictions and XAI explanations."""
    print("\n--- 🤖 ML Predictions & Explainable AI (Phases 6 & 7) ---")
    tasks = database.get_all_tasks()
    active_tasks = [t for t in tasks if t.status != "Completed"]
    if not active_tasks:
        print("No active pending tasks to predict.")
        return

    for task in active_tasks:
        pred = predict_task_completion(task)
        exp = generate_task_explanation(task)
        print("-" * 55)
        print(f"Task #{task.id}: {task.title}")
        print(f"  • ML On-Time Probability: {pred['probability']}% ({pred['risk_level']})")
        print(f"  • Urgency Drivers:        {', '.join(exp['primary_drivers'])}")
        if exp["actionable_tips"]:
            print(f"  • Actionable Tips:        {exp['actionable_tips'][0]}")

def view_schedule_optimizer_flow():
    """Generate daily schedule agenda."""
    print("\n--- ⏱️ Daily Work Schedule Optimizer (Phase 7) ---")
    tasks = database.get_all_tasks()
    try:
        hours_in = input("Enter available work capacity today in hours (default 7.0): ").strip()
        hours = float(hours_in) if hours_in else 7.0
    except ValueError:
        hours = 7.0

    agenda = generate_daily_schedule_agenda(tasks, max_hours=hours)
    print(f"\n{agenda['notes']}")
    for item in agenda["schedule"]:
        t = item["task"]
        print(f"  [{item['time_slot']}] {item['block_name']} ({item['hours']}h)")
        print(f"    -> Task #{t.id}: {t.title} (Smart Score: {item['smart_score']})")

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
            print(f"✅ Success: Task #{task_id} status updated to [{new_status}]!")
        except ValueError as e:
            print(f"Error: {e}")
    else:
        print("Error: Invalid choice.")

def edit_task_flow():
    """Guide the user through editing existing task details."""
    print("\n--- ✏️ Edit Task Details ---")
    tasks = database.get_all_tasks()
    if not tasks:
        print("No tasks available to edit.")
        return

    try:
        task_id = int(input("Enter Task ID to edit: ").strip())
    except ValueError:
        print("Error: ID must be a number.")
        return

    task = next((t for t in tasks if t.id == task_id), None)
    if not task:
        print(f"Error: Task with ID {task_id} not found.")
        return

    print(f"\nEditing Task #{task.id}: {task.title}")
    print("Press Enter to keep the current value shown in brackets [current].")

    new_title = input(f"Enter title [{task.title}]: ").strip()
    new_title = new_title if new_title else task.title

    current_desc = task.description or ""
    new_desc = input(f"Enter description [{current_desc}]: ").strip()
    new_desc = new_desc if new_desc else current_desc

    new_deadline = input(f"Enter deadline (YYYY-MM-DD) [{task.deadline}]: ").strip()
    new_deadline = new_deadline if new_deadline else task.deadline.isoformat()

    new_priority = input(f"Enter priority (High, Medium, Low) [{task.priority}]: ").strip()
    new_priority = new_priority.capitalize() if new_priority else task.priority
    if new_priority not in ["High", "Medium", "Low"]:
        print("Error: Priority must be High, Medium, or Low.")
        return

    hours_input = input(f"Enter estimated hours [{task.estimated_hours}]: ").strip()
    if hours_input:
        try:
            new_hours = float(hours_input)
            if new_hours < 0:
                print("Error: Estimated hours cannot be negative.")
                return
        except ValueError:
            print("Error: Invalid number for hours.")
            return
    else:
        new_hours = task.estimated_hours

    try:
        datetime.datetime.strptime(new_deadline, "%Y-%m-%d")
        database.update_task(
            task_id=task.id,
            title=new_title,
            description=new_desc,
            deadline=new_deadline,
            priority=new_priority,
            estimated_hours=new_hours
        )
        print(f"\n✅ Success: Task #{task.id} updated successfully!")
    except ValueError as e:
        print(f"\n❌ Error updating task: {e}")

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

    task_to_delete = next((t for t in tasks if t.id == task_id), None)
    if not task_to_delete:
        print(f"Error: Task with ID {task_id} not found.")
        return

    database.delete_task(task_id)
    print(f"✅ Success: Task ID #{task_id} ('{task_to_delete.title}') deleted.")

def seed_sample_flow():
    """Seed sample tasks."""
    confirm = input("Load realistic sample tasks? This will populate sample records (Y/n): ").strip().lower()
    if confirm in ["n", "no"]:
        return
    database.seed_sample_tasks(clear_existing=False)
    print("✅ Success: Sample tasks added successfully!")

def launch_dashboard_flow():
    """Launches the Streamlit Web Dashboard."""
    dashboard_path = os.path.join(current_dir, "dashboard.py")
    print(f"\n🚀 Launching Streamlit Web Dashboard: {dashboard_path}")
    print("Press Ctrl+C in your terminal to stop the server when done.")
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", dashboard_path])
    except KeyboardInterrupt:
        print("\nDashboard stopped.")

def main():
    database.init_db()
    
    while True:
        print_menu()
        choice = input("Select an option (1-13): ").strip()
        
        if choice == "1":
            add_task_flow()
        elif choice == "2":
            view_tasks_flow()
        elif choice == "3":
            view_smart_priority_flow()
        elif choice == "4":
            view_reminders_flow()
        elif choice == "5":
            view_analytics_flow()
        elif choice == "6":
            view_ml_predictions_flow()
        elif choice == "7":
            view_schedule_optimizer_flow()
        elif choice == "8":
            update_status_flow()
        elif choice == "9":
            edit_task_flow()
        elif choice == "10":
            delete_task_flow()
        elif choice == "11":
            seed_sample_flow()
        elif choice == "12":
            launch_dashboard_flow()
        elif choice == "13":
            print("\nThank you for using Smart Reminder AI. Goodbye!")
            sys.exit(0)
        else:
            print("\nError: Invalid choice. Please enter a number between 1 and 13.")

if __name__ == "__main__":
    main()

