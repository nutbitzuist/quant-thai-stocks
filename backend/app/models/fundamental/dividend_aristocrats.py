"""
Dividend Aristocrats Model
Identifies high-quality dividend payers
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional
from app.models.base import FundamentalModel, SignalType


class DividendAristocratsModel(FundamentalModel):
    """
    Dividend Aristocrats Strategy
    
    Identifies stocks with:
    1. High dividend yield
    2. Sustainable payout ratio (not too high)
    3. Strong financials to maintain dividends
    
    Real Dividend Aristocrats have 25+ years of dividend increases,
    but we use available metrics as proxies.
    """
    
    def __init__(
        self,
        min_dividend_yield: float = 2.0,
        max_payout_ratio: float = 80,
        min_roe: float = 10
    ):
        super().__init__(
            name="Dividend Aristocrats",
            description="Find quality dividend stocks with sustainable payouts",
            parameters={
                "min_dividend_yield": min_dividend_yield,
                "max_payout_ratio": max_payout_ratio,
                "min_roe": min_roe
            }
        )
        self.min_div_yield = min_dividend_yield
        self.max_payout = max_payout_ratio
        self.min_roe = min_roe
    
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
            
            # Dividend Yield Score (higher is better, up to a point)
            div_yield = row.get('dividend_yield')
            if div_yield is not None:
                div_yield_pct = div_yield * 100 if div_yield < 1 else div_yield
                if div_yield_pct >= self.min_div_yield:
                    # Sweet spot is 3-6%, above 8% might be unsustainable
                    if div_yield_pct <= 6:
                        scores['yield'] = 60 + div_yield_pct * 5
                    elif div_yield_pct <= 8:
                        scores['yield'] = 80
                    else:
                        scores['yield'] = 70  # Very high yield might be risky
                else:
                    scores['yield'] = div_yield_pct * 10
            else:
                scores['yield'] = 0
            
            # Payout Ratio Score (lower is better, but not too low)
            payout = row.get('payout_ratio')
            if payout is not None:
                payout_pct = payout * 100 if payout < 2 else payout
                if 20 <= payout_pct <= self.max_payout:
                    scores['payout'] = 80 - abs(payout_pct - 50)  # 50% is ideal
                elif payout_pct > self.max_payout:
                    scores['payout'] = 30  # Too high, unsustainable
                else:
                    scores['payout'] = 40  # Too low, not committed
            else:
                scores['payout'] = 50  # Unknown
            
            # Quality Score (ROE)
            roe = row.get('roe')
            if roe is not None:
                roe_pct = roe * 100 if abs(roe) < 1 else roe
                if roe_pct >= self.min_roe:
                    scores['quality'] = min(100, 50 + roe_pct * 2)
                else:
                    scores['quality'] = max(0, roe_pct * 3)
            else:
                scores['quality'] = 50
            
            # Financial Health (low debt)
            de = row.get('debt_to_equity')
            if de is not None:
                if de < 50:
                    scores['health'] = 80
                elif de < 100:
                    scores['health'] = 60
                else:
                    scores['health'] = 40
            else:
                scores['health'] = 50
            
            # Combined score
            total_score = (
                scores.get('yield', 0) * 0.35 +
                scores.get('payout', 0) * 0.20 +
                scores.get('quality', 0) * 0.25 +
                scores.get('health', 0) * 0.20
            )
            
            # Determine signal
            if total_score >= 70 and scores.get('yield', 0) > 30:
                signal_type = "BUY"
            elif total_score <= 40:
                signal_type = "SELL"
            else:
                signal_type = "HOLD"
            
            results.append({
                "ticker": ticker,
                "score": total_score,
                "signal_type": signal_type,
                "dividend_yield": round(div_yield * 100, 2) if div_yield and div_yield < 1 else div_yield,
                "payout_ratio": payout,
                "roe": roe,
                "yield_score": round(scores.get('yield', 0), 1),
                "quality_score": round(scores.get('quality', 0), 1)
            })
        
        return pd.DataFrame(results)
