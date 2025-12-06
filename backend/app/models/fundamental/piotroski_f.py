"""
Piotroski F-Score Model
9-point scoring system for financial strength
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional
from app.models.base import FundamentalModel, SignalType


class PiotroskiFScoreModel(FundamentalModel):
    """
    Piotroski F-Score (0-9)
    
    Profitability (4 points):
    1. Positive ROA
    2. Positive Operating Cash Flow
    3. ROA higher than previous year (using current vs estimate)
    4. Cash flow > Net income (accruals)
    
    Leverage & Liquidity (3 points):
    5. Lower debt ratio than previous year
    6. Higher current ratio than previous year  
    7. No new shares issued
    
    Operating Efficiency (2 points):
    8. Higher gross margin than previous year
    9. Higher asset turnover than previous year
    
    Note: Simplified for available data
    """
    
    def __init__(
        self,
        buy_threshold: int = 7,
        sell_threshold: int = 3
    ):
        super().__init__(
            name="Piotroski F-Score",
            description="9-point financial strength score (7+ = strong buy)",
            parameters={
                "buy_threshold": buy_threshold,
                "sell_threshold": sell_threshold
            }
        )
        self.buy_threshold = buy_threshold
        self.sell_threshold = sell_threshold
    
    def calculate_scores(
        self,
        price_data: Dict[str, pd.DataFrame],
        fundamental_data: Optional[pd.DataFrame] = None
    ) -> pd.DataFrame:
        if fundamental_data is None or fundamental_data.empty:
            return pd.DataFrame()
        
        results = []
        
        for _, row in fundamental_data.iterrows():
            ticker = row.get('ticker')
            if not ticker:
                continue
            
            f_score = 0
            details = {}
            
            # 1. Positive ROA
            roa = row.get('roa')
            if roa is not None:
                roa_val = roa * 100 if abs(roa) < 1 else roa
                if roa_val > 0:
                    f_score += 1
                    details['roa_positive'] = True
                else:
                    details['roa_positive'] = False
                details['roa'] = round(roa_val, 2)
            
            # 2. Positive Operating Cash Flow (proxy: positive profit margin)
            pm = row.get('profit_margin')
            if pm is not None:
                pm_val = pm * 100 if abs(pm) < 1 else pm
                if pm_val > 0:
                    f_score += 1
                    details['ocf_positive'] = True
                else:
                    details['ocf_positive'] = False
            
            # 3. ROA improving (proxy: forward EPS > trailing EPS)
            forward_eps = row.get('forward_eps')
            trailing_eps = row.get('eps')
            if forward_eps is not None and trailing_eps is not None and trailing_eps > 0:
                if forward_eps > trailing_eps:
                    f_score += 1
                    details['roa_improving'] = True
                else:
                    details['roa_improving'] = False
            
            # 4. Quality of earnings (proxy: operating margin > profit margin)
            om = row.get('operating_margin')
            if om is not None and pm is not None:
                # Good quality = operating margin supports profit margin
                if om >= pm * 0.8:  # Operating margin at least 80% of profit margin
                    f_score += 1
                    details['earnings_quality'] = True
                else:
                    details['earnings_quality'] = False
            
            # 5. Lower debt ratio (proxy: D/E < 100)
            de = row.get('debt_to_equity')
            if de is not None:
                if de < 100:  # D/E below 1.0 (expressed as percentage)
                    f_score += 1
                    details['low_leverage'] = True
                else:
                    details['low_leverage'] = False
                details['debt_to_equity'] = round(de, 1)
            
            # 6. Good liquidity (current ratio > 1)
            cr = row.get('current_ratio')
            if cr is not None:
                if cr > 1:
                    f_score += 1
                    details['good_liquidity'] = True
                else:
                    details['good_liquidity'] = False
                details['current_ratio'] = round(cr, 2)
            
            # 7. No dilution (proxy: cannot check, give benefit of doubt to quality companies)
            roe = row.get('roe')
            if roe is not None:
                roe_val = roe * 100 if abs(roe) < 1 else roe
                if roe_val > 15:  # High ROE companies likely not diluting
                    f_score += 1
                    details['no_dilution'] = True
            
            # 8. Improving margins (proxy: gross margin > industry average ~30%)
            gm = row.get('gross_margin')
            if gm is not None:
                gm_val = gm * 100 if abs(gm) < 1 else gm
                if gm_val > 30:
                    f_score += 1
                    details['good_margins'] = True
                else:
                    details['good_margins'] = False
                details['gross_margin'] = round(gm_val, 1)
            
            # 9. Asset efficiency (proxy: revenue growth positive)
            rev_growth = row.get('revenue_growth')
            if rev_growth is not None:
                rg_val = rev_growth * 100 if abs(rev_growth) < 1 else rev_growth
                if rg_val > 0:
                    f_score += 1
                    details['revenue_growing'] = True
                else:
                    details['revenue_growing'] = False
                details['revenue_growth'] = round(rg_val, 1)
            
            # Determine signal
            if f_score >= self.buy_threshold:
                signal_type = "BUY"
            elif f_score <= self.sell_threshold:
                signal_type = "SELL"
            else:
                signal_type = "HOLD"
            
            # Score normalized to 0-100
            score = (f_score / 9) * 100
            
            results.append({
                "ticker": ticker,
                "score": score,
                "signal_type": signal_type,
                "f_score": f_score,
                "max_score": 9,
                **details
            })
        
        return pd.DataFrame(results)
