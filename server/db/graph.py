"""
Neo4j Graph Database connection and operations
For MVP: Uses in-memory graph simulation
"""
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
import math


class InMemoryGraph:
    """
    In-memory graph database simulation for MVP.
    Implements citation graph operations without requiring Neo4j.
    """
    
    def __init__(self):
        self.nodes: Dict[str, dict] = {}
        self.edges: List[dict] = []
        self.adjacency: Dict[str, List[str]] = defaultdict(list)
        self.reverse_adjacency: Dict[str, List[str]] = defaultdict(list)
        self._pagerank_cache: Dict[str, float] = {}
    
    def add_node(self, node_id: str, properties: dict):
        """Add a case node to the graph"""
        self.nodes[node_id] = {
            "id": node_id,
            **properties,
            "pagerank": 0.0,
            "status": properties.get("status", "green")
        }
    
    def add_edge(self, source_id: str, target_id: str, edge_type: str, sentiment: str = "neutral"):
        """Add a citation edge from source (citing) to target (cited)"""
        edge = {
            "source": source_id,
            "target": target_id,
            "type": edge_type,
            "sentiment": sentiment
        }
        self.edges.append(edge)
        self.adjacency[source_id].append(target_id)
        self.reverse_adjacency[target_id].append(source_id)
        
        # Update status if overruling
        if edge_type == "overrules" and target_id in self.nodes:
            self.nodes[target_id]["status"] = "red"
    
    def get_citing_cases(self, case_id: str) -> List[dict]:
        """Get cases that cite this case (cited_by)"""
        citing_ids = self.reverse_adjacency.get(case_id, [])
        return [self.nodes[cid] for cid in citing_ids if cid in self.nodes]
    
    def get_cited_cases(self, case_id: str) -> List[dict]:
        """Get cases that this case cites"""
        cited_ids = self.adjacency.get(case_id, [])
        return [self.nodes[cid] for cid in cited_ids if cid in self.nodes]
    
    def get_case_status(self, case_id: str) -> str:
        """Get KeyCite status for a case"""
        if case_id not in self.nodes:
            return "unknown"
        return self.nodes[case_id].get("status", "green")
    
    def calculate_pagerank(self, damping: float = 0.85, iterations: int = 20) -> Dict[str, float]:
        """
        Calculate PageRank scores for all nodes.
        Higher scores indicate more authoritative cases.
        """
        n = len(self.nodes)
        if n == 0:
            return {}
        
        # Initialize scores
        scores = {node_id: 1.0 / n for node_id in self.nodes}
        
        for _ in range(iterations):
            new_scores = {}
            for node_id in self.nodes:
                # Sum of scores from citing cases
                incoming_score = 0.0
                for citing_id in self.reverse_adjacency.get(node_id, []):
                    if citing_id in scores:
                        out_degree = len(self.adjacency.get(citing_id, []))
                        if out_degree > 0:
                            incoming_score += scores[citing_id] / out_degree
                
                new_scores[node_id] = (1 - damping) / n + damping * incoming_score
            
            scores = new_scores
        
        # Normalize to 0-1 range
        max_score = max(scores.values()) if scores else 1
        self._pagerank_cache = {k: v / max_score for k, v in scores.items()}
        
        # Update node properties
        for node_id, score in self._pagerank_cache.items():
            if node_id in self.nodes:
                self.nodes[node_id]["pagerank"] = score
        
        return self._pagerank_cache
    
    def check_overruling_risk(self, case_id: str) -> List[dict]:
        """
        The "Bad Law Bot" - Check if a case relies on overruled authority.
        Returns list of risk alerts.
        """
        risks = []
        cited_cases = self.get_cited_cases(case_id)
        
        for cited in cited_cases:
            if cited.get("status") == "red":
                risks.append({
                    "cited_case_id": cited["id"],
                    "cited_case_title": cited.get("title", "Unknown"),
                    "reason": "Cites overruled authority",
                    "confidence": 0.95,
                    "severity": "high"
                })
            elif cited.get("status") == "yellow":
                risks.append({
                    "cited_case_id": cited["id"],
                    "cited_case_title": cited.get("title", "Unknown"),
                    "reason": "Cites case with negative treatment",
                    "confidence": 0.75,
                    "severity": "medium"
                })
        
        return risks
    
    def get_citation_path(self, source_id: str, target_id: str, max_depth: int = 5) -> Optional[List[str]]:
        """Find citation path between two cases using BFS"""
        if source_id == target_id:
            return [source_id]
        
        visited = {source_id}
        queue = [(source_id, [source_id])]
        
        while queue:
            current, path = queue.pop(0)
            if len(path) > max_depth:
                continue
            
            for neighbor in self.adjacency.get(current, []):
                if neighbor == target_id:
                    return path + [neighbor]
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        
        return None
    
    def get_graph_stats(self) -> dict:
        """Get statistics about the citation graph"""
        total_nodes = len(self.nodes)
        total_edges = len(self.edges)
        
        # Count by status
        status_counts = defaultdict(int)
        for node in self.nodes.values():
            status_counts[node.get("status", "green")] += 1
        
        # Find most cited
        citation_counts = {nid: len(self.reverse_adjacency.get(nid, [])) for nid in self.nodes}
        most_cited = sorted(citation_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "total_cases": total_nodes,
            "total_citations": total_edges,
            "status_distribution": dict(status_counts),
            "most_cited": [{"case_id": cid, "citations": count} for cid, count in most_cited],
            "avg_citations": total_edges / total_nodes if total_nodes > 0 else 0
        }


# Global graph instance
_graph = InMemoryGraph()


def get_graph() -> InMemoryGraph:
    """Get graph database instance"""
    return _graph


def initialize_graph_from_db(db) -> InMemoryGraph:
    """Initialize graph from database cases and citations"""
    graph = get_graph()
    
    # Add all cases as nodes
    for case in db.get_all_cases():
        graph.add_node(case["id"], {
            "title": case["title"],
            "citation": case["citation"],
            "court": case["court"],
            "date": case.get("date_decided", ""),
            "status": case.get("citation_status", "green")
        })
    
    # Add citation edges
    for citation in db.citations:
        graph.add_edge(
            citation["source_id"],
            citation["target_id"],
            citation["type"],
            citation.get("sentiment", "neutral")
        )
    
    # Calculate PageRank
    graph.calculate_pagerank()
    
    return graph
