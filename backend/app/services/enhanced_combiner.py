"""
Enhanced Signal Combiner Service
Allows selecting specific models, weighted voting, and rich context
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging

from app.services.signal_context import (
    SignalContextBuilder, EnhancedSignal, get_signal_context_builder
)

logger = logging.getLogger(__name__)


class CombineMethod(Enum):
    """Methods for combining signals"""
    UNANIMOUS = "unanimous"  # All selected models must agree
    MAJORITY = "majority"  # More than 50% must agree
    WEIGHTED = "weighted"  # Weighted by model performance/confidence
    ANY = "any"  # At least one model signals


@dataclass
class ModelWeight:
    """Weight configuration for a model"""
    model_id: str
    weight: float = 1.0
    enabled: bool = True
    category: str = ""  # technical, fundamental, quantitative


@dataclass
class CombinedSignal:
    """Result of combining multiple model signals"""
    ticker: str
    final_signal: str  # BUY, SELL, HOLD
    confidence: float  # 0-100
    
    # Voting details
    buy_votes: int
    sell_votes: int
    hold_votes: int
    total_models: int
    
    # Weighted scores
    weighted_buy_score: float
    weighted_sell_score: float
    
    # Model breakdown
    agreeing_models: List[str]
    disagreeing_models: List[str]
    model_signals: Dict[str, str]  # model_id -> signal
    model_scores: Dict[str, float]  # model_id -> score
    
    # Aggregate metrics
    avg_score: float
    max_score: float
    min_score: float
    score_std: float
    
    # Enhanced context (optional)
    enhanced_context: Optional[EnhancedSignal] = None
    
    def to_dict(self) -> Dict:
        return {
            "ticker": self.ticker,
            "final_signal": self.final_signal,
            "confidence": round(self.confidence, 1),
            "confidence_label": self._get_confidence_label(),
            "voting": {
                "buy": self.buy_votes,
                "sell": self.sell_votes,
                "hold": self.hold_votes,
                "total": self.total_models,
            },
            "weighted_scores": {
                "buy": round(self.weighted_buy_score, 2),
                "sell": round(self.weighted_sell_score, 2),
            },
            "agreeing_models": self.agreeing_models,
            "disagreeing_models": self.disagreeing_models,
            "model_signals": self.model_signals,
            "model_scores": {k: round(v, 2) for k, v in self.model_scores.items()},
            "aggregate_metrics": {
                "avg_score": round(self.avg_score, 2),
                "max_score": round(self.max_score, 2),
                "min_score": round(self.min_score, 2),
                "score_std": round(self.score_std, 2),
            },
            "enhanced_context": self.enhanced_context.to_dict() if self.enhanced_context else None,
        }
    
    def _get_confidence_label(self) -> str:
        if self.confidence >= 90:
            return "Very High"
        elif self.confidence >= 75:
            return "High"
        elif self.confidence >= 60:
            return "Moderate"
        elif self.confidence >= 40:
            return "Low"
        else:
            return "Very Low"


class EnhancedSignalCombiner:
    """
    Enhanced signal combiner with:
    - Model selection (choose which models to include)
    - Weighted voting (assign weights to models)
    - Multiple combination methods
    - Rich context generation
    """
    
    # Default model weights (can be customized)
    DEFAULT_WEIGHTS = {
        # Technical models
        "rsi_reversal": 1.0,
        "macd_crossover": 1.0,
        "minervini_trend": 1.2,
        "darvas_box": 1.0,
        "turtle_trading": 1.1,
        "elder_triple_screen": 1.1,
        "bollinger_squeeze": 1.0,
        "adx_trend": 1.0,
        "keltner_channel": 1.0,
        "volume_profile": 0.9,
        "dual_ema": 0.9,
        
        # Fundamental models
        "canslim": 1.3,
        "value_composite": 1.2,
        "quality_score": 1.1,
        "piotroski_f": 1.2,
        "magic_formula": 1.2,
        "dividend_aristocrats": 1.0,
        "earnings_momentum": 1.1,
        "garp": 1.1,
        "altman_z": 1.0,
        "ev_ebitda": 1.1,
        "fcf_yield": 1.1,
        "momentum_value": 1.2,
        
        # Quantitative models
        "mean_reversion": 1.0,
        "pairs_trading": 0.9,
        "factor_momentum": 1.1,
        "volatility_breakout": 1.0,
    }
    
    def __init__(self):
        self.model_weights: Dict[str, ModelWeight] = {}
        self.model_results: Dict[str, Any] = {}
        self.context_builder = get_signal_context_builder()
        
        # Initialize with default weights
        for model_id, weight in self.DEFAULT_WEIGHTS.items():
            self.model_weights[model_id] = ModelWeight(
                model_id=model_id,
                weight=weight,
                enabled=True
            )
    
    def set_model_weight(self, model_id: str, weight: float, enabled: bool = True):
        """Set weight for a specific model"""
        self.model_weights[model_id] = ModelWeight(
            model_id=model_id,
            weight=weight,
            enabled=enabled
        )
    
    def set_model_weights(self, weights: Dict[str, float]):
        """Set weights for multiple models"""
        for model_id, weight in weights.items():
            self.set_model_weight(model_id, weight)
    
    def enable_models(self, model_ids: List[str]):
        """Enable only specific models (disable all others)"""
        for model_id in self.model_weights:
            self.model_weights[model_id].enabled = model_id in model_ids
    
    def disable_models(self, model_ids: List[str]):
        """Disable specific models"""
        for model_id in model_ids:
            if model_id in self.model_weights:
                self.model_weights[model_id].enabled = False
    
    def add_model_result(self, model_id: str, result: Any):
        """Add result from a model run"""
        self.model_results[model_id] = result
        self.context_builder.set_model_results(model_id, result)
    
    def get_enabled_models(self) -> List[str]:
        """Get list of enabled model IDs"""
        return [m.model_id for m in self.model_weights.values() if m.enabled]
    
    def combine_signals(
        self,
        method: CombineMethod = CombineMethod.WEIGHTED,
        min_models: int = 2,
        min_confidence: float = 50.0,
        include_context: bool = True,
        price_data: Optional[Dict[str, pd.DataFrame]] = None,
        fundamental_data: Optional[pd.DataFrame] = None,
        market_regime: Optional[Dict] = None
    ) -> List[CombinedSignal]:
        """
        Combine signals from all enabled models
        
        Args:
            method: How to combine signals
            min_models: Minimum models that must have data for a ticker
            min_confidence: Minimum confidence to include in results
            include_context: Whether to generate enhanced context
            price_data: Price data for context generation
            fundamental_data: Fundamental data for context generation
            market_regime: Current market regime
        
        Returns:
            List of combined signals sorted by confidence
        """
        
        # Set context data
        if price_data:
            self.context_builder.set_price_data(price_data)
        if fundamental_data is not None:
            self.context_builder.set_fundamental_data(fundamental_data)
        if market_regime:
            self.context_builder.set_market_regime(market_regime)
        
        # Collect all signals by ticker
        ticker_signals: Dict[str, Dict[str, Tuple[str, float]]] = {}  # ticker -> {model_id: (signal, score)}
        
        enabled_models = self.get_enabled_models()
        
        for model_id, result in self.model_results.items():
            if model_id not in enabled_models:
                continue
            
            if not hasattr(result, 'rankings'):
                continue
            
            for ranking in result.rankings:
                ticker = ranking.get('ticker')
                signal = ranking.get('signal', 'HOLD')
                score = ranking.get('score', 50)
                
                if ticker not in ticker_signals:
                    ticker_signals[ticker] = {}
                
                ticker_signals[ticker][model_id] = (signal, score)
        
        # Combine signals for each ticker
        combined_signals = []
        
        for ticker, model_data in ticker_signals.items():
            if len(model_data) < min_models:
                continue
            
            combined = self._combine_ticker_signals(
                ticker, model_data, method, include_context
            )
            
            if combined.confidence >= min_confidence:
                combined_signals.append(combined)
        
        # Sort by confidence
        combined_signals.sort(key=lambda x: x.confidence, reverse=True)
        
        return combined_signals
    
    def _combine_ticker_signals(
        self,
        ticker: str,
        model_data: Dict[str, Tuple[str, float]],
        method: CombineMethod,
        include_context: bool
    ) -> CombinedSignal:
        """Combine signals for a single ticker"""
        
        buy_votes = 0
        sell_votes = 0
        hold_votes = 0
        
        weighted_buy = 0.0
        weighted_sell = 0.0
        weighted_hold = 0.0
        total_weight = 0.0
        
        model_signals = {}
        model_scores = {}
        scores = []
        
        for model_id, (signal, score) in model_data.items():
            weight = self.model_weights.get(model_id, ModelWeight(model_id, 1.0)).weight
            
            model_signals[model_id] = signal
            model_scores[model_id] = score
            scores.append(score)
            
            if signal == "BUY":
                buy_votes += 1
                weighted_buy += weight * score
            elif signal == "SELL":
                sell_votes += 1
                weighted_sell += weight * score
            else:
                hold_votes += 1
                weighted_hold += weight * 50  # Neutral score for hold
            
            total_weight += weight
        
        # Normalize weighted scores
        if total_weight > 0:
            weighted_buy /= total_weight
            weighted_sell /= total_weight
            weighted_hold /= total_weight
        
        # Determine final signal based on method
        total_votes = buy_votes + sell_votes + hold_votes
        
        if method == CombineMethod.UNANIMOUS:
            if buy_votes == total_votes:
                final_signal = "BUY"
                confidence = 100.0
            elif sell_votes == total_votes:
                final_signal = "SELL"
                confidence = 100.0
            else:
                final_signal = "HOLD"
                confidence = max(buy_votes, sell_votes, hold_votes) / total_votes * 100
        
        elif method == CombineMethod.MAJORITY:
            if buy_votes > total_votes / 2:
                final_signal = "BUY"
                confidence = buy_votes / total_votes * 100
            elif sell_votes > total_votes / 2:
                final_signal = "SELL"
                confidence = sell_votes / total_votes * 100
            else:
                final_signal = "HOLD"
                confidence = hold_votes / total_votes * 100 if hold_votes > 0 else 50
        
        elif method == CombineMethod.WEIGHTED:
            if weighted_buy > weighted_sell and weighted_buy > weighted_hold:
                final_signal = "BUY"
                confidence = min(100, weighted_buy)
            elif weighted_sell > weighted_buy and weighted_sell > weighted_hold:
                final_signal = "SELL"
                confidence = min(100, weighted_sell)
            else:
                final_signal = "HOLD"
                confidence = 50 + (max(weighted_buy, weighted_sell) - 50) * 0.5
        
        else:  # ANY
            if buy_votes > 0:
                final_signal = "BUY"
                confidence = buy_votes / total_votes * 100
            elif sell_votes > 0:
                final_signal = "SELL"
                confidence = sell_votes / total_votes * 100
            else:
                final_signal = "HOLD"
                confidence = 50
        
        # Determine agreeing/disagreeing models
        agreeing = [m for m, s in model_signals.items() if s == final_signal]
        disagreeing = [m for m, s in model_signals.items() if s != final_signal and s != "HOLD"]
        
        # Calculate aggregate metrics
        avg_score = np.mean(scores) if scores else 50
        max_score = max(scores) if scores else 50
        min_score = min(scores) if scores else 50
        score_std = np.std(scores) if len(scores) > 1 else 0
        
        # Build enhanced context if requested
        enhanced_context = None
        if include_context and final_signal != "HOLD":
            try:
                enhanced_context = self.context_builder.build_enhanced_signal(
                    ticker=ticker,
                    signal_type=final_signal,
                    score=avg_score,
                    model_id="combined",
                    all_scores=scores
                )
            except Exception as e:
                logger.warning(f"Failed to build context for {ticker}: {e}")
        
        return CombinedSignal(
            ticker=ticker,
            final_signal=final_signal,
            confidence=confidence,
            buy_votes=buy_votes,
            sell_votes=sell_votes,
            hold_votes=hold_votes,
            total_models=total_votes,
            weighted_buy_score=weighted_buy,
            weighted_sell_score=weighted_sell,
            agreeing_models=agreeing,
            disagreeing_models=disagreeing,
            model_signals=model_signals,
            model_scores=model_scores,
            avg_score=avg_score,
            max_score=max_score,
            min_score=min_score,
            score_std=score_std,
            enhanced_context=enhanced_context
        )
    
    def get_model_agreement_matrix(self) -> pd.DataFrame:
        """
        Generate a matrix showing how often models agree with each other
        Useful for understanding model correlations
        """
        enabled_models = self.get_enabled_models()
        
        # Collect signals by ticker
        ticker_signals: Dict[str, Dict[str, str]] = {}
        
        for model_id, result in self.model_results.items():
            if model_id not in enabled_models:
                continue
            if not hasattr(result, 'rankings'):
                continue
            
            for ranking in result.rankings:
                ticker = ranking.get('ticker')
                signal = ranking.get('signal', 'HOLD')
                
                if ticker not in ticker_signals:
                    ticker_signals[ticker] = {}
                ticker_signals[ticker][model_id] = signal
        
        # Calculate agreement rates
        agreement_matrix = {}
        
        for model1 in enabled_models:
            agreement_matrix[model1] = {}
            for model2 in enabled_models:
                if model1 == model2:
                    agreement_matrix[model1][model2] = 100.0
                    continue
                
                agreements = 0
                total = 0
                
                for ticker, signals in ticker_signals.items():
                    if model1 in signals and model2 in signals:
                        total += 1
                        if signals[model1] == signals[model2]:
                            agreements += 1
                
                agreement_matrix[model1][model2] = (agreements / total * 100) if total > 0 else 0
        
        return pd.DataFrame(agreement_matrix)


# Singleton instance
_enhanced_combiner: Optional[EnhancedSignalCombiner] = None


def get_enhanced_combiner() -> EnhancedSignalCombiner:
    """Get singleton instance"""
    global _enhanced_combiner
    if _enhanced_combiner is None:
        _enhanced_combiner = EnhancedSignalCombiner()
    return _enhanced_combiner


def reset_enhanced_combiner():
    """Reset the singleton (useful for testing)"""
    global _enhanced_combiner
    _enhanced_combiner = None
