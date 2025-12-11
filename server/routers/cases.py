"""
Cases API Router
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from models.case import Case, CaseSummary, CaseWithCitations
from models.citation import KeyCiteResult
from db.database import get_db
from services.citation import get_citation_service

router = APIRouter(prefix="/api/cases", tags=["Cases"])


@router.get("", response_model=List[CaseSummary])
async def list_cases(
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0, ge=0),
    status: Optional[str] = None
):
    """List all cases with optional status filter"""
    db = get_db()
    cases = db.get_all_cases()
    
    if status:
        cases = [c for c in cases if c.get("citation_status") == status]
    
    paginated = cases[offset:offset + limit]
    
    return [CaseSummary(
        id=c["id"],
        title=c["title"],
        citation=c["citation"],
        court=c["court"],
        date_decided=c["date_decided"],
        citation_status=c.get("citation_status", "green"),
        authority_score=c.get("authority_score", 0.5)
    ) for c in paginated]


@router.get("/{case_id}", response_model=Case)
async def get_case(case_id: str):
    """Get a specific case by ID"""
    db = get_db()
    case = db.get_case(case_id)
    
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    return Case(
        id=case["id"],
        title=case["title"],
        citation=case["citation"],
        court=case["court"],
        court_level=case.get("court_level", "district"),
        date_decided=case["date_decided"],
        jurisdiction=case.get("jurisdiction", "federal"),
        full_text=case["full_text"],
        headnotes=case.get("headnotes", []),
        topics=case.get("topics", []),
        citation_status=case.get("citation_status", "green"),
        authority_score=case.get("authority_score", 0.5),
        citing_count=case.get("citing_count", 0),
        cited_by_count=case.get("cited_by_count", 0)
    )


@router.get("/{case_id}/keycite", response_model=KeyCiteResult)
async def get_keycite(case_id: str):
    """Get KeyCite status and analysis for a case"""
    citation_service = get_citation_service()
    result = citation_service.get_keycite_status(case_id)
    
    if result.status == "unknown":
        raise HTTPException(status_code=404, detail="Case not found")
    
    return result


@router.get("/{case_id}/citations")
async def get_case_citations(case_id: str, depth: int = Query(default=1, le=3)):
    """Get citation network for a case"""
    citation_service = get_citation_service()
    network = citation_service.get_citation_network(case_id, depth)
    return network


@router.get("/{case_id}/risks")
async def check_risks(case_id: str):
    """Check for overruling risks (Bad Law Bot)"""
    citation_service = get_citation_service()
    risks = citation_service.check_implicit_overruling(case_id)
    return {"case_id": case_id, "risks": risks, "has_risks": len(risks) > 0}
