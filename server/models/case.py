"""
Pydantic models for legal documents and cases
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date
from enum import Enum


class CourtLevel(str, Enum):
    """Court hierarchy levels"""
    SUPREME = "supreme"
    APPELLATE = "appellate"
    DISTRICT = "district"
    STATE_SUPREME = "state_supreme"
    STATE_APPELLATE = "state_appellate"
    STATE_TRIAL = "state_trial"


class CitationStatus(str, Enum):
    """KeyCite-style validity status"""
    GREEN = "green"       # Good law, positive treatment
    YELLOW = "yellow"     # Caution, some negative treatment
    RED = "red"           # Bad law, overruled/reversed
    ORANGE = "orange"     # Overruling risk (implicit)


class CaseBase(BaseModel):
    """Base case document model"""
    title: str = Field(..., description="Case name, e.g., 'Brown v. Board of Education'")
    citation: str = Field(..., description="Official citation, e.g., '347 U.S. 483'")
    court: str = Field(..., description="Issuing court")
    court_level: CourtLevel = Field(default=CourtLevel.DISTRICT)
    date_decided: date
    docket_number: Optional[str] = None
    jurisdiction: str = Field(default="federal")


class CaseCreate(CaseBase):
    """Model for creating a new case"""
    full_text: str = Field(..., description="Full text of the opinion")
    headnotes: Optional[List[str]] = None
    topics: Optional[List[str]] = None


class Case(CaseBase):
    """Full case model with computed fields"""
    id: str
    full_text: str
    headnotes: List[str] = []
    topics: List[str] = []
    citation_status: CitationStatus = CitationStatus.GREEN
    authority_score: float = Field(default=0.0, description="PageRank-based authority")
    citing_count: int = 0
    cited_by_count: int = 0
    
    class Config:
        from_attributes = True


class CaseSummary(BaseModel):
    """Lightweight case summary for search results"""
    id: str
    title: str
    citation: str
    court: str
    date_decided: date
    citation_status: CitationStatus
    authority_score: float
    snippet: Optional[str] = None
    relevance_score: Optional[float] = None


class CaseWithCitations(Case):
    """Case with citation relationships"""
    citing: List["CaseSummary"] = []
    cited_by: List["CaseSummary"] = []
    overruling_risks: List["OverrulingRisk"] = []


class OverrulingRisk(BaseModel):
    """Risk alert for implicit overruling"""
    cited_case_id: str
    cited_case_title: str
    reason: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    overruled_principle: Optional[str] = None
