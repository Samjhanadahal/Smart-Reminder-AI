import streamlit as st
import datetime
import pandas as pd
import os
import sys

# Ensure src directory is in sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

import database
from models import Task
from smart_priority import calculate_smart_priority, rank_tasks
from reminders import get_reminder_alerts, check_workload_overload
from analytics import (
    calculate_productivity_metrics,
    plot_status_chart,
    plot_priority_bar_chart,
    plot_ontime_performance_chart
)
from ml_predictor import predict_task_completion, predict_hypothetical
from recommendations import generate_task_explanation, generate_daily_schedule_agenda

# --- Page Configuration ---
st.set_page_config(
    page_title="Smart Reminder AI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom Styling (Modern AI SaaS Dashboard • Dark Navy & Sky Blue) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    /* Core Resets & Fonts */
    html, body, [class*="css"], .stApp {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    
    .stApp {
        background-color: #0B1120;
        color: #F8FAFC;
    }

    /* Streamlit Container Layout */
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 2.5rem !important;
        max-width: 1300px;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #0D1526 !important;
        border-right: 1px solid #1E293B !important;
    }
    section[data-testid="stSidebar"] hr {
        border-color: #1E293B !important;
        margin: 14px 0 !important;
    }

    /* Header Container */
    .app-header {
        background: #111827;
        border: 1px solid #1E293B;
        border-radius: 14px;
        padding: 22px 28px;
        margin-bottom: 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 16px;
    }
    .header-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 3px 10px;
        background: rgba(56, 189, 248, 0.1);
        border: 1px solid rgba(56, 189, 248, 0.25);
        border-radius: 9999px;
        font-size: 0.74rem;
        font-weight: 600;
        color: #38BDF8;
        margin-bottom: 6px;
        letter-spacing: 0.02em;
    }
    .status-dot {
        width: 6px;
        height: 6px;
        background: #22C55E;
        border-radius: 50%;
        display: inline-block;
    }
    .header-title {
        font-size: 1.85rem;
        font-weight: 800;
        color: #F8FAFC;
        margin: 0 0 4px 0;
        letter-spacing: -0.02em;
    }
    .header-title-accent {
        color: #38BDF8;
    }
    .header-subtitle {
        color: #94A3B8;
        font-size: 0.92rem;
        font-weight: 400;
        margin: 0;
        line-height: 1.4;
    }
    .header-meta-box {
        display: flex;
        gap: 20px;
        align-items: center;
    }
    .header-stat {
        display: flex;
        flex-direction: column;
        align-items: flex-end;
    }
    .header-stat-label {
        font-size: 0.7rem;
        text-transform: uppercase;
        color: #64748B;
        font-weight: 600;
        letter-spacing: 0.05em;
    }
    .header-stat-value {
        font-size: 0.88rem;
        color: #38BDF8;
        font-weight: 600;
    }

    /* KPI Metric Cards */
    .metric-card {
        background: #111827;
        border: 1px solid #1E293B;
        border-radius: 12px;
        padding: 16px 18px;
        transition: transform 0.15s ease, border-color 0.15s ease;
        height: 100%;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        border-color: rgba(56, 189, 248, 0.35);
    }
    .metric-label {
        font-size: 0.74rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #94A3B8;
        margin-bottom: 6px;
    }
    .metric-value {
        font-size: 1.85rem;
        font-weight: 800;
        line-height: 1.15;
        color: #F8FAFC;
    }
    .metric-sub {
        font-size: 0.78rem;
        color: #64748B;
        margin-top: 6px;
    }

    /* Alert & Warning Banner */
    .alert-banner {
        background: #111827;
        border: 1px solid #1E293B;
        border-left: 3px solid #38BDF8;
        border-radius: 10px;
        padding: 12px 18px;
        margin-bottom: 16px;
        font-size: 0.88rem;
        color: #F1F5F9;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .alert-banner.warning {
        border-left-color: #F59E0B;
    }
    .alert-banner.danger {
        border-left-color: #EF4444;
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #0E1626 !important;
        border-radius: 10px !important;
        padding: 4px !important;
        border: 1px solid #1E293B !important;
        gap: 4px !important;
        margin-bottom: 18px !important;
    }
    .stTabs [data-baseweb="tab"] {
        color: #94A3B8 !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        padding: 8px 16px !important;
        border-radius: 8px !important;
        border: none !important;
        background: transparent !important;
        transition: all 0.15s ease !important;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: #F8FAFC !important;
        background: rgba(56, 189, 248, 0.06) !important;
    }
    .stTabs [aria-selected="true"] {
        color: #38BDF8 !important;
        background: #172033 !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.25) !important;
        font-weight: 700 !important;
    }
    .stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] {
        display: none !important;
    }

    /* Input Fields & Dropdowns */
    div[data-baseweb="input"] input, 
    div[data-baseweb="textarea"] textarea,
    div[data-baseweb="select"] > div {
        background-color: #111827 !important;
        color: #F8FAFC !important;
        border: 1px solid #1E293B !important;
        border-radius: 8px !important;
        font-size: 0.88rem !important;
    }
    div[data-baseweb="input"]:focus-within, 
    div[data-baseweb="select"]:focus-within {
        border-color: #38BDF8 !important;
        box-shadow: 0 0 0 1px #38BDF8 !important;
    }
    .stTextInput label, .stSelectbox label, .stDateInput label, .stNumberInput label, .stSlider label {
        color: #94A3B8 !important;
        font-size: 0.75rem !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.04em !important;
        margin-bottom: 4px !important;
    }

    /* Buttons */
    div.stButton > button[kind="primary"], 
    div.stButton > button[data-testid="baseButton-primary"] {
        background-color: #38BDF8 !important;
        color: #0B1120 !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 8px !important;
        transition: all 0.15s ease !important;
    }
    div.stButton > button[kind="primary"]:hover {
        background-color: #7DD3FC !important;
        box-shadow: 0 4px 12px rgba(56, 189, 248, 0.25) !important;
    }
    div.stButton > button[kind="secondary"], 
    div.stButton > button[data-testid="baseButton-secondary"] {
        background-color: #172033 !important;
        color: #F1F5F9 !important;
        border: 1px solid #1E293B !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.15s ease !important;
    }
    div.stButton > button[kind="secondary"]:hover {
        border-color: #38BDF8 !important;
        color: #38BDF8 !important;
        background-color: #1E293B !important;
    }

    /* Task Card Design (Consistent dark surface, subtle status indicator) */
    .task-card {
        background: #111827;
        border: 1px solid #1E293B;
        border-left: 3px solid #475569;
        border-radius: 10px;
        padding: 14px 18px;
        margin-bottom: 10px;
        transition: all 0.15s ease;
    }
    .task-card:hover {
        border-color: #334155;
        transform: translateY(-1px);
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.25);
    }
    .task-card.status-completed {
        border-left-color: #22C55E;
        opacity: 0.85;
    }
    .task-card.status-inprogress {
        border-left-color: #38BDF8;
    }
    .task-card.status-pending {
        border-left-color: #475569;
    }
    .task-card.status-overdue {
        border-left-color: #EF4444;
    }

    .task-header-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 12px;
        margin-bottom: 6px;
        flex-wrap: wrap;
    }
    .task-title-group {
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .task-id-badge {
        font-size: 0.8rem;
        font-weight: 700;
        color: #64748B;
    }
    .task-title-text {
        font-size: 1.05rem;
        font-weight: 700;
        color: #F8FAFC;
        letter-spacing: -0.01em;
    }
    .task-title-text.completed {
        text-decoration: line-through;
        color: #94A3B8;
    }
    .task-badges-row {
        display: flex;
        align-items: center;
        gap: 6px;
        flex-wrap: wrap;
    }

    .task-desc-text {
        font-size: 0.88rem;
        color: #94A3B8;
        line-height: 1.45;
        margin-bottom: 10px;
    }

    .task-footer-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 0.8rem;
        color: #64748B;
        border-top: 1px solid rgba(255, 255, 255, 0.04);
        padding-top: 8px;
        flex-wrap: wrap;
        gap: 8px;
    }
    .task-meta-left {
        display: flex;
        align-items: center;
        gap: 14px;
        flex-wrap: wrap;
    }
    .task-meta-item {
        display: inline-flex;
        align-items: center;
        gap: 4px;
    }
    .task-explanation-text {
        color: #94A3B8;
        font-size: 0.8rem;
    }

    /* Small, Restrained SaaS Badges */
    .badge {
        display: inline-flex;
        align-items: center;
        padding: 2px 8px;
        border-radius: 6px;
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.02em;
        line-height: 1.3;
    }
    .badge-status-completed {
        background: rgba(34, 197, 94, 0.12);
        color: #22C55E;
        border: 1px solid rgba(34, 197, 94, 0.25);
    }
    .badge-status-inprogress {
        background: rgba(56, 189, 248, 0.12);
        color: #38BDF8;
        border: 1px solid rgba(56, 189, 248, 0.25);
    }
    .badge-status-pending {
        background: rgba(100, 116, 139, 0.15);
        color: #94A3B8;
        border: 1px solid rgba(100, 116, 139, 0.25);
    }
    .badge-priority-high {
        background: rgba(245, 158, 11, 0.12);
        color: #F59E0B;
        border: 1px solid rgba(245, 158, 11, 0.25);
    }
    .badge-priority-medium {
        background: rgba(56, 189, 248, 0.08);
        color: #38BDF8;
        border: 1px solid rgba(56, 189, 248, 0.18);
    }
    .badge-priority-low {
        background: rgba(100, 116, 139, 0.1);
        color: #94A3B8;
        border: 1px solid rgba(100, 116, 139, 0.2);
    }
    .badge-ai {
        background: #172033;
        color: #38BDF8;
        border: 1px solid rgba(56, 189, 248, 0.25);
    }
    .badge-overdue {
        background: rgba(239, 68, 68, 0.15);
        color: #EF4444;
        border: 1px solid rgba(239, 68, 68, 0.35);
        font-weight: 700;
    }
    .badge-today {
        background: rgba(245, 158, 11, 0.15);
        color: #F59E0B;
        border: 1px solid rgba(245, 158, 11, 0.35);
        font-weight: 700;
    }
    .badge-deadline {
        background: #172033;
        color: #94A3B8;
        border: 1px solid #1E293B;
    }

    /* Schedule Items */
    .schedule-item {
        background: #111827;
        border: 1px solid #1E293B;
        border-left: 3px solid #38BDF8;
        border-radius: 10px;
        padding: 14px 18px;
        margin-bottom: 10px;
    }
    .schedule-time {
        font-size: 0.85rem;
        font-weight: 700;
        color: #38BDF8;
    }

    /* Sidebar Brand Card */
    .sidebar-brand {
        background: #111827;
        border: 1px solid #1E293B;
        border-radius: 10px;
        padding: 14px 16px;
        margin-bottom: 16px;
    }
    .brand-name {
        font-size: 1.1rem;
        font-weight: 800;
        color: #F8FAFC;
        margin: 0;
    }
    .brand-accent {
        color: #38BDF8;
    }
    .brand-desc {
        font-size: 0.78rem;
        color: #94A3B8;
        margin: 3px 0 0 0;
    }

    /* Action button column container */
    .action-btn-row {
        display: flex;
        gap: 6px;
        align-items: center;
        justify-content: flex-end;
    }
