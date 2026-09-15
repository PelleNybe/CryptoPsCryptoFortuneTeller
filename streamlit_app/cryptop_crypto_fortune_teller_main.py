# cryptop_crypto_fortune_teller_main.py

import streamlit as st
import logging
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import datetime
import html
import uuid

from modules.cryptop_crypto_fortune_teller_helper import (
    get_historical_volume,
    calculate_black_scholes,
    get_coin_list,
    get_historical_prices,
    get_historical_ohlc,
    get_coin_metrics,
    get_fear_and_greed_index,
    calculate_rsi,
    calculate_macd,
    calculate_bollinger_bands,
    compute_volatility,
    get_trending_coins,
    get_current_price,
    calculate_backtest,
    get_batch_historical_prices,
    calculate_stochastic_oscillator,
    calculate_ichimoku_cloud,
    calculate_pivot_points,
    calculate_fibonacci_levels,
    calculate_roi,
    calculate_moon_math,
    get_coin_market_cap_batch,
    get_coin_market_data,
    check_risk_level,
    generate_trading_signal,
    validate_coin_id,
    detect_candlestick_patterns,
    get_exchange_arbitrage,
    calculate_correlation_matrix,
    calculate_dca_strategy,
    detect_volume_anomalies,
    calculate_vwap,
    calculate_parabolic_sar,
    get_historical_volume,
    calculate_adx,
    calculate_cci,
    get_top_gainers_losers,
    calculate_impermanent_loss,
    get_defi_yields,
    get_whale_alerts,
    get_crypto_news_sentiment,
    get_tokenomics_data
)
from modules.utils import validate_url
from modules.cryptop_crypto_fortune_teller_models import (
    auto_tune_prophet,
    forecast_general_ensemble
)
from modules.exchange_manager import ExchangeManager
from modules.freqtrade_manager import FreqtradeManager
from modules.cryptop_crypto_fortune_teller_styles import apply_custom_css

# 1) Page config

# Technical Improvement 5: Session Vault for Secure Credential Management
@st.cache_resource
def get_exchange_vault(session_id):
    return ExchangeManager()

@st.cache_resource
def get_freqtrade_vault(session_id):
    # Store just a reference or dict, or the manager itself
    return {"client": None}


st.set_page_config(
    page_title="Crypto P's Crypto Fortune Teller",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 2) Apply Custom CSS for "Awesome Design" - PSYCHEDELIC CARNIVAL THEME
apply_custom_css()

# 3) Header
logo_path = "assets/logo.png"

col1, col2, col3 = st.columns([1, 6, 1])
with col2:
    try:
        st.image(logo_path, width=150, alt="Crypto P's Fortune Teller Logo")
    except Exception as e:
        logging.error("Failed to load logo", exc_info=True)
        st.write("🔮") # Fallback if image missing
    st.markdown("<h1 style='text-align: center; color: #FFD700; text-shadow: 0 0 10px #FF00FF;'>🎪 Crypto P's 🔮<br>Fortune Teller</h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center; color: #00FFFF; font-family: Cinzel, serif;'>✨ Peer into the Misty Future of the Blockchain ✨</h4>", unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# Feature: Ticker Tape (Visual Improvement 1)
# Fetch trending coins quickly for the banner
with st.spinner("Initializing Oracle..."):
    gainers, losers = get_top_gainers_losers(limit=10)

if not gainers.empty:
    # Optimization: Replaced itertuples with list comprehensions for speed
    top_gainers = gainers.head(5)
    gainer_items = [
        f"<span style='margin-right: 30px; font-weight: bold;'>🔥 {html.escape(str(sym).upper())} <span style='color: {html.escape('#00FF00' if pct > 0 else '#FF0000')}'>{html.escape(f'{pct:+.2f}%')}</span></span>"
        for sym, pct in zip(top_gainers['symbol'], top_gainers['price_change_percentage_24h'])
    ]

    top_losers = losers.head(5)
    loser_items = [
        f"<span style='margin-right: 30px; font-weight: bold;'>🧊 {html.escape(str(sym).upper())} <span style='color: {html.escape('#00FF00' if pct > 0 else '#FF0000')}'>{html.escape(f'{pct:+.2f}%')}</span></span>"
        for sym, pct in zip(top_losers['symbol'], top_losers['price_change_percentage_24h'])
    ]
    ticker_items = gainer_items + loser_items

    ticker_html = f"""
    <div style="width: 100%; overflow: hidden; background: linear-gradient(90deg, #150020, #2a0e3b, #150020); border-bottom: 2px solid #FF00FF; border-top: 2px solid #00FFFF; padding: 10px 0; margin-bottom: 20px;">
        <div style="white-space: nowrap; animation: ticker 25s linear infinite; font-family: 'Orbitron', sans-serif; font-size: 1.2rem; color: white;">
            {''.join(ticker_items)}
            {''.join(ticker_items)}
        </div>
    </div>
    <style>
        @keyframes ticker {{
            0%   {{ transform: translateX(100%); }}
            100% {{ transform: translateX(-100%); }}
        }}
    </style>
    """
    st.markdown(''.join([ticker_html]), unsafe_allow_html=True)


# 4) Sidebar
with st.sidebar:
    st.header("🔍 User Inputs")

    # Coin Selection
    with st.spinner("Loading coins..."):
        df_coins = get_coin_list()

    if df_coins.empty:
        st.error("Could not load coin list.")
        st.stop()

    display_series = df_coins['name'] + ' (' + df_coins['symbol'].str.upper() + ')'
    options = display_series.tolist()
    mapping = pd.Series(df_coins.id.values, index=display_series).to_dict()

    with st.expander("🪙 Asset Selection", expanded=True):
        selected_option = st.selectbox("Select Cryptocurrency", options, index=0, help="Search and select the cryptocurrency you want to analyze.")
        coin_id = mapping[selected_option]

        #Global Input Validation for coin_id
        if not validate_coin_id(coin_id):
            st.error("Invalid Asset ID detected. Please select a valid asset.")
            st.stop()

    with st.expander("🔮 Forecast Settings", expanded=True):
        st.markdown("### ⚙️ Model Ensemble")
        selected_models = st.multiselect(
            "Select Models to Combine",
            [
                "Prophet (Standard)",
                "Prophet (Volatile)",
                "Prophet (Conservative)",
                "LSTM",
                "ARIMA",
                "SARIMA",
                "Random Forest",
                "Monte Carlo (GBM)"
            ],
            default=["Prophet (Standard)", "Random Forest"],
            help="Combine multiple statistical and AI models for robust predictions."
        )

        forecast_days = st.slider("Forecast Horizon (Days)", 7, 365, 30, help="Predict up to 1 year into the future.")

        enhance_sentiment = st.checkbox(
            "Enhance with Community Sentiment",
            value=False,
            help="Analyze community data (Twitter/Reddit sentiment) to adjust the forecast."
        )

        with st.expander("🔧 Advanced Model Config"):
            st.write("Tune the Prophet model hyperparameters.")
            p_changepoint = st.slider("Changepoint Prior Scale", 0.001, 0.5, 0.05, step=0.001, help="Flexibility of the trend. Higher = more flexible (overfitting risk).")
            p_seasonality = st.slider("Seasonality Prior Scale", 0.01, 20.0, 10.0, step=0.1, help="Strength of seasonality.")
            p_season_mode = st.radio("Seasonality Mode", ["additive", "multiplicative"], index=0)

            auto_tune = st.checkbox("Auto-Tune Prophet Hyperparameters (Beta)", value=False, help="Run an automatic grid search to find optimal changepoint and seasonality scales. Overrides manual sliders.")

            if auto_tune:
                with st.spinner("Auto-tuning Prophet models..."):
                    # Use a small historical sample for speed
                    hist_for_tune = get_historical_prices(coin_id, days=365)
                    if not hist_for_tune.empty:
                        best_params = auto_tune_prophet(hist_for_tune)
                        st.success(f"Tuning complete. Best CPS: {best_params.get('changepoint_prior_scale')}, SPS: {best_params.get('seasonality_prior_scale')}")
                        p_changepoint = best_params.get('changepoint_prior_scale', p_changepoint)
                        p_seasonality = best_params.get('seasonality_prior_scale', p_seasonality)

            model_params = {
                'changepoint_prior_scale': p_changepoint,
                'seasonality_prior_scale': p_seasonality,
                'seasonality_mode': p_season_mode
            }

    st.markdown("---")

    # Fear & Greed
    st.subheader("😱 Fear & Greed")
    fng = get_fear_and_greed_index()
    if fng:
        val = int(fng['value'])

        fig_fng = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = val,
            title = {'text': fng['classification'], 'font': {'size': 18}},
            gauge = {
                'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
                'bar': {'color': "white"},
                'bgcolor': "black",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, 40], 'color': "red"},
                    {'range': [40, 60], 'color': "orange"},
                    {'range': [60, 100], 'color': "green"}],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90}}))

        fig_fng.update_layout(height=250, margin=dict(t=30, b=0, l=30, r=30), paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"})
        st.plotly_chart(fig_fng, use_container_width=True)
    else:
        st.write("N/A")

    st.markdown("---")

    # Quick Converter
    with st.expander("💱 Quick Converter"):
        conv_amount = st.number_input("Amount", min_value=0.0, value=1.0, step=0.1)
        if st.button("Convert"):
            with st.spinner("Converting..."):
                prices = get_current_price(coin_id, vs_currencies='usd,eur,btc,eth')
                if prices and coin_id in prices:
                    p = prices[coin_id]
                    st.write(f"**USD:** ${p.get('usd', 0) * conv_amount:,.2f}")
                    st.write(f"**EUR:** €{p.get('eur', 0) * conv_amount:,.2f}")
                    st.write(f"**BTC:** ₿{p.get('btc', 0) * conv_amount:.6f}")
                    st.write(f"**ETH:** Ξ{p.get('eth', 0) * conv_amount:.6f}")
                else:
                    st.error("Conversion failed.")

    st.info("Note: Prediction models are for educational purposes only. Not financial advice.")

# 5) Main Content Tabs
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11 = st.tabs([
    "🔮 Forecast",
    "📊 Analysis",
    "⚖️ Compare",
    "🧪 Backtest",
    "💰 Portfolio",
    "🌍 Market",
    "🧮 Calculators",
    "🔧 Stats",
    "🔌 Connect",
    "💎 Alpha Insights",
    "🧙 About"
])

# --- TAB 1: FORECAST ---
with tab1:
    st.subheader(f"Price Forecast: {selected_option}")

    with st.spinner("Consulting the oracles..."):
        # Fetch sufficient history for all models (1 year min usually good, maybe 2 for seasonality)
        price_df = get_historical_prices(coin_id, 'usd', days=730)

        if price_df.empty:
            st.error("No historical data available for this coin.")
        else:
            # 1. Risk Warning
            risk_msg = check_risk_level(price_df)
            if risk_msg:
                st.warning(risk_msg)

            # 2. Sentiment Score
            s_score = 0.0
            if enhance_sentiment:
                metrics = get_coin_metrics(coin_id)
                up_pct = metrics.get('sentiment_up_pct')
                if up_pct is not None:
                    s_score = (float(up_pct) - 50.0) / 50.0
                    st.info(f"✨ Sentiment Enhancement Active! Market Sentiment is {up_pct:.1f}% Bullish. Adjustment Factor: {s_score:.2f}")
                else:
                    st.warning("Sentiment data unavailable. Proceeding with neutral sentiment.")

            if not selected_models:
                st.warning("Please select at least one model variant.")
                forecast_df = pd.DataFrame()
            else:
                forecast_df = forecast_general_ensemble(
                    price_df,
                    model_names=selected_models,
                    periods=forecast_days,
                    sentiment_score=s_score,
                    model_params=model_params
                )

            if not forecast_df.empty:
                # Generate Trading Signal
                current_p = price_df['close'].iloc[-1]
                signal, signal_color = generate_trading_signal(current_p, forecast_df)

                col_sig1, col_sig2 = st.columns([1, 3])
                with col_sig1:
                    st.markdown(f"""
                    <div style="border: 2px solid {html.escape(signal_color)}; padding: 10px; border-radius: 10px; text-align: center; background-color: rgba(0,0,0,0.5);">
                        <h3 style="color: {html.escape(signal_color)}; margin: 0;">{html.escape(signal)}</h3>
                        <p style="margin: 0; font-size: 0.8rem; color: #fff;">Trading Signal</p>
                    </div>
                    """, unsafe_allow_html=True)

                with col_sig2:
                    st.write("### AI Prediction Summary")
                    final_price = forecast_df['yhat'].iloc[-1]
                    gain_loss = ((final_price - current_p) / current_p) * 100
                    st.write(f"Projected Price in {forecast_days} days: **${final_price:,.2f}** ({gain_loss:+.2f}%)")

                # Plot
                fig = go.Figure()

                # Historical (Limit history view to last 365 days for clarity, but model used 730)
                disp_hist = price_df.iloc[-365:]
                fig.add_trace(go.Scatter(
                    x=disp_hist.index, y=disp_hist['close'],
                    mode='lines', name='History',
                    line=dict(color='#00FFFF', width=2)
                ))

                # Forecast
                fig.add_trace(go.Scatter(
                    x=forecast_df['ds'], y=forecast_df['yhat'],
                    mode='lines', name='Forecast',
                    line=dict(color='#FF00FF', dash='dash', width=3)
                ))

                # Confidence Intervals if available and meaningful (not all zero/same)
                # Check if upper != lower
                if (forecast_df['yhat_upper'] != forecast_df['yhat_lower']).any():
                    fig.add_trace(go.Scatter(
                        x=forecast_df['ds'], y=forecast_df['yhat_upper'],
                        mode='lines', marker=dict(color="#444"), line=dict(width=0), showlegend=False
                    ))
                    fig.add_trace(go.Scatter(
                        x=forecast_df['ds'], y=forecast_df['yhat_lower'],
                        marker=dict(color="#444"), line=dict(width=0), mode='lines',
                        fillcolor='rgba(255, 0, 255, 0.1)', fill='tonexty', showlegend=False
                    ))

                title_text = f"{selected_option} - Ensemble Forecast"

                fig.update_layout(
                    title=title_text,
                    xaxis_title="Date", yaxis_title="Price (USD)",
                    template="plotly_dark", height=500, hovermode="x unified"
                )
                st.plotly_chart(fig, use_container_width=True)

                # Download Forecast Data
                csv = forecast_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download Forecast CSV",
                    data=csv,
                    file_name=f'{coin_id}_forecast.csv',
                    mime='text/csv',
                )

