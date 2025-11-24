# src/backtest_engine.py
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class BacktestEngine:
    def __init__(self, lookback_period=252*5):  # 5 years default
        self.lookback_period = lookback_period
        
    def historical_simulation(self, portfolio_weights, price_data, start_date=None, end_date=None):
        """Run historical simulation"""
        if start_date is None:
            start_date = price_data.index[-self.lookback_period]
        if end_date is None:
            end_date = price_data.index[-1]
        
        # Filter data for simulation period
        sim_data = price_data.loc[start_date:end_date]
        
        # Calculate returns
        returns = sim_data.pct_change().dropna()
        
        # Calculate portfolio returns
        portfolio_returns = self._calculate_portfolio_returns(returns, portfolio_weights)
        
        # Calculate performance metrics
        results = self._calculate_performance_metrics(portfolio_returns, returns)
        
        return results
    
    def _calculate_portfolio_returns(self, returns, portfolio_weights):
        """Calculate portfolio returns from asset returns and weights"""
        # Align weights with return columns
        aligned_weights = np.array([portfolio_weights.get(col, 0) for col in returns.columns])
        
        # Calculate portfolio returns
        portfolio_returns = returns.dot(aligned_weights)
        
        return portfolio_returns
    
    def _calculate_performance_metrics(self, portfolio_returns, asset_returns):
        """Calculate comprehensive performance metrics"""
        total_return = (1 + portfolio_returns).prod() - 1
        annual_return = (1 + total_return) ** (252/len(portfolio_returns)) - 1
        volatility = portfolio_returns.std() * np.sqrt(252)
        sharpe_ratio = (annual_return - 0.02) / volatility if volatility > 0 else 0
        
        # Maximum drawdown
        cumulative_returns = (1 + portfolio_returns).cumprod()
        rolling_max = cumulative_returns.expanding().max()
        drawdowns = (cumulative_returns - rolling_max) / rolling_max
        max_drawdown = drawdowns.min()
        
        results = {
            'total_return': total_return,
            'annual_return': annual_return,
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'returns': portfolio_returns,
            'cumulative_returns': cumulative_returns
        }
        
        return results
    
    def monte_carlo_simulation(self, portfolio_weights, historical_returns, n_simulations=1000, days=252):
        """Run Monte Carlo simulation for forward-looking analysis"""
        # Estimate parameters from historical data
        mean_returns = historical_returns.mean()
        cov_matrix = historical_returns.cov()
        
        aligned_weights = np.array([portfolio_weights.get(col, 0) for col in historical_returns.columns])
        
        simulations = []
        
        for _ in range(n_simulations):
            # Generate correlated random returns
            simulated_returns = np.random.multivariate_normal(mean_returns, cov_matrix, days)
            
            # Calculate portfolio performance
            portfolio_path = np.cumprod(1 + simulated_returns.dot(aligned_weights))
            simulations.append(portfolio_path)
        
        simulations = np.array(simulations)
        
        # Calculate statistics
        final_values = simulations[:, -1]
        
        mc_results = {
            'expected_return': np.mean(final_values) - 1,
            'value_at_risk_95': np.percentile(final_values, 5) - 1,
            'expected_shortfall_95': final_values[final_values <= np.percentile(final_values, 5)].mean() - 1,
            'simulation_paths': simulations
        }
        
        return mc_results
    
    def stress_test(self, portfolio_weights, price_data, stress_periods):
        """Run stress tests for specific historical periods"""
        stress_results = {}
        
        for period_name, (start_date, end_date) in stress_periods.items():
            period_data = price_data.loc[start_date:end_date]
            period_returns = period_data.pct_change().dropna()
            
            portfolio_stress_returns = self._calculate_portfolio_returns(period_returns, portfolio_weights)
            
            stress_results[period_name] = {
                'total_return': (1 + portfolio_stress_returns).prod() - 1,
                'max_drawdown': self._calculate_max_drawdown(portfolio_stress_returns),
                'volatility': portfolio_stress_returns.std() * np.sqrt(252)
            }
        
        return stress_results
    
    def _calculate_max_drawdown(self, returns):
        """Calculate maximum drawdown for a return series"""
        cumulative = (1 + returns).cumprod()
        rolling_max = cumulative.expanding().max()
        drawdown = (cumulative - rolling_max) / rolling_max
        return drawdown.min()