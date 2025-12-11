"""
Analytics models for litigation analytics
"""
from pydantic import BaseModel, Field
from typing import Optional, List


class JudgeProfile(BaseModel):
    """Judge analytics profile"""
    id: str
    name: str
    court: str
    total_cases: int
    avg_time_to_ruling_days: float
    motion_grant_rate: float
    summary_judgment_rate: float
    case_types: List[str] = []


class AttorneyProfile(BaseModel):
    """Attorney analytics profile"""
    id: str
    name: str
    firm: Optional[str] = None
    total_cases: int
    win_rate: float
    practice_areas: List[str] = []
    top_clients: List[str] = []


class CaseOutcome(BaseModel):
    """Case outcome statistics"""
    outcome_type: str
    count: int
    percentage: float


class TimelineEvent(BaseModel):
    """Docket timeline event"""
    date: str
    event_type: str
    description: str
    document_id: Optional[str] = None


class AnalyticsRequest(BaseModel):
    """Request for analytics data"""
    entity_type: str = Field(..., pattern="^(judge|attorney|court)$")
    entity_id: Optional[str] = None
    entity_name: Optional[str] = None


class DashboardStats(BaseModel):
    """Dashboard summary statistics"""
    total_cases: int
    total_citations: int
    recent_filings: int
    overruled_cases: int
    top_jurisdictions: List[dict]
    trending_topics: List[str]
