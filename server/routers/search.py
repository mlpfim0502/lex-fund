"""
Search API Router
"""
from fastapi import APIRouter
from models.search import SearchRequest, SearchResponse
from services.search import get_search_service

router = APIRouter(prefix="/api/search", tags=["Search"])


@router.post("", response_model=SearchResponse)
async def search(request: SearchRequest):
    """
    Execute a legal search query.
    
    Supports three modes:
    - keyword: Traditional BM25 text matching
    - semantic: Vector similarity search
    - hybrid: Combined keyword + semantic with RRF fusion
    """
    search_service = get_search_service()
    return search_service.search(request)


@router.get("/suggestions")
async def get_suggestions(query: str):
    """Get search suggestions for autocomplete"""
    # Common legal search suggestions
    suggestions = []
    query_lower = query.lower()
    
    common_terms = [
        "breach of contract", "negligence", "due process",
        "equal protection", "first amendment", "fourth amendment",
        "summary judgment", "statute of limitations", "injunctive relief",
        "constitutional law", "administrative law", "criminal procedure"
    ]
    
    for term in common_terms:
        if query_lower in term:
            suggestions.append(term)
    
    return {"query": query, "suggestions": suggestions[:5]}


@router.get("/topics")
async def list_topics():
    """List available legal topics for filtering"""
    topics = [
        {"id": "constitutional", "name": "Constitutional Law", "count": 156},
        {"id": "criminal", "name": "Criminal Procedure", "count": 124},
        {"id": "civil_rights", "name": "Civil Rights", "count": 98},
        {"id": "administrative", "name": "Administrative Law", "count": 87},
        {"id": "contracts", "name": "Contracts", "count": 234},
        {"id": "torts", "name": "Torts", "count": 189},
        {"id": "property", "name": "Property", "count": 156},
        {"id": "corporate", "name": "Corporate Law", "count": 145},
        {"id": "employment", "name": "Employment Law", "count": 112},
        {"id": "family", "name": "Family Law", "count": 89}
    ]
    return {"topics": topics}
