"""
CANSLIM Model
William O'Neil's famous growth stock selection system
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional
from app.models.base import FundamentalModel, SignalType
from app.data.fetcher import get_fetcher


class CANSLIMModel(FundamentalModel):
    """
    CANSLIM Growth Stock Selection (William O'Neil)
    
    C - Current Quarterly Earnings (up 25%+)
    A - Annual Earnings Growth (5-year history)
    N - New Products/Management/Highs
    S - Supply and Demand (volume on up days)
    L - Leader or Laggard (RS Rating > 80)
    I - Institutional Sponsorship (fund ownership)
    M - Market Direction (bull market)
    
    Note: Some criteria require data not available from Yahoo Finance,
    so we use proxies where necessary.
    """
    
    def __init__(
        self,
        min_quarterly_eps_growth: float = 25,
        min_annual_eps_growth: float = 25,
        min_rs_rating: float = 80,
        min_roe: float = 17
    ):
        super().__init__(
            name="CANSLIM",
            description="William O'Neil's growth stock selection (C-A-N-S-L-I-M)",
            parameters={
                "min_quarterly_eps_growth": min_quarterly_eps_growth,
                "min_annual_eps_growth": min_annual_eps_growth,
                "min_rs_rating": min_rs_rating,
                "min_roe": min_roe
            }
        )
        self.min_quarterly_eps_growth = min_quarterly_eps_growth
        self.min_annual_eps_growth = min_annual_eps_growth
        self.min_rs_rating = min_rs_rating
        self.min_roe = min_roe
    
    def calculate_scores(
        self,
        price_data: Dict[str, pd.DataFrame],
        fundamental_data: Optional[pd.DataFrame] = None
    ) -> pd.DataFrame:
        fetcher = get_fetcher()
        results = []
        
        if fundamental_data is None or fundamental_data.empty:
            return pd.DataFrame()
        
        # Calculate market returns for RS rating
        market_returns = []
        for ticker, df in price_data.items():
            if df is not None and len(df) >= 252:
                ret = (df['close'].iloc[-1] / df['close'].iloc[-252] - 1) * 100
                market_returns.append(ret)
        avg_market_return = np.mean(market_returns) if market_returns else 0
        
        for _, row in fundamental_data.iterrows():
            ticker = row.get('ticker')
            if ticker not in price_data or price_data[ticker] is None:
                continue
            
            df = price_data[ticker]
            if len(df) < 252:
                continue
            
            try:
                df = fetcher.calculate_technicals(df)
                close = df['close'].iloc[-1]
                
                scores = {}
                criteria_met = 0
                total_criteria = 7
                
                # C - Current Quarterly Earnings
                quarterly_growth = row.get('earnings_quarterly_growth')
                if quarterly_growth is not None:
                    quarterly_growth_pct = quarterly_growth * 100 if quarterly_growth < 1 else quarterly_growth
                    if quarterly_growth_pct >= self.min_quarterly_eps_growth:
                        criteria_met += 1
                        scores['C'] = min(100, quarterly_growth_pct * 2)
                    else:
                        scores['C'] = max(0, quarterly_growth_pct * 2)
                else:
                    scores['C'] = 50  # Unknown
                
                # A - Annual Earnings Growth
                annual_growth = row.get('earnings_growth')
                if annual_growth is not None:
                    annual_growth_pct = annual_growth * 100 if abs(annual_growth) < 2 else annual_growth
                    if annual_growth_pct >= self.min_annual_eps_growth:
                        criteria_met += 1
                        scores['A'] = min(100, annual_growth_pct * 2)
                    else:
                        scores['A'] = max(0, 50 + annual_growth_pct)
                else:
                    scores['A'] = 50
                
                # N - New Highs (price within 15% of 52-week high)
                high_52w = df['high'].rolling(252).max().iloc[-1]
                pct_from_high = (close / high_52w) * 100
                if pct_from_high >= 85:  # Within 15% of high
                    criteria_met += 1
                    scores['N'] = min(100, pct_from_high)
                else:
                    scores['N'] = pct_from_high
                
                # S - Supply/Demand (volume on up days vs down days)
                up_days = df[df['close'] > df['close'].shift(1)].tail(20)
                down_days = df[df['close'] < df['close'].shift(1)].tail(20)
                
                up_volume = up_days['volume'].mean() if len(up_days) > 0 else 0
                down_volume = down_days['volume'].mean() if len(down_days) > 0 else 0
                
                if up_volume > down_volume * 1.2:  # 20% more volume on up days
                    criteria_met += 1
                    scores['S'] = min(100, 50 + (up_volume / down_volume - 1) * 100) if down_volume > 0 else 75
                else:
                    scores['S'] = 50
                
                # L - Leader (Relative Strength)
                stock_return = (close / df['close'].iloc[-252] - 1) * 100 if len(df) >= 252 else 0
                rs_rating = 50 + (stock_return - avg_market_return) * 2
                rs_rating = max(0, min(100, rs_rating))
                
                if rs_rating >= self.min_rs_rating:
                    criteria_met += 1
                    scores['L'] = rs_rating
                else:
                    scores['L'] = rs_rating
                
                # I - Institutional (use ROE as proxy for quality institutions like)
                roe = row.get('roe')
                if roe is not None:
                    roe_pct = roe * 100 if abs(roe) < 1 else roe
                    if roe_pct >= self.min_roe:
                        criteria_met += 1
                        scores['I'] = min(100, roe_pct * 3)
                    else:
                        scores['I'] = max(0, roe_pct * 3)
                else:
                    scores['I'] = 50
                
                # M - Market (trend of 200-day MA)
                sma_200 = df['sma_200'].iloc[-1] if 'sma_200' in df.columns else df['close'].rolling(200).mean().iloc[-1]
                sma_200_1m = df['close'].rolling(200).mean().iloc[-22]
                
                if sma_200 > sma_200_1m and close > sma_200:
                    criteria_met += 1
                    scores['M'] = 80
                elif close > sma_200:
                    scores['M'] = 60
                else:
                    scores['M'] = 40
                
                # Calculate overall score
                overall_score = np.mean(list(scores.values()))
                
                if criteria_met >= 5:
                    signal_type = "BUY"
                elif criteria_met <= 2:
                    signal_type = "SELL"
                else:
                    signal_type = "HOLD"
                
                results.append({
                    "ticker": ticker,
                    "score": overall_score,
                    "signal_type": signal_type,
                    "criteria_met": criteria_met,
                    "criteria_total": total_criteria,
                    "C_score": round(scores.get('C', 0), 1),
                    "A_score": round(scores.get('A', 0), 1),
                    "N_score": round(scores.get('N', 0), 1),
                    "S_score": round(scores.get('S', 0), 1),
                    "L_score": round(scores.get('L', 0), 1),
                    "I_score": round(scores.get('I', 0), 1),
                    "M_score": round(scores.get('M', 0), 1),
                    "rs_rating": round(rs_rating, 1)
                })
                
            except Exception as e:
                continue
        
        return pd.DataFrame(results)