# --- TAB 2: ANALYSIS ---
with tab2:
    st.subheader("Technical Analysis")

    col_ctrl1, col_ctrl2 = st.columns([1, 2])
    with col_ctrl1:
        date_opt = st.radio("Timeframe", ["90 Days", "180 Days", "1 Year", "Custom"], index=1)

        days_back = 180
        if date_opt == "90 Days": days_back = 90
        elif date_opt == "180 Days": days_back = 180
        elif date_opt == "1 Year": days_back = 365
        else:
             # Custom date range handling
             start_date = st.date_input("Start Date", datetime.date.today() - datetime.timedelta(days=180))
             days_back = (datetime.date.today() - start_date).days
             if days_back < 1: days_back = 7

    with col_ctrl2:
        st.write("Indicators & Overlays:")
        col_ind1, col_ind2, col_ind3 = st.columns(3)
        show_fib = col_ind1.checkbox("Fibonacci Levels")
        show_sma = col_ind2.checkbox("SMA Ribbon")
        show_ichi = col_ind3.checkbox("Ichimoku Cloud")
        show_stoch = col_ind1.checkbox("Stochastic Osc.")
        show_bb = col_ind2.checkbox("Bollinger Bands", value=True)
        show_pivot = col_ind3.checkbox("Pivot Points")
        show_vwap = col_ind1.checkbox("VWAP")
        show_sar = col_ind2.checkbox("Parabolic SAR")
        show_adx = col_ind3.checkbox("ADX / DMI")
        show_cci = col_ind1.checkbox("CCI")

    with st.spinner("Analyzing market patterns..."):
        # Fetch OHLC
        ohlc_df = get_historical_ohlc(coin_id, days=days_back)
        if ohlc_df.empty:
            ohlc_df = get_historical_prices(coin_id, days=days_back)
            if not ohlc_df.empty:
                ohlc_df['open'] = ohlc_df['close']
                ohlc_df['high'] = ohlc_df['close']
                ohlc_df['low'] = ohlc_df['close']

        if ohlc_df.empty:
            st.error("No data available.")
        else:
            # Calculations
            bb_df = calculate_bollinger_bands(ohlc_df) if show_bb else pd.DataFrame()
            ichi_df = calculate_ichimoku_cloud(ohlc_df) if show_ichi else pd.DataFrame()
            fib_levels = calculate_fibonacci_levels(ohlc_df) if show_fib else {}
            stoch_df = calculate_stochastic_oscillator(ohlc_df) if show_stoch else pd.DataFrame()
            pivot_points = calculate_pivot_points(ohlc_df) if show_pivot else {}

            # VWAP & SAR Logic
            vwap_series = pd.Series(dtype=float)
            if show_vwap:
                vol_df = get_historical_volume(coin_id, days=days_back)
                if not vol_df.empty:
                    # Join volume to OHLC for calculation
                    temp_df = ohlc_df.join(vol_df, how='left')
                    vwap_series = calculate_vwap(temp_df)

            sar_series = calculate_parabolic_sar(ohlc_df) if show_sar else pd.Series(dtype=float)

            # Plot 1: Main Chart with Volume Subplot
            # Visual Improvement 3: Candlestick Chart with Volume Subplot
            fig_main = make_subplots(rows=2, cols=1, shared_xaxes=True,
                                     vertical_spacing=0.03, subplot_titles=('Price Action', 'Volume'),
                                     row_width=[0.2, 0.7])

            fig_main.add_trace(go.Candlestick(
                x=ohlc_df.index, open=ohlc_df['open'], high=ohlc_df['high'],
                low=ohlc_df['low'], close=ohlc_df['close'], name='OHLC'
            ), row=1, col=1)

            # Fetch and add volume if available
            vol_for_chart = get_historical_volume(coin_id, days=days_back)
            if not vol_for_chart.empty:
                # Merge to align dates
                merged_vol = ohlc_df.join(vol_for_chart, how='left').fillna(0)
                colors = np.where(merged_vol['open'] - merged_vol['close'] >= 0, 'green', 'red')
                fig_main.add_trace(go.Bar(
                    x=merged_vol.index, y=merged_vol['volume'], marker_color=colors, name='Volume'
                ), row=2, col=1)

            # VWAP
            if show_vwap and not vwap_series.empty:
                fig_main.add_trace(go.Scatter(x=vwap_series.index, y=vwap_series, line=dict(color='#ff9f43', width=2), name='VWAP'), row=1, col=1)

            # Parabolic SAR
            if show_sar and not sar_series.empty:
                fig_main.add_trace(go.Scatter(x=sar_series.index, y=sar_series, mode='markers', marker=dict(color='white', size=4, symbol='cross'), name='Parabolic SAR'), row=1, col=1)

            # Bollinger Bands
            if not bb_df.empty:
                fig_main.add_trace(go.Scatter(x=bb_df.index, y=bb_df['B_Upper'], line=dict(color='#bd93f9', width=1), name='BB Upper'), row=1, col=1)
                fig_main.add_trace(go.Scatter(x=bb_df.index, y=bb_df['B_Lower'], line=dict(color='#bd93f9', width=1), name='BB Lower', fill='tonexty', fillcolor='rgba(189, 147, 249, 0.1)'), row=1, col=1)
                fig_main.add_trace(go.Scatter(x=bb_df.index, y=bb_df['SMA'], line=dict(color='#FFD700', width=1), name='BB SMA 20'), row=1, col=1)

            # Ichimoku
            if not ichi_df.empty:
                fig_main.add_trace(go.Scatter(x=ichi_df.index, y=ichi_df['SpanA'], line=dict(width=0), showlegend=False, name='Span A'), row=1, col=1)
                fig_main.add_trace(go.Scatter(x=ichi_df.index, y=ichi_df['SpanB'], line=dict(width=0), fill='tonexty', fillcolor='rgba(0, 255, 255, 0.1)', name='Ichimoku Cloud'), row=1, col=1)
                fig_main.add_trace(go.Scatter(x=ichi_df.index, y=ichi_df['Tenkan'], line=dict(color='#00FFFF', width=1), name='Tenkan'), row=1, col=1)
                fig_main.add_trace(go.Scatter(x=ichi_df.index, y=ichi_df['Kijun'], line=dict(color='#FF4500', width=1), name='Kijun'), row=1, col=1)

            # SMA Ribbon
            if show_sma:
                colors = ['#FF0000', '#FFA500', '#FFFF00', '#008000']
                for i, period in enumerate([20, 50, 100, 200]):
                    sma = ohlc_df['close'].rolling(window=period).mean()
                    fig_main.add_trace(go.Scatter(x=ohlc_df.index, y=sma, line=dict(color=colors[i], width=1), name=f'SMA {period}'), row=1, col=1)

            # Fibonacci
            if show_fib:
                for label, val in fib_levels.items():
                    fig_main.add_hline(y=val, line_dash="dot", line_color="gray", annotation_text=label, row=1, col=1)

            # Annotations (Max/Min)
            max_idx = ohlc_df['high'].idxmax()
            min_idx = ohlc_df['low'].idxmin()
            fig_main.add_annotation(x=max_idx, y=ohlc_df.loc[max_idx]['high'], text="Max", showarrow=True, arrowhead=1, row=1, col=1)
            fig_main.add_annotation(x=min_idx, y=ohlc_df.loc[min_idx]['low'], text="Min", showarrow=True, arrowhead=1, row=1, col=1)

            fig_main.update_layout(title="Price Action", template="plotly_dark", xaxis_rangeslider_visible=False, height=600)
            st.plotly_chart(fig_main, use_container_width=True)

            # Pivot Points Display
            if show_pivot and pivot_points:
                st.write("**Daily Pivot Points (Projected):**")
                cols = st.columns(7)
                cols[0].metric("S3", f"{pivot_points['S3']:.2f}")
                cols[1].metric("S2", f"{pivot_points['S2']:.2f}")
                cols[2].metric("S1", f"{pivot_points['S1']:.2f}")
                cols[3].metric("Pivot", f"{pivot_points['Pivot']:.2f}")
                cols[4].metric("R1", f"{pivot_points['R1']:.2f}")
                cols[5].metric("R2", f"{pivot_points['R2']:.2f}")
                cols[6].metric("R3", f"{pivot_points['R3']:.2f}")

            # Feature: Candlestick Pattern Recognition
            with st.expander("🕯️ AI Pattern Recognition", expanded=True):
                patterns = detect_candlestick_patterns(ohlc_df)
                if patterns:
                    st.success(f"Detected Patterns on Latest Candle: {', '.join(patterns)}")
                else:
                    st.info("No specific patterns detected on the latest candle.")

            # Sub-charts: RSI, Stoch, MACD
            st.markdown("### Indicators")

            # Stochastic
            if show_stoch and not stoch_df.empty:
                fig_stoch = go.Figure()
                fig_stoch.add_trace(go.Scatter(x=stoch_df.index, y=stoch_df['%K'], name='%K', line=dict(color='#00FFFF')))
                fig_stoch.add_trace(go.Scatter(x=stoch_df.index, y=stoch_df['%D'], name='%D', line=dict(color='#FF4500')))
                fig_stoch.add_hline(y=80, line_dash="dot", line_color="red")
                fig_stoch.add_hline(y=20, line_dash="dot", line_color="green")
                fig_stoch.update_layout(title="Stochastic Oscillator", template="plotly_dark", height=250, yaxis_range=[0, 100])
                st.plotly_chart(fig_stoch, use_container_width=True)

            # ADX / CCI row
            if show_adx or show_cci:
                col_i1, col_i2 = st.columns(2)
                with col_i1:
                    if show_adx:
                        adx_df = calculate_adx(ohlc_df)
                        fig_adx = go.Figure()
                        fig_adx.add_trace(go.Scatter(x=adx_df.index, y=adx_df['ADX'], name='ADX', line=dict(color='white', width=2)))
                        fig_adx.add_trace(go.Scatter(x=adx_df.index, y=adx_df['+DI'], name='+DI', line=dict(color='green', width=1)))
                        fig_adx.add_trace(go.Scatter(x=adx_df.index, y=adx_df['-DI'], name='-DI', line=dict(color='red', width=1)))
                        fig_adx.add_hline(y=25, line_dash="dot", line_color="gray")
                        fig_adx.update_layout(title="ADX / DMI", template="plotly_dark", height=250)
                        st.plotly_chart(fig_adx, use_container_width=True)

                with col_i2:
                    if show_cci:
                        cci_series = calculate_cci(ohlc_df)
                        fig_cci = go.Figure()
                        fig_cci.add_trace(go.Scatter(x=cci_series.index, y=cci_series, name='CCI', line=dict(color='orange')))
                        fig_cci.add_hline(y=100, line_dash="dot", line_color="red")
                        fig_cci.add_hline(y=-100, line_dash="dot", line_color="green")
                        fig_cci.update_layout(title="CCI", template="plotly_dark", height=250)
                        st.plotly_chart(fig_cci, use_container_width=True)

            col_a1, col_a2 = st.columns(2)

            with col_a1:
                rsi = calculate_rsi(ohlc_df)
                fig_rsi = go.Figure()
                fig_rsi.add_trace(go.Scatter(x=rsi.index, y=rsi, name='RSI', line=dict(color='#FF4500')))
                fig_rsi.add_hline(y=70, line_dash="dot", line_color="red")
                fig_rsi.add_hline(y=30, line_dash="dot", line_color="green")
                # Technical Improvement: Advanced Shading
                fig_rsi.add_hrect(y0=70, y1=100, fillcolor="red", opacity=0.1, layer="below", line_width=0)
                fig_rsi.add_hrect(y0=0, y1=30, fillcolor="green", opacity=0.1, layer="below", line_width=0)
                fig_rsi.update_layout(title="RSI", template="plotly_dark", height=250, yaxis_range=[0, 100])
                st.plotly_chart(fig_rsi, use_container_width=True)

            with col_a2:
                macd_df = calculate_macd(ohlc_df)
                if not macd_df.empty:
                    fig_macd = make_subplots(specs=[[{"secondary_y": False}]])
                    fig_macd.add_trace(go.Bar(x=macd_df.index, y=macd_df['Histogram'], name='Hist', marker_color=np.where(macd_df['Histogram'] < 0, 'red', 'green')))
                    fig_macd.add_trace(go.Scatter(x=macd_df.index, y=macd_df['MACD'], name='MACD', line=dict(color='#00FFFF', width=2)))
                    fig_macd.add_trace(go.Scatter(x=macd_df.index, y=macd_df['Signal'], name='Signal', line=dict(color='#FF4500', width=2), fill='tonexty', fillcolor='rgba(255, 69, 0, 0.2)'))
                    fig_macd.update_layout(title="MACD", template="plotly_dark", height=250)
                    st.plotly_chart(fig_macd, use_container_width=True)

            # Export Data
            st.download_button(
                label="📥 Download Historical Data CSV",
                data=ohlc_df.to_csv().encode('utf-8'),
                file_name=f'{coin_id}_history.csv',
                mime='text/csv',
            )

