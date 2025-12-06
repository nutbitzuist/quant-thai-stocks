"""
History Service
Stores and retrieves model run history
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
import json
import os


@dataclass
class RunRecord:
    """Record of a single model run"""
    id: str
    model_id: str
    model_name: str
    category: str
    universe: str
    run_timestamp: str
    total_analyzed: int
    stocks_with_data: int
    buy_signals: List[Dict]
    sell_signals: List[Dict]
    parameters: Dict[str, Any]
    errors: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return asdict(self)


class HistoryService:
    """
    In-memory storage for model run history
    In production, this would use a database
    """
    
    def __init__(self, max_records: int = 100):
        self.max_records = max_records
        self._history: List[RunRecord] = []
        self._run_counter = 0
    
    def add_run(
        self,
        model_id: str,
        model_name: str,
        category: str,
        universe: str,
        total_analyzed: int,
        stocks_with_data: int,
        buy_signals: List[Dict],
        sell_signals: List[Dict],
        parameters: Dict[str, Any],
        errors: List[str] = None
    ) -> RunRecord:
        """Add a new run to history"""
        self._run_counter += 1
        
        record = RunRecord(
            id=f"run_{self._run_counter}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            model_id=model_id,
            model_name=model_name,
            category=category,
            universe=universe,
            run_timestamp=datetime.now().isoformat(),
            total_analyzed=total_analyzed,
            stocks_with_data=stocks_with_data,
            buy_signals=buy_signals,
            sell_signals=sell_signals,
            parameters=parameters,
            errors=errors or []
        )
        
        self._history.insert(0, record)  # Most recent first
        
        # Trim old records
        if len(self._history) > self.max_records:
            self._history = self._history[:self.max_records]
        
        return record
    
    def get_all(self, limit: int = 50) -> List[Dict]:
        """Get all run records"""
        return [r.to_dict() for r in self._history[:limit]]
    
    def get_by_id(self, run_id: str) -> Optional[RunRecord]:
        """Get a specific run by ID"""
        for record in self._history:
            if record.id == run_id:
                return record
        return None
    
    def get_by_model(self, model_id: str, limit: int = 20) -> List[Dict]:
        """Get runs for a specific model"""
        filtered = [r for r in self._history if r.model_id == model_id]
        return [r.to_dict() for r in filtered[:limit]]
    
    def get_summary(self) -> Dict:
        """Get summary statistics"""
        if not self._history:
            return {
                "total_runs": 0,
                "models_run": [],
                "universes_used": [],
                "recent_runs": []
            }
        
        models = list(set(r.model_name for r in self._history))
        universes = list(set(r.universe for r in self._history))
        
        return {
            "total_runs": len(self._history),
            "models_run": models,
            "universes_used": universes,
            "recent_runs": [
                {
                    "id": r.id,
                    "model": r.model_name,
                    "universe": r.universe,
                    "timestamp": r.run_timestamp,
                    "buy_count": len(r.buy_signals),
                    "sell_count": len(r.sell_signals)
                }
                for r in self._history[:10]
            ]
        }
    
    def clear(self) -> int:
        """Clear all history"""
        count = len(self._history)
        self._history = []
        return count


# Singleton instance
_history_service = None

def get_history_service() -> HistoryService:
    global _history_service
    if _history_service is None:
        _history_service = HistoryService()
    return _history_service
