"""
Base Model Classes
Foundation for all technical and fundamental models
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
import pandas as pd
import numpy as np


class SignalType(Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


class ModelCategory(Enum):
    TECHNICAL = "Technical"
    FUNDAMENTAL = "Fundamental"


@dataclass
class Signal:
    """Represents a trading signal"""
    ticker: str
    signal_type: SignalType
    score: float  # 0-100, higher = stronger signal
    price: float
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "ticker": self.ticker,
            "signal_type": self.signal_type.value,
            "score": round(self.score, 2),
            "price_at_signal": round(self.price, 2) if self.price else 0,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }


@dataclass
class ModelResult:
    """Contains all results from running a model"""
    model_name: str
    category: str
    run_timestamp: datetime
    signals: List[Signal]
    rankings: List[Dict]  # All stocks with scores
    parameters: Dict[str, Any]
    errors: List[str] = field(default_factory=list)
    
    def get_buy_signals(self, top_n: int = 10) -> List[Signal]:
        buys = [s for s in self.signals if s.signal_type == SignalType.BUY]
        return sorted(buys, key=lambda x: x.score, reverse=True)[:top_n]
    
    def get_sell_signals(self, top_n: int = 10) -> List[Signal]:
        sells = [s for s in self.signals if s.signal_type == SignalType.SELL]
        return sorted(sells, key=lambda x: x.score, reverse=True)[:top_n]
    
    def to_dict(self) -> Dict:
        return {
            "model_name": self.model_name,
            "category": self.category,
            "run_timestamp": self.run_timestamp.isoformat(),
            "buy_signals": [s.to_dict() for s in self.get_buy_signals()],
            "sell_signals": [s.to_dict() for s in self.get_sell_signals()],
            "total_analyzed": len(self.rankings),
            "errors": self.errors,
            "parameters": self.parameters
        }


class BaseModel(ABC):
    """Abstract base class for all models"""
    
    def __init__(
        self,
        name: str,
        description: str,
        category: ModelCategory,
        parameters: Dict[str, Any]
    ):
        self.name = name
        self.description = description
        self.category = category
        self.parameters = parameters
    
    @abstractmethod
    def calculate_scores(
        self,
        price_data: Dict[str, pd.DataFrame],
        fundamental_data: Optional[pd.DataFrame] = None
    ) -> pd.DataFrame:
        """
        Calculate scores for all stocks
        Must return DataFrame with columns: ticker, score, signal_type, and any metadata
        """
        pass
    
    def run(
        self,
        price_data: Dict[str, pd.DataFrame],
        fundamental_data: Optional[pd.DataFrame] = None
    ) -> ModelResult:
        """Run the model and generate signals"""
        errors = []
        
        try:
            scores_df = self.calculate_scores(price_data, fundamental_data)
        except Exception as e:
            errors.append(f"Score calculation error: {str(e)}")
            scores_df = pd.DataFrame()
        
        signals = []
        rankings = []
        
        if not scores_df.empty:
            for _, row in scores_df.iterrows():
                ticker = row['ticker']
                score = row.get('score', 50)
                signal_type_str = row.get('signal_type', 'HOLD')
                
                # Get current price
                price = 0
                if ticker in price_data and not price_data[ticker].empty:
                    price = price_data[ticker]['close'].iloc[-1]
                
                # Determine signal type
                if isinstance(signal_type_str, str):
                    signal_type = SignalType[signal_type_str]
                else:
                    signal_type = signal_type_str
                
                # Create metadata from extra columns
                metadata = {k: v for k, v in row.items() 
                           if k not in ['ticker', 'score', 'signal_type']}
                
                signal = Signal(
                    ticker=ticker,
                    signal_type=signal_type,
                    score=score,
                    price=price,
                    timestamp=datetime.now(),
                    metadata=metadata
                )
                
                if signal_type in [SignalType.BUY, SignalType.SELL]:
                    signals.append(signal)
                
                rankings.append({
                    "ticker": ticker,
                    "score": round(score, 2),
                    "signal": signal_type.value,
                    "price": round(price, 2) if price else 0,
                    **{k: round(v, 4) if isinstance(v, float) else v 
                       for k, v in metadata.items()}
                })
        
        # Sort rankings by score
        rankings = sorted(rankings, key=lambda x: x['score'], reverse=True)
        
        return ModelResult(
            model_name=self.name,
            category=self.category.value,
            run_timestamp=datetime.now(),
            signals=signals,
            rankings=rankings,
            parameters=self.parameters,
            errors=errors
        )
    
    def get_info(self) -> Dict:
        """Get model metadata"""
        return {
            "id": self.name.lower().replace(" ", "_"),
            "name": self.name,
            "description": self.description,
            "category": self.category.value,
            "parameters": self.parameters
        }
    
    # Utility methods for subclasses
    @staticmethod
    def percentile_rank(series: pd.Series) -> pd.Series:
        """Convert values to percentile ranks (0-100)"""
        return series.rank(pct=True) * 100
    
    @staticmethod
    def normalize_score(value: float, min_val: float, max_val: float) -> float:
        """Normalize a value to 0-100 scale"""
        if max_val == min_val:
            return 50
        return max(0, min(100, (value - min_val) / (max_val - min_val) * 100))


class TechnicalModel(BaseModel):
    """Base class for technical analysis models"""
    
    def __init__(self, name: str, description: str, parameters: Dict[str, Any]):
        super().__init__(name, description, ModelCategory.TECHNICAL, parameters)


class FundamentalModel(BaseModel):
    """Base class for fundamental analysis models"""
    
    def __init__(self, name: str, description: str, parameters: Dict[str, Any]):
        super().__init__(name, description, ModelCategory.FUNDAMENTAL, parameters)
