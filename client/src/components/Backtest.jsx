import { useState, useEffect, useRef } from 'react';
import Chart from 'chart.js/auto';
import 'chartjs-adapter-date-fns';
import annotationPlugin from 'chartjs-plugin-annotation';
import zoomPlugin from 'chartjs-plugin-zoom';
import API_URL from '../config';

Chart.register(annotationPlugin, zoomPlugin);

function Backtest() {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [data, setData] = useState(null);

    // Form state
    const [startDate, setStartDate] = useState('1970-01-01');
    const [endDate, setEndDate] = useState('2025-12-07');
    const [maPeriod, setMaPeriod] = useState(200);
    const [leverage, setLeverage] = useState(3.0);

    // View toggles
    const [showRelativeReturns, setShowRelativeReturns] = useState(false);
    const [riskChartMode, setRiskChartMode] = useState('drawdown'); // 'drawdown' or 'sharpe'

    // Chart refs
    const navChartRef = useRef(null);
    const navChartInstance = useRef(null);
    const riskChartRef = useRef(null);
    const riskChartInstance = useRef(null);

    const runBacktest = async () => {
        setLoading(true);
        setError(null);

        try {
            const params = new URLSearchParams({
                start: startDate,
                end: endDate,
                ma_period: maPeriod.toString(),
                leverage: leverage.toString()
            });

            const response = await fetch(`${API_URL}/api/backtest?${params}`);
            const result = await response.json();

            if (result.success) {
                setData(result);
            } else {
                setError(result.detail || 'Backtest failed');
            }
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    // Format large numbers with K, M, B suffixes
    const formatCompact = (value) => {
        if (value == null || isNaN(value)) return '--';
        if (Math.abs(value) >= 1e9) return (value / 1e9).toFixed(1) + 'B';
        if (Math.abs(value) >= 1e6) return (value / 1e6).toFixed(1) + 'M';
        if (Math.abs(value) >= 1e3) return (value / 1e3).toFixed(1) + 'K';
        return value.toFixed(2);
    };

    // Detect theme for chart colors
    const isDarkTheme = () => {
        return document.documentElement.getAttribute('data-theme') !== 'light';
    };

    const resetZoom = () => {
        if (navChartInstance.current) {
            navChartInstance.current.resetZoom();
        }
    };

    // Initialize NAV chart when data changes
    useEffect(() => {
        if (!data || !navChartRef.current) return;

        if (navChartInstance.current) {
            navChartInstance.current.destroy();
        }

        const ctx = navChartRef.current.getContext('2d');
        const dark = isDarkTheme();

        // Build signal zone annotations
        const annotations = {};
        if (data.signal_zones && data.signal_zones.length > 0) {
            data.signal_zones.forEach((zone, i) => {
                annotations[`zone${i}`] = {
                    type: 'box',
                    xMin: zone.start,
                    xMax: zone.end,
                    backgroundColor: zone.is_stock
                        ? 'rgba(16, 185, 129, 0.12)'
                        : 'rgba(239, 68, 68, 0.12)',
                    borderWidth: 0
                };
            });
        }

        navChartInstance.current = new Chart(ctx, {
            type: 'line',
            data: {
                datasets: [
                    {
                        label: 'Strategy',
                        data: data.nav_series.map(d => ({ x: d.date, y: d.value })),
                        borderColor: '#6366f1',
                        backgroundColor: 'rgba(99, 102, 241, 0.1)',
                        fill: false,
                        tension: 0.1,
                        pointRadius: 0,
                        borderWidth: 2.5,
                        order: 1
                    },
                    {
                        label: '200 MA',
                        data: data.ma_series.map(d => ({ x: d.date, y: d.value })),
                        borderColor: '#ec4899',
                        borderWidth: 1.5,
                        pointRadius: 0,
                        borderDash: [3, 3],
                        order: 2
                    },
                    {
                        label: 'S&P 500',
                        data: data.sp500_series.map(d => ({ x: d.date, y: d.value })),
                        borderColor: '#3b82f6',
                        borderWidth: 1.5,
                        pointRadius: 0,
                        borderDash: [5, 5],
                        order: 3
                    },
                    {
                        label: 'Stock 3x',
                        data: data.stock_series.map(d => ({ x: d.date, y: d.value })),
                        borderColor: '#10b981',
                        borderWidth: 1,
                        pointRadius: 0,
                        hidden: true,
                        order: 4
                    },
                    {
                        label: 'Gold',
                        data: data.gold_series.map(d => ({ x: d.date, y: d.value })),
                        borderColor: '#f59e0b',
                        borderWidth: 1,
                        pointRadius: 0,
                        hidden: true,
                        order: 5
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    intersect: false,
                    mode: 'index'
                },
                scales: {
                    x: {
                        type: 'time',
                        time: { unit: 'year' },
                        grid: { color: dark ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.08)' },
                        ticks: { color: dark ? 'rgba(255, 255, 255, 0.6)' : 'rgba(0, 0, 0, 0.6)' }
                    },
                    y: {
                        type: 'logarithmic',
                        grid: { color: dark ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.08)' },
                        ticks: {
                            color: dark ? 'rgba(255, 255, 255, 0.6)' : 'rgba(0, 0, 0, 0.6)',
                            callback: (value) => formatCompact(value)
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: true,
                        position: 'top',
                        labels: {
                            color: dark ? 'rgba(255, 255, 255, 0.8)' : 'rgba(0, 0, 0, 0.8)',
                            usePointStyle: true
                        }
                    },
                    tooltip: {
                        backgroundColor: dark ? 'rgba(0, 0, 0, 0.85)' : 'rgba(255, 255, 255, 0.95)',
                        titleColor: dark ? '#fff' : '#000',
                        bodyColor: dark ? '#fff' : '#000',
                        borderColor: dark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)',
                        borderWidth: 1,
                        callbacks: {
                            label: (context) => `${context.dataset.label}: ${formatCompact(context.parsed.y)}`
                        }
                    },
                    annotation: { annotations },
                    zoom: {
                        pan: {
                            enabled: true,
                            mode: 'x'
                        },
                        zoom: {
                            wheel: { enabled: true },
                            pinch: { enabled: true },
                            mode: 'x'
                        }
                    }
                }
            }
        });

        return () => {
            if (navChartInstance.current) navChartInstance.current.destroy();
        };
    }, [data]);

    // Initialize Risk chart (Drawdown or Rolling Sharpe)
    useEffect(() => {
        if (!data || !riskChartRef.current) return;

        if (riskChartInstance.current) {
            riskChartInstance.current.destroy();
        }

        const ctx = riskChartRef.current.getContext('2d');
        const dark = isDarkTheme();

        const isDrawdown = riskChartMode === 'drawdown';
        const chartData = isDrawdown ? data.drawdown_series : data.rolling_sharpe_series;

        if (!chartData || chartData.length === 0) return;

        riskChartInstance.current = new Chart(ctx, {
            type: 'line',
            data: {
                datasets: [{
                    label: isDrawdown ? 'Drawdown %' : 'Rolling Sharpe (252d)',
                    data: chartData.map(d => ({ x: d.date, y: d.value })),
                    borderColor: isDrawdown ? '#ef4444' : '#10b981',
                    backgroundColor: isDrawdown ? 'rgba(239, 68, 68, 0.2)' : 'rgba(16, 185, 129, 0.2)',
                    fill: true,
                    tension: 0.1,
                    pointRadius: 0,
                    borderWidth: 1.5
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: { intersect: false, mode: 'index' },
                scales: {
                    x: {
                        type: 'time',
                        time: { unit: 'year' },
                        grid: { color: dark ? 'rgba(255, 255, 255, 0.05)' : 'rgba(0, 0, 0, 0.05)' },
                        ticks: { color: dark ? 'rgba(255, 255, 255, 0.6)' : 'rgba(0, 0, 0, 0.6)' }
                    },
                    y: {
                        grid: { color: dark ? 'rgba(255, 255, 255, 0.05)' : 'rgba(0, 0, 0, 0.05)' },
                        ticks: {
                            color: dark ? 'rgba(255, 255, 255, 0.6)' : 'rgba(0, 0, 0, 0.6)',
                            callback: (value) => isDrawdown ? value.toFixed(0) + '%' : value.toFixed(2)
                        }
                    }
                },
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: dark ? 'rgba(0, 0, 0, 0.85)' : 'rgba(255, 255, 255, 0.95)',
                        titleColor: dark ? '#fff' : '#000',
                        bodyColor: dark ? '#fff' : '#000',
                        callbacks: {
                            label: (context) => isDrawdown
                                ? `Drawdown: ${context.parsed.y.toFixed(2)}%`
                                : `Sharpe: ${context.parsed.y.toFixed(2)}`
                        }
                    }
                }
            }
        });

        return () => {
            if (riskChartInstance.current) riskChartInstance.current.destroy();
        };
    }, [data, riskChartMode]);

    const formatPercent = (value) => {
        if (value == null) return '--';
        return `${(value * 100).toFixed(2)}%`;
    };

    const formatNumber = (value) => {
        if (value == null) return '--';
        if (Math.abs(value) >= 1000) return formatCompact(value);
        return value.toFixed(2);
    };

    return (
        <div className="backtest-container">
            {/* Parameters Panel */}
            <aside className="backtest-sidebar">
                <h2>⚙️ Parameters</h2>

                <div className="form-group">
                    <label>Start Date</label>
                    <input
                        type="date"
                        value={startDate}
                        onChange={(e) => setStartDate(e.target.value)}
                        min="1927-01-01"
                        max="2025-12-31"
                    />
                </div>

                <div className="form-group">
                    <label>End Date</label>
                    <input
                        type="date"
                        value={endDate}
                        onChange={(e) => setEndDate(e.target.value)}
                        min="1927-01-01"
                        max="2025-12-31"
                    />
                </div>

                <div className="form-group">
                    <label>MA Period: <span className="value-highlight">{maPeriod}</span></label>
                    <input
                        type="range"
                        min="20"
                        max="400"
                        step="10"
                        value={maPeriod}
                        onChange={(e) => setMaPeriod(Number(e.target.value))}
                    />
                    <div className="range-labels">
                        <span>20</span>
                        <span>200</span>
                        <span>400</span>
                    </div>
                </div>

                <div className="form-group">
                    <label>Leverage: <span className="value-highlight">{leverage}x</span></label>
                    <input
                        type="range"
                        min="1"
                        max="5"
                        step="0.5"
                        value={leverage}
                        onChange={(e) => setLeverage(Number(e.target.value))}
                    />
                    <div className="range-labels">
                        <span>1x</span>
                        <span>3x</span>
                        <span>5x</span>
                    </div>
                </div>

                <button
                    className="btn-run-backtest"
                    onClick={runBacktest}
                    disabled={loading}
                >
                    {loading ? 'Running...' : '▶ Run Backtest'}
                </button>

                <div className="strategy-info">
                    <h3>Strategy Logic</h3>
                    <p>TQQQ 200MA / IAUM Rotation</p>
                    <ul>
                        <li>📈 <strong>TQQQ</strong>: Price &gt; MA</li>
                        <li>🥇 <strong>IAUM</strong>: Price ≤ MA</li>
                    </ul>
                </div>
            </aside>

            {/* Results Area */}
            <main className="backtest-results">
                {/* Loading Overlay */}
                {loading && (
                    <div className="loading-overlay">
                        <div className="loader">
                            <div className="loader-spinner"></div>
                            <p>Running Backtest...</p>
                            <span className="loader-subtitle">Downloading data & calculating metrics</span>
                        </div>
                    </div>
                )}

                {error && (
                    <div className="error-banner">
                        ⚠️ {error}
                    </div>
                )}

                {/* NAV Chart - TOP PRIORITY */}
                <div className="chart-card">
                    <div className="chart-header">
                        <h3>📊 NAV Performance (Log Scale)</h3>
                        {data && (
                            <div className="chart-controls">
                                <span className="zoom-hint">🔍 Scroll to zoom • Drag to pan</span>
                                <button className="btn-reset-zoom" onClick={resetZoom}>
                                    Reset Zoom
                                </button>
                            </div>
                        )}
                    </div>
                    <div className="chart-wrapper">
                        <canvas ref={navChartRef}></canvas>
                        {!data && !loading && (
                            <div className="chart-placeholder">
                                <span>📊</span>
                                <p>Click "Run Backtest" to see results</p>
                            </div>
                        )}
                    </div>
                    {data && (
                        <div className="signal-legend">
                            <span className="signal-item tqqq">
                                <span className="signal-dot"></span>
                                TQQQ (Price &gt; 200MA)
                            </span>
                            <span className="signal-item iaum">
                                <span className="signal-dot"></span>
                                IAUM (Price ≤ 200MA)
                            </span>
                        </div>
                    )}
                </div>

                {/* Metrics + Risk Chart in 2-column grid */}
                {data && (
                    <div className="metrics-risk-grid">
                        {/* Key Metrics Panel */}
                        <div className="metrics-panel">
                            <h3>📈 Key Metrics</h3>
                            <div className="metrics-compact">
                                <div className="metric-row highlight">
                                    <span className="metric-name">Final NAV</span>
                                    <span className="metric-val">{formatNumber(data.metrics.final_nav)}</span>
                                </div>
                                <div className="metric-row">
                                    <span className="metric-name">CAGR</span>
                                    <span className="metric-val positive">{formatPercent(data.metrics.cagr)}</span>
                                </div>
                                <div className="metric-row">
                                    <span className="metric-name">Max Drawdown</span>
                                    <span className="metric-val negative">{formatPercent(data.metrics.max_drawdown)}</span>
                                </div>
                                <div className="metric-row">
                                    <span className="metric-name">Sharpe Ratio</span>
                                    <span className="metric-val">{formatNumber(data.metrics.sharpe)}</span>
                                </div>
                                <div className="metric-row">
                                    <span className="metric-name">Sortino</span>
                                    <span className="metric-val">{formatNumber(data.metrics.sortino)}</span>
                                </div>
                                <div className="metric-row">
                                    <span className="metric-name">Calmar</span>
                                    <span className="metric-val">{formatNumber(data.metrics.calmar)}</span>
                                </div>
                                <div className="metric-row">
                                    <span className="metric-name">Volatility</span>
                                    <span className="metric-val">{formatPercent(data.metrics.volatility)}</span>
                                </div>
                                <div className="metric-row">
                                    <span className="metric-name">Win Rate</span>
                                    <span className="metric-val">{formatPercent(data.metrics.win_rate)}</span>
                                </div>
                                {data.metrics.recovery_days && (
                                    <div className="metric-row">
                                        <span className="metric-name">Recovery Days</span>
                                        <span className="metric-val">{data.metrics.recovery_days}d</span>
                                    </div>
                                )}
                            </div>
                        </div>

                        {/* Risk Analysis Chart */}
                        <div className="chart-card risk-chart-card">
                            <div className="chart-header">
                                <h3>📉 Risk Analysis</h3>
                                <div className="toggle-container">
                                    <button
                                        className={`toggle-btn ${riskChartMode === 'drawdown' ? 'active' : ''}`}
                                        onClick={() => setRiskChartMode('drawdown')}
                                    >
                                        Drawdown
                                    </button>
                                    <button
                                        className={`toggle-btn ${riskChartMode === 'sharpe' ? 'active' : ''}`}
                                        onClick={() => setRiskChartMode('sharpe')}
                                    >
                                        Rolling Sharpe
                                    </button>
                                </div>
                            </div>
                            <div className="chart-wrapper risk-chart-wrapper">
                                <canvas ref={riskChartRef}></canvas>
                            </div>
                        </div>
                    </div>
                )}

                {/* Annual Returns */}
                {data && data.annual_returns && (
                    <div className="annual-returns-card">
                        <div className="annual-header">
                            <h3>📅 Annual Returns</h3>
                            <div className="toggle-container">
                                <button
                                    className={`toggle-btn ${!showRelativeReturns ? 'active' : ''}`}
                                    onClick={() => setShowRelativeReturns(false)}
                                >
                                    Absolute
                                </button>
                                <button
                                    className={`toggle-btn ${showRelativeReturns ? 'active' : ''}`}
                                    onClick={() => setShowRelativeReturns(true)}
                                >
                                    vs S&P 500
                                </button>
                            </div>
                        </div>
                        <div className="returns-grid">
                            {Object.entries(data.annual_returns)
                                .sort(([a], [b]) => Number(a) - Number(b))
                                .map(([year, ret]) => {
                                    const sp500Ret = data.sp500_annual_returns?.[year] || 0;
                                    const displayValue = showRelativeReturns ? ret - sp500Ret : ret;
                                    return (
                                        <div key={year} className="return-item">
                                            <div className="year">{year}</div>
                                            <div className={`value ${displayValue >= 0 ? 'positive' : 'negative'}`}>
                                                {showRelativeReturns && displayValue > 0 ? '+' : ''}
                                                {displayValue.toFixed(0)}%
                                            </div>
                                            {showRelativeReturns && (
                                                <div className="sp500-value">
                                                    S&P: {sp500Ret.toFixed(0)}%
                                                </div>
                                            )}
                                        </div>
                                    );
                                })
                            }
                        </div>
                    </div>
                )}
            </main>
        </div>
    );
}

export default Backtest;