# --- TAB 3: COMPARE ---
with tab3:
    st.subheader("⚖️ Asset Comparison")
    st.write("Compare the performance of multiple assets over time.")

    comp_coins = st.multiselect("Select Assets to Compare", options, default=[options[0], "Bitcoin (BTC)"] if "Bitcoin (BTC)" in options else [options[0]])
    comp_days = st.selectbox("Duration", [30, 90, 180, 365, 730], index=1)

    if comp_coins:
        with st.spinner("Fetching data..."):
            comp_ids = [mapping[c] for c in comp_coins]
            comp_df = get_batch_historical_prices(comp_ids, days=comp_days)

            if not comp_df.empty:
                # Normalize to 100 (Percentage Change)
                norm_df = (comp_df / comp_df.iloc[0]) * 100

                fig_comp = go.Figure()
                for col in norm_df.columns:
                    # Find symbol name for legend
                    sym = [k for k, v in mapping.items() if v == col][0]
                    fig_comp.add_trace(go.Scatter(x=norm_df.index, y=norm_df[col], name=sym, mode='lines'))

                fig_comp.update_layout(
                    title=f"Relative Performance (Base=100) - {comp_days} Days",
                    xaxis_title="Date",
                    yaxis_title="Normalized Price",
                    template="plotly_dark",
                    hovermode="x unified"
                )
                st.plotly_chart(fig_comp, use_container_width=True)

                # Feature: Correlation Matrix
                st.markdown("### 🔗 Correlation Matrix")
                with st.spinner("Calculating correlations..."):
                    corr_matrix = calculate_correlation_matrix(comp_ids, days=comp_days)
                    if not corr_matrix.empty:
                        # Visual Improvement 2: Interactive Heatmap

                        # Replace IDs with names for better display
                        corr_names = [next(k for k, v in mapping.items() if v == col) for col in corr_matrix.columns]
                        corr_matrix.columns = corr_names
                        corr_matrix.index = corr_names

                        fig_corr = go.Figure(data=go.Heatmap(
                            z=corr_matrix.values,
                            x=corr_matrix.columns,
                            y=corr_matrix.index,
                            colorscale='RdBu',
                            zmin=-1, zmax=1,
                            hoverongaps=False,
                            text=np.round(corr_matrix.values, 2),
                            texttemplate="%{text}",
                            textfont={"size": 12}
                        ))

                        fig_corr.update_layout(
                            title=f"Correlation Heatmap ({comp_days} days)",
                            xaxis_title="Assets",
                            yaxis_title="Assets",
                            template="plotly_dark",
                            width=700,
                            height=600
                        )
                        fig_corr.update_layout(template="plotly_dark")
                        st.plotly_chart(fig_corr, use_container_width=True)

            else:
                st.error("No data available for selected coins.")
    else:
        st.info("Select at least one asset to display.")

