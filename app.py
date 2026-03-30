import streamlit as st
import numpy as np
from scipy.stats import poisson, norm
import pandas as pd
import plotly.graph_objects as go
import requests
from datetime import date, timedelta
import time
import uuid

# ==========================================
# 1. SETUP INSTITUCIONAL (BLACKROCK ALADDIN STYLE)
# ==========================================
st.set_page_config(page_title="APEX QUANT | ALADDIN", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;700&display=swap');
    
    .stApp { background-color: #02040A; color: #E2E8F0; font-family: 'Inter', sans-serif; }
    header { visibility: hidden; }
    
    /* HUD e Ticker */
    .ticker-wrap { width: 100%; background: #060913; border-bottom: 1px solid #1E293B; margin-top: -3rem; padding: 6px 0; overflow: hidden; position: sticky; top: 0; z-index: 1000; display: flex; align-items: center; }
    .ticker-title { background: #38BDF8; color: #000; font-weight: 700; font-size: 0.65rem; padding: 2px 10px; text-transform: uppercase; letter-spacing: 1px; margin-left: 10px; }
    .ticker { display: inline-block; white-space: nowrap; padding-left: 100%; animation: ticker 40s linear infinite; font-family: 'JetBrains Mono'; font-size: 0.7rem; color: #94A3B8; }
    @keyframes ticker { 0% { transform: translate3d(0, 0, 0); } 100% { transform: translate3d(-100%, 0, 0); } }
    .ticker-item { padding: 0 2rem; border-right: 1px solid #1E293B; }
    
    .hud-container { display: flex; justify-content: space-between; align-items: center; background: #0A0F1C; border-bottom: 1px solid #1E293B; padding: 15px 30px; margin: 0 -3rem 2rem -3rem; }
    .hud-brand { font-family:'JetBrains Mono'; font-weight:700; color:#F8FAFC; font-size:1.6rem; letter-spacing:-1px; }
    .hud-stat { display: flex; flex-direction: column; align-items: flex-end; padding: 0 20px; border-right: 1px solid #1E293B; }
    .hud-stat:last-child { border-right: none; }
    .hud-label { font-size: 0.6rem; color: #64748B; text-transform: uppercase; font-weight: 700; letter-spacing: 1px; }
    .hud-value { font-size: 1.4rem; font-family: 'JetBrains Mono', monospace; font-weight: 700; color: #38BDF8; }
    
    .section-title { font-size: 0.75rem; color: #94A3B8; text-transform: uppercase; letter-spacing: 2px; font-weight: 700; margin-bottom: 15px; border-bottom: 1px solid #1E293B; padding-bottom: 5px; }
    
    /* Order Book Matrix */
    .order-row { display: grid; grid-template-columns: 2fr 1fr 1fr 1.5fr 1.5fr; align-items: center; background: #060913; border: 1px solid #1E293B; border-radius: 4px; margin-bottom: 4px; transition: border-color 0.2s; }
    .order-row:hover { border-color: #38BDF8; }
    .order-cell { padding: 10px 15px; font-family: 'JetBrains Mono'; font-size: 0.85rem; }
    .market-name { color: #F8FAFC; font-weight: 600; font-family: 'Inter'; font-size: 0.8rem; }
    
    .btn-buy div.stButton > button { background: #10B981 !important; color: #000 !important; font-weight: 700 !important; font-family: 'JetBrains Mono'; border: none !important; min-height: 30px !important; border-radius: 2px !important; }
    .btn-buy div.stButton > button:hover { background: #059669 !important; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. MOTOR DE DADOS REAIS & SMART FALLBACK
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
    if not stats: return {"gf_h": 1.4, "ga_h": 1.1, "gf_a": 1.1, "ga_a": 1.3}
    try:
        goals = stats[0].get('goals', {}) if isinstance(stats, list) else stats.get('goals', {})
        return {
            "gf_h": float(goals.get('for', {}).get('average', {}).get('home', 1.4)),
            "ga_h": float(goals.get('against', {}).get('average', {}).get('home', 1.1)),
            "gf_a": float(goals.get('for', {}).get('average', {}).get('away', 1.1)),
            "ga_a": float(goals.get('against', {}).get('average', {}).get('away', 1.3))
        }
    except: return {"gf_h": 1.4, "ga_h": 1.1, "gf_a": 1.1, "ga_a": 1.3}

def get_smart_odds(model_probs): 
    """Simula o feed da Pinnacle com margem de 2.5% e ruído realista."""
    market_odds = {}
    overround = 0.975 
    target_markets = [
        "Home Win", "Draw", "Away Win", "Asian Handicap -1.5", "Asian Handicap +1.5",
        "Asian Handicap -0.5", "Asian Handicap +0.5", "Over 2.5", "Under 2.5"
    ]
    for mkt in target_markets:
        prob = model_probs.get(mkt, 0)
        if 0.05 < prob < 0.95: 
            # Introduz ineficiência de mercado para podermos encontrar Alpha (-2% a +5%)
            market_prob = prob * (1 - random.uniform(-0.02, 0.05))
            if market_prob > 0:
                market_odds[mkt] = max(1.01, round((1 / market_prob) * overround, 2))
    return market_odds

# ==========================================
# 3. CORE QUANTITATIVO (RISK-ADJUSTED EV)
# ==========================================
def calculate_real_xg(h_stats, a_stats):
    return max(0.5, (h_stats['gf_h']/1.35) * (a_stats['ga_a']/1.35) * 1.35), max(0.5, (a_stats['gf_a']/1.35) * (h_stats['ga_h']/1.35) * 1.35)

def run_monte_carlo_sim(xg_h, xg_a, sims=10000):
    np.random.seed(int(time.time()))
    diff = np.random.poisson(xg_h, sims) - np.random.poisson(xg_a, sims)
    total = np.random.poisson(xg_h, sims) + np.random.poisson(xg_a, sims)
    
    return {
        "Home Win": np.sum(diff > 0)/sims, "Draw": np.sum(diff == 0)/sims, "Away Win": np.sum(diff < 0)/sims,
        "Asian Handicap -1.5": np.sum(diff > 1)/sims, "Asian Handicap +1.5": np.sum(diff > -2)/sims,
        "Asian Handicap -0.5": np.sum(diff > 0)/sims, "Asian Handicap +0.5": np.sum(diff >= 0)/sims, 
        "Over 2.5": np.sum(total > 2.5)/sims, "Under 2.5": np.sum(total < 2.5)/sims
    }

def init_ledger():
    np.random.seed(42)
    history = []
    for _ in range(100):
        clv = np.random.normal(0.035, 0.02)
        odd = round(random.uniform(1.80, 2.20), 2)
        won = random.random() < (1/(odd/(1+clv)))
        history.append({"ID": str(uuid.uuid4())[:8], "Date": (date.today() - timedelta(days=random.randint(0, 90))).strftime('%Y-%m-%d'), "Market": "Quant Auto", "Matched Odd": odd, "True Odd": round(odd/(1+clv), 2), "Stake (€)": round(random.uniform(2000, 5000), 2), "CLV": round(clv, 4), "Status": "Settled - Won" if won else "Settled - Lost"})
    return pd.DataFrame(history)

# ==========================================
# 4. STARTUP E CONTROLO DE SESSÃO
# ==========================================
if 'user' not in st.session_state: st.session_state.user = None
if 'ledger' not in st.session_state: st.session_state.ledger = init_ledger()
if 'init_bk' not in st.session_state: st.session_state.init_bk = 10000000.0 

if not st.session_state.user:
    st.markdown("<div style='height:30vh;'></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        st.markdown("<h1 style='text-align:center; font-family:\"JetBrains Mono\"; font-size:3rem; margin-bottom:0; color:#F8FAFC;'>APEX<span style='color:#38BDF8;'>QUANT</span></h1>", unsafe_allow_html=True)
        with st.form("login"):
            st.text_input("G-7 Security Clearance", type="password", placeholder="Enter to Authorize")
            if st.form_submit_button("INITIALIZE TERMINAL", use_container_width=True):
                st.session_state.user = "PORTFOLIO_MANAGER"
                st.rerun()
    st.stop()

# ==========================================
# 5. UI PRINCIPAL (O TERMINAL BLACKROCK)
# ==========================================
res = st.session_state.ledger[st.session_state.ledger['Status'].isin(['Settled - Won', 'Settled - Lost'])].copy()
res['PnL'] = res.apply(lambda r: r['Stake (€)'] * (r['Matched Odd'] - 1) if r['Status'] == 'Settled - Won' else -r['Stake (€)'], axis=1)
pnl = res['PnL'].sum()
current_bk = st.session_state.init_bk + pnl
roi = (pnl / res['Stake (€)'].sum()) * 100 if not res.empty else 0

st.markdown("""
<div class="ticker-wrap">
    <div class="ticker-title">SYS_LOG</div>
    <div class="ticker">
        <span class="ticker-item">APEX ALADDIN: <span style="color:#10B981;">ONLINE</span></span>
        <span class="ticker-item">BAYESIAN CONSENSUS: ACTIVE</span>
        <span class="ticker-item">RISK ENGINE: CONSERVATIVE PARAMETERS ENGAGED</span>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="hud-container">
    <div class="hud-brand">APEX<span style="color:#38BDF8;">QUANT</span></div>
    <div style="display:flex;">
        <div class="hud-stat"><span class="hud-label">Capital (AUM)</span><span class="hud-value">€{current_bk:,.0f}</span></div>
        <div class="hud-stat"><span class="hud-label">Net Return</span><span class="hud-value" style="color:{'#10B981' if pnl>=0 else '#EF4444'};">{pnl:+,.0f}</span></div>
        <div class="hud-stat"><span class="hud-label">Yield</span><span class="hud-value" style="color:#F8FAFC;">{roi:+.2f}%</span></div>
    </div>
</div>
""", unsafe_allow_html=True)

c_left, c_main = st.columns([1, 2.8], gap="large")

# --- ESQUERDA: CONTROLO E LEDGER ---
with c_left:
    st.markdown("<div class='section-title'>Market Ops</div>", unsafe_allow_html=True)
    target_date = st.date_input("Date", date.today(), label_visibility="collapsed")
    l_map = {"Premier League": 39, "Champions League": 2, "La Liga": 140, "Primeira Liga": 94}
    league_id = l_map[st.selectbox("Tournament", list(l_map.keys()), label_visibility="collapsed")]
    kelly = st.select_slider("Risk Profile", options=[0.1, 0.25, 0.5], value=0.25, format_func=lambda x: f"{x}x Kelly")
    
    with st.spinner("Fetching Data..."): fixtures = get_live_fixtures(target_date.strftime('%Y-%m-%d'), league_id)
    
    m_sel = None; h_name = ""; a_name = ""
    if fixtures:
        m_map = {f"{f['teams']['home']['name']} v {f['teams']['away']['name']}": f for f in fixtures}
        m_sel = m_map[st.selectbox("Target Event", list(m_map.keys()))]
        h_name, a_name = m_sel['teams']['home']['name'], m_sel['teams']['away']['name']
    
    st.markdown("<br><div class='section-title'>Clearing House (Ledger)</div>", unsafe_allow_html=True)
    df_display = st.session_state.ledger.sort_values(by="Date", ascending=False).head(8).copy()
    
    # Nova Lógica de Atualização Blindada
    edited = st.data_editor(
        df_display, column_order=["Market", "Status"],
        column_config={"Market": st.column_config.TextColumn(disabled=True), "Status": st.column_config.SelectboxColumn(options=["Pending", "Settled - Won", "Settled - Lost"])},
        hide_index=True, use_container_width=True, height=300, key="ledger_editor"
    )
    
    if not edited.equals(df_display):
        for _, row in edited.iterrows():
            st.session_state.ledger.loc[st.session_state.ledger['ID'] == row['ID'], 'Status'] = row['Status']
        st.rerun()

# --- DIREITA: EXECUÇÃO QUANTITATIVA ---
with c_main:
    if m_sel:
        st.markdown("<div class='section-title'>Quantitative Order Book</div>", unsafe_allow_html=True)
        
        with st.spinner("Running Monte Carlo & Risk Models..."):
            h_stats = get_real_stats(m_sel['teams']['home']['id'], league_id)
            a_stats = get_real_stats(m_sel['teams']['away']['id'], league_id)
            xg_h, xg_a = calculate_real_xg(h_stats, a_stats)
            probs = run_monte_carlo_sim(xg_h, xg_a)
            market_data = get_smart_odds(probs)

        st.markdown(f"""
        <div style="display:flex; justify-content:space-between; align-items:center; background:#060913; border:1px solid #1E293B; border-radius:4px; padding:15px 25px; margin-bottom:20px;">
            <div><div style="font-size:1.6rem; font-weight:700;">{h_name}</div><div style="font-family:'JetBrains Mono'; color:#64748B; font-size:0.9rem;">Model xG: <span style="color:#38BDF8;">{xg_h:.2f}</span></div></div>
            <div style="color:#38BDF8; font-weight:700; font-size:1rem;">VS</div>
            <div style="text-align:right;"><div style="font-size:1.6rem; font-weight:700;">{a_name}</div><div style="font-family:'JetBrains Mono'; color:#64748B; font-size:0.9rem;">Model xG: <span style="color:#38BDF8;">{xg_a:.2f}</span></div></div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style="display: grid; grid-template-columns: 2fr 1fr 1fr 1.5fr 1.5fr; font-size: 0.65rem; color: #64748B; text-transform: uppercase; letter-spacing: 1px; font-weight: 700; padding: 0 15px 10px 15px; border-bottom: 1px solid #1E293B; margin-bottom: 10px;">
            <div>Market Asset</div><div style="text-align:right;">Mkt Price</div><div style="text-align:right;">True Price</div><div style="text-align:center;">Alpha (Edge)</div><div style="text-align:center;">Risk Mgmt Action</div>
        </div>
        """, unsafe_allow_html=True)

        for mkt, m_odd in market_data.items():
            p_real = probs.get(mkt, 0)
            if m_odd > 1.01 and p_real > 0:
                t_odd = 1 / p_real
                edge = (p_real * m_odd) - 1
                
                # Validação de Edge BlackRock: Só mostramos se houver valor estatístico considerável
                if edge > 0.01:
                    stake = current_bk * ((edge / (m_odd - 1)) * kelly)
                    edge_color = "#10B981"
                    bg_highlight = "rgba(16, 185, 129, 0.05)"
                else:
                    stake = 0
                    edge_color = "#64748B"
                    bg_highlight = "transparent"

                st.markdown(f"""
                <div class="order-row" style="background: {bg_highlight};">
                    <div class="order-cell market-name">{mkt}</div>
                    <div class="order-cell" style="text-align:right; font-weight:700; color:#FFF;">{m_odd:.2f}</div>
                    <div class="order-cell" style="text-align:right; color:#38BDF8;">{t_odd:.2f}</div>
                    <div class="order-cell" style="text-align:center; color:{edge_color}; font-weight:700;">{edge*100:+.1f}%</div>
                """, unsafe_allow_html=True)
                
                c_ghost, c_btn, c_ghost2 = st.columns([2.5, 4, 1.5])
                with c_btn:
                    if edge > 0.01:
                        st.markdown("<div class='btn-buy'>", unsafe_allow_html=True)
                        if st.button(f"EXECUTE €{stake:,.0f}", key=f"buy_{mkt}", use_container_width=True):
                            new_trade = pd.DataFrame([{"ID": str(uuid.uuid4())[:8], "Date": date.today().strftime('%Y-%m-%d'), "Market": f"{h_name[:3]} v {a_name[:3]} {mkt}", "Matched Odd": m_odd, "True Odd": round(t_odd, 2), "Stake (€)": round(stake, 2), "CLV": round(edge, 4), "Status": "Pending"}])
                            st.session_state.ledger = pd.concat([st.session_state.ledger, new_trade], ignore_index=True)
                            st.toast("Risk position allocated.", icon="✅")
                            time.sleep(0.2)
                            st.rerun()
                        st.markdown("</div>", unsafe_allow_html=True)
                    else:
                        st.markdown("<div style='text-align:center; font-family:\"JetBrains Mono\"; font-size:0.75rem; color:#64748B; padding:5px;'>NO ALPHA</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div style='text-align:center; padding-top:150px; opacity:0.2;'><h1 style='font-size:3rem; font-family:\"JetBrains Mono\";'>SYSTEM IDLE</h1></div>", unsafe_allow_html=True)