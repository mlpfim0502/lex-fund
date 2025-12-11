import { useState, useEffect } from 'react';
import API_URL from '../config';

// Checklist API functions
const checklistApi = {
    async getChecklist(category = null) {
        const params = category ? `?category=${category}` : '';
        const response = await fetch(`${API_URL}/api/checklist${params}`);
        if (!response.ok) throw new Error('Failed to fetch checklist');
        return response.json();
    },

    async getSummary() {
        const response = await fetch(`${API_URL}/api/checklist/summary`);
        if (!response.ok) throw new Error('Failed to fetch summary');
        return response.json();
    },

    async updateItem(itemId, update) {
        const response = await fetch(`${API_URL}/api/checklist/${itemId}`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(update)
        });
        if (!response.ok) throw new Error('Failed to update item');
        return response.json();
    },

    async completeItem(itemId) {
        const response = await fetch(`${API_URL}/api/checklist/${itemId}/complete`, {
            method: 'POST'
        });
        if (!response.ok) throw new Error('Failed to complete item');
        return response.json();
    }
};

// Phase definitions for each path
const INCUBATOR_PHASES = [
    {
        id: 'formation',
        name: 'Formation',
        icon: '🌱',
        week: 'Week 1-2',
        description: 'Form entities, open accounts, seed with personal capital',
        tips: [
            'Delaware LPs are preferred for fund structures',
            'Interactive Brokers is popular for emerging managers',
            'You can start trading immediately after account opens'
        ]
    },
    {
        id: 'track_record',
        name: 'Build Track Record',
        icon: '📈',
        week: 'Months 1-12',
        description: 'Execute your strategy and document performance',
        tips: [
            'Use Time-Weighted Returns (TWR) for accurate measurement',
            'Maintain detailed trading journal',
            'Document returns net of estimated fees (what investors would see)'
        ]
    },
    {
        id: 'marketing',
        name: 'Marketing Prep',
        icon: '📊',
        week: 'Month 6+',
        description: 'Create pitch deck, tear sheet, and marketing materials',
        tips: [
            'Include track record disclaimer on all materials',
            'Focus on risk-adjusted returns, not just absolute returns',
            'Keep materials professional but concise'
        ]
    },
    {
        id: 'soft_circle',
        name: 'Soft-Circle Investors',
        icon: '🤝',
        week: 'Months 6-12',
        description: 'Gather indications of interest from pre-existing relationships',
        tips: [
            'Only contact people you have pre-existing relationships with',
            'NO cold-calling, NO general advertising',
            'Document verbal commitments but understand they are non-binding'
        ]
    },
    {
        id: 'convert',
        name: 'Convert to Full Fund',
        icon: '🚀',
        week: 'When Ready',
        description: 'Transition to full hedge fund when conditions are met',
        tips: [
            'Aim for 6+ months track record, $3M+ soft-circled',
            'Same entities convert - no need to start over',
            'Budget $50K-$100K for full formation'
        ]
    }
];

