def apply_custom_css():
    import streamlit as st
    st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Rye&family=Cinzel:wght@400;700&family=Quicksand:wght@300;400;700&family=Orbitron:wght@400;700&display=swap');

    /* Global Fonts */
    html, body, [class*="css"] {
        font-family: 'Quicksand', sans-serif;
        color: #e0f7fa;
    }

    /* Headers - Mystical & Bold */
    h1, h2, h3 {
        font-family: 'Rye', cursive !important;
        color: #FFD700 !important; /* Gold */
        text-shadow: 0 0 10px #FFD700, 2px 2px 4px #000000;
        letter-spacing: 1.5px;
    }

    h4, h5, h6 {
        font-family: 'Cinzel', serif !important;
        color: #00FFFF !important; /* Cyan */
        text-shadow: 0 0 5px #00FFFF;
    }

    /* Main Background - Deep Psychedelic Cosmic Fortune Teller */
    .stApp {
        background: radial-gradient(circle at center, #2a0e3b 0%, #150020 60%, #000000 100%);
        background-attachment: fixed;
    }

    /* Sidebar - Glassmorphism Pro */
    [data-testid="stSidebar"] {
        background-color: rgba(14, 0, 24, 0.9) !important;
        backdrop-filter: blur(15px);
        border-right: 1px solid rgba(255, 0, 255, 0.3);
        box-shadow: 10px 0 30px rgba(0, 0, 0, 0.5);
    }

    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: #d1c4e9;
        font-size: 0.9rem;
    }

    /* Tabs styling - Floating Cards */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: transparent;
        padding-bottom: 10px;
        border-bottom: 1px solid rgba(255, 0, 255, 0.2);
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 0, 255, 0.2);
        border-radius: 8px;
        color: #ff79c6;
        font-family: 'Cinzel', serif;
        font-weight: 700;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #FF00FF 0%, #9900ff 100%) !important;
        color: #fff !important;
        border: 1px solid #fff;
        box-shadow: 0 0 15px rgba(255, 0, 255, 0.6);
        transform: translateY(-3px);
    }
    .stTabs [data-baseweb="tab"]:hover {
        background-color: rgba(255, 0, 255, 0.1);
        border-color: #FF00FF;
        color: #FF00FF;
    }

    /* Metric Cards - Crystal Ball Glow */
    [data-testid="stMetricValue"] {
        font-family: 'Orbitron', sans-serif; /* Tech feel for numbers */
        font-size: 2.5rem !important;
        color: #00FFFF !important;
        text-shadow: 0 0 15px rgba(0, 255, 255, 0.6);
    }
    [data-testid="stMetricLabel"] {
        color: #bd93f9;
        font-family: 'Cinzel', serif;
        font-size: 1rem !important;
        text-transform: uppercase;
    }
    [data-testid="stMetricDelta"] {
        font-family: 'Quicksand', sans-serif;
        font-weight: 700;
    }

    /* Inputs - Cyberpunk Fields */
    .stSelectbox > div > div, .stTextInput > div > div, .stNumberInput > div > div {
        background-color: rgba(0, 0, 0, 0.6);
        border: 1px solid #bd93f9;
        color: #fff;
        border-radius: 8px;
    }
    .stSelectbox > div > div:hover, .stTextInput > div > div:hover {
        border-color: #00FFFF;
        box-shadow: 0 0 8px rgba(0, 255, 255, 0.3);
    }

    /* Buttons - Magic Pulse */
    .stButton button {
        background: linear-gradient(90deg, #FF00FF, #8A2BE2);
        color: #fff;
        font-family: 'Cinzel', serif;
        font-weight: bold;
        border: 1px solid rgba(255, 255, 255, 0.5);
        border-radius: 30px;
        padding: 0.5rem 2rem;
        box-shadow: 0 4px 15px rgba(138, 43, 226, 0.5);
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 1.5px;
    }

    @keyframes pulse-glow {
        0% { box-shadow: 0 0 0 0 rgba(255, 0, 255, 0.7); }
        70% { box-shadow: 0 0 0 10px rgba(255, 0, 255, 0); }
        100% { box-shadow: 0 0 0 0 rgba(255, 0, 255, 0); }
    }

    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 25px rgba(255, 0, 255, 0.8);
        border-color: #00FFFF;
        color: #00FFFF;
        animation: pulse-glow 1.5s infinite;
    }

    .stButton button:active {
        transform: translateY(1px);
    }

    /* Expander - Secret Scroll */
    .streamlit-expanderHeader {
        font-family: 'Cinzel', serif;
        color: #ff79c6;
        background-color: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(189, 147, 249, 0.2);
        border-radius: 8px;
    }
    .streamlit-expanderContent {
        background-color: rgba(0, 0, 0, 0.2);
        border: 1px solid rgba(189, 147, 249, 0.1);
        border-radius: 0 0 8px 8px;
    }

    /* Dataframe/Table - Futuristic Terminal */
    [data-testid="stDataFrame"] {
        border: 1px solid rgba(0, 255, 255, 0.2);
        border-radius: 8px;
        background-color: rgba(0, 0, 0, 0.4);
    }
    [data-testid="stDataFrame"] th {
        color: #FF00FF !important;
        font-family: 'Orbitron', sans-serif;
    }

    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #0e0018;
    }
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #FF00FF, #00FFFF);
        border-radius: 4px;
    }

    /* Image glow */
    img {
        filter: drop-shadow(0 0 10px rgba(255, 0, 255, 0.4));
        transition: transform 0.3s ease;
    }
    img:hover {
        transform: scale(1.02);
    }

    /* Divider - Laser Beam */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, #FF00FF, #00FFFF, transparent);
        margin-top: 2rem;
        margin-bottom: 2rem;
        opacity: 0.8;
    }

    /* Alerts */
    [data-testid="stNotification"], .stAlert {
        background-color: rgba(20, 20, 40, 0.9);
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
    }


    /* Visual Improvement 2: Magic Orb Loader */
    .stSpinner > div > div {
        border-color: #FF00FF transparent #00FFFF transparent !important;
        animation: spin-magic 1.2s cubic-bezier(0.5, 0, 0.5, 1) infinite !important;
        border-width: 4px !important;
        width: 30px !important;
        height: 30px !important;
        box-shadow: 0 0 15px rgba(255, 0, 255, 0.5);
    }

    .stSpinner > div {
        color: #bd93f9 !important;
        font-family: 'Cinzel', serif !important;
        font-weight: bold;
        text-shadow: 0 0 5px #FF00FF;
    }

    @keyframes spin-magic {
        0% { transform: rotate(0deg) scale(1); }
        50% { transform: rotate(180deg) scale(1.2); }
        100% { transform: rotate(360deg) scale(1); }
    }


    /* Visual Improvement 3: Glassmorphism Metric Cards */
    [data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(10px) saturate(150%);
        -webkit-backdrop-filter: blur(10px) saturate(150%);
        border: 1px solid rgba(0, 255, 255, 0.3);
        border-radius: 15px;
        padding: 15px 20px;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        position: relative;
        overflow: hidden;
    }

    /* Neon Top Border Glow */
    [data-testid="metric-container"]::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent, #00FFFF, #FF00FF, transparent);
    }

    [data-testid="metric-container"]:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px 0 rgba(0, 255, 255, 0.4);
        border-color: #FF00FF;
    }


        /* Visual Improvement 5: Glassmorphism UI Elements and Custom Loader */

        /* Glassmorphism for expanders and metrics */
        .streamlit-expanderHeader {
            background: rgba(20, 0, 30, 0.4) !important;
            backdrop-filter: blur(10px) !important;
            -webkit-backdrop-filter: blur(10px) !important;
            border-radius: 12px 12px 0 0 !important;
            border-bottom: 1px solid rgba(255, 0, 255, 0.3) !important;
        }

        .streamlit-expanderContent {
            background: rgba(10, 0, 20, 0.6) !important;
            backdrop-filter: blur(10px) !important;
            -webkit-backdrop-filter: blur(10px) !important;
            border-radius: 0 0 12px 12px !important;
            border: 1px solid rgba(0, 255, 255, 0.2) !important;
            border-top: none !important;
        }

        div[data-testid="stMetricValue"] {
            background: linear-gradient(135deg, rgba(255,0,255,0.1) 0%, rgba(0,255,255,0.1) 100%);
            padding: 10px 15px;
            border-radius: 8px;
            backdrop-filter: blur(5px);
            border: 1px solid rgba(255,255,255,0.1);
            text-shadow: 0 0 5px rgba(255, 255, 255, 0.5);
            display: inline-block;
        }

        /* Animated neon borders for dataframes */
        div[data-testid="stDataFrame"] {
            border: 2px solid transparent;
            border-image: linear-gradient(45deg, #FF00FF, #00FFFF) 1;
            box-shadow: 0 0 15px rgba(255, 0, 255, 0.2);
            animation: pulse-border 3s infinite alternate;
        }

        @keyframes pulse-border {
            0% { box-shadow: 0 0 5px rgba(0, 255, 255, 0.2); }
            100% { box-shadow: 0 0 20px rgba(255, 0, 255, 0.5); }
        }

        /* Custom Spinner/Loader Styling override */
        .stSpinner > div > div {
            border-top-color: #FF00FF !important;
            border-right-color: #00FFFF !important;
            border-bottom-color: #FF00FF !important;
            border-left-color: #00FFFF !important;
            animation: spin 1s linear infinite, color-shift 3s ease-in-out infinite alternate !important;
        }

        @keyframes color-shift {
            0% { filter: hue-rotate(0deg); }
            100% { filter: hue-rotate(360deg); }
        }


        /* Visual Improvement 6: Enhanced Tables */
        [data-testid="stDataFrame"] tbody tr:hover {
            background-color: rgba(255, 0, 255, 0.1) !important;
            transition: background-color 0.2s ease;
        }

        [data-testid="stDataFrame"] td {
            color: #d1c4e9 !important;
        }

        /* General nice glow on the whole app */
        .stApp::before {
            content: '';
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            box-shadow: inset 0 0 100px rgba(153, 0, 255, 0.1);
            pointer-events: none;
            z-index: 9999;
        }


    /* Visual Improvement 8: Enhanced Global Glow */
    .stApp {
        background: radial-gradient(circle at center, #1b092b 0%, #0d0014 60%, #000000 100%) !important;
    }

    .stMarkdown h1 {
        background: -webkit-linear-gradient(45deg, #FF00FF, #00FFFF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 20px rgba(255,0,255,0.4);
    }

    [data-testid="stSidebar"] {
        border-right: 1px solid rgba(0, 255, 255, 0.2) !important;
        background: rgba(10, 0, 20, 0.85) !important;
    }

    /* Interactive metric glow on hover */
    [data-testid="stMetricValue"]:hover {
        transform: scale(1.05);
        transition: transform 0.2s ease;
        text-shadow: 0 0 25px rgba(0, 255, 255, 0.8);
    }

</style>
""", unsafe_allow_html=True)
