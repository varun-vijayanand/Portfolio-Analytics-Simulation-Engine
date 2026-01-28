# Portfolio Analytics Simulation Engine
55ip / J.P. Morgan–style institutional portfolio analytics platform.

## Overview
Modular toolkit that mirrors a buy-side portfolio/risk analyst workflow: ingest a portfolio, align to strategy, backtest, simulate forward paths, run factor + risk analytics, and produce institutional PDF/Excel deliverables with governance trails.

Core capabilities:
- Portfolio ingestion & validation (CSV, corporate actions)
- Historical backtesting + Monte Carlo
- Risk analytics (VaR/ES, beta, tracking error, drawdown)
- Factor modeling (Value, Momentum, Size, Quality, Low-Vol)
- Strategy alignment & drift checks
- SQL-backed governance logging + issue tracking
- Institutional reports (BlackRock, J.P. Morgan, UBS sections) + legacy PDF/Excel
- Optional LLM narratives (falls back to rules-based text when API key absent)

## Quick Start
1) Install Python 3.10+ and create a virtual env.  
2) From the repo root:
```
cd portfolio-analytics-engine
python -m venv .venv && source .venv/bin/activate
pip install -r ../requirements.txt
```
3) Run the end-to-end demo (uses yfinance for fresh prices; bundled sample data is also present under `data/`):
```
python run_analysis.py
```
Outputs land in `portfolio-analytics-engine/reports/` and governance artifacts in `portfolio-analytics-engine/governance/`.

4) Run tests:
```
pytest
```

## Repository Layout
- `portfolio-analytics-engine/run_analysis.py` — orchestrates the full workflow (ingest → align → backtest → risk/factors → reporting).
- `portfolio-analytics-engine/src/data_ingestion.py` — portfolio CSV loader, market/benchmark downloaders, corporate actions, Fama–French/risk-free loaders.
- `portfolio-analytics-engine/src/backtest_engine.py` — historical simulation, performance metrics, Monte Carlo, stress tests.
- `portfolio-analytics-engine/src/strategy_checker.py` — active weight, drift, concentration, tracking error checks.
- `portfolio-analytics-engine/src/risk_metrics.py` — VaR/ES, beta, tracking error, information ratio, drawdown.
- `portfolio-analytics-engine/src/factor_model.py` — factor exposure math + Fama–French regression helper.
- `portfolio-analytics-engine/src/report_generator.py` — legacy Excel + simple PDF and single-brand institutional reports.
- `portfolio-analytics-engine/src/institutional_report_engine.py` — blended BlackRock/JPM/UBS PDF plus governance logging.
- `portfolio-analytics-engine/src/llm_narrative.py` — optional OpenAI-powered narratives with safe fallbacks.
- `portfolio-analytics-engine/src/sql_engine.py` / `sql_queries.py` — SQLite metadata logging + query helpers.
- `portfolio-analytics-engine/src/issue_logger.py` — governance issue log JSON helper.
- `portfolio-analytics-engine/notebooks/*.ipynb` — stepwise exploratory workflows (cleaning, alignment, backtest, risk, reporting).
- `portfolio-analytics-engine/data/` — sample raw/cleaned/reference data to run offline.
- `portfolio-analytics-engine/tests/` — pytest coverage for backtesting and risk math.

## Workflow (what `run_analysis.py` does)
1. Build a sample portfolio (5 equities, equal weight).
2. Ingest portfolio CSV; fetch market prices via yfinance.
3. Strategy alignment report (active weights, drift, concentration).
4. Historical backtest with lookback clamping + derived performance metrics.
5. Risk metrics (vol, VaR/ES, drawdown, beta/TE/IR if benchmark supplied).
6. Factor exposure calculation (mock factor data for demo).
7. Reporting:
   - Excel workbook and simple PDF (legacy)
   - Blended institutional PDF (BlackRock → JPM → UBS sections)
8. Governance: SQLite metadata + JSON issue log; narratives recorded per run.

## Data & Offline Use
- Bundled under `portfolio-analytics-engine/data/`:
  - `raw/` price, dividend, split, Fama–French, risk-free samples
  - `reference/` benchmark + holdings configs
  - `cleaned/` example cleaned datasets
- If yfinance is blocked, swap to the provided CSVs by reading them directly in `run_analysis.py`.

## LLM Narratives
- Optional: set `OPENAI_API_KEY` to enable live LLM calls.
- Without a key, deterministic fallback narratives are used (safe for air-gapped runs).

## Governance & Reporting Outputs
- PDFs/XLSX written to `portfolio-analytics-engine/reports/`.
- Metadata DB + issue log in `portfolio-analytics-engine/governance/` (auto-created).

## Extending
- Add factors: extend `FACTOR_DEFINITIONS` in `src/utils.py` and supply real factor data.
- Swap benchmarks: update `PortfolioConfig.BENCHMARKS`.
- Deploy as batch/cron: schedule `run_analysis.py` and archive `reports/` + `governance/`.
