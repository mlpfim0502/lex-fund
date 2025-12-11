"""
Backtest Engine for Leveraged Rotation Strategy (LRS)
Modular design for API integration
"""
import pandas as pd
import numpy as np
import yfinance as yf
import time
import os
import hashlib
import pickle
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta

# Cache configuration
CACHE_DIR = Path("/tmp/backtest_cache")
CACHE_TTL_HOURS = 4

@dataclass
class BacktestResult:
    """Container for backtest results"""
    nav: pd.Series
    metrics: Dict[str, float]
    annual_returns: Dict[int, float]
    sp500_annual_returns: Dict[int, float]  # S&P 500 annual returns for comparison
    data_info: Dict[str, str]
    stock_nav: pd.Series  # Leveraged (3x) stock NAV
    stock_nav_1x: pd.Series  # Unleveraged (1x) stock NAV
    gold_nav: pd.Series
    stock_ma: pd.Series  # Moving average of stock NAV
    sp500_nav: pd.Series  # S&P 500 NAV for chart
    signal: pd.Series  # Trading signal (True=stock, False=gold)
    drawdown_series: pd.Series  # Daily drawdown for chart
    rolling_sharpe: pd.Series  # 252-day rolling Sharpe ratio
    recovery_days: Optional[int]  # Days to recover from max drawdown

# =========================================================================
# Data Download with Caching
# =========================================================================

TICKERS = ["^GSPC", "^IXIC", "^NDX", "QQQ", "TQQQ", "IAU", "GC=F"]

def _get_cache_path(start: str, end: str) -> Path:
    """Generate cache file path based on date parameters."""
    cache_key = hashlib.md5(f"{start}_{end}".encode()).hexdigest()[:12]
    return CACHE_DIR / f"data_{cache_key}.pkl"

def _is_cache_valid(cache_path: Path) -> bool:
    """Check if cache file exists and is within TTL."""
    if not cache_path.exists():
        return False
    age_hours = (time.time() - cache_path.stat().st_mtime) / 3600
    return age_hours < CACHE_TTL_HOURS

def download_data(start: str, end: str, max_retries: int = 3, timeout: int = 60) -> pd.DataFrame:
    """Download historical data with caching and retry logic."""
    # Check if end date is too close to today
    today = datetime.now().date()
    try:
        end_date = pd.to_datetime(end).date()
    except:
        end_date = today
    
    days_from_today = (today - end_date).days
    
    # Check cache first
    cache_path = _get_cache_path(start, end)
    if _is_cache_valid(cache_path):
        try:
            with open(cache_path, 'rb') as f:
                print(f"[Cache] Loading data from {cache_path}")
                return pickle.load(f)
        except Exception as e:
            print(f"[Cache] Failed to load: {e}")
    
    # Download fresh data
    for attempt in range(max_retries):
        try:
            raw = yf.download(
                TICKERS,
                start=start,
                end=end,
                auto_adjust=True,
                timeout=timeout,
                progress=False
            )
            if not raw.empty:
                close = raw["Close"].ffill().bfill()
                # Save to cache
                CACHE_DIR.mkdir(parents=True, exist_ok=True)
                with open(cache_path, 'wb') as f:
                    pickle.dump(close, f)
                print(f"[Cache] Saved data to {cache_path}")
                return close
            print(f"[Warning] Attempt {attempt + 1}: No data returned for range {start} to {end}")
            time.sleep(2)
        except Exception as e:
            print(f"Download attempt {attempt + 1} failed: {e}")
            time.sleep(2)
    
    # Provide informative error message
    if days_from_today <= 1:
        raise RuntimeError(
            f"Failed to download data: End date '{end}' is too close to today ({today}). "
            f"Financial data may not be available yet due to market data delays. "
            f"Try setting the end date to at least 2-3 days before today."
        )
    elif days_from_today < 0:
        raise RuntimeError(
            f"Failed to download data: End date '{end}' is in the future. "
            f"Please use a date on or before today ({today})."
        )
    else:
        raise RuntimeError(
            f"Failed to download data after {max_retries} attempts. "
            f"Please check your internet connection or try again later."
        )

# =========================================================================
# Returns Calculation
# =========================================================================

