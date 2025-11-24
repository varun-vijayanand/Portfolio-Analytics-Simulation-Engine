# tests/test_backtest.py
import pytest
import pandas as pd
import numpy as np
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from backtest_engine import BacktestEngine

class TestBacktestEngine:
    def setup_method(self):
        self.engine = BacktestEngine()
        self.portfolio_weights = {'AAPL': 0.6, 'MSFT': 0.4}
        
        # Create mock price data
        dates = pd.date_range('2020-01-01', '2023-01-01', freq='D')
        np.random.seed(42)
        self.price_data = pd.DataFrame({
            'AAPL': 100 * np.cumprod(1 + np.random.normal(0.001, 0.02, len(dates))),
            'MSFT': 200 * np.cumprod(1 + np.random.normal(0.0008, 0.018, len(dates)))
        }, index=dates)
    
    def test_historical_simulation(self):
        results = self.engine.historical_simulation(
            self.portfolio_weights, 
            self.price_data
        )
        
        assert 'total_return' in results
        assert 'volatility' in results
        assert 'sharpe_ratio' in results
        assert 'max_drawdown' in results
        assert len(results['returns']) > 0
    
    def test_monte_carlo_simulation(self):
        returns_data = self.price_data.pct_change().dropna()
        results = self.engine.monte_carlo_simulation(
            self.portfolio_weights, 
            returns_data, 
            n_simulations=100, 
            days=50
        )
        
        assert 'expected_return' in results
        assert 'value_at_risk_95' in results
        assert 'expected_shortfall_95' in results
        assert results['simulation_paths'].shape[0] == 100

if __name__ == '__main__':
    pytest.main([__file__])