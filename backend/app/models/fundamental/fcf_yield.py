"""
Free Cash Flow Yield Model
Focus on companies generating strong free cash flow relative to price
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional
from app.models.base import FundamentalModel, Signal, ModelCategory


class FCFYieldModel(FundamentalModel):
    """
    Free Cash Flow Yield Screen
    
    FCF Yield = Free Cash Flow / Market Cap
    
    Why FCF Yield matters:
    - Cash is harder to manipulate than earnings
    - Shows actual cash generation ability
    - Better indicator of dividend sustainability
    - Useful for identifying undervalued cash generators
    
    Signals:
    - BUY: High FCF yield with consistent FCF generation
    - SELL: Negative FCF or very low yield
    - HOLD: Average FCF yield
    """
    
    def __init__(
        self,
        min_fcf_yield: float = 5.0,
        min_fcf_margin: float = 5.0,
        require_positive_fcf: bool = True,
        max_capex_ratio: float = 50.0
    ):
        self.min_fcf_yield = min_fcf_yield
        self.min_fcf_margin = min_fcf_margin
        self.require_positive_fcf = require_positive_fcf
        self.max_capex_ratio = max_capex_ratio
        
        params = {
            "min_fcf_yield": min_fcf_yield,
            "min_fcf_margin": min_fcf_margin,
            "require_positive_fcf": require_positive_fcf,
            "max_capex_ratio": max_capex_ratio
        }
        super().__init__(
            name="FCF Yield",
            description="Find stocks with high free cash flow yield - cash generation focus",
            parameters=params
        )
    
    def calculate_fcf_yield(self, fundamental_data: dict) -> Optional[float]:
        """Calculate FCF Yield = FCF / Market Cap * 100"""
        try:
            fcf = fundamental_data.get('free_cash_flow', 0)
            market_cap = fundamental_data.get('market_cap', 0)
            
            if not market_cap or market_cap <= 0:
                return None
            
            if fcf is None:
                # Try to calculate from operating cash flow - capex
                ocf = fundamental_data.get('operating_cash_flow', 0)
                capex = abs(fundamental_data.get('capital_expenditure', 0) or 0)
                if ocf:
                    fcf = ocf - capex
                else:
                    return None
            
            return (fcf / market_cap) * 100
        except:
            return None
    
    def calculate_fcf_margin(self, fundamental_data: dict) -> Optional[float]:
        """Calculate FCF Margin = FCF / Revenue * 100"""
        try:
            fcf = fundamental_data.get('free_cash_flow', 0)
            revenue = fundamental_data.get('total_revenue', 0)  # Use correct field name
            
            if not revenue or revenue <= 0:
                return None
            
            if fcf is None:
                ocf = fundamental_data.get('operating_cash_flow', 0)
                capex = abs(fundamental_data.get('capital_expenditure', 0) or 0)
                if ocf:
                    fcf = ocf - capex
                else:
                    return None
            
            return (fcf / revenue) * 100
        except:
            return None
    
    def calculate_capex_ratio(self, fundamental_data: dict) -> Optional[float]:
        """Calculate CapEx as % of Operating Cash Flow"""
        try:
            ocf = fundamental_data.get('operating_cash_flow', 0)
            capex = abs(fundamental_data.get('capital_expenditure', 0) or 0)
            
            if not ocf or ocf <= 0:
                return None
            
            return (capex / ocf) * 100
        except:
            return None
    
    def calculate_fcf_conversion(self, fundamental_data: dict) -> Optional[float]:
        """Calculate FCF to Net Income conversion ratio"""
        try:
            fcf = fundamental_data.get('free_cash_flow', 0)
            net_income = fundamental_data.get('net_income', 0)
            
            if not net_income or net_income <= 0:
                return None
            
            if fcf is None:
                ocf = fundamental_data.get('operating_cash_flow', 0)
                capex = abs(fundamental_data.get('capital_expenditure', 0) or 0)
                if ocf:
                    fcf = ocf - capex
                else:
                    return None
            
            return (fcf / net_income) * 100
        except:
            return None
    
    def calculate_scores(
        self,
        price_data: Dict[str, pd.DataFrame],
        fundamental_data: Optional[pd.DataFrame] = None
    ) -> pd.DataFrame:
        """Calculate FCF Yield scores for all stocks"""
        
        results = []
        
        if fundamental_data is None or fundamental_data.empty:
            return pd.DataFrame(results)
        
        for _, row in fundamental_data.iterrows():
            ticker = row.get('ticker', row.name if isinstance(row.name, str) else 'UNKNOWN')
            
            try:
                fund_dict = row.to_dict()
                
                # Calculate metrics
                fcf_yield = self.calculate_fcf_yield(fund_dict)
                fcf_margin = self.calculate_fcf_margin(fund_dict)
                capex_ratio = self.calculate_capex_ratio(fund_dict)
                fcf_conversion = self.calculate_fcf_conversion(fund_dict)
                
                # Skip if we can't calculate FCF yield
                if fcf_yield is None:
                    continue
                
                # Skip negative FCF if required
                if self.require_positive_fcf and fcf_yield < 0:
                    continue
                
                # Determine signal
                signal_type = "HOLD"
                score = 50
                
                # Check for BUY signal
                if fcf_yield >= self.min_fcf_yield:
                    if fcf_margin is None or fcf_margin >= self.min_fcf_margin:
                        # Check capex ratio
                        if capex_ratio is None or capex_ratio <= self.max_capex_ratio:
                            signal_type = "BUY"
                            
                            # Score based on FCF yield (higher is better)
                            yield_score = min(100, fcf_yield * 5)
                            margin_score = min(100, fcf_margin * 4) if fcf_margin else 50
                            conversion_score = min(100, fcf_conversion) if fcf_conversion and fcf_conversion > 0 else 50
                            
                            score = (yield_score * 0.5 + margin_score * 0.3 + conversion_score * 0.2)
                
                # Check for SELL signal
                elif fcf_yield < 0:
                    signal_type = "SELL"
                    score = max(0, 30 + fcf_yield * 2)  # More negative = lower score
                
                elif fcf_yield < self.min_fcf_yield / 2:
                    signal_type = "SELL"
                    score = 30 + (fcf_yield / self.min_fcf_yield) * 20
                
                # High capex ratio is a warning
                if capex_ratio and capex_ratio > self.max_capex_ratio * 1.5:
                    if signal_type == "BUY":
                        signal_type = "HOLD"
                        score = score * 0.8
                
                results.append({
                    'ticker': ticker,
                    'score': round(score, 2),
                    'signal': signal_type,
                    'fcf_yield': round(fcf_yield, 2) if fcf_yield else None,
                    'fcf_margin': round(fcf_margin, 2) if fcf_margin else None,
                    'capex_ratio': round(capex_ratio, 2) if capex_ratio else None,
                    'fcf_conversion': round(fcf_conversion, 2) if fcf_conversion else None,
                    'market_cap': fund_dict.get('market_cap'),
                    'name': fund_dict.get('name', ticker)
                })
                
            except Exception as e:
                self.errors.append(f"Error processing {ticker}: {str(e)}")
                continue
        
        return pd.DataFrame(results)