def build_stock_returns(close: pd.DataFrame, leverage: float = 3.0) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """
    Build synthetic stock returns by stitching indices across eras.
    Returns: (leveraged returns, leveraged NAV, unleveraged NAV)
    """
    r_sp = close["^GSPC"].pct_change(fill_method=None)
    r_ixic = close["^IXIC"].pct_change(fill_method=None)
    r_ndx = close["^NDX"].pct_change(fill_method=None)
    r_qqq = close["QQQ"].pct_change(fill_method=None)
    r_tqqq = close["TQQQ"].pct_change(fill_method=None)
    
    # Stitch returns across eras (1x unleveraged)
    r_series = pd.Series(index=close.index, dtype=float)
    r_series.loc["1927":"1970"] = r_sp.loc["1927":"1970"]
    r_series.loc["1971":"1985"] = r_ixic.loc["1971":"1985"]
    r_series.loc["1986":"1999"] = r_ndx.loc["1986":"1999"]
    r_series.loc["2000":"2009"] = r_qqq.loc["2000":"2009"]
    r_series.loc["2010":] = r_qqq.loc["2010":]  # Use QQQ for 1x even in TQQQ era
    
    r_series = r_series.replace([np.inf, -np.inf], np.nan).fillna(0)
    
    # 1x unleveraged NAV
    stock_nav_1x = (1 + r_series).cumprod()
    stock_nav_1x /= stock_nav_1x.iloc[0]
    
    # Apply leverage to simulated period
    r_stock_3x = r_series * leverage
    r_stock_3x.loc["2010-01-01":] = r_tqqq.loc["2010-01-01":].fillna(0)
    
    # 3x leveraged NAV
    stock_nav = (1 + r_stock_3x).cumprod()
    stock_nav /= stock_nav.iloc[0]
    
    return r_stock_3x, stock_nav, stock_nav_1x

def build_gold_returns(close: pd.DataFrame) -> Tuple[pd.Series, pd.Series]:
    """
    Build gold returns by stitching futures and ETF.
    Returns: (gold returns, gold NAV)
    """
    r_gold = pd.Series(index=close.index, dtype=float)
    iau_start = close["IAU"].first_valid_index()
    
    r_gold.loc[:iau_start] = close["GC=F"].pct_change(fill_method=None).loc[:iau_start]
    r_gold.loc[iau_start:] = close["IAU"].pct_change(fill_method=None).loc[iau_start:]
    
    r_gold = r_gold.replace([np.inf, -np.inf], np.nan).fillna(0)
    
    gold_nav = (1 + r_gold).cumprod()
    gold_nav /= gold_nav.iloc[0]
    
    return r_gold, gold_nav

# =========================================================================
# Signal Generation
# =========================================================================

def generate_signal(stock_nav: pd.Series, ma_period: int = 200) -> Tuple[pd.Series, pd.Series]:
    """
    Generate trading signal based on MA crossover.
    Returns: (signal, ma) where signal is Boolean series (True=stock, False=gold)
    """
    data_points = len(stock_nav)
    if data_points < ma_period:
        print(f"[Warning] Data has only {data_points} points, but MA period is {ma_period}. "
              f"MA line will not be visible. Consider reducing MA period to {max(5, data_points // 2)} or less, "
              f"or expanding your date range.")
    
    ma = stock_nav.rolling(ma_period).mean()
    # Use yesterday's values to avoid look-ahead bias
    signal = stock_nav.shift(1) > ma.shift(1)
    return signal, ma

# =========================================================================
# Metrics Calculation
# =========================================================================

def calculate_cagr(nav: pd.Series) -> float:
    years = (nav.index[-1] - nav.index[0]).days / 365
    return (nav.iloc[-1] / nav.iloc[0]) ** (1 / years) - 1

def calculate_volatility(returns: pd.Series) -> float:
    return returns.std() * np.sqrt(252)

def calculate_sharpe(returns: pd.Series) -> float:
    vol = calculate_volatility(returns)
    return returns.mean() * 252 / vol if vol > 0 else np.nan

def calculate_sortino(returns: pd.Series) -> float:
    downside = returns[returns < 0].std() * np.sqrt(252)
    return returns.mean() * 252 / downside if downside > 0 else np.nan

def calculate_max_drawdown(nav: pd.Series) -> float:
    high = nav.cummax()
    dd = nav / high - 1
    return dd.min()

def calculate_drawdown_series(nav: pd.Series) -> pd.Series:
    """Calculate drawdown series for charting."""
    high = nav.cummax()
    return nav / high - 1

def calculate_recovery_days(nav: pd.Series) -> Optional[int]:
    """
    Calculate days to recover from maximum drawdown.
    Returns None if still in drawdown or never recovered.
    """
    high = nav.cummax()
    dd = nav / high - 1
    
    # Find max drawdown point
    mdd_idx = dd.idxmin()
    
    # Find when NAV recovered to new high after max drawdown
    post_mdd = nav.loc[mdd_idx:]
    high_at_mdd = high.loc[mdd_idx]
    
    # Find first point where NAV >= previous high
    recovered = post_mdd[post_mdd >= high_at_mdd]
    
    if len(recovered) > 0:
        recovery_date = recovered.index[0]
        return (recovery_date - mdd_idx).days
    return None  # Still in drawdown

