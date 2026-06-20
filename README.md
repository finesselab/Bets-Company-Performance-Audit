# Bets Company Performance Audit

## Project Overview
This repository contains an end-to-end data analytics, machine learning segmentation, and behavioral retention pipeline developed for a sports betting and gaming platform. The project audits user transaction ledger data, builds advanced customer segmentation frameworks, tracks long-term cohort retention profiles, and integrates an AI-driven automated marketing recommendation engine directly into an interactive executive performance dashboard.

---

## Data Pipeline & Architecture Workflow

### 1. Data Engineering & ETL Pipeline (`1. ETL code 1.py`)
* **Objective:** Ingest raw relational database tables (`USERS`, `ACTIONS`, `BONUS`) and map complex conditional ledger rules into analytics-ready dimensions.
* **Key Tasks:** * Computes dynamic marketing campaign flags (e.g., *High Roller*, *Weekend Special*, *VIP Exclusive*) over exact time windows based on user bet stakes and deposit volumes.
  * Measures onboarding effectiveness by extracting conditional Welcome Bonus eligibility thresholds ($\ge £100$ deposits within a registration window).
  * Cleanses multi-table data using `pandas` and writes structurally optimized schemas back to AWS hosted SQL Server (`users_welcomebonus` and `actions_df`).

### 2. Feature Engineering & RFM Modeling (`2. RFM SQL Code.txt`)
* **Objective:** Compress high-velocity user action histories into static consumer behavioral metrics.
* **Key Tasks:**
  * Defines an automated T-SQL View (`RFM_data`) calculating standard customer metrics relative to the maximum timeline boundary.
  * **Recency:** Days since a user's absolute last interaction.
  * **Frequency:** The total count of distinct calendar days a user placed an active stake.
  * **Monetary Value:** Total Stakes (`ACTION_TYPE = 'BET'`).

### 3. Machine Learning Segmentation (`3. KMeans Clustering.py`)
* **Objective:** Clusters the customer base into distinct data-driven operational characteristics.
* **Key Tasks:**
  * Pulls live RFM views from SQL Server, handles feature scaling via `StandardScaler`, and applies an unsupervised **K-Means Clustering** algorithm ($k=4$).
  * Outlines population variance metrics via the Elbow Method (Sum of Squared Errors) to map out high-value bettors, frequent bettors, casual bettors and inactive bettors.

### 4. Generative AI Recommendation (`4. LLM summary and marketing recommendation.py`)
* **Objective:** Automate human-like business strategy generation from cluster data.
* **Key Tasks:**
  * Feeds K-Means cluster summaries directly into a loop-driven LLM pipeline (`Groq / Llama-3.3`).
  * Enforces a strict JSON schema mapping data definitions directly to Power BI (`cluster_summaries` and `marketing_recommendations`).

---

## Power BI Dashboard

### Tab 1: Corporate Performance Overview
* **Objective:** Tracks platform health metrics including Gross Gaming Revenue (GGR), Monthly Active Users (MAU) vs. corporate targets, and bet counts.
* **Key Auditing Diagnostic Ratios:** Surfaces key auditing ratios such as the *Bonus-to-GGR ratio* ($2.70$) and *Withdrawals-to-Deposit ratio* ($0.98$) alongside a moving 30-day average trendline to isolate high-volume revenue windows.

### Tab 2: Customer Behaviour and Recommendation
* **Objective:** Visualizes the distribution of the user base across the 4 core K-Means segments (*High-Value Bettors*, *Frequent Bettors*, *Casual Bettors*, and *Inactive Bettors*) cross-referenced by baseline user classifications (`player` vs. `VIP`).
* **AI Strategy Integration:** Integrates the final structured AI data directly into interactive tables, pairing the behavioral profiles with automated marketing campaign recommendations (e.g., matching the high-risk "Inactive Bettors" segment to targeted reactivation).

### Tab 3: Customer Retention Rate 
* **Objective:** Locks the initial lifecycle baseline to each user's first active 2024 transaction month, then tracks engagement for the exact same cohort over a 12-month period. 
* **Key Insight:** Uncovers a core, highly resilient player base (maintaining 98%–99% activity retention throughout the trailing year).
