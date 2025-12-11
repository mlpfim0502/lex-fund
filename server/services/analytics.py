"""
Analytics service for litigation analytics
"""
from typing import List, Dict, Optional
from db.database import get_db
from models.analytics import JudgeProfile, DashboardStats
from collections import defaultdict


class AnalyticsService:
    """
    Litigation analytics service.
    Provides judge profiles, case statistics, and trends.
    """
    
    def __init__(self):
        self.db = get_db()
        # Mock judge data for MVP
        self.judges = {
            "judge_001": {
                "id": "judge_001",
                "name": "Hon. John G. Roberts Jr.",
                "court": "Supreme Court of the United States",
                "total_cases": 1847,
                "avg_time_to_ruling_days": 95.5,
                "motion_grant_rate": 0.48,
                "summary_judgment_rate": 0.35,
                "case_types": ["Constitutional Law", "Civil Rights", "Federal Jurisdiction"]
            },
            "judge_002": {
                "id": "judge_002",
                "name": "Hon. Sonia Sotomayor",
                "court": "Supreme Court of the United States",
                "total_cases": 1523,
                "avg_time_to_ruling_days": 88.2,
                "motion_grant_rate": 0.42,
                "summary_judgment_rate": 0.38,
                "case_types": ["Criminal Law", "Employment", "Immigration"]
            },
            "judge_003": {
                "id": "judge_003",
                "name": "Hon. Clarence Thomas",
                "court": "Supreme Court of the United States",
                "total_cases": 2105,
                "avg_time_to_ruling_days": 102.1,
                "motion_grant_rate": 0.55,
                "summary_judgment_rate": 0.41,
                "case_types": ["Constitutional Law", "Second Amendment", "Federalism"]
            }
        }
    
    def get_judge_profile(self, judge_id: str) -> Optional[JudgeProfile]:
        """Get analytics profile for a judge"""
        judge_data = self.judges.get(judge_id)
        if not judge_data:
            return None
        return JudgeProfile(**judge_data)
    
    def search_judges(self, query: str) -> List[JudgeProfile]:
        """Search for judges by name or court"""
        results = []
        query_lower = query.lower()
        
        for judge_data in self.judges.values():
            if (query_lower in judge_data["name"].lower() or 
                query_lower in judge_data["court"].lower()):
                results.append(JudgeProfile(**judge_data))
        
        return results
    
    def get_dashboard_stats(self) -> DashboardStats:
        """Get summary statistics for the dashboard"""
        cases = self.db.get_all_cases()
        
        # Count by jurisdiction
        jurisdiction_counts = defaultdict(int)
        for case in cases:
            jurisdiction_counts[case.get("jurisdiction", "unknown")] += 1
        
        top_jurisdictions = [
            {"name": k, "count": v}
            for k, v in sorted(jurisdiction_counts.items(), key=lambda x: x[1], reverse=True)
        ]
        
        # Count overruled
        overruled = sum(1 for c in cases if c.get("citation_status") == "red")
        
        # Get trending topics
        topic_counts = defaultdict(int)
        for case in cases:
            for topic in case.get("topics", []):
                topic_counts[topic] += 1
        trending = sorted(topic_counts.keys(), key=lambda x: topic_counts[x], reverse=True)[:5]
        
        # Count citations
        total_citations = sum(c.get("cited_by_count", 0) for c in cases)
        
        return DashboardStats(
            total_cases=len(cases),
            total_citations=total_citations,
            recent_filings=len([c for c in cases if c.get("date_decided", "").startswith("202")]),
            overruled_cases=overruled,
            top_jurisdictions=top_jurisdictions,
            trending_topics=trending
        )
    
    def get_case_timeline(self, case_id: str) -> List[dict]:
        """Get timeline events for a case"""
        case = self.db.get_case(case_id)
        if not case:
            return []
        
        # Generate mock timeline for MVP
        timeline = [
            {
                "date": case.get("date_decided", "Unknown"),
                "event_type": "decision",
                "description": "Opinion issued",
                "document_id": case_id
            }
        ]
        
        # Add citation events
        citations = self.db.get_citations_for_case(case_id)
        for cit in citations.get("cited_by", [])[:5]:
            source = self.db.get_case(cit["source_id"])
            if source:
                timeline.append({
                    "date": source.get("date_decided", "Unknown"),
                    "event_type": f"cited_{cit['type']}",
                    "description": f"{cit['type'].title()} by {source['title']}",
                    "document_id": cit["source_id"]
                })
        
        return sorted(timeline, key=lambda x: x["date"])


# Global service instance
_analytics_service = None


def get_analytics_service() -> AnalyticsService:
    """Get analytics service instance"""
    global _analytics_service
    if _analytics_service is None:
        _analytics_service = AnalyticsService()
    return _analytics_service
