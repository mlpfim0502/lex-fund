"""
Fund Formation Checklist API Router - REVISED
Comprehensive hedge fund formation checklist with timelines, dependencies, and templates
"""
from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from enum import Enum

router = APIRouter(prefix="/api/checklist", tags=["Fund Formation"])


class ChecklistCategory(str, Enum):
    PREPARATION = "preparation"
    INCUBATOR = "incubator"  # New: Incubator fund path
    LEGAL_ENTITY = "legal_entity"
    DOCUMENTS = "documents"
    COMPLIANCE = "compliance"
    SERVICE_PROVIDERS = "service_providers"
    REGULATORY = "regulatory"
    TQQQ_STRATEGY = "tqqq_strategy"


class ChecklistItemStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"


class ChecklistItem(BaseModel):
    id: str
    category: ChecklistCategory
    title: str
    description: str
    status: ChecklistItemStatus = ChecklistItemStatus.NOT_STARTED
    priority: int = 1  # 1=critical, 2=important, 3=optional
    estimated_cost: Optional[str] = None
    week_start: int = 1  # Week to start (1-12)
    week_end: int = 2    # Target completion week
    dependencies: List[str] = []  # Item IDs that must complete first
    template_url: Optional[str] = None  # Link to sample document
    regulatory_reference: Optional[str] = None  # SEC/FINRA rule
    regulatory_reference_url: Optional[str] = None  # Link to official regulatory source
    due_date: Optional[str] = None
    notes: Optional[str] = None
    completed_at: Optional[str] = None
    resources: List[str] = []


class ChecklistUpdate(BaseModel):
    status: Optional[ChecklistItemStatus] = None
    notes: Optional[str] = None
    due_date: Optional[str] = None


# ============================================================================
# COMPREHENSIVE CHECKLIST - 45+ Items Across 7 Categories
# ============================================================================

