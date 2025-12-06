"""
ADX Trend Strength Model
Average Directional Index - measures trend strength
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional
from app.models.base import TechnicalModel, SignalType
from app.data.fetcher import get_fetcher


class ADXTrendModel(TechnicalModel):
    """
    ADX (Average Directional Index) Trend Strength
    
    Developed by J. Welles Wilder Jr.
    
    Components:
    - +DI (Positive Directional Indicator): measures upward movement
    - -DI (Negative Directional Indicator): measures downward movement
    - ADX: smoothed average of the difference between +DI and -DI
    
    Interpretation:
    - ADX > 25: Strong trend (trade with trend)
    - ADX < 20: Weak trend or ranging (avoid trend strategies)
    - +DI > -DI: Uptrend
    - -DI > +DI: Downtrend
    """
    
    def __init__(
        self,
        adx_period: int = 14,
        strong_trend: float = 25,
        weak_trend: float = 20
    ):
        super().__init__(
            name="ADX Trend Strength",
            description="Identifies strong trends using ADX - buy in strong uptrends",
            parameters={
                "adx_period": adx_period,
                "strong_trend": strong_trend,
                "weak_trend": weak_trend
            }
        )
        self.period = adx_period
        self.strong = strong_trend
        self.weak = weak_trend
    
    def _calculate_adx(self, df: pd.DataFrame) -> tuple:
        """Calculate ADX, +DI, -DI"""
        high = df['high']
        low = df['low']
        close = df['close']
        
        # True Range
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(self.period).mean()
        
        # Directional Movement
        up_move = high - high.shift()
        down_move = low.shift() - low
        
        plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0)
        minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0)
        
        plus_dm = pd.Series(plus_dm, index=df.index)
        minus_dm = pd.Series(minus_dm, index=df.index)
        
        # Smoothed DM
        plus_di = 100 * (plus_dm.rolling(self.period).mean() / atr)
        minus_di = 100 * (minus_dm.rolling(self.period).mean() / atr)
        
        # DX and ADX
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di).replace(0, 1)
        adx = dx.rolling(self.period).mean()
        
        return adx, plus_di, minus_di
    
    def calculate_scores(
        self,
        price_data: Dict[str, pd.DataFrame],
        fundamental_data: Optional[pd.DataFrame] = None
    ) -> pd.DataFrame:
        results = []
        
        for ticker, df in price_data.items():
            if df is None or len(df) < self.period * 3:
                continue
            
            try:
                adx, plus_di, minus_di = self._calculate_adx(df)
                
                current_adx = adx.iloc[-1]
                current_plus = plus_di.iloc[-1]
                current_minus = minus_di.iloc[-1]
                
                # ADX trend
                adx_rising = adx.iloc[-1] > adx.iloc[-5]
                
                # Determine trend direction and strength
                is_uptrend = current_plus > current_minus
                is_downtrend = current_minus > current_plus
                is_strong = current_adx >= self.strong
                is_weak = current_adx < self.weak
                
                # Calculate score
                if is_strong and is_uptrend and adx_rising:
                    signal_type = "BUY"
                    score = 60 + min(30, current_adx) + (current_plus - current_minus)
                elif is_strong and is_downtrend and adx_rising:
                    signal_type = "SELL"
                    score = 60 + min(30, current_adx) + (current_minus - current_plus)
                elif is_weak:
                    signal_type = "HOLD"
                    score = 40 + current_adx
                else:
                    signal_type = "HOLD"
                    score = 50
                
                score = min(100, max(0, score))
                
                results.append({
                    "ticker": ticker,
                    "score": score,
                    "signal_type": signal_type,
                    "adx": round(current_adx, 2),
                    "plus_di": round(current_plus, 2),
                    "minus_di": round(current_minus, 2),
                    "trend": "Strong Up" if is_strong and is_uptrend else "Strong Down" if is_strong and is_downtrend else "Weak/Range",
                    "adx_rising": adx_rising
                })
                
            except Exception as e:
                continue
        
        return pd.DataFrame(results)