</style>
""", unsafe_allow_html=True)

# --- Initialize DB ---
DB_PATH = "data/tasks.db"
database.init_db(DB_PATH)

def load_all_tasks():
    return database.get_all_tasks(DB_PATH)

# --- Header Section (Clean, Modern AI SaaS Style) ---
tasks = load_all_tasks()
today = datetime.date.today()

active_count = len([t for t in tasks if t.status != "Completed"])
st.markdown(f"""
<div class="app-header">
    <div>
        <div class="header-badge">
            <span class="status-dot"></span>
            <span>AI Productivity Engine</span>
        </div>
        <div class="header-title">Smart Reminder <span class="header-title-accent">AI</span></div>
        <div class="header-subtitle">Intelligent priority scoring, completion risk prediction, and automated schedule optimization.</div>
    </div>
    <div class="header-meta-box">
        <div class="header-stat">
            <span class="header-stat-label">Active Workload</span>
            <span class="header-stat-value">{active_count} Active Tasks</span>
        </div>
        <div class="header-stat">
            <span class="header-stat-label">System Status</span>
            <span class="header-stat-value">Operational</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Check for initial empty DB
if not tasks:
    st.info("👋 Welcome! Your task database is currently empty. Click the button below to load realistic sample tasks and explore the AI features immediately.")
    if st.button("🚀 Load Realistic Sample Tasks", type="primary"):
        database.seed_sample_tasks(DB_PATH, clear_existing=True)
        st.success("Sample tasks loaded successfully!")
        st.rerun()