DEFAULT_CHECKLIST: List[ChecklistItem] = [
    # =========================================================================
    # PHASE 1: PREPARATION (Week 1-2)
    # =========================================================================
    ChecklistItem(
        id="prep-1",
        category=ChecklistCategory.PREPARATION,
        title="Define Investment Strategy & Thesis",
        description="Document your TQQQ/leveraged ETF strategy, target returns, risk parameters, and edge",
        priority=1,
        week_start=1, week_end=1,
        notes="Include: entry/exit rules, position sizing, max drawdown tolerance, correlation analysis",
        template_url="/docs/templates/investment_strategy.md",
        resources=["SEC Investor Bulletin: Hedge Funds: https://www.sec.gov/investor/pubs/hedgefunds.htm"]
    ),
    ChecklistItem(
        id="prep-2",
        category=ChecklistCategory.PREPARATION,
        title="Determine Fee Structure",
        description="Decide management fee (typically 1.5-2%) and performance fee (15-20%)",
        priority=1,
        week_start=1, week_end=1,
        notes="Consider: hurdle rate (e.g., T-bill + 2%), high-water mark, crystallization frequency (annual/quarterly)",
        template_url="/docs/templates/fee_structure.md",
        regulatory_reference="Advisers Act Section 205",
        regulatory_reference_url="https://www.law.cornell.edu/uscode/text/15/80b-5",
        resources=["SEC Rule 205-3 (Qualified Clients): https://www.ecfr.gov/current/title-17/chapter-II/part-275/section-275.205-3"]
    ),
    ChecklistItem(
        id="prep-3",
        category=ChecklistCategory.PREPARATION,
        title="Budget Formation Costs",
        description="Plan for $50K-$150K formation costs plus ongoing expenses",
        priority=1,
        week_start=1, week_end=1,
        estimated_cost="Planning only",
        template_url="/docs/fund_formation_roadmap.md",
        resources=["Hedge Fund Formation Cost Guide: https://www.hedgefundlawblog.com"]
    ),
    ChecklistItem(
        id="prep-4",
        category=ChecklistCategory.PREPARATION,
        title="Identify Target Investors",
        description="Define investor profile: accredited individuals, family offices, institutions",
        priority=2,
        week_start=1, week_end=2,
        notes="Determines 506(b) vs 506(c), minimum investment, marketing approach",
        regulatory_reference="Rule 501 Regulation D",
        regulatory_reference_url="https://www.ecfr.gov/current/title-17/chapter-II/part-230/section-230.501",
        resources=["SEC Accredited Investor Definition: https://www.sec.gov/education/capitalraising/building-blocks/accredited-investor"]
    ),
    ChecklistItem(
        id="prep-5",
        category=ChecklistCategory.PREPARATION,
        title="Engage Fund Formation Attorney",
        description="CRITICAL FIRST STEP: Hire specialist hedge fund lawyer before any entity formation",
        priority=1,
        week_start=1, week_end=2,
        estimated_cost="$50,000-$100,000 (full formation)",
        resources=[
            "Seward & Kissel LLP",
            "Sadis & Goldberg LLP", 
            "Cole-Frieman & Mallon LLP",
            "Schulte Roth & Zabel LLP"
        ],
        notes="Get fixed-fee quote for full formation package"
    ),

    # =========================================================================
    # PHASE 2: LEGAL ENTITY FORMATION (Week 2-4)
    # =========================================================================
    ChecklistItem(
        id="le-1",
        category=ChecklistCategory.LEGAL_ENTITY,
        title="Appoint Delaware Registered Agent",
        description="Required for all Delaware entities - receives legal service of process",
        priority=1,
        week_start=2, week_end=2,
        estimated_cost="$100-$300/year",
        dependencies=["prep-5"],
        regulatory_reference="Delaware Code 6 Del. C. § 18-104",
        regulatory_reference_url="https://delcode.delaware.gov/title6/c018/sc01/index.html",
        template_url="/docs/templates/delaware_llc_formation.md",
        resources=["Corporation Service Company (CSC): https://www.cscglobal.com", "CT Corporation: https://www.wolterskluwer.com/en/solutions/ct-corporation", "Harvard Business Services: https://www.delawareinc.com"]
    ),
    ChecklistItem(
        id="le-2",
        category=ChecklistCategory.LEGAL_ENTITY,
        title="Form Management Company LLC",
        description="Delaware LLC serving as registered investment adviser (RIA). Collects management fees",
        priority=1,
        week_start=2, week_end=3,
        estimated_cost="$500-$1,500",
        dependencies=["le-1", "prep-5"],
        resources=["Delaware Division of Corporations: https://corp.delaware.gov"],
        template_url="/docs/templates/llc_operating_agreement.md",
        regulatory_reference="Delaware Code 6 Del. C. § 18-201",
        regulatory_reference_url="https://delcode.delaware.gov/title6/c018/sc02/index.html"
    ),
    ChecklistItem(
        id="le-3",
        category=ChecklistCategory.LEGAL_ENTITY,
        title="Draft Management Company Operating Agreement",
        description="Defines ownership, management structure, profit distribution of the adviser",
        priority=1,
        week_start=2, week_end=3,
        estimated_cost="Included in attorney fees",
        dependencies=["le-2"],
        template_url="/docs/templates/llc_operating_agreement.md"
    ),
    ChecklistItem(
        id="le-4",
        category=ChecklistCategory.LEGAL_ENTITY,
        title="Form General Partner LLC",
        description="Delaware LLC that controls the Fund LP. Has unlimited liability for fund obligations",
        priority=1,
        week_start=2, week_end=3,
        estimated_cost="$500-$1,500",
        dependencies=["le-1", "prep-5"],
        regulatory_reference="Delaware Code 6 Del. C. § 18-201",
        regulatory_reference_url="https://delcode.delaware.gov/title6/c018/sc02/index.html",
        template_url="/docs/templates/delaware_llc_formation.md",
        resources=["Delaware Division of Corporations: https://corp.delaware.gov"]
    ),
    ChecklistItem(
        id="le-5",
        category=ChecklistCategory.LEGAL_ENTITY,
        title="Draft GP Operating Agreement",
        description="Defines GP authority, indemnification, capital contributions",
        priority=1,
        week_start=2, week_end=3,
        estimated_cost="Included in attorney fees",
        dependencies=["le-4"],
        template_url="/docs/templates/llc_operating_agreement.md"
    ),
    ChecklistItem(
        id="le-6",
        category=ChecklistCategory.LEGAL_ENTITY,
        title="Form Fund LP (Limited Partnership)",
        description="Main investment vehicle - Delaware LP that holds investor capital and trades TQQQ",
        priority=1,
        week_start=3, week_end=4,
        estimated_cost="$1,000-$2,000",
        dependencies=["le-4"],
        resources=["Delaware Division of Corporations: https://corp.delaware.gov"],
        regulatory_reference="Delaware Code Title 6, Chapter 17",
        regulatory_reference_url="https://delcode.delaware.gov/title6/c017/index.html"
    ),
    ChecklistItem(
        id="le-7",
        category=ChecklistCategory.LEGAL_ENTITY,
        title="Obtain EINs for All Entities",
        description="Federal Employer Identification Numbers from IRS (3 EINs needed)",
        priority=1,
        week_start=3, week_end=4,
        estimated_cost="Free",
        dependencies=["le-2", "le-4", "le-6"],
        resources=["IRS EIN Online: https://www.irs.gov/ein"],
        regulatory_reference="IRS Form SS-4",
        regulatory_reference_url="https://www.irs.gov/forms-pubs/about-form-ss-4"
    ),
    ChecklistItem(
        id="le-8",
        category=ChecklistCategory.LEGAL_ENTITY,
        title="Open Business Bank Accounts",
        description="Separate accounts for Management Co (operating) and Fund LP (trading)",
        priority=2,
        week_start=4, week_end=5,
        estimated_cost="Varies",
        dependencies=["le-7"],
        notes="Consider: Silicon Valley Bank, First Republic, Signature Bank (for funds)",
        resources=["Mercury Bank (startup-friendly): https://mercury.com", "First Republic: https://www.firstrepublic.com"]
    ),
    ChecklistItem(
        id="le-9",
        category=ChecklistCategory.LEGAL_ENTITY,
        title="Foreign Qualification (If Needed)",
        description="Register entities in states where you have physical presence",
        priority=3,
        week_start=4, week_end=5,
        estimated_cost="$200-$500/state",
        dependencies=["le-6"],
        resources=["State-by-State Guide: https://www.nass.org/business-services/corporations"]
    ),

    # =========================================================================
    # PHASE 3: LEGAL DOCUMENTS (Week 4-8)
    # =========================================================================
    ChecklistItem(
        id="doc-1",
        category=ChecklistCategory.DOCUMENTS,
        title="Draft Private Placement Memorandum (PPM)",
        description="Primary disclosure document: strategy, risks, fees, manager background. MUST include TQQQ Appendix",
        priority=1,
        week_start=4, week_end=7,
        estimated_cost="$15,000-$50,000",
        dependencies=["prep-1", "prep-2", "le-6"],
        regulatory_reference="Securities Act Section 4(a)(2), Rule 506",
        regulatory_reference_url="https://www.ecfr.gov/current/title-17/chapter-II/part-230/section-230.506",
        template_url="/docs/fund_formation_roadmap.md",
        notes="See TQQQ Strategy section for required leveraged ETF disclosures"
    ),
    ChecklistItem(
        id="doc-2",
        category=ChecklistCategory.DOCUMENTS,
        title="Draft Limited Partnership Agreement (LPA)",
        description="Governs fund operations: GP authority, LP rights, allocations, withdrawals, side pockets",
        priority=1,
        week_start=4, week_end=7,
        estimated_cost="$10,000-$25,000",
        dependencies=["le-6"],
        template_url="/docs/templates/llc_operating_agreement.md"
    ),
    ChecklistItem(
        id="doc-3",
        category=ChecklistCategory.DOCUMENTS,
        title="Draft Subscription Agreement",
        description="Investor capital commitment with accredited investor representations and warranties",
        priority=1,
        week_start=5, week_end=7,
        estimated_cost="$5,000-$10,000",
        dependencies=["doc-1"],
        regulatory_reference="Rule 501 Regulation D",
        regulatory_reference_url="https://www.ecfr.gov/current/title-17/chapter-II/part-230/section-230.501",
        template_url="/docs/templates/subscription_agreement.md"
    ),
    ChecklistItem(
        id="doc-4",
        category=ChecklistCategory.DOCUMENTS,
        title="Create Investor Questionnaire",
        description="Collect investor info, verify accredited/QP status, perform AML/KYC",
        priority=1,
        week_start=5, week_end=7,
        estimated_cost="$1,000-$3,000",
        dependencies=["doc-3"],
        template_url="/docs/templates/aml_kyc_program.md"
    ),
    ChecklistItem(
        id="doc-5",
        category=ChecklistCategory.DOCUMENTS,
        title="Draft Investment Management Agreement (IMA)",
        description="Contract between Fund LP and Management Co defining advisory services and fees",
        priority=1,
        week_start=5, week_end=7,
        estimated_cost="$5,000-$10,000",
        dependencies=["le-2", "le-6"],
        template_url="/docs/templates/fee_structure.md"
    ),
    ChecklistItem(
        id="doc-6",
        category=ChecklistCategory.DOCUMENTS,
        title="Prepare Side Letter Template",
        description="Negotiated terms for large/institutional investors (fee discounts, liquidity, MFN)",
        priority=2,
        week_start=6, week_end=8,
        estimated_cost="$2,000-$5,000",
        dependencies=["doc-2"],
        template_url="/docs/templates/subscription_agreement.md",
        notes="Common provisions: reduced fees, enhanced liquidity, co-invest rights"
    ),
    ChecklistItem(
        id="doc-7",
        category=ChecklistCategory.DOCUMENTS,
        title="Draft Form ADV Part 2A (Brochure)",
        description="If RIA registered: plain-English brochure describing services, fees, conflicts",
        priority=2,
        week_start=6, week_end=8,
        estimated_cost="Included in Form ADV filing",
        dependencies=["reg-2"],
        regulatory_reference="Investment Advisers Act Rule 204-3",
        regulatory_reference_url="https://www.ecfr.gov/current/title-17/chapter-II/part-275/section-275.204-3",
        resources=["SEC Form ADV: https://www.sec.gov/about/forms/formadv.pdf"]
    ),

    # =========================================================================
    # PHASE 4: COMPLIANCE (Week 5-8)
    # =========================================================================
    ChecklistItem(
        id="comp-1",
        category=ChecklistCategory.COMPLIANCE,
        title="Develop Compliance Manual",
        description="Written supervisory procedures covering all regulatory requirements",
        priority=1,
        week_start=5, week_end=8,
        estimated_cost="$5,000-$15,000",
        dependencies=["prep-5"],
        regulatory_reference="Advisers Act Rule 206(4)-7",
        regulatory_reference_url="https://www.ecfr.gov/current/title-17/chapter-II/part-275/section-275.206(4)-7",
        template_url="/docs/templates/compliance_manual_toc.md"
    ),
    ChecklistItem(
        id="comp-2",
        category=ChecklistCategory.COMPLIANCE,
        title="Create Code of Ethics",
        description="Personal trading policy, pre-clearance requirements, restricted lists",
        priority=1,
        week_start=5, week_end=8,
        estimated_cost="Included in compliance manual",
        dependencies=["comp-1"],
        regulatory_reference="Advisers Act Rule 204A-1",
        regulatory_reference_url="https://www.ecfr.gov/current/title-17/chapter-II/part-275/section-275.204A-1",
        template_url="/docs/templates/compliance_manual_toc.md"
    ),
    ChecklistItem(
        id="comp-3",
        category=ChecklistCategory.COMPLIANCE,
        title="Establish AML/KYC Program",
        description="Anti-money laundering policies, customer identification procedures",
        priority=1,
        week_start=5, week_end=8,
        dependencies=["comp-1"],
        regulatory_reference="Bank Secrecy Act, FinCEN CDD Rule 31 CFR § 1010.230",
        regulatory_reference_url="https://www.ecfr.gov/current/title-31/subtitle-B/chapter-X/part-1010/subpart-B/section-1010.230",
        template_url="/docs/templates/aml_kyc_program.md",
        resources=["FinCEN: https://www.fincen.gov", "OFAC SDN List: https://sanctionssearch.ofac.treas.gov/"]
    ),
    ChecklistItem(
        id="comp-4",
        category=ChecklistCategory.COMPLIANCE,
        title="Create Cybersecurity Policy",
        description="SEC-required: data protection, incident response, vendor management",
        priority=1,
        week_start=6, week_end=8,
        estimated_cost="$2,000-$5,000",
        dependencies=["comp-1"],
        regulatory_reference="SEC Cybersecurity Risk Alert (2023)",
        regulatory_reference_url="https://www.sec.gov/investment/im-info-2023-cybersecurity",
        template_url="/docs/templates/compliance_manual_toc.md"
    ),
    ChecklistItem(
        id="comp-5",
        category=ChecklistCategory.COMPLIANCE,
        title="Develop Business Continuity Plan (BCP)",
        description="Disaster recovery, backup systems, key person contingency",
        priority=1,
        week_start=6, week_end=8,
        estimated_cost="$1,000-$3,000",
        dependencies=["comp-1"],
        regulatory_reference="Advisers Act Rule 206(4)-4",
        regulatory_reference_url="https://www.ecfr.gov/current/title-17/chapter-II/part-275/section-275.206(4)-4",
        template_url="/docs/templates/compliance_manual_toc.md"
    ),
    ChecklistItem(
        id="comp-6",
        category=ChecklistCategory.COMPLIANCE,
        title="Create Valuation Policy",
        description="NAV calculation methodology - especially for leveraged ETF positions",
        priority=1,
        week_start=6, week_end=8,
        dependencies=["comp-1"],
        notes="Document TQQQ valuation during market disruptions, halts, extreme volatility",
        regulatory_reference="SEC Rule 2a-5",
        regulatory_reference_url="https://www.sec.gov/rules/final/2020/ic-34128.pdf",
        template_url="/docs/templates/valuation_policy.md",
        resources=["SEC Valuation Rule: https://www.sec.gov/rules/final/2020/ic-34128.pdf"]
    ),
    ChecklistItem(
        id="comp-7",
        category=ChecklistCategory.COMPLIANCE,
        title="Establish Error Correction Policy",
        description="Procedures for identifying and correcting trade errors, NAV errors",
        priority=2,
        week_start=7, week_end=8,
        dependencies=["comp-1"],
        template_url="/docs/templates/compliance_manual_toc.md"
    ),
    ChecklistItem(
        id="comp-8",
        category=ChecklistCategory.COMPLIANCE,
        title="Designate Chief Compliance Officer (CCO)",
        description="Individual responsible for compliance oversight - can be founder initially",
        priority=1,
        week_start=5, week_end=6,
        estimated_cost="$0 (if founder) or $100K+ (external)",
        dependencies=["prep-5"],
        regulatory_reference="Advisers Act Rule 206(4)-7(c)",
        regulatory_reference_url="https://www.ecfr.gov/current/title-17/chapter-II/part-275/section-275.206(4)-7",
        resources=["SEC CCO Guidance: https://www.sec.gov/about/offices/ocie/ocieccoletter.htm"]
    ),

    # =========================================================================
    # PHASE 5: SERVICE PROVIDERS (Week 3-8)
    # =========================================================================
    ChecklistItem(
        id="sp-1",
        category=ChecklistCategory.SERVICE_PROVIDERS,
        title="Select Prime Broker / Custodian",
        description="Qualified custodian to hold fund assets. Must support leveraged ETF trading",
        priority=1,
        week_start=3, week_end=6,
        estimated_cost="Account minimums vary",
        dependencies=["le-6"],
        resources=[
            "Interactive Brokers (best for <$50M): https://www.interactivebrokers.com",
            "TD Ameritrade Institutional",
            "Pershing (BNY Mellon)"
        ],
        notes="Confirm TQQQ margin requirements and position limits with broker",
        regulatory_reference="SEC Custody Rule",
        regulatory_reference_url="https://www.ecfr.gov/current/title-17/chapter-II/part-275/section-275.206(4)-2"
    ),
    ChecklistItem(
        id="sp-2",
        category=ChecklistCategory.SERVICE_PROVIDERS,
        title="Engage Fund Auditor",
        description="Annual audit required for Form ADV. Select auditor experienced with hedge funds",
        priority=2,
        week_start=5, week_end=8,
        estimated_cost="$15,000-$30,000/year",
        dependencies=["le-6"],
        resources=["EisnerAmper", "Citrin Cooperman", "Anchin", "WithumSmith+Brown"],
        regulatory_reference="SEC Custody Rule - Surprise Exam",
        regulatory_reference_url="https://www.sec.gov/divisions/investment/custody_faq_030510.htm"
    ),
    ChecklistItem(
        id="sp-3",
        category=ChecklistCategory.SERVICE_PROVIDERS,
        title="Consider Fund Administrator",
        description="Third-party for NAV calculation, investor reporting. Optional but adds credibility",
        priority=3,
        week_start=5, week_end=8,
        estimated_cost="$2,000-$5,000/month",
        dependencies=["le-6"],
        resources=["NAV Consulting: https://navconsulting.net", "Opus Fund Services: https://opusfundservices.com", "Theorem Fund Services"]
    ),
    ChecklistItem(
        id="sp-4",
        category=ChecklistCategory.SERVICE_PROVIDERS,
        title="Engage Tax Counsel",
        description="K-1 preparation, partnership tax matters, offshore structure advice (if applicable)",
        priority=2,
        week_start=5, week_end=8,
        estimated_cost="$5,000-$15,000/year",
        dependencies=["le-6"],
        resources=["IRS Partnership Tax Forms: https://www.irs.gov/forms-pubs/about-schedule-k-1-form-1065", "Partnership Taxation Guide: https://www.irs.gov/businesses/partnerships"]
    ),
    ChecklistItem(
        id="sp-5",
        category=ChecklistCategory.SERVICE_PROVIDERS,
        title="Obtain E&O / Professional Liability Insurance",
        description="Covers claims of negligence, errors in investment advice",
        priority=1,
        week_start=6, week_end=8,
        estimated_cost="$5,000-$15,000/year",
        dependencies=["le-2"],
        notes="$1M-$5M coverage typical for emerging managers",
        resources=["AIMA Insurance Guide: https://www.aima.org", "Marsh McLennan: https://www.marsh.com"]
    ),
    ChecklistItem(
        id="sp-6",
        category=ChecklistCategory.SERVICE_PROVIDERS,
        title="Obtain D&O Insurance",
        description="Directors and Officers liability - protects GP members personally",
        priority=2,
        week_start=6, week_end=8,
        estimated_cost="$3,000-$10,000/year",
        dependencies=["le-4"],
        resources=["Chubb D&O: https://www.chubb.com", "AIG D&O: https://www.aig.com"]
    ),
    ChecklistItem(
        id="sp-7",
        category=ChecklistCategory.SERVICE_PROVIDERS,
        title="Fidelity Bond (If Registered)",
        description="Required for SEC-registered advisers with ERISA clients",
        priority=2,
        week_start=7, week_end=9,
        estimated_cost="$1,000-$3,000/year",
        dependencies=["reg-2"],
        regulatory_reference="ERISA Section 412",
        regulatory_reference_url="https://www.law.cornell.edu/uscode/text/29/1112",
        resources=["DOL Fidelity Bonding: https://www.dol.gov/agencies/ebsa/about-ebsa/our-activities/resource-center/faqs/fidelity-bonding"]
    ),

    # =========================================================================
    # PHASE 6: REGULATORY FILINGS (Week 8-10) - LAST PHASE
    # =========================================================================
    ChecklistItem(
        id="reg-1",
        category=ChecklistCategory.REGULATORY,
        title="Determine Registration Requirement",
        description="Assess SEC RIA, State RIA, or Exempt Reporting Adviser (ERA) based on AUM",
        priority=1,
        week_start=2, week_end=4,
        dependencies=["prep-3"],
        resources=["SEC Registration Guide: https://www.sec.gov/divisions/investment/iaregulation/memoia.htm"],
        notes="<$100M: State or ERA | $100M-$150M: State or SEC | >$150M: SEC required"
    ),
    ChecklistItem(
        id="reg-2",
        category=ChecklistCategory.REGULATORY,
        title="File Form ADV (Parts 1, 2A, 2B)",
        description="Investment adviser registration via IARD. Part 2A is the client brochure",
        priority=1,
        week_start=8, week_end=10,
        estimated_cost="$5,000-$15,000 (legal fees) + $225 IARD fee",
        dependencies=["le-2", "comp-1"],
        regulatory_reference="Advisers Act Section 203",
        regulatory_reference_url="https://www.law.cornell.edu/uscode/text/15/80b-3",
        resources=["IARD System: https://www.iard.com"]
    ),
    ChecklistItem(
        id="reg-3",
        category=ChecklistCategory.REGULATORY,
        title="File Form D with SEC (Within 15 Days of First Sale)",
        description="Notice filing for Regulation D private placement - 506(b) or 506(c)",
        priority=1,
        week_start=10, week_end=10,
        estimated_cost="Free",
        dependencies=["doc-1", "doc-3"],
        regulatory_reference="Rules 503, 506 of Regulation D",
        regulatory_reference_url="https://www.ecfr.gov/current/title-17/chapter-II/part-230/section-230.506",
        resources=["SEC EDGAR Form D: https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&type=D"],
        notes="IMPORTANT: File within 15 days of first investor subscription"
    ),
    ChecklistItem(
        id="reg-4",
        category=ChecklistCategory.REGULATORY,
        title="State Blue Sky Filings",
        description="Notice filings in states where investors reside (varies by state)",
        priority=2,
        week_start=10, week_end=11,
        estimated_cost="$100-$500 per state",
        dependencies=["reg-3"],
        notes="Some states accept Rule 506 federal preemption; others require notice",
        regulatory_reference="NSMIA, State Securities Laws",
        regulatory_reference_url="https://www.sec.gov/answers/bluesky.htm",
        resources=["NASAA Blue Sky Requirements: https://www.nasaa.org", "State-by-State Requirements: https://www.sec.gov/answers/bluesky.htm"]
    ),
    ChecklistItem(
        id="reg-5",
        category=ChecklistCategory.REGULATORY,
        title="Form PF (If Applicable)",
        description="Required for SEC-registered advisers with >$150M in private fund AUM",
        priority=2,
        week_start=11, week_end=12,
        estimated_cost="$3,000-$8,000 (legal fees)",
        dependencies=["reg-2"],
        regulatory_reference="Advisers Act Rule 204(b)-1",
        regulatory_reference_url="https://www.ecfr.gov/current/title-17/chapter-II/part-275/section-275.204(b)-1",
        notes="Filed quarterly (large advisers) or annually (smaller advisers)"
    ),
    ChecklistItem(
        id="reg-6",
        category=ChecklistCategory.REGULATORY,
        title="NFA/CFTC Registration (If Trading Futures/Swaps)",
        description="Required if strategy includes commodity interests beyond de minimis exemption",
        priority=3,
        week_start=8, week_end=10,
        estimated_cost="$5,000-$15,000",
        dependencies=["le-2"],
        regulatory_reference="Commodity Exchange Act",
        regulatory_reference_url="https://www.law.cornell.edu/uscode/text/7/chapter-1",
        resources=["NFA Registration: https://www.nfa.futures.org"],
        notes="Pure TQQQ ETF strategy may qualify for exemption - consult attorney"
    ),

    # =========================================================================
    # PHASE 7: TQQQ STRATEGY REQUIREMENTS (Throughout)
    # =========================================================================
    ChecklistItem(
        id="tqqq-1",
        category=ChecklistCategory.TQQQ_STRATEGY,
        title="Draft Volatility Decay Disclosure",
        description="REQUIRED: Explain that 3x leverage applies DAILY, not over longer periods",
        priority=1,
        week_start=4, week_end=7,
        dependencies=["doc-1"],
        regulatory_reference="FINRA Notice 09-31",
        regulatory_reference_url="https://www.finra.org/rules-guidance/notices/09-31",
        template_url="/docs/templates/volatility_decay_disclosure.md",
        notes="Include numerical example: if QQQ +10% then -10%, TQQQ loses ~2.25%, not 0%"
    ),
    ChecklistItem(
        id="tqqq-2",
        category=ChecklistCategory.TQQQ_STRATEGY,
        title="Include FINRA 09-31 Suitability Warning",
        description="Verbatim or summary of FINRA guidance on leveraged ETF suitability",
        priority=1,
        week_start=4, week_end=7,
        dependencies=["doc-1"],
        regulatory_reference="FINRA Regulatory Notice 09-31",
        regulatory_reference_url="https://www.finra.org/rules-guidance/notices/09-31",
        resources=["FINRA 09-31: https://www.finra.org/rules-guidance/notices/09-31"]
    ),
    ChecklistItem(
        id="tqqq-3",
        category=ChecklistCategory.TQQQ_STRATEGY,
        title="Add Compounding Risk Section",
        description="Mathematical explanation with tables showing daily vs cumulative returns",
        priority=1,
        week_start=4, week_end=7,
        dependencies=["doc-1"],
        template_url="/docs/templates/volatility_decay_disclosure.md"
    ),
    ChecklistItem(
        id="tqqq-4",
        category=ChecklistCategory.TQQQ_STRATEGY,
        title="Document Position Limit Policy",
        description="Define max allocation to leveraged ETFs (suggested: 40% single, 75% total)",
        priority=1,
        week_start=4, week_end=7,
        dependencies=["prep-1"],
        notes="Include rationale and how limits are monitored",
        template_url="/docs/templates/position_limits_vix_rules.md",
        resources=["FINRA Suitability FAQ: https://www.finra.org/rules-guidance/key-topics/suitability"]
    ),
    ChecklistItem(
        id="tqqq-5",
        category=ChecklistCategory.TQQQ_STRATEGY,
        title="Establish VIX Circuit Breaker Rules",
        description="Automatic risk reduction when VIX exceeds thresholds (e.g., VIX>30: reduce 50%, VIX>40: exit)",
        priority=2,
        week_start=4, week_end=7,
        dependencies=["prep-1"],
        notes="Document in both PPM and internal trading procedures",
        template_url="/docs/templates/position_limits_vix_rules.md",
        resources=["CBOE VIX Index: https://www.cboe.com/tradable_products/vix/"]
    ),
    ChecklistItem(
        id="tqqq-6",
        category=ChecklistCategory.TQQQ_STRATEGY,
        title="Disclose Margin / Leverage Limits",
        description="Document broker margin requirements for TQQQ (typically 75% Reg T)",
        priority=1,
        week_start=5, week_end=7,
        dependencies=["sp-1"],
        notes="Reg T: 75% initial/maintenance. Portfolio margin may allow lower",
        regulatory_reference="Regulation T (12 CFR 220), FINRA Rule 4210",
        regulatory_reference_url="https://www.ecfr.gov/current/title-12/chapter-II/subchapter-A/part-220",
        resources=["Fed Regulation T: https://www.ecfr.gov/current/title-12/chapter-II/subchapter-A/part-220"]
    ),
    ChecklistItem(
        id="tqqq-7",
        category=ChecklistCategory.TQQQ_STRATEGY,
        title="Daily Rebalancing Disclosure",
        description="Explain how ProShares rebalances daily and impact on returns",
        priority=1,
        week_start=4, week_end=7,
        dependencies=["doc-1"],
        resources=["ProShares TQQQ Prospectus: https://www.proshares.com/funds/tqqq.html"]
    ),
    ChecklistItem(
        id="tqqq-8",
        category=ChecklistCategory.TQQQ_STRATEGY,
        title="Counterparty / Swap Risk Disclosure",
        description="Explain that TQQQ uses swaps and carries counterparty exposure",
        priority=2,
        week_start=5, week_end=7,
        dependencies=["doc-1"],
        notes="Reference ProShares prospectus for swap counterparty details",
        resources=["ProShares TQQQ SAI: https://www.proshares.com/funds/tqqq.html", "SEC Swap Data: https://www.sec.gov/swaps"]
    ),
    ChecklistItem(
        id="tqqq-9",
        category=ChecklistCategory.TQQQ_STRATEGY,
        title="Prepare Backtesting Documentation",
        description="Historical analysis showing strategy performance with decay accounted for",
        priority=2,
        week_start=3, week_end=8,
        dependencies=["prep-1"],
        notes="Include: various market regimes, drawdowns, rolling returns, vs buy-and-hold QQQ",
        template_url="/docs/templates/investment_strategy.md",
        resources=["Yahoo Finance Historical Data: https://finance.yahoo.com", "Portfolio Visualizer: https://www.portfoliovisualizer.com"]
    ),

    # =========================================================================
    # PHASE 8: INCUBATOR FUND PATH (Alternative to Full Launch)
    # Cost-effective stepping stone - $2,500-$3,500 vs $50K-$100K
    # Based on Investment Law Group's incubator fund concept
    # =========================================================================
    ChecklistItem(
        id="incub-1",
        category=ChecklistCategory.INCUBATOR,
        title="Evaluate Incubator vs Full Launch",
        description="Decide if incubator path makes sense: build track record with your own capital before full launch",
        priority=1,
        week_start=1, week_end=1,
        estimated_cost="N/A",
        template_url="/docs/templates/incubator_fund_guide.md",
        resources=["Investment Law Group Incubator Guide: https://investmentlawgroup.com"],
        notes="Incubator ideal if: no outside capital yet, want to test strategy, need track record for investors. EXEMPTION STRATEGY: (1) ERA - keep AUM < $150M, (2) De Minimis - < 5 retail clients per state without physical presence, (3) Rule 506(b) - accredited investors only, no general solicitation. Apply conservative 70% factor to projected revenue."
    ),
    ChecklistItem(
        id="incub-2",
        category=ChecklistCategory.INCUBATOR,
        title="Form Incubator Fund LP/LLC",
        description="Form simplified fund entity to hold your trading capital and build track record",
        priority=1,
        week_start=1, week_end=2,
        estimated_cost="$500-$1,000",
        dependencies=["incub-1"],
        regulatory_reference="Delaware Code Title 6",
        regulatory_reference_url="https://delcode.delaware.gov/title6/",
        template_url="/docs/templates/delaware_llc_formation.md",
        resources=["Delaware Division of Corporations: https://corp.delaware.gov"]
    ),
    ChecklistItem(
        id="incub-3",
        category=ChecklistCategory.INCUBATOR,
        title="Form Investment Manager LLC (Optional)",
        description="Form GP/Manager LLC - can use personal capacity initially but LLC recommended",
        priority=2,
        week_start=1, week_end=2,
        estimated_cost="$500-$1,000",
        dependencies=["incub-1"],
        notes="Can serve as GP individually during incubation; form LLC before accepting outside capital",
        template_url="/docs/templates/llc_operating_agreement.md",
        regulatory_reference="Delaware Code 6 Del. C. § 18-201",
        regulatory_reference_url="https://delcode.delaware.gov/title6/c018/sc02/index.html"
    ),
    ChecklistItem(
        id="incub-4",
        category=ChecklistCategory.INCUBATOR,
        title="Engage Incubator Fund Attorney",
        description="Hire attorney to prepare simplified formation documents (~$2,500-$3,500 total)",
        priority=1,
        week_start=1, week_end=2,
        estimated_cost="$2,500-$3,500",
        dependencies=["incub-1"],
        resources=["Investment Law Group: https://investmentlawgroup.com", "Hedge Fund Law Blog: https://hedgefundlawblog.com"],
        template_url="/docs/templates/incubator_fund_guide.md"
    ),
    ChecklistItem(
        id="incub-5",
        category=ChecklistCategory.INCUBATOR,
        title="Open Brokerage Account for Fund",
        description="Open trading account in fund entity name at any broker",
        priority=1,
        week_start=2, week_end=3,
        estimated_cost="Varies",
        dependencies=["incub-2"],
        resources=["Interactive Brokers: https://www.interactivebrokers.com", "TD Ameritrade: https://www.tdameritrade.com"],
        notes="No broker minimum required unless imposed by broker; fund with personal capital",
        regulatory_reference="SEC Custody Rule",
        regulatory_reference_url="https://www.ecfr.gov/current/title-17/chapter-II/part-275/section-275.206(4)-2"
    ),
    ChecklistItem(
        id="incub-6",
        category=ChecklistCategory.INCUBATOR,
        title="Seed Fund with Personal Capital",
        description="Contribute your own capital to begin trading and building track record",
        priority=1,
        week_start=2, week_end=3,
        estimated_cost="Your capital",
        dependencies=["incub-5"],
        notes="No minimum required; consider strategy needs and investor expectations",
        template_url="/docs/templates/incubator_fund_guide.md"
    ),
    ChecklistItem(
        id="incub-6b",
        category=ChecklistCategory.INCUBATOR,
        title="Implement Basic AML/KYC Framework",
        description="Establish customer identification procedures even during incubator phase",
        priority=2,
        week_start=3, week_end=8,
        dependencies=["incub-5"],
        template_url="/docs/templates/aml_kyc_program.md",
        regulatory_reference="Bank Secrecy Act / USA PATRIOT Act",
        regulatory_reference_url="https://www.fincen.gov/resources/statutes-and-regulations/bank-secrecy-act",
        notes="Basic CIP before accepting outside capital: ID verification, source of funds documentation, ongoing monitoring procedures"
    ),
    ChecklistItem(
        id="incub-7",
        category=ChecklistCategory.INCUBATOR,
        title="Execute Strategy & Build Track Record",
        description="Trade per your documented strategy for 3-12 months to create verifiable track record",
        priority=1,
        week_start=3, week_end=52,
        dependencies=["incub-6", "prep-1"],
        notes="Longer track record = more attractive to investors. Aim for 6-12 months minimum",
        template_url="/docs/templates/investment_strategy.md"
    ),
    ChecklistItem(
        id="incub-8",
        category=ChecklistCategory.INCUBATOR,
        title="Calculate & Document Returns (TWR)",
        description="Calculate time-weighted returns monthly; document net of hypothetical fees",
        priority=1,
        week_start=4, week_end=52,
        dependencies=["incub-7"],
        resources=["CFA Institute GIPS Standards: https://www.cfainstitute.org/en/ethics-standards/codes/gips-standards"],
        notes="Use time-weighted returns (TWR), not money-weighted. Account for contributions/withdrawals",
        regulatory_reference="CFA GIPS Standards",
        regulatory_reference_url="https://www.gipsstandards.org/"
    ),
    ChecklistItem(
        id="incub-9",
        category=ChecklistCategory.INCUBATOR,
        title="Develop Marketing Materials",
        description="Create pitch deck, tear sheet, and track record presentation with disclaimers",
        priority=2,
        week_start=8, week_end=24,
        dependencies=["incub-7"],
        template_url="/docs/templates/incubator_fund_guide.md",
        notes="Include required disclaimers about past performance and manager-only capital"
    ),
    ChecklistItem(
        id="incub-9b",
        category=ChecklistCategory.INCUBATOR,
        title="Prepare Due Diligence Questionnaire (DDQ)",
        description="Create institutional DDQ covering investment process, risk management, operations, and compliance",
        priority=2,
        week_start=12, week_end=36,
        dependencies=["incub-8"],
        notes="Institutional LPs require comprehensive DDQ. Cover: investment philosophy, team bios, risk controls, IT security, business continuity, compliance program",
        resources=["AIMA DDQ Template: https://www.aima.org", "ILPA DDQ: https://ilpa.org"]
    ),
    ChecklistItem(
        id="incub-10",
        category=ChecklistCategory.INCUBATOR,
        title="Soft-Circle Investor Interest",
        description="Gather indications of interest from pre-existing relationships (NO general solicitation)",
        priority=2,
        week_start=12, week_end=52,
        dependencies=["incub-8", "incub-9b"],
        regulatory_reference="Rule 506(b) pre-existing relationship",
        regulatory_reference_url="https://www.ecfr.gov/current/title-17/chapter-II/part-230/section-230.506",
        notes="CANNOT: advertise, cold-call, or accept outside capital. CAN: talk to friends, family, colleagues. Consider using prime broker capital introduction services or third-party placement agents when ready"
    ),
    ChecklistItem(
        id="incub-11",
        category=ChecklistCategory.INCUBATOR,
        title="Select Service Providers for Full Launch",
        description="Research and select administrator, auditor, and other service providers for conversion",
        priority=3,
        week_start=20, week_end=52,
        dependencies=["incub-7"],
        resources=["NAV Consulting: https://navconsulting.net", "Opus Fund Services: https://opusfundservices.com"],
        template_url="/docs/templates/incubator_fund_guide.md"
    ),
    ChecklistItem(
        id="incub-12",
        category=ChecklistCategory.INCUBATOR,
        title="Convert to Full Hedge Fund",
        description="When ready: engage full formation attorney, prepare PPM/LPA, engage service providers",
        priority=1,
        week_start=40, week_end=52,
        estimated_cost="$50,000-$100,000",
        dependencies=["incub-7", "incub-10"],
        notes="Convert when: 6+ month track record, soft-circled commitments, ready for full-time fund management. REQUIRED: File Form D within 15 days of first securities sale. Submit Form ADV via IARD as ERA. If AUM > $150M, register with SEC. For non-US investors, consider offshore feeder structure (e.g., Cayman Islands ELP).",
        template_url="/docs/fund_formation_roadmap.md"
    ),

    # =========================================================================
    # PHASE 9: ADVANCED ITEMS FROM JOHN S. LORE GUIDE
    # Additional requirements for comprehensive fund formation
    # =========================================================================
    
    # Liability Avoidance (Lore Ch. 1)
    ChecklistItem(
        id="adv-1",
        category=ChecklistCategory.COMPLIANCE,
        title="Review Anti-Fraud Provisions",
        description="Understand Section 10(b) Exchange Act, state securities laws - avoid personal liability",
        priority=1,
        week_start=2, week_end=4,
        dependencies=["prep-5"],
        regulatory_reference="Securities Exchange Act Section 10(b), Rule 10b-5",
        regulatory_reference_url="https://www.ecfr.gov/current/title-17/chapter-II/part-240/subpart-A/subject-group-ECFR93b344c9f8f6bc2/section-240.10b-5",
        resources=["SEC 10b-5: https://www.sec.gov/divisions/corpfin/guidance/exchangeactrules-interps.htm"],
        notes="Lore: 'Even inadvertent mistakes can lead to substantial personal liability' - fines up to $5M, 20 years"
    ),
    ChecklistItem(
        id="adv-2",
        category=ChecklistCategory.DOCUMENTS,
        title="Draft Comprehensive Risk Factors",
        description="Risk factors must be crafted to fit specific risks the fund may face - key PPM section",
        priority=1,
        week_start=4, week_end=7,
        dependencies=["doc-1"],
        template_url="/docs/templates/volatility_decay_disclosure.md",
        notes="Lore: 'Risk factors vary significantly from one fund to another and require the drafting attorney to foresee potential contingencies'"
    ),
    
    # Fund Structure Decisions (Lore Ch. 9)
    ChecklistItem(
        id="adv-3",
        category=ChecklistCategory.PREPARATION,
        title="Choose 3(c)(1) vs 3(c)(7) Structure",
        description="3(c)(1): ≤100 accredited investors | 3(c)(7): ≤2000 qualified purchasers ($5M+ net investments)",
        priority=1,
        week_start=1, week_end=2,
        dependencies=["prep-4"],
        regulatory_reference="Investment Company Act Sections 3(c)(1) and 3(c)(7)",
        regulatory_reference_url="https://www.law.cornell.edu/uscode/text/15/80a-3",
        resources=["SEC 3(c)(1) Exemption: https://www.sec.gov/divisions/investment/guidance/icreg40-86.htm"],
        notes="Most startup funds use 3(c)(1) due to lower investor suitability requirements"
    ),
    ChecklistItem(
        id="adv-4",
        category=ChecklistCategory.PREPARATION,
        title="Choose Open-End vs Closed-End Structure",
        description="Open-end: periodic redemptions, typical for liquid strategies | Closed-end: 5-10 yr term, for illiquid",
        priority=2,
        week_start=1, week_end=2,
        dependencies=["prep-1"],
        notes="Lore: 'Structure is driven in large part by the fund's strategy - degree of liquidity of portfolio investments'"
    ),
    
    # Fund Terms (Lore Ch. 8)
    ChecklistItem(
        id="adv-5",
        category=ChecklistCategory.DOCUMENTS,
        title="Define High Water Mark Provisions",
        description="Prevent duplicate performance compensation following volatility - essential investor protection",
        priority=1,
        week_start=4, week_end=6,
        dependencies=["prep-2", "doc-2"],
        template_url="/docs/templates/fee_structure.md",
        notes="Lore: 'high water mark is established immediately following the allocation of incentive compensation'"
    ),
    ChecklistItem(
        id="adv-6",
        category=ChecklistCategory.DOCUMENTS,
        title="Define Lock-up and Gate Provisions",
        description="Lock-up: 1yr+ before withdrawals | Gates: limit redemptions to 10-25% per period",
        priority=1,
        week_start=4, week_end=6,
        dependencies=["doc-2"],
        notes="Lore: 'In 2008-2009 a large number of funds invoked gate provisions to prevent being forced to sell assets at unfavorable terms'"
    ),
    ChecklistItem(
        id="adv-7",
        category=ChecklistCategory.DOCUMENTS,
        title="Develop Side Letter Policy",
        description="Framework for negotiating special terms with strategic investors without prejudicing others",
        priority=2,
        week_start=5, week_end=7,
        dependencies=["doc-3"],
        notes="Lore: 'Care must be taken not to allow side letters to prejudice other investors' - avoid preferential liquidity"
    ),
    
    # Investment Management Agreement (Lore Ch. 3D)
    ChecklistItem(
        id="adv-8",
        category=ChecklistCategory.DOCUMENTS,
        title="Draft Investment Management Agreement",
        description="Agreement between fund and manager defining services, discretionary authority, power of attorney",
        priority=1,
        week_start=5, week_end=7,
        estimated_cost="Included in attorney fees",
        dependencies=["le-2", "le-6"],
        notes="Lore: 'assigns to the fund manager a power of attorney over the fund's assets, including the contributions made by the limited partners'"
    ),
    
    # State Registrations (Lore Ch. 11)
    ChecklistItem(
        id="adv-9",
        category=ChecklistCategory.REGULATORY,
        title="Evaluate State RIA Registration",
        description="If <$150M AUM and investing in securities, may need state RIA registration where management is located",
        priority=1,
        week_start=3, week_end=5,
        dependencies=["prep-3", "reg-1"],
        regulatory_reference="State Securities Laws, Advisers Act",
        regulatory_reference_url="https://www.nasaa.org/contact-your-regulator/",
        resources=["NASAA State Regulators: https://www.nasaa.org/contact-your-regulator/"],
        notes="Lore: 'Many states require hedge fund managers to register once 5+ investors reached in that state'"
    ),
    ChecklistItem(
        id="adv-10",
        category=ChecklistCategory.REGULATORY,
        title="Series 65 Examination (If Required)",
        description="130-question FINRA exam covering securities regulations, ethics, investment analysis",
        priority=2,
        week_start=3, week_end=8,
        estimated_cost="$175 exam fee",
        dependencies=["reg-2"],
        regulatory_reference="FINRA Series 65",
        regulatory_reference_url="https://www.finra.org/registration-exams-ce/qualification-exams/series65",
        resources=["FINRA Series 65: https://www.finra.org/registration-exams-ce/qualification-exams/series65"],
        notes="Required by most states for investment adviser representatives"
    ),
    ChecklistItem(
        id="adv-11",
        category=ChecklistCategory.COMPLIANCE,
        title="Prepare Form ADV Parts 1 & 2",
        description="Part 1: Business operations (46 pages) | Part 2A: Firm Brochure | Part 2B: Brochure Supplement",
        priority=1,
        week_start=7, week_end=10,
        estimated_cost="Included in registration fees",
        dependencies=["reg-2"],
        regulatory_reference="Advisers Act Form ADV",
        regulatory_reference_url="https://www.sec.gov/forms/formadv.pdf",
        resources=["SEC Form ADV: https://www.sec.gov/forms/formadv.pdf"],
        notes="Lore: 'contains false or misleading information can result in criminal or civil liability'"
    ),
    
    # Commodities Registration (Lore Ch. 12)
    ChecklistItem(
        id="adv-12",
        category=ChecklistCategory.REGULATORY,
        title="Evaluate CPO/CTA Registration",
        description="If trading futures, options, swaps, forex swaps - may need CFTC/NFA registration",
        priority=2,
        week_start=3, week_end=6,
        dependencies=["prep-1"],
        regulatory_reference="Commodity Exchange Act",
        regulatory_reference_url="https://www.law.cornell.edu/uscode/text/7/chapter-1",
        resources=["NFA Registration: https://www.nfa.futures.org/registration-membership/how-to-guide/commodity-pool-operator.html"],
        notes="De minimis exemption (4.13(a)(3)): <5% initial margin AND <100% net notional"
    ),
    ChecklistItem(
        id="adv-13",
        category=ChecklistCategory.REGULATORY,
        title="File CPO De Minimis Exemption (If Applicable)",
        description="Rule 4.13(a)(3) - limited commodity interests exemption from full CPO registration",
        priority=2,
        week_start=5, week_end=8,
        dependencies=["adv-12"],
        regulatory_reference="CFTC Rule 4.13(a)(3)",
        regulatory_reference_url="https://www.ecfr.gov/current/title-17/chapter-I/part-4/section-4.13",
        resources=["NFA CPO Exemptions: https://www.nfa.futures.org/registration-membership/who-has-to-register/cpo.html"],
        notes="Must file annually; 2 tests: initial margin <5% AND net notional <100%"
    ),
    
    # Marketing (Lore Ch. 6)
    ChecklistItem(
        id="adv-14",
        category=ChecklistCategory.COMPLIANCE,
        title="Develop Marketing Compliance Policy",
        description="Rules for capital raising: pre-existing relationships, no general solicitation (unless 506(c))",
        priority=1,
        week_start=6, week_end=8,
        dependencies=["doc-1", "reg-3"],
        regulatory_reference="Rule 506(b) and 506(c)",
        regulatory_reference_url="https://www.ecfr.gov/current/title-17/chapter-II/part-230/section-230.506",
        notes="Lore: 'Using intermediaries' - avoid unregistered finders (SEC enforcement risk)"
    ),
    ChecklistItem(
        id="adv-15",
        category=ChecklistCategory.SERVICE_PROVIDERS,
        title="Consider Placement Agent",
        description="FINRA-registered broker-dealer for capital raising - selective due diligence required",
        priority=3,
        week_start=8, week_end=12,
        estimated_cost="2-6% of capital raised",
        dependencies=["doc-1"],
        notes="Lore: 'broker-dealers are very selective and will perform due diligence review of the fund'"
    ),
    
    # Ongoing Compliance (Lore Ch. 11)
    ChecklistItem(
        id="adv-16",
        category=ChecklistCategory.COMPLIANCE,
        title="Establish Ongoing RIA Compliance Program",
        description="Annual ADV updates, record keeping, client disclosure, compliance manual maintenance",
        priority=1,
        week_start=10, week_end=12,
        dependencies=["reg-2", "comp-1"],
        regulatory_reference="Advisers Act ongoing obligations",
        notes="Lore: 'annual license renewals, detailed recordkeeping, ongoing investor disclosure'"
    ),
    ChecklistItem(
        id="adv-17",
        category=ChecklistCategory.COMPLIANCE,
        title="Obtain Surety Bond (If Required)",
        description="Most states require RIAs to provide surety bond - amount varies by state and custody status",
        priority=2,
        week_start=8, week_end=10,
        estimated_cost="$500-$3,000/year",
        dependencies=["reg-2"],
        regulatory_reference="State RIA bonding requirements",
        notes="Lore: 'Hedge funds that have custody of client assets are required to obtain a larger bond'"
    )
]