# --- TAB 4: BACKTEST ---
with tab4:
    st.subheader("🧪 Strategy Backtester")

    col_bt1, col_bt2 = st.columns(2)
    with col_bt1:
        strategy = st.selectbox("Strategy", ["SMA Crossover", "RSI Mean Reversion", "Bollinger Band Squeeze", "MACD Crossover", "VWAP Reversion"])
    with col_bt2:
        bt_days = st.selectbox("Backtest Period", [180, 365, 730], index=1)

    if st.button("Run Backtest"):
        with st.spinner("Simulating..."):
            bt_data = get_historical_prices(coin_id, days=bt_days)
            if not bt_data.empty:
                res_df, metrics = calculate_backtest(bt_data, strategy_type=strategy)

                m1, m2, m3 = st.columns(3)
                m1.metric("Total Return", f"{metrics['Total Return']:.2%}", delta_color="normal")
                m2.metric("Market Return", f"{metrics['Market Return']:.2%}", delta_color="normal")
                alpha = metrics['Total Return'] - metrics['Market Return']
                m3.metric("Alpha", f"{alpha:.2%}", delta=f"{alpha:.2%}")

                fig_bt = go.Figure()
                fig_bt.add_trace(go.Scatter(x=res_df.index, y=res_df['cumulative_market_returns'], name='Buy & Hold', line=dict(dash='dot')))
                fig_bt.add_trace(go.Scatter(x=res_df.index, y=res_df['cumulative_strategy_returns'], name='Strategy', line=dict(color='#00FF00', width=2)))
                fig_bt.update_layout(title="Equity Curve", template="plotly_dark", yaxis_title="Growth Factor")
                st.plotly_chart(fig_bt, use_container_width=True)
            else:
                st.error("Backtest failed.")

