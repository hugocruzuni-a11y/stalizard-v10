import streamlit as st
import numpy as np
import pandas as pd
import requests
import plotly.graph_objects as go
from datetime import date
import time

# ==========================================
# 1. HIGH-PERFORMANCE SETUP & STYLING
# ==========================================
st.set_page_config(page_title="APEX QUANT | ALPHA TERMINAL", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800;900&family=JetBrains+Mono:wght@400;700;800&display=swap');
    
    .stApp { background-color: #030407; color: #FFFFFF; font-family: 'Outfit', sans-serif; background-image: radial-gradient(circle at 50% 0%, #0A1128 0%, #030407 80%); }
    header, footer { visibility: hidden; }
    
    .top-nav { background: rgba(3, 4, 7, 0.8); backdrop-filter: blur(20px); border-bottom: 1px solid rgba(0, 240, 255, 0.15); padding: 15px 40px; display: flex; justify-content: space-between; align-items: center; margin: -3rem -3rem 2rem -3rem; position: sticky; top: 0; z-index: 1000; box-shadow: 0 10px 30px rgba(0,0,0,0.5);}
    .logo { font-size: 2.2rem; font-weight: 900; letter-spacing: -1px; color: #FFFFFF; line-height: 1;}
    .logo span { color: #00F0FF; text-shadow: 0 0 15px rgba(0, 240, 255, 0.4); }
    
    .live-status { display: flex; align-items: center; gap: 10px; background: rgba(255, 0, 85, 0.1); border: 1px solid rgba(255, 0, 85, 0.3); padding: 8px 16px; border-radius: 50px; font-size: 0.8rem; font-weight: 800; text-transform: uppercase; color: #FF0055; letter-spacing: 1px;}
    .dot { width: 8px; height: 8px; background-color: #FF0055; border-radius: 50%; animation: pulse-red 1.5s infinite; }
    @keyframes pulse-red { 0% { transform: scale(0.95); opacity: 1; } 50% { transform: scale(1.2); opacity: 0.5; } 100% { transform: scale(0.95); opacity: 1; } }

    .lock-card { background: linear-gradient(180deg, #0A101D 0%, #05080F 100%); border: 1px solid rgba(0, 240, 255, 0.2); border-radius: 20px; padding: 30px; box-shadow: inset 0 0 40px rgba(0,0,0,0.8), 0 20px 50px rgba(0,0,0,0.5); position: relative; overflow: hidden; margin-bottom: 20px;}
    .lock-card::before { content: ''; position: absolute; top: 0; left: 0; width: 100%; height: 4px; background: linear-gradient(90deg, #00F0FF, #00FF88); }
    
    .matchup { text-align: center; margin-bottom: 25px; }
    .league-tag { font-size: 0.8rem; color: #00F0FF; text-transform: uppercase; letter-spacing: 3px; font-weight: 800; margin-bottom: 5px; }
    .teams { font-size: 2.2rem; font-weight: 900; line-height: 1.2; letter-spacing: -1px; }
    .teams span { color: #64748B; font-weight: 400; font-size: 1.5rem; margin: 0 15px; }

    .order-row { display: grid; grid-template-columns: 2fr 1fr 1fr 1.5fr; align-items: center; background: #080C16; border: 1px solid #1E293B; border-radius: 6px; margin-bottom: 6px; transition: all 0.2s; }
    .order-row:hover { border-color: #00F0FF; background: rgba(0, 240, 255, 0.05); }
    .order-cell { padding: 10px 15px; font-family: 'JetBrains Mono'; font-size: 0.9rem; }
    .market-name { color: #F8FAFC; font-weight: 800; font-family: 'Inter'; font-size: 0.80rem; text-transform: uppercase; }
    
    .metric-box { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.1); border-radius: 10px; padding: 15px; text-align: center; }
    .metric-title { font-size: 0.75rem; color: #64748B; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 5px; font-weight: 800;}
    .metric-value { font-size: 1.5rem; font-family: 'JetBrains Mono'; font-weight: 900; color: #FFF; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. DATA ENGINE (LIVE API) & MATH ALGORITHMS
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
    if odds_data and odds_data[0].get('bookmakers'):
        for bet in odds_data[0]['bookmakers'][0].get('bets', []):
            name = bet['name']
            vals = {str(v['value']): float(v['odd']) for v in bet['values']}
            if name == 'Match Winner':
                market_odds["Home Win"], market_odds["Draw"], market_odds["Away Win"] = vals.get('Home', 0), vals.get('Draw', 0), vals.get('Away', 0)
            elif name == 'Goals Over/Under':
                market_odds["Over 2.5"], market_odds["Under 2.5"] = vals.get('Over 2.5', 0), vals.get('Under 2.5', 0)
                market_odds["Over 3.5"], market_odds["Under 3.5"] = vals.get('Over 3.5', 0), vals.get('Under 3.5', 0)
            elif name == 'Both Teams Score':
                market_odds["BTTS - Yes"], market_odds["BTTS - No"] = vals.get('Yes', 0), vals.get('No', 0)
            elif name == 'Asian Handicap':
                for k, odd in vals.items():
                    if "Home -0.5" in k: market_odds["AH -0.5 (H)"] = odd
                    if "Home +0.5" in k: market_odds["AH +0.5 (H)"] = odd
    return market_odds

def calculate_projected_goals(h_stats, a_stats):
    h_attack, a_defense = h_stats['gf_h'] / 1.55, a_stats['ga_a'] / 1.55
    a_attack, h_defense = a_stats['gf_a'] / 1.25, h_stats['ga_h'] / 1.25
    return round(max(0.1, h_attack * a_defense * 1.55), 2), round(max(0.1, a_attack * h_defense * 1.25), 2)

def run_monte_carlo_sim(proj_h, proj_a, sims=20000):
    np.random.seed(int(time.time()))
    h_goals, a_goals = np.random.poisson(proj_h, sims), np.random.poisson(proj_a, sims)
    for i in range(sims):
        if h_goals[i] == 1 and a_goals[i] == 0 and np.random.random() < 0.06: a_goals[i] = 1
        elif h_goals[i] == 0 and a_goals[i] == 1 and np.random.random() < 0.06: h_goals[i] = 1
    diff, total = h_goals - a_goals, h_goals + a_goals
    hw, dr, aw = np.sum(diff > 0)/sims, np.sum(diff == 0)/sims, np.sum(diff < 0)/sims
    return {
        "Home Win": hw, "Draw": dr, "Away Win": aw,
        "AH -0.5 (H)": hw, "AH +0.5 (H)": hw + dr,
        "Over 2.5": np.sum(total > 2.5)/sims, "Under 2.5": np.sum(total < 2.5)/sims,
        "Over 3.5": np.sum(total > 3.5)/sims, "Under 3.5": np.sum(total < 3.5)/sims,
        "BTTS - Yes": np.sum((h_goals > 0) & (a_goals > 0))/sims, "BTTS - No": np.sum((h_goals == 0) | (a_goals == 0))/sims
    }

def calculate_kelly(prob, odd, fraction=0.25):
    """Calcula a percentagem da banca a apostar usando 1/4 Kelly Criterion."""
    b = odd - 1
    q = 1 - prob
    kelly_pct = ((b * prob) - q) / b
    return max(0, kelly_pct) * fraction * 100

# ==========================================
# 3. PRO TERMINAL UI & PLOTLY VISUALIZATIONS
# ==========================================
st.markdown("""
<div class="top-nav">
    <div class="logo">APEX<span>QUANT</span></div>
    <div class="live-status"><div class="dot"></div> ALGORITHMIC TRADING TERMINAL</div>
</div>
""", unsafe_allow_html=True)

col_menu, col_core, col_book = st.columns([1, 1.8, 2.2], gap="large")

with col_menu:
    st.markdown("<h3 style='color:#00F0FF; font-weight:900; font-size:1.1rem; text-transform:uppercase; letter-spacing:2px; margin-bottom:20px;'>Market Screener</h3>", unsafe_allow_html=True)
    target_date = st.date_input("Match Date", date.today())
    l_map = {"🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League": 39, "🇪🇺 Champions League": 2, "🇪🇸 La Liga": 140, "🇵🇹 Primeira Liga": 94, "🇮🇹 Serie A": 135, "🇩🇪 Bundesliga": 78}
    league_name = st.selectbox("Competition", list(l_map.keys()))
    
    with st.spinner("Connecting to institutional latency feeds..."):
        fixtures = get_live_fixtures(target_date.strftime('%Y-%m-%d'), l_map[league_name])
    
    m_sel = None
    if fixtures:
        m_map = {f"{f['teams']['home']['name']} vs {f['teams']['away']['name']}": f for f in fixtures}
        m_sel = m_map[st.selectbox("Select Target Match", list(m_map.keys()))]
        st.button("🔄 RUN QUANT ALGO", use_container_width=True)
    else: st.error("No liquid fixtures found.")

if m_sel:
    h_id, a_id = m_sel['teams']['home']['id'], m_sel['teams']['away']['id']
    with st.spinner("Computing 20k Bivariate Poisson paths..."):
        h_stats, a_stats = get_real_stats(h_id, l_map[league_name]), get_real_stats(a_id, l_map[league_name])
        proj_h, proj_a = calculate_projected_goals(h_stats, a_stats)
        true_probs = run_monte_carlo_sim(proj_h, proj_a)
        live_odds = get_real_odds(m_sel['fixture']['id'])
    
    best_bet, max_edge, valid_markets = None, 0, []
    if live_odds:
        for mkt, odd in live_odds.items():
            prob = true_probs.get(mkt, 0)
            if odd > 1.05 and prob > 0:
                edge = (prob * odd) - 1
                valid_markets.append({"Market": mkt, "Odd": odd, "TrueProb": prob, "Edge": edge})
                if edge > max_edge:
                    max_edge, best_bet = edge, {"Market": mkt, "Odd": odd, "TrueProb": prob, "Edge": edge}
    
    with col_core:
        st.markdown(f"""
        <div class="lock-card">
            <div class="matchup">
                <div class="league-tag">{league_name} • QUOTES</div>
                <div class="teams">{m_sel['teams']['home']['name']} <span>vs</span> {m_sel['teams']['away']['name']}</div>
            </div>
            <div style="display:flex; justify-content: space-around; margin-top: 10px;">
                <div class="metric-box"><div class="metric-title">xG PROXY (HOME)</div><div class="metric-value" style="color:#00F0FF;">{proj_h:.2f}</div></div>
                <div class="metric-box"><div class="metric-title">xG PROXY (AWAY)</div><div class="metric-value" style="color:#D4AF37;">{proj_a:.2f}</div></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if best_bet and best_bet["Edge"] > 0:
            rec_kelly = calculate_kelly(best_bet['TrueProb'], best_bet['Odd'])
            st.markdown(f"""
                <div style="background: rgba(0, 255, 136, 0.05); border: 2px dashed #00FF88; border-radius: 12px; padding: 20px; text-align: center; margin: 20px 0; box-shadow: 0 0 30px rgba(0,255,136,0.1);">
                    <div style="color: #00FF88; font-size: 0.8rem; font-weight: 800; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 10px;">⚡ INSTITUTIONAL ALPHA IDENTIFIED ⚡</div>
                    <div style="font-size: 2.2rem; font-weight: 900; color: #FFFFFF; text-shadow: 0 0 20px rgba(0,255,136,0.4);">{best_bet['Market']}</div>
                    <div style="display:flex; justify-content:center; gap:20px; margin-top:15px; font-family:'JetBrains Mono';">
                        <div style="background: rgba(255,255,255,0.1); padding: 5px 15px; border-radius: 6px;">ODD: <span style="color:#FFD700; font-weight:800;">{best_bet['Odd']:.2f}</span></div>
                        <div style="background: rgba(0,255,136,0.1); padding: 5px 15px; border-radius: 6px; color:#00FF88; font-weight:800;">EDGE: +{best_bet['Edge']*100:.1f}%</div>
                        <div style="background: rgba(255,0,85,0.1); padding: 5px 15px; border-radius: 6px; color:#FF0055; font-weight:800;">SIZE (1/4 KELLY): {rec_kelly:.2f}%</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # --- VISUAL DATA EXPORT (THE PLOTLY CHART) ---
            st.markdown("<h4 style='color:#64748B; font-size: 0.9rem; text-transform:uppercase; text-align:center; font-weight:800; letter-spacing:1px; margin-top:20px;'>Probability Delta Analysis</h4>", unsafe_allow_html=True)
            
            # Prepare data for top 3 positive EV markets to keep the chart clean
            pos_markets = sorted([m for m in valid_markets if m['Edge'] > 0], key=lambda x: x['Edge'], reverse=True)[:3]
            if pos_markets:
                m_names = [m['Market'] for m in pos_markets]
                implied_probs = [(1/m['Odd'])*100 for m in pos_markets]
                true_probs_pct = [m['TrueProb']*100 for m in pos_markets]

                fig = go.Figure(data=[
                    go.Bar(name='Bookmaker (Implied)', y=m_names, x=implied_probs, orientation='h', marker_color='#1E293B', width=0.3),
                    go.Bar(name='Model (True Prob)', y=m_names, x=true_probs_pct, orientation='h', marker_color='#00F0FF', width=0.3)
                ])
                fig.update_layout(
                    barmode='group',
                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(family="Outfit", color="#FFFFFF", size=12),
                    margin=dict(l=0, r=0, t=30, b=0),
                    xaxis=dict(title='Probability (%)', showgrid=True, gridcolor='rgba(255,255,255,0.1)', range=[0, max(max(true_probs_pct), max(implied_probs)) + 10]),
                    yaxis=dict(autorange="reversed"),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

        elif not live_odds: st.warning("⚠️ Pending Bookmaker Liquidity.")
        else: st.error("📉 EFFICIENT MARKET. Pass.")

    with col_book:
        st.markdown("<h3 style='color:#FFFFFF; font-weight:900; font-size:1.1rem; text-transform:uppercase; letter-spacing:2px; margin-bottom:20px;'>Live Order Book</h3>", unsafe_allow_html=True)
        if live_odds:
            st.markdown("""
            <div style="display: grid; grid-template-columns: 2fr 1fr 1fr 1.5fr; font-size: 0.65rem; color: #64748B; text-transform: uppercase; letter-spacing: 1px; font-weight: 800; padding: 0 15px 10px 15px; border-bottom: 1px solid #1E293B; margin-bottom: 10px;">
                <div>Market</div><div style="text-align:right;">Line</div><div style="text-align:right;">Fair</div><div style="text-align:center;">Alpha (EV)</div>
            </div>
            <div style="max-height: 600px; overflow-y: auto; padding-right: 5px;">
            """, unsafe_allow_html=True)
            
            valid_markets = sorted(valid_markets, key=lambda x: x['Edge'], reverse=True)
            for m in valid_markets:
                is_edge = m['Edge'] > 0
                c_edge, bg, border = ("#00FF88", "rgba(0, 255, 136, 0.05)", "border-left: 3px solid #00FF88;") if is_edge else ("#EF4444", "transparent", "border-left: 3px solid transparent;")
                
                st.markdown(f"""
                <div class="order-row" style="{border} background:{bg};">
                    <div class="order-cell market-name">{m['Market']}</div>
                    <div class="order-cell" style="text-align:right; font-weight:800; color:#FFF;">{m['Odd']:.2f}</div>
                    <div class="order-cell" style="text-align:right; color:#00F0FF;">{(1/m['TrueProb']):.2f}</div>
                    <div class="order-cell" style="text-align:center; color:{c_edge}; font-weight:800;">{m['Edge']*100:+.1f}%</div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
