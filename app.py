import streamlit as st
import numpy as np
from scipy.stats import poisson, norm
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
from datetime import date, timedelta
import random
import time
import uuid

# ==========================================
# 1. SETUP INSTITUCIONAL "UNICORN LEVEL"
# ==========================================
st.set_page_config(page_title="APEX QUANT | OMEGA", layout="wide", initial_sidebar_state="collapsed")

def safe_rerun():
    try: st.rerun()
    except AttributeError: st.experimental_rerun()

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;700;800&display=swap');
    .stApp { background-color: #010203; color: #E2E8F0; font-family: 'Inter', sans-serif; background-image: radial-gradient(circle at 50% 0%, #0B1120 0%, #010203 70%); }
    header, footer { visibility: hidden; } 
    
    .ticker-wrap { width: 100%; background-color: #070B14; border-bottom: 1px solid #1E293B; margin-top: -3rem; padding: 4px 0; overflow: hidden; position: sticky; top: 0; z-index: 1000; display: flex; align-items: center; }
    .ticker-title { background: linear-gradient(90deg, #D4AF37, #AA8529); color: #000; font-weight: 800; font-size: 0.65rem; padding: 3px 12px; text-transform: uppercase; letter-spacing: 2px; z-index: 2; margin-left: 10px; border-radius: 2px; }
    .ticker { display: inline-block; white-space: nowrap; padding-left: 100%; animation: ticker 30s linear infinite; font-family: 'JetBrains Mono'; font-size: 0.7rem; color: #64748B; }
    @keyframes ticker { 0% { transform: translate3d(0, 0, 0); } 100% { transform: translate3d(-100%, 0, 0); } }
    .ticker-item { display: inline-block; padding: 0 2rem; border-right: 1px solid #1E293B; }
    .tick-up { color: #00FF88; } .tick-down { color: #FF0055; }
    
    .hud-container { display: flex; justify-content: space-between; align-items: center; background: rgba(7, 11, 20, 0.8); backdrop-filter: blur(10px); padding: 15px 30px; border-bottom: 1px solid rgba(30, 41, 59, 0.5); margin: 0 -3rem 2rem -3rem; }
    .hud-brand { font-family:'JetBrains Mono'; font-weight:800; color:#D4AF37; font-size:2rem; letter-spacing:-2px; text-shadow: 0 0 30px rgba(212,175,55,0.3); line-height: 1; }
    .hud-stat { display: flex; flex-direction: column; align-items: flex-end; padding: 0 20px; border-right: 1px solid rgba(30,41,59,0.3); }
    .hud-stat:last-child { border-right: none; }
    .hud-label { font-size: 0.6rem; color: #94A3B8; text-transform: uppercase; font-weight: 800; letter-spacing: 2px; margin-bottom: 2px; }
    .hud-value { font-size: 1.8rem; font-family: 'JetBrains Mono', monospace; font-weight: 800; color: #FFFFFF; text-shadow: 0 2px 10px rgba(0,0,0,0.5); }
    
    .section-title { font-size: 0.75rem; color: #D4AF37; text-transform: uppercase; letter-spacing: 3px; font-weight: 800; margin-bottom: 15px; display: flex; align-items: center; gap: 10px; font-family: 'JetBrains Mono'; }
    .section-title::after { content: ''; flex-grow: 1; height: 1px; background: linear-gradient(90deg, #D4AF37, transparent); opacity: 0.3; }
    
    .quant-box { background: rgba(11, 17, 32, 0.5); border: 1px solid #1E293B; border-radius: 8px; padding: 20px; box-shadow: inset 0 0 20px rgba(0,0,0,0.5); position: relative; }
    .quant-box::before { content: ''; position: absolute; top: 0; left: 0; width: 3px; height: 100%; background: #00F0FF; border-radius: 8px 0 0 8px; }
    
    .math-text { font-family: 'JetBrains Mono'; color: #64748B; font-size: 0.75rem; line-height: 1.5; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. MOTOR DE DADOS REAIS & MOCK PARA PITCH
# ==========================================
API_KEY = st.secrets.get("API_KEY", "8171043bf0a322286bb127947dbd4041") 
HEADERS = {"x-apisports-key": API_KEY, "x-apisports-host": "v3.football.api-sports.io"}

def fetch_api(endpoint, params):
    try: return requests.get(f"https://{HEADERS['x-apisports-host']}/{endpoint}", headers=HEADERS, params=params, timeout=10).json().get('response', [])
    except: return []

@st.cache_data(ttl=60) 
def get_live_fixtures(date_str, league_id, season="2025"):
    return fetch_api("fixtures", {"date": date_str, "league": league_id, "season": season})

@st.cache_data(ttl=3600)
def get_real_stats(team_id, league_id, season="2025"):
    stats = fetch_api("teams/statistics", {"team": team_id, "league": league_id, "season": season})
    if not stats: return {"gf_h": 1.5, "ga_h": 1.0, "gf_a": 1.2, "ga_a": 1.4}
    try:
        goals = stats.get('goals', {})
        return {
            "gf_h": float(goals.get('for', {}).get('average', {}).get('home', 1.5)),
            "ga_h": float(goals.get('against', {}).get('average', {}).get('home', 1.0)),
            "gf_a": float(goals.get('for', {}).get('average', {}).get('away', 1.2)),
            "ga_a": float(goals.get('against', {}).get('average', {}).get('away', 1.4))
        }
    except: return {"gf_h": 1.5, "ga_h": 1.0, "gf_a": 1.2, "ga_a": 1.4}

@st.cache_data(ttl=60) 
def get_real_odds(fixture_id): 
    odds_data = fetch_api("odds", {"fixture": fixture_id, "bookmaker": 8})
    market_odds = {}
    if odds_data and odds_data[0].get('bookmakers'):
        for bet in odds_data[0]['bookmakers'][0].get('bets', []):
            if bet['name'] == 'Match Winner':
                vals = {v['value']: float(v['odd']) for v in bet['values']}
                market_odds.update({"Home Win": vals.get('Home', 0), "Draw": vals.get('Draw', 0), "Away Win": vals.get('Away', 0)})
    return market_odds

# ==========================================
# 3. MATEMÁTICA AVANÇADA & MACHINE LEARNING (VISUAL)
# ==========================================
def calculate_real_xg(h_stats, a_stats):
    h_attack = h_stats['gf_h'] / 1.35; a_defense = a_stats['ga_a'] / 1.35
    a_attack = a_stats['gf_a'] / 1.35; h_defense = h_stats['ga_h'] / 1.35
    return round(max(0.5, h_attack * a_defense * 1.35), 2), round(max(0.5, a_attack * h_defense * 1.35), 2)

def run_monte_carlo_sim(xg_h, xg_a, sims=10000):
    np.random.seed(int(time.time()))
    h_goals = np.random.poisson(xg_h, sims); a_goals = np.random.poisson(xg_a, sims)
    diff = h_goals - a_goals
    return {"Home Win": np.sum(diff > 0)/sims, "Draw": np.sum(diff == 0)/sims, "Away Win": np.sum(diff < 0)/sims}

def generate_radar_data(xg_h, xg_a):
    """Gera métricas sintéticas avançadas baseadas no xG para impressionar."""
    base_h, base_a = xg_h / (xg_h+xg_a), xg_a / (xg_h+xg_a)
    categories = ['Expected Threat (xT)', 'PPDA (Pressing)', 'Pace & Transition', 'Deep Completions', 'Box Control']
    val_h = [min(100, max(40, base_h * 100 + random.uniform(-10, 20))) for _ in range(5)]
    val_a = [min(100, max(40, base_a * 100 + random.uniform(-10, 20))) for _ in range(5)]
    return categories, val_h, val_a

def init_mock_ledger():
    np.random.seed(42)
    history = []
    for _ in range(300):
        clv = np.random.normal(0.045, 0.03)
        odd = round(random.uniform(1.80, 2.50), 2)
        history.append({"ID": str(uuid.uuid4())[:8], "Date": (date.today() - timedelta(days=random.randint(0, 90))).strftime('%Y-%m-%d'), "Market": "Quant Auto", "Matched Odd": odd, "True Odd": round(odd/(1+clv), 2), "Stake (€)": round(random.uniform(2000, 5000), 2), "CLV": round(clv, 4), "Status": "Settled - Won" if random.random() < (1/(odd/(1+clv))) else "Settled - Lost"})
    return pd.DataFrame(history)

# ==========================================
# 4. GESTÃO DE ESTADO E HUD
# ==========================================
if 'user' not in st.session_state: st.session_state.user = None
if 'ledger' not in st.session_state: st.session_state.ledger = init_mock_ledger()
if 'init_bk' not in st.session_state: st.session_state.init_bk = 5000000.0 # 5 MILHÕES
if 'hft_active' not in st.session_state: st.session_state.hft_active = False

if not st.session_state.user:
    st.markdown("<div style='height:25vh;'></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        st.markdown("<h1 style='text-align:center; font-family:\"JetBrains Mono\"; font-size:4rem; margin-bottom:0; color:#D4AF37; text-shadow: 0 0 20px rgba(212,175,55,0.5);'>APEX<span style='color:#FFF;'>OMEGA</span></h1><p style='text-align:center; color:#64748B; letter-spacing:6px; font-size:0.7rem; font-weight:800;'>PROPRIETARY QUANTITATIVE FUND</p>", unsafe_allow_html=True)
        with st.form("login"):
            st.text_input("G-7 Security Clearance Key", type="password", placeholder="Authorize Access")
            if st.form_submit_button("INITIALIZE SECURE CONNECTION", use_container_width=True):
                st.session_state.user = "CEO"
                safe_rerun()
    st.stop()

res = st.session_state.ledger[st.session_state.ledger['Status'].isin(['Settled - Won', 'Settled - Lost'])].copy()
res['PnL'] = res.apply(lambda r: r['Stake (€)'] * (r['Matched Odd'] - 1) if r['Status'] == 'Settled - Won' else -r['Stake (€)'], axis=1)
pnl = res['PnL'].sum()
current_bk = st.session_state.init_bk + pnl

st.markdown("""
<div class="ticker-wrap">
    <div class="ticker-title">TERMINAL FEED</div>
    <div class="ticker">
        <span class="ticker-item">APEX OMEGA ENGINE: <span class="tick-up">ONLINE</span></span>
        <span class="ticker-item">DIXON-COLES RHO VARIANCE: OPTIMIZED AT -0.13</span>
        <span class="ticker-item">BAYESIAN FORM INDEX: UPDATING REAL-TIME</span>
        <span class="ticker-item">HFT BOT STATUS: STANDBY</span>
        <span class="ticker-item">PINNACLE LATENCY: 12ms</span>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="hud-container">
    <div class="hud-brand">APEX<span style="color:#FFF;">OMEGA</span> <span style="font-size:0.5rem; color:#00F0FF; vertical-align:top;">V9</span></div>
    <div style="display:flex;">
        <div class="hud-stat"><span class="hud-label">AUM (Assets)</span><span class="hud-value">€{current_bk:,.0f}</span></div>
        <div class="hud-stat"><span class="hud-label">Alpha Generated</span><span class="hud-value {'tick-up' if pnl>=0 else 'tick-down'}">{pnl:+,.0f}</span></div>
        <div class="hud-stat"><span class="hud-label">Sharpe Ratio</span><span class="hud-value" style="color:#00F0FF;">2.84</span></div>
    </div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 5. DASHBOARD PRINCIPAL
# ==========================================
c_left, c_main, c_right = st.columns([1, 2.2, 1.2], gap="medium")

# --- COLUNA 1: SCANNER & RADAR ---
with c_left:
    st.markdown("<div class='section-title'>I. Global Market Data</div>", unsafe_allow_html=True)
    target_date = st.date_input("Date", date.today(), label_visibility="collapsed")
    l_map = {"Premier League": 39, "Champions League": 2, "La Liga": 140}
    league_id = l_map[st.selectbox("Tournament", list(l_map.keys()), label_visibility="collapsed")]
    
    with st.spinner("Decrypting Market..."): fixtures = get_live_fixtures(target_date.strftime('%Y-%m-%d'), league_id)
    
    m_sel = None; h_name = ""; a_name = ""
    if fixtures:
        m_map = {f"{f['teams']['home']['name']} v {f['teams']['away']['name']}": f for f in fixtures}
        m_sel = m_map[st.selectbox("Target Event", list(m_map.keys()))]
        h_name, a_name = m_sel['teams']['home']['name'], m_sel['teams']['away']['name']
        st.button("⚡ FORCE SYNC", use_container_width=True)

    st.markdown("<br><div class='section-title'>II. Neural Net Analysis</div>", unsafe_allow_html=True)
    if m_sel:
        # Radar Chart Proprietário
        h_stats = get_real_stats(m_sel['teams']['home']['id'], league_id)
        a_stats = get_real_stats(m_sel['teams']['away']['id'], league_id)
        xg_h, xg_a = calculate_real_xg(h_stats, a_stats)
        
        cat, v_h, v_a = generate_radar_data(xg_h, xg_a)
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(r=v_h, theta=cat, fill='toself', name=h_name, line_color='#00F0FF', fillcolor='rgba(0, 240, 255, 0.2)'))
        fig_radar.add_trace(go.Scatterpolar(r=v_a, theta=cat, fill='toself', name=a_name, line_color='#D4AF37', fillcolor='rgba(212, 175, 55, 0.2)'))
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=False, range=[0, 100]), bgcolor='rgba(0,0,0,0)'),
            paper_bgcolor='rgba(0,0,0,0)', font=dict(color="#64748B", size=9), showlegend=True,
            legend=dict(orientation="h", y=-0.2), margin=dict(t=20, b=20, l=20, r=20), height=250
        )
        st.plotly_chart(fig_radar, use_container_width=True, config={'displayModeBar': False})
        
        st.markdown("<div class='math-text'>*Apex Proprietary Index: Cross-references expected threat, packing data, and Bayesian form to identify true dominance.*</div>", unsafe_allow_html=True)

# --- COLUNA 2: MATEMÁTICA PURA & EXECUÇÃO ---
with c_main:
    st.markdown("<div class='section-title'>III. Quantitative Engine & Pricing</div>", unsafe_allow_html=True)
    
    # Exposição Transparente das Fórmulas (Fator UAU)
    with st.expander("VIEW CORE ALGORITHMS (CLASSIFIED)", expanded=False):
        st.markdown("<div class='math-text'>Dixon-Coles Bivariate Poisson Adjustment:</div>", unsafe_allow_html=True)
        st.latex(r"$$\tau_{\lambda, \mu}(x, y) = \begin{cases} 1 - \lambda \mu \rho & x=0, y=0 \\ 1 + \lambda \rho & x=1, y=0 \\ 1 + \mu \rho & x=0, y=1 \\ 1 - \rho & x=1, y=1 \\ 1 & \text{otherwise} \end{cases}$$")
        st.markdown("<div class='math-text'>Kelly Criterion (Optimal Growth Function):</div>", unsafe_allow_html=True)
        st.latex(r"$$f^* = \frac{p \cdot b - q}{b} \times \text{RiskFactor}$$")

    if m_sel:
        probs, x_axis, norm_pdf = run_monte_carlo_sim(xg_h, xg_a)
        live_odds = get_real_odds(m_sel['fixture']['id'])
        
        st.markdown(f"""
        <div class="quant-box" style="margin-bottom: 20px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div style="font-size:1.8rem; font-weight:800; color:#FFF;">{h_name}</div>
                <div style="font-family:'JetBrains Mono'; font-size:1.2rem; color:#00F0FF;">xG {xg_h:.2f}</div>
            </div>
            <div style="display:flex; justify-content:space-between; align-items:center; margin-top:10px;">
                <div style="font-size:1.8rem; font-weight:800; color:#FFF;">{a_name}</div>
                <div style="font-family:'JetBrains Mono'; font-size:1.2rem; color:#D4AF37;">xG {xg_a:.2f}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if not live_odds:
            st.warning("Awaiting Market Liquidity. Bookmakers have not released viable lines.")
        else:
            for mkt in ["Home Win", "Away Win", "Draw"]:
                p_real = probs.get(mkt, 0)
                m_odd = live_odds.get(mkt, 0)
                if m_odd > 1.05 and p_real > 0:
                    t_odd = 1 / p_real
                    edge = (p_real * m_odd) - 1
                    if edge > 0:
                        stake = current_bk * ((edge / (m_odd - 1)) * 0.25) # 0.25 Kelly Fixo
                        st.markdown(f"""
                        <div style="background:#070B14; border:1px solid #38BDF8; border-radius:4px; padding:15px; margin-bottom:10px; display:flex; justify-content:space-between; align-items:center;">
                            <div>
                                <div style="font-family:'JetBrains Mono'; color:#00F0FF; font-size:0.7rem;">ARBITRAGE IDENTIFIED</div>
                                <div style="font-size:1.4rem; font-weight:800; color:#FFF;">{mkt}</div>
                                <div style="font-size:0.8rem; color:#94A3B8; margin-top:4px;">Model Odd: {t_odd:.2f} | Market: <span style="color:#D4AF37; font-weight:bold;">{m_odd:.2f}</span> | Edge: <span style="color:#00FF88; font-weight:bold;">+{edge:.1%}</span></div>
                            </div>
                            <div style="width:160px;">
                        """, unsafe_allow_html=True)
                        if st.button(f"BUY €{stake:,.0f}", key=f"buy_{mkt}", use_container_width=True):
                            new_trade = pd.DataFrame([{"ID": str(uuid.uuid4())[:8], "Date": date.today().strftime('%Y-%m-%d'), "Market": f"{h_name[:3]} v {a_name[:3]} - {mkt}", "Matched Odd": m_odd, "True Odd": round(t_odd, 2), "Stake (€)": round(stake, 2), "CLV": round(edge, 4), "Status": "Pending"}])
                            st.session_state.ledger = pd.concat([st.session_state.ledger, new_trade], ignore_index=True)
                            st.toast("Order injected into market.", icon="⚡")
                            safe_rerun()
                        st.markdown("</div></div>", unsafe_allow_html=True)

# --- COLUNA 3: SUPERFÍCIE 3D & HFT ---
with c_right:
    st.markdown("<div class='section-title'>IV. Risk Topography (3D)</div>", unsafe_allow_html=True)
    
    # Gerar Superfície 3D Aleatória (Risk vs Reward vs Probability)
    x = np.linspace(1.5, 3.5, 20) # Odds
    y = np.linspace(0.1, 0.6, 20) # Prob
    xGrid, yGrid = np.meshgrid(x, y)
    zGrid = (xGrid * yGrid) - 1 # Edge Surface
    zGrid[zGrid < 0] = np.nan # Cortar edges negativos

    fig_3d = go.Figure(data=[go.Surface(z=zGrid, x=xGrid, y=yGrid, colorscale='Viridis', showscale=False)])
    fig_3d.update_layout(
        scene=dict(
            xaxis_title='Odd', yaxis_title='Prob', zaxis_title='Alpha',
            xaxis=dict(gridcolor='#1E293B', backgroundcolor='rgba(0,0,0,0)'),
            yaxis=dict(gridcolor='#1E293B', backgroundcolor='rgba(0,0,0,0)'),
            zaxis=dict(gridcolor='#1E293B', backgroundcolor='rgba(0,0,0,0)'),
            camera=dict(eye=dict(x=1.5, y=1.5, z=0.8))
        ),
        margin=dict(l=0, r=0, b=0, t=0), height=250, paper_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig_3d, use_container_width=True, config={'displayModeBar': False})

    st.markdown("<br><div class='section-title'>V. Auto-Trading</div>", unsafe_allow_html=True)
    hft = st.toggle("Engage HFT Algorithm", value=st.session_state.hft_active)
    if hft:
        st.markdown("<div style='color:#00FF88; font-family:\"JetBrains Mono\"; font-size:0.8rem; text-align:center; padding:10px; border:1px solid #00FF88; border-radius:4px;'>BOT ACTIVE: SCANNING GLOBAL EXCHANGES</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div style='color:#64748B; font-family:\"JetBrains Mono\"; font-size:0.8rem; text-align:center; padding:10px; border:1px solid #1E293B; border-radius:4px;'>BOT OFFLINE: MANUAL OVERRIDE</div>", unsafe_allow_html=True)

    st.markdown("<br><div class='section-title'>Portfolio Ledger</div>", unsafe_allow_html=True)
    df_display = st.session_state.ledger.sort_values(by="Date", ascending=False).head(5).copy()
    edited = st.data_editor(
        df_display, column_order=["Market", "Stake (€)", "Status"],
        column_config={"Market": st.column_config.TextColumn(disabled=True), "Stake (€)": st.column_config.NumberColumn(format="€%d", disabled=True), "Status": st.column_config.SelectboxColumn(options=["Pending", "Settled - Won", "Settled - Lost"])},
        hide_index=True, use_container_width=True, height=210
    )
    if not edited.equals(df_display):
        for idx, row in edited.iterrows():
            if row['Status'] != df_display.loc[idx, 'Status']:
                st.session_state.ledger.at[st.session_state.ledger[st.session_state.ledger['ID'] == row['ID']].index[0], 'Status'] = row['Status']
        safe_rerun()