"""
Citation and relationship models
"""
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
from datetime import datetime


class CitationType(str, Enum):
    """Types of citation relationships"""
    CITES = "cites"
    OVERRULES = "overrules"
    DISTINGUISHES = "distinguishes"
    AFFIRMS = "affirms"
    REVERSES = "reverses"
    FOLLOWS = "follows"
    CRITICIZES = "criticizes"
    QUESTIONS = "questions"


class CitationSentiment(str, Enum):
    """Sentiment of citation treatment"""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    CAUTIONARY = "cautionary"


class Citation(BaseModel):
    """Citation relationship between two cases"""
    id: str
    source_case_id: str  # The citing case
    target_case_id: str  # The cited case
    citation_type: CitationType = CitationType.CITES
    sentiment: CitationSentiment = CitationSentiment.NEUTRAL
    context: Optional[str] = Field(None, description="Surrounding text where citation appears")
    depth_of_treatment: int = Field(default=1, ge=1, le=4, description="1=Mentioned, 4=Examined")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class CitationCreate(BaseModel):
    """Model for creating a citation edge"""
    source_case_id: str
    target_case_id: str
    citation_type: CitationType = CitationType.CITES
    sentiment: CitationSentiment = CitationSentiment.NEUTRAL
    context: Optional[str] = None


class CitationGraphStats(BaseModel):
    """Statistics about the citation graph"""
    total_cases: int
    total_citations: int
    avg_citations_per_case: float
    most_cited_cases: list
    recent_overrulings: list


class KeyCiteResult(BaseModel):
    """KeyCite analysis result for a case"""
    case_id: str
    status: str  # green, yellow, red, orange
    status_reason: Optional[str] = None
    negative_treatments: list = []
    positive_treatments: list = []
    citing_references: int = 0
    overruling_risks: list = []
