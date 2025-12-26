"""
History Service
Stores and retrieves model run history with user ownership
Backed by PostgreSQL
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, desc, func
from sqlalchemy.orm import selectinload, defer
import logging
import json

from app.database.models import RunHistory
from app.database import get_db

logger = logging.getLogger(__name__)


class HistoryService:
    """
    Database-backed storage for model run history.
    Uses AsyncSession.
    """
    
    def __init__(self):
        # No in-memory storage anymore
        pass
    
    async def add_run(
        self,
        db: AsyncSession,
        model_id: str,
        model_name: str,
        category: str,
        universe: str,
        total_analyzed: int,
        stocks_with_data: int,
        buy_signals: List[Dict],
        sell_signals: List[Dict],
        parameters: Dict[str, Any],
        errors: List[str] = None,
        user_id: str = ""
    ) -> Dict:
        """Add a new run to history"""
        
        record = RunHistory(
            # ID auto-generated
            model_id=model_id,
            model_name=model_name,
            category=category,
            universe=universe,
            run_timestamp=datetime.now(),
            total_analyzed=total_analyzed,
            stocks_with_data=stocks_with_data,
            buy_signals=buy_signals,
            sell_signals=sell_signals,
            parameters=parameters,
            errors=errors or [],
            user_id=user_id
        )
        
        db.add(record)
        await db.flush()  # Generate ID but don't commit transaction
        await db.refresh(record)
        
        return self._to_dict(record)
    
    async def get_all(self, db: AsyncSession, limit: int = 50, user_id: Optional[str] = None) -> List[Dict]:
        """Get all run records, optionally filtered by user"""
        stmt = select(RunHistory).options(
            defer(RunHistory.buy_signals),
            defer(RunHistory.sell_signals),
            defer(RunHistory.parameters),
            defer(RunHistory.errors)
        ).order_by(desc(RunHistory.run_timestamp)).limit(limit)
        
        if user_id:
            stmt = stmt.where(RunHistory.user_id == user_id)
            
        result = await db.execute(stmt)
        records = result.scalars().all()
        
        return [self._to_summary_dict(r) for r in records]
    
    async def get_by_id(self, db: AsyncSession, run_id: str, user_id: Optional[str] = None) -> Optional[Dict]:
        """Get a specific run by ID"""
        stmt = select(RunHistory).where(RunHistory.id == run_id)
        result = await db.execute(stmt)
        record = result.scalar_one_or_none()
        
        if not record:
            return None
            
        if user_id and record.user_id != user_id:
            return None
            
        return self._to_dict(record)
    
    async def get_by_model(self, db: AsyncSession, model_id: str, limit: int = 20, user_id: Optional[str] = None) -> List[Dict]:
        """Get runs for a specific model"""
        stmt = select(RunHistory).options(
            defer(RunHistory.buy_signals),
            defer(RunHistory.sell_signals),
            defer(RunHistory.parameters),
            defer(RunHistory.errors)
        ).where(RunHistory.model_id == model_id).order_by(desc(RunHistory.run_timestamp)).limit(limit)
        
        if user_id:
            stmt = stmt.where(RunHistory.user_id == user_id)
            
        result = await db.execute(stmt)
        records = result.scalars().all()
        
        return [self._to_summary_dict(r) for r in records]
    
    async def get_summary(self, db: AsyncSession, user_id: Optional[str] = None) -> Dict:
        """Get summary statistics"""
        
        # Base query for aggregation
        base_query = select(RunHistory)
        if user_id:
            base_query = base_query.where(RunHistory.user_id == user_id)
            
        # Total runs
        count_stmt = select(func.count()).select_from(base_query.subquery())
        total_runs = (await db.execute(count_stmt)).scalar() or 0
        
        # Models run (distinct)
        models_stmt = select(RunHistory.model_name).distinct()
        if user_id:
            models_stmt = models_stmt.where(RunHistory.user_id == user_id)
        models = (await db.execute(models_stmt)).scalars().all()
        
        # Universes used (distinct)
        universes_stmt = select(RunHistory.universe).distinct()
        if user_id:
            universes_stmt = universes_stmt.where(RunHistory.user_id == user_id)
        universes = (await db.execute(universes_stmt)).scalars().all()
        
        # Recent runs (top 10)
        recent_stmt = select(RunHistory).order_by(desc(RunHistory.run_timestamp)).limit(10)
        if user_id:
            recent_stmt = recent_stmt.where(RunHistory.user_id == user_id)
        recent_records = (await db.execute(recent_stmt)).scalars().all()
        
        recent_runs = [
            {
                "id": r.id,
                "model": r.model_name,
                "universe": r.universe,
                "timestamp": r.run_timestamp.isoformat(),
                "buy_count": len(r.buy_signals) if r.buy_signals else 0,
                "sell_count": len(r.sell_signals) if r.sell_signals else 0
            }
            for r in recent_records
        ]

        return {
            "total_runs": total_runs,
            "models_run": list(models),
            "universes_used": list(universes),
            "recent_runs": recent_runs
        }
    
    async def clear_for_user(self, db: AsyncSession, user_id: str) -> int:
        """Clear history for a specific user"""
        if not user_id:
            logger.warning("Attempted to clear history without user_id")
            return 0
            
        stmt = delete(RunHistory).where(RunHistory.user_id == user_id)
        result = await db.execute(stmt)
        await db.commit()
        
        cleared = result.rowcount
        logger.info(f"Cleared {cleared} history records for user {user_id}")
        return cleared
        
    def _to_dict(self, record: RunHistory) -> Dict:
        """Convert DB model to dictionary"""
        return {
            "id": record.id,
            "model_id": record.model_id,
            "model_name": record.model_name,
            "category": record.category,
            "universe": record.universe,
            "run_timestamp": record.run_timestamp.isoformat() if record.run_timestamp else None,
            "total_analyzed": record.total_analyzed,
            "stocks_with_data": record.stocks_with_data,
            "buy_signals": record.buy_signals,
            "sell_signals": record.sell_signals,
            "parameters": record.parameters,
            "errors": record.errors,
            "user_id": record.user_id
        }

    def _to_summary_dict(self, record: RunHistory) -> Dict:
        """Convert DB model to summary dictionary (skips heavy fields)"""
        return {
            "id": record.id,
            "model_id": record.model_id,
            "model_name": record.model_name,
            "category": record.category,
            "universe": record.universe,
            "run_timestamp": record.run_timestamp.isoformat() if record.run_timestamp else None,
            "total_analyzed": record.total_analyzed,
            "stocks_with_data": record.stocks_with_data,
            "buy_signals": [], # Skipped
            "sell_signals": [], # Skipped
            "parameters": {}, # Skipped
            "errors": [], # Skipped
            "user_id": record.user_id
        }


# Singleton instance
_history_service = None

def get_history_service() -> HistoryService:
    global _history_service
    if _history_service is None:
        _history_service = HistoryService()
    return _history_service