# In-memory storage
_checklist_items: dict = {item.id: item.model_copy() for item in DEFAULT_CHECKLIST}


@router.get("", response_model=List[ChecklistItem])
async def get_checklist(category: Optional[ChecklistCategory] = None):
    """Get all checklist items, optionally filtered by category"""
    items = list(_checklist_items.values())
    
    if category:
        items = [i for i in items if i.category == category]
    
    # Sort by week_start, then priority
    items.sort(key=lambda x: (x.week_start, x.priority, x.category.value))
    
    return items


@router.get("/summary")
async def get_checklist_summary():
    """Get summary statistics of checklist progress"""
    items = list(_checklist_items.values())
    
    by_status = {}
    by_category = {}
    by_week = {}
    
    for item in items:
        # Count by status
        status = item.status.value
        by_status[status] = by_status.get(status, 0) + 1
        
        # Count by category
        cat = item.category.value
        if cat not in by_category:
            by_category[cat] = {"total": 0, "completed": 0}
        by_category[cat]["total"] += 1
        if item.status == ChecklistItemStatus.COMPLETED:
            by_category[cat]["completed"] += 1
        
        # Count by week
        week = item.week_start
        if week not in by_week:
            by_week[week] = {"total": 0, "completed": 0}
        by_week[week]["total"] += 1
        if item.status == ChecklistItemStatus.COMPLETED:
            by_week[week]["completed"] += 1
    
    completed = by_status.get("completed", 0)
    total = len(items)
    
    return {
        "total_items": total,
        "completed": completed,
        "in_progress": by_status.get("in_progress", 0),
        "not_started": by_status.get("not_started", 0),
        "blocked": by_status.get("blocked", 0),
        "progress_percent": round((completed / total) * 100, 1) if total > 0 else 0,
        "by_category": by_category,
        "by_week": by_week,
        "estimated_weeks": 12
    }


