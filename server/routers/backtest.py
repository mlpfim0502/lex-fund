"""
FastAPI Router for Backtest API
Wraps the backtest_engine for API access
"""
from fastapi import APIRouter, Query, HTTPException
from typing import Optional
import pandas as pd
from services.backtest_engine import run_backtest

router = APIRouter(prefix="/api/backtest", tags=["backtest"])


@router.get("")
async def backtest(
    start: str = Query(default="1970-01-01", description="Start date (YYYY-MM-DD)"),
    end: str = Query(default="2025-12-07", description="End date (YYYY-MM-DD)"),
    ma_period: int = Query(default=200, ge=5, le=500, description="Moving average period"),
    leverage: float = Query(default=3.0, ge=1.0, le=5.0, description="Leverage multiplier")
):
    """
    Run backtest with user-specified parameters.
    """
    try:
        result = run_backtest(
            start=start,
            end=end,
            ma_period=ma_period,
            leverage=leverage
        )
        
        def safe_value(v):
            """Handle NaN/Inf values"""
            if pd.isna(v) or v != v:
                return None
            if abs(v) == float('inf'):
                return None
            return float(v)
        
        # Downsample NAV series for performance
        nav_data = result.nav.copy()
        if len(nav_data) > 1000:
            nav_data = nav_data.resample("W").last()
        
        nav_series = [
            {"date": d.strftime("%Y-%m-%d"), "value": safe_value(v)}
            for d, v in nav_data.items()
        ]
        nav_series = [p for p in nav_series if p["value"] is not None]
        
        # Prepare comparison series
        stock_data = result.stock_nav.copy()
        stock_1x_data = result.stock_nav_1x.copy()
        gold_data = result.gold_nav.copy()
        sp500_data = result.sp500_nav.copy()
        
        if len(stock_data) > 1000:
            stock_data = stock_data.resample("W").last()
            stock_1x_data = stock_1x_data.resample("W").last()
            gold_data = gold_data.resample("W").last()
            sp500_data = sp500_data.resample("W").last()
        
        stock_series = [
            {"date": d.strftime("%Y-%m-%d"), "value": safe_value(v)}
            for d, v in stock_data.items()
        ]
        stock_series = [p for p in stock_series if p["value"] is not None]
        
        stock_1x_series = [
            {"date": d.strftime("%Y-%m-%d"), "value": safe_value(v)}
            for d, v in stock_1x_data.items()
        ]
        stock_1x_series = [p for p in stock_1x_series if p["value"] is not None]
        
        gold_series = [
            {"date": d.strftime("%Y-%m-%d"), "value": safe_value(v)}
            for d, v in gold_data.items()
        ]
        gold_series = [p for p in gold_series if p["value"] is not None]
        
        sp500_series = [
            {"date": d.strftime("%Y-%m-%d"), "value": safe_value(v)}
            for d, v in sp500_data.items()
        ]
        sp500_series = [p for p in sp500_series if p["value"] is not None]
        
        # MA series
        ma_data = result.stock_ma.copy()
        if len(ma_data) > 1000:
            ma_data = ma_data.resample("W").last()
        
        ma_series = [
            {"date": d.strftime("%Y-%m-%d"), "value": safe_value(v)}
            for d, v in ma_data.items()
        ]
        ma_series = [p for p in ma_series if p["value"] is not None]
        
        # Signal zones
        signal_zones = []
        signal_data = result.signal.dropna()
        if len(signal_data) > 0:
            current_signal = signal_data.iloc[0]
            zone_start = signal_data.index[0]
            
            for date, sig in signal_data.items():
                if sig != current_signal:
                    signal_zones.append({
                        "start": zone_start.strftime("%Y-%m-%d"),
                        "end": date.strftime("%Y-%m-%d"),
                        "is_stock": bool(current_signal)
                    })
                    current_signal = sig
                    zone_start = date
            
            signal_zones.append({
                "start": zone_start.strftime("%Y-%m-%d"),
                "end": signal_data.index[-1].strftime("%Y-%m-%d"),
                "is_stock": bool(current_signal)
            })
        
        # Drawdown series
        dd_data = result.drawdown_series.copy()
        if len(dd_data) > 1000:
            dd_data = dd_data.resample("W").last()
        
        drawdown_series = [
            {"date": d.strftime("%Y-%m-%d"), "value": safe_value(v * 100)}
            for d, v in dd_data.items()
        ]
        drawdown_series = [p for p in drawdown_series if p["value"] is not None]
        
        # Rolling Sharpe
        rs_data = result.rolling_sharpe.copy()
        if len(rs_data) > 1000:
            rs_data = rs_data.resample("W").last()
        
        rolling_sharpe_series = [
            {"date": d.strftime("%Y-%m-%d"), "value": safe_value(v)}
            for d, v in rs_data.items()
        ]
        rolling_sharpe_series = [p for p in rolling_sharpe_series if p["value"] is not None]
        
        # Add recovery_days to metrics
        metrics = result.metrics.copy()
        metrics["recovery_days"] = result.recovery_days
        
        return {
            "success": True,
            "metrics": metrics,
            "annual_returns": result.annual_returns,
            "sp500_annual_returns": result.sp500_annual_returns,
            "nav_series": nav_series,
            "stock_series": stock_series,
            "stock_1x_series": stock_1x_series,
            "gold_series": gold_series,
            "ma_series": ma_series,
            "sp500_series": sp500_series,
            "signal_zones": signal_zones,
            "drawdown_series": drawdown_series,
            "rolling_sharpe_series": rolling_sharpe_series,
            "data_info": result.data_info,
            "parameters": {
                "start": start,
                "end": end,
                "ma_period": ma_period,
                "leverage": leverage
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
