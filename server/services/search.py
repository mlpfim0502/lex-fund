"""
Search service with hybrid search (BM25 + Vector)
"""
from typing import List, Optional, Dict
from db.database import get_db
from db.vector import get_vector_db
from models.search import SearchRequest, SearchResult, SearchResponse
import time
import re


class SearchService:
    """Hybrid search service combining keyword and semantic search"""
    
    def __init__(self):
        self.db = get_db()
        self.vector_db = get_vector_db()
    
    def _keyword_search(self, query: str, top_k: int = 20) -> List[dict]:
        """BM25-style keyword search"""
        results = self.db.search_cases(query)
        return results[:top_k]
    
    def _semantic_search(self, query: str, top_k: int = 20) -> List[dict]:
        """Vector similarity search"""
        vector_results = self.vector_db.search(query, top_k)
        
        results = []
        for doc_id, score, metadata in vector_results:
            case = self.db.get_case(doc_id)
            if case:
                results.append({**case, "vector_score": score})
        
        return results
    
    def _reciprocal_rank_fusion(
        self, 
        keyword_results: List[dict], 
        semantic_results: List[dict],
        k: int = 60
    ) -> List[dict]:
        """
        Combine results using Reciprocal Rank Fusion (RRF).
        RRF score = sum(1 / (k + rank)) for each result list
        """
        scores: Dict[str, float] = {}
        cases: Dict[str, dict] = {}
        
        # Score keyword results
        for rank, result in enumerate(keyword_results, 1):
            case_id = result["id"]
            scores[case_id] = scores.get(case_id, 0) + 1 / (k + rank)
            cases[case_id] = result
        
        # Score semantic results
        for rank, result in enumerate(semantic_results, 1):
            case_id = result["id"]
            scores[case_id] = scores.get(case_id, 0) + 1 / (k + rank)
            cases[case_id] = result
        
        # Sort by combined score
        sorted_ids = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)
        
        results = []
        for case_id in sorted_ids:
            case = cases[case_id]
            case["relevance_score"] = scores[case_id]
            results.append(case)
        
        return results
    
    def _generate_snippet(self, text: str, query: str, max_length: int = 200) -> str:
        """Generate a relevant snippet from case text"""
        query_terms = query.lower().split()
        sentences = re.split(r'[.!?]+', text)
        
        # Find sentence with most query term matches
        best_sentence = ""
        best_score = 0
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            score = sum(1 for term in query_terms if term in sentence_lower)
            if score > best_score:
                best_score = score
                best_sentence = sentence.strip()
        
        if not best_sentence:
            best_sentence = text[:max_length]
        
        # Truncate if needed
        if len(best_sentence) > max_length:
            best_sentence = best_sentence[:max_length] + "..."
        
        return best_sentence
    
    def _highlight_terms(self, text: str, query: str) -> List[str]:
        """Extract highlighted matching terms"""
        query_terms = query.lower().split()
        highlights = []
        
        for term in query_terms:
            pattern = re.compile(rf'\b\w*{re.escape(term)}\w*\b', re.IGNORECASE)
            matches = pattern.findall(text)
            highlights.extend(matches[:3])  # Max 3 matches per term
        
        return list(set(highlights))[:5]
    
    def search(self, request: SearchRequest) -> SearchResponse:
        """Execute hybrid search"""
        start_time = time.time()
        
        if request.search_type.value == "keyword":
            results = self._keyword_search(request.query, request.page_size * 2)
        elif request.search_type.value == "semantic":
            results = self._semantic_search(request.query, request.page_size * 2)
        else:  # hybrid
            keyword_results = self._keyword_search(request.query, 20)
            semantic_results = self._semantic_search(request.query, 20)
            results = self._reciprocal_rank_fusion(keyword_results, semantic_results)
        
        # Apply filters
        if request.jurisdictions:
            results = [r for r in results if r.get("jurisdiction") in request.jurisdictions]
        if request.court_levels:
            results = [r for r in results if r.get("court_level") in request.court_levels]
        
        # Paginate
        total = len(results)
        start = (request.page - 1) * request.page_size
        end = start + request.page_size
        paginated = results[start:end]
        
        # Format results
        search_results = []
        for case in paginated:
            search_results.append(SearchResult(
                id=case["id"],
                title=case["title"],
                citation=case["citation"],
                court=case["court"],
                date_decided=case["date_decided"],
                citation_status=case.get("citation_status", "green"),
                authority_score=case.get("authority_score", 0.5),
                snippet=self._generate_snippet(case.get("full_text", ""), request.query),
                relevance_score=case.get("relevance_score", 0.5),
                highlights=self._highlight_terms(case.get("full_text", ""), request.query)
            ))
        
        execution_time = (time.time() - start_time) * 1000
        
        return SearchResponse(
            query=request.query,
            total_results=total,
            page=request.page,
            page_size=request.page_size,
            results=search_results,
            suggested_queries=self._get_suggestions(request.query),
            execution_time_ms=round(execution_time, 2)
        )
    
    def _get_suggestions(self, query: str) -> List[str]:
        """Generate search suggestions"""
        suggestions = []
        topics = ["constitutional law", "civil rights", "criminal procedure", 
                  "administrative law", "first amendment"]
        
        for topic in topics:
            if topic not in query.lower():
                suggestions.append(f"{query} {topic}")
                if len(suggestions) >= 3:
                    break
        
        return suggestions


# Global service instance
_search_service = None


def get_search_service() -> SearchService:
    """Get search service instance"""
    global _search_service
    if _search_service is None:
        _search_service = SearchService()
    return _search_service
