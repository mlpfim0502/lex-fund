import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../services/api';

function CaseViewer() {
    const { caseId } = useParams();
    const navigate = useNavigate();
    const [caseData, setCaseData] = useState(null);
    const [keycite, setKeycite] = useState(null);
    const [citations, setCitations] = useState(null);
    const [risks, setRisks] = useState(null);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState('overview');

    useEffect(() => {
        const loadCase = async () => {
            setLoading(true);
            try {
                const [caseRes, keyciteRes, citationsRes, risksRes] = await Promise.all([
                    api.getCase(caseId),
                    api.getKeyCite(caseId),
                    api.getCitationNetwork(caseId, 1),
                    api.checkRisks(caseId)
                ]);
                setCaseData(caseRes);
                setKeycite(keyciteRes);
                setCitations(citationsRes);
                setRisks(risksRes);
            } catch (error) {
                console.error('Failed to load case:', error);
            } finally {
                setLoading(false);
            }
        };
        loadCase();
    }, [caseId]);

    const getStatusInfo = (status) => {
        const info = {
            green: { emoji: '🟢', label: 'Good Law', class: 'green', desc: 'This case is valid law with no significant negative treatment' },
            yellow: { emoji: '🟡', label: 'Caution', class: 'yellow', desc: 'This case has been distinguished or questioned' },
            red: { emoji: '🔴', label: 'Overruled', class: 'red', desc: 'This case has been overruled and should not be cited' },
            orange: { emoji: '🟠', label: 'Risk', class: 'orange', desc: 'This case may rely on overruled authority' }
        };
        return info[status] || info.green;
    };

    if (loading) {
        return (
            <div className="case-viewer">
                <div className="case-content">
                    <div className="skeleton" style={{ height: '32px', width: '70%', marginBottom: '1rem' }} />
                    <div className="skeleton" style={{ height: '20px', width: '40%', marginBottom: '2rem' }} />
                    <div className="skeleton" style={{ height: '200px', width: '100%' }} />
                </div>
                <div className="case-sidebar">
                    <div className="skeleton" style={{ height: '150px' }} />
                    <div className="skeleton" style={{ height: '150px' }} />
                </div>
            </div>
        );
    }

    if (!caseData) {
        return (
            <div className="empty-state">
                <div className="empty-icon">📂</div>
                <p>Case not found</p>
                <button className="btn btn-primary" onClick={() => navigate('/')}>
                    Back to Search
                </button>
            </div>
        );
    }

    const statusInfo = getStatusInfo(caseData.citation_status);

    return (
        <div className="case-viewer">
            {/* Main Content */}
            <div className="case-content">
                <button
                    className="btn btn-secondary"
                    onClick={() => navigate('/')}
                    style={{ marginBottom: '1rem' }}
                >
                    ← Back to Search
                </button>

                <div className="case-header">
                    <h1 className="case-title">
                        {statusInfo.emoji} {caseData.title}
                    </h1>
                    <p className="result-citation" style={{ fontSize: '1.125rem' }}>
                        {caseData.citation}
                    </p>
                    <div className="result-meta" style={{ marginTop: '1rem' }}>
                        <span>📍 {caseData.court}</span>
                        <span>📅 {caseData.date_decided}</span>
                        <span>⭐ Authority: {(caseData.authority_score * 100).toFixed(0)}%</span>
                    </div>

                    {caseData.topics?.length > 0 && (
                        <div className="result-topics" style={{ marginTop: '1rem' }}>
                            {caseData.topics.map((topic, i) => (
                                <span key={i} className="topic-tag">{topic}</span>
                            ))}
                        </div>
                    )}
                </div>

                {/* Tabs */}
                <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.5rem' }}>
                    {['overview', 'full-text', 'citations'].map((tab) => (
                        <button
                            key={tab}
                            className={`filter-chip ${activeTab === tab ? 'active' : ''}`}
                            onClick={() => setActiveTab(tab)}
                        >
                            {tab.charAt(0).toUpperCase() + tab.slice(1).replace('-', ' ')}
                        </button>
                    ))}
                </div>

                {/* Tab Content */}
                {activeTab === 'overview' && (
                    <div>
                        <h3 style={{ marginBottom: '1rem', color: 'var(--color-text-primary)' }}>Summary</h3>
                        <p className="case-text">{caseData.full_text}</p>

                        {caseData.headnotes?.length > 0 && (
                            <div style={{ marginTop: '2rem' }}>
                                <h3 style={{ marginBottom: '1rem', color: 'var(--color-text-primary)' }}>Headnotes</h3>
                                <ul style={{ listStyle: 'disc', paddingLeft: '1.5rem' }}>
                                    {caseData.headnotes.map((note, i) => (
                                        <li key={i} style={{ color: 'var(--color-text-secondary)', marginBottom: '0.5rem' }}>
                                            {note}
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        )}
                    </div>
                )}

                {activeTab === 'full-text' && (
                    <div className="case-text" style={{ whiteSpace: 'pre-wrap' }}>
                        {caseData.full_text}
                    </div>
                )}

                {activeTab === 'citations' && citations && (
                    <div>
                        <h3 style={{ marginBottom: '1rem' }}>Citation Network</h3>
                        <div className="results-list">
                            {citations.nodes?.filter(n => n.id !== caseId).map((node) => (
                                <div
                                    key={node.id}
                                    className="result-card"
                                    onClick={() => navigate(`/case/${node.id}`)}
                                    style={{ padding: '1rem' }}
                                >
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                        <span>{getStatusInfo(node.status).emoji}</span>
                                        <span style={{ fontWeight: '600' }}>{node.title}</span>
                                    </div>
                                    <span className="result-citation">{node.citation}</span>
                                </div>
                            ))}
                            {(!citations.nodes || citations.nodes.length <= 1) && (
                                <p style={{ color: 'var(--color-text-muted)' }}>No citations found</p>
                            )}
                        </div>
                    </div>
                )}
            </div>

            {/* Sidebar */}
            <div className="case-sidebar">
                {/* KeyCite Panel */}
                <div className="keycite-panel">
                    <h3 style={{ marginBottom: '1rem', fontSize: '1rem' }}>📋 KeyCite Status</h3>

                    <div className={`keycite-status ${statusInfo.class}`}>
                        <span style={{ fontSize: '1.5rem' }}>{statusInfo.emoji}</span>
                        <div>
                            <strong>{statusInfo.label}</strong>
                            <p style={{ fontSize: '0.75rem', color: 'var(--color-text-secondary)', marginTop: '0.25rem' }}>
                                {statusInfo.desc}
                            </p>
                        </div>
                    </div>

                    {keycite && (
                        <div style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)' }}>
                            <p>📊 Citing References: <strong>{keycite.citing_references}</strong></p>
                            {keycite.negative_treatments?.length > 0 && (
                                <p style={{ color: 'var(--color-status-yellow)', marginTop: '0.5rem' }}>
                                    ⚠️ {keycite.negative_treatments.length} negative treatment(s)
                                </p>
                            )}
                        </div>
                    )}
                </div>

                {/* Bad Law Bot - Risks */}
                {risks?.has_risks && (
                    <div className="keycite-panel" style={{ borderColor: 'var(--color-status-orange)' }}>
                        <h3 style={{ marginBottom: '1rem', fontSize: '1rem', color: 'var(--color-status-orange)' }}>
                            🚨 Bad Law Bot Alert
                        </h3>
                        {risks.risks.map((risk, i) => (
                            <div
                                key={i}
                                style={{
                                    background: 'rgba(249, 115, 22, 0.1)',
                                    padding: '0.75rem',
                                    borderRadius: '8px',
                                    marginBottom: '0.5rem'
                                }}
                            >
                                <p style={{ fontSize: '0.875rem', fontWeight: '500' }}>{risk.reason}</p>
                                <p style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', marginTop: '0.25rem' }}>
                                    {risk.cited_case_title}
                                </p>
                            </div>
                        ))}
                    </div>
                )}

                {/* Authority Score */}
                <div className="keycite-panel">
                    <h3 style={{ marginBottom: '1rem', fontSize: '1rem' }}>⭐ Authority Score</h3>
                    <div style={{
                        background: 'var(--color-bg-tertiary)',
                        borderRadius: '8px',
                        padding: '1rem',
                        textAlign: 'center'
                    }}>
                        <div className="stat-value" style={{ fontSize: '2rem' }}>
                            {(caseData.authority_score * 100).toFixed(0)}%
                        </div>
                        <p style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>
                            Based on PageRank citation analysis
                        </p>
                    </div>
                </div>

                {/* Stats */}
                <div className="keycite-panel">
                    <h3 style={{ marginBottom: '1rem', fontSize: '1rem' }}>📊 Citation Stats</h3>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                        <div style={{ textAlign: 'center' }}>
                            <div style={{ fontSize: '1.5rem', fontWeight: '700', color: 'var(--color-accent-primary)' }}>
                                {caseData.cited_by_count?.toLocaleString() || 0}
                            </div>
                            <span style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>Cited By</span>
                        </div>
                        <div style={{ textAlign: 'center' }}>
                            <div style={{ fontSize: '1.5rem', fontWeight: '700', color: 'var(--color-accent-primary)' }}>
                                {caseData.citing_count || 0}
                            </div>
                            <span style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>Cites</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default CaseViewer;
