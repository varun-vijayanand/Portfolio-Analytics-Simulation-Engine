# Portfolio Analytics Simulation Engine
A 55ip / J.P. Morgan Quant R&amp;D Style Portfolio Analysis Platform

## Overview
This project replicates the core responsibilities of a Portfolio Analyst in a Quant R&D team — including portfolio evaluation, risk analysis, strategy alignment checks, historical simulations, and forward-looking modeling.

It is inspired by workflows used in 55ip, J.P. Morgan, BlackRock, and similar investment research teams.

The engine supports:
- Importing multi-asset portfolio data
- Simulating historical & forward returns
- Evaluating trade suggestions
- Monitoring strategy alignment
- Calculating risk metrics (volatility, beta, VaR, drawdown)
- Conducting factor exposures (Value, Momentum, Size, Quality)
- Investigating datasets using SQL
- Generating automated reports in Excel + Tableau
- Logging issues (JIRA-style)
- Documenting operational workflows

## Key Features

### 1. Portfolio Ingestion & Cleaning
- Load positions: weights, tickers, trade dates
- Validate constraints
- Handle corporate actions
- Generate clean datasets & metadata

### 2. Strategy Alignment Check
- Detect deviations vs target strategy
- Logic for:
- overweight/underweight detection
- tracking error
- drift thresholds

### 3. Backtesting & Simulation
- Historical simulation (5Y, 10Y, dynamic windows)
- Forward-looking scenarios:
- Monte Carlo
- Regime shifts
- Stress periods (COVID, GFC, taper tantrum)

### 4. Risk Analysis
- Volatility
- Beta vs benchmark
- Maximum Drawdown
- Value-at-Risk (parametric & historical)
- Expected Shortfall

### 5. Trade Suggestion Analysis
- Evaluate expected return impact
- Rebalance logic
- Turnover & transaction cost modeling

### 6. Factor Exposure Breakdown
- Based on Fama-French & AQR signals:
- Value
- Size
- Momentum
- Quality
- Low Vol

### 7. SQL-Based Dataset Investigation
- Custom queries
- Data gap detection
- Summary stats

### 8. Reporting Automation
- Excel reports (XlsxWriter)
- Tableau data extracts (.hyper)
- Daily PDF risk report

### 9. Governance & Issue Tracking
- Automated audit logs
- JIRA-style JSON issue registry


## Tech Stack
- Python: pandas, numpy, statsmodels, matplotlib, seaborn
- SQL: SQLite/PostgreSQL
- Backtesting: custom engine + vectorized operations
- Reporting: XlsxWriter, FPDF
- Dashboard: Tableau
- Documentation: Markdown + flow diagrams
