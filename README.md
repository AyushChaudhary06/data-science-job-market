# 📊 Data Science Job Market Intelligence Dashboard

A data analytics project that explores the **DA/DS job market** using real Glassdoor job posting data. Built with Python, SQL, and Streamlit — fully interactive and deployed live.

🔗 **Live App:** [View on Streamlit Cloud](#) *(deploy link here)*  
📁 **Dataset:** Glassdoor Data Science Jobs (Kaggle)

---

## 🧠 Project Overview

This project answers real questions that every data professional asks:

- Which cities have the most DA/DS job openings?
- What skills are companies demanding the most?
- How does salary vary across roles, company size, and sector?
- Which companies are hiring aggressively right now?

---

## 🔍 Key Insights

| Insight | Finding |
|--------|---------|
| 🥇 Most in-demand skill | **SQL** (1,389 job postings) |
| 🥈 Second most demanded | **Excel** (1,354 job postings) |
| 🐍 Top programming language | **Python** (637 postings) |
| 📊 Most common role | Data Analyst |
| 🏙️ Top hiring city | New York, NY |

---

## 🛠️ Tech Stack

| Layer | Tools Used |
|-------|-----------|
| Data Cleaning | Python, Pandas |
| Analysis | Pandas, Plotly |
| Database | PostgreSQL + SQL queries |
| Dashboard | Streamlit, Plotly Express |
| Deployment | Streamlit Community Cloud |

---

## 📁 Project Structure

```
job-market-analysis/
│
├── app/
│   └── app.py                  # Streamlit app (4 pages)
│
├── data/
│   ├── raw/                    # Original Kaggle dataset
│   └── processed/
│       ├── cleaned_jobs.csv    # Cleaned job postings
│       └── skills_data.csv     # Exploded skills per job
│
├── notebooks/
│   └── data_cleaning.ipynb     # EDA + data cleaning pipeline
│
├── sql/
│   └── analysis_queries.sql    # Key business queries
│
└── README.md
```

---

## 📱 App Pages

### 📊 Market Snapshot
KPI tiles (total jobs, companies, cities, avg salary, avg rating) + jobs by role, jobs by city, sector breakdown, company size distribution.

### 🔧 Skill Demand
Top skills overall + skill demand filtered by role — helps identify what to learn based on target role.

### 💰 Salary Analysis
Salary distribution by role (box plots), by sector, by company size, and by city. Includes Rating vs Salary scatter.

### 🏢 Company Intel
Top 20 hiring companies, ownership type breakdown, company age vs hiring trends, and a searchable company explorer table.

---

## ⚙️ How to Run Locally

```bash
# 1. Clone the repo
git clone https://github.com/GIT-BYHARSH/job-market-analysis.git
cd job-market-analysis

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
streamlit run app/app.py
```

---

## 📦 Requirements

```
streamlit>=1.37.0
pandas>=2.0.0
plotly>=5.0.0
```

---

## 👤 Author

**Harsh** — B.Tech CSE (AI & ML), ABES Engineering College  
📧 [LinkedIn](https://linkedin.com/in/your-profile) | 💻 [GitHub](https://github.com/GIT-BYHARSH)
