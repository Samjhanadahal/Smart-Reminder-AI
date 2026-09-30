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

# --- Custom Styling (Sleek Modern Glassmorphism & Dark Palette) ---
st.markdown("""
<style>
    /* Global Styles & Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    .stApp {
        background-color: #0b0f19;
        color: #f1f5f9;
    }
    
    /* Hero Header */
    .hero-container {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(15, 23, 42, 0.95) 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 24px 32px;
        margin-bottom: 24px;
        box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
    }
    .hero-title {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #38bdf8, #818cf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 6px;
    }
    .hero-subtitle {
        color: #94a3b8;
        font-size: 1.05rem;
        font-weight: 500;
    }
    
    /* Metric Cards */
    .metric-card {
        background: rgba(30, 41, 59, 0.6);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 14px;
        padding: 18px 20px;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        border-color: rgba(56, 189, 248, 0.3);
    }
    .metric-label {
        font-size: 0.82rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #94a3b8;
        margin-bottom: 6px;
    }
    .metric-value {
        font-size: 1.85rem;
        font-weight: 800;
        color: #f8fafc;
    }
    .metric-sub {
        font-size: 0.8rem;
        color: #64748b;
        margin-top: 4px;
    }
    
    /* Task Card */
    .task-card {
        background: rgba(30, 41, 59, 0.7);
        border-left: 4px solid #3b82f6;
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 12px;
        border-top: 1px solid rgba(255, 255, 255, 0.05);
        border-right: 1px solid rgba(255, 255, 255, 0.05);
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    }
    .task-card.critical { border-left-color: #ef4444; }
    .task-card.high { border-left-color: #f59e0b; }
    .task-card.medium { border-left-color: #3b82f6; }
    .task-card.low { border-left-color: #10b981; }
    .task-card.completed { border-left-color: #64748b; opacity: 0.75; }

    /* Badge Pills */
    .badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.02em;
        margin-right: 6px;
    }
    .badge-critical { background: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.3); }
    .badge-high { background: rgba(245, 158, 11, 0.2); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.3); }
    .badge-medium { background: rgba(59, 130, 246, 0.2); color: #60a5fa; border: 1px solid rgba(59, 130, 246, 0.3); }
    .badge-low { background: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); }
    
    .badge-overdue { background: rgba(239, 68, 68, 0.25); color: #fca5a5; font-weight: 800; border: 1px solid #ef4444; }
    .badge-today { background: rgba(245, 158, 11, 0.25); color: #fde047; font-weight: 800; border: 1px solid #f59e0b; }
    
    /* Schedule Block */
    .schedule-item {
        background: rgba(15, 23, 42, 0.85);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 10px;
        padding: 14px 18px;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- Initialize DB ---
DB_PATH = "data/tasks.db"
database.init_db(DB_PATH)

def load_all_tasks():
    return database.get_all_tasks(DB_PATH)

# --- Top Banner & Header ---
st.markdown("""
<div class="hero-container">
    <div class="hero-title">⚡ Smart Reminder AI</div>
    <div class="hero-subtitle">Intelligent Priority Scoring • Scikit-learn Risk Prediction • Daily Schedule Optimizer</div>
</div>
""", unsafe_allow_html=True)

tasks = load_all_tasks()
today = datetime.date.today()

# Check for initial empty DB and offer quick sample loading
if not tasks:
    st.info("👋 Welcome! Your task database is currently empty. Click the button below to load realistic sample tasks and explore the AI features immediately.")
    if st.button("🚀 Load Realistic Sample Tasks", type="primary"):
        database.seed_sample_tasks(DB_PATH, clear_existing=True)
        st.success("Sample tasks loaded successfully!")
        st.rerun()

# --- Reminders & Urgent Alert Banner ---
if tasks:
    alerts = get_reminder_alerts(tasks, today)
    overload = check_workload_overload(tasks, max_daily_hours=8.0, reference_date=today)
    
    alert_messages = []
    if alerts["overdue"].count > 0:
        alert_messages.append(f"🚨 **{alerts['overdue'].count} Overdue Task(s)** needing urgent triage")
    if alerts["due_today"].count > 0:
        alert_messages.append(f"⚡ **{alerts['due_today'].count} Task(s) Due Today**")
    if alerts["due_soon"].count > 0:
        alert_messages.append(f"⏰ **{alerts['due_soon'].count} Task(s) Due in 48 Hours**")

    if alert_messages:
        with st.container():
            st.warning(" | ".join(alert_messages))
    
    if overload["is_overloaded"]:
        st.error(overload["message"])

# --- Overview KPI Metric Row ---
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
        <div class="metric-value" style="color: #10b981;">{metrics['completed_count']}</div>
        <div class="metric-sub">{metrics['completion_rate']}% completion rate</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">On-Time Delivery</div>
        <div class="metric-value" style="color: #38bdf8;">{metrics['on_time_rate']}%</div>
        <div class="metric-sub">{metrics['on_time_count']} on-time historical</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Workload Remaining</div>
        <div class="metric-value" style="color: #f59e0b;">{metrics['pending_hours']}h</div>
        <div class="metric-sub">avg {metrics['avg_task_hours']}h per task</div>
    </div>
    """, unsafe_allow_html=True)

