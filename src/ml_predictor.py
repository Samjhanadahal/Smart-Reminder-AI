import datetime
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

try:
    from models import Task
except ImportError:
    from src.models import Task

_GLOBAL_MODEL_PIPELINE = None

def _generate_synthetic_training_data(n_samples: int = 600, random_state: int = 42) -> tuple[np.ndarray, np.ndarray]:
    """
    Generates realistic historical productivity samples to train the baseline ML model.
    Features:
    [estimated_hours, days_until_deadline, priority_weight, urgency_ratio, is_in_progress]
    Target:
    1 = Completed On-Time, 0 = Delayed/Overdue
    """
    rng = np.random.RandomState(random_state)
    
    # 1. Estimated hours (0.5 to 24 hours)
    est_hours = rng.exponential(scale=3.5, size=n_samples) + 0.5
    est_hours = np.clip(est_hours, 0.5, 25.0)

    # 2. Days until deadline (-3 to 20 days)
    days_left = rng.normal(loc=4.5, scale=4.0, size=n_samples)
    days_left = np.clip(days_left, -3.0, 25.0)

    # 3. Priority weight (1.0 = Low, 2.0 = Medium, 3.0 = High)
    priority_weights = rng.choice([1.0, 2.0, 3.0], size=n_samples, p=[0.25, 0.45, 0.30])

    # 4. Status: In Progress (1) vs Pending (0)
    is_in_progress = rng.choice([0.0, 1.0], size=n_samples, p=[0.6, 0.4])

    # 5. Urgency ratio: estimated_hours / available working hours
    # Assume 6 effective hours per day.
    available_hours = np.maximum(days_left * 6.0, 0.5)
    urgency_ratio = est_hours / available_hours

    X = np.column_stack([est_hours, days_left, priority_weights, urgency_ratio, is_in_progress])

    # Calculate realistic ground truth probability:
    # Overdue tasks have almost 0 chance of being on time.
    # Urgency ratio > 1.0 (requires more than 100% capacity) heavily degrades on-time odds.
    # High priority gives slight execution boost.
    # In-progress provides a head-start boost.
    z = (
        1.6 
        + 0.55 * days_left 
        - 0.18 * est_hours 
        + 0.35 * (priority_weights - 2.0) 
        + 0.60 * is_in_progress
        - 1.40 * urgency_ratio
    )
    # Sigmoid function for probability
    probs = 1.0 / (1.0 + np.exp(-np.clip(z, -8.0, 8.0)))
    # Overdue cannot be completed on time:
    probs[days_left < 0] = 0.05
    
    y = (rng.rand(n_samples) < probs).astype(int)

    return X, y

def train_task_completion_model():
    """
    Trains a Random Forest classifier pipeline on historical task patterns.
    """
    X, y = _generate_synthetic_training_data()
    
    pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('classifier', RandomForestClassifier(n_estimators=120, max_depth=6, random_state=42))
    ])
    pipeline.fit(X, y)
    return pipeline

def get_ml_model():
    """Returns singleton cached ML pipeline."""
    global _GLOBAL_MODEL_PIPELINE
    if _GLOBAL_MODEL_PIPELINE is None:
        _GLOBAL_MODEL_PIPELINE = train_task_completion_model()
    return _GLOBAL_MODEL_PIPELINE

def extract_features_from_values(estimated_hours: float, days_remaining: int, priority: str, status: str = "Pending") -> np.ndarray:
    """Extracts the feature vector matching the model schema."""
    p_map = {"High": 3.0, "Medium": 2.0, "Low": 1.0}
    p_weight = p_map.get(priority.capitalize(), 2.0)
    in_prog = 1.0 if status.lower() == "in progress" else 0.0
    
    days_float = float(days_remaining)
    available_hours = max(days_float * 6.0, 0.5)
    urgency_ratio = float(estimated_hours) / available_hours

    return np.array([[float(estimated_hours), days_float, p_weight, urgency_ratio, in_prog]])

def predict_task_completion(task: Task, reference_date: datetime.date = None) -> dict:
    """
    Predicts the likelihood of an existing task being delivered on-time.
    Returns probability %, risk band, and explanatory insight.
    """
    if reference_date is None:
        reference_date = datetime.date.today()

    if task.status == "Completed":
        was_on_time = not task.completed_at or task.completed_at <= task.deadline
        return {
            "probability": 100.0 if was_on_time else 0.0,
            "risk_level": "Delivered On-Time" if was_on_time else "Delivered Late",
            "risk_color": "#10b981" if was_on_time else "#ef4444",
            "explanation": f"Task already marked Completed on {task.completed_at}."
        }

    days_left = task.days_remaining(reference_date)

    if days_left < 0:
        return {
            "probability": 5.0,
            "risk_level": "High Risk (Overdue)",
            "risk_color": "#ef4444",
            "explanation": f"Task deadline passed {-days_left} day(s) ago. Immediate rescheduling required."
        }

    model = get_ml_model()
    features = extract_features_from_values(task.estimated_hours, days_left, task.priority, task.status)
    proba = model.predict_proba(features)[0][1] * 100.0
    proba = round(proba, 1)

    if proba >= 75.0:
        risk_level = "Low Risk"
        risk_color = "#10b981"  # Emerald
        explanation = f"Comfortable timeline. {task.estimated_hours}h estimated with {days_left}d remaining."
    elif proba >= 45.0:
        risk_level = "Moderate Risk"
        risk_color = "#f59e0b"  # Amber
        explanation = f"Tight timeline. Requires prompt attention within the next 24-48 hours."
    else:
        risk_level = "High Risk"
        risk_color = "#ef4444"  # Red
        explanation = f"High probability of missing deadline. Consider reducing scope or extending deadline."

    return {
        "probability": proba,
        "risk_level": risk_level,
        "risk_color": risk_color,
        "explanation": explanation
    }

def predict_hypothetical(estimated_hours: float, deadline_str: str, priority: str, reference_date: datetime.date = None) -> dict:
    """Predicts completion probability for user inputs before task submission."""
    if reference_date is None:
        reference_date = datetime.date.today()
    try:
        deadline_date = datetime.datetime.strptime(deadline_str, "%Y-%m-%d").date()
    except Exception:
        return {"probability": 50.0, "risk_level": "Unknown", "risk_color": "#94a3b8", "explanation": "Invalid date format."}
    
    days_left = (deadline_date - reference_date).days
    model = get_ml_model()
    features = extract_features_from_values(estimated_hours, days_left, priority, "Pending")
    proba = model.predict_proba(features)[0][1] * 100.0
    proba = round(proba, 1)

    if days_left < 0:
        return {"probability": 5.0, "risk_level": "High Risk (Past Date)", "risk_color": "#ef4444", "explanation": "Target date is already in the past."}
    if proba >= 75.0:
        return {"probability": proba, "risk_level": "Low Risk", "risk_color": "#10b981", "explanation": "Realistic estimate and deadline."}
    elif proba >= 45.0:
        return {"probability": proba, "risk_level": "Moderate Risk", "risk_color": "#f59e0b", "explanation": "Challenging schedule. Needs dedicated focus."}
    else:
        return {"probability": proba, "risk_level": "High Risk", "risk_color": "#ef4444", "explanation": "High risk of delay based on workload ratio."}
