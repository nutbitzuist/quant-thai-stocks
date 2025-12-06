"""
Minervini Trend Template Model
Mark Minervini's SEPA (Specific Entry Point Analysis) criteria
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional
from app.models.base import TechnicalModel, SignalType
from app.data.fetcher import get_fetcher


class MinerviniTrendModel(TechnicalModel):
    """
    Minervini Trend Template (SEPA)
    
    Criteria for a stock in a Stage 2 uptrend:
    1. Price above 150-day and 200-day moving average
    2. 150-day MA above 200-day MA
    3. 200-day MA trending up for at least 1 month
    4. 50-day MA above both 150-day and 200-day MA
    5. Price above 50-day MA
    6. Price at least 25% above 52-week low
    7. Price within 25% of 52-week high
    8. RS Rating > 70 (relative strength vs market)
    """
    
    def __init__(
        self,
        min_above_52w_low_pct: float = 25,
        max_below_52w_high_pct: float = 25,
        min_rs_rating: float = 70
    ):
        super().__init__(
            name="Minervini Trend Template",
            description="Find stocks in Stage 2 uptrend using Mark Minervini's criteria",
            parameters={
                "min_above_52w_low_pct": min_above_52w_low_pct,
                "max_below_52w_high_pct": max_below_52w_high_pct,
                "min_rs_rating": min_rs_rating
            }
        )
        self.min_above_52w_low_pct = min_above_52w_low_pct
        self.max_below_52w_high_pct = max_below_52w_high_pct
        self.min_rs_rating = min_rs_rating
    
    def calculate_scores(
        self,
        price_data: Dict[str, pd.DataFrame],
        fundamental_data: Optional[pd.DataFrame] = None
    ) -> pd.DataFrame:
        fetcher = get_fetcher()
        results = []
        
        # Calculate market return for RS rating
        market_returns = []
        for ticker, df in price_data.items():
            if df is not None and len(df) >= 252:
                ret = (df['close'].iloc[-1] / df['close'].iloc[-252] - 1) * 100
                market_returns.append(ret)
        
        avg_market_return = np.mean(market_returns) if market_returns else 0
        
        for ticker, df in price_data.items():
            if df is None or len(df) < 252:
                continue
            
            try:
                df = fetcher.calculate_technicals(df)
                
                close = df['close'].iloc[-1]
                
                # Calculate all MAs
                sma_50 = df['close'].rolling(50).mean().iloc[-1]
                sma_150 = df['close'].rolling(150).mean().iloc[-1]
                sma_200 = df['close'].rolling(200).mean().iloc[-1]
                
                # 200-day MA slope (1 month ago)
                sma_200_1m_ago = df['close'].rolling(200).mean().iloc[-22]
                sma_200_trending_up = sma_200 > sma_200_1m_ago
                
                # 52-week high/low
                high_52w = df['high'].rolling(252).max().iloc[-1]
                low_52w = df['low'].rolling(252).min().iloc[-1]
                
                pct_above_low = (close / low_52w - 1) * 100
                pct_below_high = (1 - close / high_52w) * 100
                
                # Relative Strength (simplified)
                stock_return = (close / df['close'].iloc[-252] - 1) * 100
                rs_rating = 50 + (stock_return - avg_market_return) * 2
                rs_rating = max(0, min(100, rs_rating))
                
                # Check all criteria
                criteria = {
                    "price_above_150ma": close > sma_150,
                    "price_above_200ma": close > sma_200,
                    "ma150_above_ma200": sma_150 > sma_200,
                    "ma200_trending_up": sma_200_trending_up,
                    "ma50_above_ma150": sma_50 > sma_150,
                    "ma50_above_ma200": sma_50 > sma_200,
                    "price_above_50ma": close > sma_50,
                    "above_52w_low": pct_above_low >= self.min_above_52w_low_pct,
                    "near_52w_high": pct_below_high <= self.max_below_52w_high_pct,
                    "strong_rs": rs_rating >= self.min_rs_rating
                }
                
                # Count passing criteria
                passing = sum(criteria.values())
                total = len(criteria)
                
                # Score based on criteria met
                score = (passing / total) * 100
                
                if passing >= 8:  # Strong buy
                    signal_type = "BUY"
                elif passing <= 3:  # Not in uptrend
                    signal_type = "SELL"
                else:
                    signal_type = "HOLD"
                
                results.append({
                    "ticker": ticker,
                    "score": score,
                    "signal_type": signal_type,
                    "criteria_met": passing,
                    "criteria_total": total,
                    "rs_rating": round(rs_rating, 1),
                    "pct_from_high": round(-pct_below_high, 1),
                    "pct_from_low": round(pct_above_low, 1),
                    "price": round(close, 2),
                    "sma_50": round(sma_50, 2),
                    "sma_200": round(sma_200, 2)
                })
                
            except Exception as e:
                continue
        
        return pd.DataFrame(results)
