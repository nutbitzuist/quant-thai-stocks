"""
Usage Logging Service
Logs model runs and user activity to database
"""

import logging
from datetime import datetime
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


async def log_model_run(
    db: AsyncSession,
    model_id: str,
    model_name: str,
    universe: str,
    market: str,
    stocks_analyzed: int,
    buy_signals: int,
    sell_signals: int,
    execution_time_ms: int,
    status: str = "success",
    error_message: Optional[str] = None,
    user_id: Optional[str] = None,
) -> Optional[str]:
    """
    Log a model run to the database
    
    Returns log ID if successful, None otherwise
    """
    try:
        from app.database.models import UsageLog
        
        log = UsageLog(
            user_id=user_id,
            model_id=model_id,
            model_name=model_name,
            universe=universe,
            market=market,
            stocks_analyzed=stocks_analyzed,
            buy_signals=buy_signals,
            sell_signals=sell_signals,
            execution_time_ms=execution_time_ms,
            status=status,
            error_message=error_message,
        )
        
        db.add(log)
        await db.commit()
        await db.refresh(log)
        
        logger.info(f"Logged model run: {model_name} on {universe} ({status})")
        return log.id
        
    except Exception as e:
        logger.warning(f"Failed to log model run: {e}")
        return None


async def get_usage_stats(db: AsyncSession):
    """Get usage statistics"""
    try:
        from app.database.models import UsageLog, User
        from sqlalchemy import func
        
        # Total logs
        total_logs = await db.scalar(select(func.count(UsageLog.id)))
        
        # Logs today
        today = datetime.utcnow().date()
        logs_today = await db.scalar(
            select(func.count(UsageLog.id)).where(
                func.date(UsageLog.created_at) == today
            )
        )
        
        # Model usage breakdown
        model_usage = await db.execute(
            select(
                UsageLog.model_name,
                func.count(UsageLog.id).label("count")
            ).group_by(UsageLog.model_name).order_by(func.count(UsageLog.id).desc()).limit(10)
        )
        
        # Total users
        total_users = await db.scalar(select(func.count(User.id)))
        
        return {
            "total_runs": total_logs or 0,
            "runs_today": logs_today or 0,
            "total_users": total_users or 0,
            "top_models": [
                {"model": row.model_name, "count": row.count}
                for row in model_usage.all()
            ]
        }
        
    except Exception as e:
        logger.warning(f"Failed to get usage stats: {e}")
        return {
            "total_runs": 0,
            "runs_today": 0,
            "total_users": 0,
            "top_models": [],
            "error": str(e)
        }


async def get_or_create_user(
    db: AsyncSession,
    email: str,
    clerk_id: Optional[str] = None,
    name: Optional[str] = None,
) -> Optional[str]:
    """Get or create a user by email, returns user ID"""
    try:
        from app.database.models import User
        
        # Try to find existing user
        result = await db.execute(
            select(User).where(User.email == email)
        )
        user = result.scalar_one_or_none()
        
        if user:
            # Update last login
            user.last_login_at = datetime.utcnow()
            if clerk_id and not user.clerk_id:
                user.clerk_id = clerk_id
            if name and not user.name:
                user.name = name
            await db.commit()
            return user.id
        
        # Create new user
        user = User(
            email=email,
            clerk_id=clerk_id,
            name=name,
            last_login_at=datetime.utcnow(),
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
        logger.info(f"Created new user: {email}")
        return user.id
        
    except Exception as e:
        logger.warning(f"Failed to get/create user: {e}")
        return None
