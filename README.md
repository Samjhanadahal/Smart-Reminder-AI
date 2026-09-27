# ⚡ Smart Reminder AI

An intelligent task and reminder application that combines **Object-Oriented Architecture**, **SQLite persistence**, **Matplotlib analytics**, **Scikit-learn Machine Learning**, and an interactive **Streamlit web dashboard** to transform productivity and task scheduling.

---

## 🌟 Key Highlights & Features

### 1. 📋 Core Task & Data Management (Phases 1 & 2)
* **Object-Oriented Design**: Clean `Task` domain model encapsulating validation, date arithmetic, status transitions, and priority weights.
* **SQLite Persistence**: Reliable transactional storage with parameterized queries, schema auto-migration, status tracking, and sample data seeding.

### 2. 🎯 Smart Dynamic Priority Scoring (Phase 3)
* Calculates real-time composite scores (0–100) combining:
  * **Base Priority Weight** (High = 30, Medium = 20, Low = 10)
  * **Urgency & Proximity** (Progressive scale for overdue, due today, next 48h, and upcoming days)
  * **Effort Intensity & Workload Pressure** (Ratio of required hours against remaining lead time)
  * **Execution Momentum** (Continuity boost for in-progress tasks)
* Dynamic priority bands: **Critical** (≥80), **High** (60–79), **Medium** (40–59), and **Low** (<40).

### 3. 🔔 Proactive Reminder Engine & Workload Overload Detection (Phase 4)
* Categorizes pending tasks into actionable buckets: **Overdue**, **Due Today**, **Due Within 48 Hours**, and **Due This Week**.
* **Burnout & Capacity Protection**: Monitors workload against daily capacity (e.g., 8h/day limit) and raises overload alerts with exact deficit metrics.
* **Daily Digest**: Formatted ASCII / notification digest ready for CLI, push notifications, or morning summaries.

### 4. 📊 Visual Analytics & Performance Reporting (Phase 5)
* Computed productivity metrics: Completion Rate, Historical On-Time Delivery %, Total/Remaining Estimated Hours, and Average Task Duration.
* Matplotlib charts styled with sleek dark themes:
  * **Task Status Breakdown**: Donut chart with completion proportions.
  * **Workload by Priority**: Horizontal bar chart comparing task count and hours across priorities.
  * **Delivery Reliability Gauge**: Historical on-time vs. late delivery percentages.

### 5. 🤖 Machine Learning On-Time Completion Predictor (Phase 6)
* Built with **Scikit-learn `RandomForestClassifier`** and `StandardScaler` pipeline.
* Evaluates non-linear feature interactions:
  * Estimated hours
  * Days remaining until deadline
  * Priority weights
  * Urgency ratio (workload vs. available daily hours)
  * In-progress momentum status
* **Live Pre-Submission Intelligence**: Predicts on-time feasibility and risk tiers (*Low Risk*, *Moderate Risk*, *High Risk*) before saving a task.

### 6. 🧠 Explainable AI (XAI) & Daily Schedule Optimizer (Phase 7)
* **Explainable AI (XAI)**: Demystifies priority rankings by highlighting specific drivers (deadline urgency, complexity warnings, quick wins) along with tailored coaching tips.
* **Focus Schedule Generator**: Organizes daily tasks into dedicated focus slots (e.g., *Morning Deep Work*, *Pre-Noon Sprint*, *Afternoon Execution*, *Wrap-up & Review*) while respecting custom daily hour budgets.

### 7. 🚀 Dual Interfaces: Streamlit Web Dashboard & CLI Master Menu (Phase 8)
* **Streamlit Web Dashboard** (`src/dashboard.py`):
  * Modern Dark Glassmorphism aesthetic with responsive metric KPI cards.
  * 4 interactive tabs: *Smart Task Center*, *Add & AI Predict*, *Explainable AI & Daily Schedule*, and *Productivity Analytics*.
  * Real-time filtering by status, priority, and AI smart ranking.
* **Interactive CLI Master Menu** (`src/app.py`):
  * Full 12-option terminal workflow for terminal enthusiasts.

---

## 🛠️ Tech Stack

| Component | Technology | Description |
| :--- | :--- | :--- |
| **Language** | Python 3.11+ | Modern, strongly typed OOP code |
| **Database** | SQLite 3 | Embedded zero-configuration SQL engine |
| **Data & Analytics** | Pandas, Matplotlib | High-performance dataframes & publication-ready charts |
| **Machine Learning** | Scikit-learn, NumPy | Random Forest ensemble classifier & numerical pipelines |
| **Web Interface** | Streamlit | Reactive dark-mode web application |
| **Testing** | Unittest | 33 comprehensive automated test cases |

---

## 📁 Project Structure

