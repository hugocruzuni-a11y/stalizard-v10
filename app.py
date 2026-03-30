import streamlit as st
import numpy as np
import pandas as pd
import requests
from datetime import date
import time

# ==========================================
# 1. INSTITUTIONAL TERMINAL SETUP
# ==========================================
st.set_page_config(page_title="APEX QUANT | ALPHA TERMINAL", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;700;800&display=swap');
    
    .stApp { background-color: #050608; color: #E2E8F0; font-family: 'JetBrains Mono', monospace; }
    header, footer { visibility: hidden; }
    
    /* Top Navigation */
    .top-nav { background: #0B0F19; border-bottom: 1px solid #1E293B; padding: 12px 30px; display: flex; justify-content: space-between; align-items: center; margin: -3rem -3rem 2rem -3rem; position: sticky; top: 0; z-index: 1000;}
    .logo { font-size: 1.4rem; font-weight: 800; letter-spacing: 1px; color: #F8FAFC; }
    .logo span { color: #10B981; }
    
    .sys-status { color: #64748B; font-size: 0.75rem; font-weight: 700; letter-spacing: 1px; text-transform: uppercase; }
    .status-dot { display: inline-block; width: 6px; height: 6px; background-color: #10B981; border-radius: 50%; margin-right: 8px; box-shadow: 0 0 5px #10B981; }

    /* Market Data Grid */
    .data-matrix { border: 1px solid #1E293B; background: #0B0F19; padding: 25px; border-radius: 4px; }
    .team-name { font-size: 1.6rem; color: #F8FAFC; font-weight: 800; line-height: 1.2; }
    .vs-text { color: #64748B; font-size: 0.9rem; margin: 5px 0 15px 0; }
    
    .metric-row { display: flex; justify-content: space-between; border-bottom: 1px solid #1E293B; padding: 10px 0; font-size: 0.85rem; }
    .metric-label { color: #94A3B8; font-weight: 700;}
    .metric-value { color: #38BDF8; font-weight: 800; }
    
    /* Order Book Table */
    .ob-header { display: grid; grid-template-columns: 2fr 1fr 1fr 1fr 1fr; border-bottom: 2px solid #334155; padding-bottom: 8px; margin-bottom: 8px; font-size: 0.7rem; color: #94A3B8; font-weight: 800; text-transform: uppercase; }
    .ob-row { display: grid; grid-template-columns: 2fr 1fr 1fr 1fr 1fr; border-bottom: 1px solid #1E293B; padding: 10px 0; font-size: 0.85rem; }
    .ob-row:hover { background: #0F172A; }
    
    /* High Conviction Box */
    .alpha-box { border: 1px solid #10B981; background: rgba(16, 185, 129, 0.05); padding: 20px; margin: 20px 0; border-radius: 4px; }
    .alpha-title { font-size: 0.7rem; color: #10B981; font-weight: 800; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 15px; }
    
    /* Buttons */
    .stButton > button { background: #1E293B !important; color: #F8FAFC !important; border: 1px solid #334155 !important; border-radius: 4px !important; font-family: 'JetBrains Mono' !important; font-weight: 700 !important; text-transform: uppercase; transition: all 0.2s; }
    .stButton > button:hover { background: #10B981 !important; color: #000 !important; border-color: #10B981 !important; }
    
    .pos-edge { color: #10B981; font-weight: 800; }
    .neg-edge { color: #EF4444; font-weight: 400; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. DATA ENGINE & ADVANCED MATH
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
                market_odds["Over 1.5"], market_odds["Under 1.5"] = vals.get('Over 1.5', 0), vals.get('Under 1.5', 0)
                market_odds["Over 2.5"], market_odds["Under 2.5"] = vals.get('Over 2.5', 0), vals.get('Under 2.5', 0)
                market_odds["Over 3.5"], market_odds["Under 3.5"] = vals.get('Over 3.5', 0), vals.get('Under 3.5', 0)
            elif name == 'Both Teams Score':
                market_odds["BTTS - Yes"], market_odds["BTTS - No"] = vals.get('Yes', 0), vals.get('No', 0)
            elif name == 'Asian Handicap':
                for k, odd in vals.items():
                    if "Home -0.5" in k: market_odds["AH -0.5 (H)"] = odd
                    if "Home +0.5" in k: market_odds["AH +0.5 (H)"] = odd
                    if "Home -1.5" in k: market_odds["AH -1.5 (H)"] = odd
                    if "Home +1.5" in k: market_odds["AH +1.5 (H)"] = odd
    return market_odds

def calculate_projected_goals(h_stats, a_stats):
    h_attack, a_defense = h_stats['gf_h'] / 1.55, a_stats['ga_a'] / 1.55
    a_attack, h_defense = a_stats['gf_a'] / 1.25, h_stats['ga_h'] / 1.25
    return round(max(0.1, h_attack * a_defense * 1.55), 2), round(max(0.1, a_attack * h_defense * 1.25), 2)

def run_monte_carlo_sim(proj_h, proj_a, sims=25000):
    np.random.seed(int(time.time()))
    h_goals, a_goals = np.random.poisson(proj_h, sims), np.random.poisson(proj_a, sims)
    
    # Dixon-Coles Adjustment for Draws
    for i in range(sims):
        if h_goals[i] == 1 and a_goals[i] == 0 and np.random.random() < 0.06: a_goals[i] = 1
        elif h_goals[i] == 0 and a_goals[i] == 1 and np.random.random() < 0.06: h_goals[i] = 1
            
    diff, total = h_goals - a_goals, h_goals + a_goals
    hw, dr, aw = np.sum(diff > 0)/sims, np.sum(diff == 0)/sims, np.sum(diff < 0)/sims
    
    return {
        "Home Win": hw, "Draw": dr, "Away Win": aw,
        "AH -0.5 (H)": hw, "AH +0.5 (H)": hw + dr,
        "AH -1.5 (H)": np.sum(diff > 1)/sims, "AH +1.5 (H)": np.sum(diff > -2)/sims,
        "Over 1.5": np.sum(total > 1.5)/sims, "Under 1.5": np.sum(total < 1.5)/sims,
        "Over 2.5": np.sum(total > 2.5)/sims, "Under 2.5": np.sum(total < 2.5)/sims,
        "Over 3.5": np.sum(total > 3.5)/sims, "Under 3.5": np.sum(total < 3.5)/sims,
        "BTTS - Yes": np.sum((h_goals > 0) & (a_goals > 0))/sims, "BTTS - No": np.sum((h_goals == 0) | (a_goals == 0))/sims
    }

def calculate_kelly(prob, odd, fraction=0.25):
    b = odd - 1
    q = 1 - prob
    kelly_pct = ((b * prob) - q) / b
    return max(0, kelly_pct) * fraction * 100

def get_market_vig():
    # Margem padrão de casas institucionais (Pinnacle/Exchanges)
    return 0.045 

# ==========================================
# 3. TERMINAL UI
# ==========================================
st.markdown("""
<div class="top-nav">
    <div class="logo">APEX<span>QUANT</span></div>
    <div class="sys-status"><span class="status-dot"></span>MARKET DATA: CONNECTED</div>
</div>
""", unsafe_allow_html=True)

col_cmd, col_data, col_book = st.columns([1, 1.6, 2.4], gap="large")

with col_cmd:
    st.markdown("<div style='color:#64748B; font-size:0.75rem; font-weight:700; margin-bottom:10px;'>MARKET PARAMETERS</div>", unsafe_allow_html=True)
    target_date = st.date_input("Date", date.today())
    l_map = {"Premier League": 39, "Champions League": 2, "La Liga": 140, "Primeira Liga": 94, "Serie A": 135}
    league_name = st.selectbox("League", list(l_map.keys()))
    
    with st.spinner("Fetching liquidity..."):
        fixtures = get_live_fixtures(target_date.strftime('%Y-%m-%d'), l_map[league_name])
    
    m_sel = None
    if fixtures:
        m_map = {f"{f['teams']['home']['name']} v {f['teams']['away']['name']}": f for f in fixtures}
        m_sel = m_map[st.selectbox("Fixture", list(m_map.keys()))]
        st.button("RUN QUANT MODEL", use_container_width=True)

if m_sel:
    h_id, a_id = m_sel['teams']['home']['id'], m_sel['teams']['away']['id']
    with st.spinner("Computing Monte Carlo parameters..."):
        h_stats, a_stats = get_real_stats(h_id, l_map[league_name]), get_real_stats(a_id, l_map[league_name])
        proj_h, proj_a = calculate_projected_goals(h_stats, a_stats)
        true_probs = run_monte_carlo_sim(proj_h, proj_a, 25000)
        live_odds = get_real_odds(m_sel['fixture']['id'])
    
    valid_markets = []
    best_bet, max_edge = None, 0
    market_margin = get_market_vig()
    
    if live_odds:
        for mkt, odd in live_odds.items():
            prob = true_probs.get(mkt, 0)
            if odd > 1.05 and prob > 0:
                market_implied = 1 / odd
                market_fair_prob = market_implied / (1 + market_margin)
                
                edge = (prob * odd) - 1
                valid_markets.append({
                    "Market": mkt, "Odd": odd, "TrueProb": prob, "Edge": edge, 
                    "MarketFairProb": market_fair_prob
                })
                if edge > max_edge:
                    max_edge, best_bet = edge, valid_markets[-1]
    
    with col_data:
        # NENHUM ESPAÇO ANTES DO HTML PARA EVITAR ERROS DO STREAMLIT
        st.markdown(f"""
<div class="data-matrix">
    <div class="team-name">{m_sel['teams']['home']['name']}</div>
    <div class="vs-text">vs</div>
    <div class="team-name" style="margin-bottom: 25px;">{m_sel['teams']['away']['name']}</div>
    
    <div class="metric-row"><span class="metric-label">Model xG (Home)</span><span class="metric-value">{proj_h:.2f}</span></div>
    <div class="metric-row"><span class="metric-label">Model xG (Away)</span><span class="metric-value">{proj_a:.2f}</span></div>
    <div class="metric-row"><span class="metric-label">Simulations</span><span class="metric-value" style="color:#F8FAFC;">25,000</span></div>
    <div class="metric-row"><span class="metric-label">Est. Book Margin</span><span class="metric-value" style="color:#F8FAFC;">{(market_margin*100):.1f}%</span></div>
</div>
""", unsafe_allow_html=True)

        if best_bet and best_bet["Edge"] > 0:
            rec_kelly = calculate_kelly(best_bet['TrueProb'], best_bet['Odd'])
            st.markdown(f"""
<div class="alpha-box">
    <div class="alpha-title">High Conviction Play</div>
    <div style="font-size: 2rem; font-weight: 800; color: #F8FAFC; margin-bottom: 15px;">{best_bet['Market']}</div>
    <div style="display: flex; justify-content: space-between; text-align: left;">
        <div>
            <div style="color: #64748B; font-size: 0.75rem; font-weight: 700;">LINE</div>
            <div style="color: #F8FAFC; font-size: 1.2rem; font-weight: 800;">{best_bet['Odd']:.2f}</div>
        </div>
        <div>
            <div style="color: #64748B; font-size: 0.75rem; font-weight: 700;">TRUE ODDS</div>
            <div style="color: #38BDF8; font-size: 1.2rem; font-weight: 800;">{(1/best_bet['TrueProb']):.2f}</div>
        </div>
        <div>
            <div style="color: #64748B; font-size: 0.75rem; font-weight: 700;">+EV</div>
            <div style="color: #10B981; font-size: 1.2rem; font-weight: 800;">+{best_bet['Edge']*100:.1f}%</div>
        </div>
        <div>
            <div style="color: #64748B; font-size: 0.75rem; font-weight: 700;">KELLY (1/4)</div>
            <div style="color: #F8FAFC; font-size: 1.2rem; font-weight: 800;">{rec_kelly:.2f}%</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

    with col_book:
        st.markdown("<div style='color:#64748B; font-size:0.75rem; font-weight:700; margin-bottom:10px;'>FULL ORDER BOOK</div>", unsafe_allow_html=True)
        if live_odds:
            st.markdown("""
            <div class="ob-header">
                <div>MARKET</div>
                <div style="text-align:right;">ODDS</div>
                <div style="text-align:right;">NO-VIG</div>
                <div style="text-align:right;">MODEL</div>
                <div style="text-align:right;">EDGE</div>
            </div>
            <div style="max-height: 550px; overflow-y: auto; padding-right: 5px;">
            """, unsafe_allow_html=True)
            
            valid_markets = sorted(valid_markets, key=lambda x: x['Edge'], reverse=True)
            for m in valid_markets:
                is_edge = m['Edge'] > 0
                txt_class = "pos-edge" if is_edge else "neg-edge"
                edge_txt = f"+{m['Edge']*100:.1f}%" if is_edge else f"{m['Edge']*100:.1f}%"
                
                st.markdown(f"""
                <div class="ob-row">
                    <div style="color:#F8FAFC; font-weight:700;">{m['Market']}</div>
                    <div style="text-align:right; color:#F8FAFC;">{m['Odd']:.2f}</div>
                    <div style="text-align:right; color:#64748B;">{m['MarketFairProb']*100:.1f}%</div>
                    <div style="text-align:right; color:#38BDF8;">{m['TrueProb']*100:.1f}%</div>
                    <div style="text-align:right;" class="{txt_class}">{edge_txt}</div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("Awaiting market liquidity for this fixture.")
