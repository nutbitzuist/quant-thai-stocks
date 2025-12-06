"""
Momentum + Value Combo Model
Factor investing combining momentum and value factors
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional
from app.models.base import FundamentalModel, Signal, ModelCategory


class MomentumValueModel(FundamentalModel):
    """
    Momentum + Value Combo - Factor Investing Strategy
    
    Combines two proven factors:
    1. Value: Low P/E, P/B, EV/EBITDA
    2. Momentum: Strong price performance over 6-12 months
    
    Research shows combining factors can improve risk-adjusted returns.
    Value stocks with momentum tend to outperform pure value or pure momentum.
    
    Signals:
    - BUY: Undervalued stock with positive momentum
    - SELL: Overvalued stock with negative momentum
    - HOLD: Mixed signals
    """
    
    def __init__(
        self,
        value_weight: float = 0.5,
        momentum_weight: float = 0.5,
        max_pe: float = 25.0,
        max_pb: float = 5.0,
        min_momentum_6m: float = 0.0,
        min_momentum_12m: float = 0.0,
        momentum_lookback: int = 252
    ):
        super().__init__()
        self.name = "Momentum + Value Combo"
        self.description = "Factor investing combining value metrics with price momentum"
        self.value_weight = value_weight
        self.momentum_weight = momentum_weight
        self.max_pe = max_pe
        self.max_pb = max_pb
        self.min_momentum_6m = min_momentum_6m
        self.min_momentum_12m = min_momentum_12m
        self.momentum_lookback = momentum_lookback
        self.parameters = {
            "value_weight": value_weight,
            "momentum_weight": momentum_weight,
            "max_pe": max_pe,
            "max_pb": max_pb,
            "min_momentum_6m": min_momentum_6m,
            "min_momentum_12m": min_momentum_12m,
            "momentum_lookback": momentum_lookback
        }
    
    def calculate_value_score(self, fundamental_data: dict) -> tuple:
        """Calculate composite value score (0-100)"""
        scores = []
        metrics = {}
        
        # P/E Score (lower is better)
        pe = fundamental_data.get('pe_ratio')
        if pe and pe > 0:
            if pe <= self.max_pe:
                pe_score = max(0, 100 - (pe / self.max_pe * 50))
            else:
                pe_score = max(0, 50 - (pe - self.max_pe) * 2)
            scores.append(pe_score)
            metrics['pe_ratio'] = pe
        
        # P/B Score (lower is better)
        pb = fundamental_data.get('pb_ratio') or fundamental_data.get('price_to_book')
        if pb and pb > 0:
            if pb <= self.max_pb:
                pb_score = max(0, 100 - (pb / self.max_pb * 50))
            else:
                pb_score = max(0, 50 - (pb - self.max_pb) * 5)
            scores.append(pb_score)
            metrics['pb_ratio'] = pb
        
        # P/S Score (lower is better)
        ps = fundamental_data.get('ps_ratio') or fundamental_data.get('price_to_sales')
        if ps and ps > 0:
            if ps <= 5:
                ps_score = max(0, 100 - ps * 10)
            else:
                ps_score = max(0, 50 - (ps - 5) * 5)
            scores.append(ps_score)
            metrics['ps_ratio'] = ps
        
        # Dividend Yield Score (higher is better, but not too high)
        div_yield = fundamental_data.get('dividend_yield', 0) or 0
        if div_yield > 0:
            if div_yield <= 6:
                div_score = min(100, div_yield * 15)
            else:
                div_score = max(50, 90 - (div_yield - 6) * 5)  # Very high yield might be risky
            scores.append(div_score)
            metrics['dividend_yield'] = div_yield
        
        if not scores:
            return 50, metrics
        
        return sum(scores) / len(scores), metrics
    
    def calculate_momentum_score(self, price_data: pd.DataFrame) -> tuple:
        """Calculate momentum score based on price performance"""
        metrics = {}
        
        if price_data is None or len(price_data) < 60:
            return 50, metrics
        
        try:
            close = price_data['close']
            current_price = close.iloc[-1]
            
            # 1-month momentum
            if len(close) >= 21:
                mom_1m = ((current_price / close.iloc[-21]) - 1) * 100
                metrics['momentum_1m'] = round(mom_1m, 2)
            
            # 3-month momentum
            if len(close) >= 63:
                mom_3m = ((current_price / close.iloc[-63]) - 1) * 100
                metrics['momentum_3m'] = round(mom_3m, 2)
            
            # 6-month momentum
            if len(close) >= 126:
                mom_6m = ((current_price / close.iloc[-126]) - 1) * 100
                metrics['momentum_6m'] = round(mom_6m, 2)
            else:
                mom_6m = metrics.get('momentum_3m', 0) * 2 if 'momentum_3m' in metrics else 0
                metrics['momentum_6m'] = round(mom_6m, 2)
            
            # 12-month momentum
            if len(close) >= 252:
                mom_12m = ((current_price / close.iloc[-252]) - 1) * 100
                metrics['momentum_12m'] = round(mom_12m, 2)
            else:
                mom_12m = mom_6m * 2 if mom_6m else 0
                metrics['momentum_12m'] = round(mom_12m, 2)
            
            # Calculate momentum score
            # Positive momentum = higher score
            scores = []
            
            # 6-month momentum score
            if mom_6m >= self.min_momentum_6m:
                mom_6m_score = min(100, 50 + mom_6m * 2)
            else:
                mom_6m_score = max(0, 50 + mom_6m * 2)
            scores.append(mom_6m_score)
            
            # 12-month momentum score
            if mom_12m >= self.min_momentum_12m:
                mom_12m_score = min(100, 50 + mom_12m)
            else:
                mom_12m_score = max(0, 50 + mom_12m)
            scores.append(mom_12m_score)
            
            # Recent momentum (1-3 months) for trend confirmation
            if 'momentum_1m' in metrics and 'momentum_3m' in metrics:
                recent_score = 50 + (metrics['momentum_1m'] + metrics['momentum_3m']) / 2
                recent_score = max(0, min(100, recent_score))
                scores.append(recent_score)
            
            return sum(scores) / len(scores), metrics
            
        except Exception as e:
            return 50, metrics
    
    def calculate_scores(
        self,
        price_data: Dict[str, pd.DataFrame],
        fundamental_data: Optional[pd.DataFrame] = None
    ) -> pd.DataFrame:
        """Calculate combined Momentum + Value scores"""
        
        results = []
        
        if fundamental_data is None or fundamental_data.empty:
            return pd.DataFrame(results)
        
        for _, row in fundamental_data.iterrows():
            ticker = row.get('ticker', row.name if isinstance(row.name, str) else 'UNKNOWN')
            
            try:
                fund_dict = row.to_dict()
                ticker_price_data = price_data.get(ticker)
                
                # Calculate value score
                value_score, value_metrics = self.calculate_value_score(fund_dict)
                
                # Calculate momentum score
                momentum_score, momentum_metrics = self.calculate_momentum_score(ticker_price_data)
                
                # Combined score
                combined_score = (
                    value_score * self.value_weight +
                    momentum_score * self.momentum_weight
                )
                
                # Determine signal
                signal_type = "HOLD"
                
                # BUY: Good value AND good momentum
                if value_score >= 60 and momentum_score >= 55:
                    signal_type = "BUY"
                # Strong BUY: Excellent on both
                elif value_score >= 70 and momentum_score >= 65:
                    signal_type = "BUY"
                    combined_score = min(100, combined_score * 1.1)
                # SELL: Poor value AND poor momentum
                elif value_score < 40 and momentum_score < 40:
                    signal_type = "SELL"
                # SELL: Very poor on either
                elif value_score < 25 or momentum_score < 25:
                    signal_type = "SELL"
                
                results.append({
                    'ticker': ticker,
                    'score': round(combined_score, 2),
                    'signal': signal_type,
                    'value_score': round(value_score, 2),
                    'momentum_score': round(momentum_score, 2),
                    **value_metrics,
                    **momentum_metrics,
                    'market_cap': fund_dict.get('market_cap'),
                    'name': fund_dict.get('name', ticker)
                })
                
            except Exception as e:
                self.errors.append(f"Error processing {ticker}: {str(e)}")
                continue
        
        return pd.DataFrame(results)
