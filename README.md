# Smart Reminder AI

A machine-learning-assisted task management and reminder tool built with Python and Streamlit. It calculates dynamic priority scores, predicts deadline risk, and helps schedule daily focus blocks.

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-FF4B4B?style=flat&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Scikit-Learn](https://img.shields.io/badge/scikit--learn-1.3+-F7931E?style=flat&logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![Tests](https://img.shields.io/badge/Tests-35%20Passed-10b981?style=flat)](tests/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=flat)](LICENSE)

---

## Overview

Smart Reminder AI is designed to help organize tasks effectively without complicated setup. It analyzes deadlines, estimated effort, and priorities to give each task an urgency score (0–100) and uses a Scikit-learn model to identify tasks at risk of being delayed.

---

## Features

- **Priority Scoring**: Computes a balanced 0–100 score based on due dates, required effort, and priority level.
- **Risk Prediction**: Uses a Random Forest classifier to flag tasks that may miss their deadlines.
- **Recommendations**: Suggests next steps and structures tasks into realistic daily focus blocks.
- **Reminders**: Organizes items into clear groups: Overdue, Due Today, Next 48 Hours, and This Week.
- **Interfaces**: Includes both a Streamlit web interface with visual charts and a terminal CLI.

---

## Installation & Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the application

To open the web dashboard:
```bash
streamlit run src/dashboard.py
```
*(On Windows, you can also run `run_dashboard.bat`)*

To use the command-line interface:
```bash
python src/app.py
```
*(On Windows, you can also run `run_cli.bat`)*

---

## Tests

To run the automated test suite:

```bash
python -m unittest discover tests
```

---

## Project Structure

```text
Smart Reminder AI/
├── data/               # SQLite database storage (tasks.db)
├── src/
│   ├── dashboard.py    # Streamlit web dashboard
│   ├── app.py          # Command-line interface
│   ├── ml_predictor.py # Risk prediction model
│   ├── smart_priority.py # Priority calculation logic
│   ├── recommendations.py # Daily schedule & task advice
│   ├── reminders.py    # Reminder logic & workload alerts
│   ├── database.py     # SQLite database operations
│   └── models.py       # Task data models
└── tests/              # Unit tests
```

---

## License

This project is licensed under the [MIT License](LICENSE).
