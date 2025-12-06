"""
Volume Profile Model
Identifies support/resistance based on volume concentration
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional
from app.models.base import TechnicalModel, SignalType
from app.data.fetcher import get_fetcher


class VolumeProfileModel(TechnicalModel):
    """
    Volume Profile Analysis
    
    Analyzes where the most trading volume occurs at different price levels.
    
    Key concepts:
    - Value Area: Price range where 70% of volume occurs
    - POC (Point of Control): Price level with highest volume
    - High Volume Node (HVN): Price levels with significant volume (support/resistance)
    - Low Volume Node (LVN): Price levels with little volume (price moves quickly through)
    
    Strategy:
    - Buy near support (HVN below current price)
    - Sell near resistance (HVN above current price)
    - Breakout above POC with volume = strong buy
    """
    
    def __init__(
        self,
        lookback_days: int = 60,
        num_bins: int = 20,
        value_area_pct: float = 70
    ):
        super().__init__(
            name="Volume Profile",
            description="Support/resistance based on volume concentration at price levels",
            parameters={
                "lookback_days": lookback_days,
                "num_bins": num_bins,
                "value_area_pct": value_area_pct
            }
        )
        self.lookback = lookback_days
        self.num_bins = num_bins
        self.value_area = value_area_pct
    
    def _calculate_volume_profile(self, df: pd.DataFrame) -> Dict:
        """Calculate volume profile for the lookback period"""
        recent = df.tail(self.lookback)
        
        # Create price bins
        price_range = recent['high'].max() - recent['low'].min()
        bin_size = price_range / self.num_bins
        
        min_price = recent['low'].min()
        
        # Allocate volume to bins
        volume_by_bin = {}
        for i in range(self.num_bins):
            bin_low = min_price + i * bin_size
            bin_high = bin_low + bin_size
            bin_mid = (bin_low + bin_high) / 2
            volume_by_bin[bin_mid] = 0
        
        for _, row in recent.iterrows():
            # Distribute volume across the day's range
            day_low = row['low']
            day_high = row['high']
            day_volume = row['volume']
            
            for bin_mid in volume_by_bin.keys():
                bin_low = bin_mid - bin_size / 2
                bin_high = bin_mid + bin_size / 2
                
                # Check overlap
                overlap_low = max(day_low, bin_low)
                overlap_high = min(day_high, bin_high)
                
                if overlap_high > overlap_low:
                    day_range = day_high - day_low if day_high > day_low else 1
                    overlap_pct = (overlap_high - overlap_low) / day_range
                    volume_by_bin[bin_mid] += day_volume * overlap_pct
        
        # Find POC (Point of Control)
        poc = max(volume_by_bin.keys(), key=lambda k: volume_by_bin[k])
        
        # Calculate Value Area
        total_volume = sum(volume_by_bin.values())
        target_volume = total_volume * (self.value_area / 100)
        
        sorted_bins = sorted(volume_by_bin.items(), key=lambda x: x[1], reverse=True)
        cumulative_volume = 0
        value_area_prices = []
        
        for price, vol in sorted_bins:
            cumulative_volume += vol
            value_area_prices.append(price)
            if cumulative_volume >= target_volume:
                break
        
        vah = max(value_area_prices) if value_area_prices else poc  # Value Area High
        val = min(value_area_prices) if value_area_prices else poc  # Value Area Low
        
        return {
            "poc": poc,
            "vah": vah,
            "val": val,
            "volume_by_bin": volume_by_bin,
            "total_volume": total_volume
        }
    
    def calculate_scores(
        self,
        price_data: Dict[str, pd.DataFrame],
        fundamental_data: Optional[pd.DataFrame] = None
    ) -> pd.DataFrame:
        results = []
        
        for ticker, df in price_data.items():
            if df is None or len(df) < self.lookback:
                continue
            
            try:
                profile = self._calculate_volume_profile(df)
                
                current_close = df['close'].iloc[-1]
                poc = profile['poc']
                vah = profile['vah']
                val = profile['val']
                
                # Determine position relative to volume profile
                above_poc = current_close > poc
                above_vah = current_close > vah
                below_val = current_close < val
                in_value_area = val <= current_close <= vah
                
                # Calculate score based on position and momentum
                recent_volume = df['volume'].iloc[-5:].mean()
                avg_volume = df['volume'].iloc[-20:].mean()
                volume_surge = recent_volume > avg_volume * 1.3
                
                # Price momentum
                mom_5d = (current_close / df['close'].iloc[-6] - 1) * 100
                
                if above_vah and volume_surge and mom_5d > 0:
                    # Breakout above value area with volume
                    signal_type = "BUY"
                    score = 75 + min(15, mom_5d * 2)
                elif below_val and volume_surge and mom_5d < 0:
                    # Breakdown below value area with volume
                    signal_type = "SELL"
                    score = 75 + min(15, abs(mom_5d) * 2)
                elif in_value_area and current_close < poc:
                    # In value area, below POC (potential support)
                    signal_type = "BUY" if mom_5d > 0 else "HOLD"
                    score = 55 + (10 if mom_5d > 0 else 0)
                elif in_value_area and current_close > poc:
                    # In value area, above POC (potential resistance)
                    signal_type = "HOLD"
                    score = 50
                else:
                    signal_type = "HOLD"
                    score = 50
                
                score = min(100, max(0, score))
                
                results.append({
                    "ticker": ticker,
                    "score": score,
                    "signal_type": signal_type,
                    "price": round(current_close, 2),
                    "poc": round(poc, 2),
                    "value_area_high": round(vah, 2),
                    "value_area_low": round(val, 2),
                    "position": "Above VAH" if above_vah else "Below VAL" if below_val else "In Value Area",
                    "volume_surge": volume_surge,
                    "momentum_5d": round(mom_5d, 2)
                })
                
            except Exception as e:
                continue
        
        return pd.DataFrame(results)
