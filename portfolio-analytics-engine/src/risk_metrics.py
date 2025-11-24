# src/risk_metrics.py
import pandas as pd
import numpy as np
from scipy import stats

class RiskMetrics:
    def __init__(self, confidence_level=0.95):
        self.confidence_level = confidence_level
        
    def calculate_var(self, returns, method='historical'):
        """Calculate Value at Risk"""
        if method == 'historical':
            return self._historical_var(returns)
        elif method == 'parametric':
            return self._parametric_var(returns)
        else:
            raise ValueError("Method must be 'historical' or 'parametric'")
    
    def _historical_var(self, returns):
        """Calculate historical VaR"""
        return np.percentile(returns, (1 - self.confidence_level) * 100)
    
    def _parametric_var(self, returns):
        """Calculate parametric VaR (assuming normal distribution)"""
        mean = returns.mean()
        std = returns.std()
        z_score = stats.norm.ppf(1 - self.confidence_level)
        return mean + z_score * std
    
    def calculate_expected_shortfall(self, returns):
        """Calculate Expected Shortfall (CVaR)"""
        var = self.calculate_var(returns, method='historical')
        es = returns[returns <= var].mean()
        return es
    
    def calculate_beta(self, portfolio_returns, benchmark_returns):
        """Calculate beta relative to benchmark"""
        covariance = np.cov(portfolio_returns, benchmark_returns)[0, 1]
        benchmark_variance = np.var(benchmark_returns)
        
        beta = covariance / benchmark_variance if benchmark_variance > 0 else 0
        return beta
    
    def calculate_risk_metrics(self, portfolio_returns, benchmark_returns=None):
        """Calculate comprehensive risk metrics"""
        metrics = {
            'volatility': portfolio_returns.std() * np.sqrt(252),
            'var_95': self.calculate_var(portfolio_returns),
            'expected_shortfall_95': self.calculate_expected_shortfall(portfolio_returns),
            'max_drawdown': self._calculate_max_drawdown(portfolio_returns)
        }
        
        if benchmark_returns is not None:
            metrics['beta'] = self.calculate_beta(portfolio_returns, benchmark_returns)
            metrics['tracking_error'] = (portfolio_returns - benchmark_returns).std() * np.sqrt(252)
            metrics['information_ratio'] = (
                (portfolio_returns.mean() - benchmark_returns.mean()) * 252 / metrics['tracking_error']
                if metrics['tracking_error'] > 0 else 0
            )
        
        return metrics
    
    def _calculate_max_drawdown(self, returns):
        """Calculate maximum drawdown"""
        cumulative = (1 + returns).cumprod()
        rolling_max = cumulative.expanding().max()
        drawdown = (cumulative - rolling_max) / rolling_max
        return drawdown.min()
    
    def risk_decomposition(self, portfolio_weights, covariance_matrix):
        """Decompose risk by asset contribution"""
        portfolio_variance = portfolio_weights.T @ covariance_matrix @ portfolio_weights
        marginal_risk = covariance_matrix @ portfolio_weights / np.sqrt(portfolio_variance)
        risk_contribution = portfolio_weights * marginal_risk
        
        return {
            'total_risk': np.sqrt(portfolio_variance),
            'marginal_risk': marginal_risk,
            'risk_contribution': risk_contribution,
            'percent_contribution': risk_contribution / np.sqrt(portfolio_variance)
        }