# --- TAB 5: PORTFOLIO ---
with tab5:
    st.subheader("💰 Portfolio Tracker")

    if 'portfolio' not in st.session_state:
        st.session_state.portfolio = []

    with st.expander("Add Asset", expanded=False):
        with st.form("add_asset_form"):
            p_coin = st.selectbox("Coin", options)
            p_amount = st.number_input("Amount", min_value=0.0, step=0.01)
            p_buy_price = st.number_input("Avg Buy Price ($)", min_value=0.0, step=0.01)
            submitted = st.form_submit_button("Add")

            if submitted:
                p_coin_id = mapping[p_coin]
                p_symbol = p_coin.split('(')[1].replace(')', '')
                st.session_state.portfolio.append({
                    'id': p_coin_id, 'name': p_coin, 'symbol': p_symbol,
                    'amount': p_amount, 'buy_price': p_buy_price
                })
                st.success(f"Added {p_amount} {p_symbol}")

    if st.session_state.portfolio:
        # Calculate
        port_data = []
        total_val = 0
        total_cost = 0

        p_ids = list({i['id'] for i in st.session_state.portfolio})
        curr_prices = get_current_price(p_ids)

        # Optimization: Vectorized portfolio calculations
        port_df_temp = pd.DataFrame(st.session_state.portfolio)
        if not port_df_temp.empty:
            if curr_prices:
                # Extract 'usd' values from curr_prices dicts efficiently without lambda
                prices_series = pd.Series([curr_prices.get(i, {}).get('usd', 0) for i in port_df_temp['id']], index=port_df_temp.index)
            else:
                prices_series = pd.Series(0, index=port_df_temp.index)

            amounts = port_df_temp['amount']
            buy_prices = port_df_temp['buy_price']

            vals = amounts * prices_series
            costs = amounts * buy_prices
            pnls = vals - costs
            pnl_pcts = np.where(costs > 0, (pnls / costs * 100), 0.0)

            total_val += vals.sum()
            total_cost += costs.sum()

            port_df_temp['Coin'] = port_df_temp['name']
            port_df_temp['Amount'] = amounts
            port_df_temp['Price'] = prices_series
            port_df_temp['Value'] = vals
            port_df_temp['PnL ($)'] = pnls
            port_df_temp['PnL (%)'] = pnl_pcts

            port_data = port_df_temp[['Coin', 'Amount', 'Price', 'Value', 'PnL ($)', 'PnL (%)']].to_dict('records')

        df_port = pd.DataFrame(port_data)

        # Best/Worst Performer
        best_perf = df_port.loc[df_port['PnL (%)'].idxmax()]
        worst_perf = df_port.loc[df_port['PnL (%)'].idxmin()]

        col_p1, col_p2, col_p3, col_p4 = st.columns(4)
        col_p1.metric("Total Value", f"${total_val:,.2f}")
        tpnl = total_val - total_cost
        tpnl_pct = (tpnl/total_cost*100) if total_cost>0 else 0
        col_p2.metric("Total PnL", f"${tpnl:,.2f}", delta=f"{tpnl_pct:.2f}%")
        col_p3.metric("Top Asset", best_perf['Coin'], delta=f"{best_perf['PnL (%)']:.2f}%")

        # Diversity Score
        if total_val > 0:
            weights = (df_port['Value'] / total_val) ** 2
            hhi = weights.sum()
            div_score = (1 - hhi) * 100 # 0 to 100
            col_p4.metric("Diversity Score", f"{div_score:.1f}/100")
        else:
            col_p4.metric("Diversity Score", "N/A")

        # Technical Improvement 2: Advanced Portfolio Risk Metrics
        if len(p_ids) > 0 and total_val > 0:
            with st.spinner("Calculating Risk Metrics..."):
                port_hist = get_batch_historical_prices(p_ids, days=180)
                if not port_hist.empty:
                    # Calculate daily portfolio returns based on current weights
                    current_weights = df_port.set_index('Coin')['Value'] / total_val
                    # Map from ids to names since history uses ids as columns
                    # Actually get_batch returns ids as columns
                    port_hist.columns = [next(k for k, v in mapping.items() if v == col) for col in port_hist.columns]

                    # Align weights
                    aligned_weights = current_weights.reindex(port_hist.columns).fillna(0)

                    # Daily returns for each asset
                    daily_returns = port_hist.pct_change().dropna()

                    # Portfolio daily return
                    port_daily_return = (daily_returns * aligned_weights).sum(axis=1)

                    # Risk-free rate (assumed 2% annual)
                    rf_daily = 0.02 / 365

                    # Excess returns
                    excess_returns = port_daily_return - rf_daily

                    # Sharpe Ratio (Annualized)
                    volatility = port_daily_return.std()
                    sharpe = (excess_returns.mean() / volatility) * np.sqrt(365) if volatility > 0 else 0

                    # Sortino Ratio (Downside volatility only)
                    downside_returns = excess_returns[excess_returns < 0]
                    downside_vol = downside_returns.std()
                    sortino = (excess_returns.mean() / downside_vol) * np.sqrt(365) if downside_vol > 0 else 0

                    # Max Drawdown
                    cumulative_returns = (1 + port_daily_return).cumprod()
                    running_max = cumulative_returns.cummax()
                    drawdown = (cumulative_returns - running_max) / running_max
                    max_drawdown = drawdown.min() * 100

                    st.markdown("### 🛡️ Risk Analysis (180-Day)")
                    r_col1, r_col2, r_col3 = st.columns(3)
                    r_col1.metric("Sharpe Ratio", f"{sharpe:.2f}", help="Risk-adjusted return. >1 is good, >2 is excellent.")
                    r_col2.metric("Sortino Ratio", f"{sortino:.2f}", help="Penalizes only downside volatility. >1 is good.")
                    r_col3.metric("Max Drawdown", f"{max_drawdown:.2f}%", help="Largest single drop from peak to trough.")

                    # Optional: Plot Drawdown
                    fig_dd = go.Figure()
                    fig_dd.add_trace(go.Scatter(x=drawdown.index, y=drawdown * 100, fill='tozeroy', line=dict(color='red')))
                    fig_dd.update_layout(title="Historical Drawdown (%)", template="plotly_dark", height=200, margin=dict(t=30, b=0))
                    st.plotly_chart(fig_dd, use_container_width=True)

        st.dataframe(df_port.style.format({'Price': "${:.2f}", 'Value': "${:.2f}", 'PnL ($)': "${:.2f}", 'PnL (%)': "{:.2f}%"}))

        # Visual Improvement 5: Sunburst / Donut Upgrade
        df_port['Root'] = 'Portfolio'
        fig_pie = px.sunburst(
            df_port, path=['Root', 'Coin'], values='Value',
            color='PnL (%)', color_continuous_scale='RdYlGn', color_continuous_midpoint=0,
            title='Hierarchical Asset Allocation & Performance',
            hover_data=['Amount', 'Value', 'PnL ($)']
        )
        fig_pie.update_traces(textinfo="label+percent entry")
        fig_pie.update_layout(template="plotly_dark", height=500, margin=dict(t=50, l=25, r=25, b=25))
        st.plotly_chart(fig_pie, use_container_width=True)

        if st.button("Clear Portfolio"):
            st.session_state.confirm_clear_portfolio = True

        if st.session_state.get('confirm_clear_portfolio'):
            st.warning("⚠️ Are you sure you want to clear your entire portfolio? This action cannot be undone.")
            col_conf_yes, col_conf_no = st.columns(2)
            with col_conf_yes:
                if st.button("Yes, Clear Everything", type="primary"):
                    st.session_state.portfolio = []
                    st.session_state.confirm_clear_portfolio = False
                    st.rerun()
            with col_conf_no:
                if st.button("Cancel"):
                    st.session_state.confirm_clear_portfolio = False
                    st.rerun()

        # Future Wealth Projection
        st.markdown("---")
        st.subheader("🔮 Future Wealth Projection")
        st.write("Estimate the future value of your assets based on AI forecasts (30-day horizon).")

        port_options = list({item['name'] for item in st.session_state.portfolio})
        if port_options:
            selected_port_asset = st.selectbox("Select Asset to Project", port_options, key="port_forecast_select")

            # Find asset details (sum amount if multiple entries)
            # Simple approach: sum amount for this coin
            total_amt = sum(i['amount'] for i in st.session_state.portfolio if i['name'] == selected_port_asset)
            asset_id = next((i['id'] for i in st.session_state.portfolio if i['name'] == selected_port_asset), None)

            if asset_id and total_amt > 0:
                with st.spinner(f"Projecting value for {selected_port_asset}..."):
                     # Fetch history
                     p_hist = get_historical_prices(asset_id, days=365)
                     if not p_hist.empty:
                         # Forecast 30 days using Standard Prophet
                         p_forecast = forecast_general_ensemble(p_hist, ["Prophet (Standard)"], periods=30)

                         if not p_forecast.empty:
                             current_price = p_hist['close'].iloc[-1]
                             current_val = total_amt * current_price
                             future_price = p_forecast['yhat'].iloc[-1]
                             future_val = total_amt * future_price

                             gain_pct = ((future_val - current_val) / current_val) * 100 if current_val > 0 else 0

                             c_fw1, c_fw2 = st.columns(2)
                             c_fw1.metric("Current Value", f"${current_val:,.2f}")
                             c_fw2.metric("Projected Value (30 Days)", f"${future_val:,.2f}", delta=f"{gain_pct:.2f}%")

                             # Plot
                             fig_fw = go.Figure()
                             # History (Last 30 days)
                             disp_hist = p_hist.iloc[-30:]
                             fig_fw.add_trace(go.Scatter(x=disp_hist.index, y=disp_hist['close'] * total_amt, name='History', line=dict(color='cyan')))
                             # Forecast
                             fig_fw.add_trace(go.Scatter(x=p_forecast['ds'], y=p_forecast['yhat'] * total_amt, name='Forecast', line=dict(color='magenta', dash='dash')))

                             # Confidence
                             if 'yhat_upper' in p_forecast.columns:
                                 fig_fw.add_trace(go.Scatter(x=p_forecast['ds'], y=p_forecast['yhat_upper'] * total_amt, showlegend=False, line=dict(width=0)))
                                 fig_fw.add_trace(go.Scatter(x=p_forecast['ds'], y=p_forecast['yhat_lower'] * total_amt, fill='tonexty', showlegend=False, line=dict(width=0), fillcolor='rgba(255,0,255,0.1)'))

                             fig_fw.update_layout(title=f"Projected Value: {selected_port_asset}", template="plotly_dark", height=350, hovermode="x unified")
                             st.plotly_chart(fig_fw, use_container_width=True)
                         else:
                             st.warning("Forecast model returned no data.")
                     else:
                         st.warning("Insufficient historical data for projection.")

    else:
        st.info("Portfolio empty.")

# --- TAB 6: MARKET ---
with tab6:
    st.subheader("🌍 Market Overview")

    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.write("### 🚀 Top Gainers (24h)")
        gainers, losers = get_top_gainers_losers(limit=5)
        if not gainers.empty:
             st.dataframe(gainers.style.format({'current_price': "${:.4f}", 'price_change_percentage_24h': "{:+.2f}%"}))
        else:
            st.warning("Could not fetch gainers.")

    with col_m2:
        st.write("### 📉 Top Losers (24h)")
        if not losers.empty:
             st.dataframe(losers.style.format({'current_price': "${:.4f}", 'price_change_percentage_24h': "{:+.2f}%"}))
        else:
             st.warning("Could not fetch losers.")

    st.markdown("---")
    st.write("### 🏆 Top 50 Cryptocurrencies by Market Cap")
    with st.spinner("Fetching global market data..."):
        df_mkt = get_coin_market_cap_batch(limit=50)

        if not df_mkt.empty:
            # Treemap
            fig_tree = px.treemap(
                df_mkt, path=['symbol'], values='market_cap',
                color='price_change_percentage_24h',
                color_continuous_scale='RdYlGn',
                color_continuous_midpoint=0,
                hover_data=['name', 'current_price', 'price_change_percentage_24h'],
                title="Market Cap Visualization (Color = 24h Change)"
            )
            fig_tree.update_layout(template="plotly_dark", height=600)
            st.plotly_chart(fig_tree, use_container_width=True)

            with st.expander("View Market Data Table"):
                st.dataframe(df_mkt.style.format({'current_price': "${:.2f}", 'market_cap': "${:,.0f}"}))
        else:
            st.error("Could not load market data.")

    st.markdown("---")
    st.write("### 🌐 Global Arbitrage Scanner")
    arb_symbol = st.text_input("Enter Symbol for Arbitrage Check (e.g., BTC/USDT)", "BTC/USDT")
    if st.button("Scan Exchanges"):
        with st.spinner(f"Scanning exchanges for {arb_symbol}..."):
            arb_df = get_exchange_arbitrage(arb_symbol)
            if not arb_df.empty:
                st.dataframe(arb_df.style.format({'Price': "${:,.2f}", 'Spread %': "{:.2f}%"}))

                best_price = arb_df['Price'].max()
                best_ex = arb_df.loc[arb_df['Price'].idxmax()]['Exchange']
                worst_price = arb_df['Price'].min()
                worst_ex = arb_df.loc[arb_df['Price'].idxmin()]['Exchange']

                profit_pct = ((best_price - worst_price) / worst_price) * 100
                st.success(f"💎 Arbitrage Opportunity: Buy on **{worst_ex}** (${worst_price:,.2f}), Sell on **{best_ex}** (${best_price:,.2f}). Potential Profit: **{profit_pct:.2f}%**")
            else:
                st.warning("Could not fetch arbitrage data. Check symbol or API limits.")

