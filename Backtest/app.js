/**
 * LRS Backtest Frontend Application
 * Handles form submission, API calls, chart rendering, and UI updates
 */

// =========================================================================
// Configuration
// =========================================================================

const API_URL = '/api/backtest';

// Chart instances
let navChart = null;
let riskChart = null;

// Store returns data for toggle
let cachedReturnsData = {
    absolute: {},
    sp500: {},
    relative: {}
};

// Store risk chart data for toggle
let cachedRiskData = {
    drawdown: [],
    rollingSharpe: [],
    currentView: 'drawdown'
};

// =========================================================================
// Theme Management
// =========================================================================

function initTheme() {
    const savedTheme = localStorage.getItem('theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

    if (savedTheme) {
        document.documentElement.setAttribute('data-theme', savedTheme);
    } else if (!prefersDark) {
        document.documentElement.setAttribute('data-theme', 'light');
    }
    // Default is dark mode (no data-theme attribute needed)
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';

    if (newTheme === 'dark') {
        document.documentElement.removeAttribute('data-theme');
    } else {
        document.documentElement.setAttribute('data-theme', newTheme);
    }

    localStorage.setItem('theme', newTheme);
}

// Initialize theme on page load
initTheme();

// =========================================================================
// DOM Elements
// =========================================================================

const elements = {
    form: document.getElementById('backtest-form'),
    startDate: document.getElementById('start-date'),
    endDate: document.getElementById('end-date'),
    maPeriod: document.getElementById('ma-period'),
    maValue: document.getElementById('ma-value'),
    leverage: document.getElementById('leverage'),
    leverageValue: document.getElementById('leverage-value'),
    runBtn: document.getElementById('run-btn'),
    loadingOverlay: document.getElementById('loading-overlay'),
    chartPlaceholder: document.getElementById('chart-placeholder'),
    annualReturns: document.getElementById('annual-returns'),
    returnsGrid: document.getElementById('returns-grid'),
    errorToast: document.getElementById('error-toast'),
    errorMessage: document.getElementById('error-message'),
    resetZoomBtn: document.getElementById('reset-zoom-btn'),
    toggleAbsolute: document.getElementById('toggle-absolute'),
    toggleRelative: document.getElementById('toggle-relative'),

    // Metrics
    metricNav: document.getElementById('metric-nav'),
    metricCagr: document.getElementById('metric-cagr'),
    metricSharpe: document.getElementById('metric-sharpe'),
    metricMdd: document.getElementById('metric-mdd'),
    metricVol: document.getElementById('metric-vol'),
    metricSortino: document.getElementById('metric-sortino'),
    metricWinrate: document.getElementById('metric-winrate'),
    metricCalmar: document.getElementById('metric-calmar'),
    metricRecovery: document.getElementById('metric-recovery'),

    // Risk chart
    riskChartContainer: document.getElementById('risk-chart-container'),
    toggleDrawdown: document.getElementById('toggle-drawdown'),
    toggleSharpe: document.getElementById('toggle-sharpe'),
};

// =========================================================================
// Event Listeners
// =========================================================================

// Form submission
elements.form.addEventListener('submit', async (e) => {
    e.preventDefault();
    await runBacktest();
});

// MA Period slider
elements.maPeriod.addEventListener('input', (e) => {
    elements.maValue.textContent = e.target.value;
});

// Leverage slider
elements.leverage.addEventListener('input', (e) => {
    elements.leverageValue.textContent = `${e.target.value}x`;
});

// Theme toggle
document.getElementById('theme-toggle').addEventListener('click', toggleTheme);

// =========================================================================
// API Functions
// =========================================================================

async function runBacktest() {
    const params = {
        start: elements.startDate.value,
        end: elements.endDate.value,
        ma_period: elements.maPeriod.value,
        leverage: elements.leverage.value,
    };

    // Validate
    if (new Date(params.start) >= new Date(params.end)) {
        showError('Start date must be before end date');
        return;
    }

    showLoading(true);

    try {
        const queryString = new URLSearchParams(params).toString();
        const response = await fetch(`${API_URL}?${queryString}`);
        const data = await response.json();

        if (!response.ok || !data.success) {
            throw new Error(data.error || 'Backtest failed');
        }

        updateUI(data);

    } catch (error) {
        console.error('Backtest error:', error);
        showError(error.message);
    } finally {
        showLoading(false);
    }
}

// =========================================================================
// UI Update Functions
// =========================================================================

function updateUI(data) {
    updateMetrics(data.metrics);
    updateChart(
        data.nav_series,
        data.stock_series,
        data.stock_1x_series,
        data.gold_series,
        data.ma_series,
        data.sp500_series,
        data.signal_zones,
        data.parameters.ma_period
    );
    updateRiskChart(data.drawdown_series, data.rolling_sharpe_series);
    updateAnnualReturns(data.annual_returns, data.sp500_annual_returns);
}

function updateMetrics(metrics) {
    // Format helpers
    const formatNumber = (n, decimals = 2) => {
        if (n >= 1e9) return (n / 1e9).toFixed(1) + 'B';
        if (n >= 1e6) return (n / 1e6).toFixed(1) + 'M';
        if (n >= 1e3) return (n / 1e3).toFixed(1) + 'K';
        return n.toFixed(decimals);
    };

    const formatPercent = (n) => (n * 100).toFixed(2) + '%';

    // Update metric cards with animation
    animateValue(elements.metricNav, formatNumber(metrics.final_nav));
    animateValue(elements.metricCagr, formatPercent(metrics.cagr));
    animateValue(elements.metricSharpe, metrics.sharpe.toFixed(2));
    animateValue(elements.metricMdd, formatPercent(metrics.max_drawdown));
    animateValue(elements.metricVol, formatPercent(metrics.volatility));
    animateValue(elements.metricSortino, metrics.sortino.toFixed(2));
    animateValue(elements.metricWinrate, formatPercent(metrics.win_rate));
    animateValue(elements.metricCalmar, metrics.calmar.toFixed(2));

    // Recovery time - format as days or "In Progress"
    const recoveryText = metrics.recovery_days !== null
        ? `${metrics.recovery_days} days`
        : 'In Progress';
    animateValue(elements.metricRecovery, recoveryText);

    // Update colors based on values
    elements.metricCagr.className = 'metric-value ' + (metrics.cagr >= 0 ? 'positive' : 'negative');
    elements.metricMdd.className = 'metric-value negative';
}

function animateValue(element, newValue) {
    element.style.opacity = '0';
    element.style.transform = 'translateY(10px)';

    setTimeout(() => {
        element.textContent = newValue;
        element.style.transition = 'all 0.3s ease';
        element.style.opacity = '1';
        element.style.transform = 'translateY(0)';
    }, 100);
}

function updateChart(navSeries, stockSeries, stock1xSeries, goldSeries, maSeries, sp500Series, signalZones, maPeriod) {
    // Hide placeholder
    elements.chartPlaceholder.hidden = true;

    // Prepare data
    const strategyData = navSeries.map(d => ({ x: d.date, y: d.value }));
    const stockData = stockSeries.map(d => ({ x: d.date, y: d.value }));
    const stock1xData = stock1xSeries.map(d => ({ x: d.date, y: d.value }));
    const goldData = goldSeries.map(d => ({ x: d.date, y: d.value }));
    const maData = maSeries.map(d => ({ x: d.date, y: d.value }));
    const sp500Data = sp500Series.map(d => ({ x: d.date, y: d.value }));

    // Build signal zone annotations
    const zoneAnnotations = {};
    signalZones.forEach((zone, i) => {
        zoneAnnotations[`zone${i}`] = {
            type: 'box',
            xMin: zone.start,
            xMax: zone.end,
            backgroundColor: zone.is_stock
                ? 'rgba(16, 185, 129, 0.08)'  // Green for stock
                : 'rgba(239, 68, 68, 0.08)',   // Red for gold
            borderWidth: 0,
            drawTime: 'beforeDatasetsDraw'
        };
    });

    // Chart configuration
    const config = {
        type: 'line',
        data: {
            datasets: [
                {
                    label: 'Strategy',
                    data: strategyData,
                    borderColor: '#6366f1',
                    backgroundColor: 'rgba(99, 102, 241, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.1,
                    pointRadius: 0,
                    pointHoverRadius: 4,
                },
                {
                    label: 'S&P 500',
                    data: sp500Data,
                    borderColor: '#3b82f6',
                    borderWidth: 1.5,
                    borderDash: [3, 3],
                    fill: false,
                    tension: 0.1,
                    pointRadius: 0,
                    pointHoverRadius: 3,
                },
                {
                    label: 'Stock (1x)',
                    data: stock1xData,
                    borderColor: '#14b8a6',
                    borderWidth: 1.5,
                    borderDash: [4, 4],
                    fill: false,
                    tension: 0.1,
                    pointRadius: 0,
                    pointHoverRadius: 3,
                },
                {
                    label: 'Stock (3x)',
                    data: stockData,
                    borderColor: '#10b981',
                    borderWidth: 1.5,
                    borderDash: [5, 5],
                    fill: false,
                    tension: 0.1,
                    pointRadius: 0,
                    pointHoverRadius: 3,
                },
                {
                    label: 'Gold',
                    data: goldData,
                    borderColor: '#f59e0b',
                    borderWidth: 1.5,
                    borderDash: [5, 5],
                    fill: false,
                    tension: 0.1,
                    pointRadius: 0,
                    pointHoverRadius: 3,
                },
                {
                    label: `${maPeriod}MA`,
                    data: maData,
                    borderColor: '#ec4899',
                    borderWidth: 2,
                    borderDash: [2, 2],
                    fill: false,
                    tension: 0.1,
                    pointRadius: 0,
                    pointHoverRadius: 3,
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    align: 'center',
                    labels: {
                        color: '#a0a0b0',
                        padding: 15,
                        usePointStyle: true,
                        pointStyle: 'line',
                        font: {
                            size: 11
                        }
                    },
                    onClick: (e, legendItem, legend) => {
                        // Toggle dataset visibility on click
                        const index = legendItem.datasetIndex;
                        const chart = legend.chart;
                        const meta = chart.getDatasetMeta(index);
                        meta.hidden = meta.hidden === null ? !chart.data.datasets[index].hidden : null;
                        chart.update();
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#fff',
                    bodyColor: '#a0a0b0',
                    padding: 12,
                    cornerRadius: 8,
                    callbacks: {
                        label: (ctx) => {
                            const value = ctx.parsed.y;
                            if (value >= 1e6) {
                                return `${ctx.dataset.label}: ${(value / 1e6).toFixed(2)}M`;
                            }
                            return `${ctx.dataset.label}: ${value.toFixed(2)}`;
                        }
                    }
                },
                zoom: {
                    pan: {
                        enabled: true,
                        mode: 'xy',
                        modifierKey: null,
                    },
                    zoom: {
                        wheel: {
                            enabled: true,
                            speed: 0.1,
                        },
                        pinch: {
                            enabled: true,
                        },
                        drag: {
                            enabled: false,
                        },
                        mode: 'xy',
                        onZoomComplete: () => {
                            elements.resetZoomBtn.hidden = false;
                        }
                    },
                    limits: {
                        x: { min: 'original', max: 'original' },
                        y: { min: 'original', max: 'original' },
                    }
                },
                annotation: {
                    annotations: zoneAnnotations
                }
            },
            scales: {
                x: {
                    type: 'time',
                    time: {
                        unit: 'year',
                        displayFormats: {
                            year: 'yyyy'
                        }
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.05)',
                    },
                    ticks: {
                        color: '#606070',
                        maxRotation: 0,
                    }
                },
                y: {
                    type: 'logarithmic',
                    grid: {
                        color: 'rgba(255, 255, 255, 0.05)',
                    },
                    ticks: {
                        color: '#606070',
                        callback: (value) => {
                            if (value >= 1e9) return (value / 1e9).toFixed(0) + 'B';
                            if (value >= 1e6) return (value / 1e6).toFixed(0) + 'M';
                            if (value >= 1e3) return (value / 1e3).toFixed(0) + 'K';
                            return value;
                        }
                    }
                }
            }
        }
    };

    // Create or update chart
    const ctx = document.getElementById('nav-chart').getContext('2d');

    if (navChart) {
        navChart.destroy();
    }

    navChart = new Chart(ctx, config);

    // Reset zoom button handler
    elements.resetZoomBtn.hidden = true;
    elements.resetZoomBtn.onclick = () => {
        navChart.resetZoom();
        elements.resetZoomBtn.hidden = true;
    };
}

function updateAnnualReturns(returns, sp500Returns) {
    elements.annualReturns.hidden = false;

    // Store data for toggle
    cachedReturnsData.absolute = returns;
    cachedReturnsData.sp500 = sp500Returns;

    // Calculate relative returns (strategy - sp500)
    cachedReturnsData.relative = {};
    Object.keys(returns).forEach(year => {
        const strategyReturn = returns[year] || 0;
        const sp500Return = sp500Returns[year] || 0;
        cachedReturnsData.relative[year] = strategyReturn - sp500Return;
    });

    // Show absolute returns by default
    renderReturnsGrid(cachedReturnsData.absolute, false);
}

function renderReturnsGrid(returns, isRelative) {
    // Sort years
    const years = Object.keys(returns).map(Number).sort((a, b) => a - b);

    // Build grid
    elements.returnsGrid.innerHTML = years.map(year => {
        const value = returns[year];
        const colorClass = value >= 0 ? 'positive' : 'negative';
        const prefix = isRelative ? (value >= 0 ? '+' : '') : (value >= 0 ? '+' : '');
        return `
            <div class="return-item">
                <div class="year">${year}</div>
                <div class="value ${colorClass}">${prefix}${Math.round(value)}%</div>
            </div>
        `;
    }).join('');
}

// Toggle button event listeners
elements.toggleAbsolute.addEventListener('click', () => {
    elements.toggleAbsolute.classList.add('active');
    elements.toggleRelative.classList.remove('active');
    renderReturnsGrid(cachedReturnsData.absolute, false);
});

elements.toggleRelative.addEventListener('click', () => {
    elements.toggleRelative.classList.add('active');
    elements.toggleAbsolute.classList.remove('active');
    renderReturnsGrid(cachedReturnsData.relative, true);
});

// =========================================================================
// Risk Chart Functions
// =========================================================================

function updateRiskChart(drawdownSeries, rollingSharpe) {
    // Show the container
    elements.riskChartContainer.hidden = false;

    // Cache the data
    cachedRiskData.drawdown = drawdownSeries.map(d => ({ x: d.date, y: d.value }));
    cachedRiskData.rollingSharpe = rollingSharpe.map(d => ({ x: d.date, y: d.value }));
    cachedRiskData.currentView = 'drawdown';

    // Reset toggle state
    elements.toggleDrawdown.classList.add('active');
    elements.toggleSharpe.classList.remove('active');

    // Render drawdown by default
    renderRiskChart('drawdown');
}

function renderRiskChart(viewType) {
    const ctx = document.getElementById('risk-chart').getContext('2d');

    // Destroy existing chart
    if (riskChart) {
        riskChart.destroy();
    }

    const isDrawdown = viewType === 'drawdown';
    const data = isDrawdown ? cachedRiskData.drawdown : cachedRiskData.rollingSharpe;

    const config = {
        type: 'line',
        data: {
            datasets: [{
                label: isDrawdown ? 'Drawdown (%)' : 'Rolling Sharpe (252d)',
                data: data,
                borderColor: isDrawdown ? '#ef4444' : '#10b981',
                backgroundColor: isDrawdown
                    ? 'rgba(239, 68, 68, 0.1)'
                    : 'rgba(16, 185, 129, 0.1)',
                borderWidth: 1.5,
                fill: true,
                tension: 0.1,
                pointRadius: 0,
                pointHoverRadius: 3,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            plugins: {
                legend: {
                    display: false,
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#fff',
                    bodyColor: '#a0a0b0',
                    padding: 12,
                    cornerRadius: 8,
                    callbacks: {
                        label: (ctx) => {
                            const value = ctx.parsed.y;
                            if (isDrawdown) {
                                return `Drawdown: ${value.toFixed(2)}%`;
                            }
                            return `Sharpe: ${value.toFixed(2)}`;
                        }
                    }
                },
            },
            scales: {
                x: {
                    type: 'time',
                    time: {
                        unit: 'year',
                        displayFormats: { year: 'yyyy' }
                    },
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#606070', maxRotation: 0 }
                },
                y: {
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: {
                        color: '#606070',
                        callback: (value) => isDrawdown ? `${value.toFixed(0)}%` : value.toFixed(1)
                    }
                }
            }
        }
    };

    riskChart = new Chart(ctx, config);
}

// Risk chart toggle handlers
elements.toggleDrawdown.addEventListener('click', () => {
    elements.toggleDrawdown.classList.add('active');
    elements.toggleSharpe.classList.remove('active');
    cachedRiskData.currentView = 'drawdown';
    renderRiskChart('drawdown');
});

elements.toggleSharpe.addEventListener('click', () => {
    elements.toggleSharpe.classList.add('active');
    elements.toggleDrawdown.classList.remove('active');
    cachedRiskData.currentView = 'rollingSharpe';
    renderRiskChart('rollingSharpe');
});

// =========================================================================
// Utility Functions
// =========================================================================

function showLoading(show) {
    elements.loadingOverlay.hidden = !show;
    elements.runBtn.disabled = show;

    const btnText = elements.runBtn.querySelector('.btn-text');
    const btnLoader = elements.runBtn.querySelector('.btn-loader');

    btnText.hidden = show;
    btnLoader.hidden = !show;
}

function showError(message) {
    elements.errorMessage.textContent = message;
    elements.errorToast.hidden = false;

    // Auto-hide after 5 seconds
    setTimeout(hideError, 5000);
}

function hideError() {
    elements.errorToast.hidden = true;
}

// Make hideError globally available for the close button
window.hideError = hideError;

// =========================================================================
// Initialize
// =========================================================================

console.log('LRS Backtest App initialized');
