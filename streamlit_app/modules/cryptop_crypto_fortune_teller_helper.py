# cryptop_crypto_fortune_teller_helper.py
import pandas as pd
import numpy as np
from pycoingecko import CoinGeckoAPI
import streamlit as st
import requests
from requests.adapters import HTTPAdapter, Retry
import time
import concurrent.futures
import re
import ccxt

# Initialize CoinGecko client (public demo API)
cg = CoinGeckoAPI()
cg.request_timeout = 20
cg.request_timeout = 20  #Enforce timeout to prevent hanging

def get_session():
    """
    Technical Improvement 1: Create a robust requests Session with retries and backoff
    to handle intermittent API failures.
    """
    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5, status_forcelist=[429, 500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

# Global robust session
req_session = get_session()

# Technical Improvement 1: Attach robust session to PyCoinGecko client
cg.session = req_session

# Replace cg direct requests to have retry wrapping where manual
def cg_retry_call(func, *args, retries=3, delay=1, **kwargs):
    for attempt in range(retries):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(delay * (attempt + 1))
            else:
                raise e


#Prevent Timedelta Overflow (DoS)
# pandas Timedelta limit is ~106,752 days.
MAX_HISTORY_DAYS = 20000


def downcast_dtypes(df):
    """
    Technical Improvement 3: Memory Optimization
    Downcasts numerical columns to float32 to save memory, especially critical
    for large batch historical data fetching.
    """
    fcols = df.select_dtypes('float').columns
    icols = df.select_dtypes('integer').columns
    for col in fcols:
        df[col] = pd.to_numeric(df[col], downcast='float')
    for col in icols:
        df[col] = pd.to_numeric(df[col], downcast='integer')
    return df

def validate_coin_id(coin_id):
    """
    Validate coin_id to ensure it only contains safe characters.
    Valid characters: a-z, 0-9, -, ., _
    """
    if not isinstance(coin_id, str):
        return False
    # Alphanumeric, hyphen, dot, underscore are standard in CoinGecko IDs
    # Blocks path traversal (/) and script injection (<>)
    if not re.match(r'^[a-z0-9\-\._]+$', coin_id):
        return False
    return True

@st.cache_data(ttl=86400) # Cache list for 24 hours
def get_coin_list():
    """
    Fetch list of all supported coins from CoinGecko.
    Returns a DataFrame with columns [id, symbol, name].
    """
    try:
        coins = cg_retry_call(cg.get_coins_list)  # get list of coins with id, symbol, name
        df_coins = pd.DataFrame(coins)
        return df_coins
    except Exception as e:
        st.error(f"Error fetching coin list: {e}")
        return pd.DataFrame(columns=['id', 'symbol', 'name'])

@st.cache_data(ttl=3600) # Cache prices for 1 hour
def _fetch_historical_prices_cached(coin_id, vs_currency='usd', days='max'):
    """
    Internal cached function to fetch historical market data (prices) for a coin.
    Uses 'days' as a resolution bucket (1, 90, or 'max') to optimize caching.
    """
    try:
        #Pass timeout to prevent hanging if supported by wrapper
        # Using 3 seconds timeout
        try:
             data = cg_retry_call(cg.get_coin_market_chart_by_id, id=coin_id, vs_currency=vs_currency, days=days, timeout=3)
        except TypeError:
             # Fallback if timeout kwarg is not supported, or use direct request
             # Since we know wrapper is old or custom, we force direct request here to be safe
             url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
             params = {'vs_currency': vs_currency, 'days': days}
             r = req_session.get(url, params=params, timeout=5)
             r.raise_for_status()
             data = r.json()

        # 'prices' is list of [timestamp, price]
        prices = data.get('prices', [])
        df = pd.DataFrame(prices, columns=['timestamp', 'close'])
        # convert ms timestamp to datetime
        df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
        df = df.set_index('date')
        df = df[['close']]
        return df
    except Exception as e:
        st.error(f"Error fetching historical prices: {e}")
        return pd.DataFrame()

def get_historical_prices(coin_id, vs_currency='usd', days=365):
    """
    Fetch historical market data (prices) for a coin.
    Returns DataFrame with date index and 'close' prices.
    Implements a Tiered Caching Strategy (Bucket 1, 90, or Max) to preserve resolution.
    """
    #Validate coin_id
    if not validate_coin_id(coin_id):
        st.error(f"Invalid coin ID: {coin_id}")
        return pd.DataFrame()

    # Determine cache bucket to preserve resolution
    try:
        days_val = float(days)
    except (ValueError, TypeError):
        days_val = 99999 # Treat as max

    # Tier 1: 1 day (5 min resolution)
    if days_val <= 1:
        fetch_days = 1
    # Tier 2: 90 days (Hourly resolution)
    elif days_val <= 90:
        fetch_days = 90
    # Tier 3: Max (>90 days) (Daily resolution)
    else:
        fetch_days = 'max'

    # Fetch from cached tier
    df = _fetch_historical_prices_cached(coin_id, vs_currency, days=fetch_days)

    if df.empty:
        return df

    # Return full df if 'max' requested or if we are using exact bucket
    if days == 'max':
        return df

    try:
        days_int = float(days)
        #Check bounds to prevent Timedelta overflow/underflow crash
        if days_int > MAX_HISTORY_DAYS or days_int < 0:
            return df
    except (ValueError, TypeError):
        # Fallback if days cannot be converted to number, return full history
        return df

    # Slice the dataframe to the requested number of days
    # Use UTC for consistency as CoinGecko timestamps are UTC based.
    # df['date'] (index) is naive UTC.
    try:
        cutoff_date = pd.Timestamp.now('UTC').replace(tzinfo=None) - pd.Timedelta(days=days_int)
        return df[df.index >= cutoff_date]
    except (pd.errors.OutOfBoundsTimedelta, OverflowError, ValueError):
        # Fallback for any other overflow issues
        return df

@st.cache_data(ttl=3600)
def _fetch_historical_ohlc_cached(coin_id, vs_currency='usd', days='max'):
    """
    Internal cached function to fetch historical OHLC data for a coin.
    Uses 'days' as a resolution bucket (1, 30, or 'max') to optimize caching.
    """
    try:
        ohlc_data = cg_retry_call(cg.get_coin_ohlc_by_id, id=coin_id, vs_currency=vs_currency, days=days)
        df = pd.DataFrame(ohlc_data, columns=['timestamp','open','high','low','close'])
        df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
        df = df.set_index('date')
        df = df[['open','high','low','close']]
        return df
    except Exception as e:
        st.error(f"Error fetching OHLC data: {e}")
        return pd.DataFrame()

def get_historical_ohlc(coin_id, vs_currency='usd', days=30):
    """
    Fetch historical OHLC data for a coin.
    Returns DataFrame with date index and columns ['open','high','low','close'].
    Implements a Tiered Caching Strategy (Bucket 1, 30, or Max) to preserve resolution while minimizing API calls.
    """
    #Validate coin_id
    if not validate_coin_id(coin_id):
        st.error(f"Invalid coin ID: {coin_id}")
        return pd.DataFrame()

    # Determine cache bucket to preserve resolution
    try:
        days_val = float(days)
    except (ValueError, TypeError):
        days_val = 99999 # Treat as max

    # Tier 1: 1 day (30 min resolution)
    if days_val <= 1:
        fetch_days = 1
    # Tier 2: 30 days (4 hour resolution)
    elif days_val <= 30:
        fetch_days = 30
    # Tier 3: Max (>30 days) (4 day resolution)
    else:
        #Public API limits OHLC to 365 days.
        # Use '365' instead of 'max' to prevent 400 Bad Request.
        fetch_days = 365

    # Fetch from cached tier
    df = _fetch_historical_ohlc_cached(coin_id, vs_currency, days=fetch_days)

    if df.empty:
        return df

    # Return full df if 'max' requested (implicitly capped at 365 now)
    if days == 'max':
        return df

    #Check bounds for days_val (which is already float or max)
    if days_val > MAX_HISTORY_DAYS or days_val < 0:
        return df

    # Slice the dataframe to the requested number of days
    try:
        cutoff_date = pd.Timestamp.now('UTC').replace(tzinfo=None) - pd.Timedelta(days=days_val)
        return df[df.index >= cutoff_date]
    except (pd.errors.OutOfBoundsTimedelta, OverflowError, ValueError):
        return df

@st.cache_data
def compute_volatility(df, window=14):
    """
    Compute volatility indicators: rolling standard deviation and Average True Range (ATR).
    Returns DataFrame with columns ['rolling_std', 'ATR'].
    ATR is calculated using high, low, and previous close (Welles Wilder method).
    """
    if 'close' not in df or df.empty:
         return pd.DataFrame()

    vol = pd.DataFrame(index=df.index)
    vol['rolling_std'] = df['close'].rolling(window).std()
    # Compute ATR if high/low available
    if 'high' in df and 'low' in df:
        # Optimization: Use numpy for element-wise operations instead of pandas concat/apply
        #Replaced pd.concat(...).max(axis=1) with np.fmax
        # Speedup: ~2.8x faster
        h = df['high'].values.astype(float)
        l = df['low'].values.astype(float)
        c = df['close'].values.astype(float)

        # High - Low
        hl = h - l

        # Shifted Close (equivalent to df['close'].shift(1))
        prev_c = np.empty_like(c)
        prev_c[1:] = c[:-1]
        prev_c[0] = np.nan  # First element is NaN

        # Calculate True Range components
        h_pc = np.abs(h - prev_c)
        l_pc = np.abs(l - prev_c)

        # True Range is max(High-Low, |High-PrevClose|, |Low-PrevClose|)
        # np.fmax ignores NaNs, matching pandas behavior for this case
        tr_values = np.fmax(hl, np.fmax(h_pc, l_pc))

        # Convert back to Series for rolling mean
        tr_series = pd.Series(tr_values, index=df.index)
        vol['ATR'] = tr_series.rolling(window).mean()
    else:
        vol['ATR'] = np.nan
    return vol

def check_risk_level(df):
    """
    Analyze volatility and return a risk warning if applicable.
    Returns string (message) or None.
    """
    if df.empty or len(df) < 15:
        return None

    # Calculate volatility
    vol_data = compute_volatility(df, window=14)
    if vol_data.empty:
        return None

    rolling_std = vol_data['rolling_std']
    current_vol = rolling_std.iloc[-1]
    avg_vol = rolling_std.mean()

    # Thresholds: If current volatility is > 2x average, it's High Risk
    if current_vol > 2 * avg_vol:
        return "⚠️ High Volatility Detected: Market is extremely turbulent. Prices may fluctuate wildly."
    elif current_vol > 1.5 * avg_vol:
        return "⚠️ Elevated Volatility: Caution advised."

    return None

def generate_trading_signal(current_price, forecast_df):
    """
    Generate a Buy/Sell signal based on forecast vs current price.
    Returns string signal and color.
    """
    if forecast_df.empty or 'yhat' not in forecast_df.columns:
        return "N/A", "gray"

    # Get last forecasted price
    target_price = forecast_df['yhat'].iloc[-1]

    if current_price == 0:
        return "N/A", "gray"

    pct_change = ((target_price - current_price) / current_price) * 100

    if pct_change > 20:
        return "STRONG BUY", "#00FF00" # Green
    elif pct_change > 5:
        return "BUY", "#90EE90" # Light Green
    elif pct_change < -20:
        return "STRONG SELL", "#FF0000" # Red
    elif pct_change < -5:
        return "SELL", "#FF6347" # Tomato
    else:
        return "HOLD", "#FFFF00" # Yellow

@st.cache_data(ttl=3600)
def get_coin_metrics(coin_id):
    """
    Fetch additional metrics for a coin: community and developer data.
    Uses CoinGecko API to get community (social) and developer stats.
    """
    #Validate coin_id
    if not validate_coin_id(coin_id):
        return {}

    try:
        data = cg_retry_call(cg.get_coin_by_id, id=coin_id, localization='false', tickers='false', market_data='false', community_data='true', developer_data='true', sparkline='false')
        comm = data.get('community_data', {}) or {}
        dev = data.get('developer_data', {}) or {}
        metrics = {
            'twitter_followers': comm.get('twitter_followers'),
            'reddit_subscribers': comm.get('reddit_subscribers'),
            'reddit_active_48h': comm.get('reddit_accounts_active_48h'),
            'reddit_avg_posts_48h': comm.get('reddit_average_posts_48h'),
            'reddit_avg_comments_48h': comm.get('reddit_average_comments_48h'),
            'total_issues': dev.get('total_issues'),
            'closed_issues': dev.get('closed_issues'),
            'pull_requests_merged': dev.get('pull_requests_merged'),
            'pr_contributors': dev.get('pull_request_contributors'),
            'forks': dev.get('forks'),
            'stars': dev.get('stars'),
            'subscribers': dev.get('subscribers'),
            'sentiment_up_pct': comm.get('sentiment_votes_up_percentage'),
            'sentiment_down_pct': comm.get('sentiment_votes_down_percentage')
        }
        return metrics
    except Exception as e:
        st.error(f"Error fetching coin metrics: {e}")
        return {}

@st.cache_data(ttl=60)
def get_coin_market_data(coin_id):
    """
    Fetch market data for a specific coin (price, circulating supply).
    """
    #Validate coin_id
    if not validate_coin_id(coin_id):
        return {}

    try:
        data = cg_retry_call(cg.get_coin_by_id, id=coin_id, localization='false', tickers='false', market_data='true', community_data='false', developer_data='false', sparkline='false')
        market_data = data.get('market_data', {})
        if not market_data:
            return {}

        return {
            'current_price': market_data.get('current_price', {}).get('usd'),
            'circulating_supply': market_data.get('circulating_supply')
        }
    except Exception as e:
        st.error(f"Error fetching coin market data: {e}")
        return {}

@st.cache_data(ttl=3600)
def get_fear_and_greed_index():
    """
    Fetch the Crypto Fear & Greed Index from alternative.me.
    """
    url = "https://api.alternative.me/fng/"
    try:
        #Added User-Agent, extended timeout, and status check
        headers = {'User-Agent': 'CryptoPsFortuneTeller/1.0'}
        r = req_session.get(url, headers=headers, timeout=20)
        r.raise_for_status()
        data = r.json()
        if data.get('data'):
            item = data['data'][0]
            return {
                'value': item['value'],
                'classification': item['value_classification'],
                'timestamp': item['timestamp']
            }
        return None
    except Exception as e:
        st.error(f"Error fetching Fear & Greed Index: {e}")
        return None

@st.cache_data
def calculate_rsi(df, period=14):
    """Calculate RSI for a given DataFrame with a 'close' column."""
    if 'close' not in df:
        return pd.Series(dtype=float)

    delta = df['close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    # Use Wilder's Smoothing (EMA with alpha=1/period)
    avg_gain = gain.ewm(alpha=1/period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/period, adjust=False).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

@st.cache_data
def calculate_macd(df, short_window=12, long_window=26, signal_window=9):
    """Calculate MACD, Signal, and Histogram."""
    if 'close' not in df:
        return pd.DataFrame()

    exp1 = df['close'].ewm(span=short_window, adjust=False).mean()
    exp2 = df['close'].ewm(span=long_window, adjust=False).mean()
    macd = exp1 - exp2
    signal = macd.ewm(span=signal_window, adjust=False).mean()
    hist = macd - signal
    return pd.DataFrame({'MACD': macd, 'Signal': signal, 'Histogram': hist})

@st.cache_data
def calculate_bollinger_bands(df, window=20, num_std=2):
    """Calculate Bollinger Bands."""
    if 'close' not in df:
        return pd.DataFrame()

    sma = df['close'].rolling(window=window).mean()
    std = df['close'].rolling(window=window).std()
    upper = sma + (std * num_std)
    lower = sma - (std * num_std)
    return pd.DataFrame({'B_Upper': upper, 'B_Lower': lower, 'SMA': sma})

@st.cache_data(ttl=3600)
def get_trending_coins():
    """
    Fetch top 7 trending coins on CoinGecko.
    """
    try:
        trending = cg_retry_call(cg.get_search_trending)
        return trending.get('coins', [])
    except Exception as e:
        st.error(f"Error fetching trending coins: {e}")
        return []

@st.cache_data(ttl=60)
def get_current_price(coin_ids, vs_currencies='usd,eur,btc,eth'):
    """
    Fetch current prices for a list of coin IDs.
    """
    if isinstance(coin_ids, list):
        coin_ids = ','.join(coin_ids)
    try:
        prices = cg_retry_call(cg.get_price, ids=coin_ids, vs_currencies=vs_currencies)
        return prices
    except Exception as e:
        st.error(f"Error fetching prices: {e}")
        return {}

@st.cache_data
def calculate_backtest(df, strategy_type='SMA Crossover'):
    """
    Perform a simple backtest on the provided DataFrame.
    Returns the dataframe with returns and a metrics dictionary.
    """
    if df.empty or 'close' not in df.columns:
        return pd.DataFrame(), {}

    df = df.copy()
    # Initialize signal series with 0.0 (Neutral)
    signal_series = pd.Series(0.0, index=df.index)

    # 1. Generate Signals
    if strategy_type == 'SMA Crossover':
        # Simple Moving Average Crossover (Golden Cross)
        short_window = 20
        long_window = 50
        df['short_mavg'] = df['close'].rolling(window=short_window, min_periods=1).mean()
        df['long_mavg'] = df['close'].rolling(window=long_window, min_periods=1).mean()

        # Create signal: 1 when short > long, else 0
        signal_series = pd.Series(np.where(df['short_mavg'] > df['long_mavg'], 1.0, 0.0), index=df.index)

    elif strategy_type == 'RSI Mean Reversion':
        # Buy if RSI < 30, Sell if RSI > 70
        rsi = calculate_rsi(df)

        # Vectorized approach using masking and forward fill
        signal_series = pd.Series(
            np.select([rsi < 30, rsi > 70], [1.0, 0.0], default=np.nan),
            index=rsi.index
        )

        # Forward fill to propagate the last active signal
        signal_series = signal_series.ffill().fillna(0.0)

    elif strategy_type == 'Bollinger Band Squeeze':
        # Buy when price breaks above upper band, Sell when price breaks below lower band
        bb = calculate_bollinger_bands(df)
        if not bb.empty:
            df = df.join(bb)
            # Breakout signals
            signal_series = pd.Series(
                np.select([df['close'] > df['B_Upper'], df['close'] < df['B_Lower']], [1.0, 0.0], default=np.nan),
                index=df.index
            )
            # Forward fill
            signal_series = signal_series.ffill().fillna(0.0)

    elif strategy_type == 'VWAP Reversion':
        # Buy when price dips 5% below VWAP, Sell when price crosses above VWAP
        # Technical Improvement 4: VWAP Reversion Strategy
        vwap = calculate_vwap(df)
        if not vwap.empty:
            df['vwap'] = vwap
            # Threshold: 5% below VWAP
            buy_threshold = df['vwap'] * 0.95
            signal_series = pd.Series(
                np.select([df['close'] < buy_threshold, df['close'] > df['vwap']], [1.0, 0.0], default=np.nan),
                index=df.index
            )
            # Forward fill
            signal_series = signal_series.ffill().fillna(0.0)

    elif strategy_type == 'MACD Crossover':
        # Buy when MACD crosses above Signal, Sell when MACD crosses below Signal
        macd = calculate_macd(df)
        if not macd.empty:
            df = df.join(macd)
            signal_series = pd.Series(np.where(df['MACD'] > df['Signal'], 1.0, 0.0), index=df.index)

    # 2. Calculate Returns
    # Market Returns
    df['returns'] = df['close'].pct_change()

    # Add signal to output df for visualization
    df['signal'] = signal_series

    # Strategy Returns = Position(t-1) * Return(t)
    df['strategy_returns'] = df['signal'].shift(1) * df['returns']

    # 3. Metrics
    # Fill NaN (first row) with 0
    df['strategy_returns'] = df['strategy_returns'].fillna(0)
    df['returns'] = df['returns'].fillna(0)

    df['cumulative_market_returns'] = (1 + df['returns']).cumprod()
    df['cumulative_strategy_returns'] = (1 + df['strategy_returns']).cumprod()

    total_return = df['cumulative_strategy_returns'].iloc[-1] - 1
    market_return = df['cumulative_market_returns'].iloc[-1] - 1

    metrics = {
        'Total Return': total_return,
        'Market Return': market_return
    }

    return df, metrics

@st.cache_data(ttl=3600)
def get_batch_historical_prices(coin_ids: list, days: int = 90) -> pd.DataFrame:
    """
    Fetch historical prices for multiple coins and return a combined DataFrame.
    Uses concurrent requests to speed up fetching.
    """
    #Limit batch size to prevent API abuse/DoS
    MAX_BATCH_SIZE = 10

    if not coin_ids:
        return pd.DataFrame()

    # Ensure list and deduplicate to prevent redundant API calls
    if not isinstance(coin_ids, list):
        coin_ids = list(coin_ids)

    # Deduplicate while preserving order (Python 3.7+ dicts preserve insertion order)
    coin_ids = list(dict.fromkeys(coin_ids))

    if len(coin_ids) > MAX_BATCH_SIZE:
        st.warning(f"⚠️ Security Limit: Request truncated to first {MAX_BATCH_SIZE} unique assets to prevent API rate limit exhaustion.")
        coin_ids = coin_ids[:MAX_BATCH_SIZE]

    dfs = []

    def fetch_price(cid):
        try:
            # Re-use existing function which is cached and handles its own errors
            df = get_historical_prices(cid, days=days)
            if not df.empty:
                df = df.rename(columns={'close': cid})
                return df
        except Exception:
            logging.error(f"Failed to fetch price for {cid}", exc_info=True)
        return None

    # Use ThreadPoolExecutor for concurrent requests
    # Limit max_workers to avoid hitting rate limits too hard
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        # map returns an iterator that yields results in the order calls were submitted
        results = executor.map(fetch_price, coin_ids)
        dfs = [df for df in results if df is not None]

    if not dfs:
        return pd.DataFrame()

    # Concatenate all at once along columns (axis=1)
    # Technical Improvement 3: Optimize memory footprint before concatenation
    dfs = [downcast_dtypes(d) for d in dfs]
    combined_df = pd.concat(dfs, axis=1, join='outer')
    return downcast_dtypes(combined_df)

# --- NEW FEATURES ---

@st.cache_data
def calculate_adx(df, period=14):
    """
    Calculate Average Directional Index (ADX).
    Requires 'high', 'low', 'close'.
    """
    if not all(col in df.columns for col in ['high', 'low', 'close']):
        return pd.Series(dtype=float)

    # +DM, -DM
    high_diff = df['high'].diff()
    low_diff = -df['low'].diff()

    plus_dm = np.where((high_diff > low_diff) & (high_diff > 0), high_diff, 0.0)
    minus_dm = np.where((low_diff > high_diff) & (low_diff > 0), low_diff, 0.0)

    # TR
    tr = compute_volatility(df, window=1)['ATR'] # ATR with window 1 is basically TR (if correctly implemented)
    # Actually, let's recalculate TR explicitly to be safe and avoid circular dep issues on windowing
    h = df['high'].values.astype(float)
    l = df['low'].values.astype(float)
    c = df['close'].values.astype(float)

    prev_c = np.empty_like(c)
    prev_c[1:] = c[:-1]
    prev_c[0] = np.nan

    hl = h - l
    h_pc = np.abs(h - prev_c)
    l_pc = np.abs(l - prev_c)

    tr_vals = np.fmax(hl, np.fmax(h_pc, l_pc))
    tr = pd.Series(tr_vals, index=df.index)

    # Smooth TR, +DM, -DM
    tr_smooth = tr.rolling(period).sum()
    plus_dm_smooth = pd.Series(plus_dm, index=df.index).rolling(period).sum()
    minus_dm_smooth = pd.Series(minus_dm, index=df.index).rolling(period).sum()

    # +DI, -DI
    plus_di = 100 * (plus_dm_smooth / tr_smooth)
    minus_di = 100 * (minus_dm_smooth / tr_smooth)

    # DX
    dx = 100 * (abs(plus_di - minus_di) / (plus_di + minus_di))

    # ADX
    adx = dx.rolling(period).mean()

    return pd.DataFrame({'ADX': adx, '+DI': plus_di, '-DI': minus_di})

@st.cache_data
def calculate_cci(df, period=20):
    """
    Calculate Commodity Channel Index (CCI).
    """
    if not all(col in df.columns for col in ['high', 'low', 'close']):
        return pd.Series(dtype=float)

    tp = (df['high'] + df['low'] + df['close']) / 3
    sma_tp = tp.rolling(period).mean()

    #Vectorized MAD calculation using numpy sliding_window_view
    # Speedup: ~30x faster than pd.rolling().apply()
    from numpy.lib.stride_tricks import sliding_window_view
    tp_vals = tp.values
    padded_tp = np.pad(tp_vals, (period - 1, 0), constant_values=np.nan)
    if len(padded_tp) >= period:
        windows = sliding_window_view(padded_tp, window_shape=period)
        window_means = np.nanmean(windows, axis=1, keepdims=True)
        abs_dev = np.abs(windows - window_means)
        mad_vals = np.nanmean(abs_dev, axis=1)
    else:
        mad_vals = np.full(len(tp), np.nan)

    mad = pd.Series(mad_vals, index=tp.index)

    cci = (tp - sma_tp) / (0.015 * mad)
    return cci

@st.cache_data(ttl=3600)
def get_top_gainers_losers(limit=10):
    """
    Fetch top gainers and losers from CoinGecko markets.
    """
    try:
        # Fetch top 100 coins to find gainers/losers
        data = cg_retry_call(cg.get_coins_markets, vs_currency='usd', order='market_cap_desc', per_page=100, page=1)
        df = pd.DataFrame(data)
        if df.empty:
            return pd.DataFrame(), pd.DataFrame()

        cols = ['name', 'symbol', 'current_price', 'price_change_percentage_24h', 'image']
        df = df[cols]

        gainers = df.sort_values(by='price_change_percentage_24h', ascending=False).head(limit)
        losers = df.sort_values(by='price_change_percentage_24h', ascending=True).head(limit)

        return gainers, losers
    except Exception as e:
        st.error(f"Error fetching gainers/losers: {e}")
        return pd.DataFrame(), pd.DataFrame()

def calculate_impermanent_loss(price_a_change, price_b_change):
    """
    Calculate Impermanent Loss for a 50/50 Liquidity Pool.
    Inputs are percentage changes (e.g., 50 for +50%, -10 for -10%).
    """
    # Convert pct to ratio (e.g., 50 -> 1.5)
    ratio_a = 1 + (price_a_change / 100.0)
    ratio_b = 1 + (price_b_change / 100.0)

    # Price ratio change (k)
    # If we assume standard Uniswap V2 50/50 pool logic:
    # IL = 2 * sqrt(price_ratio) / (1 + price_ratio) - 1
    # But here we have two assets changing independently.
    # The price ratio change relative to each other is what matters.
    # Let's simplify: IL is function of the price ratio divergence.
    # P_new / P_old = ratio_a / ratio_b (if we track pair A/B)

    # Correct formula for 50/50 pool holding asset A and B:
    # Value_held = 0.5 * A * ratio_a + 0.5 * B * ratio_b
    # Value_pool = sqrt(ratio_a * ratio_b)
    # IL = (Value_pool - Value_held) / Value_held

    # Actually, easier formula:
    # IL = 2 * sqrt(ratio_a * ratio_b) / (ratio_a + ratio_b) - 1

    if ratio_a + ratio_b == 0:
        return 0.0

    il = (2 * np.sqrt(ratio_a * ratio_b) / (ratio_a + ratio_b)) - 1
    return il * 100 # Percentage

@st.cache_data
def calculate_stochastic_oscillator(df, k_window=14, d_window=3):
    """
    Calculate Stochastic Oscillator (K and D).
    Requires 'high', 'low', 'close' columns.
    """
    if not all(col in df.columns for col in ['high', 'low', 'close']):
        return pd.DataFrame()

    low_min = df['low'].rolling(window=k_window).min()
    high_max = df['high'].rolling(window=k_window).max()

    k = 100 * ((df['close'] - low_min) / (high_max - low_min))
    d = k.rolling(window=d_window).mean()

    return pd.DataFrame({'%K': k, '%D': d}, index=df.index)

@st.cache_data
def calculate_ichimoku_cloud(df):
    """
    Calculate Ichimoku Cloud components.
    Requires 'high', 'low' columns.
    """
    if not all(col in df.columns for col in ['high', 'low', 'close']):
        return pd.DataFrame()

    # Conversion Line (Tenkan-sen): (9-period high + 9-period low) / 2
    period9_high = df['high'].rolling(window=9).max()
    period9_low = df['low'].rolling(window=9).min()
    tenkan_sen = (period9_high + period9_low) / 2

    # Base Line (Kijun-sen): (26-period high + 26-period low) / 2
    period26_high = df['high'].rolling(window=26).max()
    period26_low = df['low'].rolling(window=26).min()
    kijun_sen = (period26_high + period26_low) / 2

    # Leading Span A (Senkou Span A): (Conversion Line + Base Line) / 2
    senkou_span_a = ((tenkan_sen + kijun_sen) / 2).shift(26)

    # Leading Span B (Senkou Span B): (52-period high + 52-period low) / 2
    period52_high = df['high'].rolling(window=52).max()
    period52_low = df['low'].rolling(window=52).min()
    senkou_span_b = ((period52_high + period52_low) / 2).shift(26)

    # Lagging Span (Chikou Span): Close plotted 26 periods in the past
    chikou_span = df['close'].shift(-26)

    return pd.DataFrame({
        'Tenkan': tenkan_sen,
        'Kijun': kijun_sen,
        'SpanA': senkou_span_a,
        'SpanB': senkou_span_b,
        'Chikou': chikou_span
    }, index=df.index)

@st.cache_data
def calculate_pivot_points(df):
    """
    Calculate Pivot Points (Standard) based on the previous day's High, Low, Close.
    Returns a dict with pivot levels for the *current* day (projected from last full candle).
    """
    if df.empty or len(df) < 1:
        return {}

    # We take the last completed candle (assuming daily data)
    last_candle = df.iloc[-1]

    # If using current day's incomplete candle, it's an estimation.
    # For daily pivots, we typically use yesterday's HLC.
    if len(df) > 1:
        prev_candle = df.iloc[-2]
    else:
        prev_candle = last_candle

    high = prev_candle['high'] if 'high' in prev_candle else prev_candle['close']
    low = prev_candle['low'] if 'low' in prev_candle else prev_candle['close']
    close = prev_candle['close']

    pivot = (high + low + close) / 3
    r1 = (2 * pivot) - low
    s1 = (2 * pivot) - high
    r2 = pivot + (high - low)
    s2 = pivot - (high - low)
    r3 = high + 2 * (pivot - low)
    s3 = low - 2 * (high - pivot)

    return {
        'Pivot': pivot,
        'R1': r1, 'S1': s1,
        'R2': r2, 'S2': s2,
        'R3': r3, 'S3': s3
    }

@st.cache_data
def calculate_fibonacci_levels(df):
    """
    Calculate Fibonacci Retracement levels based on the visible high and low range.
    Returns a dict of levels.
    """
    if df.empty or 'high' not in df or 'low' not in df:
        return {}

    max_price = df['high'].max()
    min_price = df['low'].min()
    diff = max_price - min_price

    return {
        '0.0% (High)': max_price,
        '23.6%': max_price - 0.236 * diff,
        '38.2%': max_price - 0.382 * diff,
        '50.0%': max_price - 0.5 * diff,
        '61.8%': max_price - 0.618 * diff,
        '78.6%': max_price - 0.786 * diff,
        '100.0% (Low)': min_price
    }

@st.cache_data
def calculate_vwap(df):
    """
    Calculate Volume Weighted Average Price (VWAP).
    Since we use daily data, this will be a Rolling VWAP (e.g., 20 days) or Cumulative from start.
    We'll use a Rolling 20-day VWAP for trend analysis.
    """
    if df.empty or 'volume' not in df or 'close' not in df:
        # Try fetching volume if missing
        return pd.Series(dtype=float)

    # Typical Price = (High + Low + Close) / 3
    # If High/Low missing, use Close
    if 'high' in df and 'low' in df:
        tp = (df['high'] + df['low'] + df['close']) / 3
    else:
        tp = df['close']

    # We need volume. If it's not in the main DF (prices often don't have volume if not from OHLC),
    # we might need to rely on what's passed.
    # The get_historical_ohlc function DOES NOT return volume by default in this app's implementation
    # (see _fetch_historical_ohlc_cached).
    # If volume is missing, we can't calculate VWAP.
    if 'volume' not in df:
         return pd.Series(dtype=float)

    # Fill NA volumes if timestamps didn't perfectly align
    vol_filled = df['volume'].ffill().fillna(0)
    vp = tp * vol_filled

    # Rolling 20-day VWAP
    cum_vp = vp.rolling(20).sum()
    cum_vol = vol_filled.rolling(20).sum()

    vwap = cum_vp / cum_vol
    return vwap

@st.cache_data
def calculate_parabolic_sar(df, af=0.02, max_af=0.2):
    """
    Calculate Parabolic SAR.
    """
    if df.empty or 'high' not in df or 'low' not in df:
        return pd.Series(dtype=float)

    high = df['high'].values
    low = df['low'].values
    close = df['close'].values

    # Pre-allocate numpy array instead of pandas series for speed
    psar = np.zeros(len(df), dtype=float)

    bull = True
    af_val = af
    ep = high[0] # Extreme Point

    psar[0] = low[0] # Starting value

    for i in range(1, len(df)):
        prev_psar = psar[i-1]

        # Calculate current SAR
        curr_psar = prev_psar + af_val * (ep - prev_psar)

        # Check for reversal
        if bull:
            if low[i] < curr_psar:
                bull = False
                curr_psar = ep
                ep = low[i]
                af_val = af
            else:
                if high[i] > ep:
                    ep = high[i]
                    af_val = min(af_val + af, max_af)
                # Cap SAR at lowest of previous 2 lows
                # (Standard Wilder adjustment)
                if i > 1:
                    curr_psar = min(curr_psar, low[i-1], low[i-2])

        else: # Bear
            if high[i] > curr_psar:
                bull = True
                curr_psar = ep
                ep = high[i]
                af_val = af
            else:
                if low[i] < ep:
                    ep = low[i]
                    af_val = min(af_val + af, max_af)
                # Cap SAR at highest of previous 2 highs
                if i > 1:
                    curr_psar = max(curr_psar, high[i-1], high[i-2])

        psar[i] = curr_psar

    return pd.Series(psar, index=df.index)

def calculate_roi(initial_investment, initial_price, current_price):
    """
    Calculate Return on Investment.
    """
    if initial_price == 0:
        return 0, 0

    amount_bought = initial_investment / initial_price
    current_value = amount_bought * current_price
    profit = current_value - initial_investment

    #Prevent division by zero
    if initial_investment == 0:
        return current_value, 0.0

    roi_pct = (profit / initial_investment) * 100

    return current_value, roi_pct

def calculate_moon_math(current_price, current_supply, target_market_cap):
    """
    Calculate price required to reach a target market cap.
    """
    if current_supply == 0:
        return 0, 0 #Return tuple to match expected unpacking

    target_price = target_market_cap / current_supply

    #Prevent division by zero
    if current_price == 0:
        return 0, 0

    upside = ((target_price - current_price) / current_price) * 100
    return target_price, upside

@st.cache_data(ttl=3600)
def get_coin_market_cap_batch(limit=50):
    """
    Fetch market data for top N coins to visualize market cap.
    Used for the Market Overview visualization.
    """
    try:
        # vs_currency='usd' is default
        data = cg_retry_call(cg.get_coins_markets, vs_currency='usd', order='market_cap_desc', per_page=limit, page=1)
        df = pd.DataFrame(data)
        # We want: id, symbol, name, market_cap, current_price, price_change_percentage_24h
        return df[['id', 'symbol', 'name', 'market_cap', 'current_price', 'price_change_percentage_24h', 'total_volume']]
    except Exception as e:
        st.error(f"Error fetching market cap batch: {e}")
        return pd.DataFrame()

@st.cache_data
def detect_candlestick_patterns(df):
    """
    Feature 1: AI Pattern Recognition
    Detects Hammer, Doji, Bullish Engulfing, Bearish Engulfing patterns on the latest candles.
    """
    if df.empty or len(df) < 2:
        return []

    patterns = []

    # Get last two candles
    curr = df.iloc[-1]
    prev = df.iloc[-2]

    # Helper for body size
    def get_body(row):
        return abs(row['close'] - row['open'])

    def is_green(row):
        return row['close'] > row['open']

    curr_body = get_body(curr)
    curr_range = curr['high'] - curr['low']
    # prev_body = get_body(prev) # Unused
    # prev_range = prev['high'] - prev['low'] # Unused

    # 1. Doji: Body is very small relative to range
    if curr_range > 0 and (curr_body / curr_range) < 0.1:
        patterns.append("Doji (Indecision)")

    # 2. Hammer: Small body, long lower wick, short upper wick
    # Lower wick > 2 * body
    lower_wick = min(curr['close'], curr['open']) - curr['low']
    upper_wick = curr['high'] - max(curr['close'], curr['open'])

    if curr_body > 0 and lower_wick > (2 * curr_body) and upper_wick < (0.5 * curr_body):
         patterns.append("Hammer (Potential Reversal)")

    # 3. Bullish Engulfing: Prev red, Curr green, Curr body engulfs Prev body
    if not is_green(prev) and is_green(curr):
        if curr['close'] > prev['open'] and curr['open'] < prev['close']:
            patterns.append("Bullish Engulfing")

    # 4. Bearish Engulfing: Prev green, Curr red, Curr body engulfs Prev body
    if is_green(prev) and not is_green(curr):
        if curr['open'] > prev['close'] and curr['close'] < prev['open']:
            patterns.append("Bearish Engulfing")

    return patterns

@st.cache_data(ttl=60)
def get_exchange_arbitrage(symbol_str):
    """
    Advanced Arbitrage Matrix & Liquidity Heatmap
    Fetches prices for a symbol across major exchanges.
    Returns a complex DataFrame showing buy/sell spreads and potential alpha.
    """
    exchanges = ['binance', 'kraken', 'coinbase', 'kucoin', 'okx', 'gate', 'bybit']
    data = []

    # Normalize symbol
    symbol = symbol_str.upper()
    if '/' not in symbol:
        symbol += '/USDT' # Default to USDT pair if not specified

    def fetch_ticker(ex_name):
        import logging
        try:
            import ccxt
            exchange_class = getattr(ccxt, ex_name)
            exchange = exchange_class({'enableRateLimit': True, 'timeout': 5000})
            ticker = exchange.fetch_ticker(symbol)
            return {
                'Exchange': ex_name.capitalize(),
                'Price': ticker.get('last'),
                'Bid': ticker.get('bid'),
                'Ask': ticker.get('ask'),
                'Volume 24h': ticker.get('baseVolume', 0)
            }
        except Exception:
            logging.error("Failed to fetch ticker", exc_info=True)
            return None

    import concurrent.futures
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(exchanges)) as executor:
        results = executor.map(fetch_ticker, exchanges)
        data = [r for r in results if r and r.get('Price') is not None]

    if not data:
        return pd.DataFrame()

    df = pd.DataFrame(data)

    # Fill missing Bid/Ask with Price
    df['Bid'] = df['Bid'].fillna(df['Price'])
    df['Ask'] = df['Ask'].fillna(df['Price'])

    min_ask = df['Ask'].min()
    max_bid = df['Bid'].max()

    df['Spread %'] = ((df['Price'] - df['Price'].min()) / df['Price'].min() * 100).round(2)
    df['Alpha Potential'] = ((df['Bid'] - min_ask) / min_ask * 100).round(2)
    df['Arbitrage'] = np.where(df['Alpha Potential'] > 0, '🔥 Yes', 'No')

    df = df.sort_values(by='Price').reset_index(drop=True)
    return df

@st.cache_data(ttl=3600)
def calculate_correlation_matrix(coin_ids, days=90):
    """
    Feature 3: Correlation Matrix
    Computes the Pearson correlation matrix for the selected coins.
    """
    df = get_batch_historical_prices(coin_ids, days=days)
    if df.empty:
        return pd.DataFrame()

    # Calculate percentage change (returns)
    returns_df = df.pct_change()
    corr_matrix = returns_df.corr()
    return corr_matrix

@st.cache_data(ttl=3600)
def calculate_dca_strategy(coin_id, amount, freq_days, duration_days):
    """
    Feature 4: DCA Simulator
    Simulates Dollar Cost Averaging vs Lump Sum.
    """
    # Fetch history
    df = get_historical_prices(coin_id, days=duration_days)
    if df.empty:
        return None

    df = df.sort_index()

    # Resample to frequency
    start_date = df.index[0]
    end_date = df.index[-1]

    dca_dates = pd.date_range(start=start_date, end=end_date, freq=f'{freq_days}D')

    # Filter df to nearest dates
    dca_df = df.reindex(dca_dates, method='nearest')

    # Drop missing values and non-positive prices
    dca_df = dca_df.dropna(subset=['close'])
    dca_df = dca_df[dca_df['close'] > 0]

    if dca_df.empty:
        return None

    # Vectorized computation
    prices = dca_df['close'].values
    coins_bought = amount / prices

    total_invested = np.arange(1, len(prices) + 1) * amount
    total_coins = np.cumsum(coins_bought)
    portfolio_value = total_coins * prices

    res_df = pd.DataFrame({
        'date': dca_df.index,
        'invested': total_invested,
        'value': portfolio_value,
        'price': prices
    })

    res_df = res_df.set_index('date')

    current_price = df.iloc[-1]['close']

    # Extract scalar final values
    final_total_coins = total_coins[-1]
    final_total_invested = total_invested[-1]

    dca_final_value = final_total_coins * current_price

    # Lump Sum Comparison (invest total_invested at start)
    lump_coins = final_total_invested / df.iloc[0]['close']
    lump_final_value = lump_coins * current_price

    return {
        'dca_value': dca_final_value,
        'lump_value': lump_final_value,
        'total_invested': final_total_invested,
        'history_df': res_df
    }

@st.cache_data(ttl=3600)
def get_historical_volume(coin_id, days=30):
    """
    Fetch historical volume data.
    """
    if not validate_coin_id(coin_id):
        return pd.DataFrame()

    try:
        data = cg_retry_call(cg.get_coin_market_chart_by_id, id=coin_id, vs_currency='usd', days=days)
        volumes = data.get('total_volumes', [])
        df = pd.DataFrame(volumes, columns=['timestamp', 'volume'])
        df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
        df = df.set_index('date')
        return df[['volume']]
    except Exception:
        logging.error("Failed to get total volume", exc_info=True)
        return pd.DataFrame()

@st.cache_data(ttl=3600)
def detect_volume_anomalies(coin_id, days=30):
    """
    Feature 5: Whale Sonar
    Detects volume spikes > 2.0 * 20-day moving average.
    """
    df = get_historical_volume(coin_id, days=days)
    if df.empty:
        return pd.DataFrame()

    df['vol_ma'] = df['volume'].rolling(20).mean()
    df['anomaly'] = df['volume'] > (2.0 * df['vol_ma'])

    # Return rows with anomalies
    return df[df['anomaly']]

@st.cache_data
def calculate_black_scholes(S, K, T, r, sigma):
    """
    Calculate Black-Scholes option price for Call and Put options.
    S: Current Asset Price
    K: Strike Price
    T: Time to Expiration (in years)
    r: Risk-free Interest Rate (annual)
    sigma: Volatility (annualized)
    """
    from scipy.stats import norm
    import numpy as np

    # Handle zero/negative inputs
    if T <= 0 or S <= 0 or K <= 0 or sigma <= 0:
        return 0.0, 0.0

    d1 = (np.log(S / K) + (r + (sigma ** 2) / 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)

    call_price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    put_price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)

    return call_price, put_price
import requests
import pandas as pd
import streamlit as st
import datetime
from textblob import TextBlob
from pycoingecko import CoinGeckoAPI

cg = CoinGeckoAPI()
cg.request_timeout = 20

@st.cache_data(ttl=3600)
def get_defi_yields(limit=20):
    try:
        r = requests.get('https://yields.llama.fi/pools', timeout=10)
        r.raise_for_status()
        data = r.json().get('data', [])
        df = pd.DataFrame(data)
        if not df.empty:
            df = df[['chain', 'project', 'symbol', 'tvlUsd', 'apy', 'ilRisk']]
            df = df.sort_values(by='tvlUsd', ascending=False).head(limit)
            df['tvlUsd'] = [f"${x:,.0f}" for x in df['tvlUsd']]
            df['apy'] = [f"{x:.2f}%" if pd.notnull(x) else "N/A" for x in df['apy']]
            return df
    except Exception as e:
        logging.error(f"Error fetching DeFi yields: {e}", exc_info=True)
    return pd.DataFrame()

@st.cache_data(ttl=300)
def get_whale_alerts(coin_id="bitcoin"):
    try:
        # Simulate whale movements using CoinGecko large volume shifts if an API isn't freely available
        res = cg.get_coin_market_chart_by_id(id=coin_id, vs_currency='usd', days='1')
        vols = res['total_volumes']
        df = pd.DataFrame(vols, columns=['timestamp', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

        # Calculate moving average and find spikes
        df['vol_ma'] = df['volume'].rolling(window=12).mean() # roughly 1 hr
        df['is_whale'] = df['volume'] > (df['vol_ma'] * 2.5) # 250% spike

        whales = df[df['is_whale']].tail(10).copy()
        if not whales.empty:
            whales['volume'] = [f"${x:,.0f}" for x in whales['volume']]
            return whales[['timestamp', 'volume']].sort_values(by='timestamp', ascending=False)
    except Exception as e:
        logging.error(f"Error fetching whale alerts: {e}", exc_info=True)
    return pd.DataFrame()

@st.cache_data(ttl=1800)
def get_crypto_news_sentiment(limit=10):
    try:
        r = requests.get('https://min-api.cryptocompare.com/data/v2/news/', params={'lang': 'EN'}, timeout=10)
        r.raise_for_status()
        data = r.json().get('Data', [])[:limit]

        def process_news_item(item):
            title = item.get('title', '')
            body = item.get('body', '')
            url = item.get('url', '')
            source = item.get('source_info', {}).get('name', 'Unknown')

            # NLP Sentiment
            blob = TextBlob(title + " " + body)
            polarity = blob.sentiment.polarity

            if polarity > 0.2:
                sentiment_label = "Bullish 🚀"
            elif polarity < -0.2:
                sentiment_label = "Bearish 📉"
            else:
                sentiment_label = "Neutral 😐"

            return {
                'Source': source,
                'Title': title,
                'Sentiment': sentiment_label,
                'Score': round(polarity, 2),
                'URL': url
            }

        news_data = [process_news_item(item) for item in data]
        return pd.DataFrame(news_data)
    except Exception as e:
        logging.error(f"Error fetching news sentiment: {e}", exc_info=True)
    return pd.DataFrame()

@st.cache_data(ttl=3600)
def get_tokenomics_data(coin_id):
    try:
        data = cg.get_coin_by_id(id=coin_id, localization=False, tickers=False, market_data=True, community_data=False, developer_data=False, sparkline=False)
        md = data.get('market_data', {})

        circulating = md.get('circulating_supply', 0)
        total = md.get('total_supply', 0)
        max_supply = md.get('max_supply', 0)

        tokenomics = {
            'Circulating Supply': f"{circulating:,.0f}" if circulating else "N/A",
            'Total Supply': f"{total:,.0f}" if total else "N/A",
            'Max Supply': f"{max_supply:,.0f}" if max_supply else "Unlimited",
            'Supply Inflation Ratio': f"{(circulating / total * 100):.2f}%" if circulating and total else "N/A"
        }
        return pd.DataFrame(list(tokenomics.items()), columns=['Metric', 'Value'])
    except Exception as e:
        logging.error(f"Error fetching tokenomics: {e}", exc_info=True)
    return pd.DataFrame()
