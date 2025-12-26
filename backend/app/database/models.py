"""
Database Models for QuantStack
Defines tables for user data persistence
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, Text, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import uuid

from app.database import Base
from app.database.encryption import EncryptedString


def generate_uuid():
    return str(uuid.uuid4())


class User(Base):
    """User model - stores user information synced from Clerk"""
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    clerk_id = Column(String, unique=True, index=True, nullable=True)  # Clerk user ID
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(EncryptedString, nullable=True)
    
    # Subscription info
    plan = Column(String, default="free")  # free, pro, unlimited
    billing_cycle = Column(String, default="monthly")  # monthly, annual
    
    # Usage tracking
    scans_used = Column(Integer, default=0)
    scans_limit = Column(Integer, default=10)  # Free tier limit
    
    # Status
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    usage_logs = relationship("UsageLog", back_populates="user", cascade="all, delete-orphan")
    custom_universes = relationship("CustomUniverse", back_populates="user", cascade="all, delete-orphan")
    scheduled_scans = relationship("ScheduledScan", back_populates="user", cascade="all, delete-orphan")
    run_history = relationship("RunHistory", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(email={self.email}, plan={self.plan})>"


class UsageLog(Base):
    """Usage log - tracks every model run for analytics"""
    __tablename__ = "usage_logs"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=True, index=True)
    
    # Request info
    model_id = Column(String, nullable=False, index=True)
    model_name = Column(String, nullable=True)
    universe = Column(String, nullable=True)
    market = Column(String, nullable=True)  # US, Thailand
    
    # Results
    stocks_analyzed = Column(Integer, default=0)
    buy_signals = Column(Integer, default=0)
    sell_signals = Column(Integer, default=0)
    
    # Performance
    execution_time_ms = Column(Integer, default=0)
    status = Column(String, default="success")  # success, error, timeout
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="usage_logs")
    
    def __repr__(self):
        return f"<UsageLog(model={self.model_name}, user={self.user_id})>"


class CustomUniverse(Base):
    """Custom universe - user-defined stock lists that persist"""
    __tablename__ = "custom_universes"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=True, index=True)
    
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    symbols = Column(JSON, default=list)  # List of stock symbols
    market = Column(String, default="US")
    
    # Status
    is_public = Column(Boolean, default=False)  # Allow sharing
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="custom_universes")
    
    @property
    def count(self):
        return len(self.symbols) if self.symbols else 0
    
    def __repr__(self):
        return f"<CustomUniverse(name={self.name}, count={self.count})>"


class BacktestResult(Base):
    """Saved backtest results for historical reference"""
    __tablename__ = "backtest_results"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=True, index=True)
    
    # Strategy info
    model_id = Column(String, nullable=False)
    model_name = Column(String, nullable=True)
    universe = Column(String, nullable=True)
    
    # Time period
    start_date = Column(String, nullable=True)
    end_date = Column(String, nullable=True)
    
    # Performance metrics (stored as JSON for flexibility)
    metrics = Column(JSON, default=dict)
    
    # Full result data
    result_data = Column(JSON, default=dict)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<BacktestResult(model={self.model_name}, user={self.user_id})>"


class ScheduledScan(Base):
    """Scheduled scan configuration"""
    __tablename__ = "scheduled_scans"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=True, index=True)
    
    model_id = Column(String, nullable=False)
    model_name = Column(String, nullable=True)
    universe = Column(String, nullable=False)
    
    # Schedule
    schedule_time = Column(String, nullable=False)  # HH:MM
    days = Column(JSON, default=list)  # List of day strings
    
    # Config
    enabled = Column(Boolean, default=True)
    parameters = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_run = Column(DateTime(timezone=True), nullable=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="scheduled_scans")
    
    def __repr__(self):
        return f"<ScheduledScan(model={self.model_name}, time={self.schedule_time})>"


class RunHistory(Base):
    """History of model runs"""
    __tablename__ = "run_history"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=True, index=True)
    
    # Model info
    model_id = Column(String, nullable=False, index=True)
    model_name = Column(String, nullable=True)
    category = Column(String, nullable=True)
    universe = Column(String, nullable=True)
    
    # Stats
    total_analyzed = Column(Integer, default=0)
    stocks_with_data = Column(Integer, default=0)
    
    # Full results (signals)
    buy_signals = Column(JSON, default=list)
    sell_signals = Column(JSON, default=list)
    
    # Config & Errors
    parameters = Column(JSON, default=dict)
    errors = Column(JSON, default=list)
    
    # Timestamps
    run_timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="run_history")
    
    
    def __repr__(self):
        return f"<RunHistory(model={self.model_name}, user={self.user_id})>"


class AuditLog(Base):
    """Audit log - tracks critical user actions for security and compliance"""
    __tablename__ = "audit_logs"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=True, index=True)
    
    # Action info
    action = Column(String, nullable=False, index=True)  # e.g., DELETE_UNIVERSE, UPDATE_SETTINGS
    resource_type = Column(String, nullable=False)       # e.g., custom_universe, scheduled_scan
    resource_id = Column(String, nullable=True)          # ID of the affected resource
    
    # Context
    details = Column(JSON, nullable=True)                # Previous value, new value, metadata
    ip_address = Column(EncryptedString, nullable=True)
    user_agent = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", backref="audit_logs")
    
    def __repr__(self):
        return f"<AuditLog(action={self.action}, user={self.user_id})>"
