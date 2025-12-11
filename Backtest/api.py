"""
Flask API for Backtest Frontend
"""
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import pandas as pd
from backtest_engine import run_backtest

app = Flask(__name__, static_folder=".", static_url_path="")
CORS(app)

@app.route("/")
def index():
    """Serve the frontend."""
    return send_from_directory(".", "index.html")

@app.route("/api/backtest", methods=["GET"])
def backtest():
    """
    Run backtest with user-specified parameters.
    
    Query params:
        start: Start date (YYYY-MM-DD), default: 1970-01-01
        end: End date (YYYY-MM-DD), default: 2025-12-07
        ma_period: Moving average period, default: 200
        leverage: Leverage multiplier, default: 3.0
    """
    try:
        # Parse parameters with defaults
        start = request.args.get("start", "1970-01-01")
        end = request.args.get("end", "2025-12-07")
        ma_period = int(request.args.get("ma_period", 200))
        leverage = float(request.args.get("leverage", 3.0))
        
        # Validate parameters
        if ma_period < 5 or ma_period > 500:
            return jsonify({"error": "ma_period must be between 5 and 500"}), 400
        if leverage < 1.0 or leverage > 5.0:
            return jsonify({"error": "leverage must be between 1.0 and 5.0"}), 400
        
        # Run backtest
        result = run_backtest(
            start=start,
            end=end,
            ma_period=ma_period,
            leverage=leverage
        )
        
        # Helper function to safely convert value (handles NaN/Inf)
        def safe_value(v):
            if pd.isna(v) or v != v:  # v != v is a NaN check
                return None
            if abs(v) == float('inf'):
                return None
            return float(v)
        
        # Prepare NAV series for chart (downsample for performance)
        nav_data = result.nav.copy()
        if len(nav_data) > 1000:
            # Resample to ~500 points for smooth chart
            nav_data = nav_data.resample("W").last()
        
        nav_series = [
            {"date": d.strftime("%Y-%m-%d"), "value": safe_value(v)}
            for d, v in nav_data.items()
        ]
        # Filter out None values
        nav_series = [p for p in nav_series if p["value"] is not None]
        
        # Prepare stock and gold NAV for comparison
        stock_data = result.stock_nav.copy()
        stock_1x_data = result.stock_nav_1x.copy()
        gold_data = result.gold_nav.copy()
        if len(stock_data) > 1000:
            stock_data = stock_data.resample("W").last()
            stock_1x_data = stock_1x_data.resample("W").last()
            gold_data = gold_data.resample("W").last()
        
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
        
        # Prepare MA series for chart
        ma_data = result.stock_ma.copy()
        if len(ma_data) > 1000:
            ma_data = ma_data.resample("W").last()
        
        ma_series = [
            {"date": d.strftime("%Y-%m-%d"), "value": safe_value(v)}
            for d, v in ma_data.items()
        ]
        # Filter out None values at the start (before MA window is filled)
        ma_series = [p for p in ma_series if p["value"] is not None]
        
        # Prepare S&P 500 series for chart
        sp500_data = result.sp500_nav.copy()
        if len(sp500_data) > 1000:
            sp500_data = sp500_data.resample("W").last()
        
        sp500_series = [
            {"date": d.strftime("%Y-%m-%d"), "value": safe_value(v)}
            for d, v in sp500_data.items()
        ]
        sp500_series = [p for p in sp500_series if p["value"] is not None]
        
        # Calculate signal zones (periods where signal is stock vs gold)
        signal_zones = []
        signal_data = result.signal.dropna()
        if len(signal_data) > 0:
            current_signal = signal_data.iloc[0]
            zone_start = signal_data.index[0]
            
            for date, sig in signal_data.items():
                if sig != current_signal:
                    # End current zone, start new one
                    signal_zones.append({
                        "start": zone_start.strftime("%Y-%m-%d"),
                        "end": date.strftime("%Y-%m-%d"),
                        "is_stock": bool(current_signal)
                    })
                    current_signal = sig
                    zone_start = date
            
            # Add last zone
            signal_zones.append({
                "start": zone_start.strftime("%Y-%m-%d"),
                "end": signal_data.index[-1].strftime("%Y-%m-%d"),
                "is_stock": bool(current_signal)
            })
        
        # Prepare drawdown series for chart
        dd_data = result.drawdown_series.copy()
        if len(dd_data) > 1000:
            dd_data = dd_data.resample("W").last()
        
        drawdown_series = [
            {"date": d.strftime("%Y-%m-%d"), "value": safe_value(v * 100)}  # Convert to percentage
            for d, v in dd_data.items()
        ]
        drawdown_series = [p for p in drawdown_series if p["value"] is not None]
        
        # Prepare rolling Sharpe series for chart
        rs_data = result.rolling_sharpe.copy()
        if len(rs_data) > 1000:
            rs_data = rs_data.resample("W").last()
        
        rolling_sharpe_series = [
            {"date": d.strftime("%Y-%m-%d"), "value": safe_value(v)}
            for d, v in rs_data.items()
        ]
        rolling_sharpe_series = [p for p in rolling_sharpe_series if p["value"] is not None]
        
        # Add recovery_days to metrics
        metrics_with_recovery = result.metrics.copy()
        metrics_with_recovery["recovery_days"] = result.recovery_days
        
        return jsonify({
            "success": True,
            "metrics": metrics_with_recovery,
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
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

if __name__ == "__main__":
    print("Starting Backtest API server...")
    print("Open http://localhost:5001 in your browser")
    app.run(host="0.0.0.0", port=5001, debug=True)
