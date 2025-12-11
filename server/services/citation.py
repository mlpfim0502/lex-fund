"""
Citation Graph Service - "Bad Law Bot" Implementation
"""
from typing import List, Dict, Optional
from db.graph import get_graph, InMemoryGraph
from db.database import get_db
from models.citation import KeyCiteResult, CitationGraphStats


class CitationService:
    """
    Citation analysis service implementing KeyCite-like functionality.
    Detects bad law, overruling risks, and calculates authority scores.
    """
    
    def __init__(self):
        self.graph = get_graph()
        self.db = get_db()
    
    def get_keycite_status(self, case_id: str) -> KeyCiteResult:
        """
        Get KeyCite-style analysis for a case.
        Returns status flags, negative treatments, and overruling risks.
        """
        case = self.db.get_case(case_id)
        if not case:
            return KeyCiteResult(
                case_id=case_id,
                status="unknown",
                status_reason="Case not found in database"
            )
        
        status = case.get("citation_status", "green")
        status_reason = self._get_status_reason(status, case_id)
        
        # Get citation relationships
        citations = self.db.get_citations_for_case(case_id)
        
        negative_treatments = []
        positive_treatments = []
        
        for cit in citations.get("cited_by", []):
            source_case = self.db.get_case(cit["source_id"])
            if source_case:
                treatment = {
                    "case_id": cit["source_id"],
                    "case_title": source_case["title"],
                    "treatment_type": cit["type"],
                    "sentiment": cit["sentiment"]
                }
                if cit["sentiment"] == "negative":
                    negative_treatments.append(treatment)
                elif cit["sentiment"] == "positive":
                    positive_treatments.append(treatment)
        
        # Check for overruling risks
        overruling_risks = self.graph.check_overruling_risk(case_id)
        
        return KeyCiteResult(
            case_id=case_id,
            status=status,
            status_reason=status_reason,
            negative_treatments=negative_treatments,
            positive_treatments=positive_treatments,
            citing_references=case.get("cited_by_count", 0),
            overruling_risks=overruling_risks
        )
    
    def _get_status_reason(self, status: str, case_id: str) -> str:
        """Generate human-readable status reason"""
        reasons = {
            "green": "This case is valid law with no significant negative treatment",
            "yellow": "This case has been distinguished or questioned by subsequent courts",
            "red": "This case has been overruled or reversed and should not be cited as authority",
            "orange": "This case may rely on overruled authority - verify before citing"
        }
        return reasons.get(status, "Status unknown")
    
    def get_citation_network(self, case_id: str, depth: int = 2) -> dict:
        """
        Get citation network centered on a case.
        Returns nodes and edges for visualization.
        """
        nodes = []
        edges = []
        visited = set()
        
        def traverse(current_id: str, current_depth: int):
            if current_id in visited or current_depth > depth:
                return
            visited.add(current_id)
            
            case = self.db.get_case(current_id)
            if not case:
                return
            
            nodes.append({
                "id": case["id"],
                "title": case["title"],
                "citation": case["citation"],
                "status": case.get("citation_status", "green"),
                "authority": case.get("authority_score", 0.5)
            })
            
            # Get citing relationships
            citations = self.db.get_citations_for_case(current_id)
            
            for cit in citations.get("citing", []):
                edges.append({
                    "source": current_id,
                    "target": cit["target_id"],
                    "type": cit["type"]
                })
                if current_depth < depth:
                    traverse(cit["target_id"], current_depth + 1)
            
            for cit in citations.get("cited_by", []):
                edges.append({
                    "source": cit["source_id"],
                    "target": current_id,
                    "type": cit["type"]
                })
                if current_depth < depth:
                    traverse(cit["source_id"], current_depth + 1)
        
        traverse(case_id, 0)
        
        return {
            "center_case": case_id,
            "nodes": nodes,
            "edges": edges
        }
    
    def check_implicit_overruling(self, case_id: str) -> List[dict]:
        """
        "Bad Law Bot" - Check if a case implicitly relies on overruled authority.
        This is the killer feature that Westlaw Edge offers.
        """
        risks = []
        case = self.db.get_case(case_id)
        if not case:
            return risks
        
        citations = self.db.get_citations_for_case(case_id)
        
        for cit in citations.get("citing", []):
            cited_case = self.db.get_case(cit["target_id"])
            if cited_case and cited_case.get("citation_status") == "red":
                # This case cites an overruled case
                risks.append({
                    "risk_type": "direct_reliance",
                    "cited_case_id": cited_case["id"],
                    "cited_case_title": cited_case["title"],
                    "reason": f"This case cites {cited_case['title']}, which has been overruled",
                    "confidence": 0.95,
                    "recommendation": "Review the specific legal principle relied upon to determine if it remains valid"
                })
        
        return risks
    
    def get_authority_ranking(self, topic: str = None, limit: int = 10) -> List[dict]:
        """Get most authoritative cases, optionally filtered by topic"""
        cases = self.db.get_all_cases()
        
        if topic:
            cases = [c for c in cases if any(topic.lower() in t.lower() for t in c.get("topics", []))]
        
        # Sort by authority score
        ranked = sorted(cases, key=lambda x: x.get("authority_score", 0), reverse=True)
        
        return [{
            "id": c["id"],
            "title": c["title"],
            "citation": c["citation"],
            "authority_score": c.get("authority_score", 0),
            "cited_by_count": c.get("cited_by_count", 0)
        } for c in ranked[:limit]]
    
    def get_graph_stats(self) -> CitationGraphStats:
        """Get statistics about the citation graph"""
        stats = self.graph.get_graph_stats()
        
        # Get recent overrulings
        cases = self.db.get_all_cases()
        overruled = [c for c in cases if c.get("citation_status") == "red"]
        recent_overrulings = sorted(overruled, key=lambda x: x.get("date_decided", ""), reverse=True)[:5]
        
        return CitationGraphStats(
            total_cases=stats["total_cases"],
            total_citations=stats["total_citations"],
            avg_citations_per_case=stats["avg_citations"],
            most_cited_cases=stats["most_cited"],
            recent_overrulings=[{
                "id": c["id"],
                "title": c["title"],
                "date": c.get("date_decided", "")
            } for c in recent_overrulings]
        )


# Global service instance
_citation_service = None


def get_citation_service() -> CitationService:
    """Get citation service instance"""
    global _citation_service
    if _citation_service is None:
        _citation_service = CitationService()
    return _citation_service
