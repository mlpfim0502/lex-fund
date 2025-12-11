"""
SQLAlchemy Database Models for Production
Persistent storage for legal events, signals, and watchlist
"""
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, Text,
    ForeignKey, Enum, create_engine
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from datetime import datetime
import enum

Base = declarative_base()


class EventType(str, enum.Enum):
    LAWSUIT = "lawsuit"
    REGULATORY = "regulatory"
    PATENT = "patent"
    ANTITRUST = "antitrust"
    SEC_FILING = "sec_filing"
    COURT_OPINION = "court_opinion"


class SignalType(str, enum.Enum):
    LONG = "long"
    SHORT = "short"
    NEUTRAL = "neutral"
    MONITOR = "monitor"


class EventStatus(str, enum.Enum):
    PENDING = "pending"
    ACTIVE = "active"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"


class Company(Base):
    """Companies on watchlist"""
    __tablename__ = "companies"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(10), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    cik = Column(String(10))  # SEC CIK
    sector = Column(String(100))
    market_cap = Column(Float)
    active = Column(Boolean, default=True)
    
    # Risk tracking
    legal_risk_score = Column(Float, default=0.0)  # 0-1
    last_risk_update = Column(DateTime)
    
    # Relationships
    legal_events = relationship("LegalEvent", back_populates="company")
    signals = relationship("TradingSignal", back_populates="company")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class LegalEvent(Base):
    """Legal events affecting companies"""
    __tablename__ = "legal_events"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    
    # Event details
    event_type = Column(String(50), nullable=False)
    case_id = Column(String(100))  # External case ID (CourtListener, PACER)
    case_name = Column(String(500))
    court = Column(String(100))
    
    # Risk assessment
    severity = Column(Float, default=0.5)  # 0-1 AI-scored
    potential_impact_usd = Column(Float)
    liability_probability = Column(Float)
    
    # Status
    status = Column(String(20), default="pending")
    date_filed = Column(DateTime)
    date_resolved = Column(DateTime)
    
    # Source info
    source = Column(String(50))  # courtlistener, sec_edgar, manual
    source_url = Column(String(500))
    raw_data = Column(Text)  # JSON of original data
    
    # Metadata
    detected_at = Column(DateTime, default=datetime.utcnow)
    last_checked = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    company = relationship("Company", back_populates="legal_events")
    signals = relationship("TradingSignal", back_populates="legal_event")


class TradingSignal(Base):
    """Trading signals generated from legal events"""
    __tablename__ = "trading_signals"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    legal_event_id = Column(Integer, ForeignKey("legal_events.id"), index=True)
    
    # Signal details
    signal_type = Column(String(20), nullable=False)  # long, short, neutral
    confidence = Column(Float, nullable=False)  # 0-1
    rationale = Column(Text)
    
    # Position sizing
    recommended_size_pct = Column(Float)  # % of portfolio
    target_price = Column(Float)
    stop_loss_price = Column(Float)
    
    # Execution
    executed = Column(Boolean, default=False)
    executed_at = Column(DateTime)
    execution_price = Column(Float)
    
    # Outcome tracking
    closed = Column(Boolean, default=False)
    closed_at = Column(DateTime)
    close_price = Column(Float)
    pnl = Column(Float)  # Profit/Loss
    
    # Metadata
    generated_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    
    # Relationships
    company = relationship("Company", back_populates="signals")
    legal_event = relationship("LegalEvent", back_populates="signals")


class Case(Base):
    """Legal cases from CourtListener"""
    __tablename__ = "cases"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    external_id = Column(String(50), unique=True, index=True)  # CourtListener ID
    
    # Case details
    title = Column(String(500), nullable=False)
    citation = Column(String(100))
    docket_number = Column(String(100))
    court = Column(String(100))
    court_level = Column(String(20))  # supreme, appellate, district
    
    # Dates
    date_filed = Column(DateTime)
    date_decided = Column(DateTime)
    
    # Content
    summary = Column(Text)
    full_text = Column(Text)
    headnotes = Column(Text)  # JSON array
    topics = Column(String(500))  # Comma-separated
    
    # Citation analysis
    citation_status = Column(String(20), default="green")  # green, yellow, red
    authority_score = Column(Float, default=0.5)
    citing_count = Column(Integer, default=0)
    cited_by_count = Column(Integer, default=0)
    
    # Vector embedding
    embedding_id = Column(String(100))  # Qdrant point ID
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SECFiling(Base):
    """SEC filings parsed for legal content"""
    __tablename__ = "sec_filings"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey("companies.id"), index=True)
    
    # Filing details
    accession_number = Column(String(50), unique=True, nullable=False)
    form_type = Column(String(20), nullable=False)  # 10-K, 10-Q, 8-K
    filing_date = Column(DateTime, nullable=False)
    
    # Extracted content
    legal_proceedings = Column(Text)  # JSON array
    risk_factors = Column(Text)  # JSON array
    material_events = Column(Text)  # JSON array for 8-K
    
    # Analysis
    has_legal_content = Column(Boolean, default=False)
    legal_severity = Column(Float, default=0.0)
    
    # Metadata
    source_url = Column(String(500))
    parsed_at = Column(DateTime, default=datetime.utcnow)


# Database connection management
class DatabaseManager:
    """Manage database connections and sessions"""
    
    def __init__(self, database_url: str):
        # Convert postgres:// to postgresql+asyncpg://
        if database_url.startswith("postgresql://"):
            async_url = database_url.replace("postgresql://", "postgresql+asyncpg://")
        else:
            async_url = database_url
        
        self.engine = create_async_engine(async_url, echo=False)
        self.session_factory = sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
    
    async def create_tables(self):
        """Create all tables"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    async def get_session(self) -> AsyncSession:
        """Get a database session"""
        return self.session_factory()
    
    async def close(self):
        """Close database connections"""
        await self.engine.dispose()


# Singleton
_db_manager = None


def get_db_manager(database_url: str = None) -> DatabaseManager:
    """Get database manager instance"""
    global _db_manager
    if _db_manager is None:
        from config import get_settings
        url = database_url or get_settings().postgres_url
        _db_manager = DatabaseManager(url)
    return _db_manager
