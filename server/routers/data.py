"""
Data Ingestion API Router
Endpoints for triggering data ingestion and monitoring
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from typing import Optional, List
from pydantic import BaseModel

from services.data_ingestion import (
    get_courtlistener_client,
    get_sec_edgar_client,
    get_scheduler,
    get_cik,
    COMPANY_CIKS
)
from services.signal_generator import get_signal_generator, TradingSignal

router = APIRouter(prefix="/api/data", tags=["Data Ingestion"])


class WatchlistItem(BaseModel):
    ticker: str
    company_name: Optional[str] = None


class IngestionStatus(BaseModel):
    job_id: str
    status: str
    completed: int = 0
    total: int = 0
    errors: List[str] = []


# ============================================================================
# WATCHLIST MANAGEMENT
# ============================================================================

@router.get("/watchlist")
async def get_watchlist():
    """Get current watchlist of monitored companies"""
    scheduler = get_scheduler()
    return {
        "watchlist": scheduler.watchlist,
        "companies": [
            {"ticker": t, "cik": COMPANY_CIKS.get(t)}
            for t in scheduler.watchlist
        ]
    }


@router.post("/watchlist")
async def add_to_watchlist(item: WatchlistItem):
    """Add a company to the monitoring watchlist"""
    scheduler = get_scheduler()
    
    if item.ticker not in COMPANY_CIKS:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown ticker {item.ticker}. Add CIK mapping first."
        )
    
    scheduler.add_to_watchlist(item.ticker)
    return {"status": "added", "ticker": item.ticker}


@router.delete("/watchlist/{ticker}")
async def remove_from_watchlist(ticker: str):
    """Remove a company from the monitoring watchlist"""
    scheduler = get_scheduler()
    scheduler.remove_from_watchlist(ticker)
    return {"status": "removed", "ticker": ticker}


# ============================================================================
# MANUAL DATA INGESTION
# ============================================================================

@router.post("/ingest/opinions")
async def ingest_court_opinions(
    background_tasks: BackgroundTasks,
    days: int = Query(default=1, le=30)
):
    """Trigger manual ingestion of recent court opinions"""
    client = get_courtlistener_client()
    
    async def ingest():
        return await client.get_recent_opinions(days_back=days)
    
    background_tasks.add_task(ingest)
    return {"status": "started", "job": "court_opinions", "days": days}


@router.post("/ingest/company/{ticker}")
async def ingest_company_data(
    ticker: str,
    background_tasks: BackgroundTasks
):
    """Ingest all legal data for a specific company"""
    cik = get_cik(ticker)
    if not cik:
        raise HTTPException(status_code=404, detail=f"No CIK found for {ticker}")
    
    sec_client = get_sec_edgar_client()
    cl_client = get_courtlistener_client()
    
    # Get SEC filings
    filings = await sec_client.get_company_filings(cik, count=10)
    
    # Get litigation
    # Note: This requires CourtListener API key for full access
    # litigation = await cl_client.search_company_litigation(ticker)
    
    return {
        "ticker": ticker,
        "cik": cik,
        "sec_filings_found": len(filings),
        "filings": filings[:5]  # Return first 5
    }


@router.get("/company/{ticker}/legal-risk")
async def get_company_legal_risk(ticker: str):
    """Get comprehensive legal risk analysis for a company"""
    cik = get_cik(ticker)
    if not cik:
        raise HTTPException(status_code=404, detail=f"No CIK found for {ticker}")
    
    sec_client = get_sec_edgar_client()
    
    try:
        risk_analysis = await sec_client.analyze_company_legal_risk(cik)
        return {
            "ticker": ticker,
            "cik": cik,
            **risk_analysis
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# SIGNAL GENERATION
# ============================================================================

@router.post("/signals/analyze")
async def analyze_event_for_signal(
    case_name: str,
    court: str,
    company_name: str,
    ticker: str,
    case_summary: str,
    nature_of_suit: str = "Unknown"
):
    """
    Analyze a legal event and generate trading signal.
    Uses LLM to assess litigation risk and recommend action.
    """
    generator = get_signal_generator()
    
    signal = await generator.analyze_litigation(
        case_name=case_name,
        court=court,
        date_filed="2024-01-01",  # Would come from event
        company_name=company_name,
        ticker=ticker,
        case_summary=case_summary,
        nature_of_suit=nature_of_suit
    )
    
    return signal


@router.get("/signals/test")
async def test_signal_generation(ticker: str = "AAPL"):
    """Test signal generation with a mock case"""
    generator = get_signal_generator()
    
    signal = await generator.analyze_litigation(
        case_name="Test v. Company Inc.",
        court="US District Court, N.D. California",
        date_filed="2024-12-01",
        company_name="Apple Inc.",
        ticker=ticker,
        case_summary="Plaintiff alleges patent infringement on mobile device technology. Claims $500M in damages.",
        nature_of_suit="Patent Infringement"
    )
    
    return {
        "test_case": "Patent Infringement Mock",
        "signal": signal
    }


# ============================================================================
# SCHEDULER STATUS
# ============================================================================

@router.get("/scheduler/status")
async def get_scheduler_status():
    """Get data ingestion scheduler status"""
    scheduler = get_scheduler()
    
    jobs = []
    for job in scheduler.scheduler.get_jobs():
        jobs.append({
            "id": job.id,
            "name": job.name,
            "next_run": str(job.next_run_time) if job.next_run_time else None
        })
    
    return {
        "running": scheduler.scheduler.running,
        "jobs": jobs,
        "watchlist_count": len(scheduler.watchlist)
    }


@router.post("/scheduler/start")
async def start_scheduler():
    """Start the data ingestion scheduler"""
    scheduler = get_scheduler()
    if not scheduler.scheduler.running:
        scheduler.start()
    return {"status": "started"}


@router.post("/scheduler/stop")
async def stop_scheduler():
    """Stop the data ingestion scheduler"""
    scheduler = get_scheduler()
    if scheduler.scheduler.running:
        scheduler.stop()
    return {"status": "stopped"}
