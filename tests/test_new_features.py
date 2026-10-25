import pytest
import pandas as pd
import numpy as np
import sys
import os
from unittest.mock import MagicMock, patch

# Ensure streamlit_app is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from streamlit_app.modules.cryptop_crypto_fortune_teller_helper import (
    detect_candlestick_patterns,
    get_exchange_arbitrage,
    calculate_correlation_matrix,
    calculate_dca_strategy,
    detect_volume_anomalies,
    get_historical_volume
)

# --- Feature 1: Pattern Recognition ---
def test_detect_candlestick_patterns_doji():
    # Doji: Open ~ Close
    data = {
        'open': [100, 100],
        'high': [110, 110],
        'low': [90, 90],
        'close': [100, 100.01]
    }
    df = pd.DataFrame(data)
    patterns = detect_candlestick_patterns(df)
    assert "Doji (Indecision)" in patterns

def test_detect_candlestick_patterns_hammer():
    # Hammer: Small body, long lower wick
    # Body = 10. Upper wick = 2. Lower wick = 40.
    data = {
        'open': [100, 100],
        'high': [105, 112],
        'low': [90, 60],
        'close': [95, 110]
    }
    # Curr: Open=100, Close=110 (Green). High=112, Low=60.
    # Body = 10.
    # Lower wick = 100 - 60 = 40 (> 20).
    # Upper wick = 112 - 110 = 2 (< 5).
    # Should be Hammer.
    df = pd.DataFrame(data)
    patterns = detect_candlestick_patterns(df)
    assert "Hammer (Potential Reversal)" in patterns

# --- Feature 2: Arbitrage ---

@patch('streamlit_app.modules.cryptop_crypto_fortune_teller_helper.concurrent.futures.ThreadPoolExecutor')
def test_get_exchange_arbitrage(mock_executor_class):
    mock_executor = MagicMock()
    mock_executor_class.return_value.__enter__.return_value = mock_executor

    # Simple synchronous map
    def sync_map(fn, *iterables):
        return [fn(x) for x in iterables[0]]

    mock_executor.map.side_effect = sync_map

    # Now mock ccxt inside sys.modules
    mock_ccxt = MagicMock()
    mock_ex_binance = MagicMock()
    mock_ex_binance.fetch_ticker.return_value = {'last': 50000}
    mock_ex_kraken = MagicMock()
    mock_ex_kraken.fetch_ticker.return_value = {'last': 51000}

    mock_ccxt.binance.return_value = mock_ex_binance
    mock_ccxt.kraken.return_value = mock_ex_kraken

    mock_ccxt.coinbase.side_effect = AttributeError("Mock Error")
    mock_ccxt.kucoin.side_effect = AttributeError("Mock Error")
    mock_ccxt.okx.side_effect = AttributeError("Mock Error")
    mock_ccxt.gate.side_effect = AttributeError("Mock Error")
    mock_ccxt.bybit.side_effect = AttributeError("Mock Error")

    with patch.dict('sys.modules', {'ccxt': mock_ccxt}):
        df = get_exchange_arbitrage('BTC')

    assert not df.empty
    assert 'Exchange' in df.columns
    assert 'Spread %' in df.columns
    exchanges = df['Exchange'].values
    assert 'Binance' in exchanges
    assert 'Kraken' in exchanges

    kraken_row = df[df['Exchange'] == 'Kraken'].iloc[0]
    assert kraken_row['Spread %'] == 2.0

# --- Feature 3: Correlation ---
@patch('streamlit_app.modules.cryptop_crypto_fortune_teller_helper.get_batch_historical_prices')
def test_calculate_correlation_matrix(mock_batch):
    # Create sample data
    # BTC: Up, Down, Up
    # ETH: Up, Down, Up (Correlated)
    # SOL: Down, Up, Down (Inverse)
    data = {
        'bitcoin': [100, 110, 100, 110],
        'ethereum': [100, 110, 100, 110],
        'solana': [100, 90, 100, 90]
    }
    df = pd.DataFrame(data)
    mock_batch.return_value = df

    matrix = calculate_correlation_matrix(['bitcoin', 'ethereum', 'solana'])

    # Check correlation between returns
    assert matrix.loc['bitcoin', 'ethereum'] > 0.99
    assert matrix.loc['bitcoin', 'solana'] < -0.99

# --- Feature 4: DCA ---
@patch('streamlit_app.modules.cryptop_crypto_fortune_teller_helper.get_historical_prices')
def test_calculate_dca_strategy(mock_hist):
    # Price stays flat at $100
    dates = pd.date_range(start='2023-01-01', periods=10, freq='D')
    df = pd.DataFrame({'close': [100]*10}, index=dates)
    df['date'] = dates
    mock_hist.return_value = df

    # Invest $100 every day for 10 days
    res = calculate_dca_strategy('bitcoin', 100, 1, 10)

    # Total invested = 1000
    # Bought 1 coin each day = 10 coins
    # Value = 10 * 100 = 1000

    assert res['total_invested'] == 1000
    assert res['dca_value'] == 1000
    assert res['lump_value'] == 1000 # Lump sum at start ($100 price) buys 10 coins too

# --- Feature 5: Whale Sonar ---
@patch('streamlit_app.modules.cryptop_crypto_fortune_teller_helper.get_historical_volume')
def test_detect_volume_anomalies(mock_vol):
    dates = pd.date_range(start='2023-01-01', periods=30, freq='D')
    vols = [1000] * 29 + [5000] # Last day spike 5x
    df = pd.DataFrame({'volume': vols}, index=dates)
    mock_vol.return_value = df

    anomalies = detect_volume_anomalies('bitcoin')

    assert not anomalies.empty
    assert anomalies.iloc[-1]['volume'] == 5000
    assert len(anomalies) == 1
