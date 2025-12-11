# LexAI - Westlaw Edge Alternative

A modern legal research platform with AI-powered features including citation analysis, semantic search, and legal know-how automation.

## Architecture

- **Backend**: FastAPI (Python) with PostgreSQL, Neo4j, and Qdrant
- **Frontend**: React + Vite with premium dark theme UI
- **AI**: RAG pipeline with LLM integration

## Quick Start

### Backend
```bash
cd server
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend
```bash
cd client
npm install
npm run dev
```

## Features

- 🔍 **Hybrid Search**: Semantic + keyword search for comprehensive results
- ⚖️ **Citation Graph**: Neo4j-powered citation relationships and authority analysis
- 🚨 **Bad Law Bot**: Algorithmic detection of overruled precedents
- 💬 **AI Assistant**: RAG-powered legal Q&A with citations
- 📊 **Litigation Analytics**: Judge and attorney statistics
- 📝 **Document Comparison**: Side-by-side statute diff view

## License

MIT
