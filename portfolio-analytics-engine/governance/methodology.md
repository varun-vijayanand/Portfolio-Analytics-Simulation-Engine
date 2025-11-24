# Analytical Methodology

## Risk Metrics Calculation

### Value at Risk (VaR)
- **Historical VaR**: 95th percentile of historical returns
- **Parametric VaR**: Mean + Z-score * Standard Deviation
- **Confidence Level**: 95% (Z-score = 1.645)

### Expected Shortfall (CVaR)
- Average of returns beyond VaR threshold
- More conservative than VaR

### Factor Exposures
Based on Fama-French 5-factor model:
1. **Market Factor** (MKT)
2. **Size Factor** (SMB - Small Minus Big)
3. **Value Factor** (HML - High Minus Low)
4. **Profitability Factor** (RMW - Robust Minus Weak)
5. **Investment Factor** (CMA - Conservative Minus Aggressive)

## Backtesting Methodology

### Historical Simulation
- Lookback period: 5 years (1260 trading days)
- Rebalancing: Quarterly
- Transaction costs: 10 basis points

### Monte Carlo Simulation
- Number of simulations: 10,000
- Time horizon: 252 days (1 year)
- Return distribution: Multivariate normal

## Data Validation Rules
1. Portfolio weights must sum to 1.0 ± 0.01
2. No negative weights unless shorting allowed
3. All tickers must have valid price data
4. No duplicate positions