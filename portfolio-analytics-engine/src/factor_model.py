# src/factor_model.py
import pandas as pd
import numpy as np
import statsmodels.api as sm
from .utils import PortfolioConfig

class FactorModel:
    def __init__(self):
        self.config = PortfolioConfig()
        
    def calculate_factor_exposures(self, portfolio_weights, factor_data):
        """Calculate portfolio exposures to factors"""
        # Align portfolio weights with factor data
        common_assets = set(portfolio_weights.keys()) & set(factor_data.columns)
        
        if not common_assets:
            raise ValueError("No common assets between portfolio and factor data")
        
        # Calculate weighted average factor exposures
        factor_exposures = {}
        
        for factor in factor_data.index:
            weighted_exposure = 0
            for asset in common_assets:
                weighted_exposure += portfolio_weights[asset] * factor_data.loc[factor, asset]
            
            factor_exposures[factor] = weighted_exposure
        
        return factor_exposures
    
    def fama_french_analysis(self, portfolio_returns, factor_returns):
        """Run Fama-French regression analysis"""
        # Ensure alignment
        common_dates = portfolio_returns.index.intersection(factor_returns.index)
        portfolio_aligned = portfolio_returns.loc[common_dates]
        factors_aligned = factor_returns.loc[common_dates]
        
        # Add constant for alpha
        X = sm.add_constant(factors_aligned)
        y = portfolio_aligned
        
        model = sm.OLS(y, X).fit()
        
        return {
            'alpha': model.params['const'],
            'factor_exposures': model.params.drop('const').to_dict(),
            'r_squared': model.rsquared,
            't_stats': model.tvalues.to_dict(),
            'p_values': model.pvalues.to_dict()
        }
    
    def generate_factor_data(self, tickers):
        """Generate mock factor data for demonstration"""
        # In production, this would fetch from commercial data providers
        np.random.seed(42)
        
        factors = ['Value', 'Momentum', 'Size', 'Quality', 'Low_Vol']
        factor_data = pd.DataFrame(
            np.random.normal(0, 1, (len(factors), len(tickers))),
            index=factors,
            columns=tickers
        )
        
        return factor_data