import streamlit as st
import numpy as np
import pandas as pd
import requests
import math
import plotly.graph_objects as go
from datetime import date
import time

# ==========================================
# 1. INSTITUTIONAL UX SETUP (WALL STREET TIER)
# ==========================================
st.set_page_config(page_title="APEX QUANT TERMINAL", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700;800&family=Inter:wght@400;500;600;800&display=swap');

/* Base Theme */
.stApp { background-color: #030712; color: #E2E8F0; font-family: 'Inter', sans-serif; }
header, footer { visibility: hidden; }

/* Top Nav with Pulse Animation */
.top-nav { background: rgba(0, 0, 0, 0.8); backdrop-filter: blur(10px); border-bottom: 1px solid #1E293B; padding: 15px 30px; display: flex; justify-content: space-between; align-items: center; margin: -3rem -3rem 2rem -3rem; position: sticky; top: 0; z-index: 1000;}
.logo { font-size: 1.5rem; font-weight: 800; color: #FFFFFF; font-family: 'JetBrains Mono', monospace; letter-spacing: -0.5px; }
.logo span { color: #10B981; }

@keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.4; } 100% { opacity: 1; } }
.sys-status { font-size: 0.75rem; font-weight: 600; color: #10B981; font-family: 'JetBrains Mono', monospace; display: flex; align-items: center; gap: 8px;}
.dot { height: 8px; width: 8px; background-color: #10B981; border-radius: 50%; display: inline-block; animation: pulse 1.5s infinite; box-shadow: 0 0 8px #10B981;}

/* Grid Panels */
.grid-panel { border: 1px solid #1E293B; background: linear-gradient(180deg, #0B0F19 0%, #030712 100%); padding: 22px; margin-bottom: 20px; border-radius: 8px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.5); }
.panel-title { font-size: 0.75rem; color: #64748B; text-transform: uppercase; border-bottom: 1px solid #1E293B; padding-bottom: 10px; margin-bottom: 15px; font-weight: 800; letter-spacing: 1.5px; }

/* Metrics & Values */
.data-row { display: flex; justify-content: space-between; font-size: 0.85rem; margin-bottom: 8px; align-items: center;}
.data-lbl { color: #94A3B8; font-weight: 500; }
.data-val { color: #F8FAFC; font-weight: 700; font-family: 'JetBrains Mono', monospace; }

/* Highlight Colors */
.hl-green { color: #10B981 !important; text-shadow: 0 0 10px rgba(16,185,129,0.3); }
.hl-red { color: #EF4444 !important; }
.hl-blue { color: #38BDF8 !important; }
.hl-warn { color: #F59E0B !important; }

/* Alpha Box (The Money Maker) */
.trade-signal { border: 1px solid rgba(16, 185, 129, 0.5); background: linear-gradient(145deg, rgba(16,185,129,0.08) 0%, rgba(0,0,0,0) 100%); padding: 25px; margin-top: 10px; border-radius: 8px; box-shadow: 0 0 25px rgba(16, 185, 129, 0.15); position: relative; overflow: hidden;}
.trade-signal::before { content: ''; position: absolute; top: 0; left: 0; width: 5px; height: 100%; background: #10B981; }
.trade-asset { font-size: 2.2rem; color: #10B981; font-weight: 800; margin-bottom: 20px; font-family: 'JetBrains Mono', monospace; text-shadow: 0 0 15px rgba(16,185,129,0.4); }

/* Order Book Table */
.ob-table { width: 100%; font-size: 0.85rem; border-collapse: collapse; font-family: 'JetBrains Mono', monospace; }
.ob-table th { color: #64748B; text-align: right; font-weight: 700; border-bottom: 1px solid #334155; padding: 12px 8px; font-family: 'Inter', sans-serif; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.5px;}
.ob-table th:first-child { text-align: left; }
.ob-table td { text-align: right; padding: 12px 8px; border-bottom: 1px solid #0F172A; transition: background 0.2s; }
.ob-table td:first-child { text-align: left; color: #E2E8F0; font-weight: 600; font-family: 'Inter', sans-serif; }
.ob-table tr:hover td { background: rgba(30, 41, 59, 0.5); cursor: crosshair; }

/* Sub-Metric Cards */
.metric-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 20px; }
.metric-card { background: #0F172A; border: 1px solid #1E293B; border-radius: 6px; padding: 15px; text-align: center; }
.metric-card-title { font-size: 0.7rem; color: #64748B; text-transform: uppercase; font-weight: 700; letter-spacing: 1px; margin-bottom: 5px;}
.metric-card-val { font-size: 1.5rem; color: #F8FAFC; font-weight: 800; font-family: 'JetBrains Mono', monospace;}

/* Override Streamlit Widgets */
div[data-baseweb="select"] > div, div[data-baseweb="input"] > div { background-color: #0F172A !important; border: 1px solid #1E293B !important; color: #F8FAFC !important; border-radius: 6px !important; }
.stButton > button { background: linear-gradient(180deg, #1E293B 0%, #0F172A 100%) !important; color: #F8FAFC !important; border: 1px solid #334155 !important; font-weight: 700 !important; width: 100%; border-radius: 6px !important; padding: 20px !important; transition: all 0.3s ease !important; }
.stButton > button:hover { background: #10B981 !important; color: #030712 !important; border-color: #10B981 !important; box-shadow: 0 0 15px rgba(16,185,129,0.4) !important; transform: translateY(-1px); }

/* Insights Manual */
.manual-box { font-size: 0.75rem; color: #94A3B8; border-left: 2px solid #38BDF8; padding-left: 15px; margin-top: 10px; line-height: 1.6; background: rgba(56, 189, 248, 0.05); padding: 15px; border-radius: 0 6px 6px 0;}
.manual-term { color: #38BDF8; font-weight: 700; display: block; margin-top: 8px; text-transform: uppercase; letter-spacing: 0.5px;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. ALGORITHMIC ENGINE
# ==========================================
API_KEY = st.secrets.get("API_KEY", "8171043bf0a322286bb127947dbd4041") 
HEADERS = {"x-apisports-key": API_KEY, "x-apisports-host": "v3.football.api-sports.io"}

def fetch_api(endpoint, params):
    try:
        r = requests.get(f"https://{HEADERS['x-apisports-host']}/{endpoint}", headers=HEADERS, params=params, timeout=10)
        return r.json().get('response', [])
    except: return []

@st.cache_data(ttl=60) 
def get_live_fixtures(date_str, league_id, season="2025"):
    return fetch_api("fixtures", {"date": date_str, "league": league_id, "season": season})

@st.cache_data(ttl=3600)
def get_real_stats(team_id, league_id, season="2025"):
    stats = fetch_api("teams/statistics", {"team": team_id, "league": league_id, "season": season})
    if not stats: return {"gf_h": 1.55, "ga_h": 1.25, "gf_a": 1.25, "ga_a": 1.55}
    try:
        goals = stats.get('goals', {}) if isinstance(stats, dict) else stats[0].get('goals', {})
        return {
            "gf_h": float(goals.get('for', {}).get('average', {}).get('home', 1.55)),
            "ga_h": float(goals.get('against', {}).get('average', {}).get('home', 1.25)),
            "gf_a": float(goals.get('for', {}).get('average', {}).get('away', 1.25)),
            "ga_a": float(goals.get('against', {}).get('average', {}).get('away', 1.55))
        }
    except: return {"gf_h": 1.55, "ga_h": 1.25, "gf_a": 1.25, "ga_a": 1.55}

@st.cache_data(ttl=60)
def get_real_odds(fixture_id):
    odds_data = fetch_api("odds", {"fixture": fixture_id, "bookmaker": 8})
    market_odds = {}
    if not odds_data or not odds_data[0].get('bookmakers'): return market_odds
    try:
        bets = odds_data[0]['bookmakers'][0].get('bets', [])
        for bet in bets:
            name = bet.get('name', '')
            vals = {str(v.get('value', '')): float(v.get('odd', 0.0)) for v in bet.get('values', [])}
            
            if name == 'Match Winner':
                if 'Home' in vals: market_odds["Home Win"] = vals['Home']
                if 'Draw' in vals: market_odds["Draw"] = vals['Draw']
                if 'Away' in vals: market_odds["Away Win"] = vals['Away']
            elif name == 'Double Chance':
                if 'Home/Draw' in vals: market_odds["Double Chance (1X)"] = vals['Home/Draw']
                if 'Draw/Away' in vals: market_odds["Double Chance (X2)"] = vals['Draw/Away']
                if 'Home/Away' in vals: market_odds["Double Chance (12)"] = vals['Home/Away']
            elif name == 'Draw No Bet':
                if 'Home' in vals: market_odds["Draw No Bet (Home)"] = vals['Home']
                if 'Away' in vals: market_odds["Draw No Bet (Away)"] = vals['Away']
            elif name == 'Goals Over/Under':
                if 'Over 1.5' in vals: market_odds["Over 1.5 Goals"] = vals['Over 1.5']
                if 'Under 1.5' in vals: market_odds["Under 1.5 Goals"] = vals['Under 1.5']
                if 'Over 2.5' in vals: market_odds["Over 2.5 Goals"] = vals['Over 2.5']
                if 'Under 2.5' in vals: market_odds["Under 2.5 Goals"] = vals['Under 2.5']
                if 'Over 3.5' in vals: market_odds["Over 3.5 Goals"] = vals['Over 3.5']
                if 'Under 3.5' in vals: market_odds["Under 3.5 Goals"] = vals['Under 3.5']
            elif name == 'Both Teams Score':
                if 'Yes' in vals: market_odds["BTTS (Yes)"] = vals['Yes']
                if 'No' in vals: market_odds["BTTS (No)"] = vals['No']
            elif name == 'Asian Handicap':
                for k, odd in vals.items():
                    if "-0.5" in k and "Home" in k: market_odds["Asian Handicap -0.5"] = odd
                    if "+0.5" in k and "Home" in k: market_odds["Asian Handicap +0.5"] = odd
                    if "-1.0" in k and "Home" in k: market_odds["Asian Handicap -1.0"] = odd
                    if "+1.0" in k and "Home" in k: market_odds["Asian Handicap +1.0"] = odd
                    if "-1.5" in k and "Home" in k: market_odds["Asian Handicap -1.5"] = odd
                    if "+1.5" in k and "Home" in k: market_odds["Asian Handicap +1.5"] = odd
    except: pass 
    return market_odds

def calculate_lambdas(h_stats, a_stats):
    hfa_multiplier = 1.10 
    lam_h = round(max(0.1, (h_stats['gf_h']/1.55 * hfa_multiplier) * (a_stats['ga_a']/1.55) * 1.55), 3)
    lam_a = round(max(0.1, (a_stats['gf_a']/1.25) * (h_stats['ga_h']/1.25) * 1.25), 3)
    return lam_h, lam_a

def run_monte_carlo_sim(lam_h, lam_a, sims=50000):
    np.random.seed(42) 
    h_goals, a_goals = np.random.poisson(lam_h, sims), np.random.poisson(lam_a, sims)
    
    for i in range(sims):
        if h_goals[i] == 1 and a_goals[i] == 0 and np.random.random() < 0.05: a_goals[i] = 1
        elif h_goals[i] == 0 and a_goals[i] == 1 and np.random.random() < 0.05: h_goals[i] = 1
            
    diff, total = h_goals - a_goals, h_goals + a_goals
    hw, dr, aw = np.sum(diff > 0)/sims, np.sum(diff == 0)/sims, np.sum(diff < 0)/sims
    
    dnb_h_prob = hw / (hw + aw) if (hw + aw) > 0 else 0
    dnb_a_prob = aw / (hw + aw) if (hw + aw) > 0 else 0
    
    ah_minus_1_prob = np.sum(diff > 1) / sims
    ah_minus_1_push = np.sum(diff == 1) / sims
    ah_minus_1_true = ah_minus_1_prob / (1 - ah_minus_1_push) if (1 - ah_minus_1_push) > 0 else 0

    ah_plus_1_prob = np.sum(diff > -1) / sims
    ah_plus_1_push = np.sum(diff == -1) / sims
    ah_plus_1_true = ah_plus_1_prob / (1 - ah_plus_1_push) if (1 - ah_plus_1_push) > 0 else 0
    
    return {
        "Home Win": hw, "Draw": dr, "Away Win": aw,
        "Double Chance (1X)": hw + dr, "Double Chance (X2)": aw + dr, "Double Chance (12)": hw + aw,
        "Draw No Bet (Home)": dnb_h_prob, "Draw No Bet (Away)": dnb_a_prob,
        "Asian Handicap -0.5": hw, "Asian Handicap +0.5": hw + dr,
        "Asian Handicap -1.0": ah_minus_1_true, "Asian Handicap +1.0": ah_plus_1_true,
        "Asian Handicap -1.5": np.sum(diff > 1)/sims, "Asian Handicap +1.5": np.sum(diff > -2)/sims,
        "Over 1.5 Goals": np.sum(total > 1.5)/sims, "Under 1.5 Goals": np.sum(total < 1.5)/sims,
        "Over 2.5 Goals": np.sum(total > 2.5)/sims, "Under 2.5 Goals": np.sum(total < 2.5)/sims,
        "Over 3.5 Goals": np.sum(total > 3.5)/sims, "Under 3.5 Goals": np.sum(total < 3.5)/sims,
        "BTTS (Yes)": np.sum((h_goals > 0) & (a_goals > 0))/sims, 
        "BTTS (No)": np.sum((h_goals == 0) | (a_goals == 0))/sims
    }

def calculate_dynamic_margin(odds):
    try:
        hw, dr, aw = odds.get("Home Win", 0), odds.get("Draw", 0), odds.get("Away Win", 0)
        if hw > 0 and dr > 0 and aw > 0:
            implied_sum = (1/hw) + (1/dr) + (1/aw)
            return max(0.01, implied_sum - 1)
    except: pass
    return 0.045

def calculate_kelly(prob, odd, fraction=0.25):
    b = odd - 1
    q = 1 - prob
    if b <= 0: return 0
    k = ((b * prob) - q) / b
    return max(0, k * fraction * 100)

def poisson_pmf(lam, k):
    return (lam**k * math.exp(-lam)) / math.factorial(k)

# ==========================================
# 3. INTERFACE (READABLE & VISUAL)
# ==========================================
st.markdown("""
<div class="top-nav">
<div class="logo">APEX <span style="color:#10B981;">QUANT</span></div>
<div class="sys-status"><span class="dot"></span> TIER-1 LIQUIDITY POOL CONNECTED</div>
</div>
""", unsafe_allow_html=True)

col_ctrl, col_exec = st.columns([1, 2.8], gap="large")

with col_ctrl:
    st.markdown("""<div class='grid-panel'><div class='panel-title'>Model Setup</div>""", unsafe_allow_html=True)
    
    target_date = st.date_input("Match Date", date.today())
    l_map = {"Premier League": 39, "Champions League": 2, "La Liga": 140, "Primeira Liga": 94, "Serie A": 135}
    league_name = st.selectbox("Select League", list(l_map.keys()))
    bankroll = st.number_input("Total Bankroll ($)", value=100000, step=10000, format="%d")
    
    fixtures = get_live_fixtures(target_date.strftime('%Y-%m-%d'), l_map[league_name])
    m_sel = None
    btn_run = False
    
    if fixtures:
        m_map = {f"{f['teams']['home']['name']} v {f['teams']['away']['name']}": f for f in fixtures}
        m_sel = m_map[st.selectbox("Select Fixture", list(m_map.keys()))]
        btn_run = st.button("EXECUTE QUANT MODEL")
    else:
        st.markdown("<div style='color:#EF4444; font-size:0.8rem; font-weight:600; text-align:center; padding: 10px; border: 1px solid #EF4444; border-radius: 4px; margin-top: 15px;'>NO FIXTURES DETECTED</div>", unsafe_allow_html=True)
        
    st.markdown("</div>", unsafe_allow_html=True)
    
    with st.expander("TERMINAL DOCUMENTATION", expanded=True):
        st.markdown("""
        <div class='manual-box'>
        <span class='manual-term'>Prime Alpha Signal</span>
        O sistema ignora anomalias com baixa taxa de acerto. A recomendação principal foca-se no mercado com maior <b>Kelly Criterion</b> (probabilidade de acerto > 35% cruzada com a Edge do mercado).
        <span class='manual-term'>Dynamic De-Vigging</span>
        Proprietary model extracts exact Overround (bookmaker margin) from the 1X2 primary market and adjusts fair probabilities dynamically.
        </div>
        """, unsafe_allow_html=True)

if m_sel and btn_run:
    with st.spinner('Compiling data & computing Risk-Adjusted Alpha...'):
        time.sleep(1) 
        
        h_id, a_id = m_sel['teams']['home']['id'], m_sel['teams']['away']['id']
        h_name = m_sel['teams']['home']['name']
        a_name = m_sel['teams']['away']['name']
        
        h_stats, a_stats = get_real_stats(h_id, l_map[league_name]), get_real_stats(a_id, l_map[league_name])
        lam_h, lam_a = calculate_lambdas(h_stats, a_stats)
        true_probs = run_monte_carlo_sim(lam_h, lam_a, 50000)
        live_odds = get_real_odds(m_sel['fixture']['id'])
        
        valid_markets = []
        best_bet = None
        dynamic_margin = calculate_dynamic_margin(live_odds)
        
        if live_odds:
            for mkt, odd in live_odds.items():
                prob = true_probs.get(mkt, 0)
                if odd > 1.05 and prob > 0:
                    f_prob = (1 / odd) / (1 + dynamic_margin)
                    edge = (prob * odd) - 1
                    kelly_val = calculate_kelly(prob, odd) if edge > 0 else 0
                    
                    valid_markets.append({
                        "Market": mkt, 
                        "BookOdd": odd, 
                        "ModelProb": prob, 
                        "Edge": edge, 
                        "TrueOdd": f_prob,
                        "Kelly": kelly_val
                    })
            
            # FILTRO DE OURO: Apenas apostas com Edge Positivo E pelo menos 35% de probabilidade
            prime_bets = [m for m in valid_markets if m['Edge'] > 0 and m['ModelProb'] >= 0.35]
            
            if prime_bets:
                # Escolher a melhor aposta com base na alocação de capital ideal (Maior Kelly)
                best_bet = max(prime_bets, key=lambda x: x['Kelly'])
        
        with col_exec:
            st.markdown(f"""
            <div class='metric-grid'>
                <div class='metric-card'>
                    <div class='metric-card-title'>{h_name} Expected Goals (xG)</div>
                    <div class='metric-card-val' style='color:#38BDF8;'>{lam_h:.2f}</div>
                </div>
                <div class='metric-card'>
                    <div class='metric-card-title'>{a_name} Expected Goals (xG)</div>
                    <div class='metric-card-val' style='color:#10B981;'>{lam_a:.2f}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            col_alpha, col_chart = st.columns([1.2, 1])
            
            with col_alpha:
                if best_bet:
                    dollar_sz = (best_bet['Kelly']/100) * bankroll
                    
                    st.markdown(f"""
    <div class='trade-signal'>
    <div class='panel-title' style='color:#10B981; border-color:rgba(16,185,129,0.2);'>PRIME ALPHA SIGNAL (Risk-Adjusted)</div>
    <div class='trade-asset'>{best_bet['Market']} @ {best_bet['BookOdd']:.3f}</div>
    <div class='data-row'><span class='data-lbl'>Win Probability (Strike Rate)</span><span class='data-val'>{best_bet['ModelProb']*100:.2f}%</span></div>
    <div class='data-row'><span class='data-lbl'>Expected Value (Edge)</span><span class='data-val hl-green'>+{best_bet['Edge']*100:.2f}%</span></div>
    <div class='data-row'><span class='data-lbl'>Optimal Stake (1/4 Kelly)</span><span class='data-val hl-blue'>${dollar_sz:,.0f} ({best_bet['Kelly']:.2f}%)</span></div>
    <div class='data-row' style='margin-top:12px; border-top: 1px dashed #1E293B; padding-top: 12px;'><span class='data-lbl'>Detected Market Margin</span><span class='data-val hl-warn'>{dynamic_margin*100:.2f}%</span></div>
    </div>
    """, unsafe_allow_html=True)
                elif live_odds:
                    st.markdown("""
    <div class='grid-panel'><div class='data-val hl-red' style='text-align: center; font-size: 1.2rem; padding: 20px;'>NO PRIME ALPHA DETECTED.<br><span style='font-size: 0.8rem; color: #94A3B8;'>Market is efficient or variance is too high. Protect Capital. Pass.</span></div></div>
    """, unsafe_allow_html=True)

            with col_chart:
                st.markdown("""<div class='grid-panel' style='padding-bottom: 5px;'><div class='panel-title'>Goal Expectancy Distribution (Poisson)</div>""", unsafe_allow_html=True)
                goals_range = list(range(6))
                h_probs_chart = [poisson_pmf(lam_h, g)*100 for g in goals_range]
                a_probs_chart = [poisson_pmf(lam_a, g)*100 for g in goals_range]

                fig_dist = go.Figure(data=[
                    go.Bar(name=h_name, x=goals_range, y=h_probs_chart, marker_color='#38BDF8', opacity=0.9, hovertemplate="<b>%{x} Goals</b><br>Probability: %{y:.1f}%<extra></extra>"),
                    go.Bar(name=a_name, x=goals_range, y=a_probs_chart, marker_color='#10B981', opacity=0.9, hovertemplate="<b>%{x} Goals</b><br>Probability: %{y:.1f}%<extra></extra>")
                ])
                fig_dist.update_layout(
                    barmode='group',
                    template='plotly_dark',
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    height=200,
                    margin=dict(l=0, r=0, t=10, b=0),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=10, color="#94A3B8")),
                    xaxis=dict(title="Goals", title_font=dict(size=10, color="#64748B"), tickfont=dict(size=10, color="#94A3B8"), gridcolor="rgba(30,41,59,0.5)", zeroline=False),
                    yaxis=dict(title="Probability (%)", title_font=dict(size=10, color="#64748B"), tickfont=dict(size=10, color="#94A3B8"), gridcolor="rgba(30,41,59,0.5)", zeroline=False)
                )
                st.plotly_chart(fig_dist, use_container_width=True, config={'displayModeBar': False})
                st.markdown("</div>", unsafe_allow_html=True)

            if live_odds and valid_markets:
                st.markdown("""<div class='grid-panel' style='padding-bottom: 5px;'><div class='panel-title'>Probability Delta (Model vs Bookmaker) - Top 5 Markets</div>""", unsafe_allow_html=True)
                
                # Para o gráfico continuo a usar o Edge puro para visualizar as maiores disparidades
                top_markets = sorted([m for m in valid_markets if m['Edge'] > 0], key=lambda x: x['Edge'], reverse=True)[:5]
                
                if top_markets:
                    m_names = [m['Market'] for m in top_markets]
                    sys_probs = [m['ModelProb']*100 for m in top_markets]
                    book_probs = [m['TrueOdd']*100 for m in top_markets]
                    
                    fig_delta = go.Figure()
                    fig_delta.add_trace(go.Bar(
                        y=m_names, x=book_probs, name='Bookie (No-Vig)', orientation='h', marker_color='#334155', hovertemplate="Bookie: %{x:.1f}%<extra></extra>"
                    ))
                    fig_delta.add_trace(go.Bar(
                        y=m_names, x=sys_probs, name='System Prob', orientation='h', marker_color='#10B981', hovertemplate="System: %{x:.1f}%<extra></extra>"
                    ))
                    
                    fig_delta.update_layout(
                        barmode='group',
                        template='plotly_dark',
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        height=220,
                        margin=dict(l=0, r=0, t=10, b=0),
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=10, color="#94A3B8")),
                        xaxis=dict(title="Probability (%)", title_font=dict(size=10, color="#64748B"), tickfont=dict(size=10, color="#94A3B8"), gridcolor="rgba(30,41,59,0.5)", zeroline=False),
                        yaxis=dict(autorange="reversed", tickfont=dict(size=11, color="#E2E8F0"), gridcolor="rgba(0,0,0,0)")
                    )
                    st.plotly_chart(fig_delta, use_container_width=True, config={'displayModeBar': False})
                else:
                    st.info("No +EV markets to chart.")
                st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("""<div class='grid-panel'><div class='panel-title'>Algorithmic Order Book (Sorted by Kelly Criterion)</div>""", unsafe_allow_html=True)
            
            if live_odds:
                # Ordena a tabela toda pelo Kelly para refletir a nova prioridade do algoritmo
                valid_markets = sorted(valid_markets, key=lambda x: x['Kelly'], reverse=True)
                
                table_html = "<table class='ob-table'><tr><th>Market</th><th>Book Odds</th><th>Model Prob</th><th>Edge (+EV)</th><th>Kelly Rec.</th></tr>"
                
                for m in valid_markets:
                    edge_val = m['Edge'] * 100
                    color_cls = "hl-green" if edge_val > 0 else "hl-red"
                    sign = "+" if edge_val > 0 else ""
                    
                    row = f"<tr><td>{m['Market']}</td><td>{m['BookOdd']:.3f}</td>"
                    row += f"<td>{m['ModelProb']*100:.1f}%</td>"
                    row += f"<td class='{color_cls}'>{sign}{edge_val:.2f}%</td>"
                    row += f"<td style='color:#38BDF8;'>{m['Kelly']:.2f}%</td></tr>"
                    
                    table_html += row
                    
                table_html += "</table>"
                
                st.markdown(table_html, unsafe_allow_html=True)
            else:
                st.markdown("""<div class='data-lbl'>Waiting for market liquidity...</div>""", unsafe_allow_html=True)
                
            st.markdown("""</div>""", unsafe_allow_html=True)
