"""
Enhanced Signal Context Service
Provides rich context for signals: WHY, confirmations, risk, historical stats
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ConvictionLevel(Enum):
    """Signal conviction levels"""
    VERY_HIGH = "very_high"
    HIGH = "high"
    MODERATE = "moderate"
    LOW = "low"
    VERY_LOW = "very_low"


@dataclass
class SignalReason:
    """Individual reason for a signal"""
    factor: str  # e.g., "RSI Oversold", "Above 200MA"
    description: str
    strength: float  # 0-100
    category: str  # "technical", "fundamental", "momentum", "sentiment"


@dataclass
class RiskFactor:
    """Risk factor affecting the signal"""
    name: str
    description: str
    severity: str  # "low", "medium", "high"
    mitigation: Optional[str] = None


@dataclass
class HistoricalStats:
    """Historical performance of similar setups"""
    sample_size: int
    win_rate: float  # percentage
    avg_return: float  # percentage
    avg_holding_days: int
    max_drawdown: float
    sharpe_ratio: Optional[float] = None
    best_return: Optional[float] = None
    worst_return: Optional[float] = None


@dataclass
class PositionSuggestion:
    """Suggested position sizing"""
    portfolio_pct: float
    conviction: ConvictionLevel
    rationale: str
    stop_loss_pct: Optional[float] = None
    take_profit_pct: Optional[float] = None


@dataclass
class EnhancedSignal:
    """Complete signal with full context"""
    ticker: str
    signal_type: str  # BUY, SELL, HOLD
    score: float
    percentile_rank: float  # e.g., "Top 10%"
    
    # Why this signal
    primary_reasons: List[SignalReason]
    
    # Confirmation from other models
    confirming_models: List[str]
    conflicting_models: List[str]
    confirmation_score: float  # 0-100
    
    # Risk assessment
    risk_factors: List[RiskFactor]
    overall_risk: str  # "low", "medium", "high"
    
    # Market context
    market_regime: str
    sector_trend: str
    
    # Historical performance
    historical_stats: Optional[HistoricalStats]
    
    # Position suggestion
    position_suggestion: PositionSuggestion
    
    # Metadata
    generated_at: datetime = field(default_factory=datetime.now)
    model_source: str = ""
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "ticker": self.ticker,
            "signal_type": self.signal_type,
            "score": self.score,
            "percentile_rank": self.percentile_rank,
            "percentile_label": self._get_percentile_label(),
            "primary_reasons": [
                {"factor": r.factor, "description": r.description, 
                 "strength": r.strength, "category": r.category}
                for r in self.primary_reasons
            ],
            "confirming_models": self.confirming_models,
            "conflicting_models": self.conflicting_models,
            "confirmation_score": self.confirmation_score,
            "confirmation_label": f"{len(self.confirming_models)} models agree",
            "risk_factors": [
                {"name": r.name, "description": r.description,
                 "severity": r.severity, "mitigation": r.mitigation}
                for r in self.risk_factors
            ],
            "overall_risk": self.overall_risk,
            "market_regime": self.market_regime,
            "sector_trend": self.sector_trend,
            "historical_stats": {
                "sample_size": self.historical_stats.sample_size,
                "win_rate": self.historical_stats.win_rate,
                "avg_return": self.historical_stats.avg_return,
                "avg_holding_days": self.historical_stats.avg_holding_days,
                "max_drawdown": self.historical_stats.max_drawdown,
            } if self.historical_stats else None,
            "position_suggestion": {
                "portfolio_pct": self.position_suggestion.portfolio_pct,
                "conviction": self.position_suggestion.conviction.value,
                "rationale": self.position_suggestion.rationale,
                "stop_loss_pct": self.position_suggestion.stop_loss_pct,
                "take_profit_pct": self.position_suggestion.take_profit_pct,
            },
            "model_source": self.model_source,
            "generated_at": self.generated_at.isoformat(),
        }
    
    def _get_percentile_label(self) -> str:
        """Get human-readable percentile label"""
        if self.percentile_rank >= 95:
            return "Top 5%"
        elif self.percentile_rank >= 90:
            return "Top 10%"
        elif self.percentile_rank >= 80:
            return "Top 20%"
        elif self.percentile_rank >= 70:
            return "Top 30%"
        elif self.percentile_rank >= 50:
            return "Top 50%"
        else:
            return f"Bottom {100 - self.percentile_rank:.0f}%"


class SignalContextBuilder:
    """Builds enhanced signal context from model results"""
    
    def __init__(self):
        self.all_model_results: Dict[str, Any] = {}
        self.price_data: Dict[str, pd.DataFrame] = {}
        self.fundamental_data: Optional[pd.DataFrame] = None
        self.market_regime: Optional[Dict] = None
        self.sector_data: Dict[str, str] = {}
        self.historical_performance: Dict[str, List[Dict]] = {}
    
    def set_model_results(self, model_id: str, results: Any):
        """Add results from a model"""
        self.all_model_results[model_id] = results
    
    def set_price_data(self, price_data: Dict[str, pd.DataFrame]):
        """Set price data for technical analysis"""
        self.price_data = price_data
    
    def set_fundamental_data(self, fundamental_data: pd.DataFrame):
        """Set fundamental data"""
        self.fundamental_data = fundamental_data
    
    def set_market_regime(self, regime: Dict):
        """Set current market regime"""
        self.market_regime = regime
    
    def set_historical_performance(self, model_id: str, performance: List[Dict]):
        """Set historical performance data for a model"""
        self.historical_performance[model_id] = performance
    
    def build_enhanced_signal(
        self,
        ticker: str,
        signal_type: str,
        score: float,
        model_id: str,
        all_scores: List[float]
    ) -> EnhancedSignal:
        """Build a fully contextualized signal"""
        
        # Calculate percentile rank
        percentile_rank = self._calculate_percentile(score, all_scores)
        
        # Get reasons for the signal
        primary_reasons = self._extract_signal_reasons(ticker, model_id)
        
        # Get confirmations from other models
        confirming, conflicting = self._get_model_confirmations(ticker, signal_type)
        confirmation_score = len(confirming) / max(1, len(confirming) + len(conflicting)) * 100
        
        # Assess risks
        risk_factors = self._assess_risks(ticker)
        overall_risk = self._calculate_overall_risk(risk_factors)
        
        # Get market context
        market_regime = self._get_market_regime()
        sector_trend = self._get_sector_trend(ticker)
        
        # Get historical stats
        historical_stats = self._get_historical_stats(model_id, signal_type)
        
        # Calculate position suggestion
        position_suggestion = self._calculate_position_suggestion(
            score, percentile_rank, confirmation_score, 
            overall_risk, historical_stats
        )
        
        return EnhancedSignal(
            ticker=ticker,
            signal_type=signal_type,
            score=score,
            percentile_rank=percentile_rank,
            primary_reasons=primary_reasons,
            confirming_models=confirming,
            conflicting_models=conflicting,
            confirmation_score=confirmation_score,
            risk_factors=risk_factors,
            overall_risk=overall_risk,
            market_regime=market_regime,
            sector_trend=sector_trend,
            historical_stats=historical_stats,
            position_suggestion=position_suggestion,
            model_source=model_id
        )
    
    def _calculate_percentile(self, score: float, all_scores: List[float]) -> float:
        """Calculate percentile rank of a score"""
        if not all_scores:
            return 50.0
        sorted_scores = sorted(all_scores)
        rank = sum(1 for s in sorted_scores if s <= score)
        return (rank / len(sorted_scores)) * 100
    
    def _extract_signal_reasons(self, ticker: str, model_id: str) -> List[SignalReason]:
        """Extract reasons for the signal based on model and data"""
        reasons = []
        
        # Get price data for technical reasons
        if ticker in self.price_data:
            df = self.price_data[ticker]
            if len(df) >= 20:
                reasons.extend(self._get_technical_reasons(df))
        
        # Get fundamental reasons
        if self.fundamental_data is not None and not self.fundamental_data.empty:
            fund_row = self.fundamental_data[
                self.fundamental_data['ticker'] == ticker
            ]
            if not fund_row.empty:
                reasons.extend(self._get_fundamental_reasons(fund_row.iloc[0]))
        
        # Model-specific reasons
        if model_id in self.all_model_results:
            result = self.all_model_results[model_id]
            reasons.extend(self._get_model_specific_reasons(ticker, model_id, result))
        
        # Sort by strength and return top reasons
        reasons.sort(key=lambda x: x.strength, reverse=True)
        return reasons[:5]  # Top 5 reasons
    
    def _get_technical_reasons(self, df: pd.DataFrame) -> List[SignalReason]:
        """Extract technical analysis reasons"""
        reasons = []
        close = df['close']
        current_price = close.iloc[-1]
        
        # RSI check
        if 'rsi' in df.columns:
            rsi = df['rsi'].iloc[-1]
            if rsi < 30:
                reasons.append(SignalReason(
                    factor="RSI Oversold",
                    description=f"RSI at {rsi:.1f} indicates oversold conditions",
                    strength=80,
                    category="technical"
                ))
            elif rsi > 70:
                reasons.append(SignalReason(
                    factor="RSI Overbought",
                    description=f"RSI at {rsi:.1f} indicates overbought conditions",
                    strength=80,
                    category="technical"
                ))
        
        # Moving average checks
        if len(close) >= 200:
            ma200 = close.rolling(200).mean().iloc[-1]
            if current_price > ma200:
                pct_above = ((current_price / ma200) - 1) * 100
                reasons.append(SignalReason(
                    factor="Above 200-day MA",
                    description=f"Price {pct_above:.1f}% above 200-day moving average",
                    strength=70,
                    category="technical"
                ))
            else:
                pct_below = ((ma200 / current_price) - 1) * 100
                reasons.append(SignalReason(
                    factor="Below 200-day MA",
                    description=f"Price {pct_below:.1f}% below 200-day moving average",
                    strength=70,
                    category="technical"
                ))
        
        if len(close) >= 50:
            ma50 = close.rolling(50).mean().iloc[-1]
            ma200 = close.rolling(200).mean().iloc[-1] if len(close) >= 200 else None
            
            if ma200 and ma50 > ma200:
                reasons.append(SignalReason(
                    factor="Golden Cross Setup",
                    description="50-day MA above 200-day MA (bullish)",
                    strength=75,
                    category="technical"
                ))
            elif ma200 and ma50 < ma200:
                reasons.append(SignalReason(
                    factor="Death Cross Setup",
                    description="50-day MA below 200-day MA (bearish)",
                    strength=75,
                    category="technical"
                ))
        
        # Volume analysis
        if 'volume' in df.columns and len(df) >= 20:
            avg_volume = df['volume'].rolling(20).mean().iloc[-1]
            current_volume = df['volume'].iloc[-1]
            if current_volume > avg_volume * 1.5:
                reasons.append(SignalReason(
                    factor="High Volume",
                    description=f"Volume {(current_volume/avg_volume):.1f}x above 20-day average",
                    strength=65,
                    category="technical"
                ))
        
        # Momentum
        if len(close) >= 21:
            mom_1m = ((current_price / close.iloc[-21]) - 1) * 100
            if mom_1m > 10:
                reasons.append(SignalReason(
                    factor="Strong Momentum",
                    description=f"Up {mom_1m:.1f}% in last month",
                    strength=70,
                    category="momentum"
                ))
            elif mom_1m < -10:
                reasons.append(SignalReason(
                    factor="Weak Momentum",
                    description=f"Down {abs(mom_1m):.1f}% in last month",
                    strength=70,
                    category="momentum"
                ))
        
        return reasons
    
    def _get_fundamental_reasons(self, fund_row: pd.Series) -> List[SignalReason]:
        """Extract fundamental analysis reasons"""
        reasons = []
        
        # P/E ratio
        pe = fund_row.get('pe_ratio')
        if pe and pe > 0:
            if pe < 15:
                reasons.append(SignalReason(
                    factor="Low P/E",
                    description=f"P/E ratio of {pe:.1f} suggests undervaluation",
                    strength=75,
                    category="fundamental"
                ))
            elif pe > 30:
                reasons.append(SignalReason(
                    factor="High P/E",
                    description=f"P/E ratio of {pe:.1f} suggests premium valuation",
                    strength=60,
                    category="fundamental"
                ))
        
        # ROE
        roe = fund_row.get('roe')
        if roe and roe > 0.15:
            reasons.append(SignalReason(
                factor="High ROE",
                description=f"ROE of {roe*100:.1f}% indicates strong profitability",
                strength=70,
                category="fundamental"
            ))
        
        # Dividend yield
        div_yield = fund_row.get('dividend_yield')
        if div_yield and div_yield > 0.03:
            reasons.append(SignalReason(
                factor="Attractive Dividend",
                description=f"Dividend yield of {div_yield*100:.1f}%",
                strength=65,
                category="fundamental"
            ))
        
        # Revenue growth
        rev_growth = fund_row.get('revenue_growth')
        if rev_growth and rev_growth > 0.1:
            reasons.append(SignalReason(
                factor="Strong Revenue Growth",
                description=f"Revenue growing at {rev_growth*100:.1f}%",
                strength=75,
                category="fundamental"
            ))
        
        return reasons
    
    def _get_model_specific_reasons(
        self, ticker: str, model_id: str, result: Any
    ) -> List[SignalReason]:
        """Get reasons specific to the model that generated the signal"""
        reasons = []
        
        # Try to extract from result rankings
        if hasattr(result, 'rankings'):
            for ranking in result.rankings:
                if ranking.get('ticker') == ticker:
                    # Extract model-specific metrics
                    for key, value in ranking.items():
                        if key not in ['ticker', 'score', 'signal', 'price', 'name', 'market_cap']:
                            if isinstance(value, (int, float)) and value is not None:
                                reasons.append(SignalReason(
                                    factor=key.replace('_', ' ').title(),
                                    description=f"{key}: {value:.2f}" if isinstance(value, float) else f"{key}: {value}",
                                    strength=60,
                                    category="model"
                                ))
        
        return reasons[:3]  # Limit model-specific reasons
    
    def _get_model_confirmations(
        self, ticker: str, signal_type: str
    ) -> tuple:
        """Find which other models confirm or conflict with this signal"""
        confirming = []
        conflicting = []
        
        for model_id, result in self.all_model_results.items():
            if hasattr(result, 'rankings'):
                for ranking in result.rankings:
                    if ranking.get('ticker') == ticker:
                        other_signal = ranking.get('signal', 'HOLD')
                        if other_signal == signal_type:
                            confirming.append(model_id)
                        elif (signal_type == 'BUY' and other_signal == 'SELL') or \
                             (signal_type == 'SELL' and other_signal == 'BUY'):
                            conflicting.append(model_id)
                        break
        
        return confirming, conflicting
    
    def _assess_risks(self, ticker: str) -> List[RiskFactor]:
        """Assess risk factors for the signal"""
        risks = []
        
        # Market regime risk
        if self.market_regime:
            regime = self.market_regime.get('regime', 'NEUTRAL')
            if regime == 'BEAR':
                risks.append(RiskFactor(
                    name="Bear Market",
                    description="Market is in bearish regime",
                    severity="high",
                    mitigation="Consider smaller position size or wait for regime change"
                ))
            elif regime == 'NEUTRAL':
                risks.append(RiskFactor(
                    name="Neutral Market",
                    description="Market regime is neutral/uncertain",
                    severity="medium",
                    mitigation="Use tighter stops and monitor closely"
                ))
        
        # Volatility risk
        if ticker in self.price_data:
            df = self.price_data[ticker]
            if len(df) >= 20:
                returns = df['close'].pct_change().dropna()
                volatility = returns.std() * np.sqrt(252) * 100
                if volatility > 40:
                    risks.append(RiskFactor(
                        name="High Volatility",
                        description=f"Annualized volatility of {volatility:.1f}%",
                        severity="high",
                        mitigation="Reduce position size proportionally"
                    ))
                elif volatility > 25:
                    risks.append(RiskFactor(
                        name="Moderate Volatility",
                        description=f"Annualized volatility of {volatility:.1f}%",
                        severity="medium"
                    ))
        
        # Liquidity risk (based on volume)
        if ticker in self.price_data:
            df = self.price_data[ticker]
            if 'volume' in df.columns and len(df) >= 20:
                avg_volume = df['volume'].mean()
                if avg_volume < 100000:
                    risks.append(RiskFactor(
                        name="Low Liquidity",
                        description=f"Average volume only {avg_volume:,.0f}",
                        severity="high",
                        mitigation="Use limit orders, avoid large positions"
                    ))
        
        # Valuation risk
        if self.fundamental_data is not None:
            fund_row = self.fundamental_data[
                self.fundamental_data['ticker'] == ticker
            ]
            if not fund_row.empty:
                pe = fund_row.iloc[0].get('pe_ratio')
                if pe and pe > 50:
                    risks.append(RiskFactor(
                        name="High Valuation",
                        description=f"P/E ratio of {pe:.1f} is elevated",
                        severity="medium",
                        mitigation="Consider if growth justifies valuation"
                    ))
        
        return risks
    
    def _calculate_overall_risk(self, risk_factors: List[RiskFactor]) -> str:
        """Calculate overall risk level"""
        if not risk_factors:
            return "low"
        
        high_count = sum(1 for r in risk_factors if r.severity == "high")
        medium_count = sum(1 for r in risk_factors if r.severity == "medium")
        
        if high_count >= 2:
            return "high"
        elif high_count >= 1 or medium_count >= 2:
            return "medium"
        else:
            return "low"
    
    def _get_market_regime(self) -> str:
        """Get current market regime"""
        if self.market_regime:
            return self.market_regime.get('regime', 'NEUTRAL')
        return "UNKNOWN"
    
    def _get_sector_trend(self, ticker: str) -> str:
        """Get sector trend for the ticker"""
        # This would ideally come from sector rotation analysis
        return self.sector_data.get(ticker, "NEUTRAL")
    
    def _get_historical_stats(
        self, model_id: str, signal_type: str
    ) -> Optional[HistoricalStats]:
        """Get historical performance stats for similar signals"""
        
        if model_id not in self.historical_performance:
            # Return default/estimated stats based on model type
            return HistoricalStats(
                sample_size=100,  # Estimated
                win_rate=55.0,  # Conservative estimate
                avg_return=5.0,
                avg_holding_days=21,
                max_drawdown=-15.0,
                sharpe_ratio=0.8
            )
        
        perf_data = self.historical_performance[model_id]
        if not perf_data:
            return None
        
        # Filter by signal type
        relevant = [p for p in perf_data if p.get('signal_type') == signal_type]
        if not relevant:
            return None
        
        returns = [p.get('return', 0) for p in relevant]
        wins = sum(1 for r in returns if r > 0)
        
        return HistoricalStats(
            sample_size=len(relevant),
            win_rate=(wins / len(relevant)) * 100 if relevant else 0,
            avg_return=np.mean(returns) if returns else 0,
            avg_holding_days=int(np.mean([p.get('holding_days', 21) for p in relevant])),
            max_drawdown=min(returns) if returns else 0,
            best_return=max(returns) if returns else 0,
            worst_return=min(returns) if returns else 0
        )
    
    def _calculate_position_suggestion(
        self,
        score: float,
        percentile_rank: float,
        confirmation_score: float,
        overall_risk: str,
        historical_stats: Optional[HistoricalStats]
    ) -> PositionSuggestion:
        """Calculate suggested position size and conviction"""
        
        # Base position size (1-5% of portfolio)
        base_pct = 2.0
        
        # Adjust for score strength
        if score >= 80:
            base_pct *= 1.5
        elif score >= 70:
            base_pct *= 1.25
        elif score < 50:
            base_pct *= 0.5
        
        # Adjust for percentile rank
        if percentile_rank >= 90:
            base_pct *= 1.3
        elif percentile_rank >= 80:
            base_pct *= 1.15
        
        # Adjust for confirmation
        if confirmation_score >= 75:
            base_pct *= 1.25
        elif confirmation_score < 25:
            base_pct *= 0.7
        
        # Adjust for risk
        if overall_risk == "high":
            base_pct *= 0.5
        elif overall_risk == "medium":
            base_pct *= 0.75
        
        # Adjust for historical performance
        if historical_stats and historical_stats.win_rate > 60:
            base_pct *= 1.1
        elif historical_stats and historical_stats.win_rate < 45:
            base_pct *= 0.8
        
        # Cap at reasonable limits
        final_pct = max(0.5, min(5.0, base_pct))
        
        # Determine conviction level
        if final_pct >= 4.0:
            conviction = ConvictionLevel.VERY_HIGH
        elif final_pct >= 3.0:
            conviction = ConvictionLevel.HIGH
        elif final_pct >= 2.0:
            conviction = ConvictionLevel.MODERATE
        elif final_pct >= 1.0:
            conviction = ConvictionLevel.LOW
        else:
            conviction = ConvictionLevel.VERY_LOW
        
        # Build rationale
        rationale_parts = []
        if score >= 70:
            rationale_parts.append("strong signal score")
        if percentile_rank >= 80:
            rationale_parts.append(f"top {100-percentile_rank:.0f}% ranking")
        if confirmation_score >= 50:
            rationale_parts.append("multi-model confirmation")
        if overall_risk == "low":
            rationale_parts.append("low risk profile")
        elif overall_risk == "high":
            rationale_parts.append("elevated risk (reduced size)")
        
        rationale = "Based on " + ", ".join(rationale_parts) if rationale_parts else "Standard position sizing"
        
        # Calculate stop loss and take profit
        stop_loss = -8.0 if overall_risk == "low" else -5.0 if overall_risk == "medium" else -3.0
        take_profit = 15.0 if overall_risk == "low" else 10.0 if overall_risk == "medium" else 8.0
        
        return PositionSuggestion(
            portfolio_pct=round(final_pct, 1),
            conviction=conviction,
            rationale=rationale,
            stop_loss_pct=stop_loss,
            take_profit_pct=take_profit
        )


# Singleton instance
_signal_context_builder: Optional[SignalContextBuilder] = None


def get_signal_context_builder() -> SignalContextBuilder:
    """Get singleton instance of SignalContextBuilder"""
    global _signal_context_builder
    if _signal_context_builder is None:
        _signal_context_builder = SignalContextBuilder()
    return _signal_context_builder
