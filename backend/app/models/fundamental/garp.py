"""
GARP (Growth at Reasonable Price) Model
Peter Lynch's investment approach
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional
from app.models.base import FundamentalModel, SignalType


class GARPModel(FundamentalModel):
    """
    Growth at Reasonable Price (GARP)
    
    Made famous by Peter Lynch, GARP combines:
    1. Growth characteristics (earnings, revenue growth)
    2. Value characteristics (reasonable P/E)
    3. PEG Ratio as the key metric (P/E / Growth Rate)
    
    PEG < 1.0 = undervalued growth
    PEG 1.0-2.0 = fairly valued
    PEG > 2.0 = overvalued
    """
    
    def __init__(
        self,
        max_peg: float = 1.5,
        min_growth: float = 10,
        max_pe: float = 40
    ):
        super().__init__(
            name="GARP",
            description="Growth at Reasonable Price - Peter Lynch's PEG ratio approach",
            parameters={
                "max_peg": max_peg,
                "min_growth": min_growth,
                "max_pe": max_pe
            }
        )
        self.max_peg = max_peg
        self.min_growth = min_growth
        self.max_pe = max_pe
    
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
            
            # Get PEG ratio (or calculate it)
            peg = row.get('peg_ratio')
            pe = row.get('pe_ratio')
            growth = row.get('earnings_growth')
            
            # Calculate PEG if not available
            if peg is None and pe is not None and growth is not None:
                growth_pct = growth * 100 if abs(growth) < 2 else growth
                if growth_pct > 0:
                    peg = pe / growth_pct
            
            # Growth rate
            if growth is not None:
                growth_pct = growth * 100 if abs(growth) < 2 else growth
            else:
                growth_pct = 0
            
            # Calculate score components
            scores = {}
            
            # PEG Score (lower is better)
            if peg is not None and peg > 0:
                if peg < 0.5:
                    scores['peg'] = 100
                elif peg < 1.0:
                    scores['peg'] = 90
                elif peg < self.max_peg:
                    scores['peg'] = 70
                elif peg < 2.0:
                    scores['peg'] = 50
                else:
                    scores['peg'] = 30
            else:
                scores['peg'] = 40
            
            # Growth Score
            if growth_pct >= self.min_growth:
                scores['growth'] = min(100, 50 + growth_pct * 2)
            elif growth_pct > 0:
                scores['growth'] = 30 + growth_pct * 2
            else:
                scores['growth'] = max(0, 30 + growth_pct)
            
            # P/E Score (reasonable, not too high)
            if pe is not None:
                if 5 <= pe <= 15:
                    scores['pe'] = 90
                elif 15 < pe <= 25:
                    scores['pe'] = 70
                elif 25 < pe <= self.max_pe:
                    scores['pe'] = 50
                elif pe > self.max_pe:
                    scores['pe'] = 30
                else:
                    scores['pe'] = 40
            else:
                scores['pe'] = 50
            
            # Combined score
            total_score = (
                scores.get('peg', 0) * 0.50 +
                scores.get('growth', 0) * 0.30 +
                scores.get('pe', 0) * 0.20
            )
            
            # Determine signal
            if total_score >= 70 and growth_pct >= self.min_growth:
                signal_type = "BUY"
            elif total_score <= 40 or (peg and peg > 2.5):
                signal_type = "SELL"
            else:
                signal_type = "HOLD"
            
            results.append({
                "ticker": ticker,
                "score": total_score,
                "signal_type": signal_type,
                "peg_ratio": round(peg, 2) if peg else None,
                "pe_ratio": round(pe, 2) if pe else None,
                "growth_rate": round(growth_pct, 2),
                "peg_score": round(scores.get('peg', 0), 1)
            })
        
        return pd.DataFrame(results)
