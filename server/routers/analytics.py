"""
Analytics API Router - Litigation Analytics
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from models.analytics import JudgeProfile, DashboardStats
from services.analytics import get_analytics_service
from services.citation import get_citation_service

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


@router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard():
    """Get dashboard summary statistics"""
    analytics_service = get_analytics_service()
    return analytics_service.get_dashboard_stats()


@router.get("/judges", response_model=list)
async def search_judges(query: str = Query(default="")):
    """Search for judges by name or court"""
    analytics_service = get_analytics_service()
    
    if query:
        judges = analytics_service.search_judges(query)
    else:
        # Return all judges
        judges = analytics_service.search_judges("")
        if not judges:
            # Return mock data
            judges = [
                analytics_service.get_judge_profile("judge_001"),
                analytics_service.get_judge_profile("judge_002"),
                analytics_service.get_judge_profile("judge_003")
            ]
            judges = [j for j in judges if j]
    
    return judges


@router.get("/judges/{judge_id}", response_model=JudgeProfile)
async def get_judge(judge_id: str):
    """Get detailed analytics for a specific judge"""
    analytics_service = get_analytics_service()
    profile = analytics_service.get_judge_profile(judge_id)
    
    if not profile:
        raise HTTPException(status_code=404, detail="Judge not found")
    
    return profile


@router.get("/cases/{case_id}/timeline")
async def get_case_timeline(case_id: str):
    """Get timeline of events for a case"""
    analytics_service = get_analytics_service()
    timeline = analytics_service.get_case_timeline(case_id)
    return {"case_id": case_id, "events": timeline}


@router.get("/authority")
async def get_authority_ranking(
    topic: Optional[str] = None,
    limit: int = Query(default=10, le=50)
):
    """Get most authoritative cases, optionally filtered by topic"""
    citation_service = get_citation_service()
    ranking = citation_service.get_authority_ranking(topic, limit)
    return {"topic": topic, "rankings": ranking}


@router.get("/graph/stats")
async def get_graph_stats():
    """Get citation graph statistics"""
    citation_service = get_citation_service()
    stats = citation_service.get_graph_stats()
    return stats
