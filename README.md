<div align="center">

<img src="streamlit_app/assets/logo.png" alt="Crypto P's Crypto Fortune Teller Logo" width="300" style="border-radius: 50%; box-shadow: 0 0 25px #A020F0; margin-bottom: 25px;">

# <span style="font-size: 2.5em;">🔮</span> <span style="color:#A020F0; text-shadow: 0 0 10px #A020F0, 0 0 20px #FF00FF, 0 0 40px #FF00FF, 0 0 80px #FF00FF; font-weight: 900; letter-spacing: 2px;">Crypto P's Crypto Fortune Teller</span> <span style="font-size: 2.5em;">🔮</span>

**A Psychedelic Cosmic Fortune Teller of AI-Powered Crypto Analytics, Advanced Modeling & Forecasting**

<br>

[![Python Version](https://img.shields.io/badge/Python-3.11%2B-blueviolet.svg?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Streamlit App](https://img.shields.io/badge/Streamlit-App-FF4B4B.svg?style=for-the-badge&logo=streamlit&logoColor=white)](https://cryptop.coraxcolab.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-success.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)
[![Security: Checked](https://img.shields.io/badge/Security-AST%20%26%20Regex%20Checked-brightgreen.svg?style=for-the-badge)](https://github.com/PelleNybe)
[![CI](https://github.com/PelleNybe/CryptoPsFortuneTeller/actions/workflows/ci.yml/badge.svg?style=for-the-badge)](https://github.com/PelleNybe/CryptoPsFortuneTeller/actions/workflows/ci.yml)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=for-the-badge)](http://makeapullrequest.com)

<br>

<a href="https://cryptop.coraxcolab.com">
  <img src="https://img.shields.io/badge/🚀_LAUNCH_APP_NOW-FF4B4B?style=for-the-badge&logo=rocket&logoColor=white" alt="Launch App" width="300" style="box-shadow: 0 0 10px #FF4B4B; border-radius: 5px;">
</a>

<br><br>

<img src="streamlit_app/assets/crypto.gif" alt="Crypto Animation" width="800" style="border-radius: 12px; box-shadow: 0px 8px 25px rgba(160, 32, 240, 0.7); margin-bottom: 20px;">

<br>

### ✨ *Peer into the misty future of cryptocurrency prices with advanced machine learning, real-time data, and deep technical analysis.* ✨

<hr style="border: 2px solid #A020F0; border-radius: 2px; width: 85%;">

</div>

## 🌌 Discover the Future of Trading

Welcome to **Crypto P's Crypto Fortune Teller**, an interactive, stunningly designed Streamlit application that empowers you to peer into the misty future of cryptocurrency prices. By leveraging advanced machine learning models (Prophet, LSTM, ARIMA, Random Forest) and real-time data from CoinGecko, CCXT Exchanges, and Freqtrade, this tool provides price forecasts, deep technical analysis, strategy backtesting, and comprehensive market insights.

<br>

<details>
<summary><b><h3 style="display:inline-block; cursor:pointer; color: #FF00FF;">🚀 Recent Enhancements</h3></b></summary>
<br>
<ul>
  <li><b>Robust API Session Management:</b> Implemented a robust `requests.Session` with retry logic and exponential backoff for PyCoinGecko to handle rate limits and transient network errors (Technical Improvement).</li>
  <li><b>Memory Optimization via Downcasting:</b> Automatically downcasts historical dataframes (`float64` to `float32`) to reduce memory footprint, especially crucial for large batch historical data fetching (Technical Improvement).</li>
  <li><b>Auto-ARIMA Model Selection:</b> Integrated automated hyperparameter grid-search for the ARIMA model to dynamically select the optimal `(p, d, q)` order based on AIC score (Technical Improvement).</li>
  <li><b>CCXT L2 Order Book Integration:</b> Added L2 Order Book depth fetching capabilities to the `ExchangeManager` for real-time liquidity and bid-ask analysis (Technical Improvement).</li>
  <li><b>Secure Credential Management (Session Vault):</b> Utilized Streamlit's `st.cache_resource` and session UUIDs to securely store sensitive API credentials for CCXT Exchanges and Freqtrade bots (Technical Improvement).</li>
  <li><b>Dynamic Scrolling Ticker Tape:</b> Implemented a CSS-animated ticker tape displaying live top gainers and losers in the main UI (Visual Improvement).</li>
  <li><b>Psychedelic Cosmic Theme Styling:</b> Enforced a deep purple/black neon aesthetic with custom Google Fonts (`Rye`, `Cinzel`, `Quicksand`, `Orbitron`) and glassmorphism elements (Visual Improvement).</li>
  <li><b>Enhanced Fear & Greed Gauge:</b> Upgraded the Fear & Greed index display with an interactive Plotly Gauge chart (Visual Improvement).</li>
  <li><b>Hierarchical Portfolio Allocation:</b> Replaced the standard pie chart with a dynamic Plotly Sunburst chart for visualizing portfolio composition and PnL simultaneously (Visual Improvement).</li>
  <li><b>Custom Trading Signal Badges:</b> Designed styled HTML/CSS badges for "Buy/Sell/Hold" signals, dynamically colored based on model ensemble projections (Visual Improvement).</li>
</ul>
</details>

<br>

<details>
<summary><b><h3 style="display:inline-block; cursor:pointer; color: #00FFFF;">🧠 AI-Powered Forecasting</h3></b></summary>
<br>
<ul>
  <li><b>Prophet Model:</b> Utilizes Facebook's Prophet model for accurate time-series forecasting, capturing seasonality and trends with confidence intervals.</li>
  <li><b>LSTM Networks:</b> Deploys Long Short-Term Memory (Recurrent Neural Network) models to detect complex patterns in price sequences.</li>
  <li><b>Ensemble Projections:</b> 30-day ensemble forecast to estimate the future value of specific assets in your portfolio.</li>
  <li><b>Random Forest & ARIMA:</b> Advanced statistical and ensemble methods for comprehensive price prediction.</li>
  <li><b>Customizable Horizon:</b> Forecast up to 365 days into the future (capped for performance).</li>
  <li><b>Monte Carlo Simulations:</b> Geometric Brownian Motion model for probabilistic price paths.</li>
  <li><b>Hyperparameter Auto-Tuning:</b> Automated grid-search CV for finding optimal Prophet parameters.</li>
</ul>
</details>

<details>
<summary><b><h3 style="display:inline-block; cursor:pointer; color: #FFFF00;">📈 Advanced Technical Analysis</h3></b></summary>
<br>
<ul>
  <li><b>Interactive Candlestick Charts:</b> Zoom, pan, and analyze price action across multiple timeframes.</li>
  <li><b>Rich Indicator Suite:</b> SMA Ribbon, Bollinger Bands, Ichimoku Cloud, Fibonacci Levels, Pivot Points.</li>
  <li><b>Oscillators & Momentum:</b> RSI, Stochastic Oscillator, MACD, CCI, ADX, VWAP, Parabolic SAR.</li>
  <li><b>Sentiment:</b> Real-time gauge of market sentiment via Fear & Greed Index.</li>
</ul>
</details>

<details>
<summary><b><h3 style="display:inline-block; cursor:pointer; color: #FF4500;">🤖 Automated Trading & Exchanges</h3></b></summary>
<br>
<ul>
  <li><b>CCXT Integration:</b> Direct connectivity to Bitget, Gate, Bybit, OKX, KuCoin, and Binance.</li>
  <li><b>Freqtrade Bot Manager:</b> Seamlessly monitor and control your Freqtrade bot instance via direct API calls.</li>
  <li><b>Live Order Books & Volume:</b> Real-time data from major centralized exchanges.</li>
</ul>
</details>

<details>
<summary><b><h3 style="display:inline-block; cursor:pointer; color: #1E90FF;">🧪 Strategy Backtesting</h3></b></summary>
<br>
<ul>
  <li><b>Simulation Engine:</b> Test trading strategies against historical data (e.g., SMA Crossover, RSI Mean Reversion, Bollinger Squeeze, MACD Crossover).</li>
  <li><b>Performance Metrics:</b> View Total Return, Market Return, Alpha, Equity Curves, and Risk assessment.</li>
</ul>
</details>

<details>
<summary><b><h3 style="display:inline-block; cursor:pointer; color: #32CD32;">💼 Portfolio & Market Tools</h3></b></summary>
<br>
<ul>
  <li><b>Portfolio Tracker:</b> Monitor your holdings, track PnL, view allocation pie charts, and project future wealth.</li>
  <li><b>Advanced Risk Metrics:</b> Calculate Sharpe Ratio, Sortino Ratio, and Max Drawdown for your portfolio.</li>
  <li><b>Market Heatmap:</b> Visualize the top 50 coins by market cap using an interactive Treemap.</li>
  <li><b>Smart Calculators:</b> DCA, ROI, "Moon Math", Risk/Reward planning, and Black-Scholes Options Pricing.</li>
  <li><b>Order Book Depth:</b> Fetch real-time L2 order books via CCXT and visualize bid-ask imbalances.</li>
  <li><b>Social Intel:</b> Developer activity (GitHub) and community sentiment (Reddit/Twitter).</li>
</ul>
</details>

<details>
<summary><b><h3 style="display:inline-block; cursor:pointer; color: #00FF00;">💎 Alpha Insights: Institutional-Grade Intelligence</h3></b></summary>
<br>
<ul>
  <li><b>🐋 On-Chain Whale Tracker & Anomaly Detection:</b> Detect anomalous volume spikes indicative of institutional or whale accumulation/distribution.</li>
  <li><b>🌾 DeFi Yield Farming Scanner:</b> Real-time APY and TVL from major DeFi protocols to identify the most lucrative yield opportunities (Powered by DefiLlama).</li>
  <li><b>📰 AI Sentiment & News NLP Analysis:</b> Aggregates recent crypto news and performs Natural Language Processing (NLP) sentiment analysis to gauge market mood.</li>
  <li><b>💱 Advanced Arbitrage Matrix & Liquidity Heatmap:</b> Visualizes cross-exchange spread matrices to highlight high-frequency trading arbitrage opportunities across 7+ top-tier exchanges.</li>
  <li><b>📉 Tokenomics & Unlocks Dashboard:</b> Tracks circulating supply, max supply constraints, and emission metrics to predict supply-side pressure.</li>
</ul>
</details>

<br>


<div align="center">
<hr style="border: 1px solid #A020F0; width: 80%;">
</div>

## 📸 A Glimpse into the Magic

<div align="center">
  <!-- [INSERT LATEST GUI SCREENSHOT HERE] -->
  <div style="width: 48%; height: 200px; background-color: #333; display: inline-flex; align-items: center; justify-content: center; border-radius: 8px; margin: 1%; color: #fff; font-family: monospace;">[INSERT LATEST GUI SCREENSHOT HERE]</div>
  <!-- [INSERT LATEST GUI SCREENSHOT HERE] -->
  <div style="width: 48%; height: 200px; background-color: #333; display: inline-flex; align-items: center; justify-content: center; border-radius: 8px; margin: 1%; color: #fff; font-family: monospace;">[INSERT LATEST GUI SCREENSHOT HERE]</div>
  <br>
  <!-- [INSERT LATEST GUI SCREENSHOT HERE] -->
  <div style="width: 48%; height: 200px; background-color: #333; display: inline-flex; align-items: center; justify-content: center; border-radius: 8px; margin: 1%; color: #fff; font-family: monospace;">[INSERT LATEST GUI SCREENSHOT HERE]</div>
  <!-- [INSERT LATEST GUI SCREENSHOT HERE] -->
  <div style="width: 48%; height: 200px; background-color: #333; display: inline-flex; align-items: center; justify-content: center; border-radius: 8px; margin: 1%; color: #fff; font-family: monospace;">[INSERT LATEST GUI SCREENSHOT HERE]</div>
</div>

<br>
<div align="center">
<hr style="border: 1px solid #A020F0; width: 80%;">
</div>


## 👨‍💻 Meet the Mastermind

<div align="center">

This masterpiece of crypto-analytical software was conjured by **Pelle Nyberg** at **Corax CoLAB**.

<a href="https://github.com/PelleNybe">
  <img src="https://github.com/PelleNybe.png" alt="Pelle Nyberg" width="180" style="border-radius: 50%; border: 5px solid #A020F0; box-shadow: 0 0 25px #FF00FF; margin: 25px;">
</a>

### **Pelle Nyberg**
<span style="font-size: 1.2em; font-style: italic; color: #A020F0; text-shadow: 0 0 2px #A020F0;">Visionary Software Engineer & Crypto Analyst</span>

<a href="https://github.com/PelleNybe"><img src="https://img.shields.io/badge/GitHub-PelleNybe-181717?style=for-the-badge&logo=github&logoColor=white" alt="GitHub"></a>
<a href="https://www.linkedin.com/in/pellenyberg/"><img src="https://img.shields.io/badge/LinkedIn-Connect-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white" alt="LinkedIn"></a>
<a href="https://pellenybe.github.io"><img src="https://img.shields.io/badge/Portfolio-Visit_Site-005571?style=for-the-badge&logo=firefox&logoColor=white" alt="Portfolio"></a>
<a href="https://cryptop.coraxcolab.com"><img src="https://img.shields.io/badge/Crypto_P-Live_App-A020F0?style=for-the-badge&logo=streamlit&logoColor=white" alt="Crypto P App"></a>

<br><br>

### **Corax CoLAB**
<span style="font-size: 1.2em; font-style: italic; color: #00FFFF; text-shadow: 0 0 2px #00FFFF;">Innovating the Digital Frontier</span>

<a href="https://coraxcolab.com"><img src="https://img.shields.io/badge/Corax_CoLAB-Official_Website-FF6B6B?style=for-the-badge&logo=googlechrome&logoColor=white" alt="Corax CoLAB"></a>

<br><br>
<i>Empowering traders and developers with cutting-edge tools and futuristic insights.</i>
<br><br>

</div>
<div align="center">
<hr style="border: 1px solid #A020F0; width: 80%;">
</div>

## 🎨 A Psychedelic Cosmic Fortune Teller Theme

The UI enforces a **'Psychedelic Cosmic Fortune Teller'** theme, utilizing dark-themed neon accents, deep purple/black radial gradients, and custom Google Fonts (`Rye`, `Cinzel`, `Quicksand`, `Orbitron`). It’s an immersive, trippy, yet highly professional analytics experience that transports you to another dimension while keeping you grounded in solid data.

<br>

## 🛡️ Enterprise-Grade Security & Architecture

We take security seriously. This application includes:
- 🔒 **XSS & SSRF Protection:** Automated AST-based XSS scanners and strict URL validators.
- 🗄️ **Session Vault:** Secure server-side caching of sensitive credentials (Exchange/Freqtrade keys).
- ⚡ **Tiered Bucket Caching:** Optimized API calls via Streamlit `@st.cache_data`.
- 🧪 **Rigorous Test Suite:** Over a dozen test files covering backtesting, ML models, ensemble logic, API endpoints, and security configurations.

<br>

<details>
<summary><b><h3 style="display:inline-block; cursor:pointer; color: #FF1493;">🛠️ Tech Stack & Dependencies</h3></b></summary>
<br>

<div align="center">
  <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white" alt="Streamlit">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white" alt="Pandas">
  <img src="https://img.shields.io/badge/Numpy-777BB4?style=for-the-badge&logo=numpy&logoColor=white" alt="Numpy">
  <img src="https://img.shields.io/badge/Plotly-239120?style=for-the-badge&logo=plotly&logoColor=white" alt="Plotly">
  <img src="https://img.shields.io/badge/TensorFlow-FF6F00?style=for-the-badge&logo=tensorflow&logoColor=white" alt="TensorFlow">
  <img src="https://img.shields.io/badge/scikit--learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white" alt="Scikit-Learn">
</div>

*   **Frontend & Framework:** Streamlit
*   **Data & Math:** Pandas, NumPy (`>=1.25.0,<2.0.0`)
*   **Visualization:** Plotly
*   **Machine Learning:** Facebook Prophet, TensorFlow/Keras (LSTM), Scikit-Learn, Statsmodels
*   **Crypto & APIs:** PyCoinGecko, CCXT (Exchanges), Requests
</details>

<br>

<details>
<summary><b><h3 style="display:inline-block; cursor:pointer; color: #FFA500;">📂 Project Structure Snapshot</h3></b></summary>
<br>

```text
CryptoPsFortuneTeller/
├── streamlit_app/
│   ├── assets/
│   │   ├── logo.png               # App logo
│   │   └── crypto.gif             # Animation
│   ├── modules/
│   │   ├── cryptop_crypto_fortune_teller_helper.py  # Indicators, Data fetching
│   │   ├── cryptop_crypto_fortune_teller_models.py  # Prophet, LSTM, ARIMA, RF
│   │   ├── cryptop_crypto_fortune_teller_styles.py  # Psychedelic CSS Theme
│   │   ├── exchange_manager.py                      # CCXT Connectivity
│   │   └── freqtrade_manager.py                     # Freqtrade API control
│   └── cryptop_crypto_fortune_teller_main.py      # Entry point
├── benchmarks/                    # Performance benchmarking (LSTM, Prophet, Caching)
├── tests/                         # Extensive Pytest & Unittest suite
├── health_check.py                # Environment & API validation
└── requirements.txt               # Pinned dependencies (e.g. numpy<2.0.0)
```
</details>

<details>
<summary><b><h3 style="display:inline-block; cursor:pointer; color: #00FF00;">💎 Alpha Insights: Institutional-Grade Intelligence</h3></b></summary>
<br>
<ul>
  <li><b>🐋 On-Chain Whale Tracker & Anomaly Detection:</b> Detect anomalous volume spikes indicative of institutional or whale accumulation/distribution.</li>
  <li><b>🌾 DeFi Yield Farming Scanner:</b> Real-time APY and TVL from major DeFi protocols to identify the most lucrative yield opportunities (Powered by DefiLlama).</li>
  <li><b>📰 AI Sentiment & News NLP Analysis:</b> Aggregates recent crypto news and performs Natural Language Processing (NLP) sentiment analysis to gauge market mood.</li>
  <li><b>💱 Advanced Arbitrage Matrix & Liquidity Heatmap:</b> Visualizes cross-exchange spread matrices to highlight high-frequency trading arbitrage opportunities across 7+ top-tier exchanges.</li>
  <li><b>📉 Tokenomics & Unlocks Dashboard:</b> Tracks circulating supply, max supply constraints, and emission metrics to predict supply-side pressure.</li>
</ul>
</details>

<br>

<div align="center">
<hr style="border: 1px solid #A020F0; width: 80%;">
</div>

## ⚙️ Installation & Local Development

### 1. Clone & Setup
```bash
git clone https://github.com/PelleNybe/CryptoPsFortuneTeller.git
cd CryptoPsFortuneTeller
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Environment Variables
For local development, copy the `.env.example` file to `.env` and configure your API keys (optional, as the UI currently prompts for credentials).
```bash
cp .env.example .env
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Health Check & Tests
Verify your environment and API connectivity:
```bash
python3 health_check.py
python3 -m pytest
```

### 4. Launch the Fortune Teller
```bash
streamlit run streamlit_app/cryptop_crypto_fortune_teller_main.py
```

<div align="center">
<hr style="border: 1px solid #A020F0; width: 80%;">
</div>

## ⚠️ Disclaimer

**This application is for educational and entertainment purposes only.**

The price forecasts, backtests, and technical analysis provided by this tool are based on historical data and machine learning algorithms, which cannot predict the future with certainty. Cryptocurrency markets are highly volatile. **This is not financial advice.** Always conduct your own research and never invest more than you can afford to lose.

<div align="center">
<hr style="border: 1px solid #A020F0; width: 80%;">
</div>

## 🤝 Community & Contributing

We love contributions from the community! Whether it's fixing bugs, adding new features, or improving documentation, your help is welcome.

*   **[Read our Contributing Guidelines](CONTRIBUTING.md)** to learn how to get started.
*   **[Review our Code of Conduct](CODE_OF_CONDUCT.md)** to understand the standards for participating in our community.
*   **[Check our Security Policy](SECURITY.md)** if you need to report a vulnerability privately.

If you like the project, please consider giving it a ⭐ Star, sharing it with your friends, or Forking it to make your own changes!

<br>

<div align="center">
  <p><b>Built with ❤️ by Pelle Nyberg & Corax CoLAB</b></p>
  <p>&copy; 2024 Corax CoLAB. All rights reserved.</p>

  <img src="streamlit_app/assets/logo.png" width="100" style="opacity: 0.5;">
</div>
