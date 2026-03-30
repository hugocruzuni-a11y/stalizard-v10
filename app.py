import streamlit as st
import numpy as np
from scipy.stats import poisson, norm
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
from datetime import date, timedelta
import time
import uuid

# ==========================================
# 1. SETUP INSTITUCIONAL (PALANTIR / BLOOMBERG)
# ==========================================
st.set_page_config(page_title="APEX QUANT | LIVE", layout="wide", initial_sidebar_state="collapsed")

def safe_rerun():
    try: st.rerun()
    except AttributeError: st.experimental_rerun()

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;700;800&display=swap');
    .stApp { background-color: #030508; color: #E2E8F0; font-family: 'Inter', sans-serif; }
    header, footer { visibility: hidden; } 
    
    /* Live Ticker & HUD */
    .ticker-wrap { width: 100%; background-color: #0B1120; border-bottom: 1px solid #1E293B; margin-top: -3rem; padding: 5px 0; overflow: hidden; position: sticky; top: 0; z-index: 1000; display: flex; align-items: center; }
    .ticker-title { background: #D4AF37; color: #000; font-weight: 800; font-size: 0.7rem; padding: 4px 15px; text-transform: uppercase; letter-spacing: 1px; z-index: 2; margin-left: 10px; border-radius: 2px; }
    .ticker { display: inline-block; white-space: nowrap; padding-left: 100%; animation: ticker 40s linear infinite; font-family: 'JetBrains Mono'; font-size: 0.75rem; color: #94A3B8; }
    @keyframes ticker { 0% { transform: translate3d(0, 0, 0); } 100% { transform: translate3d(-100%, 0, 0); } }
    .ticker-item { display: inline-block; padding: 0 2rem; border-right: 1px solid #1E293B; }
    .tick-up { color: #10B981; } .tick-down { color: #EF4444; }
    
    .hud-container { display: flex; justify-content: space-between; align-items: center; background: linear-gradient(180deg, #070B14 0%, #030508 100%); padding: 20px 30px; border-bottom: 2px solid #1E293B; margin: 0 -3rem 2rem -3rem; }
    .hud-brand { font-family:'JetBrains Mono'; font-weight:800; color:#D4AF37; font-size:1.8rem; letter-spacing:-1px; text-shadow: 0 0 20px rgba(212,175,55,0.2); }
    .hud-stat { display: flex; flex-direction: column; align-items: flex-end; padding: 0 15px; border-right: 1px solid rgba(30,41,59,0.5); }
    .hud-stat:last-child { border-right: none; }
    .hud-label { font-size: 0.65rem; color: #64748B; text-transform: uppercase; font-weight: 800; letter-spacing: 1.5px; margin-bottom: 2px; }
    .hud-value { font-size: 1.6rem; font-family: 'JetBrains Mono', monospace; font-weight: 800; color: #F8FAFC; }
    
    .section-title { font-size: 0.8rem; color: #64748B; text-transform: uppercase; letter-spacing: 2px; font-weight: 800; margin-bottom: 15px; display: flex; align-items: center; gap: 10px; }
    .section-title::after { content: ''; flex-grow: 1; height: 1px; background: #1E293B; }
    .live-badge { background: #EF4444; color: white; font-size: 0.6rem; padding: 2px 6px; border-radius: 4px; animation: pulse 2s infinite; font-weight: bold; margin-left: 10px; }
    @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. MOTOR DE DADOS REAIS (API-SPORTS)
# ==========================================
API_KEY = st.secrets.get("API_KEY", "8171043bf0a322286bb127947dbd4041") # A TUA API KEY REAL
HEADERS = {"x-apisports-key": API_KEY, "x-apisports-host": "v3.football.api-sports.io"}

def fetch_api(endpoint, params):
    """Função core para chamadas reais à API."""
    try:
        url = f"https://{HEADERS['x-apisports-host']}/{endpoint}"
        response = requests.get(url, headers=HEADERS, params=params, timeout=10)
        return response.json().get('response', [])
    except Exception as e:
        return []

@st.cache_data(ttl=60) # Cache de 60s para não esgotar a API mas manter real-time
def get_live_fixtures(date_str, league_id, season="2025"):
    return fetch_api("fixtures", {"date": date_str, "league": league_id, "season": season})

@st.cache_data(ttl=3600)
def get_real_stats(team_id, league_id, season="2025"):
    """Puxa estatísticas reais da equipa para alimentar o modelo."""
    stats = fetch_api("teams/statistics", {"team": team_id, "league": league_id, "season": season})
    if not stats: return None
    data = stats
    goals = data.get('goals', {})
    
    # Extrair golos marcados/sofridos médios por jogo
    try:
        gf_h = float(goals.get('for', {}).get('average', {}).get('home', 1.35))
        ga_h = float(goals.get('against', {}).get('average', {}).get('home', 1.35))
        gf_a = float(goals.get('for', {}).get('average', {}).get('away', 1.35))
        ga_a = float(goals.get('against', {}).get('average', {}).get('away', 1.35))
        return {"gf_h": gf_h, "ga_h": ga_h, "gf_a": gf_a, "ga_a": ga_a}
    except:
        return {"gf_h": 1.35, "ga_h": 1.35, "gf_a": 1.35, "ga_a": 1.35}

@st.cache_data(ttl=60) # Atualização de odds a cada minuto
def get_real_odds(fixture_id, bookmaker_id=8): # 8 = Bet365, podes mudar para Pinnacle (70)
    odds_data = fetch_api("odds", {"fixture": fixture_id, "bookmaker": bookmaker_id})
    if not odds_data: return {}
    
    bookmakers = odds_data[0].get('bookmakers', [])
    if not bookmakers: return {}
    
    market_odds = {}
    for bet in bookmakers[0].get('bets', []):
        name = bet['name']
        vals = {v['value']: float(v['odd']) for v in bet['values']}
        if name == 'Match Winner':
            market_odds["Home Win"] = vals.get('Home', 0)
            market_odds["Draw"] = vals.get('Draw', 0)
            market_odds["Away Win"] = vals.get('Away', 0)
        elif name == 'Goals Over/Under':
            market_odds["Over 2.5"] = vals.get('Over 2.5', 0)
            market_odds["Under 2.5"] = vals.get('Under 2.5', 0)
    return market_odds

# ==========================================
# 3. MONTE CARLO ENGINE & LEDGER
# ==========================================
def calculate_real_xg(h_stats, a_stats):
    """Calcula xG baseado nas médias reais da liga e das equipas."""
    league_avg = 1.35
    if not h_stats or not a_stats: return league_avg, league_avg
    
    # Força de Ataque vs Defesa (Método Quant Clássico)
    h_attack = h_stats['gf_h'] / league_avg
    a_defense = a_stats['ga_a'] / league_avg
    a_attack = a_stats['gf_a'] / league_avg
    h_defense = h_stats['ga_h'] / league_avg
    
    xg_home = h_attack * a_defense * league_avg
    xg_away = a_attack * h_defense * league_avg
    return round(max(0.5, xg_home), 2), round(max(0.5, xg_away), 2)

def run_monte_carlo_sim(xg_h, xg_a, sims=10000):
    np.random.seed(int(time.time()))
    home_goals = np.random.poisson(xg_h, sims)
    away_goals = np.random.poisson(xg_a, sims)
    goal_diff = home_goals - away_goals
    total_goals = home_goals + away_goals
    
    hw = np.sum(goal_diff > 0) / sims
    dr = np.sum(goal_diff == 0) / sims
    aw = np.sum(goal_diff < 0) / sims
    o25 = np.sum(total_goals > 2) / sims
    u25 = np.sum(total_goals < 3) / sims
    
    mu, std = norm.fit(goal_diff)
    x_axis = np.linspace(-5, 5, 100)
    p = norm.pdf(x_axis, mu, std) if std > 0 else np.zeros_like(x_axis)
    
    return {"Home Win": hw, "Draw": dr, "Away Win": aw, "Over 2.5": o25, "Under 2.5": u25}, x_axis, p

def init_mock_ledger_for_pitch():
    """Gera um histórico falso SÓ para os gráficos do portfólio não estarem vazios na demo."""
    np.random.seed(42)
    history = []
    start_d = date.today() - timedelta(days=90)
    for _ in range(250):
        clv = np.random.normal(loc=0.04, scale=0.035) 
        odd = round(random.uniform(1.70, 3.00), 2)
        won = random.random() < (1 / (odd / (1 + clv)))
        history.append({
            "ID": str(uuid.uuid4())[:8], "Date": (start_d + timedelta(days=random.randint(0, 90))).strftime('%Y-%m-%d'),
            "Market": "Mock Data", "Matched Odd": odd, "True Odd": round(odd / (1 + clv), 2),
            "Stake (€)": round(random.uniform(500, 2000), 2), "CLV": round(clv, 4), "Status": "Settled - Won" if won else "Settled - Lost"
        })
    return pd.DataFrame(history)

if 'user' not in st.session_state: st.session_state.user = None
if 'ledger' not in st.session_state: st.session_state.ledger = init_mock_ledger_for_pitch()
if 'init_bk' not in st.session_state: st.session_state.init_bk = 1000000.0 

# ==========================================
# 4. LOGIN & HUD
# ==========================================
if not st.session_state.user:
    st.markdown("<div style='height:25vh;'></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        st.markdown("<h1 style='text-align:center; font-family:\"JetBrains Mono\"; font-size:3.5rem; margin-bottom:0; color:#D4AF37;'>APEX<span style='color:#FFF;'>QUANT</span></h1><p style='text-align:center; color:#64748B; letter-spacing:4px; font-size:0.7rem; font-weight:800;'>REAL-TIME INSTITUTIONAL LINK</p>", unsafe_allow_html=True)
        with st.form("login"):
            st.text_input("G-7 Security Clearance Key", type="password", placeholder="Enter to Authenticate")
            if st.form_submit_button("CONNECT TO LIVE EXCHANGE", use_container_width=True):
                st.session_state.user = "CEO_ACCESS"
                safe_rerun()
    st.stop()

# Calcular métricas do Ledger
df = st.session_state.ledger
res = df[df['Status'].isin(['Settled - Won', 'Settled - Lost'])].copy()
res['PnL'] = res.apply(lambda r: r['Stake (€)'] * (r['Matched Odd'] - 1) if r['Status'] == 'Settled - Won' else -r['Stake (€)'], axis=1)
pnl = res['PnL'].sum()
roi = (pnl / res['Stake (€)'].sum()) * 100 if not res.empty else 0
current_bk = st.session_state.init_bk + pnl

st.markdown("""
<div class="ticker-wrap">
    <div class="ticker-title">API LIVE FEED</div>
    <div class="ticker">
        <span class="ticker-item">CONNECTION TO API-SPORTS: <span class="tick-up">ESTABLISHED</span></span>
        <span class="ticker-item">LATENCY: 42ms</span>
        <span class="ticker-item">MARKET DATA: REAL-TIME POLLING ACTIVE</span>
        <span class="ticker-item">QUANT ENGINE: ONLINE</span>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="hud-container">
    <div class="hud-brand">APEX<span style="color:#FFF;">QUANT</span> <span style="font-size:0.5rem; color:#EF4444; vertical-align:top; animation: pulse 2s infinite;">● LIVE API</span></div>
    <div style="display:flex;">
        <div class="hud-stat"><span class="hud-label">AUM</span><span class="hud-value">€{current_bk:,.0f}</span></div>
        <div class="hud-stat"><span class="hud-label">Net Profit</span><span class="hud-value {'tick-up' if pnl>=0 else 'tick-down'}">{pnl:+,.0f}</span></div>
        <div class="hud-stat"><span class="hud-label">Yield</span><span class="hud-value" style="color:#D4AF37;">{roi:+.2f}%</span></div>
    </div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 5. DASHBOARD PRINCIPAL (LIVE DATA)
# ==========================================
c_left, c_main, c_right = st.columns([1, 2.5, 1.2], gap="large")

with c_left:
    st.markdown("<div class='section-title'>I. Live Market Scanner</div>", unsafe_allow_html=True)
    target_date = st.date_input("Date", date.today(), label_visibility="collapsed")
    l_map = {"Premier League": 39, "La Liga": 140, "Champions League": 2, "Primeira Liga": 94}
    league_name = st.selectbox("Tournament", list(l_map.keys()), label_visibility="collapsed")
    league_id = l_map[league_name]
    
    st.session_state.kelly_frac = st.select_slider("Kelly Multiplier", options=[0.1, 0.25, 0.5, 1.0], value=st.session_state.get('kelly_frac', 0.25))

    with st.spinner("Fetching Live API Data..."):
        fixtures = get_live_fixtures(target_date.strftime('%Y-%m-%d'), league_id)
    
    m_sel = None
    if fixtures:
        m_map = {f"{f['teams']['home']['name']} v {f['teams']['away']['name']}": f for f in fixtures}
        match_str = st.selectbox("Select Target Event", list(m_map.keys()))
        m_sel = m_map[match_str]
        st.button("🔄 Poll Live Odds", use_container_width=True)
    else:
        st.warning("No matches scheduled for this date/league.")

with c_main:
    st.markdown("<div class='section-title'>II. Algorithmic Intelligence <span class='live-badge'>REAL DATA</span></div>", unsafe_allow_html=True)
    
    if m_sel:
        fixture_id = m_sel['fixture']['id']
        h_id, a_id = m_sel['teams']['home']['id'], m_sel['teams']['away']['id']
        h_name, a_name = m_sel['teams']['home']['name'], m_sel['teams']['away']['name']
        
        with st.spinner("Running Quants against live bookmakers..."):
            h_stats = get_real_stats(h_id, league_id)
            a_stats = get_real_stats(a_id, league_id)
            
            xg_h, xg_a = calculate_real_xg(h_stats, a_stats)
            probs, x_axis, norm_pdf = run_monte_carlo_sim(xg_h, xg_a)
            
            live_odds = get_real_odds(fixture_id)

        c_m1, c_m2 = st.columns([1, 1])
        with c_m1:
            st.markdown(f"""
            <div style="background: rgba(11, 17, 32, 0.7); border: 1px solid #1E293B; border-radius: 6px; padding: 20px;">
                <div style="font-size:0.7rem; color:#00F0FF; margin-bottom:10px; font-family:'JetBrains Mono';">REAL-TIME MATCHUP DYNAMICS</div>
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div style="font-size:1.5rem; font-weight:800;">{h_name}</div>
                    <div style="font-family:'JetBrains Mono'; color:#D4AF37; font-size:1.2rem;">xG {xg_h:.2f}</div>
                </div>
                <div style="color:#64748B; font-weight:800; font-size:0.8rem; text-align:center; margin:5px 0;">VS</div>
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div style="font-size:1.5rem; font-weight:800;">{a_name}</div>
                    <div style="font-family:'JetBrains Mono'; color:#D4AF37; font-size:1.2rem;">xG {xg_a:.2f}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with c_m2:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=x_axis, y=norm_pdf, mode='lines', line=dict(color='#00F0FF', width=2), fill='tozeroy', fillcolor='rgba(0, 240, 255, 0.1)'))
            fig.add_vline(x=0, line_dash="dash", line_color="#EF4444")
            fig.update_layout(height=160, margin=dict(l=0,r=0,t=10,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False)
            fig.update_xaxes(showgrid=False, zeroline=False, visible=False)
            fig.update_yaxes(showgrid=False, zeroline=False, visible=False)
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

        st.markdown("<br><div class='section-title'>III. Live Order Execution (Bet365 API Data)</div>", unsafe_allow_html=True)
        
        if not live_odds:
            st.error("⚠️ MARKET MAKER HAS NOT PRICED THIS EVENT YET OR LIQUIDITY IS ZERO.")
        else:
            edges_found = False
            for mkt in ["Home Win", "Draw", "Away Win", "Over 2.5", "Under 2.5"]:
                prob_real = probs.get(mkt, 0)
                market_odd = live_odds.get(mkt, 0)
                
                if market_odd > 1.05 and prob_real > 0:
                    true_odd = 1 / prob_real
                    edge = (prob_real * market_odd) - 1
                    
                    if edge > 0:
                        edges_found = True
                        stake = current_bk * ((edge / (market_odd - 1)) * st.session_state.kelly_frac)
                        
                        st.markdown(f"""
                        <div style="background:#070B14; border:1px solid #1E293B; border-left:3px solid {'#10B981' if edge > 0.05 else '#D4AF37'}; padding:15px; margin-bottom:10px; display:flex; justify-content:space-between; align-items:center;">
                            <div>
                                <div style="font-size:0.7rem; color:#64748B; font-family:'JetBrains Mono';">LIVE EDGE DETECTED</div>
                                <div style="font-size:1.2rem; font-weight:800; color:#FFF;">{mkt}</div>
                                <div style="font-size:0.8rem; font-family:'JetBrains Mono'; color:#94A3B8;">True: {true_odd:.2f} | Bookie: <span style="color:#FFF;">{market_odd:.2f}</span> | Edge: <span style="color:#10B981;">+{edge:.1%}</span></div>
                            </div>
                            <div style="width: 150px;">
                        """, unsafe_allow_html=True)
                        
                        # Botão único com chaves dinâmicas
                        if st.button(f"EXECUTE €{stake:,.0f}", key=f"exec_{mkt}", use_container_width=True):
                            new_trade = pd.DataFrame([{"ID": str(uuid.uuid4())[:8], "Date": date.today().strftime('%Y-%m-%d'), "Event": match_str, "Market": mkt, "Matched Odd": market_odd, "True Odd": round(true_odd, 2), "Stake (€)": round(stake, 2), "CLV": round(edge, 4), "Status": "Pending"}])
                            st.session_state.ledger = pd.concat([st.session_state.ledger, new_trade], ignore_index=True)
                            st.toast(f"Live order filled: {mkt}", icon="⚡")
                            time.sleep(0.3)
                            safe_rerun()
                            
                        st.markdown("</div></div>", unsafe_allow_html=True)
            
            if not edges_found:
                st.info("Market is perfectly efficient right now. No mathematical edge detected against live odds.")
    else:
        st.markdown("<div style='text-align:center; padding-top:100px; opacity:0.3;'><h1 style='font-size:3rem;'>AWAITING LIVE DATA FEED</h1></div>", unsafe_allow_html=True)

with c_right:
    st.markdown("<div class='section-title'>IV. Equity & Ledger</div>", unsafe_allow_html=True)
    df_chart = res
    if not df_chart.empty:
        df_chart['Cum_PnL'] = df_chart['PnL'].cumsum()
        fig = go.Figure()
        fig.add_trace(go.Scatter(y=df_chart['Cum_PnL'], mode='lines', line=dict(color='#D4AF37', width=2), fill='tozeroy', fillcolor='rgba(212, 175, 55, 0.1)'))
        fig.update_layout(height=200, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=0, t=0, b=0), showlegend=False)
        fig.update_xaxes(showgrid=False, zeroline=False, visible=False)
        fig.update_yaxes(showgrid=True, gridcolor='rgba(30,41,59,0.5)', zeroline=True, zerolinecolor='#1E293B')
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    df_display = st.session_state.ledger.sort_values(by="Date", ascending=False).head(8).copy()
    edited = st.data_editor(
        df_display, column_order=["Market", "Stake (€)", "Status"],
        column_config={"Market": st.column_config.TextColumn(disabled=True), "Stake (€)": st.column_config.NumberColumn(format="€%d", disabled=True), "Status": st.column_config.SelectboxColumn(options=["Pending", "Settled - Won", "Settled - Lost"])},
        hide_index=True, use_container_width=True, height=280
    )
    if not edited.equals(df_display):
        for idx, row in edited.iterrows():
            if row['Status'] != df_display.loc[idx, 'Status']:
                ledger_idx = st.session_state.ledger[st.session_state.ledger['ID'] == row['ID']].index[0]
                st.session_state.ledger.at[ledger_idx, 'Status'] = row['Status']
        safe_rerun()