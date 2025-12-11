import { useState, useEffect } from 'react';

function Roadmap() {
    const [activePhase, setActivePhase] = useState(null);
    const [selectedPath, setSelectedPath] = useState('incubator'); // 'incubator' or 'full'

    // Incubator Path data
    const incubatorPhases = [
        {
            id: 'inc-1',
            name: "Formation",
            icon: "🌱",
            duration: "Week 1-2",
            status: "not_started",
            items: [
                { name: "Form Fund LP in Delaware", cost: "$500-$1,000", ref: "https://corp.delaware.gov" },
                { name: "Form Manager LLC (optional)", cost: "$500-$1,000", ref: "https://corp.delaware.gov" },
                { name: "Engage Incubator Attorney", cost: "$2,500-$3,500", ref: "https://investmentlawgroup.com" },
                { name: "Obtain EINs", cost: "Free", ref: "https://www.irs.gov/ein" },
                { name: "Open Brokerage Account", cost: "$0", ref: "https://www.interactivebrokers.com" },
                { name: "Seed with Personal Capital", cost: "Your $", ref: null }
            ]
        },
        {
            id: 'inc-2',
            name: "Build Track Record",
            icon: "📈",
            duration: "Months 1-12",
            status: "not_started",
            items: [
                { name: "Execute Investment Strategy", cost: "-", ref: null },
                { name: "Calculate Monthly Returns (TWR)", cost: "-", ref: "https://www.cfainstitute.org" },
                { name: "Maintain Trading Journal", cost: "-", ref: null },
                { name: "Document Performance Net of Fees", cost: "-", ref: null }
            ]
        },
        {
            id: 'inc-3',
            name: "Marketing Prep",
            icon: "📊",
            duration: "Months 6+",
            status: "not_started",
            items: [
                { name: "Create Pitch Deck", cost: "$0-$2,000", ref: null },
                { name: "Develop Tear Sheet", cost: "$0", ref: null },
                { name: "Add Track Record Disclaimer", cost: "$0", ref: null },
                { name: "Prepare Marketing Materials", cost: "$500-$1,500", ref: null }
            ]
        },
        {
            id: 'inc-4',
            name: "Soft-Circle Investors",
            icon: "🤝",
            duration: "Months 6-12",
            status: "not_started",
            items: [
                { name: "Contact Pre-existing Relationships", cost: "$0", ref: null },
                { name: "Gather Indications of Interest", cost: "$0", ref: null },
                { name: "Refine Fund Terms Based on Feedback", cost: "$0", ref: null },
                { name: "NO General Solicitation", cost: "N/A", ref: "https://www.sec.gov/education/capitalraising" }
            ]
        },
        {
            id: 'inc-5',
            name: "Convert to Full Fund",
            icon: "🚀",
            duration: "When Ready",
            status: "not_started",
            items: [
                { name: "Engage Full Formation Attorney", cost: "$50K-$100K", ref: null },
                { name: "Prepare PPM", cost: "Included", ref: null },
                { name: "Prepare Formal LPA", cost: "Included", ref: null },
                { name: "Engage Service Providers", cost: "$3K-$5K/mo", ref: null },
                { name: "File Form D", cost: "$0", ref: "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&type=D" }
            ]
        }
    ];

    const phases = [
        {
            id: 1,
            name: "Legal Entity Formation",
            icon: "🏢",
            duration: "Weeks 1-3",
            status: "not_started",
            items: [
                { name: "Form Management Company LLC", cost: "$500-$1,500", ref: "https://corp.delaware.gov" },
                { name: "Form General Partner LLC", cost: "$500-$1,500", ref: "https://corp.delaware.gov" },
                { name: "Form Fund LP", cost: "$1,000-$2,000", ref: "https://corp.delaware.gov" },
                { name: "Obtain EINs", cost: "Free", ref: "https://www.irs.gov/businesses/small-businesses-self-employed/apply-for-an-employer-identification-number-ein-online" },
                { name: "Open Bank Accounts", cost: "Varies", ref: null }
            ]
        },
        {
            id: 2,
            name: "Regulatory & Legal",
            icon: "📋",
            duration: "Weeks 2-4",
            status: "not_started",
            items: [
                { name: "Determine Registration (SEC/State/ERA)", cost: "$0", ref: "https://www.sec.gov/divisions/investment/iaregulation/memoia.htm" },
                { name: "Engage Fund Formation Attorney", cost: "$50K-$100K", ref: null },
                { name: "File Form D (after first close)", cost: "Free", ref: "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&type=D" }
            ]
        },
        {
            id: 3,
            name: "Legal Documents",
            icon: "📄",
            duration: "Weeks 4-10",
            status: "not_started",
            items: [
                { name: "Draft PPM with TQQQ Disclosures", cost: "$15K-$50K", ref: "https://www.finra.org/rules-guidance/notices/09-31" },
                { name: "Draft LPA", cost: "$10K-$25K", ref: null },
                { name: "Draft Subscription Agreement", cost: "$5K-$10K", ref: "https://www.sec.gov/education/capitalraising/building-blocks/accredited-investor" },
                { name: "Draft Investment Management Agreement", cost: "$5K-$10K", ref: null }
            ]
        },
        {
            id: 4,
            name: "Compliance Setup",
            icon: "✅",
            duration: "Weeks 6-10",
            status: "not_started",
            items: [
                { name: "Develop Compliance Manual", cost: "$5K-$15K", ref: "https://www.sec.gov/rules/final/ia-2204.htm" },
                { name: "Create Code of Ethics", cost: "Included", ref: null },
                { name: "Establish AML/KYC Procedures", cost: "$2K-$5K", ref: null },
                { name: "Designate CCO", cost: "$0", ref: null }
            ]
        },
        {
            id: 5,
            name: "Service Providers",
            icon: "🤝",
            duration: "Weeks 6-10",
            status: "not_started",
            items: [
                { name: "Select Prime Broker", cost: "$0 (minimums apply)", ref: "https://www.interactivebrokers.com" },
                { name: "Engage Fund Auditor", cost: "$15K-$30K/yr", ref: null },
                { name: "Consider Fund Administrator", cost: "$2K-$5K/mo", ref: null },
                { name: "Obtain E&O Insurance", cost: "$5K-$15K/yr", ref: null }
            ]
        },
        {
            id: 6,
            name: "Launch",
            icon: "🚀",
            duration: "Week 10+",
            status: "not_started",
            items: [
                { name: "Final Document Review", cost: "$0", ref: null },
                { name: "First Investor Close", cost: "$0", ref: null },
                { name: "File Form D (within 15 days)", cost: "$0", ref: "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&type=D" },
                { name: "Begin Trading TQQQ Strategy", cost: "$0", ref: null }
            ]
        }
    ];

    const tqqqDisclosures = [
        {
            title: "Volatility Decay Warning",
            content: "TQQQ is designed for DAILY returns. Over longer periods, returns will differ significantly from 3x the index due to compounding.",
            required: true,
            reference: "FINRA Notice 09-31"
        },
        {
            title: "Compounding Risk Example",
            content: "If NASDAQ rises 10% then falls 10% over 30 days, TQQQ will NOT be flat — expect a loss due to daily rebalancing.",
            required: true,
            reference: "FINRA Notice 09-65"
        },
        {
            title: "Position Limits",
            content: "Recommended: Maximum 40% of NAV in any single leveraged ETF, 75% total in all leveraged products.",
            required: false,
            reference: "Best Practice"
        },
        {
            title: "VIX Circuit Breakers",
            content: "Consider reducing leveraged exposure when VIX > 30 and exiting when VIX > 40.",
            required: false,
            reference: "Risk Management"
        }
    ];

    const costSummary = {
        incubator: {
            setup: { low: 3000, high: 5000 },
            annual: { low: 1000, high: 3000 },
            conversion: { low: 50000, high: 100000 }
        },
        full: {
            setup: { low: 38000, high: 110000 },
            annual: { low: 44000, high: 105000 }
        }
    };

    const currentCosts = selectedPath === 'incubator' ? costSummary.incubator : costSummary.full;
    const currentPhases = selectedPath === 'incubator' ? incubatorPhases : phases;

    return (
        <div>
            <div style={{ marginBottom: '2rem' }}>
                <h1 style={{ marginBottom: '0.5rem' }}>🗺️ Fund Formation Roadmap</h1>
                <p style={{ color: 'var(--color-text-secondary)' }}>
                    Complete guide to launching a US hedge fund using TQQQ strategy
                </p>
            </div>

            {/* Path Selector */}
            <div className="card" style={{ marginBottom: '2rem', padding: '1.5rem' }}>
                <h2 style={{ marginBottom: '1rem' }}>🛤️ Choose Your Path</h2>
                <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
                    <div
                        onClick={() => setSelectedPath('incubator')}
                        style={{
                            flex: '1',
                            minWidth: '280px',
                            padding: '1.5rem',
                            borderRadius: '12px',
                            border: selectedPath === 'incubator'
                                ? '3px solid #22c55e'
                                : '2px solid var(--color-border)',
                            background: selectedPath === 'incubator'
                                ? 'rgba(34, 197, 94, 0.1)'
                                : 'var(--color-bg-tertiary)',
                            cursor: 'pointer',
                            transition: 'all 0.2s'
                        }}
                    >
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                            <span style={{ fontSize: '2rem' }}>🌱</span>
                            {selectedPath === 'incubator' && (
                                <span style={{
                                    background: '#22c55e',
                                    color: 'white',
                                    padding: '4px 12px',
                                    borderRadius: '20px',
                                    fontSize: '0.75rem',
                                    fontWeight: '600'
                                }}>
                                    RECOMMENDED
                                </span>
                            )}
                        </div>
                        <h3 style={{ marginBottom: '0.5rem' }}>Incubator Path</h3>
                        <div style={{
                            fontSize: '1.5rem',
                            fontWeight: '700',
                            color: '#22c55e',
                            marginBottom: '0.5rem'
                        }}>
                            $3K - $5K
                        </div>
                        <p style={{ fontSize: '0.9rem', color: 'var(--color-text-secondary)', marginBottom: '0.75rem' }}>
                            Build track record with your own capital first. Cost-effective for most emerging managers.
                        </p>
                        <ul style={{ fontSize: '0.85rem', paddingLeft: '1.25rem' }}>
                            <li>✅ Test strategy in real market</li>
                            <li>✅ Create verifiable track record</li>
                            <li>✅ Soft-circle investors before full launch</li>
                            <li>✅ Convert to full fund when ready</li>
                        </ul>
                    </div>

                    <div
                        onClick={() => setSelectedPath('full')}
                        style={{
                            flex: '1',
                            minWidth: '280px',
                            padding: '1.5rem',
                            borderRadius: '12px',
                            border: selectedPath === 'full'
                                ? '3px solid var(--color-accent-primary)'
                                : '2px solid var(--color-border)',
                            background: selectedPath === 'full'
                                ? 'var(--color-accent-glow)'
                                : 'var(--color-bg-tertiary)',
                            cursor: 'pointer',
                            transition: 'all 0.2s'
                        }}
                    >
                        <div style={{ marginBottom: '0.5rem' }}>
                            <span style={{ fontSize: '2rem' }}>🚀</span>
                        </div>
                        <h3 style={{ marginBottom: '0.5rem' }}>Full Launch</h3>
                        <div style={{
                            fontSize: '1.5rem',
                            fontWeight: '700',
                            color: 'var(--color-accent-primary)',
                            marginBottom: '0.5rem'
                        }}>
                            $50K - $100K
                        </div>
                        <p style={{ fontSize: '0.9rem', color: 'var(--color-text-secondary)', marginBottom: '0.75rem' }}>
                            Direct launch when you have investors ready and capital committed.
                        </p>
                        <ul style={{ fontSize: '0.85rem', paddingLeft: '1.25rem' }}>
                            <li>📋 Full PPM, LPA, Sub Docs</li>
                            <li>📋 Form D, RIA registration</li>
                            <li>📋 Fund admin, auditor engaged</li>
                            <li>📋 Accept outside capital immediately</li>
                        </ul>
                    </div>
                </div>

                {/* Decision Helper */}
                <div style={{
                    marginTop: '1.5rem',
                    padding: '1rem',
                    background: 'var(--color-bg-tertiary)',
                    borderRadius: '8px',
                    fontSize: '0.9rem'
                }}>
                    <strong>Which path is right for you?</strong>
                    <div style={{ marginTop: '0.5rem', display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1rem' }}>
                        <div>
                            <span style={{ color: '#22c55e' }}>🌱 Choose Incubator if:</span>
                            <ul style={{ margin: '0.25rem 0 0 1rem', padding: 0, fontSize: '0.85rem' }}>
                                <li>No outside investors committed yet</li>
                                <li>Want to test strategy first</li>
                                <li>Need 6+ month track record</li>
                                <li>Limited formation budget</li>
                            </ul>
                        </div>
                        <div>
                            <span style={{ color: 'var(--color-accent-primary)' }}>🚀 Choose Full Launch if:</span>
                            <ul style={{ margin: '0.25rem 0 0 1rem', padding: 0, fontSize: '0.85rem' }}>
                                <li>Have $3M+ committed</li>
                                <li>Have verified track record</li>
                                <li>Have $100K+ for formation</li>
                                <li>Ready for full-time management</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>

            {/* Cost Summary Cards */}
            <div className="dashboard-grid" style={{ marginBottom: '2rem' }}>
                <div className="stat-card">
                    <div className="stat-value" style={{ fontSize: '1.8rem' }}>
                        ${(currentCosts.setup.low / 1000).toFixed(0)}K - ${(currentCosts.setup.high / 1000).toFixed(0)}K
                    </div>
                    <div className="stat-label">💰 {selectedPath === 'incubator' ? 'Incubator' : 'Setup'} Cost</div>
                </div>
                {selectedPath === 'incubator' ? (
                    <div className="stat-card">
                        <div className="stat-value" style={{ fontSize: '1.8rem' }}>
                            ${(currentCosts.conversion.low / 1000).toFixed(0)}K - ${(currentCosts.conversion.high / 1000).toFixed(0)}K
                        </div>
                        <div className="stat-label">🔄 Conversion Cost</div>
                    </div>
                ) : (
                    <div className="stat-card">
                        <div className="stat-value" style={{ fontSize: '1.8rem' }}>
                            ${(currentCosts.annual.low / 1000).toFixed(0)}K - ${(currentCosts.annual.high / 1000).toFixed(0)}K
                        </div>
                        <div className="stat-label">📅 Annual Cost</div>
                    </div>
                )}
                <div className="stat-card">
                    <div className="stat-value" style={{ fontSize: '1.8rem' }}>
                        {selectedPath === 'incubator' ? '1-2' : '10-12'}
                    </div>
                    <div className="stat-label">📆 Weeks to {selectedPath === 'incubator' ? 'Start' : 'Launch'}</div>
                </div>
                <div className="stat-card">
                    <div className="stat-value" style={{ fontSize: '1.8rem' }}>{currentPhases.length}</div>
                    <div className="stat-label">📋 {selectedPath === 'incubator' ? 'Phases' : 'Major Phases'}</div>
                </div>
            </div>

            {/* Organization Structure */}
            <div className="card" style={{ marginBottom: '2rem' }}>
                <h2 style={{ marginBottom: '1rem' }}>🏗️ Fund Structure</h2>
                <div style={{
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    gap: '1rem',
                    padding: '1rem'
                }}>
                    {/* Investors */}
                    <div style={{
                        padding: '1rem 2rem',
                        background: 'var(--color-accent-glow)',
                        borderRadius: '12px',
                        border: '2px solid var(--color-accent-primary)',
                        textAlign: 'center'
                    }}>
                        <div style={{ fontSize: '1.5rem' }}>👥</div>
                        <strong>Limited Partners (Investors)</strong>
                        <div style={{ fontSize: '0.8rem', color: 'var(--color-text-muted)' }}>
                            Accredited / Qualified Purchasers
                        </div>
                    </div>

                    <div style={{ fontSize: '1.5rem' }}>↓ Capital</div>

                    {/* Fund */}
                    <div style={{
                        padding: '1rem 2rem',
                        background: 'var(--color-status-green)',
                        borderRadius: '12px',
                        color: 'white',
                        textAlign: 'center'
                    }}>
                        <div style={{ fontSize: '1.5rem' }}>💼</div>
                        <strong>FUND LP (Delaware)</strong>
                        <div style={{ fontSize: '0.8rem', opacity: 0.9 }}>
                            Holds: TQQQ, Cash, Other Assets
                        </div>
                    </div>

                    <div style={{ fontSize: '1.5rem' }}>↓ Managed By</div>

                    {/* GP and Management Row */}
                    <div style={{ display: 'flex', gap: '2rem', flexWrap: 'wrap', justifyContent: 'center' }}>
                        <div style={{
                            padding: '1rem 2rem',
                            background: 'var(--color-status-yellow)',
                            borderRadius: '12px',
                            color: 'black',
                            textAlign: 'center'
                        }}>
                            <div style={{ fontSize: '1.5rem' }}>⚙️</div>
                            <strong>GP LLC</strong>
                            <div style={{ fontSize: '0.8rem' }}>Controls Fund LP</div>
                        </div>

                        <div style={{
                            padding: '1rem 2rem',
                            background: 'var(--color-accent-primary)',
                            borderRadius: '12px',
                            color: 'white',
                            textAlign: 'center'
                        }}>
                            <div style={{ fontSize: '1.5rem' }}>🏢</div>
                            <strong>Management Co LLC</strong>
                            <div style={{ fontSize: '0.8rem' }}>2% Mgmt + 20% Carry</div>
                        </div>
                    </div>

                    <div style={{ fontSize: '1.5rem' }}>↓ Owned By</div>

                    {/* You */}
                    <div style={{
                        padding: '1rem 2rem',
                        background: 'linear-gradient(135deg, var(--color-accent-primary), var(--color-accent-secondary))',
                        borderRadius: '12px',
                        color: 'white',
                        textAlign: 'center'
                    }}>
                        <div style={{ fontSize: '1.5rem' }}>👤</div>
                        <strong>YOU (Principal)</strong>
                        <div style={{ fontSize: '0.8rem', opacity: 0.9 }}>100% Ownership</div>
                    </div>
                </div>
            </div>

            {/* Timeline Phases */}
            <div className="card" style={{ marginBottom: '2rem' }}>
                <h2 style={{ marginBottom: '1rem' }}>
                    📅 {selectedPath === 'incubator' ? 'Incubator' : 'Formation'} Timeline
                </h2>
                <div style={{
                    display: 'flex',
                    overflowX: 'auto',
                    gap: '1rem',
                    padding: '1rem 0'
                }}>
                    {currentPhases.map((phase, index) => (
                        <div
                            key={phase.id}
                            style={{
                                minWidth: '200px',
                                padding: '1rem',
                                background: activePhase === phase.id ? 'var(--color-accent-glow)' : 'var(--color-bg-tertiary)',
                                borderRadius: '12px',
                                border: activePhase === phase.id ? '2px solid var(--color-accent-primary)' : '1px solid var(--color-border)',
                                cursor: 'pointer',
                                transition: 'all 0.2s'
                            }}
                            onClick={() => setActivePhase(activePhase === phase.id ? null : phase.id)}
                        >
                            <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>{phase.icon}</div>
                            <div style={{ fontWeight: '600', marginBottom: '0.25rem' }}>{phase.name}</div>
                            <div style={{ fontSize: '0.8rem', color: 'var(--color-text-muted)' }}>{phase.duration}</div>
                            <div style={{
                                marginTop: '0.5rem',
                                fontSize: '0.75rem',
                                padding: '2px 8px',
                                background: 'var(--color-bg-secondary)',
                                borderRadius: '4px',
                                display: 'inline-block'
                            }}>
                                {phase.items.length} items
                            </div>

                            {activePhase === phase.id && (
                                <div style={{ marginTop: '1rem', borderTop: '1px solid var(--color-border)', paddingTop: '1rem' }}>
                                    {phase.items.map((item, i) => (
                                        <div key={i} style={{
                                            display: 'flex',
                                            justifyContent: 'space-between',
                                            fontSize: '0.85rem',
                                            marginBottom: '0.5rem'
                                        }}>
                                            <span>{item.name}</span>
                                            {item.ref && (
                                                <a
                                                    href={item.ref}
                                                    target="_blank"
                                                    rel="noopener noreferrer"
                                                    onClick={(e) => e.stopPropagation()}
                                                    style={{ marginLeft: '0.5rem' }}
                                                >
                                                    🔗
                                                </a>
                                            )}
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            </div>

            {/* TQQQ Specific Disclosures */}
            <div className="card" style={{ marginBottom: '2rem' }}>
                <h2 style={{ marginBottom: '1rem' }}>⚠️ Required TQQQ Disclosures</h2>
                <p style={{ color: 'var(--color-text-secondary)', marginBottom: '1rem' }}>
                    These disclosures MUST be included in your PPM per FINRA guidance
                </p>

                <div className="results-list">
                    {tqqqDisclosures.map((disc, i) => (
                        <div
                            key={i}
                            className="result-card"
                            style={{
                                borderLeft: disc.required
                                    ? '4px solid var(--color-status-red)'
                                    : '4px solid var(--color-status-yellow)'
                            }}
                        >
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                                <div>
                                    <div style={{ fontWeight: '600', marginBottom: '0.5rem' }}>
                                        {disc.required && '🔴 REQUIRED: '}
                                        {disc.title}
                                    </div>
                                    <p style={{ color: 'var(--color-text-secondary)', fontSize: '0.9rem' }}>
                                        {disc.content}
                                    </p>
                                </div>
                                <span style={{
                                    fontSize: '0.75rem',
                                    padding: '4px 8px',
                                    background: 'var(--color-bg-tertiary)',
                                    borderRadius: '4px',
                                    whiteSpace: 'nowrap'
                                }}>
                                    {disc.reference}
                                </span>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Incubator CAN/CANNOT Section - Only shown for incubator path */}
            {selectedPath === 'incubator' && (
                <div className="card" style={{ marginBottom: '2rem' }}>
                    <h2 style={{ marginBottom: '1rem' }}>📋 Incubator Rules</h2>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1.5rem' }}>
                        <div style={{
                            padding: '1rem',
                            background: 'rgba(34, 197, 94, 0.1)',
                            borderRadius: '8px',
                            border: '2px solid #22c55e'
                        }}>
                            <h3 style={{ color: '#22c55e', marginBottom: '0.75rem' }}>✅ What You CAN Do</h3>
                            <ul style={{ fontSize: '0.9rem', paddingLeft: '1.25rem', margin: 0, lineHeight: 1.8 }}>
                                <li>Trade your own capital in the fund</li>
                                <li>Build and document track record</li>
                                <li>Create pitch deck, tear sheet</li>
                                <li>Soft-circle pre-existing relationships</li>
                                <li>Add/withdraw personal capital</li>
                                <li>Operate multiple incubator funds</li>
                            </ul>
                        </div>
                        <div style={{
                            padding: '1rem',
                            background: 'rgba(239, 68, 68, 0.1)',
                            borderRadius: '8px',
                            border: '2px solid #ef4444'
                        }}>
                            <h3 style={{ color: '#ef4444', marginBottom: '0.75rem' }}>❌ What You CANNOT Do</h3>
                            <ul style={{ fontSize: '0.9rem', paddingLeft: '1.25rem', margin: 0, lineHeight: 1.8 }}>
                                <li>Accept outside investor capital</li>
                                <li>General solicitation / advertising</li>
                                <li>Hold yourself out as RIA</li>
                                <li>Charge management / performance fees</li>
                                <li>Cold-call potential investors</li>
                            </ul>
                        </div>
                    </div>
                    <div style={{
                        marginTop: '1rem',
                        padding: '0.75rem',
                        background: 'var(--color-bg-tertiary)',
                        borderRadius: '6px',
                        fontSize: '0.85rem',
                        color: 'var(--color-text-secondary)'
                    }}>
                        <strong>Source:</strong> John S. Lore, Esq. - "With very few exceptions, the incubator fund should not accept outside investors. Even investment from close friends and family can run afoul of state and federal securities law."
                    </div>
                </div>
            )}

            {/* Key References */}
            <div className="card">
                <h2 style={{ marginBottom: '1rem' }}>📚 Key References</h2>
                <div style={{ display: 'grid', gap: '1rem', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))' }}>
                    <div style={{ padding: '1rem', background: 'var(--color-bg-tertiary)', borderRadius: '8px' }}>
                        <h3 style={{ fontSize: '1rem', marginBottom: '0.5rem' }}>SEC Resources</h3>
                        <ul style={{ fontSize: '0.875rem', paddingLeft: '1rem' }}>
                            <li><a href="https://www.sec.gov/divisions/investment/iaregulation/memoia.htm" target="_blank" rel="noopener">Investment Adviser Registration</a></li>
                            <li><a href="https://www.sec.gov/investor/pubs/hedgefunds.htm" target="_blank" rel="noopener">Hedge Fund Investor Bulletin</a></li>
                            <li><a href="https://www.sec.gov/education/capitalraising/building-blocks/accredited-investor" target="_blank" rel="noopener">Accredited Investor Definition</a></li>
                        </ul>
                    </div>

                    <div style={{ padding: '1rem', background: 'var(--color-bg-tertiary)', borderRadius: '8px' }}>
                        <h3 style={{ fontSize: '1rem', marginBottom: '0.5rem' }}>FINRA Guidance</h3>
                        <ul style={{ fontSize: '0.875rem', paddingLeft: '1rem' }}>
                            <li><a href="https://www.finra.org/rules-guidance/notices/09-31" target="_blank" rel="noopener">📌 Notice 09-31: Leveraged ETFs</a></li>
                            <li><a href="https://www.finra.org/rules-guidance/key-topics/private-placements" target="_blank" rel="noopener">Private Placements Guidance</a></li>
                        </ul>
                    </div>

                    <div style={{ padding: '1rem', background: 'var(--color-bg-tertiary)', borderRadius: '8px' }}>
                        <h3 style={{ fontSize: '1rem', marginBottom: '0.5rem' }}>
                            {selectedPath === 'incubator' ? '🌱 Incubator Resources' : 'Formation Resources'}
                        </h3>
                        <ul style={{ fontSize: '0.875rem', paddingLeft: '1rem' }}>
                            <li><a href="https://corp.delaware.gov" target="_blank" rel="noopener">Delaware Division of Corporations</a></li>
                            <li><a href="https://www.irs.gov/businesses/small-businesses-self-employed/apply-for-an-employer-identification-number-ein-online" target="_blank" rel="noopener">IRS EIN Application</a></li>
                            {selectedPath === 'incubator' ? (
                                <>
                                    <li><a href="https://investmentlawgroup.com" target="_blank" rel="noopener">Investment Law Group (Incubator Specialists)</a></li>
                                    <li><a href="https://www.hedgefundlawblog.com" target="_blank" rel="noopener">Hedge Fund Law Blog</a></li>
                                </>
                            ) : (
                                <li><a href="https://www.iard.com" target="_blank" rel="noopener">IARD System</a></li>
                            )}
                        </ul>
                    </div>
                </div>

                <div style={{ marginTop: '1.5rem', padding: '1rem', background: 'var(--color-accent-glow)', borderRadius: '8px' }}>
                    <p style={{ fontSize: '0.9rem' }}>
                        📄 <strong>Full Documentation:</strong>{' '}
                        <a href="/docs/fund_formation_roadmap.md" target="_blank">
                            View Complete Roadmap with Incubator Path →
                        </a>
                        {selectedPath === 'incubator' && (
                            <span style={{ marginLeft: '1rem' }}>
                                | <a href="/docs/templates/incubator_fund_guide.md" target="_blank">
                                    Incubator Fund Guide →
                                </a>
                            </span>
                        )}
                    </p>
                </div>
            </div>
        </div>
    );
}

export default Roadmap;