# --- Proactive Alerts & Overload Warning Banner ---
if tasks:
    alerts = get_reminder_alerts(tasks, today)
    overload = check_workload_overload(tasks, max_daily_hours=8.0, reference_date=today)
    
    alert_parts = []
    has_overdue = alerts["overdue"].count > 0
    
    if has_overdue:
        alert_parts.append(f"<span style='color: #EF4444; font-weight: 700;'>{alerts['overdue'].count} Overdue Task(s)</span> requiring urgent attention")
    if alerts["due_today"].count > 0:
        alert_parts.append(f"<span style='color: #F59E0B; font-weight: 700;'>{alerts['due_today'].count} Due Today</span>")
    if alerts["due_soon"].count > 0:
        alert_parts.append(f"<span style='color: #38BDF8;'>{alerts['due_soon'].count} Due in 48h</span>")

    if alert_parts:
        banner_class = "danger" if has_overdue else "warning"
        icon = "⚠️" if has_overdue else "⏱️"
        alert_text = " • ".join(alert_parts)
        st.markdown(f"""
        <div class="alert-banner {banner_class}">
            <span>{icon}</span>
            <span>{alert_text}</span>
        </div>
        """, unsafe_allow_html=True)
    
    if overload["is_overloaded"]:
        st.error(overload["message"])

