"""
Audit Service
Handles recording of critical user actions for security and compliance.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import Dict, Optional, Any, List
import logging
from datetime import datetime

from app.database.models import AuditLog

logger = logging.getLogger(__name__)

class AuditService:
    """Service for creating and querying audit logs"""
    
    async def log(
        self,
        db: AsyncSession,
        user_id: str,
        action: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AuditLog:
        """
        Create a new audit log entry.
        
        Args:
            db: Database session
            user_id: ID of user performing the action
            action: Action name (e.g., "DELETE_UNIVERSE")
            resource_type: Type of resource (e.g., "custom_universe")
            resource_id: ID of the resource
            details: Additional context (diff, reason, etc.)
            ip_address: Client IP address
            user_agent: Client User-Agent string
        """
        try:
            log_entry = AuditLog(
                user_id=user_id,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                details=details,
                ip_address=ip_address,
                user_agent=user_agent,
                created_at=datetime.now()
            )
            
            db.add(log_entry)
            # We don't commit here to allow atomic transactions with the action being performed.
            # Caller should commit.
            await db.flush()
            
            logger.info(f"Audit log created: {action} by {user_id} on {resource_type}:{resource_id}")
            return log_entry
            
        except Exception as e:
            logger.error(f"Failed to create audit log: {str(e)}", exc_info=True)
            # We don't want audit logging failure to block the main action if possible,
            # but for strict security systems it should. 
            # For now, we'll log the error but let it propagate so the caller decides.
            raise e

    async def get_logs_for_user(
        self,
        db: AsyncSession,
        user_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[AuditLog]:
        """Get audit logs for a specific user"""
        stmt = select(AuditLog).where(AuditLog.user_id == user_id)\
            .order_by(desc(AuditLog.created_at))\
            .offset(offset).limit(limit)
            
        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_logs_for_resource(
        self,
        db: AsyncSession,
        resource_type: str,
        resource_id: str,
        limit: int = 50
    ) -> List[AuditLog]:
        """Get logs relative to a specific resource"""
        stmt = select(AuditLog).where(
            AuditLog.resource_type == resource_type,
            AuditLog.resource_id == resource_id
        ).order_by(desc(AuditLog.created_at)).limit(limit)
        
        result = await db.execute(stmt)
        return result.scalars().all()


# Singleton instance
_audit_service = None

def get_audit_service() -> AuditService:
    global _audit_service
    if _audit_service is None:
        _audit_service = AuditService()
    return _audit_service
