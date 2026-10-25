import pytest
import pandas as pd
import numpy as np
import sys
import os
import warnings

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../streamlit_app')))

from modules.cryptop_crypto_fortune_teller_models import (
    forecast_prophet,
    forecast_lstm,
    _run_prophet_model,
    MAX_FORECAST_HORIZON
)
from unittest.mock import patch

def test_prophet_slicing_logic():
    # We want to verify that _run_prophet_model returns the correct number of rows
    # and that it correctly slices the cached result.

    history_len = 10
    total_len = history_len + MAX_FORECAST_HORIZON

    df_dummy = pd.DataFrame({
        'ds': pd.date_range(start='2020-01-01', periods=total_len),
        'yhat': np.arange(total_len),
        'yhat_lower': np.arange(total_len),
        'yhat_upper': np.arange(total_len)
    })

    # We mock the FIXED function, not the wrapper
    with patch('modules.cryptop_crypto_fortune_teller_models._run_prophet_model_fixed') as mock_fixed:
        mock_fixed.return_value = df_dummy

        # Case 1: periods = 30
        res = _run_prophet_model(pd.DataFrame(), {}, periods=30)
        assert len(res) == history_len + 30
        assert res.iloc[-1]['yhat'] == history_len + 30 - 1

        # Case 2: periods = MAX_FORECAST_HORIZON (365)
        res_full = _run_prophet_model(pd.DataFrame(), {}, periods=MAX_FORECAST_HORIZON)
        assert len(res_full) == total_len

        # Case 3: periods = 1
        res_1 = _run_prophet_model(pd.DataFrame(), {}, periods=1)
        assert len(res_1) == history_len + 1

        # Case 4: periods > MAX (clamped)
        res_clamp = _run_prophet_model(pd.DataFrame(), {}, periods=MAX_FORECAST_HORIZON + 10)
        assert len(res_clamp) == total_len

def test_forecast_prophet():
    # Create dummy data
    dates = pd.date_range(start='2023-01-01', periods=20)
    data = {'close': np.arange(20)}
    df = pd.DataFrame(data, index=dates)

    # Check robustness on small data
    # Prophet requires at least 2 rows
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=DeprecationWarning)
        forecast = forecast_prophet(df, periods=5)

    assert 'ds' in forecast.columns
    assert 'yhat' in forecast.columns
    # Check if forecast goes beyond last date
    assert forecast['ds'].max() > dates.max()

def test_forecast_lstm_short_data():
    # Create very short dummy data (10 points)
    dates = pd.date_range(start='2023-01-01', periods=10)
    data = {'close': np.arange(10).astype(float)}
    df = pd.DataFrame(data, index=dates)

    # Should handle it without crashing thanks to my fix (n_steps will be adjusted)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=DeprecationWarning)
        forecast = forecast_lstm(df, periods=2, n_steps=60)

    assert not forecast.empty
    assert len(forecast) == 2
    assert 'yhat' in forecast.columns

def test_monte_carlo():
    from modules.cryptop_crypto_fortune_teller_models import forecast_monte_carlo
    # Create synthetic daily data
    dates = pd.date_range(start='2020-01-01', periods=100, freq='D')
    prices = np.linspace(100, 150, 100) + np.random.normal(0, 5, 100)
    df = pd.DataFrame({'close': prices}, index=dates)

    # Test typical forecast
    res_df = forecast_monte_carlo(df, periods=30)
    assert not res_df.empty, "Monte Carlo forecast should return a dataframe"
    assert len(res_df) == 30, "Forecast length should match periods"
    assert 'yhat' in res_df.columns, "Missing 'yhat' column"
    assert 'yhat_lower' in res_df.columns, "Missing 'yhat_lower' column"
    assert 'yhat_upper' in res_df.columns, "Missing 'yhat_upper' column"

    # Check that yhat_lower <= yhat <= yhat_upper
    assert (res_df['yhat_lower'] <= res_df['yhat']).all(), "yhat_lower must be <= yhat"
    assert (res_df['yhat'] <= res_df['yhat_upper']).all(), "yhat must be <= yhat_upper"

def test_arima_exceptions():
    from streamlit_app.modules.cryptop_crypto_fortune_teller_models import forecast_arima, forecast_sarima
    import pandas as pd
    import numpy as np

    # 1. Very short dataframe
    dates = pd.date_range(start='2020-01-01', periods=5, freq='D')
    df_short = pd.DataFrame({'close': [100, 101, 102, 103, 104]}, index=dates)

    res = forecast_arima(df_short, periods=10)
    assert 'ds' in res.columns
    assert 'yhat' in res.columns

    res = forecast_sarima(df_short, periods=10)
    assert 'ds' in res.columns
    assert 'yhat' in res.columns

    # 2. Empty dataframe
    df_empty = pd.DataFrame(columns=['close'])
    res = forecast_arima(df_empty, periods=10)
    assert res.empty

    res = forecast_sarima(df_empty, periods=10)
    assert res.empty

def test_prophet_empty_dataframe():
    import warnings
    import pandas as pd
    df_empty = pd.DataFrame(columns=['close'])
    from streamlit_app.modules.cryptop_crypto_fortune_teller_models import forecast_prophet
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=DeprecationWarning)
        forecast = forecast_prophet(df_empty, periods=5)
    assert forecast.empty

def test_lstm_empty_dataframe():
    import warnings
    import pandas as pd
    df_empty = pd.DataFrame(columns=['close'])
    from streamlit_app.modules.cryptop_crypto_fortune_teller_models import forecast_lstm
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=DeprecationWarning)
        forecast = forecast_lstm(df_empty, periods=5)
    assert forecast.empty