# --- Overview KPI Metric Cards ---
metrics = calculate_productivity_metrics(tasks)

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Total Tasks</div>
        <div class="metric-value">{metrics['total_tasks']}</div>
        <div class="metric-sub">{metrics['pending_count']} pending • {metrics['in_progress_count']} in progress</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Completed</div>
        <div class="metric-value" style="color: #22C55E;">{metrics['completed_count']}</div>
        <div class="metric-sub">{metrics['completion_rate']}% completed</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">On-Time Delivery</div>
        <div class="metric-value" style="color: #38BDF8;">{metrics['on_time_rate']}%</div>
        <div class="metric-sub">{metrics['on_time_count']} on-time historical</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Workload Remaining</div>
        <div class="metric-value" style="color: #F8FAFC;">{metrics['pending_hours']}<span style="color: #38BDF8; font-size: 1.2rem;">h</span></div>
        <div class="metric-sub">avg {metrics['avg_task_hours']}h per task</div>
    </div>
    """, unsafe_allow_html=True)

with col5:
    overdue_val = metrics['overdue_count']
    overdue_color = "#EF4444" if overdue_val > 0 else "#94A3B8"
    overdue_sub = "Requires immediate focus" if overdue_val > 0 else "All tasks on schedule"
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Overdue Tasks</div>
        <div class="metric-value" style="color: {overdue_color};">{overdue_val}</div>
        <div class="metric-sub">{overdue_sub}</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

# --- Main App Navigation Tabs ---
tab_tasks, tab_add, tab_ai, tab_analytics = st.tabs([
    "📋 Smart Task Center",
    "➕ Add & AI Predict",
    "🧠 Explainable AI & Schedule",
    "📊 Productivity Analytics"
])

# ==========================================
# TAB 1: SMART TASK CENTER
# ==========================================
with tab_tasks:
    # Filter Toolbar
    search_col, fcol1, fcol2, fcol3 = st.columns([3, 2, 2, 2.5])
    with search_col:
        search_query = st.text_input("Search Tasks", placeholder="Search by title or keywords...").strip().lower()
    with fcol1:
        status_filter = st.selectbox("Status", ["All Active", "All (Including Completed)", "Pending", "In Progress", "Completed"])
    with fcol2:
        priority_filter = st.selectbox("Priority", ["All Priorities", "High", "Medium", "Low"])
    with fcol3:
        sort_by = st.selectbox("Sort By", [
            "Smart Priority (AI Ranked)",
            "Deadline (Earliest First)",
            "Effort (Estimated Hours Desc)",
            "ID (Creation Order)"
        ])

    # Filter tasks
    filtered_tasks = list(tasks)
    if search_query:
        filtered_tasks = [t for t in filtered_tasks if search_query in t.title.lower() or (t.description and search_query in t.description.lower())]

    if status_filter == "All Active":
        filtered_tasks = [t for t in filtered_tasks if t.status != "Completed"]
    elif status_filter in ["Pending", "In Progress", "Completed"]:
        filtered_tasks = [t for t in filtered_tasks if t.status == status_filter]
        
    if priority_filter != "All Priorities":
        filtered_tasks = [t for t in filtered_tasks if t.priority == priority_filter]

    # Sort tasks
    if sort_by == "Smart Priority (AI Ranked)":
        ranked_items = rank_tasks(filtered_tasks, reference_date=today, include_completed=True)
        filtered_tasks = [item[0] for item in ranked_items]
    elif sort_by == "Deadline (Earliest First)":
        filtered_tasks.sort(key=lambda t: t.deadline)
    elif sort_by == "Effort (Estimated Hours Desc)":
        filtered_tasks.sort(key=lambda t: -t.estimated_hours)
    elif sort_by == "ID (Creation Order)":
        filtered_tasks.sort(key=lambda t: t.id)

    if not filtered_tasks:
        st.info("No tasks match your selected filters.")
    else:
        for task in filtered_tasks:
            smart_meta = calculate_smart_priority(task, reference_date=today)
            ml_meta = predict_task_completion(task, reference_date=today)
            days_left = task.days_remaining(today)
            is_completed = task.status == "Completed"
            is_overdue = days_left < 0 and not is_completed
            
            # Subtle card status class (consistent dark surface, subtle left border)
            if is_completed:
                card_status_class = "status-completed"
            elif is_overdue:
                card_status_class = "status-overdue"
            elif task.status == "In Progress":
                card_status_class = "status-inprogress"
            else:
                card_status_class = "status-pending"

            # Status badge
            if is_completed:
                status_badge = '<span class="badge badge-status-completed">Completed</span>'
            elif task.status == "In Progress":
                status_badge = '<span class="badge badge-status-inprogress">In Progress</span>'
            else:
                status_badge = '<span class="badge badge-status-pending">Pending</span>'

            # Priority badge
            p_lower = task.priority.lower()
            priority_badge = f'<span class="badge badge-priority-{p_lower}">{task.priority} Priority</span>'

            # Deadline badge (red only when overdue, orange if today, neutral otherwise)
            if is_overdue:
                deadline_badge = f'<span class="badge badge-overdue">{-days_left}d Overdue</span>'
            elif days_left == 0 and not is_completed:
                deadline_badge = '<span class="badge badge-today">Due Today</span>'
            else:
                days_label = f"{days_left}d left" if days_left > 0 else "Due today"
                deadline_badge = f'<span class="badge badge-deadline">{task.deadline} ({days_label})</span>'

            # AI Score badge
            ai_score_badge = f'<span class="badge badge-ai">AI Score {smart_meta["score"]}</span>'

            # ML risk color and text
            prob_color = ml_meta["risk_color"]
            if ml_meta["risk_level"] == "High Risk":
                ml_display_color = "#EF4444"
            elif ml_meta["risk_level"] == "Medium Risk":
                ml_display_color = "#F59E0B"
            else:
                ml_display_color = "#38BDF8"

            desc_html = task.description if task.description else "<span style='color: #64748B;'>No description provided</span>"
            title_cls = "task-title-text completed" if is_completed else "task-title-text"

            with st.container():
                c_card, c_actions = st.columns([7.8, 2.2])
                with c_card:
                    st.markdown(f"""
                    <div class="task-card {card_status_class}">
                        <div class="task-header-row">
                            <div class="task-title-group">
                                <span class="task-id-badge">#{task.id}</span>
                                <span class="{title_cls}">{task.title}</span>
                            </div>
                            <div class="task-badges-row">
                                {status_badge}
                                {priority_badge}
                                {deadline_badge}
                                {ai_score_badge}
                            </div>
                        </div>
                        <div class="task-desc-text">
                            {desc_html}
                        </div>
                        <div class="task-footer-row">
                            <div class="task-meta-left">
                                <span class="task-meta-item">⏱ {task.estimated_hours}h effort</span>
                                <span class="task-meta-item" style="color: {ml_display_color};">
                                    ML Risk: {ml_meta['risk_level']} ({ml_meta['probability']}%)
                                </span>
                            </div>
                            <div class="task-explanation-text">
                                {smart_meta['explanation']}
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with c_actions:
                    # Clean quick action buttons
                    bcol1, bcol2 = st.columns(2)
                    with bcol1:
                        if not is_completed:
                            if st.button("✓ Done", key=f"done_{task.id}", help="Mark Completed", use_container_width=True):
                                database.update_task_status(task.id, "Completed", DB_PATH)
                                st.rerun()
                        else:
                            if st.button("↺ Reopen", key=f"reopen_{task.id}", help="Reopen task to Pending", use_container_width=True):
                                database.update_task_status(task.id, "Pending", DB_PATH)
                                st.rerun()
                    with bcol2:
                        if task.status == "Pending":
                            if st.button("▶ Start", key=f"start_{task.id}", help="Start Task", use_container_width=True):
                                database.update_task_status(task.id, "In Progress", DB_PATH)
                                st.rerun()
                        else:
                            edit_active = st.session_state.get(f"edit_{task.id}", False)
                            btn_label = "✕ Close" if edit_active else "✎ Edit"
                            if st.button(btn_label, key=f"edit_btn_{task.id}", help="Edit task details", use_container_width=True):
                                st.session_state[f"edit_{task.id}"] = not edit_active
                                st.rerun()

                    bcol3, bcol4 = st.columns(2)
                    with bcol3:
                        if task.status == "Pending":
                            edit_active = st.session_state.get(f"edit_{task.id}", False)
                            btn_label = "✕ Close" if edit_active else "✎ Edit"
                            if st.button(btn_label, key=f"edit_btn_{task.id}", help="Edit task details", use_container_width=True):
                                st.session_state[f"edit_{task.id}"] = not edit_active
                                st.rerun()
                    with bcol4:
                        if st.button("🗑 Del", key=f"del_{task.id}", help="Delete task", use_container_width=True):
                            database.delete_task(task.id, DB_PATH)
                            st.rerun()

            # Inline Edit Form
            if st.session_state.get(f"edit_{task.id}", False):
                with st.expander(f"Edit Task #{task.id}: {task.title}", expanded=True):
                    with st.form(f"edit_form_{task.id}"):
                        e_col1, e_col2 = st.columns(2)
                        with e_col1:
                            new_title = st.text_input("Task Title *", value=task.title)
                            new_desc = st.text_area("Description", value=task.description or "", height=80)
                        with e_col2:
                            new_deadline = st.date_input("Deadline *", value=task.deadline)
                            p_options = ["High", "Medium", "Low"]
                            p_idx = p_options.index(task.priority) if task.priority in p_options else 1
                            new_priority = st.selectbox("Priority *", p_options, index=p_idx)
                            new_hours = st.number_input("Estimated Hours *", min_value=0.25, max_value=80.0, value=float(task.estimated_hours), step=0.5)

                        save_col, cancel_col = st.columns(2)
                        with save_col:
                            if st.form_submit_button("Save Changes", type="primary", use_container_width=True):
                                if not new_title.strip():
                                    st.error("Error: Task title cannot be empty.")
                                else:
                                    database.update_task(
                                        task_id=task.id,
                                        title=new_title.strip(),
                                        description=new_desc.strip(),
                                        deadline=new_deadline.isoformat(),
                                        priority=new_priority,
                                        estimated_hours=new_hours,
                                        db_path=DB_PATH
                                    )
                                    st.session_state[f"edit_{task.id}"] = False
                                    st.success("Task updated successfully!")
                                    st.rerun()
                        with cancel_col:
                            if st.form_submit_button("Cancel", use_container_width=True):
                                st.session_state[f"edit_{task.id}"] = False
                                st.rerun()