# --- TAB 7: CALCULATORS ---
with tab7:
    st.subheader("🧮 Crypto Calculators")

    c_tab1, c_tab2, c_tab3, c_tab4, c_tab5, c_tab6 = st.tabs(["If I Invested...", "Moon Math", "Risk/Reward", "DCA Time Machine", "Impermanent Loss", "Options Pricing"])

    with c_tab1:
        st.write("#### 💸 If I Invested...")
        col_calc1, col_calc2 = st.columns(2)
        with col_calc1:
            inv_amount = st.number_input("Investment Amount ($)", 100, 10000, 1000, help="The initial amount in USD you want to simulate investing.")
            inv_date = st.date_input("On Date", datetime.date.today() - datetime.timedelta(days=365), help="The past date when you would have made this investment.")

        if st.button("Calculate ROI"):
            with st.spinner("Calculating ROI..."):
                # Fetch price on that date
                # We need to use history function roughly
                days_diff = (datetime.date.today() - inv_date).days
                if days_diff < 1:
                    st.warning("Date must be in the past.")
                else:
                    hist = get_historical_prices(coin_id, days=days_diff+5) # Buffer
                    if not hist.empty:
                        # Find closest date
                        closest_idx = hist.index.searchsorted(pd.Timestamp(inv_date))
                        if closest_idx < len(hist):
                            past_price = hist.iloc[closest_idx]['close']
                            curr_p = get_current_price(coin_id).get(coin_id, {}).get('usd', 0)

                            val, pct = calculate_roi(inv_amount, past_price, curr_p)
                            st.metric("Current Value", f"${val:,.2f}", delta=f"{pct:.2f}%")
                            st.write(f"Price then: ${past_price:,.2f} | Price now: ${curr_p:,.2f}")
                        else:
                            st.error("Date out of range.")
                    else:
                        st.error("Data unavailable.")

    with c_tab2:
        st.write("#### 🚀 Moon Math")
        st.write(f"Calculate the price of **{selected_option}** if it hits a target Market Cap.")

        mc_target_input = st.number_input("Target Market Cap ($)", value=1_000_000_000.0, step=1_000_000.0, help="Enter a hypothetical market cap (e.g., Bitcoin's market cap) to see what the coin price would be.")

        if st.button("Calculate Moon Price"):
            with st.spinner("Crunching the numbers..."):
                try:
                    #Input Validation for coin_id to prevent injection
                    # (Redundant due to global check, but kept for defense in depth)
                    if not validate_coin_id(coin_id):
                         st.error("Invalid Asset ID.")
                         st.stop()

                    market_data = get_coin_market_data(coin_id)
                    supply = market_data.get('circulating_supply')
                    curr_p = market_data.get('current_price')

                    if supply and curr_p is not None:
                        t_price, upside = calculate_moon_math(curr_p, supply, mc_target_input)
                        st.metric("Target Price", f"${t_price:,.4f}", delta=f"{upside:.2f}%")
                        st.write(f"Circulating Supply: {supply:,.0f}")
                    else:
                        st.error("Could not fetch supply data.")
                except Exception as e:
                    st.error(f"Error: {e}")

    with c_tab3:
        st.write("#### ⚖️ Risk/Reward Calculator")
        col_r1, col_r2, col_r3 = st.columns(3)
        entry = col_r1.number_input("Entry Price", value=0.0, help="The price at which you plan to buy (or bought) the asset.")
        stop = col_r2.number_input("Stop Loss", value=0.0, help="The price at which you will sell to limit your loss.")
        target = col_r3.number_input("Take Profit", value=0.0, help="The price at which you will sell to take your profit.")

        if entry > 0 and stop > 0 and target > 0:
            risk = abs(entry - stop)
            reward = abs(target - entry)
            rr = reward / risk if risk > 0 else 0

            st.metric("Risk / Reward Ratio", f"1 : {rr:.2f}")
            if rr >= 2:
                st.success("Good R:R Ratio!")
            elif rr < 1:
                st.warning("Poor R:R Ratio.")

    with c_tab4:
        st.write("#### ⏳ Dollar Cost Averaging (DCA) Time Machine")
        st.write("Simulate a recurring investment strategy vs. Lump Sum.")

        col_dca1, col_dca2, col_dca3 = st.columns(3)
        dca_amount = col_dca1.number_input("Recurring Amount ($)", 10, 10000, 100)
        dca_freq = col_dca2.number_input("Frequency (Days)", 1, 30, 7)
        dca_duration = col_dca3.number_input("Duration (Days)", 30, 1825, 365)

        if st.button("Run DCA Simulation"):
            with st.spinner("Travelling through time..."):
                dca_res = calculate_dca_strategy(coin_id, dca_amount, dca_freq, dca_duration)
                if dca_res:
                    st.metric("Total Invested", f"${dca_res['total_invested']:,.2f}")

                    c_dca_a, c_dca_b = st.columns(2)
                    dca_val = dca_res['dca_value']
                    lump_val = dca_res['lump_value']

                    dca_gain = ((dca_val - dca_res['total_invested']) / dca_res['total_invested']) * 100
                    lump_gain = ((lump_val - dca_res['total_invested']) / dca_res['total_invested']) * 100

                    c_dca_a.metric("DCA Final Value", f"${dca_val:,.2f}", delta=f"{dca_gain:.2f}%")
                    c_dca_b.metric("Lump Sum Value", f"${lump_val:,.2f}", delta=f"{lump_gain:.2f}%")

                    # Plot
                    hist_df = dca_res['history_df']
                    fig_dca = go.Figure()
                    fig_dca.add_trace(go.Scatter(x=hist_df.index, y=hist_df['value'], name='DCA Value', fill='tozeroy'))
                    fig_dca.add_trace(go.Scatter(x=hist_df.index, y=hist_df['invested'], name='Invested', line=dict(dash='dot')))
                    fig_dca.update_layout(title="DCA Portfolio Growth", template="plotly_dark")
                    st.plotly_chart(fig_dca, use_container_width=True)
                else:
                    st.error("Simulation failed. Check data availability.")

    with c_tab5:
        st.write("#### 💧 Impermanent Loss Calculator")
        st.write("Estimate potential loss when providing liquidity to a pool.")
        col_il1, col_il2 = st.columns(2)
        price_a = col_il1.number_input("Price Change Asset A (%)", value=0.0, step=1.0)
        price_b = col_il2.number_input("Price Change Asset B (%)", value=0.0, step=1.0)

        il_val = calculate_impermanent_loss(price_a, price_b)
        st.metric("Impermanent Loss", f"{il_val:.2f}%", delta=f"{il_val:.2f}%")
        st.info("Note: This assumes a 50/50 Liquidity Pool.")

    with c_tab6:
        st.write("#### 📈 Black-Scholes Options Pricing")
        st.write("Estimate fair value for European Call and Put options.")

        # Pre-fill S with current price if available
        current_p = get_current_price(coin_id).get(coin_id, {}).get('usd', 0)

        col_bs1, col_bs2, col_bs3 = st.columns(3)
        S = col_bs1.number_input("Current Asset Price (S)", value=float(current_p) if current_p else 1000.0, min_value=0.0)
        K = col_bs2.number_input("Strike Price (K)", value=float(current_p) * 1.1 if current_p else 1100.0, min_value=0.0)
        T_days = col_bs3.number_input("Days to Expiration", value=30, min_value=1)

        col_bs4, col_bs5, col_bs6 = st.columns(3)
        r = col_bs4.number_input("Risk-Free Rate (Annual %)", value=4.5) / 100

        # Pre-fill Volatility from history if possible
        vol_est = 50.0 # Default 50%
        hist = get_historical_prices(coin_id, days=90)
        if not hist.empty:
            vol_est = hist['close'].pct_change().std() * np.sqrt(365) * 100

        sigma = col_bs5.number_input("Implied Volatility (Annual %)", value=float(vol_est)) / 100

        if st.button("Calculate Option Price"):
            T_years = T_days / 365.0
            call, put = calculate_black_scholes(S, K, T_years, r, sigma)

            # Interactive visualization of pricing surface
            bs_c1, bs_c2 = st.columns(2)
            bs_c1.metric("Call Option Fair Value", f"${call:.2f}")
            bs_c2.metric("Put Option Fair Value", f"${put:.2f}")

            st.info("Note: Crypto options often have American exercise styles and extreme jump-risk, making Black-Scholes an approximation.")