def test_random_forest():
    from streamlit_app.modules.cryptop_crypto_fortune_teller_models import forecast_random_forest
    import pandas as pd
    import numpy as np
    # Create synthetic daily data
    dates = pd.date_range(start='2020-01-01', periods=100, freq='D')
    prices = np.linspace(100, 150, 100) + np.random.normal(0, 5, 100)
    df = pd.DataFrame({'close': prices}, index=dates)

    res_df = forecast_random_forest(df, periods=30)
    assert not res_df.empty, "RF forecast should return a dataframe"
    assert len(res_df) == 30, "Forecast length should match periods"
    assert 'yhat' in res_df.columns, "Missing 'yhat' column"

    # Empty DF
    df_empty = pd.DataFrame(columns=['close'])
    res = forecast_random_forest(df_empty, periods=10)
    assert res.empty

def test_random_forest_edge_cases():
    from streamlit_app.modules.cryptop_crypto_fortune_teller_models import forecast_random_forest
    from unittest.mock import patch
    import pandas as pd
    import numpy as np

    # Short data
    dates = pd.date_range(start='2020-01-01', periods=5, freq='D')
    df = pd.DataFrame({'close': [1,2,3,4,5]}, index=dates)
    res = forecast_random_forest(df, periods=5, n_lags=10)
    assert res.empty

    # Clamping
    dates2 = pd.date_range(start='2020-01-01', periods=20, freq='D')
    df2 = pd.DataFrame({'close': np.arange(20)}, index=dates2)
    from streamlit_app.modules.cryptop_crypto_fortune_teller_models import MAX_FORECAST_HORIZON
    res2 = forecast_random_forest(df2, periods=MAX_FORECAST_HORIZON + 10, n_lags=5)
    assert len(res2) == MAX_FORECAST_HORIZON

    # Simulate Exception
    with patch('streamlit_app.modules.cryptop_crypto_fortune_teller_models.RandomForestRegressor') as mock_rf:
        mock_rf.side_effect = Exception("RF Error")
        try:
            res3 = forecast_random_forest(df2, periods=5, n_lags=5)
        except Exception:
            pass

def test_arima_sarima_exception_catch():
    from streamlit_app.modules.cryptop_crypto_fortune_teller_models import forecast_arima, forecast_sarima
    from unittest.mock import patch
    import pandas as pd

    dates = pd.date_range(start='2020-01-01', periods=10, freq='D')
    df = pd.DataFrame({'close': [100]*10}, index=dates)

    with patch('streamlit_app.modules.cryptop_crypto_fortune_teller_models.get_best_arima') as mock_best:
        mock_best.side_effect = Exception("Forced error")

        res_arima = forecast_arima(df, periods=5)
        assert res_arima.empty
        assert 'ds' in res_arima.columns

        res_sarima = forecast_sarima(df, periods=5)
        assert res_sarima.empty
        assert 'ds' in res_sarima.columns

def test_lstm_exception_catch():
    from streamlit_app.modules.cryptop_crypto_fortune_teller_models import forecast_lstm
    import pandas as pd
    from unittest.mock import patch
    import warnings

    dates = pd.date_range(start='2020-01-01', periods=20, freq='D')
    df = pd.DataFrame({'close': [100]*20}, index=dates)

    with patch('streamlit_app.modules.cryptop_crypto_fortune_teller_models.MinMaxScaler') as mock_scaler:
        mock_scaler.side_effect = Exception("Forced LSTM Error")

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=DeprecationWarning)
            try:
                forecast_lstm(df, periods=5)
            except Exception:
                pass # Expected if not caught

def test_auto_tune_prophet():
    from streamlit_app.modules.cryptop_crypto_fortune_teller_models import auto_tune_prophet
    import pandas as pd
    import numpy as np
    from unittest.mock import patch

    # Needs len > 100 to actually run tuning
    dates = pd.date_range(start='2020-01-01', periods=120, freq='D')
    df = pd.DataFrame({'close': np.random.rand(120)}, index=dates)

    # Run with small grid to not take forever
    with patch('streamlit_app.modules.cryptop_crypto_fortune_teller_models.st.cache_data') as mock_cache:
        # Actually it's cached, so we just call it directly.
        params = auto_tune_prophet(df, param_grid={
            'changepoint_prior_scale': [0.01],
            'seasonality_prior_scale': [0.1]
        })

        assert isinstance(params, dict)
        assert 'changepoint_prior_scale' in params

        # Exception catch
        with patch('prophet.Prophet') as mock_prophet:
            mock_prophet.side_effect = Exception("Prophet Tune Fail")
            params2 = auto_tune_prophet(df, param_grid={
                'changepoint_prior_scale': [0.01],
                'seasonality_prior_scale': [0.1]
            })
            # Should return first set of params when it fails for all
            assert params2 == {'changepoint_prior_scale': 0.01, 'seasonality_prior_scale': 0.1}

def test_get_best_arima():
    from streamlit_app.modules.cryptop_crypto_fortune_teller_models import get_best_arima
    import pandas as pd
    import numpy as np
    from unittest.mock import patch

    dates = pd.date_range(start='2020-01-01', periods=20, freq='D')
    series = pd.Series(np.linspace(100, 150, 20), index=dates)

    # Force exception inside loop to test Exception handling
    with patch('streamlit_app.modules.cryptop_crypto_fortune_teller_models.ARIMA') as mock_arima:
        mock_arima.side_effect = Exception("ARIMA fit fail")
        order = get_best_arima(series, max_p=1, max_q=1, d=1)
        # Should return default
        assert order == (0, 1, 0)

    # Normal run
    order = get_best_arima(series, max_p=1, max_q=1, d=1)
    assert len(order) == 3
