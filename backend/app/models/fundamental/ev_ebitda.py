"""
EV/EBITDA Screen Model
Enterprise Value to EBITDA - Better than P/E for cross-company comparisons
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional
from app.models.base import FundamentalModel, Signal, ModelCategory


class EVEBITDAModel(FundamentalModel):
    """
    EV/EBITDA Screen - Enterprise Value to EBITDA ratio analysis
    
    Why EV/EBITDA is better than P/E:
    - Capital structure neutral (accounts for debt)
    - Less affected by accounting differences
    - Better for comparing companies across industries
    - Excludes non-cash charges (depreciation/amortization)
    
    Signals:
    - BUY: Low EV/EBITDA with positive EBITDA growth
    - SELL: High EV/EBITDA or negative EBITDA
    - HOLD: Average valuation
    """
    
    def __init__(
        self,
        max_ev_ebitda: float = 15.0,
        min_ev_ebitda: float = 0.0,
        min_ebitda_margin: float = 10.0,
        prefer_low_debt: bool = True,
        debt_to_ebitda_max: float = 4.0
    ):
        self.max_ev_ebitda = max_ev_ebitda
        self.min_ev_ebitda = min_ev_ebitda
        self.min_ebitda_margin = min_ebitda_margin
        self.prefer_low_debt = prefer_low_debt
        self.debt_to_ebitda_max = debt_to_ebitda_max
        
        params = {
            "max_ev_ebitda": max_ev_ebitda,
            "min_ev_ebitda": min_ev_ebitda,
            "min_ebitda_margin": min_ebitda_margin,
            "prefer_low_debt": prefer_low_debt,
            "debt_to_ebitda_max": debt_to_ebitda_max
        }
        super().__init__(
            name="EV/EBITDA Screen",
            description="Find undervalued stocks using Enterprise Value to EBITDA ratio",
            parameters=params
        )
    
    def calculate_ev_ebitda(self, fundamental_data: dict) -> Optional[float]:
        """Calculate EV/EBITDA ratio"""
        try:
            # First try to use pre-calculated EV/EBITDA from yfinance
            ev_to_ebitda = fundamental_data.get('ev_to_ebitda')
            if ev_to_ebitda and ev_to_ebitda > 0:
                return ev_to_ebitda
            
            # Fallback: calculate manually
            # Get market cap
            market_cap = fundamental_data.get('market_cap', 0)
            if not market_cap or market_cap <= 0:
                return None
            
            # Get debt and cash
            total_debt = fundamental_data.get('total_debt', 0) or 0
            cash = fundamental_data.get('total_cash', 0) or 0
            
            # Calculate Enterprise Value (or use pre-calculated)
            ev = fundamental_data.get('enterprise_value')
            if not ev or ev <= 0:
                ev = market_cap + total_debt - cash
            
            # Get EBITDA
            ebitda = fundamental_data.get('ebitda', 0)
            if not ebitda or ebitda <= 0:
                return None
            
            return ev / ebitda
        except:
            return None
    
    def calculate_ebitda_margin(self, fundamental_data: dict) -> Optional[float]:
        """Calculate EBITDA margin"""
        try:
            # First try pre-calculated margin from yfinance (as decimal 0-1)
            ebitda_margins = fundamental_data.get('ebitda_margins')
            if ebitda_margins and ebitda_margins > 0:
                return ebitda_margins * 100  # Convert to percentage
            
            # Fallback: calculate manually
            ebitda = fundamental_data.get('ebitda', 0)
            revenue = fundamental_data.get('total_revenue', 0)
            
            if not revenue or revenue <= 0 or not ebitda:
                return None
            
            return (ebitda / revenue) * 100
        except:
            return None
    
    def calculate_debt_to_ebitda(self, fundamental_data: dict) -> Optional[float]:
        """Calculate Debt/EBITDA ratio"""
        try:
            total_debt = fundamental_data.get('total_debt', 0) or 0
            ebitda = fundamental_data.get('ebitda', 0)
            
            if not ebitda or ebitda <= 0:
                return None
            
            return total_debt / ebitda
        except:
            return None
    
    def calculate_scores(
        self,
        price_data: Dict[str, pd.DataFrame],
        fundamental_data: Optional[pd.DataFrame] = None
    ) -> pd.DataFrame:
        """Calculate EV/EBITDA scores for all stocks"""
        
        results = []
        
        if fundamental_data is None or fundamental_data.empty:
            return pd.DataFrame(results)
        
        for _, row in fundamental_data.iterrows():
            ticker = row.get('ticker', row.name if isinstance(row.name, str) else 'UNKNOWN')
            
            try:
                fund_dict = row.to_dict()
                
                # Calculate metrics
                ev_ebitda = self.calculate_ev_ebitda(fund_dict)
                ebitda_margin = self.calculate_ebitda_margin(fund_dict)
                debt_to_ebitda = self.calculate_debt_to_ebitda(fund_dict)
                
                # Skip if we can't calculate EV/EBITDA
                if ev_ebitda is None:
                    continue
                
                # Determine signal
                signal_type = "HOLD"
                score = 50
                
                # Check for BUY signal
                if (self.min_ev_ebitda <= ev_ebitda <= self.max_ev_ebitda):
                    if ebitda_margin and ebitda_margin >= self.min_ebitda_margin:
                        # Check debt level if required
                        if self.prefer_low_debt and debt_to_ebitda:
                            if debt_to_ebitda <= self.debt_to_ebitda_max:
                                signal_type = "BUY"
                                # Score based on how low EV/EBITDA is
                                ev_score = max(0, 100 - (ev_ebitda / self.max_ev_ebitda * 50))
                                margin_score = min(100, ebitda_margin * 2)
                                debt_score = max(0, 100 - (debt_to_ebitda / self.debt_to_ebitda_max * 50))
                                score = (ev_score * 0.5 + margin_score * 0.3 + debt_score * 0.2)
                        else:
                            signal_type = "BUY"
                            ev_score = max(0, 100 - (ev_ebitda / self.max_ev_ebitda * 50))
                            margin_score = min(100, ebitda_margin * 2) if ebitda_margin else 50
                            score = (ev_score * 0.6 + margin_score * 0.4)
                
                # Check for SELL signal
                elif ev_ebitda > self.max_ev_ebitda * 1.5 or ev_ebitda < 0:
                    signal_type = "SELL"
                    score = max(0, 30 - (ev_ebitda - self.max_ev_ebitda) * 2)
                
                # High debt is a warning
                if debt_to_ebitda and debt_to_ebitda > self.debt_to_ebitda_max * 1.5:
                    if signal_type == "BUY":
                        signal_type = "HOLD"
                        score = score * 0.7
                
                results.append({
                    'ticker': ticker,
                    'score': round(score, 2),
                    'signal': signal_type,
                    'ev_ebitda': round(ev_ebitda, 2) if ev_ebitda else None,
                    'ebitda_margin': round(ebitda_margin, 2) if ebitda_margin else None,
                    'debt_to_ebitda': round(debt_to_ebitda, 2) if debt_to_ebitda else None,
                    'market_cap': fund_dict.get('market_cap'),
                    'name': fund_dict.get('name', ticker)
                })
                
            except Exception as e:
                self.errors.append(f"Error processing {ticker}: {str(e)}")
                continue
        
        return pd.DataFrame(results)