def calculate_rolling_sharpe(returns: pd.Series, window: int = 252) -> pd.Series:
    """
    Calculate rolling Sharpe ratio with specified window.
    Uses annualized returns and volatility.
    """
    rolling_mean = returns.rolling(window).mean() * 252
    rolling_std = returns.rolling(window).std() * np.sqrt(252)
    rolling_sharpe = rolling_mean / rolling_std
    return rolling_sharpe.replace([np.inf, -np.inf], np.nan)

def calculate_win_rate(returns: pd.Series) -> float:
    return (returns > 0).mean()

def calculate_calmar(cagr: float, mdd: float) -> float:
    return cagr / abs(mdd) if mdd < 0 else np.nan

def calculate_all_metrics(nav: pd.Series, returns: pd.Series) -> Dict[str, float]:
    """Calculate all performance metrics."""
    cagr = calculate_cagr(nav)
    mdd = calculate_max_drawdown(nav)
    
    return {
        "final_nav": float(nav.iloc[-1]),
        "cagr": float(cagr),
        "volatility": float(calculate_volatility(returns)),
        "sharpe": float(calculate_sharpe(returns)),
        "sortino": float(calculate_sortino(returns)),
        "max_drawdown": float(mdd),
        "win_rate": float(calculate_win_rate(returns)),
        "calmar": float(calculate_calmar(cagr, mdd)),
        "start_date": nav.index[0].strftime("%Y-%m-%d"),
        "end_date": nav.index[-1].strftime("%Y-%m-%d"),
    }

def calculate_annual_returns(nav: pd.Series) -> Dict[int, float]:
    """Calculate annual returns as percentages."""
    annual_nav = nav.resample("YE").last()
    annual_ret = annual_nav.pct_change().dropna()
    return {int(d.year): float(r * 100) for d, r in annual_ret.items()}

# =========================================================================
# Main Backtest Function
# =========================================================================

