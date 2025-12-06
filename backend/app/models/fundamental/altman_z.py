"""
Altman Z-Score Model
Bankruptcy/Financial Distress Prediction
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional
from app.models.base import FundamentalModel, SignalType


class AltmanZScoreModel(FundamentalModel):
    """
    Altman Z-Score
    
    Predicts probability of bankruptcy within 2 years.
    Developed by Edward Altman in 1968.
    
    Z = 1.2*A + 1.4*B + 3.3*C + 0.6*D + 1.0*E
    
    Where:
    A = Working Capital / Total Assets
    B = Retained Earnings / Total Assets
    C = EBIT / Total Assets
    D = Market Value of Equity / Total Liabilities
    E = Sales / Total Assets
    
    Interpretation:
    Z > 2.99 = Safe Zone (very low bankruptcy risk)
    1.81 < Z < 2.99 = Grey Zone (some risk)
    Z < 1.81 = Distress Zone (high bankruptcy risk)
    
    Note: We use available proxies from Yahoo Finance
    """
    
    def __init__(
        self,
        safe_threshold: float = 2.99,
        distress_threshold: float = 1.81
    ):
        super().__init__(
            name="Altman Z-Score",
            description="Bankruptcy prediction - avoid financially distressed companies",
            parameters={
                "safe_threshold": safe_threshold,
                "distress_threshold": distress_threshold
            }
        )
        self.safe_threshold = safe_threshold
        self.distress_threshold = distress_threshold
    
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
            
            # Proxy calculations using available metrics
            # A = Working Capital / Total Assets (use current ratio as proxy)
            current_ratio = row.get('current_ratio', 1.0) or 1.0
            A = (current_ratio - 1) * 0.3  # Rough approximation
            A = max(-0.5, min(0.5, A))
            
            # B = Retained Earnings / Total Assets (use ROA as proxy)
            roa = row.get('roa', 0) or 0
            roa_val = roa * 100 if abs(roa) < 1 else roa
            B = roa_val / 100 * 2  # Approximation
            
            # C = EBIT / Total Assets (use operating margin * some factor)
            op_margin = row.get('operating_margin', 0) or 0
            op_val = op_margin * 100 if abs(op_margin) < 1 else op_margin
            C = op_val / 100 * 0.5
            
            # D = Market Value Equity / Total Liabilities (inverse of D/E)
            de = row.get('debt_to_equity', 100) or 100
            D = 1 / (de / 100 + 0.01) if de > 0 else 1.0
            D = min(3.0, D)
            
            # E = Sales / Total Assets (use ROA / profit margin as proxy)
            profit_margin = row.get('profit_margin', 0.1) or 0.1
            pm_val = profit_margin if profit_margin > 0.01 else 0.1
            E = roa_val / 100 / pm_val if pm_val > 0 else 0.5
            E = max(0, min(3, E))
            
            # Calculate Z-Score
            z_score = 1.2*A + 1.4*B + 3.3*C + 0.6*D + 1.0*E
            
            # Normalize to 0-100 score
            # Z-Score typically ranges from -4 to +8
            # Map: < 1.81 = 0-30, 1.81-2.99 = 30-70, > 2.99 = 70-100
            if z_score >= self.safe_threshold:
                score = 70 + (z_score - self.safe_threshold) * 10
            elif z_score >= self.distress_threshold:
                score = 30 + (z_score - self.distress_threshold) / (self.safe_threshold - self.distress_threshold) * 40
            else:
                score = max(0, 30 + (z_score - self.distress_threshold) * 15)
            
            score = max(0, min(100, score))
            
            # Determine signal
            if z_score >= self.safe_threshold:
                signal_type = "BUY"
                zone = "Safe"
            elif z_score >= self.distress_threshold:
                signal_type = "HOLD"
                zone = "Grey"
            else:
                signal_type = "SELL"
                zone = "Distress"
            
            results.append({
                "ticker": ticker,
                "score": score,
                "signal_type": signal_type,
                "z_score": round(z_score, 2),
                "zone": zone,
                "current_ratio": round(current_ratio, 2),
                "debt_to_equity": round(de, 1) if de else None
            })
        
        return pd.DataFrame(results)
