"""
Database connection utilities
"""
from typing import Dict, List, Optional
import json
from datetime import date, datetime


# In-memory storage for MVP (simulates PostgreSQL)
class InMemoryDB:
    """Simple in-memory database for MVP demonstration"""
    
    def __init__(self):
        self.cases: Dict[str, dict] = {}
        self.citations: List[dict] = []
        self._load_sample_data()
    
    def _load_sample_data(self):
        """Load sample legal cases for demonstration"""
        sample_cases = [
            {
                "id": "case_001",
                "title": "Brown v. Board of Education",
                "citation": "347 U.S. 483",
                "court": "Supreme Court of the United States",
                "court_level": "supreme",
                "date_decided": "1954-05-17",
                "jurisdiction": "federal",
                "full_text": "We conclude that, in the field of public education, the doctrine of 'separate but equal' has no place. Separate educational facilities are inherently unequal. Therefore, we hold that the plaintiffs and others similarly situated are deprived of the equal protection of the laws guaranteed by the Fourteenth Amendment.",
                "headnotes": ["Equal Protection", "Public Education", "Desegregation"],
                "topics": ["Constitutional Law", "Civil Rights", "Education Law"],
                "citation_status": "green",
                "authority_score": 0.98,
                "citing_count": 0,
                "cited_by_count": 15420
            },
            {
                "id": "case_002",
                "title": "Marbury v. Madison",
                "citation": "5 U.S. 137",
                "court": "Supreme Court of the United States",
                "court_level": "supreme",
                "date_decided": "1803-02-24",
                "jurisdiction": "federal",
                "full_text": "It is emphatically the province and duty of the Judicial Department to say what the law is. Those who apply the rule to particular cases must, of necessity, expound and interpret that rule. If two laws conflict with each other, the Courts must decide on the operation of each.",
                "headnotes": ["Judicial Review", "Constitutional Interpretation", "Supremacy"],
                "topics": ["Constitutional Law", "Judicial Power", "Separation of Powers"],
                "citation_status": "green",
                "authority_score": 0.99,
                "citing_count": 0,
                "cited_by_count": 25000
            },
            {
                "id": "case_003",
                "title": "Miranda v. Arizona",
                "citation": "384 U.S. 436",
                "court": "Supreme Court of the United States",
                "court_level": "supreme",
                "date_decided": "1966-06-13",
                "jurisdiction": "federal",
                "full_text": "The person in custody must, prior to interrogation, be clearly informed that he has the right to remain silent, and that anything he says will be used against him in court; he must be clearly informed that he has the right to consult with a lawyer and to have the lawyer with him during interrogation.",
                "headnotes": ["Fifth Amendment", "Self-Incrimination", "Miranda Rights"],
                "topics": ["Criminal Procedure", "Constitutional Law", "Police Procedures"],
                "citation_status": "green",
                "authority_score": 0.95,
                "citing_count": 1,
                "cited_by_count": 18500
            },
            {
                "id": "case_004",
                "title": "Roe v. Wade",
                "citation": "410 U.S. 113",
                "court": "Supreme Court of the United States",
                "court_level": "supreme",
                "date_decided": "1973-01-22",
                "jurisdiction": "federal",
                "full_text": "The Constitution does not explicitly mention any right of privacy. However, the Court has recognized that a right of personal privacy does exist under the Constitution. This right of privacy is broad enough to encompass a woman's decision whether or not to terminate her pregnancy.",
                "headnotes": ["Privacy Rights", "Due Process", "Reproductive Rights"],
                "topics": ["Constitutional Law", "Privacy", "Healthcare Law"],
                "citation_status": "red",
                "authority_score": 0.45,
                "citing_count": 2,
                "cited_by_count": 12000
            },
            {
                "id": "case_005",
                "title": "Dobbs v. Jackson Women's Health Organization",
                "citation": "597 U.S. ___",
                "court": "Supreme Court of the United States",
                "court_level": "supreme",
                "date_decided": "2022-06-24",
                "jurisdiction": "federal",
                "full_text": "We hold that Roe and Casey must be overruled. The Constitution makes no reference to abortion, and no such right is implicitly protected by any constitutional provision. Roe was egregiously wrong from the start. Its reasoning was exceptionally weak, and the decision has had damaging consequences.",
                "headnotes": ["Abortion", "Stare Decisis", "Constitutional Interpretation"],
                "topics": ["Constitutional Law", "Healthcare Law", "Federalism"],
                "citation_status": "green",
                "authority_score": 0.85,
                "citing_count": 1,
                "cited_by_count": 850
            },
            {
                "id": "case_006",
                "title": "Gideon v. Wainwright",
                "citation": "372 U.S. 335",
                "court": "Supreme Court of the United States",
                "court_level": "supreme",
                "date_decided": "1963-03-18",
                "jurisdiction": "federal",
                "full_text": "The right of one charged with crime to counsel may not be deemed fundamental and essential to fair trials in some countries, but it is in ours. Reason and reflection require us to recognize that in our adversary system of criminal justice, any person haled into court, who is too poor to hire a lawyer, cannot be assured a fair trial unless counsel is provided for him.",
                "headnotes": ["Right to Counsel", "Sixth Amendment", "Indigent Defense"],
                "topics": ["Criminal Procedure", "Constitutional Law", "Public Defense"],
                "citation_status": "green",
                "authority_score": 0.92,
                "citing_count": 0,
                "cited_by_count": 8500
            },
            {
                "id": "case_007",
                "title": "New York Times Co. v. Sullivan",
                "citation": "376 U.S. 254",
                "court": "Supreme Court of the United States",
                "court_level": "supreme",
                "date_decided": "1964-03-09",
                "jurisdiction": "federal",
                "full_text": "The constitutional guarantees require a federal rule that prohibits a public official from recovering damages for a defamatory falsehood relating to his official conduct unless he proves that the statement was made with 'actual malice' - that is, with knowledge that it was false or with reckless disregard of whether it was false or not.",
                "headnotes": ["First Amendment", "Defamation", "Actual Malice Standard"],
                "topics": ["Constitutional Law", "Media Law", "First Amendment"],
                "citation_status": "green",
                "authority_score": 0.94,
                "citing_count": 0,
                "cited_by_count": 9200
            },
            {
                "id": "case_008",
                "title": "Chevron U.S.A. Inc. v. Natural Resources Defense Council",
                "citation": "467 U.S. 837",
                "court": "Supreme Court of the United States",
                "court_level": "supreme",
                "date_decided": "1984-06-25",
                "jurisdiction": "federal",
                "full_text": "When a court reviews an agency's construction of the statute which it administers, if the intent of Congress is clear, that is the end of the matter. However, if the statute is silent or ambiguous with respect to the specific issue, the question for the court is whether the agency's answer is based on a permissible construction of the statute.",
                "headnotes": ["Administrative Deference", "Statutory Interpretation", "Agency Authority"],
                "topics": ["Administrative Law", "Environmental Law", "Regulatory Law"],
                "citation_status": "red",
                "authority_score": 0.40,
                "citing_count": 0,
                "cited_by_count": 18000
            },
            {
                "id": "case_009",
                "title": "Loper Bright Enterprises v. Raimondo",
                "citation": "603 U.S. ___",
                "court": "Supreme Court of the United States",
                "court_level": "supreme",
                "date_decided": "2024-06-28",
                "jurisdiction": "federal",
                "full_text": "Chevron is overruled. Courts must exercise their independent judgment in deciding whether an agency has acted within its statutory authority. The APA requires courts to determine the meaning of statutory provisions and to set aside agency action that is contrary to law.",
                "headnotes": ["Chevron Overruled", "Judicial Independence", "Agency Deference"],
                "topics": ["Administrative Law", "Regulatory Law", "Separation of Powers"],
                "citation_status": "green",
                "authority_score": 0.88,
                "citing_count": 1,
                "cited_by_count": 120
            },
            {
                "id": "case_010",
                "title": "Citizens United v. Federal Election Commission",
                "citation": "558 U.S. 310",
                "court": "Supreme Court of the United States",
                "court_level": "supreme",
                "date_decided": "2010-01-21",
                "jurisdiction": "federal",
                "full_text": "Political speech does not lose First Amendment protection simply because its source is a corporation. The Government may regulate corporate political speech through disclaimer and disclosure requirements, but it may not suppress that speech altogether.",
                "headnotes": ["Campaign Finance", "Corporate Speech", "First Amendment"],
                "topics": ["Constitutional Law", "Election Law", "First Amendment"],
                "citation_status": "yellow",
                "authority_score": 0.78,
                "citing_count": 0,
                "cited_by_count": 4500
            },
            {
                "id": "case_011",
                "title": "Obergefell v. Hodges",
                "citation": "576 U.S. 644",
                "court": "Supreme Court of the United States",
                "court_level": "supreme",
                "date_decided": "2015-06-26",
                "jurisdiction": "federal",
                "full_text": "The right to marry is a fundamental right inherent in the liberty of the person, and under the Due Process and Equal Protection Clauses of the Fourteenth Amendment couples of the same sex may not be deprived of that right and that liberty.",
                "headnotes": ["Same-Sex Marriage", "Equal Protection", "Due Process"],
                "topics": ["Constitutional Law", "Family Law", "Civil Rights"],
                "citation_status": "green",
                "authority_score": 0.89,
                "citing_count": 0,
                "cited_by_count": 2800
            },
            {
                "id": "case_012",
                "title": "Terry v. Ohio",
                "citation": "392 U.S. 1",
                "court": "Supreme Court of the United States",
                "court_level": "supreme",
                "date_decided": "1968-06-10",
                "jurisdiction": "federal",
                "full_text": "Where a police officer observes unusual conduct which leads him reasonably to conclude that criminal activity may be afoot, the officer may briefly stop the suspicious person and make reasonable inquiries aimed at confirming or dispelling his suspicions.",
                "headnotes": ["Stop and Frisk", "Fourth Amendment", "Reasonable Suspicion"],
                "topics": ["Criminal Procedure", "Constitutional Law", "Police Powers"],
                "citation_status": "green",
                "authority_score": 0.91,
                "citing_count": 0,
                "cited_by_count": 12000
            }
        ]
        
        for case in sample_cases:
            self.cases[case["id"]] = case
        
        # Add sample citations
        self.citations = [
            {"source_id": "case_003", "target_id": "case_002", "type": "cites", "sentiment": "positive"},
            {"source_id": "case_004", "target_id": "case_002", "type": "cites", "sentiment": "positive"},
            {"source_id": "case_004", "target_id": "case_003", "type": "cites", "sentiment": "neutral"},
            {"source_id": "case_005", "target_id": "case_004", "type": "overrules", "sentiment": "negative"},
            {"source_id": "case_009", "target_id": "case_008", "type": "overrules", "sentiment": "negative"},
        ]
    
    def get_case(self, case_id: str) -> Optional[dict]:
        return self.cases.get(case_id)
    
    def get_all_cases(self) -> List[dict]:
        return list(self.cases.values())
    
    def search_cases(self, query: str) -> List[dict]:
        query_lower = query.lower()
        results = []
        for case in self.cases.values():
            score = 0
            if query_lower in case["title"].lower():
                score += 10
            if query_lower in case["full_text"].lower():
                score += 5
            if any(query_lower in topic.lower() for topic in case.get("topics", [])):
                score += 3
            if score > 0:
                results.append({**case, "relevance_score": score})
        return sorted(results, key=lambda x: x["relevance_score"], reverse=True)
    
    def get_citations_for_case(self, case_id: str) -> dict:
        citing = [c for c in self.citations if c["source_id"] == case_id]
        cited_by = [c for c in self.citations if c["target_id"] == case_id]
        return {"citing": citing, "cited_by": cited_by}


# Global database instance
db = InMemoryDB()


def get_db() -> InMemoryDB:
    """Get database instance"""
    return db