# ==========================================
# TAB 2: ADD & AI PREDICT TASK
# ==========================================
with tab_add:
    st.subheader("Add Task with Real-Time AI Prediction")
    st.markdown("Enter task parameters below to receive an instant machine learning completion forecast before saving.")
    
    with st.form("add_task_form"):
        form_col1, form_col2 = st.columns(2)
        with form_col1:
            title_input = st.text_input("Task Title *", placeholder="e.g., Finalize project technical architecture")
            description_input = st.text_area("Description", placeholder="Add key context, dependencies, or scope...", height=100)
            
        with form_col2:
            deadline_input = st.date_input("Deadline *", min_value=today - datetime.timedelta(days=30), value=today + datetime.timedelta(days=2))
            priority_input = st.selectbox("Base Priority *", ["High", "Medium", "Low"], index=1)
            hours_input = st.number_input("Estimated Hours *", min_value=0.25, max_value=80.0, value=3.0, step=0.5)

        # Real-time AI simulation preview
        st.markdown("---")
        st.markdown("##### Real-Time AI Risk Forecast")
        
        pred = predict_hypothetical(
            estimated_hours=hours_input,
            deadline_str=deadline_input.isoformat(),
            priority=priority_input,
            reference_date=today
        )
        
        preview_col1, preview_col2, preview_col3 = st.columns(3)
        with preview_col1:
            st.metric("On-Time Probability", f"{pred['probability']}%")
        with preview_col2:
            st.metric("Predicted Risk", pred["risk_level"])
        with preview_col3:
            days_diff = (deadline_input - today).days
            st.metric("Timeline Headroom", f"{days_diff} day(s)")

        st.caption(f"💡 **AI Guidance**: {pred['explanation']}")

        submitted = st.form_submit_button("Add Task to Smart Reminder AI", type="primary", use_container_width=True)
        if submitted:
            if not title_input.strip():
                st.error("Error: Task title is required.")
            else:
                new_id = database.add_task(
                    title=title_input.strip(),
                    description=description_input.strip(),
                    deadline=deadline_input.isoformat(),
                    priority=priority_input,
                    estimated_hours=hours_input,
                    db_path=DB_PATH
                )
                st.success(f"Task '{title_input}' successfully added with ID #{new_id}!")
                st.rerun()

