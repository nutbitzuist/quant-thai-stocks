"""
Volatility Breakout Model
ATR-based entry signals for breakout trading
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional
from app.models.base import QuantitativeModel, SignalType
from app.data.fetcher import get_fetcher


class VolatilityBreakoutModel(QuantitativeModel):
    """
    Volatility Breakout Strategy (ATR-based)
    
    Identifies stocks breaking out of their normal volatility range.
    Uses Average True Range (ATR) to define breakout levels.
    
    - Buy when price breaks above previous close + ATR multiplier
    - Sell when price breaks below previous close - ATR multiplier
    
    Also considers volatility contraction (squeeze) before breakout
    for higher probability setups.
    """
    
    def __init__(
        self,
        atr_period: int = 14,
        atr_multiplier: float = 2.0,
        squeeze_period: int = 20,
        squeeze_threshold: float = 0.7,
        volume_confirmation: bool = True,
        min_data_points: int = 50
    ):
        super().__init__(
            name="Volatility Breakout",
            description="ATR-based breakout entries with volatility squeeze detection",
            parameters={
                "atr_period": atr_period,
                "atr_multiplier": atr_multiplier,
                "squeeze_period": squeeze_period,
                "squeeze_threshold": squeeze_threshold,
                "volume_confirmation": volume_confirmation,
                "min_data_points": min_data_points
            }
        )
        self.atr_period = atr_period
        self.atr_multiplier = atr_multiplier
        self.squeeze_period = squeeze_period
        self.squeeze_threshold = squeeze_threshold
        self.volume_confirmation = volume_confirmation
        self.min_data_points = min_data_points
    
    def calculate_atr(self, df: pd.DataFrame) -> pd.Series:
        """Calculate Average True Range"""
        high = df['high']
        low = df['low']
        close = df['close']
        
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=self.atr_period).mean()
        
        return atr
    
    def calculate_volatility_percentile(self, atr: pd.Series, period: int) -> pd.Series:
        """Calculate where current ATR sits relative to recent history"""
        return atr.rolling(window=period).apply(
            lambda x: (x.iloc[-1] <= x).sum() / len(x) * 100 if len(x) > 0 else 50
        )
    
    def detect_squeeze(self, atr: pd.Series, period: int) -> pd.Series:
        """
        Detect volatility squeeze (contraction)
        Returns True when current ATR is below threshold percentile of recent ATR
        """
        vol_percentile = self.calculate_volatility_percentile(atr, period)
        return vol_percentile < (self.squeeze_threshold * 100)
    
    def calculate_breakout_levels(
        self, 
        df: pd.DataFrame, 
        atr: pd.Series
    ) -> tuple:
        """Calculate upper and lower breakout levels"""
        close = df['close']
        
        upper_breakout = close.shift(1) + (atr * self.atr_multiplier)
        lower_breakout = close.shift(1) - (atr * self.atr_multiplier)
        
        return upper_breakout, lower_breakout
    
    def calculate_scores(
        self,
        price_data: Dict[str, pd.DataFrame],
        fundamental_data: Optional[pd.DataFrame] = None
    ) -> pd.DataFrame:
        results = []
        
        for ticker, df in price_data.items():
            if df is None or len(df) < self.min_data_points:
                continue
            
            try:
                close = df['close']
                high = df['high']
                low = df['low']
                volume = df['volume']
                
                # Calculate ATR
                atr = self.calculate_atr(df)
                current_atr = atr.iloc[-1]
                
                if pd.isna(current_atr):
                    continue
                
                # Calculate breakout levels
                upper_breakout, lower_breakout = self.calculate_breakout_levels(df, atr)
                
                current_price = close.iloc[-1]
                prev_close = close.iloc[-2]
                current_upper = upper_breakout.iloc[-1]
                current_lower = lower_breakout.iloc[-1]
                
                # Check for breakout
                broke_upper = high.iloc[-1] > current_upper
                broke_lower = low.iloc[-1] < current_lower
                
                # Detect squeeze (volatility contraction)
                is_squeeze = self.detect_squeeze(atr, self.squeeze_period).iloc[-1]
                
                # Calculate ATR as percentage of price
                atr_pct = (current_atr / current_price) * 100
                
                # Volume confirmation
                volume_sma = volume.rolling(window=20).mean()
                volume_ratio = volume.iloc[-1] / volume_sma.iloc[-1] if volume_sma.iloc[-1] > 0 else 1
                volume_confirmed = volume_ratio > 1.5
                
                # Calculate volatility percentile
                vol_percentile = self.calculate_volatility_percentile(atr, self.squeeze_period).iloc[-1]
                
                # Distance from breakout levels
                dist_to_upper = ((current_upper - current_price) / current_price) * 100
                dist_to_lower = ((current_price - current_lower) / current_price) * 100
                
                # Determine signal
                if broke_upper:
                    signal_type = "BUY"
                    base_score = 65
                    
                    # Bonus for squeeze breakout
                    if is_squeeze:
                        base_score += 15
                    
                    # Bonus for volume confirmation
                    if self.volume_confirmation and volume_confirmed:
                        base_score += 10
                    
                    # Bonus for strength of breakout
                    breakout_strength = (high.iloc[-1] - current_upper) / current_atr
                    base_score += min(10, breakout_strength * 5)
                    
                    score = base_score
                    
                elif broke_lower:
                    signal_type = "SELL"
                    base_score = 65
                    
                    if is_squeeze:
                        base_score += 15
                    
                    if self.volume_confirmation and volume_confirmed:
                        base_score += 10
                    
                    breakout_strength = (current_lower - low.iloc[-1]) / current_atr
                    base_score += min(10, breakout_strength * 5)
                    
                    score = base_score
                    
                elif is_squeeze:
                    # Squeeze detected but no breakout yet - potential setup
                    signal_type = "HOLD"
                    # Score based on how tight the squeeze is
                    score = 50 + (100 - vol_percentile) / 5
                    
                else:
                    signal_type = "HOLD"
                    score = 50
                
                score = max(0, min(100, score))
                
                results.append({
                    "ticker": ticker,
                    "score": score,
                    "signal_type": signal_type,
                    "current_price": round(current_price, 2),
                    "atr": round(current_atr, 2),
                    "atr_pct": round(atr_pct, 2),
                    "upper_breakout": round(current_upper, 2),
                    "lower_breakout": round(current_lower, 2),
                    "broke_upper": broke_upper,
                    "broke_lower": broke_lower,
                    "is_squeeze": bool(is_squeeze),
                    "volatility_percentile": round(vol_percentile, 1),
                    "volume_ratio": round(volume_ratio, 2),
                    "volume_confirmed": volume_confirmed
                })
                
            except Exception as e:
                continue
        
        return pd.DataFrame(results)