```
Smart Reminder AI/
├── data/
│   └── tasks.db               # SQLite database (auto-created on first run)
├── src/
│   ├── __init__.py            # Package root & public module exports
│   ├── app.py                 # CLI master menu & terminal application
│   ├── dashboard.py           # Streamlit web dashboard (glassmorphism UI)
│   ├── models.py              # OOP Task model and validation rules
│   ├── database.py            # SQLite database access layer & seeding
│   ├── smart_priority.py      # Smart Priority scoring algorithm (0-100)
│   ├── reminders.py           # Reminder engine, alert categorization & digest
│   ├── analytics.py           # Metrics calculation & Matplotlib dark charts
│   ├── ml_predictor.py        # Scikit-learn Random Forest predictive pipeline
│   └── recommendations.py     # Explainable AI & daily schedule optimizer
├── tests/
│   ├── test_tasks.py          # Unit tests for Task model
│   ├── test_database.py       # Unit tests for database CRUD operations
│   ├── test_smart_priority.py # Unit tests for Smart Priority calculations
│   ├── test_reminders.py      # Unit tests for reminder alert bucketing
│   ├── test_analytics.py      # Unit tests for analytics & plot generators
│   ├── test_ml_predictor.py   # Unit tests for ML feature extraction & models
│   └── test_recommendations.py# Unit tests for XAI tips & schedule agenda
├── requirements.txt           # Project dependencies
├── .gitignore                 # Git ignore rules for Python, SQLite & cache
└── README.md                  # Comprehensive project documentation
```

---

## 🚀 Getting Started

### 1. Prerequisites
Ensure you have **Python 3.11** (or 3.10+) installed on your machine.

### 2. Clone the Repository
```bash
git clone https://github.com/Samjhanadahal/Smart-Reminder-AI.git
cd "Smart Reminder AI"
```

### 3. Set Up a Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 💻 How to Run

### Option A: Launch the Streamlit Web Dashboard (Recommended)
Launch the web interface in your browser:
```bash
streamlit run src/dashboard.py
```
> The dashboard will automatically open at `http://localhost:8501`. If your database is empty, click **"Load Realistic Sample Tasks"** to test features immediately!

### Option B: Launch the Interactive CLI Master Menu
For terminal-based task management:
```bash
python src/app.py
```

```
=======================================================
         ⚡ SMART REMINDER AI - MASTER MENU
=======================================================
 1. Add a New Task (with AI Feasibility Forecast)
 2. View All Tasks (Standard View)
 3. View Smart Priority AI Ranked Tasks (Phase 3)
 4. View Reminder Alerts & Daily Digest (Phase 4)
 5. View Productivity Analytics Summary (Phase 5)
 6. AI Completion Predictions & Explanations (Phase 6 & 7)
 7. Generate Optimized Daily Work Schedule (Phase 7)
 8. Update Task Status
 9. Delete a Task
10. Seed Realistic Sample Tasks (Demo Data)
11. Launch Streamlit Web Dashboard (Phase 8)
12. Exit
=======================================================
```

---

## 🧪 Running the Automated Test Suite

Run the full automated test suite containing **33 unit tests** across all 7 test suites:

```bash
python -m unittest discover tests
```

Expected output:
```
.................................
----------------------------------------------------------------------
Ran 33 tests in 0.480s

OK
```

You can also run specific test modules individually:
```bash
python -m unittest tests/test_tasks.py
python -m unittest tests/test_smart_priority.py
python -m unittest tests/test_ml_predictor.py
python -m unittest tests/test_recommendations.py
```

---

## 🧠 Algorithmic Architecture

### 1. Smart Priority Score Calculation
$$\text{Score} = \text{PriorityWeight} + \text{UrgencyScore} + \text{EffortScore} + \text{StatusBonus}$$

* **Priority Weight**: High = 30 pts, Medium = 20 pts, Low = 10 pts
* **Urgency Score**: Overdue ($\ge 45\text{ pts} + 2 \times \text{days overdue}$), Due today ($42\text{ pts}$), $\le 3\text{ days}$ ($26\text{ pts}$), $\le 7\text{ days}$ ($16\text{ pts}$), $\le 14\text{ days}$ ($8\text{ pts}$)
* **Effort & Workload**: Scaled by estimated hours with an additional penalty if high effort tasks have $\le 2$ days remaining.
* **Status Bonus**: $+4\text{ pts}$ for in-progress tasks to encourage focus momentum.

### 2. Scikit-learn Risk Prediction Model
* **Model Type**: Random Forest Classifier with standard scaling pipeline (`StandardScaler` + `RandomForestClassifier(n_estimators=120, max_depth=6)`).
* **Feature Schema**:
  1. `estimated_hours` ($[0.5, 25]$)
  2. `days_until_deadline` ($[-3, 25]$)
  3. `priority_weight` ($1.0, 2.0, 3.0$)
  4. `urgency_ratio` ($\frac{\text{estimated\_hours}}{\text{available\_working\_hours}}$)
  5. `is_in_progress` ($0$ or $1$)

---

## 📄 License
This project is open-source and available under the [MIT License](LICENSE).
