"""
Quality Score Model
Ranks stocks based on profitability and financial health
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional
from app.models.base import FundamentalModel, SignalType


class QualityScoreModel(FundamentalModel):
    """
    Quality Score
    
    Identifies high-quality companies based on:
    - Return on Equity (ROE)
    - Return on Assets (ROA)  
    - Profit Margin
    - Operating Margin
    - Debt to Equity (lower = better)
    - Current Ratio (higher = better)
    """
    
    def __init__(
        self,
        roe_weight: float = 0.25,
        roa_weight: float = 0.15,
        profit_margin_weight: float = 0.20,
        operating_margin_weight: float = 0.15,
        debt_weight: float = 0.15,
        current_ratio_weight: float = 0.10
    ):
        super().__init__(
            name="Quality Score",
            description="Find high-quality stocks based on ROE, margins, and financial health",
            parameters={
                "roe_weight": roe_weight,
                "roa_weight": roa_weight,
                "profit_margin_weight": profit_margin_weight,
                "operating_margin_weight": operating_margin_weight,
                "debt_weight": debt_weight,
                "current_ratio_weight": current_ratio_weight
            }
        )
        self.roe_weight = roe_weight
        self.roa_weight = roa_weight
        self.profit_margin_weight = profit_margin_weight
        self.operating_margin_weight = operating_margin_weight
        self.debt_weight = debt_weight
        self.current_ratio_weight = current_ratio_weight
    
    def calculate_scores(
        self,
        price_data: Dict[str, pd.DataFrame],
        fundamental_data: Optional[pd.DataFrame] = None
    ) -> pd.DataFrame:
        if fundamental_data is None or fundamental_data.empty:
            return pd.DataFrame()
        
        df = fundamental_data.copy()
        df = df.dropna(subset=['ticker'])
        
        if df.empty:
            return pd.DataFrame()
        
        scores = pd.DataFrame()
        scores['ticker'] = df['ticker']
        
        # ROE (higher = better)
        if 'roe' in df.columns and df['roe'].notna().any():
            roe_vals = df['roe'].fillna(0)
            # Convert to percentage if needed
            roe_vals = roe_vals.apply(lambda x: x * 100 if abs(x) < 1 else x)
            scores['roe_rank'] = roe_vals.rank(pct=True) * 100
            scores['roe'] = roe_vals
        else:
            scores['roe_rank'] = 50
            scores['roe'] = 0
        
        # ROA (higher = better)
        if 'roa' in df.columns and df['roa'].notna().any():
            roa_vals = df['roa'].fillna(0)
            roa_vals = roa_vals.apply(lambda x: x * 100 if abs(x) < 1 else x)
            scores['roa_rank'] = roa_vals.rank(pct=True) * 100
            scores['roa'] = roa_vals
        else:
            scores['roa_rank'] = 50
            scores['roa'] = 0
        
        # Profit Margin (higher = better)
        if 'profit_margin' in df.columns and df['profit_margin'].notna().any():
            pm_vals = df['profit_margin'].fillna(0)
            pm_vals = pm_vals.apply(lambda x: x * 100 if abs(x) < 1 else x)
            scores['pm_rank'] = pm_vals.rank(pct=True) * 100
            scores['profit_margin'] = pm_vals
        else:
            scores['pm_rank'] = 50
            scores['profit_margin'] = 0
        
        # Operating Margin (higher = better)
        if 'operating_margin' in df.columns and df['operating_margin'].notna().any():
            om_vals = df['operating_margin'].fillna(0)
            om_vals = om_vals.apply(lambda x: x * 100 if abs(x) < 1 else x)
            scores['om_rank'] = om_vals.rank(pct=True) * 100
            scores['operating_margin'] = om_vals
        else:
            scores['om_rank'] = 50
            scores['operating_margin'] = 0
        
        # Debt to Equity (lower = better, so invert)
        if 'debt_to_equity' in df.columns and df['debt_to_equity'].notna().any():
            de_vals = df['debt_to_equity'].fillna(df['debt_to_equity'].median())
            scores['debt_rank'] = 100 - de_vals.rank(pct=True) * 100
            scores['debt_to_equity'] = de_vals
        else:
            scores['debt_rank'] = 50
            scores['debt_to_equity'] = 0
        
        # Current Ratio (higher = better)
        if 'current_ratio' in df.columns and df['current_ratio'].notna().any():
            cr_vals = df['current_ratio'].fillna(1)
            scores['cr_rank'] = cr_vals.rank(pct=True) * 100
            scores['current_ratio'] = cr_vals
        else:
            scores['cr_rank'] = 50
            scores['current_ratio'] = 0
        
        # Fill any NaN ranks with neutral
        scores = scores.fillna(50)
        
        # Calculate composite score
        scores['score'] = (
            scores['roe_rank'] * self.roe_weight +
            scores['roa_rank'] * self.roa_weight +
            scores['pm_rank'] * self.profit_margin_weight +
            scores['om_rank'] * self.operating_margin_weight +
            scores['debt_rank'] * self.debt_weight +
            scores['cr_rank'] * self.current_ratio_weight
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
        
        return scores
