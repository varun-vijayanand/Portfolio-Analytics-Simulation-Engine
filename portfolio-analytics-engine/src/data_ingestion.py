# src/data_ingestion.py
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
import sqlite3
from .utils import PortfolioConfig

class DataIngestion:
    def __init__(self, db_path='data/portfolio.db'):
        self.db_path = db_path
        self.config = PortfolioConfig()
        
    def load_portfolio_data(self, file_path=None, df=None):
        """Load portfolio positions from file or DataFrame"""
        if df is not None:
            portfolio_df = df.copy()
        else:
            portfolio_df = pd.read_csv(file_path)
        
        # Validate required columns
        required_cols = ['ticker', 'weight', 'trade_date']
        missing_cols = [col for col in required_cols if col not in portfolio_df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        return self._clean_portfolio_data(portfolio_df)
    
    def _clean_portfolio_data(self, portfolio_df):
        """Clean and validate portfolio data"""
        # Remove duplicates
        portfolio_df = portfolio_df.drop_duplicates()
        
        # Validate weights sum to 1
        weight_sum = portfolio_df['weight'].sum()
        if abs(weight_sum - 1.0) > 0.01:
            raise ValueError(f"Portfolio weights sum to {weight_sum:.4f}, should be 1.0")
        
        # Handle missing data
        portfolio_df = portfolio_df.dropna(subset=['ticker', 'weight'])
        
        # Add missing metadata
        portfolio_df['asset_class'] = portfolio_df['ticker'].apply(self._classify_asset)
        
        return portfolio_df
    
    def _classify_asset(self, ticker):
        """Classify asset type based on ticker"""
        equity_indicators = ['', '.', '^']
        bond_indicators = ['govt', 'bond', 'corp']
        
        ticker_lower = ticker.lower()
        
        if any(ind in ticker_lower for ind in bond_indicators):
            return 'Bond'
        elif any(ticker.endswith(ind) for ind in equity_indicators):
            return 'Equity'
        else:
            return 'Equity'  # Default assumption
    
    def fetch_market_data(self, tickers, start_date, end_date):
        """Fetch historical price data for tickers"""
        try:
            # For demonstration, using yfinance. In production, use Bloomberg/Refinitiv
            data = yf.download(tickers, start=start_date, end=end_date)['Adj Close']
            return data
        except Exception as e:
            print(f"Error fetching market data: {e}")
            # Return mock data for demonstration
            return self._generate_mock_data(tickers, start_date, end_date)
    
    def _generate_mock_data(self, tickers, start_date, end_date):
        """Generate mock price data for demonstration"""
        dates = pd.date_range(start_date, end_date, freq='D')
        data = {}
        
        for ticker in tickers:
            # Generate realistic random walk
            np.random.seed(hash(ticker) % 10000)
            returns = np.random.normal(0.0005, 0.02, len(dates))
            prices = 100 * np.cumprod(1 + returns)
            data[ticker] = prices
        
        return pd.DataFrame(data, index=dates)
    
    def save_to_database(self, df, table_name):
        """Save DataFrame to SQL database"""
        engine = create_engine(f'sqlite:///{self.db_path}')
        df.to_sql(table_name, engine, if_exists='replace', index=False)