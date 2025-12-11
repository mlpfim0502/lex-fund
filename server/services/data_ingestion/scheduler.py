"""
Data ingestion scheduler
Periodic jobs for fetching legal and financial data
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
import logging

from .courtlistener import CourtListenerClient, CourtListenerIngester
from .sec_edgar import SECEdgarClient, COMPANY_CIKS

logger = logging.getLogger(__name__)


class DataIngestionScheduler:
    """
    Scheduler for periodic data ingestion jobs.
    
    Jobs:
    - Hourly: CourtListener new opinions
    - Daily: SEC EDGAR filings for watchlist
    - Weekly: Full legal risk refresh
    """
    
    def __init__(self, db=None):
        self.scheduler = AsyncIOScheduler()
        self.db = db
        self.courtlistener = CourtListenerClient()
        self.sec_edgar = SECEdgarClient()
        self.watchlist = list(COMPANY_CIKS.keys())  # Default watchlist
        
    def start(self):
        """Start the scheduler"""
        # Hourly: Fetch new court opinions
        self.scheduler.add_job(
            self.ingest_recent_opinions,
            IntervalTrigger(hours=1),
            id="hourly_opinions",
            name="Hourly Court Opinions",
            replace_existing=True
        )
        
        # Daily at 6 AM: Fetch SEC filings
        self.scheduler.add_job(
            self.ingest_sec_filings,
            CronTrigger(hour=6, minute=0),
            id="daily_sec_filings",
            name="Daily SEC Filings",
            replace_existing=True
        )
        
        # Weekly on Sunday: Full legal risk refresh
        self.scheduler.add_job(
            self.refresh_legal_risk_scores,
            CronTrigger(day_of_week="sun", hour=2),
            id="weekly_risk_refresh",
            name="Weekly Risk Refresh",
            replace_existing=True
        )
        
        self.scheduler.start()
        logger.info("Data ingestion scheduler started")
    
    def stop(self):
        """Stop the scheduler"""
        self.scheduler.shutdown()
        logger.info("Data ingestion scheduler stopped")
    
    async def ingest_recent_opinions(self):
        """Fetch and store recent court opinions"""
        logger.info("Starting hourly court opinion ingestion")
        
        try:
            opinions = await self.courtlistener.get_recent_opinions(days_back=1)
            
            for opinion in opinions:
                # Check for watchlist companies
                text = f"{opinion.get('caseName', '')} {opinion.get('docketNumber', '')}"
                for ticker in self.watchlist:
                    company = COMPANY_CIKS.get(ticker, "")
                    if company.lower() in text.lower():
                        logger.info(f"Found case mentioning {ticker}: {opinion.get('caseName')}")
                        # Store and trigger alert
                        await self._store_legal_event(ticker, opinion)
            
            logger.info(f"Ingested {len(opinions)} opinions")
            
        except Exception as e:
            logger.error(f"Error in opinion ingestion: {e}")
    
    async def ingest_sec_filings(self):
        """Fetch SEC filings for watchlist companies"""
        logger.info("Starting daily SEC filing ingestion")
        
        for ticker, cik in COMPANY_CIKS.items():
            if ticker not in self.watchlist:
                continue
            
            try:
                # Check for new 8-K filings (material events)
                filings = await self.sec_edgar.get_company_filings(cik, form_type="8-K", count=5)
                
                for filing in filings:
                    # Check if filing is from today
                    if filing["filing_date"] == datetime.now().strftime("%Y-%m-%d"):
                        logger.info(f"New 8-K for {ticker}: {filing['accession_number']}")
                        await self._process_8k_filing(ticker, filing)
                
            except Exception as e:
                logger.error(f"Error fetching SEC filings for {ticker}: {e}")
        
        logger.info("SEC filing ingestion complete")
    
    async def refresh_legal_risk_scores(self):
        """Weekly refresh of legal risk scores for all watchlist companies"""
        logger.info("Starting weekly legal risk refresh")
        
        for ticker, cik in COMPANY_CIKS.items():
            if ticker not in self.watchlist:
                continue
            
            try:
                risk_analysis = await self.sec_edgar.analyze_company_legal_risk(cik)
                
                # Store updated risk score
                if self.db:
                    await self.db.update_company_risk_score(
                        ticker,
                        risk_analysis["overall_risk_score"]
                    )
                
                logger.info(f"{ticker} legal risk score: {risk_analysis['overall_risk_score']:.2f}")
                
            except Exception as e:
                logger.error(f"Error refreshing risk for {ticker}: {e}")
        
        logger.info("Legal risk refresh complete")
    
    async def _store_legal_event(self, ticker: str, opinion: dict):
        """Store a legal event for a company"""
        if not self.db:
            return
        
        event = {
            "ticker": ticker,
            "event_type": "court_opinion",
            "case_name": opinion.get("caseName", ""),
            "court": opinion.get("court", ""),
            "date": opinion.get("dateFiled", ""),
            "severity": 0.5,  # Default - will be scored by LLM
            "detected_at": datetime.now().isoformat()
        }
        
        await self.db.store_legal_event(event)
    
    async def _process_8k_filing(self, ticker: str, filing: dict):
        """Process an 8-K filing for trading signals"""
        if not self.db:
            return
        
        # Get filing content
        try:
            events = await self.sec_edgar.get_8k_events(
                COMPANY_CIKS[ticker],
                days_back=1
            )
            
            for event in events:
                if event.is_legal_related:
                    await self.db.store_legal_event({
                        "ticker": ticker,
                        "event_type": "8k_legal",
                        "description": event.description[:500],
                        "severity": 0.7,  # Legal 8-Ks are higher severity
                        "detected_at": datetime.now().isoformat()
                    })
                    
        except Exception as e:
            logger.error(f"Error processing 8-K for {ticker}: {e}")
    
    def add_to_watchlist(self, ticker: str):
        """Add a company to the watchlist"""
        if ticker not in self.watchlist:
            self.watchlist.append(ticker)
            logger.info(f"Added {ticker} to watchlist")
    
    def remove_from_watchlist(self, ticker: str):
        """Remove a company from the watchlist"""
        if ticker in self.watchlist:
            self.watchlist.remove(ticker)
            logger.info(f"Removed {ticker} from watchlist")
    
    async def run_manual_ingestion(self, ticker: str = None):
        """Run manual data ingestion (for testing)"""
        if ticker:
            cik = COMPANY_CIKS.get(ticker)
            if cik:
                return await self.sec_edgar.analyze_company_legal_risk(cik)
        else:
            await self.ingest_recent_opinions()
            await self.ingest_sec_filings()
        
        return {"status": "complete"}


# Global scheduler instance
_scheduler = None


def get_scheduler(db=None) -> DataIngestionScheduler:
    """Get scheduler instance"""
    global _scheduler
    if _scheduler is None:
        _scheduler = DataIngestionScheduler(db)
    return _scheduler