@router.get("/timeline")
async def get_timeline_view():
    """Get items organized by week for Gantt-style view"""
    items = list(_checklist_items.values())
    
    weeks = {}
    for week in range(1, 13):
        weeks[week] = []
    
    for item in items:
        for week in range(item.week_start, item.week_end + 1):
            if week <= 12:
                weeks[week].append({
                    "id": item.id,
                    "title": item.title,
                    "category": item.category.value,
                    "status": item.status.value,
                    "is_start": week == item.week_start,
                    "is_end": week == item.week_end,
                    "priority": item.priority
                })
    
    return weeks


@router.get("/dependencies/{item_id}")
async def get_item_dependencies(item_id: str):
    """Get all dependencies for an item"""
    if item_id not in _checklist_items:
        raise HTTPException(status_code=404, detail="Item not found")
    
    item = _checklist_items[item_id]
    deps = []
    
    for dep_id in item.dependencies:
        if dep_id in _checklist_items:
            dep = _checklist_items[dep_id]
            deps.append({
                "id": dep.id,
                "title": dep.title,
                "status": dep.status.value,
                "completed": dep.status == ChecklistItemStatus.COMPLETED
            })
    
    # Find items that depend on this one
    dependents = []
    for other in _checklist_items.values():
        if item_id in other.dependencies:
            dependents.append({
                "id": other.id,
                "title": other.title,
                "status": other.status.value
            })
    
    return {
        "item_id": item_id,
        "depends_on": deps,
        "blocking": dependents,
        "can_start": all(d["completed"] for d in deps)
    }


