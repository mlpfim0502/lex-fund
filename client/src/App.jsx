import { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import Checklist from './components/Checklist';
import DocumentViewer from './components/DocumentViewer';
import AIAssistant from './components/AIAssistant';
import Backtest from './components/Backtest';

function Navigation({ theme, toggleTheme }) {
    const location = useLocation();

    return (
        <header className="header">
            <div className="header-content">
                <Link to="/" className="logo">
                    <div className="logo-icon">📋</div>
                    <span>Fund Formation</span>
                </Link>

                <div className="header-actions">
                    <nav className="nav">
                        <Link
                            to="/"
                            className={`nav-link ${location.pathname === '/' ? 'active' : ''}`}
                        >
                            📋 Checklist
                        </Link>
                        <Link
                            to="/backtest"
                            className={`nav-link ${location.pathname === '/backtest' ? 'active' : ''}`}
                        >
                            📈 Backtest
                        </Link>
                    </nav>

                    <button
                        className="theme-toggle"
                        onClick={toggleTheme}
                        title={theme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
                    >
                        {theme === 'dark' ? '☀️' : '🌙'}
                    </button>
                </div>
            </div>
        </header>
    );
}

function App() {
    const [chatOpen, setChatOpen] = useState(false);
    const [theme, setTheme] = useState(() => {
        // Check localStorage or system preference
        const saved = localStorage.getItem('lexai-theme');
        if (saved) return saved;
        return window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark';
    });

    useEffect(() => {
        // Apply theme to document
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('lexai-theme', theme);
    }, [theme]);

    const toggleTheme = () => {
        setTheme(prev => prev === 'dark' ? 'light' : 'dark');
    };

    return (
        <Router>
            <div className="app">
                <Navigation theme={theme} toggleTheme={toggleTheme} />

                <main className="main">
                    <Routes>
                        <Route path="/" element={<Checklist />} />
                        <Route path="/checklist" element={<Checklist />} />
                        <Route path="/backtest" element={<Backtest />} />
                        <Route path="/docs/*" element={<DocumentViewer />} />
                    </Routes>
                </main>

                {/* AI Chat Toggle */}
                <button
                    className="chat-toggle"
                    onClick={() => setChatOpen(!chatOpen)}
                    title="Ask AI Assistant"
                >
                    💬
                </button>

                {/* AI Assistant Panel */}
                <AIAssistant isOpen={chatOpen} onClose={() => setChatOpen(false)} />
            </div>
        </Router>
    );
}

export default App;