with col5:
    overdue_val = metrics['overdue_count']
    overdue_color = "#ef4444" if overdue_val > 0 else "#10b981"
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Overdue Tasks</div>
        <div class="metric-value" style="color: {overdue_color};">{overdue_val}</div>
        <div class="metric-sub">{'Requires immediate focus' if overdue_val > 0 else 'All on track'}</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

# --- Main App Navigation Tabs ---
tab_tasks, tab_add, tab_ai, tab_analytics = st.tabs([
    "📋 Smart Task Center",
    "➕ Add & AI Predict",
    "🧠 Explainable AI & Daily Schedule",
    "📊 Productivity Analytics"
])

# ==========================================
# TAB 1: SMART TASK CENTER
# ==========================================
with tab_tasks:
    st.subheader("Task Management & Smart Prioritization")
    
    # Filter and Sort Controls
    search_col, fcol1, fcol2, fcol3 = st.columns([3, 2, 2, 2])
    with search_col:
        search_query = st.text_input("🔍 Search Tasks", placeholder="Filter by title or keywords...").strip().lower()
    with fcol1:
        status_filter = st.selectbox("Filter Status", ["All Active", "All (Including Completed)", "Pending", "In Progress", "Completed"])
    with fcol2:
        priority_filter = st.selectbox("Filter Priority", ["All Priorities", "High", "Medium", "Low"])
    with fcol3:
        sort_by = st.selectbox("Sort Order", [
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
            
            # Badge styles
            band_class = f"badge-{smart_meta['band'].lower()}" if smart_meta['band'] in ["Critical", "High", "Medium", "Low"] else "badge-low"
            card_class = f"task-card {smart_meta['band'].lower()}" if task.status != "Completed" else "task-card completed"

            # Deadline badge text
            if days_left < 0 and task.status != "Completed":
                deadline_badge = f'<span class="badge badge-overdue">🚨 {-days_left}d OVERDUE</span>'
            elif days_left == 0 and task.status != "Completed":
                deadline_badge = '<span class="badge badge-today">⚡ DUE TODAY</span>'
            else:
                deadline_badge = f'<span class="badge" style="background: rgba(255,255,255,0.1); color: #cbd5e1;">📅 {task.deadline} ({days_left}d left)</span>'

            # ML badge
            prob_color = ml_meta["risk_color"]
            ml_badge = f'<span class="badge" style="background: {prob_color}22; color: {prob_color}; border: 1px solid {prob_color}55;">🤖 ML: {ml_meta["risk_level"]} ({ml_meta["probability"]}%)</span>'

            with st.container():
                c_card, c_actions = st.columns([7, 3])
                with c_card:
                    st.markdown(f"""
                    <div class="{card_class}">
                        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px;">
                            <div style="font-size: 1.15rem; font-weight: 700; color: #f8fafc;">
                                #{task.id} • {task.title}
                            </div>
                            <div>
                                <span class="badge {band_class}">AI Score: {smart_meta['score']} ({smart_meta['band']})</span>
                                {deadline_badge}
                                {ml_badge}
                            </div>
                        </div>
                        <div style="color: #94a3b8; font-size: 0.95rem; margin-bottom: 8px;">
                            {task.description if task.description else '<em>No description provided.</em>'}
                        </div>
                        <div style="font-size: 0.85rem; color: #64748b;">
                            <strong>Priority:</strong> {task.priority} | 
                            <strong>Effort:</strong> {task.estimated_hours}h | 
                            <strong>Status:</strong> <span style="color: #e2e8f0; font-weight: 600;">[{task.status}]</span> |
                            <span style="color: #94a3b8;">{smart_meta['explanation']}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with c_actions:
                    # Quick action buttons
                    bcol1, bcol2, bcol3, bcol4 = st.columns(4)
                    with bcol1:
                        if task.status != "Completed":
                            if st.button("✅ Done", key=f"done_{task.id}", help="Mark task Completed"):
                                database.update_task_status(task.id, "Completed", DB_PATH)
                                st.rerun()
                        else:
                            if st.button("↩️ Reopen", key=f"reopen_{task.id}", help="Reopen task to Pending"):
                                database.update_task_status(task.id, "Pending", DB_PATH)
                                st.rerun()
                    with bcol2:
                        if task.status == "Pending":
                            if st.button("▶️ Start", key=f"start_{task.id}", help="Mark In Progress"):
                                database.update_task_status(task.id, "In Progress", DB_PATH)
                                st.rerun()
                    with bcol3:
                        edit_active = st.session_state.get(f"edit_{task.id}", False)
                        btn_label = "✖️ Close" if edit_active else "✏️ Edit"
                        if st.button(btn_label, key=f"edit_btn_{task.id}", help="Edit task details"):
                            st.session_state[f"edit_{task.id}"] = not edit_active
                            st.rerun()
                    with bcol4:
                        if st.button("🗑️ Del", key=f"del_{task.id}", help="Delete task"):
                            database.delete_task(task.id, DB_PATH)
                            st.rerun()

            # Inline Edit Form
            if st.session_state.get(f"edit_{task.id}", False):
                with st.expander(f"✏️ Edit Task Details — #{task.id} {task.title}", expanded=True):
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
                            if st.form_submit_button("💾 Save Changes", type="primary", use_container_width=True):
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
                            if st.form_submit_button("❌ Cancel", use_container_width=True):
                                st.session_state[f"edit_{task.id}"] = False
                                st.rerun()


# ==========================================
# TAB 2: ADD & AI PREDICT TASK
# ==========================================
with tab_add:
    st.subheader("Add New Task with Real-time AI Predictive Analysis")
    st.markdown("Fill in task details to receive an **instant Machine Learning forecast** of completion feasibility before saving.")
    
    with st.form("add_task_form"):
        form_col1, form_col2 = st.columns(2)
        with form_col1:
            title_input = st.text_input("Task Title *", placeholder="e.g., Prepare quarterly financial summary")
            description_input = st.text_area("Description", placeholder="Add context, subtasks, or acceptance criteria...", height=100)
            
        with form_col2:
            deadline_input = st.date_input("Deadline *", min_value=today - datetime.timedelta(days=30), value=today + datetime.timedelta(days=2))
            priority_input = st.selectbox("Base Priority *", ["High", "Medium", "Low"], index=1)
            hours_input = st.number_input("Estimated Completion Hours *", min_value=0.25, max_value=80.0, value=3.0, step=0.5)

        # Real-time AI simulation preview
        st.markdown("---")
        st.markdown("#### 🤖 Live AI Pre-Submission Intelligence")
        
        pred = predict_hypothetical(
            estimated_hours=hours_input,
            deadline_str=deadline_input.isoformat(),
            priority=priority_input,
            reference_date=today
        )
        
        preview_col1, preview_col2, preview_col3 = st.columns(3)
        with preview_col1:
            st.metric("Estimated On-Time Probability", f"{pred['probability']}%")
        with preview_col2:
            st.metric("Predicted Risk Category", pred["risk_level"])
        with preview_col3:
            days_diff = (deadline_input - today).days
            st.metric("Timeline Headroom", f"{days_diff} day(s)")

        st.caption(f"💡 **AI Guidance**: {pred['explanation']}")

        submitted = st.form_submit_button("🚀 Add Task to Smart Reminder AI", type="primary", use_container_width=True)
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
    st.subheader("Explainable AI (XAI) & Dynamic Schedule Optimizer")
    
    active_tasks = [t for t in tasks if t.status != "Completed"]
    if not active_tasks:
        st.info("No active tasks available to optimize.")
    else:
        st.markdown("### 🎯 Today's Recommended Work Agenda")
        st.markdown("The Schedule Optimizer organizes your active workload into high-impact focus blocks based on Smart Urgency and working capacity.")
        
        capacity_hours = st.slider("Today's Available Work Capacity (Hours)", min_value=2.0, max_value=12.0, value=7.0, step=0.5)
        agenda = generate_daily_schedule_agenda(active_tasks, max_hours=capacity_hours, reference_date=today)
        
        st.markdown(f"**Agenda Overview:** {agenda['notes']}")
        
        for item in agenda["schedule"]:
            t = item["task"]
            with st.container():
                st.markdown(f"""
                <div class="schedule-item">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-weight: 700; color: #38bdf8; font-size: 0.95rem;">
                            ⏰ {item['time_slot']} • {item['block_name']} ({item['hours']}h)
                        </span>
                        <span class="badge badge-high">Smart Score: {item['smart_score']}</span>
                    </div>
                    <div style="font-size: 1.1rem; font-weight: 700; color: #f8fafc; margin-top: 4px;">
                        #{t.id} {t.title}
                    </div>
                    <div style="color: #94a3b8; font-size: 0.88rem; margin-top: 4px;">
                        Deadline: {t.deadline} | Priority: {t.priority}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                if item["tips"]:
                    for tip in item["tips"]:
                        st.caption(f"💡 {tip}")

        # Export schedule to Markdown
        agenda_md_lines = [
            f"# ⚡ Smart Reminder AI - Daily Work Agenda ({today.isoformat()})",
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
            label="📥 Export Today's Work Agenda (.md)",
            data=agenda_md_content,
            file_name=f"work_agenda_{today.isoformat()}.md",
            mime="text/markdown",
            use_container_width=False
        )

        st.markdown("---")
        st.markdown("### 🔍 Explainable AI: Priority Drivers & Deep Dive")
        st.markdown("Understand why the AI ranks your top critical items at the highest priority level.")
        
        ranked_top = rank_tasks(active_tasks, reference_date=today, include_completed=False)[:5]
        for task, meta in ranked_top:
            exp = generate_task_explanation(task, reference_date=today)
            with st.expander(f"Task #{task.id}: {task.title} — AI Priority Score {meta['score']} ({meta['band']})"):
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
    st.subheader("Productivity & Performance Analytics (Pandas & Matplotlib)")
    
    if not tasks:
        st.info("No task data available for analytics yet.")
    else:
        acol1, acol2 = st.columns(2)
        with acol1:
            st.markdown("#### Status Breakdown")
            fig_status = plot_status_chart(tasks)
            st.pyplot(fig_status, clear_figure=True)
            
        with acol2:
            st.markdown("#### Workload by Priority")
            fig_priority = plot_priority_bar_chart(tasks)
            st.pyplot(fig_priority, clear_figure=True)

        st.markdown("---")
        st.markdown("#### Historical On-Time Delivery Reliability")
        fig_ontime = plot_ontime_performance_chart(tasks)
        st.pyplot(fig_ontime, clear_figure=True)

        st.markdown("---")
        st.markdown("#### Complete Tasks Data Table")
        df_tasks = database.get_tasks_as_dataframe(DB_PATH)
        csv_data = df_tasks.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Tasks as CSV",
            data=csv_data,
            file_name=f"smart_reminder_tasks_{today.isoformat()}.csv",
            mime="text/csv",
            use_container_width=False
        )
        st.dataframe(df_tasks, use_container_width=True)


# --- Sidebar Controls ---
with st.sidebar:
    st.image("https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=500&auto=format&fit=crop&q=80", use_container_width=True)
    st.markdown("### ⚡ Smart Reminder AI")
    st.caption("AI-Powered Productivity & Task Assistant")
    st.markdown("---")

    st.markdown("#### Quick Tools")
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.rerun()

    if st.button("🌱 Reload Sample Tasks", use_container_width=True):
        database.seed_sample_tasks(DB_PATH, clear_existing=True)
        st.success("Sample tasks loaded!")
        st.rerun()

    st.markdown("---")
    st.markdown("#### System Tech Stack")
    st.markdown("""
    - **Language:** Python 3.11
    - **Database:** SQLite
    - **Data Analytics:** Pandas, Matplotlib
    - **Machine Learning:** Scikit-learn Random Forest
    - **Interface:** Streamlit Dark Glassmorphism
    """)
    st.caption("Smart Reminder AI • Built with Pair Programming")
