"""
Signal Generator Service
Generate trading signals from legal events using LLM analysis
"""
import json
from typing import Optional, Dict, List
from datetime import datetime
from pydantic import BaseModel
import httpx

from config import get_settings
from prompts import format_prompt, LITIGATION_RISK_PROMPT


class TradingSignal(BaseModel):
    """Trading signal from legal analysis"""
    ticker: str
    signal_type: str  # long, short, neutral, monitor
    confidence: float
    rationale: str
    event_id: Optional[int] = None
    recommended_size_pct: Optional[float] = None
    expires_at: Optional[str] = None


class LegalAnalysisResult(BaseModel):
    """Structured result from LLM legal analysis"""
    liability_probability: float = 0.0
    estimated_damages_usd: Optional[float] = None
    timeline_to_resolution_months: int = 12
    stock_impact_assessment: str = "unknown"
    key_risk_factors: List[str] = []
    recommendation: str = "monitor"
    confidence: float = 0.0
    reasoning: str = ""


class SignalGenerator:
    """
    Generate trading signals from legal events.
    
    Pipeline:
    1. Receive legal event (case filing, SEC event, etc.)
    2. Retrieve company context (market cap, sector, history)
    3. Run LLM analysis with specialized prompts
    4. Parse structured output
    5. Apply risk thresholds
    6. Generate actionable signal
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.use_mock = self.settings.use_mock_llm
    
    async def _call_llm(self, prompt: str) -> str:
        """Call LLM (OpenAI or Anthropic) with the prompt"""
        if self.use_mock:
            return self._mock_llm_response(prompt)
        
        if self.settings.llm_provider == "anthropic" and self.settings.anthropic_api_key:
            return await self._call_anthropic(prompt)
        elif self.settings.openai_api_key:
            return await self._call_openai(prompt)
        else:
            return self._mock_llm_response(prompt)
    
    async def _call_openai(self, prompt: str) -> str:
        """Call OpenAI API"""
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.settings.openai_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.settings.llm_model,
                    "messages": [
                        {"role": "system", "content": "You are a legal analyst at a hedge fund. Respond with valid JSON only."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.1,  # Low temperature for consistency
                    "response_format": {"type": "json_object"}
                }
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
    
    async def _call_anthropic(self, prompt: str) -> str:
        """Call Anthropic API"""
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": self.settings.anthropic_api_key,
                    "Content-Type": "application/json",
                    "anthropic-version": "2023-06-01"
                },
                json={
                    "model": "claude-3-sonnet-20240229",
                    "max_tokens": 2000,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ]
                }
            )
            response.raise_for_status()
            data = response.json()
            return data["content"][0]["text"]
    
    def _mock_llm_response(self, prompt: str) -> str:
        """Mock LLM response for testing"""
        # Return a sensible mock based on prompt content
        if "short" in prompt.lower() or "litigation" in prompt.lower():
            return json.dumps({
                "liability_probability": 0.65,
                "estimated_damages_usd": 500000000,
                "damages_as_pct_market_cap": 2.5,
                "timeline_to_resolution_months": 18,
                "stock_impact_assessment": "moderate_negative",
                "key_risk_factors": [
                    "Strong plaintiff evidence",
                    "Unfavorable jurisdiction",
                    "Similar cases resulted in large settlements"
                ],
                "key_mitigating_factors": [
                    "Company has strong legal team",
                    "Insurance coverage available"
                ],
                "precedent_cases": ["Similar Co. v. Plaintiff (2022) - $300M settlement"],
                "recommendation": "monitor",
                "confidence": 0.72,
                "reasoning": "While the case presents material risk, the liability probability does not meet our threshold for a short recommendation. Continue monitoring for developments."
            })
        else:
            return json.dumps({
                "recommendation": "no_action",
                "confidence": 0.5,
                "reasoning": "Insufficient information for trading signal."
            })
    
    def _parse_analysis(self, llm_response: str) -> LegalAnalysisResult:
        """Parse LLM JSON response into structured result"""
        try:
            data = json.loads(llm_response)
            return LegalAnalysisResult(**data)
        except (json.JSONDecodeError, Exception) as e:
            print(f"Error parsing LLM response: {e}")
            return LegalAnalysisResult(
                recommendation="monitor",
                confidence=0.0,
                reasoning="Failed to parse LLM response"
            )
    
    async def analyze_litigation(
        self,
        case_name: str,
        court: str,
        date_filed: str,
        company_name: str,
        ticker: str,
        case_summary: str,
        nature_of_suit: str = "Unknown"
    ) -> TradingSignal:
        """
        Analyze a litigation event and generate trading signal.
        
        Args:
            case_name: Name of the case
            court: Court where filed
            date_filed: Filing date
            company_name: Company name
            ticker: Stock ticker
            case_summary: Summary of case
            nature_of_suit: Type of lawsuit
            
        Returns:
            TradingSignal with recommendation
        """
        # Format the prompt
        prompt = format_prompt(
            "litigation_risk",
            case_name=case_name,
            court=court,
            date_filed=date_filed,
            company_name=company_name,
            ticker=ticker,
            case_summary=case_summary,
            nature_of_suit=nature_of_suit
        )
        
        # Call LLM
        response = await self._call_llm(prompt)
        
        # Parse response
        analysis = self._parse_analysis(response)
        
        # Generate signal based on thresholds
        signal_type = "neutral"
        recommended_size = 0.0
        
        if analysis.recommendation == "short" and analysis.confidence > 0.7:
            signal_type = "short"
            recommended_size = min(0.05, analysis.confidence * 0.05)  # Max 5%
        elif analysis.recommendation == "avoid":
            signal_type = "neutral"  # Avoid means don't hold, but don't short either
        elif analysis.recommendation == "monitor":
            signal_type = "monitor"
        
        return TradingSignal(
            ticker=ticker,
            signal_type=signal_type,
            confidence=analysis.confidence,
            rationale=analysis.reasoning,
            recommended_size_pct=recommended_size
        )
    
    async def analyze_regulatory_event(
        self,
        agency: str,
        rule_title: str,
        pub_date: str,
        comment_deadline: str,
        industries: str,
        rule_summary: str
    ) -> List[TradingSignal]:
        """Analyze regulatory change and generate signals for affected sectors"""
        prompt = format_prompt(
            "regulatory_change",
            agency=agency,
            rule_title=rule_title,
            pub_date=pub_date,
            comment_deadline=comment_deadline,
            industries=industries,
            rule_summary=rule_summary
        )
        
        response = await self._call_llm(prompt)
        
        try:
            data = json.loads(response)
            signals = []
            
            # Generate signals for trading opportunities
            for opportunity in data.get("trading_opportunities", []):
                signals.append(TradingSignal(
                    ticker=opportunity.get("instrument", "SPY"),
                    signal_type=opportunity.get("action", "neutral"),
                    confidence=data.get("confidence", 0.5),
                    rationale=opportunity.get("rationale", "")
                ))
            
            return signals
            
        except Exception as e:
            print(f"Error parsing regulatory analysis: {e}")
            return []
    
    async def batch_analyze(
        self,
        events: List[Dict]
    ) -> List[TradingSignal]:
        """Analyze multiple events and return signals"""
        signals = []
        
        for event in events:
            event_type = event.get("type", "litigation")
            
            if event_type == "litigation":
                signal = await self.analyze_litigation(
                    case_name=event.get("case_name", ""),
                    court=event.get("court", ""),
                    date_filed=event.get("date_filed", ""),
                    company_name=event.get("company_name", ""),
                    ticker=event.get("ticker", ""),
                    case_summary=event.get("summary", ""),
                    nature_of_suit=event.get("nature_of_suit", "Unknown")
                )
                signals.append(signal)
            
            elif event_type == "regulatory":
                reg_signals = await self.analyze_regulatory_event(
                    agency=event.get("agency", ""),
                    rule_title=event.get("rule_title", ""),
                    pub_date=event.get("pub_date", ""),
                    comment_deadline=event.get("comment_deadline", ""),
                    industries=event.get("industries", ""),
                    rule_summary=event.get("summary", "")
                )
                signals.extend(reg_signals)
        
        return signals


# Singleton
_generator = None


def get_signal_generator() -> SignalGenerator:
    """Get signal generator instance"""
    global _generator
    if _generator is None:
        _generator = SignalGenerator()
    return _generator
