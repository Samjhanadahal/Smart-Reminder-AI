import datetime

class Task:
    """
    Represents a single Task in the Smart Reminder AI application.
    Uses basic Object-Oriented programming concepts to bundle task data and behavior.
    """
    def __init__(self, task_id: int, title: str, description: str, deadline_str: str, priority: str, estimated_hours: float):
        self.id = task_id
        self.title = title
        self.description = description
        
        # Parse the deadline string (YYYY-MM-DD) into a datetime.date object
        # This will be very useful in Phase 3 (Smart Priority) for date mathematics
        try:
            self.deadline = datetime.datetime.strptime(deadline_str, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError("Deadline must be in YYYY-MM-DD format.")
            
        self.priority = priority.capitalize()  # E.g., Low, Medium, High
        if self.priority not in ["Low", "Medium", "High"]:
            raise ValueError("Priority must be one of: Low, Medium, High")
            
        self.estimated_hours = float(estimated_hours)
        if self.estimated_hours < 0:
            raise ValueError("Estimated completion hours cannot be negative.")
            
        self.status = "Pending"  # Initially, every task is Pending
        self.created_at = datetime.date.today()
        self.completed_at = None  # None until the task is marked as Completed

    def update_status(self, new_status: str):
        """Updates the status and sets/clears completion date accordingly."""
        cleaned_status = new_status.title()
        if cleaned_status not in ["Pending", "In Progress", "Completed"]:
            raise ValueError("Status must be one of: Pending, In Progress, Completed")
            
        self.status = cleaned_status
        if cleaned_status == "Completed":
            self.completed_at = datetime.date.today()
        else:
            self.completed_at = None

    def __str__(self):
        """Returns a user-friendly string representation of the task."""
        completed_info = f" (Completed on: {self.completed_at})" if self.status == "Completed" else ""
        return (
            f"ID: {self.id} | {self.title}\n"
            f"  Description: {self.description}\n"
            f"  Deadline: {self.deadline} | Priority: {self.priority} | Est: {self.estimated_hours}h\n"
            f"  Status: [{self.status}]{completed_info}"
        )
