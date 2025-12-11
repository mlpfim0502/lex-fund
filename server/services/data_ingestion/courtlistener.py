"""
CourtListener API Integration
Real-time federal case data ingestion
"""
import httpx
from typing import List, Dict, Optional, AsyncGenerator
from datetime import datetime, date
from pydantic import BaseModel
import asyncio
from config import get_settings


class CourtListenerCase(BaseModel):
    """Case data from CourtListener API"""
    id: int
    case_name: str
    docket_number: Optional[str] = None
    court: str
    date_filed: Optional[str] = None
    date_terminated: Optional[str] = None
    nature_of_suit: Optional[str] = None
    cause: Optional[str] = None
    jury_demand: Optional[str] = None


class CourtListenerOpinion(BaseModel):
    """Opinion data from CourtListener API"""
    id: int
    cluster_id: int
    case_name: str
    court: str
    date_filed: str
    citation: Optional[str] = None
    plain_text: Optional[str] = None
    html: Optional[str] = None


class CourtListenerClient:
    """
    Client for CourtListener API (free.law)
    
    CourtListener provides:
    - Federal court opinions (PACER via RECAP)
    - Docket tracking
    - Oral argument audio
    - Citation network
    """
    
    BASE_URL = "https://www.courtlistener.com/api/rest/v3"
    
    def __init__(self):
        settings = get_settings()
        self.api_key = settings.courtlistener_api_key
        self.headers = {
            "Authorization": f"Token {self.api_key}" if self.api_key else "",
            "Content-Type": "application/json"
        }
    
    async def _request(self, endpoint: str, params: Dict = None) -> Dict:
        """Make API request to CourtListener"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            url = f"{self.BASE_URL}/{endpoint}/"
            response = await client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
    
    async def search_opinions(
        self,
        query: str,
        court: str = None,
        filed_after: date = None,
        filed_before: date = None,
        page: int = 1
    ) -> Dict:
        """
        Search for court opinions.
        
        Args:
            query: Search terms
            court: Court filter (e.g., "scotus", "ca9")
            filed_after: Filter by date
            filed_before: Filter by date
            page: Page number for pagination
        """
        params = {
            "q": query,
            "type": "o",  # opinions
            "page": page
        }
        
        if court:
            params["court"] = court
        if filed_after:
            params["filed_after"] = filed_after.isoformat()
        if filed_before:
            params["filed_before"] = filed_before.isoformat()
        
        return await self._request("search", params)
    
    async def get_opinion(self, opinion_id: int) -> Dict:
        """Get a specific opinion by ID"""
        return await self._request(f"opinions/{opinion_id}")
    
    async def get_docket(self, docket_id: int) -> Dict:
        """Get docket information"""
        return await self._request(f"dockets/{docket_id}")
    
    async def search_dockets(
        self,
        query: str = None,
        party_name: str = None,
        court: str = None,
        filed_after: date = None
    ) -> Dict:
        """
        Search for dockets (cases).
        Useful for tracking company litigation.
        
        Args:
            query: Search terms
            party_name: Filter by party (e.g., company name)
            court: Court filter
            filed_after: Filter by date
        """
        params = {"type": "d"}  # dockets
        
        if query:
            params["q"] = query
        if party_name:
            params["party_name"] = party_name
        if court:
            params["court"] = court
        if filed_after:
            params["filed_after"] = filed_after.isoformat()
        
        return await self._request("search", params)
    
    async def get_citations(self, opinion_id: int) -> Dict:
        """Get citations for an opinion"""
        return await self._request(f"opinions/{opinion_id}/cited-by")
    
    async def search_company_litigation(
        self,
        company_name: str,
        ticker: str = None
    ) -> List[Dict]:
        """
        Search for litigation involving a specific company.
        Key function for hedge fund legal risk analysis.
        
        Args:
            company_name: Company name (e.g., "Apple Inc")
            ticker: Optional stock ticker for additional search
        """
        results = []
        
        # Search by company name
        dockets = await self.search_dockets(party_name=company_name)
        if dockets.get("results"):
            results.extend(dockets["results"])
        
        # Also search opinions mentioning company
        opinions = await self.search_opinions(query=company_name)
        if opinions.get("results"):
            results.extend(opinions["results"])
        
        return results
    
    async def get_recent_opinions(
        self,
        court: str = None,
        days_back: int = 7
    ) -> List[Dict]:
        """Get recent opinions for monitoring"""
        from datetime import timedelta
        
        filed_after = date.today() - timedelta(days=days_back)
        result = await self.search_opinions(
            query="*",
            court=court,
            filed_after=filed_after
        )
        return result.get("results", [])


class CourtListenerIngester:
    """
    Ingestion service for CourtListener data.
    Handles periodic fetching and storage.
    """
    
    def __init__(self, db, client: CourtListenerClient = None):
        self.client = client or CourtListenerClient()
        self.db = db
    
    async def ingest_recent_opinions(self, days: int = 1):
        """Ingest recent opinions into database"""
        opinions = await self.client.get_recent_opinions(days_back=days)
        
        ingested = 0
        for opinion in opinions:
            try:
                # Store in database
                await self.db.store_opinion(opinion)
                ingested += 1
            except Exception as e:
                print(f"Error ingesting opinion {opinion.get('id')}: {e}")
        
        return {"ingested": ingested, "total": len(opinions)}
    
    async def monitor_company(self, company_name: str, ticker: str):
        """
        Set up monitoring for a company's litigation.
        Returns new cases found.
        """
        cases = await self.client.search_company_litigation(company_name, ticker)
        
        new_cases = []
        for case in cases:
            # Check if already in database
            existing = await self.db.get_case_by_external_id(case.get("id"))
            if not existing:
                await self.db.store_case(case, company_name, ticker)
                new_cases.append(case)
        
        return new_cases


# Singleton client
_client = None


def get_courtlistener_client() -> CourtListenerClient:
    """Get CourtListener client instance"""
    global _client
    if _client is None:
        _client = CourtListenerClient()
    return _client
