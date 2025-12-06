"""
Market Regime Detector
Identifies bull/bear market conditions and volatility regimes
"""

from typing import Dict, Optional
from dataclasses import dataclass
from datetime import datetime
import pandas as pd
import numpy as np


@dataclass
class MarketRegime:
    """Current market regime assessment"""
    regime: str  # BULL, BEAR, NEUTRAL
    trend_strength: str  # STRONG, MODERATE, WEAK
    volatility_regime: str  # HIGH, NORMAL, LOW
    risk_level: str  # HIGH, MEDIUM, LOW
    recommended_exposure: int  # 0-100%
    signals: Dict[str, bool]
    metrics: Dict[str, float]
    recommendation: str


class MarketRegimeDetector:
    """
    Detects current market regime using multiple indicators.
    
    Indicators used:
    1. Price vs Moving Averages (200-day, 50-day)
    2. Moving Average Trend (slope)
    3. Market Breadth (advance/decline proxy)
    4. Volatility (realized vs historical)
    5. Momentum (rate of change)
    """
    
    def __init__(
        self,
        sma_long: int = 200,
        sma_short: int = 50,
        volatility_window: int = 20
    ):
        self.sma_long = sma_long
        self.sma_short = sma_short
        self.vol_window = volatility_window
    
    def detect_regime(
        self,
        market_index_data: pd.DataFrame,
        universe_data: Optional[Dict[str, pd.DataFrame]] = None
    ) -> MarketRegime:
        """
        Detect market regime from index data and optionally universe data.
        
        Args:
            market_index_data: DataFrame with close prices for market index (e.g., SPY, ^SET)
            universe_data: Optional dict of individual stock price DataFrames
        
        Returns:
            MarketRegime with full assessment
        """
        close = market_index_data['close']
        
        # Calculate indicators
        sma_200 = close.rolling(self.sma_long).mean()
        sma_50 = close.rolling(self.sma_short).mean()
        
        current_price = close.iloc[-1]
        current_sma_200 = sma_200.iloc[-1]
        current_sma_50 = sma_50.iloc[-1]
        
        # Check for NaN values
        if pd.isna(current_sma_200) or pd.isna(current_sma_50):
            raise ValueError(f"Insufficient data for moving averages. Need at least {self.sma_long} days of data.")
        
        # Signals
        signals = {}
        
        # 1. Price vs 200-day MA
        signals['above_200ma'] = current_price > current_sma_200
        
        # 2. Price vs 50-day MA
        signals['above_50ma'] = current_price > current_sma_50
        
        # 3. 50-day above 200-day (Golden/Death Cross)
        signals['golden_cross'] = current_sma_50 > current_sma_200
        
        # 4. 200-day MA slope (trending up) - check for NaN
        if len(sma_200) >= 21 and not pd.isna(sma_200.iloc[-21]):
            sma_200_slope = (sma_200.iloc[-1] / sma_200.iloc[-21] - 1) * 100
            signals['200ma_rising'] = sma_200_slope > 0
        else:
            signals['200ma_rising'] = False
        
        # 5. 50-day MA slope - check for NaN
        if len(sma_50) >= 10 and not pd.isna(sma_50.iloc[-10]):
            sma_50_slope = (sma_50.iloc[-1] / sma_50.iloc[-10] - 1) * 100
            signals['50ma_rising'] = sma_50_slope > 0
        else:
            signals['50ma_rising'] = False
        
        # 6. Price momentum (20-day ROC)
        roc_20 = 0.0  # Initialize
        if len(close) >= 21:
            prev_price = close.iloc[-21]
            if not pd.isna(prev_price) and prev_price > 0:
                roc_20 = (current_price / prev_price - 1) * 100
                signals['positive_momentum'] = roc_20 > 0
            else:
                signals['positive_momentum'] = False
        else:
            signals['positive_momentum'] = False
        
        # 7. Price above 52-week high * 0.9 (within 10%)
        if len(close) >= 252:
            high_52w = close.rolling(252).max().iloc[-1]
            signals['near_highs'] = current_price > high_52w * 0.9 if not pd.isna(high_52w) else False
        else:
            signals['near_highs'] = False
        
        # 8. Price above 52-week low * 1.2 (at least 20% above)
        if len(close) >= 252:
            low_52w = close.rolling(252).min().iloc[-1]
            signals['above_lows'] = current_price > low_52w * 1.2 if not pd.isna(low_52w) else False
        else:
            signals['above_lows'] = False
        
        # Volatility
        returns = close.pct_change().dropna()
        current_vol = returns.tail(self.vol_window).std() * np.sqrt(252) * 100
        historical_vol = returns.std() * np.sqrt(252) * 100
        vol_ratio = current_vol / historical_vol if historical_vol > 0 else 1.0
        
        # Determine volatility regime
        if vol_ratio > 1.3:
            volatility_regime = "HIGH"
        elif vol_ratio < 0.7:
            volatility_regime = "LOW"
        else:
            volatility_regime = "NORMAL"
        
        # Market breadth (if universe data available)
        breadth_score = 50  # Default neutral
        if universe_data:
            advancing = 0
            declining = 0
            total_stocks = 0
            for ticker, df in universe_data.items():
                if df is not None and not df.empty:
                    try:
                        # Check if we have the required columns
                        if 'close' not in df.columns:
                            continue
                        
                        # Ensure we have enough data points
                        if len(df) < 21:
                            continue
                        
                        # Get the last valid close price
                        last_close = df['close'].iloc[-1]
                        if pd.isna(last_close):
                            continue
                        
                        # Get close price 21 days ago (if available)
                        if len(df) >= 21:
                            prev_close = df['close'].iloc[-21]
                            if pd.isna(prev_close) or prev_close == 0:
                                continue
                            
                            ret = (last_close / prev_close - 1) * 100
                            total_stocks += 1
                            if ret > 0:
                                advancing += 1
                            else:
                                declining += 1
                    except (IndexError, KeyError, ValueError) as e:
                        # Skip this ticker if there's any data issue
                        continue
            
            if total_stocks > 0 and advancing + declining > 0:
                breadth_score = (advancing / (advancing + declining)) * 100
                signals['breadth_positive'] = breadth_score > 50
            else:
                # If we couldn't calculate breadth, don't include it in signals
                signals['breadth_positive'] = None
        
        # Count bullish signals (exclude None values)
        valid_signals = {k: v for k, v in signals.items() if v is not None}
        bullish_count = sum(1 for v in valid_signals.values() if v is True)
        total_signals = len(valid_signals)
        bullish_pct = (bullish_count / total_signals * 100) if total_signals > 0 else 50
        
        # Determine regime
        if bullish_pct >= 75:
            regime = "BULL"
            trend_strength = "STRONG"
            risk_level = "LOW"
            recommended_exposure = 100
        elif bullish_pct >= 60:
            regime = "BULL"
            trend_strength = "MODERATE"
            risk_level = "MEDIUM"
            recommended_exposure = 80
        elif bullish_pct >= 40:
            regime = "NEUTRAL"
            trend_strength = "WEAK"
            risk_level = "MEDIUM"
            recommended_exposure = 50
        elif bullish_pct >= 25:
            regime = "BEAR"
            trend_strength = "MODERATE"
            risk_level = "HIGH"
            recommended_exposure = 25
        else:
            regime = "BEAR"
            trend_strength = "STRONG"
            risk_level = "HIGH"
            recommended_exposure = 0
        
        # Adjust for volatility
        if volatility_regime == "HIGH":
            recommended_exposure = max(0, recommended_exposure - 20)
            risk_level = "HIGH"
        
        # Generate recommendation
        if regime == "BULL" and trend_strength == "STRONG":
            recommendation = "Stay fully invested. Strong uptrend. Buy dips."
        elif regime == "BULL":
            recommendation = "Remain invested but be selective. Use trailing stops."
        elif regime == "NEUTRAL":
            recommendation = "Mixed signals. Reduce position sizes. Focus on quality."
        elif regime == "BEAR" and trend_strength == "STRONG":
            recommendation = "Raise cash. Avoid new longs. Consider hedges."
        else:
            recommendation = "Caution warranted. Reduce exposure. Wait for clarity."
        
        # Calculate ROC_20 for metrics (handle case where it wasn't calculated)
        roc_20_value = roc_20 if 'roc_20' in locals() and not pd.isna(roc_20) else 0.0
        
        metrics = {
            "price": round(float(current_price), 2),
            "sma_50": round(float(current_sma_50), 2),
            "sma_200": round(float(current_sma_200), 2),
            "distance_from_200ma_pct": round((float(current_price) / float(current_sma_200) - 1) * 100, 2),
            "roc_20d": round(float(roc_20_value), 2),
            "volatility_annualized": round(float(current_vol), 2),
            "volatility_ratio": round(float(vol_ratio), 2),
            "bullish_signals": int(bullish_count),
            "total_signals": int(total_signals),
            "bullish_pct": round(float(bullish_pct), 1),
            "breadth_score": round(float(breadth_score), 1)
        }
        
        # Clean signals dict - remove None values before creating MarketRegime
        signals_clean = {k: v for k, v in signals.items() if v is not None}
        
        return MarketRegime(
            regime=regime,
            trend_strength=trend_strength,
            volatility_regime=volatility_regime,
            risk_level=risk_level,
            recommended_exposure=recommended_exposure,
            signals=signals_clean,  # Use cleaned signals without None values
            metrics=metrics,
            recommendation=recommendation
        )
    
    def to_dict(self, regime: MarketRegime) -> Dict:
        """Convert MarketRegime to dictionary"""
        # Filter out None values from signals for JSON serialization
        signals_clean = {k: v for k, v in regime.signals.items() if v is not None}
        
        # Ensure all metrics values are JSON-serializable (convert numpy types)
        metrics_clean = {}
        for k, v in regime.metrics.items():
            if isinstance(v, (np.integer, np.floating)):
                metrics_clean[k] = float(v) if isinstance(v, np.floating) else int(v)
            elif isinstance(v, (int, float, str)):
                metrics_clean[k] = v
            else:
                metrics_clean[k] = str(v)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "regime": regime.regime,
            "trend_strength": regime.trend_strength,
            "volatility_regime": regime.volatility_regime,
            "risk_level": regime.risk_level,
            "recommended_exposure": int(regime.recommended_exposure),
            "recommendation": regime.recommendation,
            "signals": signals_clean,
            "metrics": metrics_clean
        }


# Singleton
_detector = None

def get_regime_detector() -> MarketRegimeDetector:
    global _detector
    if _detector is None:
        _detector = MarketRegimeDetector()
    return _detector