const FULL_FUND_PHASES = [
    {
        id: 'preparation',
        name: 'Preparation',
        icon: '🎯',
        week: 'Week 1-2',
        description: 'Define strategy, identify target investors, set fund terms',
        tips: [
            'Document your investment thesis clearly',
            '2/20 is standard but emerging managers may need to be flexible',
            'Know your target: accredited individuals vs institutions'
        ]
    },
    {
        id: 'legal_entity',
        name: 'Legal Entities',
        icon: '🏢',
        week: 'Week 2-4',
        description: 'Form Management Co LLC, GP LLC, and Fund LP',
        tips: [
            'Delaware is the standard jurisdiction',
            'Get EINs immediately after formation',
            'Consider S-Corp election for Management Co (tax benefits)'
        ]
    },
    {
        id: 'documents',
        name: 'Legal Documents',
        icon: '📄',
        week: 'Week 4-8',
        description: 'Draft PPM, LPA, Subscription Agreement, IMA',
        tips: [
            'PPM risk factors must be specific to your strategy',
            'TQQQ requires special volatility decay disclosures',
            'Have attorney draft, not DIY for investor protection'
        ]
    },
    {
        id: 'compliance',
        name: 'Compliance',
        icon: '✅',
        week: 'Week 6-10',
        description: 'Compliance manual, Code of Ethics, AML/KYC procedures',
        tips: [
            'SEC Rule 206(4)-7 requires written policies',
            'Annual compliance reviews are required',
            'Designate a Chief Compliance Officer'
        ]
    },
    {
        id: 'service_providers',
        name: 'Service Providers',
        icon: '🤝',
        week: 'Week 6-10',
        description: 'Engage prime broker, fund admin, auditor, insurance',
        tips: [
            'Interactive Brokers for emerging managers',
            'Fund admin costs $2-5K/month',
            'Annual audit costs $15-30K'
        ]
    },
    {
        id: 'regulatory',
        name: 'Regulatory',
        icon: '📋',
        week: 'Week 8-12',
        description: 'Form D filing, state registrations, RIA if required',
        tips: [
            'Form D within 15 days of first sale',
            'ERA (Exempt Reporting Adviser) if <$150M AUM',
            'State notice filings vary by state'
        ]
    },
    {
        id: 'tqqq_strategy',
        name: 'TQQQ Strategy',
        icon: '⚡',
        week: 'Week 10+',
        description: 'Leveraged ETF specific requirements and risk management',
        tips: [
            'FINRA 09-31 requires specific disclosures',
            'Document VIX-based risk triggers',
            'Consider position limits (40% single ETF, 75% total leveraged)'
        ]
    }
];

// Map checklist categories to phases
const CATEGORY_TO_PHASE = {
    'incubator': 'incubator',
    'preparation': 'preparation',
    'legal_entity': 'legal_entity',
    'documents': 'documents',
    'compliance': 'compliance',
    'service_providers': 'service_providers',
    'regulatory': 'regulatory',
    'tqqq_strategy': 'tqqq_strategy'
};

// Relevant documents for each phase
const PHASE_DOCUMENTS = {
    'formation': [
        { name: 'LLC Operating Agreement', url: '/docs/templates/llc_operating_agreement.md', icon: '📄' },
        { name: 'Incubator Fund Guide', url: '/docs/templates/incubator_fund_guide.md', icon: '🌱' }
    ],
    'track_record': [
        { name: 'Investment Strategy', url: '/docs/templates/investment_strategy.md', icon: '📊' },
        { name: 'Position & VIX Rules', url: '/docs/templates/position_limits_vix_rules.md', icon: '⚡' }
    ],
    'marketing': [
        { name: 'Fund Formation Roadmap', url: '/docs/fund_formation_roadmap.md', icon: '🗺️' }
    ],
    'soft_circle': [],
    'convert': [
        { name: 'Subscription Agreement', url: '/docs/templates/subscription_agreement.md', icon: '📝' },
        { name: 'Full Roadmap', url: '/docs/fund_formation_roadmap.md', icon: '🗺️' }
    ],
    'preparation': [
        { name: 'Investment Strategy', url: '/docs/templates/investment_strategy.md', icon: '📊' },
        { name: 'Fee Structure', url: '/docs/templates/fee_structure.md', icon: '💰' }
    ],
    'legal_entity': [
        { name: 'LLC Operating Agreement', url: '/docs/templates/llc_operating_agreement.md', icon: '📄' }
    ],
    'documents': [
        { name: 'Subscription Agreement', url: '/docs/templates/subscription_agreement.md', icon: '📝' },
        { name: 'Volatility Decay Disclosure', url: '/docs/templates/volatility_decay_disclosure.md', icon: '⚠️' }
    ],
    'compliance': [
        { name: 'Compliance Manual TOC', url: '/docs/templates/compliance_manual_toc.md', icon: '✅' },
        { name: 'AML/KYC Program', url: '/docs/templates/aml_kyc_program.md', icon: '🔍' }
    ],
    'service_providers': [],
    'regulatory': [],
    'tqqq_strategy': [
        { name: 'Position & VIX Rules', url: '/docs/templates/position_limits_vix_rules.md', icon: '⚡' },
        { name: 'Volatility Decay Disclosure', url: '/docs/templates/volatility_decay_disclosure.md', icon: '⚠️' }
    ]
};

