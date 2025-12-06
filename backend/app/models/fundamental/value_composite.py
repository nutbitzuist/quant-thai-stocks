"""
Value Composite Model
Multi-factor value scoring based on classic valuation metrics
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional
from app.models.base import FundamentalModel, SignalType


class ValueCompositeModel(FundamentalModel):
    """
    Value Composite Score
    
    Combines multiple valuation metrics:
    - P/E Ratio (lower = better)
    - P/B Ratio (lower = better)
    - P/S Ratio (lower = better)
    - Dividend Yield (higher = better)
    
    Filters out extreme values and ranks stocks by composite score.
    """
    
    def __init__(
        self,
        pe_weight: float = 0.35,
        pb_weight: float = 0.30,
        ps_weight: float = 0.20,
        div_weight: float = 0.15,
        max_pe: float = 50,
        max_pb: float = 10,
        min_pe: float = 0
    ):
        super().__init__(
            name="Value Composite",
            description="Find undervalued stocks using P/E, P/B, P/S, and dividend yield",
            parameters={
                "pe_weight": pe_weight,
                "pb_weight": pb_weight,
                "ps_weight": ps_weight,
                "div_weight": div_weight,
                "max_pe": max_pe,
                "max_pb": max_pb,
                "min_pe": min_pe
            }
        )
        self.pe_weight = pe_weight
        self.pb_weight = pb_weight
        self.ps_weight = ps_weight
        self.div_weight = div_weight
        self.max_pe = max_pe
        self.max_pb = max_pb
        self.min_pe = min_pe
    
    def calculate_scores(
        self,
        price_data: Dict[str, pd.DataFrame],
        fundamental_data: Optional[pd.DataFrame] = None
    ) -> pd.DataFrame:
        if fundamental_data is None or fundamental_data.empty:
            return pd.DataFrame()
        
        df = fundamental_data.copy()
        df = df.dropna(subset=['ticker'])
        
        # Apply filters
        if 'pe_ratio' in df.columns:
            df = df[(df['pe_ratio'] > self.min_pe) | df['pe_ratio'].isna()]
            df = df[(df['pe_ratio'] < self.max_pe) | df['pe_ratio'].isna()]
        
        if 'pb_ratio' in df.columns:
            df = df[(df['pb_ratio'] < self.max_pb) | df['pb_ratio'].isna()]
        
        if df.empty:
            return pd.DataFrame()
        
        # Calculate percentile ranks (inverted - lower value = higher rank for valuation)
        scores = pd.DataFrame()
        scores['ticker'] = df['ticker']
        
        if 'pe_ratio' in df.columns and df['pe_ratio'].notna().any():
            # Lower P/E = higher score
            scores['pe_rank'] = 100 - df['pe_ratio'].rank(pct=True) * 100
        else:
            scores['pe_rank'] = 50
        
        if 'pb_ratio' in df.columns and df['pb_ratio'].notna().any():
            scores['pb_rank'] = 100 - df['pb_ratio'].rank(pct=True) * 100
        else:
            scores['pb_rank'] = 50
        
        if 'ps_ratio' in df.columns and df['ps_ratio'].notna().any():
            scores['ps_rank'] = 100 - df['ps_ratio'].rank(pct=True) * 100
        else:
            scores['ps_rank'] = 50
        
        if 'dividend_yield' in df.columns and df['dividend_yield'].notna().any():
            # Higher dividend = higher score
            scores['div_rank'] = df['dividend_yield'].rank(pct=True) * 100
        else:
            scores['div_rank'] = 50
        
        # Fill NaN with neutral score
        scores = scores.fillna(50)
        
        # Calculate composite score
        scores['score'] = (
            scores['pe_rank'] * self.pe_weight +
            scores['pb_rank'] * self.pb_weight +
            scores['ps_rank'] * self.ps_weight +
            scores['div_rank'] * self.div_weight
        )
        
        # Determine signals
        buy_threshold = scores['score'].quantile(0.8)
        sell_threshold = scores['score'].quantile(0.2)
        
        def get_signal(score):
            if score >= buy_threshold:
                return "BUY"
            elif score <= sell_threshold:
                return "SELL"
            return "HOLD"
        
        scores['signal_type'] = scores['score'].apply(get_signal)
        
        # Add original metrics for reference
        scores = scores.merge(
            df[['ticker', 'pe_ratio', 'pb_ratio', 'ps_ratio', 'dividend_yield']],
            on='ticker',
            how='left'
        )
        
        return scores