# --- TAB 8: STATS ---
with tab8:
    st.subheader("📊 Advanced Statistics")

    vol_ohlc = get_historical_ohlc(coin_id, days=180)
    if not vol_ohlc.empty:
        vol_metrics = compute_volatility(vol_ohlc)

        fig_vol = make_subplots(specs=[[{"secondary_y": True}]])
        fig_vol.add_trace(go.Scatter(x=vol_metrics.index, y=vol_metrics['rolling_std'], name='Vol (StdDev)', line=dict(color='#FF00FF')), secondary_y=False)
        fig_vol.add_trace(go.Scatter(x=vol_metrics.index, y=vol_metrics['ATR'], name='ATR', line=dict(color='#00FFFF', dash='dot')), secondary_y=True)
        fig_vol.update_layout(title="Volatility (180d)", template="plotly_dark", height=400)
        st.plotly_chart(fig_vol, use_container_width=True)

    st.markdown("---")
    st.subheader("🐋 Whale Sonar (Volume Anomalies)")
    st.write("Detects days with unusual volume spikes (> 2x average).")

    anomalies = detect_volume_anomalies(coin_id, days=180)
    if not anomalies.empty:
        st.warning(f"Detected {len(anomalies)} volume anomalies in the last 180 days.")
        st.dataframe(anomalies.style.format({'volume': "{:,.0f}", 'vol_ma': "{:,.0f}"}))

        # Plot volume with markers
        fig_whale = go.Figure()
        fig_whale.add_trace(go.Bar(x=anomalies.index, y=anomalies['volume'], name='Whale Spike', marker_color='red'))
        fig_whale.update_layout(title="Volume Spikes", template="plotly_dark", height=300)
        st.plotly_chart(fig_whale, use_container_width=True)
    else:
        st.success("No significant volume anomalies detected recently.")

    st.markdown("---")
    metrics = get_coin_metrics(coin_id)
    if metrics:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Twitter", metrics.get('twitter_followers', 'N/A'))
        c2.metric("Reddit", metrics.get('reddit_subscribers', 'N/A'))
        c3.metric("GitHub Stars", metrics.get('stars', 'N/A'))
        c4.metric("Forks", metrics.get('forks', 'N/A'))
        st.json(metrics, expanded=False)

# --- TAB 9: CONNECT ---
with tab9:
    st.subheader("🔌 Exchange & Bot Connectivity")

    con_mode = st.radio("Connection Type", ["🏛️ Exchanges", "🤖 Freqtrade"], horizontal=True)

    # === Exchange Integration ===
    if con_mode == "🏛️ Exchanges":
        st.write("### Connect to Crypto Exchanges")
        st.info("Supports: Bitget, Gate, Bybit, OKX, KuCoin, Binance")

        # Technical Improvement 5: Session Vault Initialization
        if 'session_id' not in st.session_state:
            st.session_state.session_id = str(uuid.uuid4())

        exchange_client = get_exchange_vault(st.session_state.session_id)

        if 'exchange_connected' not in st.session_state:
            st.session_state.exchange_connected = False

        # Connection Form
        with st.expander("🔑 API Credentials", expanded=not st.session_state.exchange_connected):
            with st.form("exchange_connect_form"):
                ex_name = st.selectbox("Exchange", ["Bitget", "Gate.io", "Bybit", "OKX", "KuCoin", "Binance"])
                ex_key = st.text_input("API Key", type="password")
                ex_secret = st.text_input("API Secret", type="password")
                ex_pass = st.text_input("Passphrase (if needed)", type="password", help="Required for OKX, KuCoin, Bitget")

                submitted_ex = st.form_submit_button("Connect")

                if submitted_ex:
                    # Normalize name for CCXT
                    ex_id_map = {
                        "Bitget": "bitget", "Gate.io": "gate", "Bybit": "bybit",
                        "OKX": "okx", "KuCoin": "kucoin", "Binance": "binance"
                    }
                    target_ex = ex_id_map[ex_name]

                    success, msg = exchange_client.connect(target_ex, ex_key, ex_secret, ex_pass)
                    if success:
                        st.session_state.exchange_connected = True
                        st.session_state.connected_exchange_name = ex_name
                        st.toast(msg, icon="✅")
                            st.success(msg)
                    else:
                        st.error(msg)

        if st.session_state.exchange_connected:
            st.success(f"Connected to {st.session_state.connected_exchange_name} ✅")

            if st.button("Disconnect"):
                st.session_state.exchange_connected = False
                exchange_client = ExchangeManager() # Reset the instance
                get_exchange_vault.clear() # Clear cache for this resource
                st.rerun()

            # Balance
            st.write("#### 💰 Wallet Balance")
            if st.button("Refresh Balance"):
                st.rerun()

            bal_df, bal_err = exchange_client.get_balance()
            if bal_df is not None and not bal_df.empty:
                st.dataframe(bal_df)
                # Pie chart of assets
                fig_bal = px.sunburst(bal_df, path=['Currency'], values='Total', title='Asset Allocation (Sunburst)')
                fig_bal.update_layout(template="plotly_dark", height=300)
                st.plotly_chart(fig_bal, use_container_width=True)
            elif bal_err:
                st.error(bal_err)
            else:
                st.info("Balance is empty.")

            # Trading Interface
            st.markdown("---")
            st.write("#### 📉 Trade Execution")

            col_t1, col_t2 = st.columns(2)

            with col_t1:
                t_symbol = st.text_input("Symbol (e.g., BTC/USDT)", "BTC/USDT").upper()
                t_type = st.selectbox("Order Type", ["Limit", "Market"])
                t_side = st.selectbox("Side", ["Buy", "Sell"])

            with col_t2:
                t_amount = st.number_input("Amount", min_value=0.0, step=0.001, format="%.6f")
                t_price = st.number_input("Price (USD)", min_value=0.0, step=0.01) if t_type == "Limit" else None

            if st.button("Place Order", type="primary"):
                if t_amount > 0:
                    with st.spinner("Placing order..."):
                        order, ord_msg = exchange_client.create_order(
                            t_symbol, t_type.lower(), t_side.lower(), t_amount, t_price
                        )
                        if order:
                            st.success(ord_msg)
                            st.json(order)
                        else:
                            st.error(ord_msg)
                else:
                    st.warning("Amount must be greater than 0")

            # Open Orders
            st.markdown("---")
            with st.expander("Open Orders"):
                if st.button("Refresh Orders"):
                    st.rerun()
                orders_df, ord_err = exchange_client.fetch_open_orders(t_symbol)
                if orders_df is not None and not orders_df.empty:
                    st.dataframe(orders_df)
                elif ord_err:
                    st.error(ord_err)
                else:
                    st.info("No open orders.")

            # Order Book Analysis
            st.markdown("---")
            st.write("#### 📊 Order Book Depth Analysis")
            if st.button("Analyze Depth", key="ob_btn"):
                with st.spinner(f"Fetching L2 Order Book for {t_symbol}..."):
                    ob, err = exchange_client.get_order_book(t_symbol, limit=100)
                    if ob:
                        bids = ob.get('bids', [])
                        asks = ob.get('asks', [])

                        if bids and asks:
                            bid_df = pd.DataFrame(bids, columns=['Price', 'Volume'])
                            ask_df = pd.DataFrame(asks, columns=['Price', 'Volume'])

                            bid_df['Cumulative_Volume'] = bid_df['Volume'].cumsum()
                            ask_df['Cumulative_Volume'] = ask_df['Volume'].cumsum()

                            total_bid_vol = bid_df['Volume'].sum()
                            total_ask_vol = ask_df['Volume'].sum()
                            imbalance = total_bid_vol / (total_bid_vol + total_ask_vol)

                            ob_col1, ob_col2, ob_col3 = st.columns(3)
                            ob_col1.metric("Bid Imbalance", f"{imbalance*100:.2f}%")
                            ob_col2.metric("Total Bid Depth", f"{total_bid_vol:,.2f}")
                            ob_col3.metric("Total Ask Depth", f"{total_ask_vol:,.2f}")

                            # Visual Improvement 4: Order Book Depth Chart Visualization
                            fig_ob = go.Figure()
                            # Sort bids descending, asks ascending to create proper depth shape
                            bid_df_plot = bid_df.sort_values('Price', ascending=False)
                            bid_df_plot['Cumulative_Volume'] = bid_df_plot['Volume'].cumsum()
                            ask_df_plot = ask_df.sort_values('Price', ascending=True)
                            ask_df_plot['Cumulative_Volume'] = ask_df_plot['Volume'].cumsum()

                            fig_ob.add_trace(go.Scatter(x=bid_df_plot['Price'], y=bid_df_plot['Cumulative_Volume'], name='Bids', fill='tozeroy', fillcolor='rgba(0,255,0,0.3)', line=dict(color='#00FF00', width=2), hoverinfo='x+y', mode='lines'))
                            fig_ob.add_trace(go.Scatter(x=ask_df_plot['Price'], y=ask_df_plot['Cumulative_Volume'], name='Asks', fill='tozeroy', fillcolor='rgba(255,0,0,0.3)', line=dict(color='#FF0000', width=2), hoverinfo='x+y', mode='lines'))

                            current_price_mid = (bid_df['Price'].max() + ask_df['Price'].min()) / 2
                            fig_ob.add_vline(x=current_price_mid, line_dash="dash", line_color="gray", annotation_text="Mid Price")

                            fig_ob.update_layout(
                                title=f"L2 Market Depth for {t_symbol}",
                                xaxis_title="Price (USD)",
                                yaxis_title="Cumulative Depth",
                                template="plotly_dark",
                                hovermode="x unified",
                                height=400,
                                margin=dict(l=20, r=20, t=40, b=20)
                            )
                            st.plotly_chart(fig_ob, use_container_width=True)
                        else:
                            st.warning("Order book data is empty.")
                    else:
                        st.error(err)

    # === Freqtrade Integration ===
    elif con_mode == "🤖 Freqtrade":
        st.write("### 🤖 Freqtrade Bot Controller")

        # Technical Improvement 5: Freqtrade Session Vault
        if 'session_id' not in st.session_state:
            st.session_state.session_id = str(uuid.uuid4())

        ft_vault = get_freqtrade_vault(st.session_state.session_id)

        if 'ft_connected' not in st.session_state:
            st.session_state.ft_connected = False

        # Login Form
        with st.expander("🔌 Bot Configuration", expanded=not st.session_state.ft_connected):
            with st.form("ft_login_form"):
                ft_url = st.text_input("API URL", "http://127.0.0.1:8080")
                ft_user = st.text_input("Username", "freqtrader")
                ft_pass = st.text_input("Password", type="password")

                submitted_ft = st.form_submit_button("Connect Bot")

                if submitted_ft:
                    if not validate_url(ft_url):
                        st.error("Invalid API URL. Please enter a valid HTTP/HTTPS URL.")
                    else:
                        client = FreqtradeManager(ft_url, ft_user, ft_pass)
                        # Try login
                        success, msg = client.login()
                        if success:
                            ft_vault['client'] = client
                            st.session_state.ft_connected = True
                            st.toast(msg, icon="✅")
                            st.success(msg)
                        else:
                            st.error(msg)

        if st.session_state.ft_connected:
            st.success("Freqtrade Connected 🤖")

            client = ft_vault.get('client')

            # Controls
            col_c1, col_c2, col_c3 = st.columns(3)
            with col_c1:
                if st.button("▶️ Start Bot"):
                    res, msg = client.start_bot()
                    if res: st.toast(msg, icon="✅")
                            st.success(msg)
                    else: st.error(msg)
            with col_c2:
                if st.button("⏹️ Stop Bot"):
                    res, msg = client.stop_bot()
                    if res: st.warning(msg)
                    else: st.error(msg)
            with col_c3:
                if st.button("🔄 Refresh Status"):
                    st.rerun()

            # Status Dashboard
            status, err = client.get_status()
            if status:
                st.metric("State", status.get('state', 'Unknown'))
            elif err:
                st.error(err)

            # Profit
            st.write("#### 📉 Performance")
            profit, p_err = client.get_profit()
            if profit:
                p_col1, p_col2, p_col3 = st.columns(3)
                p_col1.metric("Total Profit %", f"{profit.get('profit_all_coin', 0):.2f}%")
                p_col2.metric("Total Profit (USDT)", f"{profit.get('profit_total_usdt', 0):.2f}")
                p_col3.metric("Trade Count", profit.get('trade_count', 0))
            elif p_err:
                st.error(p_err)

            # Whitelist
            with st.expander("📜 Whitelist"):
                wl, wl_err = client.get_whitelist()
                if wl:
                    st.write(wl)
                elif wl_err:
                    st.error(wl_err)


