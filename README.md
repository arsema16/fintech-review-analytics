# Fintech Review Analytics

A data engineering pipeline for scraping, analyzing, and visualizing Google Play Store reviews for Ethiopian banking apps.

## Project Overview

This project analyzes user reviews for three Ethiopian banks:
- **Commercial Bank of Ethiopia (CBE)** - 4.2★
- **Bank of Abyssinia (BOA)** - 3.4★
- **Dashen Bank** - 4.1★

## Challenge Context

This is Week 2 of the 10 Academy AI Mastery program. The pipeline addresses three business scenarios:

| Scenario | Description |
|----------|-------------|
| Retaining Users | Analyze whether slow loading is a systemic issue across all three apps |
| Enhancing Features | Extract desired features (fingerprint login, faster transfers, budgeting tools) |
| Managing Complaints | Cluster recurring complaints to guide customer support and AI chatbot strategy |

## Task 1: Data Collection & Preprocessing (Complete)

### Scraping Methodology

**Tool:** `google-play-scraper` Python library

**Target:** 400+ reviews per bank (1,200 total)

**Challenge & Resolution:**

Initial package names were incorrect, resulting in 0 reviews. Manual search identified correct app IDs:

| Bank | Correct Package Name |
|------|---------------------|
| Commercial Bank of Ethiopia | `com.combanketh.mobilebanking` |
| Bank of Abyssinia | `com.boa.boaMobileBanking` |
| Dashen Bank | `com.dashen.dashensuperapp` |

### Collection Results

| Bank | Reviews Collected |
|------|------------------|
| Commercial Bank of Ethiopia | 400 |
| Bank of Abyssinia | 400 |
| Dashen Bank | 400 |
| **Total** | **1,200** |

### Preprocessing Results

| Metric | Value |
|--------|-------|
| Original reviews | 1,200 |
| Final reviews | 1,148 |
| Data retention | 95.7% |
| Missing data rate | 0.0% |

### Final Columns

| Column | Description |
|--------|-------------|
| review | User review text |
| rating | 1-5 star rating |
| date | YYYY-MM-DD format |
| bank | Bank name |
| source | "Google Play" |

### Early Sentiment Findings

| Bank | Average Rating |
|------|----------------|
| Bank of Abyssinia | 3.64★ |
| Dashen Bank | 3.99★ |
| Commercial Bank of Ethiopia | 4.15★ |

## Project Structure
fintech-review-analytics/
├── .github/workflows/
│ └── unittests.yml
├── src/
│ ├── scraper.py
│ └── preprocess.py
├── tests/
│ ├── test_preprocess.py
│ └── test_actual_data.py
├── .gitignore
├── requirements.txt
└── README.md

## Setup Instructions

```bash
git clone https://github.com/arsema16/fintech-review-analytics.git
cd fintech-review-analytics
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python src/scraper.py
python src/preprocess.py
pytest tests/ -v
