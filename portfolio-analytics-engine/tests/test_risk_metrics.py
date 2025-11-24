# tests/test_risk_metrics.py
import pytest
import pandas as pd
import numpy as np
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from risk_metrics import RiskMetrics

class TestRiskMetrics:
    def setup_method(self):
        self.risk_metrics = RiskMetrics()
        np.random.seed(42)
        self.returns = pd.Series(np.random.normal(0.001, 0.02, 1000))
    
    def test_var_calculation(self):
        historical_var = self.risk_metrics.calculate_var(self.returns, 'historical')
        parametric_var = self.risk_metrics.calculate_var(self.returns, 'parametric')
        
        assert historical_var < 0  # VaR should typically be negative
        assert parametric_var < 0
    
    def test_expected_shortfall(self):
        es = self.risk_metrics.calculate_expected_shortfall(self.returns)
        var = self.risk_metrics.calculate_var(self.returns, 'historical')
        
        assert es < var  # ES should be more negative than VaR
    
    def test_comprehensive_risk_metrics(self):
        benchmark_returns = pd.Series(np.random.normal(0.0008, 0.015, 1000))
        metrics = self.risk_metrics.calculate_risk_metrics(self.returns, benchmark_returns)
        
        required_metrics = ['volatility', 'var_95', 'expected_shortfall_95', 'max_drawdown', 'beta']
        for metric in required_metrics:
            assert metric in metrics

if __name__ == '__main__':
    pytest.main([__file__])