# --- TAB 10: ALPHA INSIGHTS ---
with tab10:
    st.markdown("""
    <div style='padding: 20px; background: rgba(0, 255, 255, 0.05); border-left: 5px solid #00FFFF; border-radius: 5px; margin-bottom: 20px;'>
        <h2 style='margin-top: 0; color: #00FFFF; font-family: "Cinzel", serif;'>💎 Alpha Insights: Institutional-Grade Market Intelligence</h2>
        <p style='font-size: 1.1rem; color: #E0E0E0;'>Leverage 5 world-class features to gain an edge in the crypto market. Track whales, farm DeFi yields, analyze sentiment, exploit arbitrage, and master tokenomics.</p>
    </div>
    """, unsafe_allow_html=True)

    alpha1, alpha2, alpha3, alpha4, alpha5 = st.tabs([
        "🐋 Whale Tracker",
        "🌾 DeFi Yields",
        "📰 Sentiment NLP",
        "💱 Arbitrage Matrix",
        "📉 Tokenomics"
    ])

    with alpha1:
        st.write("### 🐋 On-Chain Whale Tracker & Anomaly Detection")
        st.write("Detects anomalous volume spikes indicative of institutional or whale accumulation/distribution.")
        col1, col2 = st.columns([1, 4])
        with col1:
            whale_coin = st.text_input("Asset ID", value="bitcoin", key="whale_coin")
        if st.button("Scan for Whales", key="whale_btn"):
            with st.spinner(f"Scanning deep liquidity pools for {whale_coin}..."):
                whale_df = get_whale_alerts(whale_coin)
                if not whale_df.empty:
                    st.success(f"Detected {len(whale_df)} recent anomalous volume events!")
                    st.dataframe(whale_df, use_container_width=True)
                else:
                    st.info("No significant whale movements detected recently.")

    with alpha2:
        st.write("### 🌾 DeFi Yield Farming Scanner")
        st.write("Real-time APY and TVL from major DeFi protocols to identify the most lucrative yield opportunities (Powered by DefiLlama).")
        if st.button("Scan DeFi Pools", key="defi_btn"):
            with st.spinner("Fetching global DeFi yields..."):
                yields_df = get_defi_yields()
                if not yields_df.empty:
                    st.dataframe(yields_df, use_container_width=True)
                else:
                    st.error("Failed to retrieve DeFi yields.")

    with alpha3:
        st.write("### 📰 AI Sentiment & News NLP Analysis")
        st.write("Aggregates recent crypto news and performs Natural Language Processing (NLP) sentiment analysis to gauge market mood.")
        if st.button("Analyze News Sentiment", key="news_btn"):
            with st.spinner("Analyzing news headlines..."):
                news_df = get_crypto_news_sentiment()
                if not news_df.empty:

                    def style_sentiment(x):
                        x_str = str(x)
                        if 'Bullish' in x_str: return 'color: lime'
                        if 'Bearish' in x_str: return 'color: red'
                        return 'color: gray'

                    st.dataframe(
                        news_df.style.map(
                            style_sentiment,
                            subset=['Sentiment']
                        ),
                        use_container_width=True
                    )
                else:
                    st.error("Failed to analyze news sentiment.")

    with alpha4:
        st.write("### 💱 Advanced Arbitrage Matrix & Liquidity Heatmap")
        st.write("Visualizes cross-exchange spread matrices to highlight high-frequency trading arbitrage opportunities.")
        col_arb1, col_arb2 = st.columns([1, 4])
        with col_arb1:
            arb_pair = st.text_input("Trading Pair", value="BTC/USDT", key="arb_pair")
        if st.button("Scan Exchanges", key="arb_btn"):
            with st.spinner(f"Scanning order books for {arb_pair}..."):
                # Call it from the helper module (it is defined there)
                arb_df = get_exchange_arbitrage(arb_pair)
                if not arb_df.empty:

                    def style_arbitrage(x):
                        if 'Yes' in str(x): return 'color: lime; font-weight: bold'
                        return ''

                    st.dataframe(
                        arb_df.style.map(
                            style_arbitrage,
                            subset=['Arbitrage']
                        ),
                        use_container_width=True
                    )
                else:
                    st.error("Failed to retrieve exchange data or pair not found.")

    with alpha5:
        st.write("### 📉 Tokenomics & Unlocks Dashboard")
        st.write("Tracks circulating supply, max supply constraints, and emission metrics to predict supply-side pressure.")
        col_tok1, col_tok2 = st.columns([1, 4])
        with col_tok1:
            tok_coin = st.text_input("Asset ID", value="solana", key="tok_coin")
        if st.button("Analyze Tokenomics", key="tok_btn"):
            with st.spinner(f"Analyzing {tok_coin} tokenomics..."):
                tok_df = get_tokenomics_data(tok_coin)
                if not tok_df.empty:
                    st.dataframe(tok_df, use_container_width=True)
                else:
                    st.error("Failed to retrieve tokenomics data.")

# --- TAB 11: ABOUT ---

with tab11:
    st.markdown("""
    <div style='text-align: center;'>
        <h2>🧙 The Oracle Speaks 🧙</h2>
        <p style='font-size: 1.2rem; font-family: Cinzel, serif; color: #00FFFF;'>
            Welcome to the upgraded Fortune Teller v3.5!
        </p>
    </div>

    ### 🌟 New Features & Enhancements (v3.5)
    1.  **Monte Carlo Forecasting:** Geometric Brownian Motion simulations.
    2.  **Order Book Depth Analysis:** Real-time L2 Depth chart visualization.
    3.  **Black-Scholes Options Calculator:** Estimate fair value for calls/puts.
    4.  **Advanced Portfolio Risk Metrics:** Sharpe, Sortino, and Drawdown analytics.
    5.  **Prophet Auto-Tuning:** Automated grid-search optimization.
    6.  **Visual Overhaul:** Glassmorphism UI, Gauge Charts, Animated Loaders, and Interactive Heatmaps.

    ---
    *Disclaimer: This tool is for entertainment and educational purposes only. The future is always in flux.*

    <div style='text-align: center; margin-top: 20px;'>
        <p>© 2025 Crypto P • The Digital Mystic</p>
    </div>
    """, unsafe_allow_html=True)
