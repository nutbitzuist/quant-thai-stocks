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


def generate_uuid():
    return str(uuid.uuid4())


class User(Base):
    """User model - stores user information synced from Clerk"""
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    clerk_id = Column(String, unique=True, index=True, nullable=True)  # Clerk user ID
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    
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
    
    # Relationships
    usage_logs = relationship("UsageLog", back_populates="user", cascade="all, delete-orphan")
    custom_universes = relationship("CustomUniverse", back_populates="user", cascade="all, delete-orphan")
    
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
