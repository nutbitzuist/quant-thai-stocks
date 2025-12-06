"""
Factor Momentum Model
Momentum of momentum - trend continuation strategy
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional
from app.models.base import QuantitativeModel, SignalType
from app.data.fetcher import get_fetcher


class FactorMomentumModel(QuantitativeModel):
    """
    Factor Momentum Strategy (Momentum of Momentum)
    
    Identifies stocks where momentum itself is accelerating or decelerating.
    - Buy when momentum is positive AND accelerating
    - Sell when momentum is negative AND decelerating
    
    This captures the "momentum crash" avoidance and trend continuation.
    Based on research showing that momentum factor returns are themselves persistent.
    """
    
    def __init__(
        self,
        short_momentum_period: int = 20,
        long_momentum_period: int = 60,
        momentum_change_period: int = 10,
        acceleration_threshold: float = 0.5,
        min_data_points: int = 100
    ):
        super().__init__(
            name="Factor Momentum",
            description="Momentum of momentum - buy accelerating uptrends, sell decelerating downtrends",
            parameters={
                "short_momentum_period": short_momentum_period,
                "long_momentum_period": long_momentum_period,
                "momentum_change_period": momentum_change_period,
                "acceleration_threshold": acceleration_threshold,
                "min_data_points": min_data_points
            }
        )
        self.short_momentum_period = short_momentum_period
        self.long_momentum_period = long_momentum_period
        self.momentum_change_period = momentum_change_period
        self.acceleration_threshold = acceleration_threshold
        self.min_data_points = min_data_points
    
    def calculate_momentum(self, prices: pd.Series, period: int) -> pd.Series:
        """Calculate momentum as percentage return over period"""
        return (prices / prices.shift(period) - 1) * 100
    
    def calculate_momentum_acceleration(self, momentum: pd.Series, period: int) -> pd.Series:
        """Calculate change in momentum (acceleration/deceleration)"""
        return momentum - momentum.shift(period)
    
    def calculate_momentum_quality(self, prices: pd.Series, period: int) -> float:
        """
        Calculate momentum quality (consistency of trend)
        Higher quality = more consistent upward/downward movement
        """
        returns = prices.pct_change().tail(period)
        if returns.empty:
            return 0.0
        
        # Percentage of positive days for uptrend, negative for downtrend
        total_return = (prices.iloc[-1] / prices.iloc[-period] - 1) if len(prices) >= period else 0
        
        if total_return > 0:
            # For uptrend, quality = % of positive days
            quality = (returns > 0).sum() / len(returns)
        else:
            # For downtrend, quality = % of negative days
            quality = (returns < 0).sum() / len(returns)
        
        return quality
    
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
                
                # Calculate short and long momentum
                short_mom = self.calculate_momentum(close, self.short_momentum_period)
                long_mom = self.calculate_momentum(close, self.long_momentum_period)
                
                current_short_mom = short_mom.iloc[-1]
                current_long_mom = long_mom.iloc[-1]
                
                if pd.isna(current_short_mom) or pd.isna(current_long_mom):
                    continue
                
                # Calculate momentum acceleration
                mom_acceleration = self.calculate_momentum_acceleration(
                    short_mom, self.momentum_change_period
                )
                current_acceleration = mom_acceleration.iloc[-1]
                
                if pd.isna(current_acceleration):
                    continue
                
                # Calculate momentum quality
                mom_quality = self.calculate_momentum_quality(
                    close, self.short_momentum_period
                )
                
                # Calculate momentum rank change (factor momentum)
                # This measures if the stock is gaining or losing momentum rank
                prev_short_mom = short_mom.iloc[-self.momentum_change_period] if len(short_mom) > self.momentum_change_period else short_mom.iloc[0]
                
                # Momentum trend (is momentum itself trending?)
                mom_trend = "accelerating" if current_acceleration > self.acceleration_threshold else \
                           "decelerating" if current_acceleration < -self.acceleration_threshold else "stable"
                
                # Determine signal
                # Strong BUY: positive momentum + accelerating
                # Strong SELL: negative momentum + decelerating
                if current_short_mom > 0 and current_acceleration > self.acceleration_threshold:
                    signal_type = "BUY"
                    # Score based on momentum strength and acceleration
                    base_score = 60 + min(20, abs(current_short_mom))
                    accel_bonus = min(20, current_acceleration * 5)
                    quality_bonus = mom_quality * 10
                    score = base_score + accel_bonus + quality_bonus
                    
                elif current_short_mom < 0 and current_acceleration < -self.acceleration_threshold:
                    signal_type = "SELL"
                    base_score = 60 + min(20, abs(current_short_mom))
                    accel_bonus = min(20, abs(current_acceleration) * 5)
                    quality_bonus = mom_quality * 10
                    score = base_score + accel_bonus + quality_bonus
                    
                elif current_short_mom > 5 and current_long_mom > 10:
                    # Strong momentum but not accelerating - still bullish
                    signal_type = "BUY"
                    score = 55 + min(15, current_short_mom / 2)
                    
                elif current_short_mom < -5 and current_long_mom < -10:
                    # Strong negative momentum - bearish
                    signal_type = "SELL"
                    score = 55 + min(15, abs(current_short_mom) / 2)
                    
                else:
                    signal_type = "HOLD"
                    score = 50
                
                score = max(0, min(100, score))
                
                results.append({
                    "ticker": ticker,
                    "score": score,
                    "signal_type": signal_type,
                    "short_momentum": round(current_short_mom, 2),
                    "long_momentum": round(current_long_mom, 2),
                    "momentum_acceleration": round(current_acceleration, 2),
                    "momentum_trend": mom_trend,
                    "momentum_quality": round(mom_quality, 2),
                    "prev_short_momentum": round(prev_short_mom, 2) if not pd.isna(prev_short_mom) else None
                })
                
            except Exception as e:
                continue
        
        return pd.DataFrame(results)
