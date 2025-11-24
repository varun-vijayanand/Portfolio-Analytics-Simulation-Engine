# src/sql_queries.py
import sqlite3
import pandas as pd

class PortfolioQueries:
    def __init__(self, db_path='data/portfolio.db'):
        self.db_path = db_path
    
    def execute_query(self, query, params=None):
        """Execute SQL query and return results"""
        conn = sqlite3.connect(self.db_path)
        try:
            if params:
                result = pd.read_sql_query(query, conn, params=params)
            else:
                result = pd.read_sql_query(query, conn)
            return result
        finally:
            conn.close()
    
    def get_portfolio_summary(self):
        """Get portfolio summary statistics"""
        query = """
        SELECT 
            COUNT(*) as num_positions,
            SUM(weight) as total_weight,
            AVG(weight) as avg_weight,
            MAX(weight) as max_weight,
            MIN(weight) as min_weight
        FROM portfolio_positions
        """
        return self.execute_query(query)
    
    def get_asset_class_breakdown(self):
        """Get portfolio breakdown by asset class"""
        query = """
        SELECT 
            asset_class,
            SUM(weight) as total_weight,
            COUNT(*) as num_positions
        FROM portfolio_positions
        GROUP BY asset_class
        ORDER BY total_weight DESC
        """
        return self.execute_query(query)
    
    def get_largest_positions(self, top_n=10):
        """Get largest portfolio positions"""
        query = """
        SELECT 
            ticker,
            weight,
            asset_class
        FROM portfolio_positions
        ORDER BY weight DESC
        LIMIT ?
        """
        return self.execute_query(query, (top_n,))
    
    def detect_data_gaps(self, start_date, end_date):
        """Detect missing price data in the time series"""
        query = """
        WITH date_range AS (
            SELECT date FROM price_data 
            WHERE date BETWEEN ? AND ?
            GROUP BY date
        ),
        expected_dates AS (
            SELECT DISTINCT date FROM date_range
        ),
        actual_dates AS (
            SELECT DISTINCT date FROM price_data 
            WHERE date BETWEEN ? AND ?
        )
        SELECT 
            ed.date as missing_date
        FROM expected_dates ed
        LEFT JOIN actual_dates ad ON ed.date = ad.date
        WHERE ad.date IS NULL
        """
        return self.execute_query(query, (start_date, end_date, start_date, end_date))