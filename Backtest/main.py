import pandas as pd
import numpy as np
import yfinance as yf
import time

start = "1920-01-01"
end   = "2025-12-07"

# 1. 下載資料（增加重試邏輯和超時設定）
tickers = ["^GSPC","^IXIC","^NDX","QQQ","TQQQ","IAU","GC=F"]

def download_with_retry(tickers, start, end, max_retries=3, timeout=60):
    """Download data with retry logic and longer timeout."""
    for attempt in range(max_retries):
        try:
            print(f"Download attempt {attempt + 1}/{max_retries}...")
            raw = yf.download(
                tickers, 
                start=start, 
                end=end, 
                auto_adjust=True,
                timeout=timeout,
                progress=True
            )
            if raw.empty:
                print(f"Warning: Downloaded data is empty (attempt {attempt + 1})")
                time.sleep(2)
                continue
            return raw
        except Exception as e:
            print(f"Download failed (attempt {attempt + 1}): {e}")
            time.sleep(2)
    
    raise RuntimeError("Failed to download data after multiple attempts")

raw = download_with_retry(tickers, start, end)

# 檢查資料是否有效
if raw.empty:
    raise RuntimeError("No data downloaded. Please check your internet connection.")

close = raw["Close"].ffill().bfill()

# 驗證每個ticker都有資料
print("\n=== Data Availability ===")
for ticker in tickers:
    if ticker in close.columns:
        valid_count = close[ticker].notna().sum()
        first_date = close[ticker].first_valid_index()
        last_date = close[ticker].last_valid_index()
        print(f"{ticker}: {valid_count} trading days ({first_date} to {last_date})")
    else:
        print(f"{ticker}: NO DATA")
print("========================\n")

# =====================================================================
# 2. 用「報酬率方式」建構股票回報序列（這樣百分百不會跳躍）
# =====================================================================

r_series = pd.Series(index=close.index, dtype=float)

# 各區段的日報酬
r_sp   = close["^GSPC"].pct_change(fill_method=None)
r_ixic = close["^IXIC"].pct_change(fill_method=None)
r_ndx  = close["^NDX"].pct_change(fill_method=None)
r_qqq  = close["QQQ"].pct_change(fill_method=None)
r_tqqq = close["TQQQ"].pct_change(fill_method=None)

# 拼貼報酬
# =====================================================================
# 正確拼接（使用年份，而不是 first_valid_index）
# =====================================================================

r_series = pd.Series(index=close.index, dtype=float)

r_series.loc["1927":"1970"] = r_sp.loc["1927":"1970"]
r_series.loc["1971":"1985"] = r_ixic.loc["1971":"1985"]
r_series.loc["1986":"1999"] = r_ndx.loc["1986":"1999"]
r_series.loc["2000":"2009"] = r_qqq.loc["2000":"2009"]
r_series.loc["2010":       ] = r_tqqq.loc["2010":]

# 缺資料補 0（表示該段停盤）
r_series = r_series.fillna(0)


# 無限值處理
r_series = r_series.replace([np.inf, -np.inf], np.nan).fillna(0)

# 模擬 3x DAILY（TQQQ 真實部分已包含 3x）
r_stock_3x = r_series * 3

# 把真實 TQQQ 期間改回真實報酬
r_stock_3x.loc["2010-01-01":] = r_tqqq.loc["2010-01-01":]

# 生成股票 NAV
stock_nav = (1 + r_stock_3x).cumprod()
stock_nav /= stock_nav.iloc[0]

# =====================================================================
# 3. 黃金報酬方式（避免價格跳）
# =====================================================================

r_gold_raw = pd.Series(index=close.index, dtype=float)
iau_start  = close["IAU"].first_valid_index()

r_gold_raw.loc[:iau_start] = close["GC=F"].pct_change(fill_method=None).loc[:iau_start]
r_gold_raw.loc[iau_start:] = close["IAU"].pct_change(fill_method=None).loc[iau_start:]

r_gold_raw = r_gold_raw.replace([np.inf, -np.inf], np.nan).fillna(0)
gold_nav = (1 + r_gold_raw).cumprod()
gold_nav /= gold_nav.iloc[0]

# =====================================================================
# 4. 200MA 訊號（昨天 vs 昨天 MA）
# =====================================================================

ma = stock_nav.rolling(200).mean()
signal = stock_nav.shift(1) > ma.shift(1)  # True=stock False=gold

# =====================================================================
# 5. 策略 NAV
# =====================================================================

r_strategy = np.where(signal, r_stock_3x, r_gold_raw)
r_strategy = pd.Series(r_strategy, index=close.index)
nav = (1 + r_strategy).cumprod()


# =====================================================================
# 7. Financial metrics（百分比 & 小數兩位）
# =====================================================================

daily_ret = r_strategy.copy()

def CAGR(series):
    years = (series.index[-1] - series.index[0]).days / 365
    return (series.iloc[-1] / series.iloc[0])**(1/years) - 1

def volatility(ret):
    return ret.std() * np.sqrt(252)

def sharpe(ret):
    vol = volatility(ret)
    return ret.mean() * 252 / vol if vol > 0 else np.nan

def sortino(ret):
    downside = ret[ret < 0].std() * np.sqrt(252)
    return ret.mean() * 252 / downside if downside > 0 else np.nan

def max_drawdown(series):
    high = series.cummax()
    dd = series / high - 1
    return dd.min()

def win_rate(ret):
    return (ret > 0).mean()

def calmar(cagr, mdd):
    return cagr / abs(mdd) if mdd < 0 else np.nan

start_date = nav.index[0].strftime("%Y-%m-%d")
end_date   = nav.index[-1].strftime("%Y-%m-%d")

# ---- 計算 ----
CAGR_val  = CAGR(nav)
MDD_val   = max_drawdown(nav)
VOL_val   = volatility(daily_ret)
SR_val    = sharpe(daily_ret)
SORT_val  = sortino(daily_ret)
WIN_val   = win_rate(daily_ret)
CAL_val   = calmar(CAGR_val, MDD_val)

# ---- 格式化 ----
def pct(x):
    return f"{x*100:.2f}%"   # 百分比格式

def num(x):
    return f"{x:.2f}"        # 小數兩位

print("\n===== LRS Financial Metrics =====")
print(f"Backtest Period : {start_date} → {end_date}")
print("--------------------------------")
print("Final NAV :", num(nav.iloc[-1]))
print("CAGR      :", pct(CAGR_val))
print("Volatility:", pct(VOL_val))
print("Sharpe    :", num(SR_val))
print("Sortino   :", num(SORT_val))
print("Max DD    :", pct(MDD_val))
print("Win Rate  :", pct(WIN_val))
print("Calmar    :", num(CAL_val))
print("=================================\n")


# =====================================================================
# 8. Annual returns (百分比、整數、一行十年、等寬對齊)
# =====================================================================

annual_nav = nav.resample("YE").last()
annual_ret = annual_nav.pct_change().dropna()
annual_pct = (annual_ret * 100).round(0).astype(int)

annual_df = annual_pct.to_frame(name="Return")
annual_df.index = annual_df.index.year

years = annual_df.index.tolist()
values = annual_df["Return"].tolist()

# 固定欄寬（可調整，如 12）
col_width = 12

print("\n===== Annual Returns (Aligned) =====")

for i in range(0, len(years), 10):
    y_slice = years[i:i+10]
    v_slice = values[i:i+10]

    row_items = []
    for y, v in zip(y_slice, v_slice):
        text = f"{y}: {v}%"
        row_items.append(text.ljust(col_width))  # 固定字寬對齊

    print("".join(row_items))

print("====================================\n")
