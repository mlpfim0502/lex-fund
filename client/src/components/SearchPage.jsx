import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';

function SearchPage() {
    const [query, setQuery] = useState('');
    const [results, setResults] = useState(null);
    const [loading, setLoading] = useState(false);
    const [searchType, setSearchType] = useState('hybrid');
    const [examples, setExamples] = useState([]);
    const navigate = useNavigate();

    useEffect(() => {
        // Load example questions
        api.getChatExamples()
            .then(data => setExamples(data.examples || []))
            .catch(err => console.error('Failed to load examples:', err));
    }, []);

    const handleSearch = async (e) => {
        e?.preventDefault();
        if (!query.trim()) return;

        setLoading(true);
        try {
            const data = await api.search(query, { searchType });
            setResults(data);
        } catch (error) {
            console.error('Search failed:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleCaseClick = (caseId) => {
        navigate(`/case/${caseId}`);
    };

    const getStatusClass = (status) => {
        const statusMap = {
            green: 'status-green',
            yellow: 'status-yellow',
            red: 'status-red',
            orange: 'status-orange'
        };
        return statusMap[status] || 'status-green';
    };

    const getStatusEmoji = (status) => {
        const emojiMap = {
            green: '🟢',
            yellow: '🟡',
            red: '🔴',
            orange: '🟠'
        };
        return emojiMap[status] || '⚪';
    };

    return (
        <div>
            {/* Hero Section */}
            {!results && (
                <section className="hero">
                    <h1 className="hero-title">Legal Research, Reimagined</h1>
                    <p className="hero-subtitle">
                        AI-powered legal research with citation analysis, semantic search, and intelligent answers.
                    </p>
                </section>
            )}

            {/* Search Box */}
            <div className="search-container">
                <form onSubmit={handleSearch} className="search-box">
                    <span className="search-icon">🔍</span>
                    <input
                        type="text"
                        className="search-input"
                        placeholder="Search cases, statutes, or ask a legal question..."
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                    />
                    <button type="submit" className="search-button" disabled={loading}>
                        {loading ? 'Searching...' : 'Search'}
                    </button>
                </form>

                {/* Search Type Filters */}
                <div className="search-filters">
                    {['hybrid', 'semantic', 'keyword'].map((type) => (
                        <button
                            key={type}
                            className={`filter-chip ${searchType === type ? 'active' : ''}`}
                            onClick={() => setSearchType(type)}
                        >
                            {type.charAt(0).toUpperCase() + type.slice(1)} Search
                        </button>
                    ))}
                </div>
            </div>

            {/* Example Queries */}
            {!results && examples.length > 0 && (
                <div style={{ marginBottom: '2rem' }}>
                    <h3 style={{ color: 'var(--color-text-secondary)', marginBottom: '1rem', fontSize: '0.875rem', fontWeight: '500' }}>
                        Try these example searches:
                    </h3>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                        {examples.map((ex, i) => (
                            <button
                                key={i}
                                className="filter-chip"
                                onClick={() => {
                                    setQuery(ex.question);
                                    handleSearch();
                                }}
                            >
                                {ex.question}
                            </button>
                        ))}
                    </div>
                </div>
            )}

            {/* Loading State */}
            {loading && (
                <div className="results-list">
                    {[1, 2, 3].map((i) => (
                        <div key={i} className="result-card">
                            <div className="skeleton" style={{ height: '24px', width: '60%', marginBottom: '0.5rem' }} />
                            <div className="skeleton" style={{ height: '16px', width: '30%', marginBottom: '1rem' }} />
                            <div className="skeleton" style={{ height: '60px', width: '100%' }} />
                        </div>
                    ))}
                </div>
            )}

            {/* Results */}
            {results && !loading && (
                <div>
                    <div style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        marginBottom: '1rem'
                    }}>
                        <p style={{ color: 'var(--color-text-secondary)' }}>
                            Found <strong>{results.total_results}</strong> results in{' '}
                            <strong>{results.execution_time_ms.toFixed(0)}ms</strong>
                        </p>
                        <button
                            className="btn btn-secondary"
                            onClick={() => setResults(null)}
                        >
                            Clear Results
                        </button>
                    </div>

                    <div className="results-list">
                        {results.results.map((result) => (
                            <div
                                key={result.id}
                                className="result-card"
                                onClick={() => handleCaseClick(result.id)}
                            >
                                <div className="result-header">
                                    <div
                                        className={`result-status ${getStatusClass(result.citation_status)}`}
                                        title={`Status: ${result.citation_status}`}
                                    />
                                    <div>
                                        <h3 className="result-title">
                                            {getStatusEmoji(result.citation_status)} {result.title}
                                        </h3>
                                        <span className="result-citation">{result.citation}</span>
                                    </div>
                                </div>

                                <div className="result-meta">
                                    <span>📍 {result.court}</span>
                                    <span>📅 {result.date_decided}</span>
                                    <span>⭐ Authority: {(result.authority_score * 100).toFixed(0)}%</span>
                                </div>

                                <p className="result-snippet">{result.snippet}</p>

                                {result.highlights?.length > 0 && (
                                    <div className="result-topics">
                                        {result.highlights.map((highlight, i) => (
                                            <span key={i} className="topic-tag">{highlight}</span>
                                        ))}
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>

                    {results.results.length === 0 && (
                        <div className="empty-state">
                            <div className="empty-icon">📭</div>
                            <p>No results found. Try adjusting your search terms.</p>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}

export default SearchPage;
