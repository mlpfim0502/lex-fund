"""
Document serving router for template files.
"""
from fastapi import APIRouter, HTTPException
from pathlib import Path

router = APIRouter(prefix="/api/docs", tags=["documents"])

# Base path for documents
DOCS_DIR = Path(__file__).parent.parent.parent / "docs"


@router.get("/{path:path}")
async def get_document(path: str):
    """
    Retrieve a document file by path.
    
    Args:
        path: Relative path to the document from docs directory
        
    Returns:
        Document content and metadata
    """
    # Prevent path traversal attacks
    if ".." in path:
        raise HTTPException(status_code=400, detail="Invalid path")
    
    doc_path = DOCS_DIR / path
    
    if not doc_path.exists():
        raise HTTPException(status_code=404, detail=f"Document not found: {path}")
    
    if not doc_path.is_file():
        raise HTTPException(status_code=400, detail="Path is not a file")
    
    # Only allow markdown files
    if not path.endswith('.md'):
        raise HTTPException(status_code=400, detail="Only markdown files are supported")
    
    try:
        content = doc_path.read_text(encoding='utf-8')
        return {
            "path": path,
            "content": content,
            "filename": doc_path.name
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading document: {str(e)}")