def run_backtest(
    start: str = "1920-01-01",
    end: str = "2025-12-07",
    ma_period: int = 200,
    leverage: float = 3.0
) -> BacktestResult:
    """
    Run the Leveraged Rotation Strategy backtest.
    
    Args:
        start: Backtest start date (YYYY-MM-DD)
        end: Backtest end date (YYYY-MM-DD)
        ma_period: Moving average period for signal
        leverage: Leverage multiplier for simulated period
    
    Returns:
        BacktestResult containing NAV, metrics, and annual returns
    """
    # Define earliest available data date (S&P 500 starts around 1927)
    EARLIEST_DATA_DATE = pd.to_datetime("1927-01-01")
    EARLIEST_RECOMMENDED_START = pd.to_datetime("1928-01-01")  # 1 year buffer for MA
    
    user_start = pd.to_datetime(start)
    user_end = pd.to_datetime(end)
    
    # Validate date range
    if user_start >= user_end:
        raise ValueError(f"Start date ({start}) must be before end date ({end})")
    
    if user_start < EARLIEST_RECOMMENDED_START:
        print(f"[Warning] Start date {start} is very early. S&P 500 data begins around 1927. "
              f"Using {EARLIEST_RECOMMENDED_START.strftime('%Y-%m-%d')} as minimum start date for reliable MA calculation.")
        user_start = EARLIEST_RECOMMENDED_START
    
    # Calculate extended start date to ensure MA is available from user's start date
    # We need ma_period + buffer trading days (~1.5x calendar days for weekends/holidays)
    extended_start = user_start - timedelta(days=int(ma_period * 1.5) + 30)
    
    # Ensure extended start doesn't go before earliest data
    if extended_start < EARLIEST_DATA_DATE:
        extended_start = EARLIEST_DATA_DATE
        remaining_days = (user_start - extended_start).days
        estimated_trading_days = int(remaining_days / 1.4)  # Rough calendar-to-trading conversion
        if estimated_trading_days < ma_period:
            print(f"[Warning] Limited historical data before {user_start.strftime('%Y-%m-%d')}. "
                  f"Only ~{estimated_trading_days} trading days available for MA calculation. "
                  f"MA line may not be visible until later in the chart.")
    
    extended_start_str = extended_start.strftime("%Y-%m-%d")
    
    print(f"[Info] Fetching data from {extended_start_str} to {end} "
          f"(extended by {ma_period} trading days for MA calculation)")
    
    # Download data with extended range
    close = download_data(extended_start_str, end)
    
    # Build returns on full data
    r_stock, stock_nav, stock_nav_1x = build_stock_returns(close, leverage)
    r_gold, gold_nav = build_gold_returns(close)
    
    # Generate signal and MA on full data (so MA is calculated with history)
    signal, stock_ma = generate_signal(stock_nav, ma_period)
    
    # Execute strategy on full data
    r_strategy = pd.Series(
        np.where(signal, r_stock, r_gold),
        index=close.index
    )
    nav_full = (1 + r_strategy).cumprod()
    
    # Calculate S&P 500 NAV on full data
    sp500_nav_full = (1 + close["^GSPC"].pct_change(fill_method=None).fillna(0)).cumprod()
    
    # Trim all series to user's requested date range for display
    # Find the actual start date in the index (may not exactly match user's input)
    valid_dates = close.index[close.index >= user_start]
    if len(valid_dates) == 0:
        raise RuntimeError(f"No data available for the specified date range starting from {start}")
    actual_start = valid_dates[0]
    
    # Trim all series
    nav = nav_full.loc[actual_start:]
    r_strategy_trimmed = r_strategy.loc[actual_start:]
    stock_nav = stock_nav.loc[actual_start:]
    stock_nav_1x = stock_nav_1x.loc[actual_start:]
    gold_nav = gold_nav.loc[actual_start:]
    stock_ma = stock_ma.loc[actual_start:]
    signal = signal.loc[actual_start:]
    sp500_nav = sp500_nav_full.loc[actual_start:]
    
    # Normalize NAVs to start at 1.0 from the user's start date
    # Apply the same scale factor to MA so it aligns with normalized stock_nav
    stock_nav_scale = stock_nav.iloc[0]
    nav = nav / nav.iloc[0]
    stock_nav = stock_nav / stock_nav_scale
    stock_nav_1x = stock_nav_1x / stock_nav_1x.iloc[0]
    gold_nav = gold_nav / gold_nav.iloc[0]
    sp500_nav = sp500_nav / sp500_nav.iloc[0]
    stock_ma = stock_ma / stock_nav_scale  # Apply same scale as stock_nav
    
    # Calculate metrics on trimmed data
    metrics = calculate_all_metrics(nav, r_strategy_trimmed)
    annual_returns = calculate_annual_returns(nav)
    sp500_annual_returns = calculate_annual_returns(sp500_nav)
    
    # Data availability info
    data_info = {}
    for ticker in TICKERS:
        if ticker in close.columns:
            first = close[ticker].first_valid_index()
            last = close[ticker].last_valid_index()
            if first is not None and last is not None:
                data_info[ticker] = f"{first.strftime('%Y-%m-%d')} to {last.strftime('%Y-%m-%d')}"
            else:
                data_info[ticker] = "No data available for this period"
    
    # Calculate new analytics
    drawdown_series = calculate_drawdown_series(nav)
    rolling_sharpe = calculate_rolling_sharpe(r_strategy)
    recovery_days = calculate_recovery_days(nav)
    
    return BacktestResult(
        nav=nav,
        metrics=metrics,
        annual_returns=annual_returns,
        sp500_annual_returns=sp500_annual_returns,
        data_info=data_info,
        stock_nav=stock_nav,
        stock_nav_1x=stock_nav_1x,
        gold_nav=gold_nav,
        stock_ma=stock_ma,
        sp500_nav=sp500_nav,
        signal=signal,
        drawdown_series=drawdown_series,
        rolling_sharpe=rolling_sharpe,
        recovery_days=recovery_days
    )

# =========================================================================
# CLI Entry Point
# =========================================================================

if __name__ == "__main__":
    print("Running backtest...")
    result = run_backtest()
    
    print("\n===== LRS Financial Metrics =====")
    print(f"Period: {result.metrics['start_date']} → {result.metrics['end_date']}")
    print("-" * 35)
    print(f"Final NAV  : {result.metrics['final_nav']:,.2f}")
    print(f"CAGR       : {result.metrics['cagr']*100:.2f}%")
    print(f"Volatility : {result.metrics['volatility']*100:.2f}%")
    print(f"Sharpe     : {result.metrics['sharpe']:.2f}")
    print(f"Sortino    : {result.metrics['sortino']:.2f}")
    print(f"Max DD     : {result.metrics['max_drawdown']*100:.2f}%")
    print(f"Win Rate   : {result.metrics['win_rate']*100:.2f}%")
    print(f"Calmar     : {result.metrics['calmar']:.2f}")
    print("=" * 35)
