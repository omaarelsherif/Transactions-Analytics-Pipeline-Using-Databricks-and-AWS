# Transactions Analytics Pipeline — Databricks & AWS

An automated data engineering pipeline built on Databricks that ingests, transforms, and visualizes transactional data using a **Medallion Architecture** (Bronze / Silver / Gold).

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Technologies](#technologies)
- [Project Structure](#project-structure)
- [Data Schema](#data-schema)
- [Setup Guide](#setup-guide)
- [Pipeline Execution](#pipeline-execution)
- [Dashboard Metrics](#dashboard-metrics)
- [Monitoring](#monitoring)
- [Key Features](#key-features)

---

## Overview

This project delivers a complete, production-ready data pipeline that:

- Ingests CSV data from AWS S3 into Databricks
- Processes data through Bronze → Silver → Gold layers using Delta Live Tables (DLT)
- Automates pipeline execution via table-update triggers
- Visualizes key business metrics through an interactive Lakeview dashboard

---

## Architecture

```
S3 Bucket (4 CSV Files)
        │
        ▼
[Ingestion Pipeline]
        │
        ▼
transactions_project.end_to_end.transactions
        │
        │  (Triggered on table update)
        ▼
[Transactions Job — Databricks Workflow]
        │
        ▼
[Transactions Pipeline — Delta Live Tables]
        ├── Bronze Layer  →  Raw ingestion
        ├── Silver Layer  →  Cleaned & validated
        └── Gold Layer    →  Business aggregates
        │
        ▼
[Daily Transactions Analytics Dashboard]
```

---

## Technologies

| Component        | Tool / Service                          |
|------------------|-----------------------------------------|
| Platform         | Databricks (Serverless Compute)         |
| Data Processing  | Delta Live Tables (DLT) with Photon     |
| Storage          | Unity Catalog (`transactions_project`)  |
| Orchestration    | Databricks Workflows                    |
| Visualization    | Lakeview Dashboards                     |
| File Format      | Delta Lake                              |
| Data Source      | AWS S3                                  |

---

## Project Structure

```
transactions-analytics/
├── README.md
├── ingestion/
│   └── (S3 ingestion config via Databricks Quick Start)
├── transformations/
│   ├── bronze/
│   │   └── transactions_bronze.sql
│   ├── silver/
│   │   └── transactions_silver.sql
│   └── gold/
│       ├── daily_aggregates.sql
│       ├── category_summary.sql
│       └── customer_metrics.sql
├── pipeline/
│   └── Transactions Pipeline (DLT Config)
├── jobs/
│   └── Transactions Job (Workflow Config)
└── dashboards/
    └── Daily Transactions Analytics.lvdash.json
```

---

## Data Schema

**Source Table:** `transactions_project.end_to_end.transactions`

| Column           | Type      | Description                        |
|------------------|-----------|------------------------------------|
| transaction_id   | STRING    | Unique transaction identifier      |
| transaction_date | TIMESTAMP | Date and time of transaction       |
| customer_id      | STRING    | Customer identifier                |
| product_id       | STRING    | Product identifier                 |
| product_name     | STRING    | Product name                       |
| category         | STRING    | Product category                   |
| quantity         | LONG      | Number of items purchased          |
| unit_price       | DOUBLE    | Price per unit                     |
| total_amount     | DOUBLE    | Total transaction amount           |
| store_location   | STRING    | Store location                     |
| payment_method   | STRING    | Payment method used                |
| _rescued_data    | STRING    | Malformed data rescue column       |

---

## Setup Guide

### Prerequisites

- Databricks workspace with Unity Catalog enabled
- AWS S3 bucket containing the source CSV files
- IAM permissions configured for S3 access
- Databricks serverless compute enabled

---

### Step 1 — Ingest Data from S3

1. Navigate to your Databricks workspace
2. Use the **Quick Start** ingestion tool:
   - **Source:** S3 bucket path
   - **Files:** 4 CSV files
   - **Target:** `transactions_project.end_to_end.transactions`
   - **Format:** CSV with header inference

---

### Step 2 — Create the DLT Pipeline

Create a new pipeline named **Transactions Pipeline** with the following configuration:

```json
{
  "name": "Transactions Pipeline",
  "storage": {
    "catalog": "transactions_project",
    "schema": "end_to_end"
  },
  "configuration": {
    "photon": true,
    "serverless": true,
    "channel": "CURRENT"
  },
  "libraries": [
    {
      "type": "glob",
      "include": "/Workspace/Users/<your-email>/Transactions Pipeline/transformations/**"
    }
  ]
}
```

---

### Step 3 — Bronze Layer

Raw data ingestion from the source table:

```sql
-- transformations/bronze/transactions_bronze.sql
CREATE OR REFRESH STREAMING LIVE TABLE transactions_bronze
COMMENT "Raw transactions data ingested from source table"
AS SELECT
  *,
  current_timestamp() AS ingestion_time
FROM STREAM(transactions_project.end_to_end.transactions)
```

---

### Step 4 — Silver Layer

Cleaned and validated transactions:

```sql
-- transformations/silver/transactions_silver.sql
CREATE OR REFRESH STREAMING LIVE TABLE transactions_silver
COMMENT "Cleansed and validated transactions"
AS SELECT
  transaction_id,
  transaction_date,
  customer_id,
  product_id,
  product_name,
  category,
  quantity,
  unit_price,
  total_amount,
  store_location,
  payment_method
FROM STREAM(LIVE.transactions_bronze)
WHERE transaction_id IS NOT NULL
  AND total_amount >= 0
  AND quantity > 0
```

---

### Step 5 — Gold Layer

Business-level aggregates ready for analytics:

```sql
-- transformations/gold/daily_aggregates.sql
CREATE OR REFRESH LIVE TABLE daily_transaction_summary
COMMENT "Daily transaction aggregates for analytics"
AS SELECT
  DATE(transaction_date)        AS transaction_day,
  category,
  store_location,
  COUNT(*)                      AS transaction_count,
  SUM(quantity)                 AS total_items_sold,
  SUM(total_amount)             AS total_revenue,
  AVG(total_amount)             AS avg_transaction_value,
  COUNT(DISTINCT customer_id)   AS unique_customers
FROM LIVE.transactions_silver
GROUP BY
  DATE(transaction_date),
  category,
  store_location
```

---

### Step 6 — Create the Automated Job

1. Create a new Databricks Job named **Transactions Job**
2. Set the trigger:
   - **Type:** Table Update
   - **Table:** `transactions_project.end_to_end.transactions`
   - **Condition:** Any new data arrival
3. Add a task:
   - **Type:** Delta Live Tables
   - **Pipeline:** Transactions Pipeline
   - **Full Refresh:** `false` (incremental updates only)

---

### Step 7 — Build the Dashboard

1. Create a Lakeview dashboard: **Daily Transactions Analytics**
2. Add the following visualizations:
   - Revenue trends over time
   - Top-selling categories
   - Store location performance
   - Payment method distribution
   - Customer purchase patterns

---

## Pipeline Execution

**Manual trigger via Databricks CLI:**

```bash
databricks pipelines start --pipeline-id 93c64af4-4d7e-44f0-bbc5-bcc54132c828
```

**Automated execution:**  
The pipeline runs automatically whenever new data is detected in the source table. Incremental processing ensures efficient and low-latency transformations.

---

## Dashboard Metrics

The **Daily Transactions Analytics** dashboard surfaces:

- Total revenue by day, week, and month
- Transaction volume trends
- Category performance analysis
- Store location comparisons
- Payment method breakdown
- Customer segmentation insights

---

## Monitoring

| Area              | What to Check                                    |
|-------------------|--------------------------------------------------|
| Pipeline Status   | Transactions Pipeline execution logs             |
| Job Runs          | Transactions Job execution history               |
| Data Quality      | DLT expectations and quality metrics             |
| Performance       | Typical incremental run time ~60 seconds         |

---

## Key Features

| Feature                | Description                                              |
|------------------------|----------------------------------------------------------|
| Medallion Architecture | Bronze / Silver / Gold layers for progressive data quality |
| Serverless Compute     | No cluster management required                           |
| Photon Engine          | Optimized query performance                              |
| Event-Driven Triggers  | Automatic pipeline execution on data arrival             |
| Unity Catalog          | Centralized governance, lineage, and security            |
| Delta Lake             | ACID transactions and time travel support                |
