"""
RAG (Retrieval-Augmented Generation) Pipeline for Legal Q&A
"""
from typing import List, Dict, Optional
from db.database import get_db
from db.vector import get_vector_db
from models.search import ChatRequest, ChatResponse, SourceCitation, ChatMessage
from config import get_settings


class RAGService:
    """
    RAG pipeline for answering legal questions with source citations.
    For MVP: Uses mock LLM responses with retrieved context.
    """
    
    def __init__(self):
        self.db = get_db()
        self.vector_db = get_vector_db()
        self.settings = get_settings()
    
    def _retrieve_relevant_docs(self, query: str, top_k: int = 5) -> List[dict]:
        """Retrieve relevant documents for the query"""
        vector_results = self.vector_db.search(query, top_k)
        
        docs = []
        for doc_id, score, metadata in vector_results:
            case = self.db.get_case(doc_id)
            if case:
                docs.append({
                    **case,
                    "relevance_score": score
                })
        
        return docs
    
    def _build_context(self, docs: List[dict]) -> str:
        """Build context string from retrieved documents"""
        context_parts = []
        for i, doc in enumerate(docs, 1):
            context_parts.append(f"""
Source {i}: {doc['title']} ({doc['citation']})
Court: {doc['court']} | Decided: {doc['date_decided']}
Excerpt: {doc['full_text'][:500]}...
""")
        return "\n".join(context_parts)
    
    def _generate_mock_response(self, query: str, context: str, docs: List[dict]) -> str:
        """
        Generate a mock LLM response for MVP.
        In production, this would call OpenAI/Claude API.
        """
        query_lower = query.lower()
        
        # Check for common legal questions and provide relevant mock answers
        if "statute of limitations" in query_lower:
            if "fraud" in query_lower and "florida" in query_lower:
                return """Based on Florida law, the statute of limitations for fraud is **4 years** from the date of discovery of the fraud. Under Florida Statutes § 95.031, the cause of action accrues when the last element constituting the cause of action occurs, but the limitations period begins when the fraud should have been discovered through reasonable diligence.

Key Points:
1. The discovery rule applies to fraud claims
2. The 4-year period begins when the plaintiff knew or should have known of the fraud
3. In some cases involving real estate, an absolute 12-year bar applies

*This analysis is based on statutory research and relevant case law.*"""
            else:
                return """The statute of limitations varies by state and type of fraud claim. Generally, fraud claims are subject to a discovery rule, meaning the limitations period begins when the fraud is discovered or should have been discovered through reasonable diligence.

Common timeframes:
- Most states: 3-6 years
- Federal securities fraud: 2 years from discovery, 5 years maximum
- Contract fraud: Often tied to contract limitations period

*Please specify the jurisdiction for more precise guidance.*"""
        
        if "overruled" in query_lower or "good law" in query_lower:
            if "roe" in query_lower:
                return """**Roe v. Wade (410 U.S. 113, 1973)** was explicitly overruled by **Dobbs v. Jackson Women's Health Organization (597 U.S. ___, 2022)**.

The Supreme Court in Dobbs held that:
1. The Constitution does not confer a right to abortion
2. Roe was "egregiously wrong from the start"
3. The authority to regulate abortion is returned to the states

**Citation Status: 🔴 RED FLAG** - Do not cite Roe v. Wade as controlling authority on abortion rights.

*See Dobbs, 597 U.S. at ___ (2022).*"""
            elif "chevron" in query_lower:
                return """**Chevron U.S.A. Inc. v. NRDC (467 U.S. 837, 1984)** was overruled by **Loper Bright Enterprises v. Raimondo (603 U.S. ___, 2024)**.

The Supreme Court held that courts must exercise independent judgment on questions of statutory interpretation, ending the 40-year practice of deferring to agency interpretations of ambiguous statutes.

**Citation Status: 🔴 RED FLAG** - Chevron deference is no longer valid law.

*See Loper Bright, 603 U.S. at ___ (2024).*"""
        
        if "miranda" in query_lower or "right to remain silent" in query_lower:
            return """Under **Miranda v. Arizona (384 U.S. 436, 1966)**, the following warnings must be given before custodial interrogation:

1. You have the right to remain silent
2. Anything you say can be used against you in court
3. You have the right to an attorney
4. If you cannot afford an attorney, one will be appointed

**Citation Status: 🟢 GREEN** - Miranda remains good law and is frequently cited.

The Miranda rule applies when a suspect is (1) in custody and (2) subject to interrogation. See also Dickerson v. United States, 530 U.S. 428 (2000) (reaffirming Miranda as constitutional rule)."""
        
        # Generic response using retrieved context
        if docs:
            top_doc = docs[0]
            return f"""Based on my research, here is what I found regarding your question about "{query}":

The most relevant case is **{top_doc['title']}** ({top_doc['citation']}), decided by the {top_doc['court']} on {top_doc['date_decided']}.

{top_doc['full_text'][:300]}...

This case addresses {', '.join(top_doc.get('topics', ['constitutional issues'])[:2])}.

**Citation Status: {self._status_to_emoji(top_doc.get('citation_status', 'green'))}**

*Please note: This is AI-generated analysis. Always verify with primary sources.*"""
        
        return """I couldn't find specific cases addressing your question in the current database. Please try:
1. Refining your search terms
2. Specifying a jurisdiction
3. Asking about a specific case or statute

*For comprehensive legal research, please consult primary legal databases.*"""
    
    def _status_to_emoji(self, status: str) -> str:
        """Convert status to emoji representation"""
        return {
            "green": "🟢 GREEN - Good law",
            "yellow": "🟡 YELLOW - Use with caution",
            "red": "🔴 RED - Overruled/Bad law",
            "orange": "🟠 ORANGE - Overruling risk"
        }.get(status, "⚪ Unknown")
    
    def _format_sources(self, docs: List[dict]) -> List[SourceCitation]:
        """Format retrieved documents as source citations"""
        sources = []
        for doc in docs[:5]:
            sources.append(SourceCitation(
                case_id=doc["id"],
                case_title=doc["title"],
                citation=doc["citation"],
                relevant_excerpt=doc["full_text"][:200] + "...",
                relevance_score=doc.get("relevance_score", 0.5)
            ))
        return sources
    
    def _get_follow_up_questions(self, query: str, docs: List[dict]) -> List[str]:
        """Generate follow-up questions based on query and results"""
        suggestions = []
        
        query_lower = query.lower()
        
        if "overruled" not in query_lower:
            suggestions.append("Is this case still good law?")
        
        if docs:
            topics = set()
            for doc in docs[:3]:
                topics.update(doc.get("topics", []))
            if topics:
                topic = list(topics)[0]
                suggestions.append(f"What are the leading cases on {topic}?")
        
        suggestions.append("What are the related statutes?")
        
        return suggestions[:3]
    
    def chat(self, request: ChatRequest) -> ChatResponse:
        """
        Process a chat request through the RAG pipeline:
        1. Retrieve relevant documents
        2. Build context
        3. Generate response with citations
        """
        # 1. Retrieve
        docs = self._retrieve_relevant_docs(request.message, top_k=5)
        
        # 2. Build context
        context = self._build_context(docs)
        
        # 3. Generate response (mock for MVP)
        if self.settings.use_mock_llm:
            answer = self._generate_mock_response(request.message, context, docs)
            confidence = 0.85 if docs else 0.3
        else:
            # TODO: Implement real LLM call
            answer = self._generate_mock_response(request.message, context, docs)
            confidence = 0.85
        
        # 4. Format response
        return ChatResponse(
            answer=answer,
            sources=self._format_sources(docs) if request.include_sources else [],
            confidence=confidence,
            follow_up_questions=self._get_follow_up_questions(request.message, docs)
        )


# Global service instance
_rag_service = None


def get_rag_service() -> RAGService:
    """Get RAG service instance"""
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service
