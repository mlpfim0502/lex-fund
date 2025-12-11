"""
Chat API Router - RAG-powered Legal Q&A
"""
from fastapi import APIRouter
from models.search import ChatRequest, ChatResponse
from services.rag import get_rag_service

router = APIRouter(prefix="/api/chat", tags=["Chat"])


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Ask a legal question and get an AI-generated answer with source citations.
    
    The RAG pipeline:
    1. Retrieves relevant cases and statutes
    2. Builds context from retrieved documents
    3. Generates answer with proper citations
    4. Validates response against sources
    """
    rag_service = get_rag_service()
    return rag_service.chat(request)


@router.get("/examples")
async def get_example_questions():
    """Get example questions to help users get started"""
    examples = [
        {
            "question": "What is the statute of limitations for fraud in Florida?",
            "category": "Statutes"
        },
        {
            "question": "Is Roe v. Wade still good law?",
            "category": "Case Validity"
        },
        {
            "question": "What are the Miranda rights requirements?",
            "category": "Criminal Procedure"
        },
        {
            "question": "What is the Chevron deference doctrine?",
            "category": "Administrative Law"
        },
        {
            "question": "What are the elements of defamation for public officials?",
            "category": "First Amendment"
        },
        {
            "question": "When can police conduct a Terry stop?",
            "category": "Fourth Amendment"
        }
    ]
    return {"examples": examples}
