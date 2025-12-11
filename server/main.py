"""
LexAI - Legal Research Platform
Main FastAPI Application Entry Point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from config import get_settings
from routers import cases_router, search_router, chat_router, analytics_router, data_router, checklist_router, docs_router, backtest_router
from db.database import get_db
from db.graph import initialize_graph_from_db
from db.vector import initialize_vector_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print("🚀 Starting LexAI Legal Intelligence Platform...")
    
    # Initialize databases
    db = get_db()
    print(f"📚 Loaded {len(db.get_all_cases())} sample cases")
    
    # Initialize graph database
    graph = initialize_graph_from_db(db)
    print(f"🔗 Initialized citation graph with {len(graph.nodes)} nodes")
    
    # Initialize vector database
    vector_db = initialize_vector_db(db)
    print(f"🧠 Indexed {vector_db.count()} documents for semantic search")
    
    print("✅ LexAI is ready!")
    print("📈 Hedge Fund Edition v2.0 - Legal Alpha Platform")
    
    yield
    
    # Shutdown
    print("👋 Shutting down LexAI...")


# Create FastAPI application
settings = get_settings()

app = FastAPI(
    title="LexAI",
    description="""
## Legal Intelligence Platform - Hedge Fund Edition

### Core Features
- 🔍 **Hybrid Search**: Semantic + keyword search with RRF fusion
- ⚖️ **Citation Analysis**: KeyCite-style validity checking
- 🚨 **Bad Law Bot**: Automatic detection of overruled precedents
- 💬 **AI Assistant**: RAG-powered legal Q&A with source citations

### Hedge Fund Features
- 📊 **Litigation Analytics**: Judge and attorney statistics
- 📈 **Signal Generation**: Legal event → trading signals
- 🔄 **Real-time Ingestion**: CourtListener & SEC EDGAR integration
- 🎯 **Company Watchlist**: Monitor litigation for positions
- 📋 **Fund Formation Checklist**: Track legal requirements for hedge fund setup

### API Documentation
Use the interactive docs below to explore the API endpoints.
    """,
    version=settings.app_version,
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(cases_router)
app.include_router(search_router)
app.include_router(chat_router)
app.include_router(analytics_router)
app.include_router(data_router)
app.include_router(checklist_router)
app.include_router(docs_router)
app.include_router(backtest_router)


@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "name": "LexAI",
        "version": settings.app_version,
        "description": "Legal Intelligence Platform - Hedge Fund Edition",
        "docs": "/docs",
        "endpoints": {
            "cases": "/api/cases",
            "search": "/api/search",
            "chat": "/api/chat",
            "analytics": "/api/analytics",
            "data": "/api/data",
            "checklist": "/api/checklist"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    db = get_db()
    return {
        "status": "healthy",
        "database": "connected",
        "cases_loaded": len(db.get_all_cases())
    }


if __name__ == "__main__":
    import uvicorn
    import os
    # Use PORT env var for Cloud Run, fallback to settings
    port = int(os.environ.get("PORT", settings.port))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=settings.debug
    )
