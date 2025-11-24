# src/strategy_checker.py
import pandas as pd
import numpy as np
from .utils import PortfolioConfig

class StrategyChecker:
    def __init__(self, target_weights=None):
        self.config = PortfolioConfig()
        self.target_weights = target_weights or {}
        
    def calculate_strategy_alignment(self, portfolio_weights, benchmark_weights=None):
        """Calculate strategy alignment metrics"""
        alignment_metrics = {}
        
        # Calculate active weights
        if benchmark_weights is not None:
            active_weights = self._calculate_active_weights(portfolio_weights, benchmark_weights)
            alignment_metrics['active_weights'] = active_weights
            
            # Tracking error
            alignment_metrics['tracking_error'] = self._calculate_tracking_error(
                portfolio_weights, benchmark_weights
            )
        
        # Drift analysis
        if self.target_weights:
            drift_metrics = self._calculate_drift_metrics(portfolio_weights)
            alignment_metrics.update(drift_metrics)
        
        # Concentration analysis
        alignment_metrics['concentration'] = self._calculate_concentration(portfolio_weights)
        
        return alignment_metrics
    
    def _calculate_active_weights(self, portfolio_weights, benchmark_weights):
        """Calculate active weights (portfolio - benchmark)"""
        active_weights = {}
        
        for asset, port_weight in portfolio_weights.items():
            bench_weight = benchmark_weights.get(asset, 0)
            active_weights[asset] = port_weight - bench_weight
        
        # Add benchmark assets not in portfolio
        for asset, bench_weight in benchmark_weights.items():
            if asset not in active_weights:
                active_weights[asset] = -bench_weight
        
        return active_weights
    
    def _calculate_tracking_error(self, portfolio_weights, benchmark_weights):
        """Calculate ex-ante tracking error"""
        # Simplified calculation - in practice, use covariance matrix
        active_weights = self._calculate_active_weights(portfolio_weights, benchmark_weights)
        te = np.sqrt(sum(w**2 for w in active_weights.values())) * 0.2  # Assumed volatility
        return te
    
    def _calculate_drift_metrics(self, portfolio_weights):
        """Calculate drift from target strategy"""
        drift_metrics = {}
        total_drift = 0
        
        for asset, current_weight in portfolio_weights.items():
            target_weight = self.target_weights.get(asset, 0)
            drift = abs(current_weight - target_weight)
            total_drift += drift
        
        drift_metrics['total_drift'] = total_drift
        drift_metrics['drift_breaches'] = total_drift > 0.10  # 10% threshold
        
        return drift_metrics
    
    def _calculate_concentration(self, portfolio_weights):
        """Calculate concentration metrics"""
        weights = list(portfolio_weights.values())
        
        concentration = {
            'herfindahl': sum(w**2 for w in weights),
            'top_5_weight': sum(sorted(weights, reverse=True)[:5]),
            'max_weight': max(weights)
        }
        
        return concentration
    
    def generate_alignment_report(self, portfolio_df, benchmark_df=None):
        """Generate comprehensive alignment report"""
        portfolio_weights = dict(zip(portfolio_df['ticker'], portfolio_df['weight']))
        benchmark_weights = None
        
        if benchmark_df is not None:
            benchmark_weights = dict(zip(benchmark_df['ticker'], benchmark_df['weight']))
        
        metrics = self.calculate_strategy_alignment(portfolio_weights, benchmark_weights)
        
        # Generate detailed report
        report = {
            'summary': {
                'tracking_error': metrics.get('tracking_error', 0),
                'total_drift': metrics.get('total_drift', 0),
                'drift_breach': metrics.get('drift_breaches', False)
            },
            'detailed_analysis': metrics
        }
        
        return report