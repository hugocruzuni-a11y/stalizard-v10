import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from scipy.stats import poisson, norm
import requests
from datetime import date, timedelta
import random
import time
import uuid

# ==========================================
# 1. ESTILO INSTITUCIONAL DE ELITE (CSS)
# ==========================================
st.set_page_config(page_title="APEX QUANT | OMEGA V10", layout="wide", initial_sidebar_state="collapsed")

def safe_rerun():
    try:
        st.rerun()
    except:
        st.experimental_rerun()

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&family=JetBrains+Mono:wght@400;700&display=swap');
    
    .stApp { background-color: #010203; color: #E2E8F0; font-family: 'Inter', sans-serif; background-image: radial-gradient(circle at 50% 0%, #080C16 0%, #010203 80%); }
    header, footer { visibility: hidden; }
    
    /* Top Bar HUD */
    .hud-container { display: flex; justify-content: space-between; align-items: center; background: rgba(5, 8, 15, 0.95); backdrop-filter: blur(12px); padding: 15px 30px; border-bottom: 1px solid rgba(0, 240, 255, 0.2); margin: -3rem -3rem 2rem -3rem; position: sticky; top: 0; z-index: 999;}
    .hud-brand { font-family:'JetBrains Mono'; font-weight:800; color:#D4AF37; font-size:1.8rem; letter-spacing:-1px; }
    .hud-stat { display: flex; flex-direction: column; align-items: flex-end; padding: 0 20px; border-right: 1px solid rgba(30,41,59,0.4); }
    .hud-stat:last-child { border-right: none; }
    .hud-label { font-size: 0.6rem; color: #94A3B8; text-transform: uppercase; font-weight: 800; letter-spacing: 1px; margin-bottom: 2px; }
    .hud-value { font-size: 1.5rem; font-family: 'JetBrains Mono', monospace; font-weight: 800; color: #FFFFFF; }
    
    /* Section UI */
    .section-title { font-size: 0.75rem; color: #D4AF37; text-transform: uppercase; letter-spacing: 3px; font-weight: 800; margin-bottom: 15px; display: flex; align-items: center; gap: 10px; font-family: 'JetBrains Mono'; }
    .section-title::after { content: ''; flex-grow: 1; height: 1px; background: linear-gradient(90deg, #D4AF37, transparent); opacity: 0.3; }
    
    /* Order Matrix */
    .order-row { display: grid; grid-template-columns: 2fr 1fr 1fr 1.5fr 1.5fr; align-items: center; background: rgba(8, 12, 22, 0.6); border: 1px solid #1E293B; border-radius: 4px; margin-bottom: 5px; transition: 0.2s; }
    .order-row:hover { border-color: #38BDF8; background: rgba(56, 189, 248, 0.05); }
    .order-cell { padding: 12px 15px; font-family: 'JetBrains Mono'; font-size: 0.85rem; }
    .market-name { color: #F8FAFC; font-weight: 700; text-transform: uppercase; font-size: 0.8rem; }
    
    /* Buttons */
    .btn-buy div.stButton > button { background: linear-gradient(90deg, #10B981, #059669) !important; color: #000 !important; font-weight: 800 !important; font-family: 'JetBrains Mono'; border: none !important; transition: 0.2s; height: 35px !important; }
    .btn-buy div.stButton > button:hover { transform: scale(1.05); box-shadow: 0 4px 15px rgba(16,185,129,0.4); }
    
    /* Matrix Log */
    .matrix-log { background: #030509; border: 1px solid #1E293B; border-left: 2px solid #D4AF37; padding: 10px; font-family: 'JetBrains Mono'; font-size: 0.65rem; color: #D4AF37; height: 100px; overflow: hidden; border-radius: 4px; margin-top: 20px;}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. DATA ENGINE (LIGAÇÃO REAL API)
# ==========================================
API_KEY = "8171043bf0a322286bb127947dbd4041"
HEADERS = {"x-apisports-key": API_KEY, "x-apisports-host": "v3.football.api-sports.io"}

def fetch_api(endpoint, params):
    try:
        r = requests.get(f"https://{HEADERS['x-apisports-host']}/{endpoint}", headers=HEADERS, params=params, timeout=10)
        return r.json().get('response', [])
    except:
        return []

@st.cache_data(ttl=300)
def get_fixtures(date_str, league_id):
    return fetch_api("fixtures", {"date": date_str, "league": league_id, "season": "2025"})

@st.cache_data(ttl=3600)
def get_stats(team_id, league_id):
    res = fetch_api("teams/statistics", {"team": team_id, "league": league_id, "season": "2025"})
    if not res: return {"gf_h": 1.5, "ga_h": 1.1, "gf_a": 1.2, "ga_a": 1.4}
    try:
        # Normalização de resposta (API por vezes envia lista, outras dict)
        data = res if isinstance(res, dict) else res[0]
        goals = data.get('goals', {})
        return {
            "gf_h": float(goals.get('for', {}).get('average', {}).get('home', 1.5)),
            "ga_h": float(goals.get('against', {}).get('average', {}).get('home', 1.1)),
            "gf_a": float(goals.get('for', {}).get('average', {}).get('away', 1.2)),
            "ga_a": float(goals.get('against', {}).get('average', {}).get('away', 1.4))
        }
    except:
        return {"gf_h": 1.5, "ga_h": 1.1, "gf_a": 1.2, "ga_a": 1.4}

@st.cache_data(ttl=60)
def get_live_odds(fixture_id):
    res = fetch_api("odds", {"fixture": fixture_id, "bookmaker": 8})
    odds = {}
    if res and res[0].get('bookmakers'):
        for bet in res[0]['bookmakers'][0].get('bets', []):
            if bet['name'] == 'Match Winner':
                vals = {v['value']: float(v['odd']) for v in bet['values']}
                odds.update({"Home Win": vals.get('Home', 0), "Draw": vals.get('Draw', 0), "Away Win": vals.get('Away', 0)})
            if bet['name'] == 'Goals Over/Under':
                vals = {v['value']: float(v['odd']) for v in bet['values']}
                odds.update({"Over 2.5": vals.get('Over 2.5', 0), "Under 2.5": vals.get('Under 2.5', 0)})
    return odds

# ==========================================
# 3. QUANT ENGINE (MONTE CARLO)
# ==========================================
def run_monte_carlo(xg_h, xg_a, sims=10000):
    np.random.seed(int(time.time()))
    h_goals = np.random.poisson(xg_h, sims)
    a_goals = np.random.poisson(xg_a, sims)
    diff = h_goals - a_goals
    total = h_goals + a_goals
    return {
        "Home Win": np.sum(diff > 0)/sims, "Draw": np.sum(diff == 0)/sims, "Away Win": np.sum(diff < 0)/sims,
        "Over 2.5": np.sum(total > 2.5)/sims, "Under 2.5": np.sum(total < 2.5)/sims
    }

def init_mock_ledger():
    np.random.seed(42)
    history = []
    for _ in range(50):
        odd = round(random.uniform(1.8, 2.5), 2)
        history.append({
            "ID": str(uuid.uuid4())[:8], "Date": "2026-03-25", "Market": "Quant AH", 
            "Matched Odd": odd, "True Odd": round(odd/1.05, 2), "Stake (€)": 5000, 
            "Status": random.choice(["Settled - Won", "Settled - Lost"])
        })
    return pd.DataFrame(history)

# ==========================================
# 4. GESTÃO DE SESSÃO E LOGIN
# ==========================================
if 'user' not in st.session_state: st.session_state.user = None
if 'ledger' not in st.session_state: st.session_state.ledger = init_mock_ledger()
if 'bankroll' not in st.session_state: st.session_state.bankroll = 10000000.0

if not st.session_state.user:
    st.markdown("<div style='height:25vh;'></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        st.markdown("<h1 style='text-align:center; font-family:\"JetBrains Mono\"; color:#D4AF37;'>APEX<span style='color:#FFF;'>QUANT</span></h1>", unsafe_allow_html=True)
        with st.form("login"):
            st.text_input("G-7 Security Access", type="password")
            if st.form_submit_button("CONNECT TO TERMINAL", use_container_width=True):
                st.session_state.user = "CEO"
                st.rerun()
    st.stop()

# ==========================================
# 5. UI DASHBOARD PRINCIPAL
# ==========================================
# Cálculos de HUD
res_df = st.session_state.ledger[st.session_state.ledger['Status'].isin(["Settled - Won", "Settled - Lost"])].copy()
res_df['PnL'] = res_df.apply(lambda r: r['Stake (€)'] * (r['Matched Odd'] - 1) if r['Status'] == "Settled - Won" else -r['Stake (€)'], axis=1)
total_pnl = res_df['PnL'].sum()
current_bk = st.session_state.bankroll + total_pnl

st.markdown(f"""
<div class="hud-container">
    <div class="hud-brand">APEX<span style="color:#FFF;">QUANT</span> <span style="font-size:0.5rem; color:#00F0FF; vertical-align:top;">OMEGA V10</span></div>
    <div style="display:flex;">
        <div class="hud-stat"><span class="hud-label">Capital (AUM)</span><span class="hud-value">€{current_bk:,.0f}</span></div>
        <div class="hud-stat"><span class="hud-label">Net Alpha</span><span class="hud-value" style="color:#00FF88;">{total_pnl:+,.0f}</span></div>
        <div class="hud-stat"><span class="hud-label">Risk Profile</span><span class="hud-value" style="color:#D4AF37;">INSTITUTIONAL</span></div>
    </div>
</div>
""", unsafe_allow_html=True)

c_left, c_main = st.columns([1, 2.8], gap="large")

with c_left:
    st.markdown("<div class='section-title'>I. Market Access</div>", unsafe_allow_html=True)
    t_date = st.date_input("Trading Date", date.today(), label_visibility="collapsed")
    l_map = {"🇬🇧 Premier League": 39, "🇪🇺 Champions League": 2, "🇪🇸 La Liga": 140, "🇮🇹 Serie A": 135}
    league_id = l_map[st.selectbox("League", list(l_map.keys()), label_visibility="collapsed")]
    
    with st.spinner("Polling API..."):
        fixtures = get_fixtures(t_date.strftime('%Y-%m-%d'), league_id)
    
    m_sel = None
    if fixtures:
        m_map = {f"{f['teams']['home']['name']} v {f['teams']['away']['name']}": f for f in fixtures}
        m_name = st.selectbox("Select Event", list(m_map.keys()), label_visibility="collapsed")
        m_sel = m_map[m_name]
        st.button("⚡ FORCE SYNC", use_container_width=True)
    else:
        st.error("No real events found.")

    st.markdown("<div class='matrix-log'>> INITIALIZING NEURAL LINK...<br>> MONTE CARLO READY (10k)<br>> DATA SOURCE: API-SPORTS<br>> STATUS: ENCRYPTED</div>", unsafe_allow_html=True)

with c_main:
    if m_sel:
        st.markdown("<div class='section-title'>II. Algorithmic Intelligence & Order Book</div>", unsafe_allow_html=True)
        
        # Puxar dados reais
        h_stats = get_stats(m_sel['teams']['home']['id'], league_id)
        a_stats = get_stats(m_sel['teams']['away']['id'], league_id)
        
        # Matemática
        xg_h = (h_stats['gf_h'] + a_stats['ga_a']) / 2
        xg_a = (a_stats['gf_a'] + h_stats['ga_h']) / 2
        probs = run_monte_carlo(xg_h, xg_a)
        odds = get_live_odds(m_sel['fixture']['id'])
        
        # Header do Jogo
        st.markdown(f"""
        <div style="display:flex; justify-content:space-between; align-items:center; background:rgba(8, 12, 22, 0.8); border:1px solid #1E293B; padding:20px; border-radius:8px; margin-bottom:20px;">
            <div style="text-align:left;"><div style="font-size:1.8rem; font-weight:800;">{m_sel['teams']['home']['name']}</div><div style="color:#00F0FF; font-family:'JetBrains Mono';">xG: {xg_h:.2f}</div></div>
            <div style="color:#64748B; font-weight:800; font-size:1.2rem;">VS</div>
            <div style="text-align:right;"><div style="font-size:1.8rem; font-weight:800;">{m_sel['teams']['away']['name']}</div><div style="color:#D4AF37; font-family:'JetBrains Mono';">xG: {xg_a:.2f}</div></div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style="display: grid; grid-template-columns: 2fr 1fr 1fr 1.5fr 1.5fr; font-size: 0.6rem; color: #64748B; text-transform: uppercase; letter-spacing: 2px; font-weight: 800; padding: 0 15px 10px 15px; border-bottom: 1px solid #1E293B; margin-bottom: 10px;">
            <div>Market Asset</div><div style="text-align:right;">API Price</div><div style="text-align:right;">True Price</div><div style="text-align:center;">Alpha</div><div style="text-align:center;">Action</div>
        </div>
        """, unsafe_allow_html=True)

        for mkt in ["Home Win", "Draw", "Away Win", "Over 2.5", "Under 2.5"]:
            p_real = probs.get(mkt, 0)
            m_odd = odds.get(mkt, 0)
            
            # Se a odd for 0 (API falhou ou jogo passou), geramos a "Closing Line" justa
            if m_odd <= 1.01:
                m_odd = round((1/p_real) * 0.97, 2) if p_real > 0 else 1.01

            t_odd = 1/p_real if p_real > 0 else 100.0
            edge = (p_real * m_odd) - 1
            
            # Kelly Criterion (1/4 Kelly para investidores conservadores)
            stake = current_bk * ((edge / (m_odd - 1)) * 0.25) if edge > 0.01 else 0
            
            st.markdown(f"""
            <div class="order-row">
                <div class="order-cell market-name">{mkt}</div>
                <div class="order-cell" style="text-align:right; font-weight:800; color:#FFF;">{m_odd:.2f}</div>
                <div class="order-cell" style="text-align:right; color:#00F0FF;">{t_odd:.2f}</div>
                <div class="order-cell" style="text-align:center; color:{'#00FF88' if edge > 0 else '#64748B'}; font-weight:800;">{edge*100:+.1f}%</div>
            """, unsafe_allow_html=True)
            
            col_b1, col_btn, col_b2 = st.columns([2.5, 4, 1.5])
            with col_btn:
                if edge > 0.01:
                    st.markdown("<div class='btn-buy'>", unsafe_allow_html=True)
                    if st.button(f"EXECUTE €{stake:,.0f}", key=f"buy_{mkt}"):
                        new_t = pd.DataFrame([{"ID": str(uuid.uuid4())[:8], "Date": str(date.today()), "Market": f"{m_name[:4]} {mkt}", "Matched Odd": m_odd, "True Odd": round(t_odd, 2), "Stake (€)": round(stake, 2), "Status": "Pending"}])
                        st.session_state.ledger = pd.concat([st.session_state.ledger, new_t], ignore_index=True)
                        st.toast("Order Filled.", icon="⚡")
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)
                else:
                    st.markdown("<div style='text-align:center; color:#475569; font-size:0.7rem; padding:10px;'>LIQUIDITY LOW</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div style='text-align:center; padding-top:150px; opacity:0.2;'><h1 style='font-size:4rem; font-family:\"JetBrains Mono\";'>SYSTEM STANDBY</h1></div>", unsafe_allow_html=True)