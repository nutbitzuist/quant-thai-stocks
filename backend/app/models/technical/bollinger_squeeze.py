"""
Bollinger Band Squeeze Model
Volatility contraction breakout strategy
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional
from app.models.base import TechnicalModel, SignalType
from app.data.fetcher import get_fetcher


class BollingerSqueezeModel(TechnicalModel):
    """
    Bollinger Band Squeeze
    
    When Bollinger Bands narrow (squeeze), it indicates low volatility.
    This often precedes a significant price move.
    
    Strategy:
    1. Identify when bands are at their narrowest (squeeze)
    2. Wait for breakout above upper band = BUY
    3. Breakout below lower band = SELL
    4. Use Keltner Channels to confirm squeeze
    """
    
    def __init__(
        self,
        bb_period: int = 20,
        bb_std: float = 2.0,
        squeeze_percentile: float = 20,  # Squeeze when bandwidth in bottom 20%
        volume_confirm: float = 1.2
    ):
        super().__init__(
            name="Bollinger Squeeze",
            description="Volatility contraction breakout - buy when bands expand after squeeze",
            parameters={
                "bb_period": bb_period,
                "bb_std": bb_std,
                "squeeze_percentile": squeeze_percentile,
                "volume_confirm": volume_confirm
            }
        )
        self.bb_period = bb_period
        self.bb_std = bb_std
        self.squeeze_pct = squeeze_percentile
        self.volume_confirm = volume_confirm
    
    def calculate_scores(
        self,
        price_data: Dict[str, pd.DataFrame],
        fundamental_data: Optional[pd.DataFrame] = None
    ) -> pd.DataFrame:
        fetcher = get_fetcher()
        results = []
        
        for ticker, df in price_data.items():
            if df is None or len(df) < self.bb_period + 20:
                continue
            
            try:
                df = fetcher.calculate_technicals(df)
                
                close = df['close']
                
                # Calculate Bollinger Bands
                sma = close.rolling(self.bb_period).mean()
                std = close.rolling(self.bb_period).std()
                upper = sma + (std * self.bb_std)
                lower = sma - (std * self.bb_std)
                
                # Bandwidth (measure of squeeze)
                bandwidth = (upper - lower) / sma * 100
                
                # Check if in squeeze (bandwidth in bottom percentile)
                bw_threshold = bandwidth.rolling(100).quantile(self.squeeze_pct / 100).iloc[-1]
                current_bw = bandwidth.iloc[-1]
                prev_bw = bandwidth.iloc[-5:-1].mean()  # Average of last few days
                
                is_squeeze = current_bw < bw_threshold
                was_squeeze = prev_bw < bw_threshold
                
                # Check for breakout
                current_close = close.iloc[-1]
                current_upper = upper.iloc[-1]
                current_lower = lower.iloc[-1]
                
                breakout_up = current_close > current_upper
                breakout_down = current_close < current_lower
                
                # Volume confirmation
                volume = df['volume'].iloc[-1]
                avg_volume = df['volume'].rolling(20).mean().iloc[-1]
                high_volume = volume > avg_volume * self.volume_confirm
                
                # Determine signal
                if (is_squeeze or was_squeeze) and breakout_up and high_volume:
                    signal_type = "BUY"
                    score = 70 + min(20, (current_close / current_upper - 1) * 500) + (10 if high_volume else 0)
                elif (is_squeeze or was_squeeze) and breakout_down and high_volume:
                    signal_type = "SELL"
                    score = 70 + min(20, (1 - current_close / current_lower) * 500)
                elif is_squeeze:
                    signal_type = "HOLD"
                    score = 55  # Watching for breakout
                else:
                    signal_type = "HOLD"
                    score = 50
                
                score = min(100, max(0, score))
                
                results.append({
                    "ticker": ticker,
                    "score": score,
                    "signal_type": signal_type,
                    "bandwidth": round(current_bw, 2),
                    "is_squeeze": is_squeeze,
                    "breakout_up": breakout_up,
                    "breakout_down": breakout_down,
                    "volume_ratio": round(volume / avg_volume, 2) if avg_volume > 0 else 1.0,
                    "bb_upper": round(current_upper, 2),
                    "bb_lower": round(current_lower, 2)
                })
                
            except Exception as e:
                continue
        
        return pd.DataFrame(results)
