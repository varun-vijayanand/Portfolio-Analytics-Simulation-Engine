# run_analysis.py
#!/usr/bin/env python3
"""
Main execution script for Portfolio Analytics Engine
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import sys

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from data_ingestion import DataIngestion
from strategy_checker import StrategyChecker
from backtest_engine import BacktestEngine
from risk_metrics import RiskMetrics
from factor_model import FactorModel
from report_generator import ReportGenerator
from issue_logger import IssueLogger

def main():
    print("🚀 Portfolio Analytics Engine - Starting Analysis")
    
    # Create necessary directories
    os.makedirs('data/raw', exist_ok=True)
    os.makedirs('data/cleaned', exist_ok=True)
    os.makedirs('data/reference', exist_ok=True)
    os.makedirs('reports', exist_ok=True)
    os.makedirs('governance', exist_ok=True)
    
    # Initialize components
    data_ingestion = DataIngestion()
    strategy_checker = StrategyChecker()
    backtest_engine = BacktestEngine()
    risk_metrics = RiskMetrics()
    factor_model = FactorModel()
    report_generator = ReportGenerator()
    issue_logger = IssueLogger()
    
    try:
        # 1. Create sample portfolio data
        print("📊 Step 1: Creating sample portfolio...")
        sample_portfolio = create_sample_portfolio()
        sample_portfolio.to_csv('data/raw/sample_portfolio.csv', index=False)
        
        # 2. Load and clean data
        print("🔧 Step 2: Loading and cleaning data...")
        portfolio_df = data_ingestion.load_portfolio_data('data/raw/sample_portfolio.csv')
        portfolio_df.to_csv('data/cleaned/portfolio_cleaned.csv', index=False)
        
        # 3. Fetch market data
        print("📈 Step 3: Fetching market data...")
        tickers = portfolio_df['ticker'].tolist()
        end_date = datetime.now()
        start_date = end_date - timedelta(days=5*365)  # 5 years
        
        price_data = data_ingestion.fetch_market_data(tickers, start_date, end_date)
        price_data.to_csv('data/cleaned/price_data.csv')
        
        # 4. Strategy alignment check
        print("🎯 Step 4: Checking strategy alignment...")
        portfolio_weights = dict(zip(portfolio_df['ticker'], portfolio_df['weight']))
        alignment_report = strategy_checker.generate_alignment_report(portfolio_df)
        
        # 5. Historical backtest
        print("📊 Step 5: Running historical backtest...")
        historical_results = backtest_engine.historical_simulation(
            portfolio_weights, price_data, start_date, end_date
        )
        
        # 6. Risk analysis
        print("⚠️  Step 6: Calculating risk metrics...")
        risk_results = risk_metrics.calculate_risk_metrics(historical_results['returns'])
        
        # 7. Factor exposure analysis
        print("🔍 Step 7: Analyzing factor exposures...")
        factor_data = factor_model.generate_factor_data(tickers)
        factor_exposures = factor_model.calculate_factor_exposures(portfolio_weights, factor_data)
        
        # 8. Compile results
        print("📋 Step 8: Compiling analysis results...")
        analysis_results = {
            'portfolio_info': portfolio_df,
            'alignment_report': alignment_report,
            'historical_results': historical_results,
            'risk_metrics': risk_results,
            'factor_exposures': factor_exposures,
            'total_return': historical_results['total_return'],
            'annual_return': historical_results['annual_return'],
            'volatility': historical_results['volatility'],
            'sharpe_ratio': historical_results['sharpe_ratio'],
            'max_drawdown': historical_results['max_drawdown']
        }
        
        # 9. Generate reports
        print("📄 Step 9: Generating reports...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Excel report
        excel_report_path = f'reports/portfolio_analysis_{timestamp}.xlsx'
        report_generator.generate_excel_report(analysis_results, excel_report_path)
        
        # PDF report
        pdf_report_path = f'reports/risk_report_{timestamp}.pdf'
        report_generator.generate_pdf_report(analysis_results, pdf_report_path)
        
        print(f"✅ Analysis completed successfully!")
        print(f"📊 Excel report: {excel_report_path}")
        print(f"📄 PDF report: {pdf_report_path}")
        print(f"📈 Total Return: {analysis_results['total_return']:.2%}")
        print(f"⚡ Volatility: {analysis_results['volatility']:.2%}")
        print(f"🎯 Sharpe Ratio: {analysis_results['sharpe_ratio']:.2f}")
        
    except Exception as e:
        # Log any issues
        issue_id = issue_logger.log_issue(
            'ANALYSIS_ERROR', 
            f'Error during portfolio analysis: {str(e)}',
            'HIGH',
            'MainAnalysis'
        )
        print(f"❌ Analysis failed. Issue logged: {issue_id}")
        raise

def create_sample_portfolio():
    """Create a sample portfolio for demonstration"""
    return pd.DataFrame({
        'ticker': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'BRK-B', 'JPM', 'JNJ', 'V', 'PG'],
        'weight': [0.15, 0.14, 0.13, 0.12, 0.10, 0.08, 0.07, 0.06, 0.08, 0.07],
        'trade_date': ['2024-01-15'] * 10,
        'asset_class': ['Equity'] * 10
    })

if __name__ == "__main__":
    main()