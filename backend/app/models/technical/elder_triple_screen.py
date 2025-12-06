"""
Elder Triple Screen Model with Force Index
Dr. Alexander Elder's multi-timeframe trading system
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional
from app.models.base import TechnicalModel, SignalType
from app.data.fetcher import get_fetcher


class ElderTripleScreenModel(TechnicalModel):
    """
    Elder Triple Screen Trading System
    
    Screen 1 (Weekly/Trend): Identify trend using weekly EMA slope
    Screen 2 (Daily/Momentum): Use oscillator for timing (Force Index, Elder Ray)
    Screen 3 (Intraday/Entry): Use trailing stops for precise entry
    
    Force Index = (Close - Previous Close) * Volume
    - Positive: Bulls in control
    - Negative: Bears in control
    
    Buy when:
    1. Weekly trend is up (EMA rising)
    2. Daily Force Index is negative (pullback in uptrend)
    3. Price above trailing stop
    
    This is adapted for daily data only (weekly simulated via 5-day periods)
    """
    
    def __init__(
        self,
        trend_period: int = 26,  # ~5 weeks
        force_period: int = 13,
        short_force_period: int = 2,
        atr_multiplier: float = 2.0
    ):
        super().__init__(
            name="Elder Triple Screen",
            description="Multi-timeframe system with Force Index for pullback entries",
            parameters={
                "trend_period": trend_period,
                "force_period": force_period,
                "short_force_period": short_force_period,
                "atr_multiplier": atr_multiplier
            }
        )
        self.trend_period = trend_period
        self.force_period = force_period
        self.short_force_period = short_force_period
        self.atr_multiplier = atr_multiplier
    
    def _calculate_force_index(self, df: pd.DataFrame, period: int) -> pd.Series:
        """Calculate Force Index: (Close - Prev Close) * Volume"""
        price_change = df['close'].diff()
        force = price_change * df['volume']
        return force.ewm(span=period, adjust=False).mean()
    
    def _calculate_elder_ray(self, df: pd.DataFrame, period: int = 13) -> tuple:
        """
        Calculate Elder Ray (Bull Power and Bear Power)
        Bull Power = High - EMA
        Bear Power = Low - EMA
        """
        ema = df['close'].ewm(span=period, adjust=False).mean()
        bull_power = df['high'] - ema
        bear_power = df['low'] - ema
        return bull_power, bear_power
    
    def calculate_scores(
        self,
        price_data: Dict[str, pd.DataFrame],
        fundamental_data: Optional[pd.DataFrame] = None
    ) -> pd.DataFrame:
        fetcher = get_fetcher()
        results = []
        
        for ticker, df in price_data.items():
            if df is None or len(df) < self.trend_period + 20:
                continue
            
            try:
                df = fetcher.calculate_technicals(df)
                
                close = df['close'].iloc[-1]
                
                # Screen 1: Trend (weekly-equivalent)
                ema_long = df['close'].ewm(span=self.trend_period, adjust=False).mean()
                ema_slope = (ema_long.iloc[-1] - ema_long.iloc[-5]) / ema_long.iloc[-5] * 100
                trend_up = ema_slope > 0
                trend_down = ema_slope < 0
                
                # Screen 2: Force Index (momentum)
                force_index = self._calculate_force_index(df, self.force_period)
                force_short = self._calculate_force_index(df, self.short_force_period)
                
                current_force = force_index.iloc[-1]
                current_force_short = force_short.iloc[-1]
                prev_force_short = force_short.iloc[-2]
                
                # Normalize force index for scoring
                force_std = force_index.std()
                force_z = current_force / force_std if force_std > 0 else 0
                
                # Elder Ray
                bull_power, bear_power = self._calculate_elder_ray(df, 13)
                current_bull = bull_power.iloc[-1]
                current_bear = bear_power.iloc[-1]
                
                # Screen 3: Entry conditions
                atr = df['atr'].iloc[-1]
                trailing_stop = close - (atr * self.atr_multiplier)
                
                # Signal logic
                # BUY: Uptrend + Force Index crossing from negative to positive (pullback ending)
                # SELL: Downtrend + Force Index crossing from positive to negative
                
                force_turning_up = current_force_short > prev_force_short and current_force_short > 0 and prev_force_short < 0
                force_turning_down = current_force_short < prev_force_short and current_force_short < 0 and prev_force_short > 0
                
                # Alternative: Buy in uptrend when Force Index is negative (dip buying)
                dip_in_uptrend = trend_up and current_force < 0 and current_bull > 0
                rally_in_downtrend = trend_down and current_force > 0 and current_bear < 0
                
                if trend_up and (force_turning_up or dip_in_uptrend):
                    signal_type = "BUY"
                    score = 60 + min(20, abs(ema_slope) * 10) + min(20, current_bull / atr * 5)
                elif trend_down and (force_turning_down or rally_in_downtrend):
                    signal_type = "SELL"
                    score = 60 + min(20, abs(ema_slope) * 10) + min(20, abs(current_bear) / atr * 5)
                else:
                    signal_type = "HOLD"
                    score = 50 + force_z * 10  # Slight bias based on force direction
                
                score = min(100, max(0, score))
                
                results.append({
                    "ticker": ticker,
                    "score": score,
                    "signal_type": signal_type,
                    "trend": "UP" if trend_up else ("DOWN" if trend_down else "NEUTRAL"),
                    "trend_slope_pct": round(ema_slope, 2),
                    "force_index": round(current_force, 0),
                    "force_z_score": round(force_z, 2),
                    "bull_power": round(current_bull, 2),
                    "bear_power": round(current_bear, 2),
                    "trailing_stop": round(trailing_stop, 2),
                    "atr": round(atr, 2)
                })
                
            except Exception as e:
                continue
        
        return pd.DataFrame(results)
