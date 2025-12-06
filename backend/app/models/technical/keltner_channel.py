"""
Keltner Channel Model
Volatility-based channel breakout
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional
from app.models.base import TechnicalModel, SignalType
from app.data.fetcher import get_fetcher


class KeltnerChannelModel(TechnicalModel):
    """
    Keltner Channel
    
    Similar to Bollinger Bands but uses ATR instead of standard deviation.
    
    Components:
    - Middle: EMA of close (typically 20)
    - Upper: EMA + (ATR * multiplier)
    - Lower: EMA - (ATR * multiplier)
    
    Strategy:
    - Breakout above upper channel = BUY
    - Breakout below lower channel = SELL
    - Inside channel = HOLD
    
    Works well for trend-following in trending markets.
    """
    
    def __init__(
        self,
        ema_period: int = 20,
        atr_period: int = 10,
        atr_multiplier: float = 2.0
    ):
        super().__init__(
            name="Keltner Channel",
            description="ATR-based channel breakout - buy above upper channel",
            parameters={
                "ema_period": ema_period,
                "atr_period": atr_period,
                "atr_multiplier": atr_multiplier
            }
        )
        self.ema_period = ema_period
        self.atr_period = atr_period
        self.multiplier = atr_multiplier
    
    def calculate_scores(
        self,
        price_data: Dict[str, pd.DataFrame],
        fundamental_data: Optional[pd.DataFrame] = None
    ) -> pd.DataFrame:
        fetcher = get_fetcher()
        results = []
        
        for ticker, df in price_data.items():
            if df is None or len(df) < max(self.ema_period, self.atr_period) + 10:
                continue
            
            try:
                df = fetcher.calculate_technicals(df)
                
                close = df['close']
                high = df['high']
                low = df['low']
                
                # Calculate EMA
                ema = close.ewm(span=self.ema_period, adjust=False).mean()
                
                # Use ATR from technicals or calculate
                if 'atr' in df.columns:
                    atr = df['atr']
                else:
                    tr1 = high - low
                    tr2 = abs(high - close.shift())
                    tr3 = abs(low - close.shift())
                    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
                    atr = tr.rolling(self.atr_period).mean()
                
                # Keltner Channels
                upper = ema + (atr * self.multiplier)
                lower = ema - (atr * self.multiplier)
                
                current_close = close.iloc[-1]
                current_upper = upper.iloc[-1]
                current_lower = lower.iloc[-1]
                current_ema = ema.iloc[-1]
                
                # Channel width
                channel_width = (current_upper - current_lower) / current_ema * 100
                
                # Position in channel
                if current_upper != current_lower:
                    position = (current_close - current_lower) / (current_upper - current_lower)
                else:
                    position = 0.5
                
                # Trend direction
                ema_slope = (ema.iloc[-1] - ema.iloc[-5]) / ema.iloc[-5] * 100
                
                # Determine signal
                if current_close > current_upper:
                    signal_type = "BUY"
                    breakout_strength = (current_close / current_upper - 1) * 100
                    score = 70 + min(20, breakout_strength * 10) + (10 if ema_slope > 0 else 0)
                elif current_close < current_lower:
                    signal_type = "SELL"
                    breakdown_strength = (1 - current_close / current_lower) * 100
                    score = 70 + min(20, breakdown_strength * 10)
                elif position > 0.8:  # Near upper channel
                    signal_type = "HOLD"
                    score = 60 if ema_slope > 0 else 50
                elif position < 0.2:  # Near lower channel
                    signal_type = "HOLD"
                    score = 40 if ema_slope < 0 else 50
                else:
                    signal_type = "HOLD"
                    score = 50
                
                score = min(100, max(0, score))
                
                results.append({
                    "ticker": ticker,
                    "score": score,
                    "signal_type": signal_type,
                    "price": round(current_close, 2),
                    "upper_channel": round(current_upper, 2),
                    "lower_channel": round(current_lower, 2),
                    "ema": round(current_ema, 2),
                    "channel_position": round(position * 100, 1),
                    "ema_slope_pct": round(ema_slope, 2)
                })
                
            except Exception as e:
                continue
        
        return pd.DataFrame(results)
