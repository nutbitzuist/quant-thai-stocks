"""
Signal Combiner
Combines signals from multiple models for confirmation
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from collections import defaultdict
import pandas as pd
from datetime import datetime


@dataclass
class CombinedSignal:
    """A combined signal from multiple models"""
    ticker: str
    signal_type: str  # BUY, SELL, HOLD
    confirmation_count: int
    total_models: int
    average_score: float
    models_agreeing: List[str]
    scores_by_model: Dict[str, float]
    strength: str  # STRONG, MODERATE, WEAK


class SignalCombiner:
    """
    Combines signals from multiple models.
    
    Strategies:
    1. Unanimous: All models must agree
    2. Majority: More than half must agree
    3. Threshold: At least N models must agree
    4. Weighted: Weight by model score
    """
    
    def __init__(
        self,
        min_confirmation: int = 3,
        strong_threshold: int = 5,
        moderate_threshold: int = 3
    ):
        self.min_confirmation = min_confirmation
        self.strong_threshold = strong_threshold
        self.moderate_threshold = moderate_threshold
    
    def combine_signals(
        self,
        model_results: Dict[str, Dict],
        signal_type: str = "BUY"
    ) -> List[CombinedSignal]:
        """
        Combine signals from multiple model results.
        
        Args:
            model_results: Dict mapping model_id to result dict with 'buy_signals' or 'sell_signals'
            signal_type: "BUY" or "SELL"
        
        Returns:
            List of CombinedSignals sorted by confirmation count
        """
        signal_key = 'buy_signals' if signal_type == "BUY" else 'sell_signals'
        
        # Aggregate signals by ticker
        ticker_signals = defaultdict(lambda: {
            'models': [],
            'scores': [],
            'signal_type': signal_type
        })
        
        total_models = len(model_results)
        
        for model_id, result in model_results.items():
            signals = result.get(signal_key, [])
            for signal in signals:
                ticker = signal.get('ticker')
                if ticker:
                    ticker_signals[ticker]['models'].append(model_id)
                    ticker_signals[ticker]['scores'].append(signal.get('score', 50))
        
        # Create combined signals
        combined = []
        for ticker, data in ticker_signals.items():
            count = len(data['models'])
            if count >= self.min_confirmation:
                avg_score = sum(data['scores']) / len(data['scores']) if data['scores'] else 0
                
                # Determine strength
                if count >= self.strong_threshold:
                    strength = "STRONG"
                elif count >= self.moderate_threshold:
                    strength = "MODERATE"
                else:
                    strength = "WEAK"
                
                combined.append(CombinedSignal(
                    ticker=ticker,
                    signal_type=signal_type,
                    confirmation_count=count,
                    total_models=total_models,
                    average_score=avg_score,
                    models_agreeing=data['models'],
                    scores_by_model=dict(zip(data['models'], data['scores'])),
                    strength=strength
                ))
        
        # Sort by confirmation count, then by average score
        combined.sort(key=lambda x: (x.confirmation_count, x.average_score), reverse=True)
        
        return combined
    
    def get_consensus_report(
        self,
        model_results: Dict[str, Dict]
    ) -> Dict:
        """Generate a full consensus report"""
        buy_signals = self.combine_signals(model_results, "BUY")
        sell_signals = self.combine_signals(model_results, "SELL")
        
        return {
            "timestamp": datetime.now().isoformat(),
            "total_models_analyzed": len(model_results),
            "min_confirmation": self.min_confirmation,
            "strong_buy_signals": [
                {
                    "ticker": s.ticker,
                    "confirmations": s.confirmation_count,
                    "avg_score": round(s.average_score, 1),
                    "strength": s.strength,
                    "models": s.models_agreeing
                }
                for s in buy_signals if s.strength == "STRONG"
            ],
            "moderate_buy_signals": [
                {
                    "ticker": s.ticker,
                    "confirmations": s.confirmation_count,
                    "avg_score": round(s.average_score, 1),
                    "models": s.models_agreeing
                }
                for s in buy_signals if s.strength == "MODERATE"
            ],
            "strong_sell_signals": [
                {
                    "ticker": s.ticker,
                    "confirmations": s.confirmation_count,
                    "avg_score": round(s.average_score, 1),
                    "strength": s.strength,
                    "models": s.models_agreeing
                }
                for s in sell_signals if s.strength == "STRONG"
            ],
            "all_buy_signals": [
                {
                    "ticker": s.ticker,
                    "confirmations": s.confirmation_count,
                    "avg_score": round(s.average_score, 1),
                    "strength": s.strength,
                    "models": s.models_agreeing
                }
                for s in buy_signals
            ],
            "all_sell_signals": [
                {
                    "ticker": s.ticker,
                    "confirmations": s.confirmation_count,
                    "avg_score": round(s.average_score, 1),
                    "strength": s.strength,
                    "models": s.models_agreeing
                }
                for s in sell_signals
            ]
        }


# Singleton
_combiner = None

def get_signal_combiner() -> SignalCombiner:
    global _combiner
    if _combiner is None:
        _combiner = SignalCombiner()
    return _combiner