function Checklist() {
    const [allItems, setAllItems] = useState([]);
    const [selectedPath, setSelectedPath] = useState('incubator');
    const [currentPhaseIndex, setCurrentPhaseIndex] = useState(0);
    const [loading, setLoading] = useState(true);
    const [expandedItems, setExpandedItems] = useState(new Set());

    useEffect(() => {
        loadData();
    }, []);

    // Reset phase when path changes
    useEffect(() => {
        setCurrentPhaseIndex(0);
    }, [selectedPath]);

    const loadData = async () => {
        setLoading(true);
        try {
            const itemsRes = await checklistApi.getChecklist();
            setAllItems(itemsRes);
        } catch (error) {
            console.error('Failed to load checklist:', error);
        } finally {
            setLoading(false);
        }
    };

    const phases = selectedPath === 'incubator' ? INCUBATOR_PHASES : FULL_FUND_PHASES;
    const currentPhase = phases[currentPhaseIndex];

    // Filter items based on selected path
    const getFilteredItems = () => {
        if (selectedPath === 'incubator') {
            return allItems.filter(item => item.category === 'incubator');
        } else {
            return allItems.filter(item => item.category !== 'incubator');
        }
    };

    // Get items for current phase
    const getCurrentPhaseItems = () => {
        const items = getFilteredItems();

        if (selectedPath === 'incubator') {
            // Map incubator items to phases based on week_start
            return items.filter(item => {
                if (currentPhase.id === 'formation') return item.week_start <= 2;
                if (currentPhase.id === 'track_record') return item.week_start > 2 && item.week_start <= 12;
                if (currentPhase.id === 'marketing') return item.week_start > 12 && item.week_start <= 26;
                if (currentPhase.id === 'soft_circle') return item.week_start > 26 && item.week_start <= 39;
                if (currentPhase.id === 'convert') return item.week_start > 39;
                return false;
            });
        } else {
            return items.filter(item => CATEGORY_TO_PHASE[item.category] === currentPhase.id);
        }
    };

    // Calculate phase completion stats
    const getPhaseStats = (phaseId, phaseIndex) => {
        const items = getFilteredItems();
        let phaseItems = [];

        if (selectedPath === 'incubator') {
            const phase = INCUBATOR_PHASES[phaseIndex];
            phaseItems = items.filter(item => {
                if (phase.id === 'formation') return item.week_start <= 2;
                if (phase.id === 'track_record') return item.week_start > 2 && item.week_start <= 12;
                if (phase.id === 'marketing') return item.week_start > 12 && item.week_start <= 26;
                if (phase.id === 'soft_circle') return item.week_start > 26 && item.week_start <= 39;
                if (phase.id === 'convert') return item.week_start > 39;
                return false;
            });
        } else {
            phaseItems = items.filter(item => CATEGORY_TO_PHASE[item.category] === phaseId);
        }

        const completed = phaseItems.filter(i => i.status === 'completed').length;
        return { completed, total: phaseItems.length };
    };

    const handleStatusChange = async (itemId, newStatus) => {
        try {
            await checklistApi.updateItem(itemId, { status: newStatus });
            loadData();
        } catch (error) {
            console.error('Failed to update status:', error);
        }
    };

    const handleComplete = async (itemId) => {
        try {
            await checklistApi.completeItem(itemId);
            loadData();
        } catch (error) {
            console.error('Failed to complete item:', error);
        }
    };

    const toggleExpandItem = (itemId) => {
        const newExpanded = new Set(expandedItems);
        if (newExpanded.has(itemId)) newExpanded.delete(itemId);
        else newExpanded.add(itemId);
        setExpandedItems(newExpanded);
    };

    const getStatusColor = (status) => {
        switch (status) {
            case 'completed': return '#22c55e';
            case 'in_progress': return '#eab308';
            case 'blocked': return '#ef4444';
            default: return 'var(--color-text-muted)';
        }
    };

    const getStatusIcon = (status) => {
        switch (status) {
            case 'completed': return '✅';
            case 'in_progress': return '🔄';
            case 'blocked': return '🚫';
            default: return '⬜';
        }
    };

    const getPriorityLabel = (priority) => {
        switch (priority) {
            case 1: return { label: 'High', color: '#ef4444' };
            case 2: return { label: 'Med', color: '#eab308' };
            default: return { label: 'Low', color: 'var(--color-text-muted)' };
        }
    };

    // Overall progress
    const getOverallProgress = () => {
        const items = getFilteredItems();
        const completed = items.filter(i => i.status === 'completed').length;
        return { completed, total: items.length, percent: items.length > 0 ? Math.round((completed / items.length) * 100) : 0 };
    };

    const currentPhaseItems = getCurrentPhaseItems();
    const phaseDocs = PHASE_DOCUMENTS[currentPhase?.id] || [];
    const overallProgress = getOverallProgress();
    const currentPhaseStats = getPhaseStats(currentPhase?.id, currentPhaseIndex);

    if (loading) {
        return (
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '50vh' }}>
                <div style={{ textAlign: 'center' }}>
                    <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>📋</div>
                    <div>Loading checklist...</div>
                </div>
            </div>
        );
    }

    return (
        <div style={{ maxWidth: '900px', margin: '0 auto' }}>
            {/* Header */}
            <div style={{ marginBottom: '1.5rem' }}>
                <h1 style={{ marginBottom: '0.25rem', fontSize: '1.75rem' }}>📋 Fund Formation</h1>
                <p style={{ color: 'var(--color-text-muted)', fontSize: '0.9rem' }}>
                    Step-by-step guide to launching your hedge fund
                </p>
            </div>

            {/* Path Selector - Compact */}
            <div style={{
                display: 'flex',
                gap: '0.75rem',
                marginBottom: '1.5rem',
                padding: '0.5rem',
                background: 'var(--color-bg-tertiary)',
                borderRadius: '12px'
            }}>
                <button
                    onClick={() => setSelectedPath('incubator')}
                    style={{
                        flex: 1,
                        padding: '0.75rem 1rem',
                        borderRadius: '8px',
                        border: 'none',
                        background: selectedPath === 'incubator' ? '#22c55e' : 'transparent',
                        color: selectedPath === 'incubator' ? 'white' : 'var(--color-text-primary)',
                        cursor: 'pointer',
                        fontWeight: '600',
                        transition: 'all 0.2s'
                    }}
                >
                    🌱 Incubator Path
                    <div style={{ fontSize: '0.75rem', fontWeight: '400', opacity: 0.9, marginTop: '2px' }}>
                        $3K-$5K • Build track record first
                    </div>
                </button>
                <button
                    onClick={() => setSelectedPath('full')}
                    style={{
                        flex: 1,
                        padding: '0.75rem 1rem',
                        borderRadius: '8px',
                        border: 'none',
                        background: selectedPath === 'full' ? 'var(--color-accent-primary)' : 'transparent',
                        color: selectedPath === 'full' ? 'white' : 'var(--color-text-primary)',
                        cursor: 'pointer',
                        fontWeight: '600',
                        transition: 'all 0.2s'
                    }}
                >
                    🚀 Full Launch
                    <div style={{ fontSize: '0.75rem', fontWeight: '400', opacity: 0.9, marginTop: '2px' }}>
                        $50K-$100K • Accept investors now
                    </div>
                </button>
            </div>

            {/* Overall Progress Bar */}
            <div style={{ marginBottom: '1.5rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem', fontSize: '0.85rem' }}>
                    <span>Overall Progress</span>
                    <span style={{ fontWeight: '600' }}>{overallProgress.completed}/{overallProgress.total} ({overallProgress.percent}%)</span>
                </div>
                <div style={{
                    height: '8px',
                    background: 'var(--color-bg-tertiary)',
                    borderRadius: '4px',
                    overflow: 'hidden'
                }}>
                    <div style={{
                        width: `${overallProgress.percent}%`,
                        height: '100%',
                        background: selectedPath === 'incubator' ? '#22c55e' : 'var(--color-accent-primary)',
                        borderRadius: '4px',
                        transition: 'width 0.3s'
                    }} />
                </div>
            </div>

            {/* Phase Stepper */}
            <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                marginBottom: '1.5rem',
                padding: '1rem',
                background: 'var(--color-bg-secondary)',
                borderRadius: '12px',
                overflow: 'auto'
            }}>
                {phases.map((phase, index) => {
                    const stats = getPhaseStats(phase.id, index);
                    const isComplete = stats.completed === stats.total && stats.total > 0;
                    const isCurrent = index === currentPhaseIndex;
                    const isPast = index < currentPhaseIndex;

                    return (
                        <div
                            key={phase.id}
                            onClick={() => setCurrentPhaseIndex(index)}
                            style={{
                                display: 'flex',
                                flexDirection: 'column',
                                alignItems: 'center',
                                cursor: 'pointer',
                                opacity: isCurrent ? 1 : 0.6,
                                transition: 'opacity 0.2s',
                                minWidth: '60px'
                            }}
                        >
                            <div style={{
                                width: '40px',
                                height: '40px',
                                borderRadius: '50%',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                fontSize: '1.25rem',
                                background: isComplete ? '#22c55e' : isCurrent ? (selectedPath === 'incubator' ? '#22c55e' : 'var(--color-accent-primary)') : 'var(--color-bg-tertiary)',
                                color: (isComplete || isCurrent) ? 'white' : 'inherit',
                                border: isCurrent ? '3px solid' : 'none',
                                borderColor: selectedPath === 'incubator' ? '#22c55e' : 'var(--color-accent-primary)'
                            }}>
                                {isComplete ? '✓' : phase.icon}
                            </div>
                            <div style={{
                                fontSize: '0.7rem',
                                marginTop: '0.5rem',
                                textAlign: 'center',
                                fontWeight: isCurrent ? '600' : '400',
                                maxWidth: '70px'
                            }}>
                                {phase.name}
                            </div>
                            <div style={{ fontSize: '0.65rem', color: 'var(--color-text-muted)' }}>
                                {stats.completed}/{stats.total}
                            </div>
                        </div>
                    );
                })}
            </div>

            {/* Current Phase Card */}
            <div className="card" style={{ marginBottom: '1rem', overflow: 'hidden' }}>
                {/* Phase Header */}
                <div style={{
                    padding: '1.25rem',
                    background: selectedPath === 'incubator' ? 'rgba(34, 197, 94, 0.1)' : 'var(--color-accent-glow)',
                    borderBottom: '1px solid var(--color-border)'
                }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
                        <span style={{ fontSize: '2rem' }}>{currentPhase.icon}</span>
                        <div>
                            <h2 style={{ margin: 0, fontSize: '1.25rem' }}>
                                Phase {currentPhaseIndex + 1}: {currentPhase.name}
                            </h2>
                            <div style={{ fontSize: '0.85rem', color: 'var(--color-text-muted)' }}>
                                {currentPhase.week} • {currentPhaseStats.completed}/{currentPhaseStats.total} completed
                            </div>
                        </div>
                    </div>
                    <p style={{ margin: 0, fontSize: '0.9rem', color: 'var(--color-text-secondary)' }}>
                        {currentPhase.description}
                    </p>
                </div>

                {/* Tips */}
                {currentPhase.tips && currentPhase.tips.length > 0 && (
                    <div style={{
                        padding: '0.75rem 1.25rem',
                        background: 'var(--color-bg-tertiary)',
                        borderBottom: '1px solid var(--color-border)',
                        fontSize: '0.85rem'
                    }}>
                        <strong style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>💡 TIPS</strong>
                        <ul style={{ margin: '0.5rem 0 0 0', paddingLeft: '1.25rem' }}>
                            {currentPhase.tips.map((tip, i) => (
                                <li key={i} style={{ marginBottom: '0.25rem' }}>{tip}</li>
                            ))}
                        </ul>
                    </div>
                )}

                {/* Documents */}
                {phaseDocs.length > 0 && (
                    <div style={{
                        padding: '0.75rem 1.25rem',
                        borderBottom: '1px solid var(--color-border)'
                    }}>
                        <strong style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>📚 DOCUMENTS</strong>
                        <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginTop: '0.5rem' }}>
                            {phaseDocs.map((doc, i) => (
                                <a
                                    key={i}
                                    href={doc.url}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    style={{
                                        display: 'inline-flex',
                                        alignItems: 'center',
                                        gap: '0.25rem',
                                        padding: '0.5rem 0.75rem',
                                        background: 'var(--color-bg-secondary)',
                                        borderRadius: '6px',
                                        fontSize: '0.85rem',
                                        textDecoration: 'none',
                                        border: '1px solid var(--color-border)'
                                    }}
                                >
                                    {doc.icon} {doc.name}
                                </a>
                            ))}
                        </div>
                    </div>
                )}

                {/* Checklist Items */}
                <div style={{ padding: '1rem 1.25rem' }}>
                    <strong style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>✓ CHECKLIST</strong>

                    {currentPhaseItems.length > 0 ? (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', marginTop: '0.75rem' }}>
                            {currentPhaseItems.map((item) => (
                                <div
                                    key={item.id}
                                    style={{
                                        padding: '0.75rem 1rem',
                                        background: 'var(--color-bg-secondary)',
                                        borderRadius: '8px',
                                        borderLeft: `4px solid ${getStatusColor(item.status)}`,
                                        cursor: 'pointer'
                                    }}
                                    onClick={() => toggleExpandItem(item.id)}
                                >
                                    <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.75rem' }}>
                                        <button
                                            onClick={(e) => {
                                                e.stopPropagation();
                                                if (item.status !== 'completed') handleComplete(item.id);
                                            }}
                                            style={{
                                                background: 'none',
                                                border: 'none',
                                                fontSize: '1.25rem',
                                                cursor: 'pointer',
                                                padding: '0',
                                                lineHeight: 1
                                            }}
                                        >
                                            {getStatusIcon(item.status)}
                                        </button>
                                        <div style={{ flex: 1 }}>
                                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
                                                <span style={{
                                                    fontWeight: '500',
                                                    textDecoration: item.status === 'completed' ? 'line-through' : 'none',
                                                    opacity: item.status === 'completed' ? 0.6 : 1
                                                }}>
                                                    {item.title}
                                                </span>
                                                <span style={{
                                                    fontSize: '0.65rem',
                                                    padding: '1px 6px',
                                                    borderRadius: '3px',
                                                    background: getPriorityLabel(item.priority).color,
                                                    color: 'white'
                                                }}>
                                                    {getPriorityLabel(item.priority).label}
                                                </span>
                                                {item.estimated_cost && (
                                                    <span style={{ fontSize: '0.8rem', color: 'var(--color-text-muted)' }}>
                                                        💰 {item.estimated_cost}
                                                    </span>
                                                )}
                                            </div>
                                            <div style={{ fontSize: '0.85rem', color: 'var(--color-text-muted)', marginTop: '0.25rem' }}>
                                                {item.description}
                                            </div>

                                            {/* Expanded Details */}
                                            {expandedItems.has(item.id) && (
                                                <div style={{
                                                    marginTop: '0.75rem',
                                                    padding: '0.75rem',
                                                    background: 'var(--color-bg-tertiary)',
                                                    borderRadius: '6px',
                                                    fontSize: '0.85rem'
                                                }}>
                                                    {item.notes && (
                                                        <div style={{ marginBottom: '0.5rem' }}>
                                                            <strong>Notes:</strong> {item.notes}
                                                        </div>
                                                    )}
                                                    {item.template_url && (
                                                        <div style={{ marginBottom: '0.5rem' }}>
                                                            📄 <a href={item.template_url} target="_blank" rel="noopener noreferrer">View Template</a>
                                                        </div>
                                                    )}
                                                    {item.regulatory_reference && (
                                                        <div style={{ marginBottom: '0.5rem' }}>
                                                            📋 <strong>Ref:</strong>{' '}
                                                            {item.regulatory_reference_url ? (
                                                                <a
                                                                    href={item.regulatory_reference_url}
                                                                    target="_blank"
                                                                    rel="noopener noreferrer"
                                                                    onClick={(e) => e.stopPropagation()}
                                                                >
                                                                    {item.regulatory_reference} ↗
                                                                </a>
                                                            ) : (
                                                                item.regulatory_reference
                                                            )}
                                                        </div>
                                                    )}
                                                    <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.75rem', flexWrap: 'wrap' }}>
                                                        {['not_started', 'in_progress', 'completed', 'blocked'].map((status) => (
                                                            <button
                                                                key={status}
                                                                onClick={(e) => {
                                                                    e.stopPropagation();
                                                                    handleStatusChange(item.id, status);
                                                                }}
                                                                style={{
                                                                    padding: '4px 10px',
                                                                    fontSize: '0.75rem',
                                                                    border: item.status === status ? '2px solid' : '1px solid var(--color-border)',
                                                                    borderColor: item.status === status ? getStatusColor(status) : 'var(--color-border)',
                                                                    background: item.status === status ? getStatusColor(status) + '20' : 'transparent',
                                                                    borderRadius: '4px',
                                                                    cursor: 'pointer'
                                                                }}
                                                            >
                                                                {getStatusIcon(status)} {status.replace('_', ' ')}
                                                            </button>
                                                        ))}
                                                    </div>
                                                </div>
                                            )}
                                        </div>
                                        <span style={{ color: 'var(--color-text-muted)', fontSize: '0.8rem' }}>
                                            {expandedItems.has(item.id) ? '▼' : '▶'}
                                        </span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <div style={{
                            padding: '2rem',
                            textAlign: 'center',
                            color: 'var(--color-text-muted)',
                            background: 'var(--color-bg-tertiary)',
                            borderRadius: '8px',
                            marginTop: '0.75rem'
                        }}>
                            No checklist items for this phase
                        </div>
                    )}
                </div>
            </div>

            {/* Navigation Buttons */}
            <div style={{ display: 'flex', justifyContent: 'space-between', gap: '1rem' }}>
                <button
                    onClick={() => setCurrentPhaseIndex(Math.max(0, currentPhaseIndex - 1))}
                    disabled={currentPhaseIndex === 0}
                    style={{
                        flex: 1,
                        padding: '0.75rem 1.5rem',
                        borderRadius: '8px',
                        border: '1px solid var(--color-border)',
                        background: 'var(--color-bg-secondary)',
                        cursor: currentPhaseIndex === 0 ? 'not-allowed' : 'pointer',
                        opacity: currentPhaseIndex === 0 ? 0.5 : 1,
                        fontWeight: '500'
                    }}
                >
                    ← Previous Phase
                </button>
                <button
                    onClick={() => setCurrentPhaseIndex(Math.min(phases.length - 1, currentPhaseIndex + 1))}
                    disabled={currentPhaseIndex === phases.length - 1}
                    style={{
                        flex: 1,
                        padding: '0.75rem 1.5rem',
                        borderRadius: '8px',
                        border: 'none',
                        background: selectedPath === 'incubator' ? '#22c55e' : 'var(--color-accent-primary)',
                        color: 'white',
                        cursor: currentPhaseIndex === phases.length - 1 ? 'not-allowed' : 'pointer',
                        opacity: currentPhaseIndex === phases.length - 1 ? 0.5 : 1,
                        fontWeight: '500'
                    }}
                >
                    Next Phase →
                </button>
            </div>
        </div>
    );
}

export default Checklist;