# ==========================================
# TAB 3: EXPLAINABLE AI & DAILY SCHEDULE
# ==========================================
with tab_ai:
    st.subheader("Explainable AI (XAI) & Schedule Optimizer")
    
    active_tasks = [t for t in tasks if t.status != "Completed"]
    if not active_tasks:
        st.info("No active tasks available to optimize.")
    else:
        st.markdown("##### Today's Optimized Focus Agenda")
        st.markdown("The Schedule Optimizer organizes active workload into focused blocks based on Smart Urgency and daily capacity.")
        
        capacity_hours = st.slider("Daily Work Capacity (Hours)", min_value=2.0, max_value=12.0, value=7.0, step=0.5)
        agenda = generate_daily_schedule_agenda(active_tasks, max_hours=capacity_hours, reference_date=today)
        
        st.markdown(f"**Agenda Summary:** {agenda['notes']}")
        
        for item in agenda["schedule"]:
            t = item["task"]
            with st.container():
                st.markdown(f"""
                <div class="schedule-item">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                        <span class="schedule-time">
                            ⏱ {item['time_slot']} • {item['block_name']} ({item['hours']}h)
                        </span>
                        <span class="badge badge-ai">Smart Score: {item['smart_score']}</span>
                    </div>
                    <div style="font-size: 1.05rem; font-weight: 700; color: #F8FAFC;">
                        #{t.id} {t.title}
                    </div>
                    <div style="color: #94A3B8; font-size: 0.85rem; margin-top: 4px;">
                        Deadline: {t.deadline} | Priority: {t.priority}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                if item["tips"]:
                    for tip in item["tips"]:
                        st.caption(f"💡 {tip}")

        # Export schedule to Markdown
        agenda_md_lines = [
            f"# Smart Reminder AI - Daily Work Agenda ({today.isoformat()})",
            f"**Available Capacity:** {capacity_hours}h | **Allocated Effort:** {agenda['total_allocated_hours']}h",
            f"**Summary:** {agenda['notes']}",
            "",
            "## Scheduled Work Blocks",
        ]
        for it in agenda["schedule"]:
            ts = it["task"]
            agenda_md_lines.append(f"### [{it['time_slot']}] {it['block_name']} ({it['hours']}h)")
            agenda_md_lines.append(f"- **Task #{ts.id}:** {ts.title}")
            agenda_md_lines.append(f"- **Smart Priority:** {it['smart_score']} ({it['smart_band']}) | **Deadline:** {ts.deadline}")
            if it["tips"]:
                for tp in it["tips"]:
                    agenda_md_lines.append(f"  - {tp}")
            agenda_md_lines.append("")
        agenda_md_content = "\n".join(agenda_md_lines)
        
        st.download_button(
            label="📥 Export Today's Agenda (.md)",
            data=agenda_md_content,
            file_name=f"work_agenda_{today.isoformat()}.md",
            mime="text/markdown",
            use_container_width=False
        )

        st.markdown("---")
        st.markdown("##### Priority Drivers & Reasoning")
        st.markdown("Inspect why the algorithm ranks critical tasks at the top of the queue.")
        
        ranked_top = rank_tasks(active_tasks, reference_date=today, include_completed=False)[:5]
        for task, meta in ranked_top:
            exp = generate_task_explanation(task, reference_date=today)
            with st.expander(f"Task #{task.id}: {task.title} — AI Score {meta['score']} ({meta['band']})"):
                ecol1, ecol2 = st.columns(2)
                with ecol1:
                    st.write("**Key Urgency Drivers:**")
                    for d in exp["primary_drivers"]:
                        st.markdown(f"• {d}")
                    st.write(f"**ML On-Time Probability:** `{exp['on_time_probability']}%` ({exp['risk_level']})")
                with ecol2:
                    st.write("**Actionable AI Recommendations:**")
                    if exp["actionable_tips"]:
                        for tip in exp["actionable_tips"]:
                            st.info(tip)
                    else:
                        st.write("Maintain current steady pace.")

# ==========================================
# TAB 4: PRODUCTIVITY ANALYTICS
# ==========================================
with tab_analytics:
    st.subheader("Productivity & Performance Analytics")
    
    if not tasks:
        st.info("No task data available for analytics yet.")
    else:
        acol1, acol2 = st.columns(2)
        with acol1:
            st.markdown("##### Status Breakdown")
            fig_status = plot_status_chart(tasks)
            st.pyplot(fig_status, clear_figure=True)
            
        with acol2:
            st.markdown("##### Workload by Priority")
            fig_priority = plot_priority_bar_chart(tasks)
            st.pyplot(fig_priority, clear_figure=True)

        st.markdown("---")
        st.markdown("##### Historical Delivery Reliability")
        fig_ontime = plot_ontime_performance_chart(tasks)
        st.pyplot(fig_ontime, clear_figure=True)

        st.markdown("---")
        st.markdown("##### All Tasks Dataset")
        df_tasks = database.get_tasks_as_dataframe(DB_PATH)
        csv_data = df_tasks.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Dataset (.csv)",
            data=csv_data,
            file_name=f"smart_reminder_tasks_{today.isoformat()}.csv",
            mime="text/csv",
            use_container_width=False
        )
        st.dataframe(df_tasks, use_container_width=True)


# --- Sidebar Controls ---
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
            <span style="font-size: 1.2rem; color: #38BDF8;">⚡</span>
            <span class="brand-name">Smart Reminder <span class="brand-accent">AI</span></span>
        </div>
        <div class="brand-desc">Productivity & Schedule Intelligence</div>
        <div style="margin-top: 10px; display: flex; align-items: center; gap: 6px;">
            <span class="status-dot"></span>
            <span style="font-size: 0.72rem; color: #38BDF8; font-weight: 600;">System Online & Synced</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("##### Quick Actions")
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.rerun()

    if st.button("🌱 Reload Sample Tasks", use_container_width=True):
        database.seed_sample_tasks(DB_PATH, clear_existing=True)
        st.success("Sample tasks reloaded!")
        st.rerun()

    st.markdown("---")
    st.markdown("##### Architecture")
    st.markdown("""
    - **Language:** Python 3.11
    - **Storage:** SQLite Engine
    - **Analytics:** Pandas & Matplotlib
    - **ML Model:** Random Forest Classifier
    - **UI Theme:** Dark Navy & Sky Blue SaaS
    """)
    st.caption("Smart Reminder AI • Pair Programming")
