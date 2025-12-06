"""
Magic Formula Model
Joel Greenblatt's investment strategy from "The Little Book That Beats the Market"
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional
from app.models.base import FundamentalModel, SignalType


class MagicFormulaModel(FundamentalModel):
    """
    Joel Greenblatt's Magic Formula
    
    Combines two factors:
    1. Earnings Yield (EBIT / Enterprise Value) - higher is better
    2. Return on Capital (EBIT / (Net Fixed Assets + Working Capital)) - higher is better
    
    Stocks are ranked by each factor, then combined ranks are used.
    Buy stocks with lowest combined rank (best value + best quality).
    """
    
    def __init__(
        self,
        earnings_yield_weight: float = 0.5,
        roc_weight: float = 0.5,
        min_market_cap: float = 50_000_000  # $50M minimum
    ):
        super().__init__(
            name="Magic Formula",
            description="Joel Greenblatt's value + quality combination (Earnings Yield + ROC)",
            parameters={
                "earnings_yield_weight": earnings_yield_weight,
                "roc_weight": roc_weight,
                "min_market_cap": min_market_cap
            }
        )
        self.ey_weight = earnings_yield_weight
        self.roc_weight = roc_weight
        self.min_market_cap = min_market_cap
    
    def calculate_scores(
        self,
        price_data: Dict[str, pd.DataFrame],
        fundamental_data: Optional[pd.DataFrame] = None
    ) -> pd.DataFrame:
        if fundamental_data is None or fundamental_data.empty:
            return pd.DataFrame()
        
        df = fundamental_data.copy()
        df = df.dropna(subset=['ticker'])
        
        # Filter by market cap
        if 'market_cap' in df.columns:
            df = df[df['market_cap'] >= self.min_market_cap]
        
        if df.empty:
            return pd.DataFrame()
        
        # Calculate Earnings Yield proxy (use inverse of P/E as proxy for EBIT/EV)
        if 'pe_ratio' in df.columns:
            df['earnings_yield'] = 100 / df['pe_ratio'].replace(0, np.nan)
            df['earnings_yield'] = df['earnings_yield'].clip(-50, 100)  # Cap extremes
        else:
            df['earnings_yield'] = 0
        
        # Calculate ROC proxy (use ROA or ROE)
        if 'roa' in df.columns:
            df['roc'] = df['roa'] * 100 if df['roa'].max() < 1 else df['roa']
        elif 'roe' in df.columns:
            df['roc'] = df['roe'] * 100 if df['roe'].max() < 1 else df['roe']
        else:
            df['roc'] = 0
        
        # Rank both factors (higher is better for both)
        df['ey_rank'] = df['earnings_yield'].rank(pct=True, ascending=True) * 100
        df['roc_rank'] = df['roc'].rank(pct=True, ascending=True) * 100
        
        # Combined Magic Formula score
        df['score'] = df['ey_rank'] * self.ey_weight + df['roc_rank'] * self.roc_weight
        
        # Determine signals
        buy_threshold = df['score'].quantile(0.8)
        sell_threshold = df['score'].quantile(0.2)
        
        results = []
        for _, row in df.iterrows():
            score = row['score']
            if score >= buy_threshold:
                signal_type = "BUY"
            elif score <= sell_threshold:
                signal_type = "SELL"
            else:
                signal_type = "HOLD"
            
            results.append({
                "ticker": row['ticker'],
                "score": score,
                "signal_type": signal_type,
                "earnings_yield": round(row['earnings_yield'], 2),
                "roc": round(row['roc'], 2),
                "ey_rank": round(row['ey_rank'], 1),
                "roc_rank": round(row['roc_rank'], 1)
            })
        
        return pd.DataFrame(results)
