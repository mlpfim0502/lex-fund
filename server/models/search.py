"""
Search and RAG models
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class SearchType(str, Enum):
    """Types of search"""
    KEYWORD = "keyword"
    SEMANTIC = "semantic"
    HYBRID = "hybrid"


class SearchRequest(BaseModel):
    """Search query request"""
    query: str = Field(..., min_length=1, description="Search query text")
    search_type: SearchType = SearchType.HYBRID
    jurisdictions: Optional[List[str]] = None
    court_levels: Optional[List[str]] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    topics: Optional[List[str]] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=100)


class SearchResult(BaseModel):
    """Individual search result"""
    id: str
    title: str
    citation: str
    court: str
    date_decided: str
    citation_status: str
    authority_score: float
    snippet: str
    relevance_score: float
    highlights: List[str] = []


class SearchResponse(BaseModel):
    """Search response with results and metadata"""
    query: str
    total_results: int
    page: int
    page_size: int
    results: List[SearchResult]
    suggested_queries: List[str] = []
    execution_time_ms: float


class ChatMessage(BaseModel):
    """Chat message for AI assistant"""
    role: str = Field(..., pattern="^(user|assistant|system)$")
    content: str


class ChatRequest(BaseModel):
    """RAG chat request"""
    message: str = Field(..., min_length=1)
    conversation_history: List[ChatMessage] = []
    include_sources: bool = True


class SourceCitation(BaseModel):
    """Source citation for RAG response"""
    case_id: str
    case_title: str
    citation: str
    relevant_excerpt: str
    relevance_score: float


class ChatResponse(BaseModel):
    """RAG chat response with sources"""
    answer: str
    sources: List[SourceCitation] = []
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    follow_up_questions: List[str] = []
