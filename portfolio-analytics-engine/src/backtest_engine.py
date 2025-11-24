# src/backtest_engine.py
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class BacktestEngine:
    def __init__(self, lookback_period=252 * 5):  # default: 5 years
        self.lookback_period = lookback_period

    def historical_simulation(self, portfolio_weights, price_data, start_date=None, end_date=None):
        """
        Run historical simulation with automatic clamping of lookback period
        if the available price_data is shorter.
        """
        if price_data is None or len(price_data) < 2:
            raise ValueError("Price data is empty or insufficient for backtesting.")

        # Determine simulation window
        if start_date is None:
            available_len = len(price_data)
            lookback = min(self.lookback_period, available_len - 1)
            start_date = price_data.index[-lookback]

        if end_date is None:
            end_date = price_data.index[-1]

        # Slice simulation data
        sim_data = price_data.loc[start_date:end_date]

        # Compute asset returns
        returns = sim_data.pct_change().dropna()

        if returns.empty:
            raise ValueError("Asset returns are empty after pct_change. Not enough valid price data.")

        # Compute portfolio returns
        portfolio_returns = self._calculate_portfolio_returns(returns, portfolio_weights)

        # Compute performance metrics
        results = self._calculate_performance_metrics(portfolio_returns)

        # Add raw return series
        results["returns"] = portfolio_returns
        results["cumulative_returns"] = (1 + portfolio_returns).cumprod()

        return results

    def _calculate_portfolio_returns(self, returns, portfolio_weights):
        """
        Multiply asset returns by aligned portfolio weights.
        Missing weights default to 0.
        """
        cols = returns.columns
        aligned_weights = np.array([portfolio_weights.get(asset, 0) for asset in cols])

        # Normalize weights if they don't sum to 1
        if aligned_weights.sum() != 1:
            aligned_weights = aligned_weights / aligned_weights.sum()

        return returns.dot(aligned_weights)

    def _calculate_performance_metrics(self, portfolio_returns):
        """
        Compute total return, annualized return, volatility, Sharpe ratio, and max drawdown.
        Uses corrected annualization formulas.
        """
        if portfolio_returns.empty:
            return {
                "total_return": 0,
                "annual_return": 0,
                "volatility": 0,
                "sharpe_ratio": 0,
                "max_drawdown": 0
            }

        total_return = (1 + portfolio_returns).prod() - 1
        mean_daily_return = portfolio_returns.mean()

        # Annualized return using correct formula
        annual_return = (1 + mean_daily_return) ** 252 - 1

        # Annualized volatility
        volatility = portfolio_returns.std() * np.sqrt(252)

        sharpe_ratio = 0
        if volatility > 0:
            sharpe_ratio = (annual_return - 0.02) / volatility  # 2% RF rate

        # Max drawdown
        cumulative = (1 + portfolio_returns).cumprod()
        rolling_max = cumulative.expanding().max()
        drawdown = (cumulative - rolling_max) / rolling_max
        max_drawdown = drawdown.min()

        return {
            "total_return": total_return,
            "annual_return": annual_return,
            "volatility": volatility,
            "sharpe_ratio": sharpe_ratio,
            "max_drawdown": max_drawdown
        }

    def monte_carlo_simulation(self, portfolio_weights, historical_returns, n_simulations=1000, days=252):
        """
        Forward-looking Monte Carlo simulations using mean + covariance of asset returns.
        """
        if historical_returns is None or len(historical_returns) < 2:
            raise ValueError("Historical returns are empty or insufficient for Monte Carlo.")

        mean_returns = historical_returns.mean()
        cov_matrix = historical_returns.cov()

        cols = historical_returns.columns
        aligned_weights = np.array([portfolio_weights.get(asset, 0) for asset in cols])

        if aligned_weights.sum() != 1:
            aligned_weights = aligned_weights / aligned_weights.sum()

        simulations = []

        for _ in range(n_simulations):
            simulated_returns = np.random.multivariate_normal(mean_returns, cov_matrix, days)
            portfolio_path = np.cumprod(1 + simulated_returns.dot(aligned_weights))
            simulations.append(portfolio_path)

        simulations = np.array(simulations)
        final_values = simulations[:, -1]

        return {
            "expected_return": np.mean(final_values) - 1,
            "value_at_risk_95": np.percentile(final_values, 5) - 1,
            "expected_shortfall_95": final_values[final_values <= np.percentile(final_values, 5)].mean() - 1,
            "simulation_paths": simulations
        }

    def stress_test(self, portfolio_weights, price_data, stress_periods):
        """
        Evaluate returns during predefined stress periods (e.g. 2008 crash, COVID crash).
        """
        results = {}

        for period_name, (start_date, end_date) in stress_periods.items():
            period_data = price_data.loc[start_date:end_date]
            period_returns = period_data.pct_change().dropna()

            if period_returns.empty:
                results[period_name] = {
                    "total_return": 0,
                    "max_drawdown": 0,
                    "volatility": 0
                }
                continue

            pr = self._calculate_portfolio_returns(period_returns, portfolio_weights)

            results[period_name] = {
                "total_return": (1 + pr).prod() - 1,
                "max_drawdown": self._calculate_max_drawdown(pr),
                "volatility": pr.std() * np.sqrt(252)
            }

        return results

    def _calculate_max_drawdown(self, returns):
        """Utility for max drawdown."""
        cumulative = (1 + returns).cumprod()
        rolling_max = cumulative.expanding().max()
        drawdown = (cumulative - rolling_max) / rolling_max
        return drawdown.min()
