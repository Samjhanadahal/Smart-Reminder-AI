# ⚡ Smart Reminder AI

[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-FF4B4B?style=flat&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Scikit-Learn](https://img.shields.io/badge/scikit--learn-1.3+-F7931E?style=flat&logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![SQLite](https://img.shields.io/badge/SQLite-3-003B57?style=flat&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Tests Passing](https://img.shields.io/badge/Tests-35%20Passed-10b981?style=flat)](tests/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=flat)](LICENSE)

An intelligent, machine-learning-powered task management and reminder assistant. It combines dynamic priority scoring, Scikit-learn completion risk prediction, Explainable AI (XAI) advice, daily schedule optimization, and a modern Streamlit web dashboard.

---

## ✨ Features

- 🎯 **Smart Priority Scoring (0–100)**: Evaluates deadlines, priority weights, effort, and progress into clear bands (*Critical*, *High*, *Medium*, *Low*).
- 🤖 **ML Feasibility Risk Predictor**: Pre-trained Random Forest model forecasting whether tasks will be completed on time before deadlines slip.
- 🧠 **Explainable AI (XAI) & Advice**: Identifies key urgency drivers and provides actionable productivity tips.
- ⏱️ **Daily Schedule Optimizer**: Automatically organizes active tasks into high-impact daily focus blocks to prevent burnout.
- 🔔 **Proactive Reminders & Daily Digest**: Triage buckets for *Overdue*, *Due Today*, *Next 48 Hours*, and *This Week* with workload overload detection.
- 📊 **Visual Analytics**: Interactive dark-themed charts (task status donut, workload by priority, and on-time delivery reliability).
- 🖥️ **Dual Interfaces**: Feature-rich Streamlit web dashboard with live search, in-line editing, and CSV/Markdown export, alongside a 13-option CLI menu.

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Launch the Application

**Option A: Web Dashboard (Recommended)**
- On Windows: Double-click `run_dashboard.bat`, or run:
```bash
python -m streamlit run src/dashboard.py
```
Open **http://localhost:8501** in your browser.

**Option B: CLI Master Menu**
- On Windows: Double-click `run_cli.bat`, or run:
```bash
python src/app.py
```

---

## 🧪 Running Tests

The test suite includes **35 automated unit tests** across all modules with a 100% pass rate:

```bash
python -m unittest discover tests
```

---

## 📁 Project Structure

```text
Smart Reminder AI/
├── data/
│   └── tasks.db               # SQLite database
├── src/
│   ├── models.py              # Task domain model & OOP logic
│   ├── database.py            # SQLite CRUD & DataFrame operations
│   ├── smart_priority.py      # Dynamic composite priority algorithm
│   ├── reminders.py           # Reminder engine & burnout detection
│   ├── analytics.py           # Metrics calculation & Matplotlib charts
│   ├── ml_predictor.py        # Scikit-learn Random Forest model
│   ├── recommendations.py     # Explainable AI & daily schedule optimizer
│   ├── dashboard.py           # Streamlit web dashboard
│   └── app.py                 # Interactive CLI master menu
├── tests/                     # 35 comprehensive unit tests
├── run_dashboard.bat          # 1-click launcher for Web UI
├── run_cli.bat                # 1-click launcher for CLI
├── requirements.txt           # Python dependencies
└── README.md
```

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
