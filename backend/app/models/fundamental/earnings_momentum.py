"""
Earnings Momentum Model
Identifies stocks with positive earnings revisions and acceleration
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional
from app.models.base import FundamentalModel, SignalType


class EarningsMomentumModel(FundamentalModel):
    """
    Earnings Momentum Strategy
    
    Identifies stocks with:
    1. Positive EPS revisions (forward EPS > trailing EPS)
    2. Earnings acceleration (growth rate increasing)
    3. Positive earnings surprises (actual > estimates)
    
    Based on research showing earnings momentum persists.
    """
    
    def __init__(
        self,
        min_eps_growth: float = 10,
        min_revenue_growth: float = 5
    ):
        super().__init__(
            name="Earnings Momentum",
            description="Find stocks with positive earnings revisions and acceleration",
            parameters={
                "min_eps_growth": min_eps_growth,
                "min_revenue_growth": min_revenue_growth
            }
        )
        self.min_eps_growth = min_eps_growth
        self.min_rev_growth = min_revenue_growth
    
    def calculate_scores(
        self,
        price_data: Dict[str, pd.DataFrame],
        fundamental_data: Optional[pd.DataFrame] = None
    ) -> pd.DataFrame:
        if fundamental_data is None or fundamental_data.empty:
            return pd.DataFrame()
        
        df = fundamental_data.copy()
        df = df.dropna(subset=['ticker'])
        
        results = []
        
        for _, row in df.iterrows():
            ticker = row.get('ticker')
            scores = {}
            
            # EPS Revision Score (forward vs trailing)
            forward_eps = row.get('forward_eps')
            trailing_eps = row.get('eps')
            
            if forward_eps is not None and trailing_eps is not None and trailing_eps > 0:
                eps_revision = (forward_eps / trailing_eps - 1) * 100
                if eps_revision > 0:
                    scores['revision'] = min(100, 50 + eps_revision * 2)
                else:
                    scores['revision'] = max(0, 50 + eps_revision * 2)
            else:
                scores['revision'] = 50
                eps_revision = 0
            
            # Earnings Growth Score
            earnings_growth = row.get('earnings_growth')
            if earnings_growth is not None:
                eg_pct = earnings_growth * 100 if abs(earnings_growth) < 2 else earnings_growth
                if eg_pct >= self.min_eps_growth:
                    scores['growth'] = min(100, 50 + eg_pct)
                else:
                    scores['growth'] = max(0, 50 + eg_pct)
            else:
                scores['growth'] = 50
                eg_pct = 0
            
            # Revenue Growth Score
            rev_growth = row.get('revenue_growth')
            if rev_growth is not None:
                rg_pct = rev_growth * 100 if abs(rev_growth) < 2 else rev_growth
                if rg_pct >= self.min_rev_growth:
                    scores['revenue'] = min(100, 50 + rg_pct * 2)
                else:
                    scores['revenue'] = max(0, 50 + rg_pct * 2)
            else:
                scores['revenue'] = 50
                rg_pct = 0
            
            # P/E Compression (Forward P/E < Trailing P/E = positive)
            forward_pe = row.get('forward_pe')
            trailing_pe = row.get('pe_ratio')
            
            if forward_pe and trailing_pe and trailing_pe > 0:
                pe_compression = (trailing_pe / forward_pe - 1) * 100
                scores['pe_compression'] = min(100, max(0, 50 + pe_compression * 3))
            else:
                scores['pe_compression'] = 50
                pe_compression = 0
            
            # Combined score
            total_score = (
                scores.get('revision', 0) * 0.35 +
                scores.get('growth', 0) * 0.30 +
                scores.get('revenue', 0) * 0.20 +
                scores.get('pe_compression', 0) * 0.15
            )
            
            # Determine signal
            if total_score >= 65 and scores.get('revision', 0) > 50:
                signal_type = "BUY"
            elif total_score <= 35:
                signal_type = "SELL"
            else:
                signal_type = "HOLD"
            
            results.append({
                "ticker": ticker,
                "score": total_score,
                "signal_type": signal_type,
                "eps_revision_pct": round(eps_revision, 2),
                "earnings_growth_pct": round(eg_pct, 2),
                "revenue_growth_pct": round(rg_pct, 2),
                "revision_score": round(scores.get('revision', 0), 1)
            })
        
        return pd.DataFrame(results)
