"""
SEC EDGAR Data Integration
Parse SEC filings for legal risk and material events
"""
import httpx
from typing import List, Dict, Optional
from datetime import datetime, date
from pydantic import BaseModel
import re
from bs4 import BeautifulSoup
from config import get_settings


class SECFiling(BaseModel):
    """SEC filing metadata"""
    accession_number: str
    form_type: str  # 10-K, 10-Q, 8-K, etc.
    filing_date: str
    company_name: str
    cik: str
    ticker: Optional[str] = None
    url: str


class LegalRiskSection(BaseModel):
    """Extracted legal risk information from filing"""
    filing_id: str
    risk_factors: List[str] = []
    legal_proceedings: List[str] = []
    contingencies: List[str] = []
    severity_score: float = 0.0  # 0-1 AI-scored severity


class MaterialEvent(BaseModel):
    """Material event from 8-K filing"""
    filing_id: str
    event_date: str
    event_type: str
    description: str
    is_legal_related: bool = False


class SECEdgarClient:
    """
    Client for SEC EDGAR (Electronic Data Gathering, Analysis, and Retrieval)
    
    Key filings for hedge fund:
    - 10-K: Annual report (Item 3 = Legal Proceedings)
    - 10-Q: Quarterly report (Legal update)
    - 8-K: Material events (lawsuits, settlements, investigations)
    - Form 4: Insider trading
    """
    
    BASE_URL = "https://data.sec.gov"
    SEARCH_URL = "https://efts.sec.gov/LATEST/search-index"
    
    def __init__(self):
        settings = get_settings()
        self.user_agent = settings.sec_edgar_user_agent
        self.headers = {
            "User-Agent": self.user_agent,
            "Accept-Encoding": "gzip, deflate",
            "Host": "data.sec.gov"
        }
    
    async def _request(self, url: str) -> str:
        """Make request to SEC EDGAR"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.text
    
    async def _request_json(self, url: str) -> Dict:
        """Make JSON request to SEC EDGAR"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
    
    async def get_company_filings(
        self,
        cik: str,
        form_type: str = None,
        count: int = 40
    ) -> List[Dict]:
        """
        Get recent filings for a company.
        
        Args:
            cik: Central Index Key (company identifier)
            form_type: Filter by form type (10-K, 10-Q, 8-K)
            count: Number of filings to retrieve
        """
        # Pad CIK to 10 digits
        cik_padded = cik.zfill(10)
        
        url = f"{self.BASE_URL}/submissions/CIK{cik_padded}.json"
        data = await self._request_json(url)
        
        filings = []
        recent = data.get("filings", {}).get("recent", {})
        
        forms = recent.get("form", [])
        dates = recent.get("filingDate", [])
        accessions = recent.get("accessionNumber", [])
        
        for i in range(min(count, len(forms))):
            if form_type and forms[i] != form_type:
                continue
            
            filings.append({
                "form_type": forms[i],
                "filing_date": dates[i],
                "accession_number": accessions[i],
                "company_name": data.get("name", ""),
                "cik": cik,
                "ticker": data.get("tickers", [""])[0] if data.get("tickers") else ""
            })
        
        return filings
    
    async def get_filing_document(
        self,
        cik: str,
        accession_number: str,
        document_type: str = "10-K"
    ) -> str:
        """Get the primary document from a filing"""
        cik_padded = cik.zfill(10)
        accession_clean = accession_number.replace("-", "")
        
        # Get filing index
        index_url = f"{self.BASE_URL}/Archives/edgar/data/{cik_padded}/{accession_clean}/index.json"
        index_data = await self._request_json(index_url)
        
        # Find primary document
        for item in index_data.get("directory", {}).get("item", []):
            name = item.get("name", "")
            if name.endswith(".htm") and document_type.lower() in name.lower():
                doc_url = f"{self.BASE_URL}/Archives/edgar/data/{cik_padded}/{accession_clean}/{name}"
                return await self._request(doc_url)
        
        return ""
    
    def extract_legal_proceedings(self, html_content: str) -> List[str]:
        """
        Extract Item 3 (Legal Proceedings) from 10-K/10-Q.
        This is critical for litigation risk assessment.
        """
        soup = BeautifulSoup(html_content, "lxml")
        text = soup.get_text()
        
        # Find Item 3 section
        legal_section = []
        
        # Common patterns for legal proceedings section
        patterns = [
            r"ITEM\s+3\.?\s*[-–—]?\s*LEGAL PROCEEDINGS(.*?)ITEM\s+4",
            r"Item\s+3\.?\s*[-–—]?\s*Legal Proceedings(.*?)Item\s+4",
            r"LEGAL PROCEEDINGS(.*?)(?:ITEM\s+4|PART\s+II)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
            if match:
                legal_text = match.group(1).strip()
                # Split into paragraphs
                paragraphs = [p.strip() for p in legal_text.split("\n\n") if p.strip()]
                legal_section.extend(paragraphs[:10])  # Limit to first 10 paragraphs
                break
        
        return legal_section
    
    def extract_risk_factors(self, html_content: str) -> List[str]:
        """
        Extract Item 1A (Risk Factors) from 10-K/10-Q.
        Filter for legal/regulatory risks.
        """
        soup = BeautifulSoup(html_content, "lxml")
        text = soup.get_text()
        
        risk_factors = []
        
        # Find risk factors section
        pattern = r"ITEM\s+1A\.?\s*[-–—]?\s*RISK FACTORS(.*?)ITEM\s+1B"
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        
        if match:
            risks_text = match.group(1)
            
            # Find legal-related risks
            legal_keywords = [
                "litigation", "lawsuit", "legal", "regulatory",
                "investigation", "subpoena", "settlement", "judgment",
                "antitrust", "patent", "intellectual property", "compliance"
            ]
            
            paragraphs = risks_text.split("\n\n")
            for para in paragraphs:
                para_lower = para.lower()
                if any(kw in para_lower for kw in legal_keywords):
                    risk_factors.append(para.strip()[:500])  # Truncate long paragraphs
        
        return risk_factors[:20]  # Limit to 20 factors
    
    async def get_8k_events(
        self,
        cik: str,
        days_back: int = 30
    ) -> List[MaterialEvent]:
        """
        Get recent 8-K material events.
        8-Ks contain immediate disclosure of major events.
        """
        filings = await self.get_company_filings(cik, form_type="8-K", count=20)
        
        events = []
        for filing in filings:
            # Get 8-K content
            try:
                content = await self.get_filing_document(
                    cik,
                    filing["accession_number"],
                    "8-K"
                )
                
                if content:
                    event = self._parse_8k_event(content, filing)
                    if event:
                        events.append(event)
            except Exception as e:
                print(f"Error parsing 8-K {filing['accession_number']}: {e}")
        
        return events
    
    def _parse_8k_event(self, html_content: str, filing: Dict) -> Optional[MaterialEvent]:
        """Parse 8-K to extract event type and description"""
        soup = BeautifulSoup(html_content, "lxml")
        text = soup.get_text()
        
        # 8-K Item numbers indicate event type
        legal_items = {
            "Item 1.01": "Entry into Material Agreement",
            "Item 2.01": "Acquisition/Disposition",
            "Item 3.01": "Securities Delisting",
            "Item 8.01": "Other Events"  # Often includes legal matters
        }
        
        event_type = "Unknown"
        is_legal = False
        
        for item, desc in legal_items.items():
            if item in text:
                event_type = desc
                # Check if legal-related
                legal_keywords = ["litigation", "lawsuit", "settlement", "investigation", "legal"]
                if any(kw in text.lower() for kw in legal_keywords):
                    is_legal = True
                break
        
        return MaterialEvent(
            filing_id=filing["accession_number"],
            event_date=filing["filing_date"],
            event_type=event_type,
            description=text[:500],  # First 500 chars
            is_legal_related=is_legal
        )
    
    async def analyze_company_legal_risk(
        self,
        cik: str
    ) -> Dict:
        """
        Comprehensive legal risk analysis for a company.
        Aggregates data from 10-K, 10-Q, and 8-K filings.
        """
        result = {
            "cik": cik,
            "legal_proceedings": [],
            "risk_factors": [],
            "recent_events": [],
            "overall_risk_score": 0.0
        }
        
        # Get latest 10-K
        filings_10k = await self.get_company_filings(cik, form_type="10-K", count=1)
        if filings_10k:
            content = await self.get_filing_document(
                cik,
                filings_10k[0]["accession_number"],
                "10-K"
            )
            if content:
                result["legal_proceedings"] = self.extract_legal_proceedings(content)
                result["risk_factors"] = self.extract_risk_factors(content)
        
        # Get recent 8-Ks
        result["recent_events"] = await self.get_8k_events(cik)
        
        # Calculate risk score (simple heuristic - in production use LLM)
        legal_count = len([e for e in result["recent_events"] if e.is_legal_related])
        proceeding_count = len(result["legal_proceedings"])
        
        result["overall_risk_score"] = min(1.0, (legal_count * 0.2) + (proceeding_count * 0.1))
        
        return result


# CIK lookup table for common companies
COMPANY_CIKS = {
    "AAPL": "320193",
    "MSFT": "789019",
    "GOOGL": "1652044",
    "AMZN": "1018724",
    "META": "1326801",
    "TSLA": "1318605",
    "NVDA": "1045810",
    "JPM": "19617",
    "GS": "886982",
    "BAC": "70858"
}


def get_cik(ticker: str) -> Optional[str]:
    """Get CIK for a ticker symbol"""
    return COMPANY_CIKS.get(ticker.upper())


# Singleton client
_client = None


def get_sec_edgar_client() -> SECEdgarClient:
    """Get SEC EDGAR client instance"""
    global _client
    if _client is None:
        _client = SECEdgarClient()
    return _client
