import { useState, useEffect } from 'react';
import api from '../services/api';

function Dashboard() {
    const [stats, setStats] = useState(null);
    const [judges, setJudges] = useState([]);
    const [rankings, setRankings] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const loadData = async () => {
            try {
                const [dashboardRes, judgesRes, rankingsRes] = await Promise.all([
                    api.getDashboard(),
                    api.searchJudges(''),
                    api.getAuthorityRanking(null, 5)
                ]);
                setStats(dashboardRes);
                setJudges(judgesRes);
                setRankings(rankingsRes.rankings || []);
            } catch (error) {
                console.error('Failed to load dashboard:', error);
            } finally {
                setLoading(false);
            }
        };
        loadData();
    }, []);

    if (loading) {
        return (
            <div>
                <h1 style={{ marginBottom: '2rem' }}>Litigation Analytics</h1>
                <div className="dashboard-grid">
                    {[1, 2, 3, 4].map((i) => (
                        <div key={i} className="stat-card">
                            <div className="skeleton" style={{ height: '60px', width: '50%' }} />
                            <div className="skeleton" style={{ height: '16px', width: '70%', marginTop: '0.5rem' }} />
                        </div>
                    ))}
                </div>
            </div>
        );
    }

    return (
        <div>
            <h1 style={{ marginBottom: '0.5rem' }}>📊 Litigation Analytics</h1>
            <p style={{ color: 'var(--color-text-secondary)', marginBottom: '2rem' }}>
                Insights into judges, courts, and case outcomes
            </p>

            {/* Stats Grid */}
            {stats && (
                <div className="dashboard-grid">
                    <div className="stat-card">
                        <div className="stat-value">{stats.total_cases?.toLocaleString()}</div>
                        <div className="stat-label">Total Cases</div>
                    </div>
                    <div className="stat-card">
                        <div className="stat-value">{stats.total_citations?.toLocaleString()}</div>
                        <div className="stat-label">Total Citations</div>
                    </div>
                    <div className="stat-card">
                        <div className="stat-value">{stats.recent_filings}</div>
                        <div className="stat-label">Recent Filings (2020+)</div>
                    </div>
                    <div className="stat-card">
                        <div className="stat-value" style={{ color: 'var(--color-status-red)' }}>
                            {stats.overruled_cases}
                        </div>
                        <div className="stat-label">Overruled Cases</div>
                    </div>
                </div>
            )}

            {/* Trending Topics */}
            {stats?.trending_topics?.length > 0 && (
                <div className="card" style={{ marginTop: '2rem' }}>
                    <h3 style={{ marginBottom: '1rem' }}>🔥 Trending Topics</h3>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                        {stats.trending_topics.map((topic, i) => (
                            <span key={i} className="filter-chip">{topic}</span>
                        ))}
                    </div>
                </div>
            )}

            {/* Two Column Layout */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem', marginTop: '2rem' }}>
                {/* Top Authorities */}
                <div className="card">
                    <h3 style={{ marginBottom: '1rem' }}>⭐ Most Authoritative Cases</h3>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                        {rankings.map((ranking, i) => (
                            <div
                                key={ranking.id}
                                style={{
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: '1rem',
                                    padding: '0.75rem',
                                    background: 'var(--color-bg-tertiary)',
                                    borderRadius: '8px'
                                }}
                            >
                                <span style={{
                                    fontWeight: '700',
                                    color: 'var(--color-accent-primary)',
                                    fontSize: '1.25rem',
                                    width: '24px'
                                }}>
                                    {i + 1}
                                </span>
                                <div style={{ flex: 1, minWidth: 0 }}>
                                    <div style={{
                                        fontWeight: '500',
                                        whiteSpace: 'nowrap',
                                        overflow: 'hidden',
                                        textOverflow: 'ellipsis'
                                    }}>
                                        {ranking.title}
                                    </div>
                                    <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>
                                        {ranking.citation}
                                    </div>
                                </div>
                                <span style={{
                                    fontSize: '0.875rem',
                                    color: 'var(--color-status-green)',
                                    fontWeight: '600'
                                }}>
                                    {(ranking.authority_score * 100).toFixed(0)}%
                                </span>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Judge Profiles */}
                <div className="card">
                    <h3 style={{ marginBottom: '1rem' }}>⚖️ Judge Profiles</h3>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                        {judges.map((judge) => (
                            <div
                                key={judge.id}
                                style={{
                                    padding: '0.75rem',
                                    background: 'var(--color-bg-tertiary)',
                                    borderRadius: '8px'
                                }}
                            >
                                <div style={{ fontWeight: '500', marginBottom: '0.25rem' }}>
                                    {judge.name}
                                </div>
                                <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', marginBottom: '0.5rem' }}>
                                    {judge.court}
                                </div>
                                <div style={{ display: 'flex', gap: '1rem', fontSize: '0.75rem' }}>
                                    <span>
                                        📊 <strong>{judge.total_cases?.toLocaleString()}</strong> cases
                                    </span>
                                    <span>
                                        ✅ <strong>{(judge.motion_grant_rate * 100).toFixed(0)}%</strong> grant rate
                                    </span>
                                    <span>
                                        ⏱️ <strong>{judge.avg_time_to_ruling_days?.toFixed(0)}</strong> days avg
                                    </span>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* Jurisdictions */}
            {stats?.top_jurisdictions?.length > 0 && (
                <div className="card" style={{ marginTop: '2rem' }}>
                    <h3 style={{ marginBottom: '1rem' }}>🌍 Jurisdiction Coverage</h3>
                    <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
                        {stats.top_jurisdictions.map((j, i) => (
                            <div
                                key={i}
                                style={{
                                    padding: '1rem 1.5rem',
                                    background: 'var(--color-bg-tertiary)',
                                    borderRadius: '8px',
                                    textAlign: 'center'
                                }}
                            >
                                <div style={{ fontSize: '1.25rem', fontWeight: '700', color: 'var(--color-accent-primary)' }}>
                                    {j.count}
                                </div>
                                <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', textTransform: 'capitalize' }}>
                                    {j.name}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}

export default Dashboard;
