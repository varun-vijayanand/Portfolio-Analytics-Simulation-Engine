# src/utils.py
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class PortfolioConfig:
    """Configuration settings for the portfolio engine"""
    BENCHMARKS = {
        'US_Equity': 'SPY',
        'Global_Equity': 'ACWI',
        'Bonds': 'AGG'
    }
    
    FACTOR_DEFINITIONS = {
        'Value': ['B/P', 'E/P', 'S/P'],
        'Momentum': ['12M_Return', '1M_Return'],
        'Size': ['Market_Cap'],
        'Quality': ['ROE', 'ROA', 'Leverage'],
        'Low_Vol': ['Volatility_12M']
    }
    
    RISK_FREE_RATE = 0.02  # 2% annual