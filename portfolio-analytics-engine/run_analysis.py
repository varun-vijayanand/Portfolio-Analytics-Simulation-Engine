#!/usr/bin/env python3
"""
Main execution script for Portfolio Analytics Engine (Updated)
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from src.data_ingestion import DataIngestion
from src.strategy_checker import StrategyChecker
from src.backtest_engine import BacktestEngine
from src.risk_metrics import RiskMetrics
from src.factor_model import FactorModel
from src.report_generator import ReportGenerator  # legacy reports
from src.issue_logger import IssueLogger
from src.institutional_report_engine import InstitutionalReportEngine  # NEW

def main():
    print("🚀 Portfolio Analytics Engine (Updated) Starting...")

    os.makedirs('data/raw', exist_ok=True)
    os.makedirs('data/cleaned', exist_ok=True)
    os.makedirs('reports', exist_ok=True)
    os.makedirs('governance', exist_ok=True)

    ingestion = DataIngestion()
    strategy = StrategyChecker()
    backtest = BacktestEngine()
    risk = RiskMetrics()
    factors = FactorModel()
    legacy_reports = ReportGenerator()
    issues = IssueLogger()
    institutional = InstitutionalReportEngine()

    try:
        print("📊 Step 1: Creating sample portfolio...")
        portfolio = create_sample_portfolio()
        portfolio.to_csv('data/raw/sample_portfolio.csv', index=False)

        print("🔧 Step 2: Loading portfolio...")
        pdf = ingestion.load_portfolio_data('data/raw/sample_portfolio.csv')

        print("📈 Step 3: Fetching market data...")
        tickers = pdf['ticker'].tolist()
        end = datetime.now()
        start = end - timedelta(days=365*3)
        prices = ingestion.fetch_market_data(tickers, start, end)

        print("🎯 Step 4: Strategy alignment...")
        weights = dict(zip(pdf['ticker'], pdf['weight']))
        alignment = strategy.generate_alignment_report(pdf)

        print("📊 Step 5: Historical backtest...")
        hist = backtest.historical_simulation(weights, prices, start, end)

        print("⚠ Step 6: Risk metrics...")
        risk_res = risk.calculate_risk_metrics(hist['returns'])

        print("🔍 Step 7: Factor exposures...")
        fdata = factors.generate_factor_data(tickers)
        exposures = factors.calculate_factor_exposures(weights, fdata)

        print("📋 Step 8: Compile results...")
        results = {
            "portfolio_info": pdf,
            "alignment_report": alignment,
            "historical_results": hist,
            "risk_metrics": risk_res,
            "factor_exposures": exposures,
            "total_return": hist["total_return"],
            "annual_return": hist["annual_return"],
            "volatility": hist["volatility"],
            "cumulative_returns": hist["cumulative_returns"],
            "benchmarks": None
        }

        print("📄 Step 9: Legacy reports...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        excel_path = f"reports/analysis_{timestamp}.xlsx"
        pdf_path   = f"reports/simple_{timestamp}.pdf"

        legacy_reports.generate_excel_report(results, excel_path)
        legacy_reports.generate_pdf_report(results, pdf_path)

        print("🏦 Step 10: New blended institutional report...")
        blended_path = institutional.generate(results)

        print("\n✅ All reports generated successfully!")
        print(f"Excel: {excel_path}")
        print(f"Simple PDF: {pdf_path}")
        print(f"Institutional Blended PDF: {blended_path}")

    except Exception as e:
        issues.log_issue(
            "ANALYSIS_ERROR",
            f"Error: {str(e)}",
            "HIGH",
            "run_analysis"
        )
        raise

def create_sample_portfolio():
    return pd.DataFrame({
        'ticker': ['AAPL','MSFT','GOOGL','AMZN','TSLA'],
        'weight': [0.2,0.2,0.2,0.2,0.2],
        'trade_date': ['2024-01-15']*5,
        'asset_class': ['Equity']*5
    })

if __name__ == "__main__":
    main()
