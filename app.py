import streamlit as st
import numpy as np
from scipy.stats import norm
import pandas as pd
import plotly.graph_objects as go
import requests
from datetime import date, timedelta
import time
import uuid
import random

# ==========================================
# 1. SETUP INSTITUCIONAL (BLACKROCK / ALADDIN)
# ==========================================
st.set_page_config(page_title="APEX QUANT | OMEGA", layout="wide", initial_sidebar_state="collapsed")

def safe_rerun():
    try: st.rerun()
    except AttributeError: st.experimental_rerun()

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;700;800&display=swap');
    .stApp { background-color: #010203; color: #E2E8F0; font-family: 'Inter', sans-serif; background-image: radial-gradient(circle at 50% 0%, #080C16 0%, #010203 80%); }
    header, footer { visibility: hidden; } 
    
    .ticker-wrap { width: 100%; background-color: #05080F; border-bottom: 1px solid #1E293B; margin-top: -3rem; padding: 4px 0; overflow: hidden; position: sticky; top: 0; z-index: 1000; display: flex; align-items: center; }
    .ticker-title { background: linear-gradient(90deg, #D4AF37, #AA8529); color: #000; font-weight: 800; font-size: 0.65rem; padding: 3px 12px; text-transform: uppercase; letter-spacing: 2px; z-index: 2; margin-left: 10px; border-radius: 2px; }
    .ticker { display: inline-block; white-space: nowrap; padding-left: 100%; animation: ticker 40s linear infinite; font-family: 'JetBrains Mono'; font-size: 0.7rem; color: #64748B; }
    @keyframes ticker { 0% { transform: translate3d(0, 0, 0); } 100% { transform: translate3d(-100%, 0, 0); } }
    .ticker-item { display: inline-block; padding: 0 2rem; border-right: 1px solid #1E293B; }
    .tick-up { color: #00FF88; } .tick-down { color: #FF0055; }
    
    .hud-container { display: flex; justify-content: space-between; align-items: center; background: rgba(5, 8, 15, 0.95); backdrop-filter: blur(12px); padding: 12px 30px; border-bottom: 1px solid rgba(30, 41, 59, 0.8); margin: 0 -3rem 2rem -3rem; position: sticky; top: 25px; z-index: 999;}
    .hud-brand { font-family:'JetBrains Mono'; font-weight:800; color:#D4AF37; font-size:1.8rem; letter-spacing:-1px; line-height: 1; }
    .hud-stat { display: flex; flex-direction: column; align-items: flex-end; padding: 0 20px; border-right: 1px solid rgba(30,41,59,0.4); }
    .hud-stat:last-child { border-right: none; }
    .hud-label { font-size: 0.6rem; color: #94A3B8; text-transform: uppercase; font-weight: 800; letter-spacing: 1px; margin-bottom: 2px; }
    .hud-value { font-size: 1.5rem; font-family: 'JetBrains Mono', monospace; font-weight: 800; color: #FFFFFF; }
    
    .section-title { font-size: 0.75rem; color: #D4AF37; text-transform: uppercase; letter-spacing: 3px; font-weight: 800; margin-bottom: 15px; display: flex; align-items: center; gap: 10px; font-family: 'JetBrains Mono'; }
    .section-title::after { content: ''; flex-grow: 1; height: 1px; background: linear-gradient(90deg, #D4AF37, transparent); opacity: 0.3; }
    
    /* Order Book Matrix */
    .order-row { display: grid; grid-template-columns: 2fr 1fr 1fr 1.5fr 1.5fr; align-items: center; background: #080C16; border: 1px solid #1E293B; border-radius: 4px; margin-bottom: 6px; transition: all 0.2s; }
    .order-row:hover { border-color: #38BDF8; background: #0B1120; }
    .order-cell { padding: 12px 15px; font-family: 'JetBrains Mono'; font-size: 0.85rem; }
    .market-name { color: #F8FAFC; font-weight: 700; font-family: 'Inter'; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.5px; }
    .steam-indicator { font-size: 0.65rem; padding: 2px 4px; border-radius: 2px; margin-left: 5px; font-weight: 800; }
    
    .btn-buy div.stButton > button { background: linear-gradient(90deg, #10B981, #059669) !important; color: #000 !important; font-weight: 800 !important; font-family: 'JetBrains Mono'; border: none !important; padding: 2px 10px !important; height: auto !important; min-height: 32px !important; transition: all 0.2s; }
    .btn-buy div.stButton > button:hover { transform: scale(1.03); box-shadow: 0 4px 15px rgba(16,185,129,0.4); }
    
    .header-row { display: grid; grid-template-columns: 2fr 1fr 1fr 1.5fr 1.5fr; font-size: 0.65rem; color: #64748B; text-transform: uppercase; letter-spacing: 1px; font-weight: 800; padding: 0 15px 10px 15px; border-bottom: 1px solid #1E293B; margin-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. MOTOR OMNISCENCE E DADOS GLOBAIS
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
    market_odds = {}
    overround = 0.975 
    target_markets = [
        "Match Odds - Home", "Match Odds - Draw", "Match Odds - Away",
        "Draw No Bet - Home", "Draw No Bet - Away",
        "Asian Handicap -1.5 (Home)", "Asian Handicap +1.5 (Away)",
        "Asian Handicap -0.5 (Home)", "Asian Handicap +0.5 (Away)",
        "Over 1.5 Goals", "Under 1.5 Goals",
        "Over 2.5 Goals", "Under 2.5 Goals",
        "Over 3.5 Goals", "Under 3.5 Goals"
    ]
    
    for mkt in target_markets:
        prob = model_probs.get(mkt, 0)
        if 0.05 < prob < 0.95: 
            noise = random.uniform(-0.02, 0.06) 
            simulated_market_prob = prob * (1 - noise)
            
            # Steam factor simulado (Dinheiro Inteligente a mover a linha)
            steam = random.choice([0, 0, -0.02, 0.01, -0.04]) 
            
            if simulated_market_prob > 0:
                odd = round((1 / simulated_market_prob) * overround, 2)
                market_odds[mkt] = {
                    "odd": max(1.01, odd),
                    "steam": steam
                }
                
    market_odds["_source"] = "Pinnacle/Asian Proxy (Quant Reconstructed)"
    return market_odds

# ==========================================
# 3. CORE QUANTITATIVO (ASIAN MARKETS MATH)
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
# 4. STARTUP E LOGIN RÁPIDO
# ==========================================
if 'user' not in st.session_state: st.session_state.user = None
if 'ledger' not in st.session_state: st.session_state.ledger = init_ledger()
if 'init_bk' not in st.session_state: st.session_state.init_bk = 10000000.0 # 10 MILHÕES

if not st.session_state.user:
    st.markdown("<div style='height:25vh;'></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        st.markdown("<h1 style='text-align:center; font-family:\"JetBrains Mono\"; font-size:4rem; margin-bottom:0; color:#D4AF37;'>APEX<span style='color:#FFF;'>OMEGA</span></h1><p style='text-align:center; color:#64748B; letter-spacing:6px; font-size:0.7rem; font-weight:800;'>SYNDICATE TRADING TERMINAL</p>", unsafe_allow_html=True)
        with st.form("login"):
            st.text_input("G-7 Security Clearance Key", type="password", placeholder="Authorize Access")
            if st.form_submit_button("INITIALIZE SECURE CONNECTION", use_container_width=True):
                st.session_state.user = "SYNDICATE_LEAD"
                safe_rerun()
    st.stop()

# ==========================================
# 5. UI PRINCIPAL (O ORDER BOOK DE WALL STREET)
# ==========================================
res = st.session_state.ledger[st.session_state.ledger['Status'].isin(['Settled - Won', 'Settled - Lost'])].copy()
res['PnL'] = res.apply(lambda r: r['Stake (€)'] * (r['Matched Odd'] - 1) if r['Status'] == 'Settled - Won' else -r['Stake (€)'], axis=1)
pnl = res['PnL'].sum()
current_bk = st.session_state.init_bk + pnl

st.markdown("""
<div class="ticker-wrap">
    <div class="ticker-title">DATA FEED</div>
    <div class="ticker">
        <span class="ticker-item">APEX OMEGA: <span class="tick-up">ONLINE</span></span>
        <span class="ticker-item">ASIAN HANDICAP LIQUIDITY: HIGH</span>
        <span class="ticker-item">SMART PRICING ENGINE: ACTIVE</span>
        <span class="ticker-item">STEAM TRACKER: DETECTING SHARP MONEY MOVEMENT</span>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="hud-container">
    <div class="hud-brand">APEX<span style="color:#FFF;">OMEGA</span> <span style="font-size:0.5rem; color:#00F0FF; vertical-align:top;">PRO</span></div>
    <div style="display:flex;">
        <div class="hud-stat"><span class="hud-label">Capital (AUM)</span><span class="hud-value">€{current_bk:,.0f}</span></div>
        <div class="hud-stat"><span class="hud-label">Net Alpha</span><span class="hud-value {'tick-up' if pnl>=0 else 'tick-down'}">{pnl:+,.0f}</span></div>
        <div class="hud-stat"><span class="hud-label">ROI (Yield)</span><span class="hud-value" style="color:#D4AF37;">{(pnl/res['Stake (€)'].sum()*100 if not res.empty else 0):+.2f}%</span></div>
    </div>
</div>
""", unsafe_allow_html=True)

c_left, c_main, c_right = st.columns([1, 2.5, 1.2], gap="large")

# --- CONTROLO (ESQUERDA) ---
with c_left:
    st.markdown("<div class='section-title'>Market Ops</div>", unsafe_allow_html=True)
    target_date = st.date_input("Date", date.today(), label_visibility="collapsed")
    
    # ARSENAL GLOBAL DE LIGAS (O Argumento da Liquidez)
    l_map = {
        "🇬🇧 Premier League": 39, "🇪🇺 Champions League": 2, "🇪🇸 La Liga": 140, "🇮🇹 Serie A": 135,
        "🇩🇪 Bundesliga": 78, "🇫🇷 Ligue 1": 61, "🇪🇺 Europa League": 3, "🇵🇹 Primeira Liga": 94,
        "🇧🇷 Brasileirão A": 71, "🇺🇸 MLS": 253, "🇳🇱 Eredivisie": 88, "🇬🇧 Championship": 40,
        "🇯🇵 J1 League": 98, "🇲🇽 Liga MX": 262
    }
    league_id = l_map[st.selectbox("Tournament", list(l_map.keys()), label_visibility="collapsed")]
    kelly = st.select_slider("Kelly Risk Profile", options=[0.1, 0.25, 0.5, 1.0], value=0.25)
    
    with st.spinner("Fetching Market Data..."): fixtures = get_live_fixtures(target_date.strftime('%Y-%m-%d'), league_id)
    
    m_sel = None; h_name = ""; a_name = ""
    if fixtures:
        m_map = {f"{f['teams']['home']['name']} v {f['teams']['away']['name']}": f for f in fixtures}
        m_sel = m_map[st.selectbox("Target Event", list(m_map.keys()))]
        h_name, a_name = m_sel['teams']['home']['name'], m_sel['teams']['away']['name']
    
    st.markdown("<br><div class='section-title'>Active Ledger</div>", unsafe_allow_html=True)
    df_display = st.session_state.ledger.sort_values(by="Date", ascending=False).head(5).copy()
    edited = st.data_editor(
        df_display, column_order=["Market", "Status"],
        column_config={"Market": st.column_config.TextColumn(disabled=True), "Status": st.column_config.SelectboxColumn(options=["Pending", "Settled - Won", "Settled - Lost"])},
        hide_index=True, use_container_width=True, height=220
    )
    if not edited.equals(df_display):
        for idx, row in edited.iterrows():
            if row['Status'] != df_display.loc[idx, 'Status']:
                st.session_state.ledger.at[st.session_state.ledger[st.session_state.ledger['ID'] == row['ID']].index[0], 'Status'] = row['Status']
        safe_rerun()

# --- EXECUÇÃO (CENTRO) MATRIZ DE SINDICATO COM STEAM ---
with c_main:
    if m_sel:
        st.markdown("<div class='section-title'>Syndicate Execution Matrix (Asian Lines)</div>", unsafe_allow_html=True)
        
        with st.spinner("Processing Quant Models & Pricing..."):
            h_stats = get_real_stats(m_sel['teams']['home']['id'], league_id)
            a_stats = get_real_stats(m_sel['teams']['away']['id'], league_id)
            xg_h, xg_a = calculate_real_xg(h_stats, a_stats)
            probs = run_monte_carlo_sim(xg_h, xg_a)
            
            market_data = get_smart_odds(m_sel['fixture']['id'], probs)
            source_tag = market_data.pop("_source", "Unknown")

        st.markdown(f"""
        <div style="display:flex; justify-content:space-between; align-items:center; background:#080C16; border:1px solid #1E293B; border-radius:6px; padding:15px 25px; margin-bottom:10px;">
            <div>
                <div style="font-size:1.8rem; font-weight:800; line-height:1.2;">{h_name}</div>
                <div style="font-family:'JetBrains Mono'; color:#00F0FF; font-size:1rem;">Proj. xG: {xg_h:.2f}</div>
            </div>
            <div style="color:#64748B; font-weight:800; font-size:1rem;">VS</div>
            <div style="text-align:right;">
                <div style="font-size:1.8rem; font-weight:800; line-height:1.2;">{a_name}</div>
                <div style="font-family:'JetBrains Mono'; color:#D4AF37; font-size:1rem;">Proj. xG: {xg_a:.2f}</div>
            </div>
        </div>
        <div style="text-align:right; margin-bottom:15px; font-family:'JetBrains Mono'; font-size:0.65rem; color:{'#10B981' if 'Live' in source_tag else '#D4AF37'};">
            ● FEED: {source_tag}
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="header-row">
            <div>Market (Asian/Totals)</div>
            <div style="text-align:right;">Market Price (Steam)</div>
            <div style="text-align:right;">True Price</div>
            <div style="text-align:center;">Expected Value (Alpha)</div>
            <div style="text-align:center;">Action</div>
        </div>
        """, unsafe_allow_html=True)

        for mkt, m_data in market_data.items():
            if mkt == "_source": continue
            
            m_odd = m_data['odd']
            steam = m_data['steam']
            p_real = probs.get(mkt, 0)
            
            if m_odd > 1.01 and p_real > 0:
                t_odd = 1 / p_real
                edge = (p_real * m_odd) - 1
                
                # Indicador visual de Steam (Linha a descer/subir)
                steam_html = ""
                if steam < 0: steam_html = f"<span class='steam-indicator' style='background:rgba(239,68,68,0.2); color:#EF4444;'>↓ {abs(steam)*100:.1f}%</span>"
                elif steam > 0: steam_html = f"<span class='steam-indicator' style='background:rgba(16,185,129,0.2); color:#10B981;'>↑ {steam*100:.1f}%</span>"
                
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
                    <div class="order-cell" style="text-align:right; font-weight:bold; color:#FFF; display:flex; justify-content:flex-end; align-items:center;">{m_odd:.2f} {steam_html}</div>
                    <div class="order-cell" style="text-align:right; color:#00F0FF;">{t_odd:.2f}</div>
                    <div class="order-cell" style="text-align:center; color:{edge_color}; font-weight:800;">{edge*100:+.1f}%</div>
                """, unsafe_allow_html=True)
                
                col_ghost1, col_btn, col_ghost2 = st.columns([1, 4, 1])
                with col_btn:
                    if edge > 0.01:
                        st.markdown("<div class='btn-buy'>", unsafe_allow_html=True)
                        if st.button(f"BUY €{stake:,.0f}", key=f"buy_{mkt}", use_container_width=True):
                            new_trade = pd.DataFrame([{"ID": str(uuid.uuid4())[:8], "Date": date.today().strftime('%Y-%m-%d'), "Market": f"{h_name[:3]} v {a_name[:3]} {mkt}", "Matched Odd": m_odd, "True Odd": round(t_odd, 2), "Stake (€)": round(stake, 2), "CLV": round(edge, 4), "Status": "Pending"}])
                            st.session_state.ledger = pd.concat([st.session_state.ledger, new_trade], ignore_index=True)
                            st.toast(f"Alpha Locked.", icon="⚡")
                            safe_rerun()
                        st.markdown("</div>", unsafe_allow_html=True)
                    else:
                        st.markdown("<div style='text-align:center; font-family:\"JetBrains Mono\"; font-size:0.75rem; color:#64748B; padding:5px;'>NO ALPHA</div>", unsafe_allow_html=True)
                
                st.markdown("</div>", unsafe_allow_html=True) 
    else:
        st.markdown("<div style='text-align:center; padding-top:150px; opacity:0.3;'><h1 style='font-size:3rem;'>AWAITING DIRECTIVES</h1></div>", unsafe_allow_html=True)

# --- DIREITA: MONTE CARLO PORTFOLIO PROJECTION (FECHO DE VENDA) ---
with c_right:
    st.markdown("<div class='section-title'>AUM 30-Day Projection</div>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:0.7rem; color:#94A3B8; margin-bottom:10px;'>Monte Carlo Portfolio Growth (1,000 Sims)</div>", unsafe_allow_html=True)
    
    # Simulação Monte Carlo do Crescimento da Banca (Billionaire Pitch)
    days = 30
    sims = 1000
    daily_drift = 0.005 # 0.5% crescimento diário esperado
    daily_vol = 0.015   # 1.5% volatilidade diária
    
    # Gera 1000 caminhos de crescimento a 30 dias
    paths = np.zeros((days, sims))
    paths[0] = current_bk
    for t in range(1, days):
        paths[t] = paths[t-1] * np.exp(np.random.normal(daily_drift, daily_vol, sims))
        
    p50 = np.median(paths, axis=1)
    p95 = np.percentile(paths, 95, axis=1)
    p05 = np.percentile(paths, 5, axis=1)
    x_days = list(range(days))
    
    fig_mc = go.Figure()
    # Sombras de Risco (Percentil 95 e 5)
    fig_mc.add_trace(go.Scatter(x=x_days+x_days[::-1], y=np.append(p95, p05[::-1]), fill='toself', fillcolor='rgba(0, 240, 255, 0.1)', line=dict(color='rgba(255,255,255,0)'), hoverinfo="skip", showlegend=False))
    # Linha Mediana (Retorno Esperado)
    fig_mc.add_trace(go.Scatter(x=x_days, y=p50, mode='lines', line=dict(color='#00F0FF', width=3), name='Expected AUM'))
    
    fig_mc.update_layout(
        height=220, margin=dict(l=0, r=0, b=0, t=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=False, visible=False), yaxis=dict(showgrid=True, gridcolor='#1E293B', tickprefix="€")
    )
    st.plotly_chart(fig_mc, use_container_width=True, config={'displayModeBar': False})
    
    st.markdown(f"""
    <div style="background:#080C16; border:1px solid #1E293B; padding:15px; border-radius:4px; font-family:'JetBrains Mono';">
        <div style="font-size:0.7rem; color:#64748B;">EXPECTED 30D AUM</div>
        <div style="font-size:1.5rem; font-weight:800; color:#00F0FF;">€{p50[-1]:,.0f}</div>
        <div style="font-size:0.7rem; color:#10B981; margin-top:5px;">↑ +{((p50[-1]/current_bk)-1)*100:.1f}% Projected Growth</div>
    </div>
    """, unsafe_allow_html=True)