@router.get("/{item_id}", response_model=ChecklistItem)
async def get_checklist_item(item_id: str):
    """Get a specific checklist item"""
    if item_id not in _checklist_items:
        raise HTTPException(status_code=404, detail="Item not found")
    return _checklist_items[item_id]


@router.patch("/{item_id}", response_model=ChecklistItem)
async def update_checklist_item(item_id: str, update: ChecklistUpdate):
    """Update a checklist item (status, notes, due date)"""
    if item_id not in _checklist_items:
        raise HTTPException(status_code=404, detail="Item not found")
    
    item = _checklist_items[item_id]
    
    if update.status:
        item.status = update.status
        if update.status == ChecklistItemStatus.COMPLETED:
            item.completed_at = datetime.now().isoformat()
    
    if update.notes is not None:
        item.notes = update.notes
    
    if update.due_date is not None:
        item.due_date = update.due_date
    
    _checklist_items[item_id] = item
    return item


@router.post("/{item_id}/complete", response_model=ChecklistItem)
async def complete_checklist_item(item_id: str):
    """Mark a checklist item as completed"""
    if item_id not in _checklist_items:
        raise HTTPException(status_code=404, detail="Item not found")
    
    item = _checklist_items[item_id]
    item.status = ChecklistItemStatus.COMPLETED
    item.completed_at = datetime.now().isoformat()
    _checklist_items[item_id] = item
    
    return item


@router.post("/reset")
async def reset_checklist():
    """Reset checklist to default state"""
    global _checklist_items
    _checklist_items = {item.id: item.model_copy() for item in DEFAULT_CHECKLIST}
    return {"status": "reset", "items": len(_checklist_items)}


@router.get("/categories/list")
async def list_categories():
    """List all checklist categories"""
    return [
        {"id": "preparation", "name": "Preparation", "icon": "🎯", "week": "1-2"},
        {"id": "incubator", "name": "Incubator Fund Path", "icon": "🌱", "week": "1-52", "description": "Cost-effective alternative: $3K vs $100K"},
        {"id": "legal_entity", "name": "Legal Entity Formation", "icon": "🏢", "week": "2-4"},
        {"id": "documents", "name": "Legal Documents", "icon": "📄", "week": "4-8"},
        {"id": "compliance", "name": "Compliance", "icon": "✅", "week": "5-8"},
        {"id": "service_providers", "name": "Service Providers", "icon": "🤝", "week": "3-8"},
        {"id": "regulatory", "name": "Regulatory Filings", "icon": "📋", "week": "8-10"},
        {"id": "tqqq_strategy", "name": "TQQQ Strategy", "icon": "⚠️", "week": "4-7"}
    ]
