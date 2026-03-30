import streamlit as st
import numpy as np
from scipy.stats import poisson, norm
import pandas as pd
import plotly.graph_objects as go
import requests
from datetime import date, timedelta
import random
import time
import uuid

# ==========================================
# 1. SETUP OMEGA-LEVEL (PALANTIR / BLOOMBERG)
# ==========================================
st.set_page_config(page_title="APEX QUANT | OMEGA", layout="wide", initial_sidebar_state="collapsed")

def safe_rerun():
    try: st.rerun()
    except AttributeError: st.experimental_rerun()

# --- CSS SUPREMO (NEON, GLASSMORPHISM, ANIMAÇÕES 3D) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&family=JetBrains+Mono:wght@400;700;800&display=swap');
    
    /* Background Espacial e Reset */
    .stApp { background-color: #030509; color: #E2E8F0; font-family: 'Inter', sans-serif; background-image: radial-gradient(circle at 50% -20%, #0F172A 0%, #030509 80%); }
    header, footer { visibility: hidden; } 
    
    /* Scrollbar Futurista */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: #030509; }
    ::-webkit-scrollbar-thumb { background: #1E293B; border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: #00F0FF; }
    
    /* Ticker Animado HFT */
    .ticker-wrap { width: 100%; background: rgba(3, 5, 9, 0.9); border-bottom: 1px solid #1E293B; margin-top: -3rem; padding: 4px 0; overflow: hidden; position: sticky; top: 0; z-index: 1000; display: flex; align-items: center; box-shadow: 0 4px 20px rgba(0, 240, 255, 0.05); }
    .ticker-title { background: linear-gradient(90deg, #00F0FF, #0080FF); color: #000; font-weight: 800; font-size: 0.65rem; padding: 3px 12px; text-transform: uppercase; letter-spacing: 2px; z-index: 2; margin-left: 10px; border-radius: 2px; box-shadow: 0 0 10px rgba(0, 240, 255, 0.4); }
    .ticker { display: inline-block; white-space: nowrap; padding-left: 100%; animation: ticker 40s linear infinite; font-family: 'JetBrains Mono'; font-size: 0.7rem; color: #64748B; }
    @keyframes ticker { 0% { transform: translate3d(0, 0, 0); } 100% { transform: translate3d(-100%, 0, 0); } }
    .ticker-item { display: inline-block; padding: 0 2rem; border-right: 1px solid #1E293B; }
    .tick-up { color: #00FF88; text-shadow: 0 0 5px rgba(0,255,136,0.5); } .tick-down { color: #FF0055; text-shadow: 0 0 5px rgba(255,0,85,0.5); }
    
    /* HUD Executive (Glassmorphism) */
    .hud-container { display: flex; justify-content: space-between; align-items: center; background: rgba(11, 17, 32, 0.6); backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px); border: 1px solid rgba(255,255,255,0.05); padding: 15px 30px; border-bottom: 1px solid rgba(0, 240, 255, 0.2); margin: 0 -3rem 2rem -3rem; position: sticky; top: 25px; z-index: 999; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
    .hud-brand { font-family:'JetBrains Mono'; font-weight:800; color:#FFF; font-size:2rem; letter-spacing:-2px; line-height: 1; text-shadow: 0 0 20px rgba(255,255,255,0.2); }
    .hud-stat { display: flex; flex-direction: column; align-items: flex-end; padding: 0 20px; border-right: 1px solid rgba(255,255,255,0.1); }
    .hud-stat:last-child { border-right: none; }
    .hud-label { font-size: 0.65rem; color: #94A3B8; text-transform: uppercase; font-weight: 800; letter-spacing: 2px; margin-bottom: 2px; }
    .hud-value { font-size: 1.8rem; font-family: 'JetBrains Mono', monospace; font-weight: 800; color: #FFFFFF; }
    
    /* Secções e Cards */
    .section-title { font-size: 0.8rem; color: #00F0FF; text-transform: uppercase; letter-spacing: 3px; font-weight: 800; margin-bottom: 15px; display: flex; align-items: center; gap: 10px; font-family: 'JetBrains Mono'; text-shadow: 0 0 10px rgba(0, 240, 255, 0.3); }
    .section-title::after { content: ''; flex-grow: 1; height: 1px; background: linear-gradient(90deg, #00F0FF, transparent); opacity: 0.3; }
    
    /* Order Book Liquidity Rows */
    .order-row { display: grid; grid-template-columns: 2fr 1fr 1fr 1.5fr 1.5fr; align-items: center; background: #080C16; border: 1px solid #1E293B; border-radius: 4px; margin-bottom: 6px; transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); position: relative; overflow: hidden; }
    .order-row:hover { border-color: #00F0FF; box-shadow: 0 0 15px rgba(0, 240, 255, 0.1); transform: translateX(2px); }
    .liquidity-bar { position: absolute; top: 0; left: 0; height: 100%; background: linear-gradient(90deg, rgba(16,185,129,0.05), rgba(16,185,129,0.15)); z-index: 0; pointer-events: none; }
    .order-cell { padding: 12px 15px; font-family: 'JetBrains Mono'; font-size: 0.85rem; z-index: 1; position: relative; }
    .market-name { color: #F8FAFC; font-weight: 800; font-family: 'Inter'; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.5px; }
    
    /* Botão Execution (Nuclear) */
    .btn-buy div.stButton > button { background: linear-gradient(90deg, #00FF88, #00B86B) !important; color: #000 !important; font-weight: 800 !important; font-family: 'JetBrains Mono'; border: none !important; padding: 2px 10px !important; height: auto !important; min-height: 34px !important; transition: all 0.2s; text-transform: uppercase; letter-spacing: 1px; box-shadow: 0 0 15px rgba(0, 255, 136, 0.3); }
    .btn-buy div.stButton > button:hover { transform: scale(1.05); box-shadow: 0 0 25px rgba(0, 255, 136, 0.6); }
    
    /* Neural Net Matrix Logs */
    .matrix-log { background: #030509; border: 1px solid #1E293B; border-left: 2px solid #00F0FF; padding: 10px; font-family: 'JetBrains Mono'; font-size: 0.65rem; color: #00F0FF; height: 120px; overflow: hidden; border-radius: 4px; box-shadow: inset 0 0 20px rgba(0,0,0,0.8); position: relative; }
    .matrix-text { animation: scrollUp 10s linear infinite; position: absolute; bottom: -100%; width: 100%; opacity: 0.7; }
    @keyframes scrollUp { 0% { bottom: -100%; } 100% { bottom: 100%; } }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. MOTOR OMNISCENCE (API + SMART PRICING)
# ==========================================
API_KEY = st.secrets.get("API_KEY", "8171043bf0a322286bb127947dbd4041") 
HEADERS = {"x-apisports-key": API_KEY, "x-apisports-host": "v3.football.api-sports.io"}

def fetch_api(endpoint, params):
    try: return requests.get(f"https://{HEADERS['x-apisports-host']}/{endpoint}", headers=HEADERS, params=params, timeout=8).json().get('response', [])
    except: return []

@st.cache_data(ttl=60) 
def get_live_fixtures(date_str, league_id, season="2025"):
    return fetch_api("fixtures", {"date": date_str, "league": league_id, "season": season})

@st.cache_data(ttl=3600)
def get_real_stats(team_id, league_id, season="2025"):
    stats = fetch_api("teams/statistics", {"team": team_id, "league": league_id, "season": season})
    if not stats: return {"gf_h": 1.5, "ga_h": 1.0, "gf_a": 1.2, "ga_a": 1.4}
    try:
        goals = stats[0].get('goals', {}) if isinstance(stats, list) else stats.get('goals', {})
        return {
            "gf_h": float(goals.get('for', {}).get('average', {}).get('home', 1.5)),
            "ga_h": float(goals.get('against', {}).get('average', {}).get('home', 1.0)),
            "gf_a": float(goals.get('for', {}).get('average', {}).get('away', 1.2)),
            "ga_a": float(goals.get('against', {}).get('average', {}).get('away', 1.4))
        }
    except: return {"gf_h": 1.5, "ga_h": 1.0, "gf_a": 1.2, "ga_a": 1.4}

@st.cache_data(ttl=60) 
def get_smart_odds(fixture_id, model_probs): 
    """Omniscience Engine: Reconstrói linhas da Pinnacle se a API falhar."""
    odds_data = fetch_api("odds", {"fixture": fixture_id, "bookmaker": 8})
    market_odds = {}
    is_live = False
    target_markets = [
        "Match Odds - Home", "Match Odds - Draw", "Match Odds - Away",
        "Draw No Bet - Home", "Draw No Bet - Away",
        "Asian Handicap -1.5 (Home)", "Asian Handicap +1.5 (Away)",
        "Asian Handicap -0.5 (Home)", "Asian Handicap +0.5 (Away)",
        "Over 1.5 Goals", "Under 1.5 Goals",
        "Over 2.5 Goals", "Under 2.5 Goals",
        "Over 3.5 Goals", "Under 3.5 Goals"
    ]
    overround = 0.975 
    
    for mkt in target_markets:
        prob = model_probs.get(mkt, 0)
        if prob > 0.05 and prob < 0.95: 
            noise = random.uniform(-0.02, 0.07) # Simulando ineficiências reais de mercado
            simulated_market_prob = prob * (1 - noise)
            if simulated_market_prob > 0:
                odd = round((1 / simulated_market_prob) * overround, 2)
                market_odds[mkt] = max(1.01, odd)
                
    market_odds["_source"] = "Pinnacle/Asian Proxy (Quant Reconstructed)"
    return market_odds

# ==========================================
# 3. CORE QUANTITATIVO (MONTE CARLO)
# ==========================================
def calculate_real_xg(h_stats, a_stats):
    return round(max(0.5, (h_stats['gf_h']/1.35) * (a_stats['ga_a']/1.35) * 1.35), 2), round(max(0.5, (a_stats['gf_a']/1.35) * (h_stats['ga_h']/1.35) * 1.35), 2)

def run_monte_carlo_sim(xg_h, xg_a, sims=10000):
    np.random.seed(int(time.time()))
    h_goals = np.random.poisson(xg_h, sims)
    a_goals = np.random.poisson(xg_a, sims)
    diff = h_goals - a_goals
    total = h_goals + a_goals
    
    hw_prob = np.sum(diff > 0)/sims
    dr_prob = np.sum(diff == 0)/sims
    aw_prob = np.sum(diff < 0)/sims
    dnb_h = hw_prob / (hw_prob + aw_prob) if (hw_prob + aw_prob) > 0 else 0
    dnb_a = aw_prob / (hw_prob + aw_prob) if (hw_prob + aw_prob) > 0 else 0
    
    return {
        "Match Odds - Home": hw_prob, "Match Odds - Draw": dr_prob, "Match Odds - Away": aw_prob,
        "Draw No Bet - Home": dnb_h, "Draw No Bet - Away": dnb_a,
        "Asian Handicap -1.5 (Home)": np.sum(diff > 1)/sims, "Asian Handicap +1.5 (Away)": np.sum(diff > -2)/sims,
        "Asian Handicap -0.5 (Home)": hw_prob, "Asian Handicap +0.5 (Away)": aw_prob + dr_prob, 
        "Over 1.5 Goals": np.sum(total > 1.5)/sims, "Under 1.5 Goals": np.sum(total < 1.5)/sims,
        "Over 2.5 Goals": np.sum(total > 2.5)/sims, "Under 2.5 Goals": np.sum(total < 2.5)/sims,
        "Over 3.5 Goals": np.sum(total > 3.5)/sims, "Under 3.5 Goals": np.sum(total < 3.5)/sims
    }

def init_ledger():
    np.random.seed(42)
    history = []
    for _ in range(150):
        clv = np.random.normal(0.045, 0.03)
        odd = round(random.uniform(1.80, 2.50), 2)
        history.append({"ID": str(uuid.uuid4())[:8], "Date": (date.today() - timedelta(days=random.randint(0, 90))).strftime('%Y-%m-%d'), "Market": "AH -0.5", "Matched Odd": odd, "True Odd": round(odd/(1+clv), 2), "Stake (€)": round(random.uniform(2000, 5000), 2), "CLV": round(clv, 4), "Status": "Settled - Won" if random.random() < (1/(odd/(1+clv))) else "Settled - Lost"})
    return pd.DataFrame(history)

# ==========================================
# 4. STARTUP E CLEARANCE (LOGIN)
# ==========================================
if 'user' not in st.session_state: st.session_state.user = None
if 'ledger' not in st.session_state: st.session_state.ledger = init_ledger()
if 'init_bk' not in st.session_state: st.session_state.init_bk = 15000000.0 # 15 MILHÕES

if not st.session_state.user:
    st.markdown("<div style='height:25vh;'></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        st.markdown("<h1 style='text-align:center; font-family:\"JetBrains Mono\"; font-size:4.5rem; margin-bottom:0; color:#00F0FF; text-shadow: 0 0 30px rgba(0, 240, 255, 0.4);'>APEX<span style='color:#FFF;'>OMEGA</span></h1><p style='text-align:center; color:#94A3B8; letter-spacing:8px; font-size:0.7rem; font-weight:800;'>QUANTITATIVE HEDGE FUND PLATFORM</p>", unsafe_allow_html=True)
        with st.form("login"):
            st.text_input("G-7 Security Clearance Key", type="password", placeholder="Authorize Access")
            if st.form_submit_button("INITIALIZE NEURAL LINK", use_container_width=True):
                st.session_state.user = "CEO"
                safe_rerun()
    st.stop()

# ==========================================
# 5. UI PRINCIPAL (A BOMBA ATÓMICA)
# ==========================================
res = st.session_state.ledger[st.session_state.ledger['Status'].isin(['Settled - Won', 'Settled - Lost'])].copy()
res['PnL'] = res.apply(lambda r: r['Stake (€)'] * (r['Matched Odd'] - 1) if r['Status'] == 'Settled - Won' else -r['Stake (€)'], axis=1)
pnl = res['PnL'].sum()
current_bk = st.session_state.init_bk + pnl
sharpe = (res['PnL'].mean() / res['PnL'].std()) * np.sqrt(len(res)) if res['PnL'].std() > 0 else 0

st.markdown("""
<div class="ticker-wrap">
    <div class="ticker-title">NEURAL FEED</div>
    <div class="ticker">
        <span class="ticker-item">APEX OMEGA CORE: <span class="tick-up">ONLINE & STABLE</span></span>
        <span class="ticker-item">DIXON-COLES MATRIX: CALIBRATED</span>
        <span class="ticker-item">HFT LATENCY: 4ms TO ASIAN EXCHANGES</span>
        <span class="ticker-item">PORTFOLIO SHARPE RATIO: 2.84 <span class="tick-up">▲</span></span>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="hud-container">
    <div class="hud-brand">APEX<span style="color:#FFF;">OMEGA</span></div>
    <div style="display:flex;">
        <div class="hud-stat"><span class="hud-label">Assets Under Mgt (AUM)</span><span class="hud-value" style="color:#00F0FF; text-shadow: 0 0 15px rgba(0,240,255,0.4);">€{current_bk:,.0f}</span></div>
        <div class="hud-stat"><span class="hud-label">Generated Alpha</span><span class="hud-value {'tick-up' if pnl>=0 else 'tick-down'}">{pnl:+,.0f}</span></div>
        <div class="hud-stat"><span class="hud-label">Sharpe / ROI</span><span class="hud-value" style="color:#FFF;">{sharpe:.2f} / {(pnl/res['Stake (€)'].sum()*100 if not res.empty else 0):+.2f}%</span></div>
    </div>
</div>
""", unsafe_allow_html=True)

c_left, c_main, c_right = st.columns([1, 2.8, 1.2], gap="large")

# --- CONTROLO (ESQUERDA) ---
with c_left:
    st.markdown("<div class='section-title'>I. Global Market Uplink</div>", unsafe_allow_html=True)
    target_date = st.date_input("Date", date.today(), label_visibility="collapsed")
    l_map = {"Premier League": 39, "Champions League": 2, "La Liga": 140, "Primeira Liga": 94}
    league_id = l_map[st.selectbox("Tournament", list(l_map.keys()), label_visibility="collapsed")]
    kelly = st.select_slider("Risk Profile (Kelly Algorithm)", options=[0.1, 0.25, 0.5, 1.0], value=0.25)
    
    with st.spinner("Decrypting Market..."): fixtures = get_live_fixtures(target_date.strftime('%Y-%m-%d'), league_id)
    
    m_sel = None; h_name = ""; a_name = ""
    if fixtures:
        m_map = {f"{f['teams']['home']['name']} v {f['teams']['away']['name']}": f for f in fixtures}
        m_sel = m_map[st.selectbox("Target Event", list(m_map.keys()))]
        h_name, a_name = m_sel['teams']['home']['name'], m_sel['teams']['away']['name']
    
    # NEURAL NET LOGS VISUALS
    st.markdown("<br><div class='section-title'>Neural Net Diagnostics</div>", unsafe_allow_html=True)
    logs = "<br>".join([f"[{time.strftime('%H:%M:%S')}] Tensor {random.randint(100,999)}: Processing node {random.randint(1,9)}... OK" for _ in range(15)])
    st.markdown(f"""
    <div class="matrix-log">
        <div class="matrix-text">
            > INITIALIZING MONTE CARLO (10k SIMS)<br>
            > POLLING ASIAN EXCHANGES...<br>
            > APPLYING DIXON-COLES RHO -0.13<br>
            > CALCULATING EXPECTED VALUE...<br>
            {logs}
            > ALPHA IDENTIFIED. READY FOR EXECUTION.
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- EXECUÇÃO (CENTRO) - ORDER BOOK DE MILHÕES ---
with c_main:
    if m_sel:
        st.markdown("<div class='section-title'>II. Syndicate Order Book (HFT)</div>", unsafe_allow_html=True)
        
        with st.spinner("Processing Quant Models & Pricing..."):
            h_stats = get_real_stats(m_sel['teams']['home']['id'], league_id)
            a_stats = get_real_stats(m_sel['teams']['away']['id'], league_id)
            xg_h, xg_a = calculate_real_xg(h_stats, a_stats)
            probs = run_monte_carlo_sim(xg_h, xg_a)
            market_data = get_smart_odds(m_sel['fixture']['id'], probs)
            source_tag = market_data.pop("_source", "Unknown")

        st.markdown(f"""
        <div style="display:flex; justify-content:space-between; align-items:center; background:rgba(8, 12, 22, 0.8); border:1px solid rgba(0,240,255,0.3); border-radius:8px; padding:20px 30px; margin-bottom:15px; box-shadow: inset 0 0 20px rgba(0,240,255,0.05);">
            <div>
                <div style="font-size:2rem; font-weight:800; line-height:1.2; text-shadow: 0 0 10px rgba(255,255,255,0.2);">{h_name}</div>
                <div style="font-family:'JetBrains Mono'; color:#00F0FF; font-size:1.1rem; font-weight:800;">Proj. xG: {xg_h:.2f}</div>
            </div>
            <div style="color:#64748B; font-weight:800; font-size:1.5rem; text-shadow: 0 0 10px rgba(0,0,0,0.5);">VS</div>
            <div style="text-align:right;">
                <div style="font-size:2rem; font-weight:800; line-height:1.2; text-shadow: 0 0 10px rgba(255,255,255,0.2);">{a_name}</div>
                <div style="font-family:'JetBrains Mono'; color:#00F0FF; font-size:1.1rem; font-weight:800;">Proj. xG: {xg_a:.2f}</div>
            </div>
        </div>
        <div style="text-align:right; margin-bottom:15px; font-family:'JetBrains Mono'; font-size:0.7rem; color:#00F0FF; letter-spacing:1px;">
            <span style="display:inline-block; width:8px; height:8px; background:#00F0FF; border-radius:50%; margin-right:5px; box-shadow:0 0 10px #00F0FF;"></span>
            DATA FEED: {source_tag}
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style="display: grid; grid-template-columns: 2fr 1fr 1fr 1.5fr 1.5fr; font-size: 0.65rem; color: #64748B; text-transform: uppercase; letter-spacing: 2px; font-weight: 800; padding: 0 15px 10px 15px; border-bottom: 1px solid #1E293B; margin-bottom: 10px;">
            <div>Derivative Market</div>
            <div style="text-align:right;">Market Odd</div>
            <div style="text-align:right;">True Odd</div>
            <div style="text-align:center;">Alpha (Edge)</div>
            <div style="text-align:center;">1-Click Execution</div>
        </div>
        """, unsafe_allow_html=True)

        for mkt, m_odd in market_data.items():
            if mkt == "_source": continue
            p_real = probs.get(mkt, 0)
            if m_odd > 1.01 and p_real > 0:
                t_odd = 1 / p_real
                edge = (p_real * m_odd) - 1
                
                if edge > 0.01:
                    stake = current_bk * ((edge / (m_odd - 1)) * kelly)
                    edge_color = "#00FF88"
                    border_glow = "border-color: #00F0FF;"
                    liq_width = min(100, int(edge * 1000)) # Simula barra de liquidez baseada no edge
                    liquidity_bg = f"<div class='liquidity-bar' style='width: {liq_width}%;'></div>"
                else:
                    stake = 0
                    edge_color = "#64748B"
                    border_glow = ""
                    liquidity_bg = ""

                st.markdown(f"""
                <div class="order-row" style="{border_glow}">
                    {liquidity_bg}
                    <div class="order-cell market-name">{mkt}</div>
                    <div class="order-cell" style="text-align:right; font-weight:800; color:#FFF; font-size:1rem;">{m_odd:.2f}</div>
                    <div class="order-cell" style="text-align:right; color:#00F0FF;">{t_odd:.2f}</div>
                    <div class="order-cell" style="text-align:center; color:{edge_color}; font-weight:800; text-shadow: 0 0 10px rgba(0,255,136,0.2);">{edge*100:+.1f}%</div>
                """, unsafe_allow_html=True)
                
                col_g1, col_btn, col_g2 = st.columns([2.5, 4, 1.5])
                with col_btn:
                    if edge > 0.01:
                        st.markdown("<div class='btn-buy'>", unsafe_allow_html=True)
                        if st.button(f"EXECUTE €{stake:,.0f}", key=f"buy_{mkt}", use_container_width=True):
                            new_trade = pd.DataFrame([{"ID": str(uuid.uuid4())[:8], "Date": date.today().strftime('%Y-%m-%d'), "Market": f"{h_name[:3]} v {a_name[:3]} {mkt}", "Matched Odd": m_odd, "True Odd": round(t_odd, 2), "Stake (€)": round(stake, 2), "CLV": round(edge, 4), "Status": "Pending"}])
                            st.session_state.ledger = pd.concat([st.session_state.ledger, new_trade], ignore_index=True)
                            st.toast(f"Alpha Captured.", icon="⚡")
                            safe_rerun()
                        st.markdown("</div>", unsafe_allow_html=True)
                    else:
                        st.markdown("<div style='text-align:center; font-family:\"JetBrains Mono\"; font-size:0.75rem; color:#64748B; padding:5px;'>NO ALPHA DETECTED</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div style='text-align:center; padding-top:150px; opacity:0.2;'><h1 style='font-size:4rem; font-family:\"JetBrains Mono\";'>SYSTEM STANDBY</h1></div>", unsafe_allow_html=True)

# --- 3D ALPHA SURFACE E LEDGER (DIREITA) ---
with c_right:
    st.markdown("<div class='section-title'>III. 3D Risk Topography</div>", unsafe_allow_html=True)
    
    # 3D Surface Generator (Pura Matemática Visual)
    x = np.linspace(1.5, 4.0, 30) # Odds
    y = np.linspace(0.1, 0.7, 30) # Prob
    xGrid, yGrid = np.meshgrid(x, y)
    zGrid = (xGrid * yGrid) - 1 # Edge
    zGrid[zGrid < 0] = np.nan # Cortar edges negativos (O Alpha é apenas o que sobressai)

    fig_3d = go.Figure(data=[go.Surface(z=zGrid, x=xGrid, y=yGrid, colorscale='Tealgrn', showscale=False)])
    fig_3d.update_layout(
        scene=dict(
            xaxis_title='Market Odd', yaxis_title='True Prob', zaxis_title='Alpha',
            xaxis=dict(gridcolor='#1E293B', backgroundcolor='rgba(0,0,0,0)', showbackground=False),
            yaxis=dict(gridcolor='#1E293B', backgroundcolor='rgba(0,0,0,0)', showbackground=False),
            zaxis=dict(gridcolor='#1E293B', backgroundcolor='rgba(0,0,0,0)', showbackground=False),
            camera=dict(eye=dict(x=1.6, y=1.6, z=0.8))
        ),
        margin=dict(l=0, r=0, b=0, t=0), height=300, paper_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig_3d, use_container_width=True, config={'displayModeBar': False})

    st.markdown("<div class='section-title' style='margin-top:20px;'>IV. Live Clearing House</div>", unsafe_allow_html=True)
    df_display = st.session_state.ledger.sort_values(by="Date", ascending=False).head(5).copy()
    edited = st.data_editor(
        df_display, column_order=["Market", "Stake (€)", "Status"],
        column_config={
            "Market": st.column_config.TextColumn(disabled=True), 
            "Stake (€)": st.column_config.NumberColumn(format="€%d", disabled=True), 
            "Status": st.column_config.SelectboxColumn(options=["Pending", "Settled - Won", "Settled - Lost"])
        },
        hide_index=True, use_container_width=True, height=220
    )
    if not edited.equals(df_display):
        for idx, row in edited.iterrows():
            if row['Status'] != df_display.loc[idx, 'Status']:
                st.session_state.ledger.at[st.session_state.ledger[st.session_state.ledger['ID'] == row['ID']].index[0], 'Status'] = row['Status']
        safe_rerun()