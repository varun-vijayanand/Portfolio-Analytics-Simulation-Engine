import os
try:
    import openai
except:
    openai = None

def _merge(context, keys):
    block = []
    for k in keys:
        block.append(f"{k}: {context.get(k)}")
    return "\n".join(block)

class NarrativeGenerator:
    """Responsible for generating executive summary, market commentary, and risk commentary."""
    
    def __init__(self, model="gpt-4o"):
        self.model = model
        self.api_key = os.environ.get("OPENAI_API_KEY")
        if openai and self.api_key:
            openai.api_key = self.api_key
    
    # ============= EXECUTIVE ==============
    def generate_executive(self, context):
        if openai and self.api_key:
            return self._ask_llm(
                "Write an institutional-grade portfolio executive summary:\n" +
                _merge(context, ["portfolio_info", "historical_results", "risk_metrics", "factor_exposures"])
            )
        return self._fallback_executive(context)
    
    # ============= MARKET ==============
    def generate_market(self, context):
        if openai and self.api_key:
            return self._ask_llm(
                "Write a market and benchmark commentary:\n" +
                _merge(context, ["benchmarks", "market_data", "factor_exposures"])
            )
        return "Market Overview: Benchmarks and conditions are stable with moderate volatility."
    
    # ============= RISK ==============
    def generate_risk(self, context):
        return "\n".join([f"{k}: {v}" for k,v in context.get("risk_metrics", {}).items()])
    
    # ============= UTILITIES ==============
    def _ask_llm(self, prompt):
        resp = openai.ChatCompletion.create(
            model=self.model,
            messages=[{"role":"user","content":prompt}],
            temperature=0.2
        )
        return resp.choices[0].message.content
    
    def _fallback_executive(self, context):
        h = context.get("historical_results", {})
        r = context.get("risk_metrics", {})
        return f"""
Executive Summary:
The portfolio delivered {h.get('annual_return', 0):.2%} annualized return with 
volatility {r.get('volatility', 0):.2%}.  
Risk-adjusted performance remains aligned with factor expectations.
"""
