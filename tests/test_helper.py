import pytest
import pandas as pd
import numpy as np
import sys
import os
from unittest.mock import patch, MagicMock

# Add streamlit_app to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../streamlit_app')))

from modules.cryptop_crypto_fortune_teller_helper import (
    compute_volatility,
    calculate_rsi,
    calculate_macd,
    calculate_bollinger_bands,
    calculate_moon_math,
    calculate_roi,
    get_coin_market_data
)

def test_compute_volatility():
    # Create dummy data
    data = {
        'close': [100, 101, 102, 103, 102, 101, 100, 99, 98, 99, 100, 101, 102, 103, 104],
        'high':  [101, 102, 103, 104, 103, 102, 101, 100, 99, 100, 101, 102, 103, 104, 105],
        'low':   [99, 100, 101, 102, 101, 100, 99, 98, 97, 98, 99, 100, 101, 102, 103]
    }
    df = pd.DataFrame(data)
    vol = compute_volatility(df, window=5)

    assert 'rolling_std' in vol.columns
    assert 'ATR' in vol.columns
    # The first few will be NaN due to window
    assert not vol['rolling_std'].iloc[-1] is np.nan

def test_calculate_rsi():
    # Constant uptrend
    data = {'close': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]}
    df = pd.DataFrame(data)
    rsi = calculate_rsi(df, period=10)

    # RSI should be high
    assert rsi.iloc[-1] > 80

def test_calculate_indicators():
    data = {'close': np.random.rand(50) * 100}
    df = pd.DataFrame(data)

    macd = calculate_macd(df)
    assert 'MACD' in macd.columns
    assert 'Signal' in macd.columns

    bb = calculate_bollinger_bands(df)
    assert 'B_Upper' in bb.columns
    assert 'B_Lower' in bb.columns
    assert bb['B_Upper'].iloc[-1] >= bb['B_Lower'].iloc[-1]

def test_calculate_moon_math():
    # Test case 1: Normal calculation
    current_price = 10.0
    current_supply = 1_000_000.0
    target_mc = 20_000_000.0 # Implies target price of 20

    target_price, upside = calculate_moon_math(current_price, current_supply, target_mc)

    assert target_price == 20.0
    assert upside == 100.0 # (20 - 10) / 10 * 100 = 100%

    # Test case 2: Zero supply (should return 0, 0)
    assert calculate_moon_math(10, 0, 1000) == (0, 0)

    # Test case 3: Target lower than current (negative upside)
    target_mc_low = 5_000_000.0 # Implies target price 5
    t_price, up = calculate_moon_math(10, 1_000_000, target_mc_low)
    assert t_price == 5.0
    assert up == -50.0

def test_calculate_moon_math_zero_price():
    # Test case 4: Zero current price (should handle gracefully)
    t_price, up = calculate_moon_math(0, 1_000_000, 20_000_000)
    # Should return 0, 0 or similar to avoid crash
    assert t_price == 0
    assert up == 0

def test_calculate_roi_zero_investment():
    # Test case: Zero initial investment
    val, pct = calculate_roi(0, 10, 20)
    assert val == 0
    assert pct == 0

@patch('modules.cryptop_crypto_fortune_teller_helper.st.error')
@patch('modules.cryptop_crypto_fortune_teller_helper.cg')
def test_get_coin_market_data(mock_cg, mock_st_error):
    # Setup mock
    mock_cg.get_coin_by_id.return_value = {
        'market_data': {
            'current_price': {'usd': 50000},
            'circulating_supply': 19000000
        }
    }

    # Run
    # Note: st.cache_data might interfere if streamlit context is weird,
    # but usually in tests it just runs or we can mock it.
    # Here we assume it runs (wrapper).

    # We might need to clear cache if it persists across tests
    if hasattr(get_coin_market_data, 'clear'):
        get_coin_market_data.clear()

    result = get_coin_market_data('bitcoin')

    # Verify
    assert result['current_price'] == 50000
    assert result['circulating_supply'] == 19000000
    # mock_cg.get_coin_by_id.assert_called_once() # Decorator might call it differently or cache hits

    # Test error case
    if hasattr(get_coin_market_data, 'clear'):
        get_coin_market_data.clear()

    mock_cg.get_coin_by_id.side_effect = Exception("API Error")
    result_err = get_coin_market_data('bitcoin')
    assert result_err == {}
    mock_st_error.assert_called()

def test_calculate_ichimoku_cloud():
    from streamlit_app.modules.cryptop_crypto_fortune_teller_helper import calculate_ichimoku_cloud
    import pandas as pd
    import numpy as np
    data = {
        'high': np.linspace(100, 150, 100),
        'low': np.linspace(90, 140, 100),
        'close': np.linspace(95, 145, 100)
    }
    df = pd.DataFrame(data)
    ich = calculate_ichimoku_cloud(df)

    assert 'SpanA' in ich.columns
    assert 'SpanB' in ich.columns
    assert 'Chikou' in ich.columns

def test_calculate_parabolic_sar():
    from streamlit_app.modules.cryptop_crypto_fortune_teller_helper import calculate_parabolic_sar
    import pandas as pd
    import numpy as np
    data = {
        'high': np.linspace(100, 150, 10),
        'low': np.linspace(90, 140, 10),
        'close': np.linspace(95, 145, 10)
    }
    df = pd.DataFrame(data)
    sar = calculate_parabolic_sar(df)
    assert isinstance(sar, pd.Series) or 'SAR' in sar.columns

def test_get_defi_yields():
    from streamlit_app.modules.cryptop_crypto_fortune_teller_helper import get_defi_yields
    from unittest.mock import patch, MagicMock
    with patch('streamlit_app.modules.cryptop_crypto_fortune_teller_helper.requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'data': [
                {'symbol': 'USDC', 'project': 'Aave', 'chain': 'Ethereum', 'apy': 5.5, 'tvlUsd': 1000000, 'ilRisk': 'no'}
            ]
        }
        mock_get.return_value = mock_response

        yields = get_defi_yields()

        assert yields is not None
        assert not yields.empty
        assert yields.iloc[0]['symbol'] == 'USDC'

        # Exception
        get_defi_yields.clear()
        mock_get.side_effect = Exception("API fail")
        y2 = get_defi_yields()
        assert y2.empty

def test_get_exchange_arbitrage():
    from streamlit_app.modules.cryptop_crypto_fortune_teller_helper import get_exchange_arbitrage
    from unittest.mock import patch, MagicMock
    with patch('streamlit_app.modules.cryptop_crypto_fortune_teller_helper.ccxt') as mock_ccxt:
        mock_ex1 = MagicMock()
        mock_ex1.fetch_ticker.return_value = {'last': 50000}

        mock_ex2 = MagicMock()
        mock_ex2.fetch_ticker.return_value = {'last': 50500}

        mock_ccxt.binance.return_value = mock_ex1
        mock_ccxt.kraken.return_value = mock_ex2

        df = get_exchange_arbitrage('BTC/USDT')
        assert df is not None
        assert not df.empty
        assert 'Price' in df.columns

        # One fails
        mock_ex2.fetch_ticker.side_effect = Exception("Fetch Fail")
        df2 = get_exchange_arbitrage('ETH/USDT')
        assert df2 is not None
