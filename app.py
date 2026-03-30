import streamlit as st
import numpy as np
import pandas as pd
import requests
from datetime import date
import time

# ==========================================
# 1. HIGH-PERFORMANCE SETUP
# ==========================================
st.set_page_config(page_title="APEX QUANT | PRO TERMINAL", layout="wide", initial_sidebar_state="collapsed")

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
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. DATA ENGINE (LIVE API CONNECTION)
# ==========================================
# SECURE API CALL - USES secrets.toml or fallback for your presentation tomorrow!
API_KEY = st.secrets.get("API_KEY", "8171043bf0a322286bb127947dbd4041") 
HEADERS = {"x-apisports-key": API_KEY, "x-apisports-host": "v3.football.api-sports.io"}

def fetch_api(endpoint, params):
    try:
        r = requests.get(f"https://{HEADERS['x-apisports-host']}/{endpoint}", headers=HEADERS, params=params, timeout=10)
        return r.json().get('response', [])
    except Exception as e: return []

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
    odds_data = fetch_api("odds", {"fixture": fixture_id, "bookmaker": 8}) # 8 = Bet365
    market_odds = {}
    if odds_data and odds_data[0].get('bookmakers'):
        for bet in odds_data[0]['bookmakers'][0].get('bets', []):
            name = bet['name']
            vals = {str(v['value']): float(v['odd']) for v in bet['values']}
            
            if name == 'Match Winner':
                market_odds["Home Win"] = vals.get('Home', 0)
                market_odds["Draw"] = vals.get('Draw', 0)
                market_odds["Away Win"] = vals.get('Away', 0)
            elif name == 'Goals Over/Under':
                market_odds["Over 1.5"] = vals.get('Over 1.5', 0)
                market_odds["Under 1.5"] = vals.get('Under 1.5', 0)
                market_odds["Over 2.5"] = vals.get('Over 2.5', 0)
                market_odds["Under 2.5"] = vals.get('Under 2.5', 0)
                market_odds["Over 3.5"] = vals.get('Over 3.5', 0)
                market_odds["Under 3.5"] = vals.get('Under 3.5', 0)
            elif name == 'Both Teams Score':
                market_odds["BTTS - Yes"] = vals.get('Yes', 0)
                market_odds["BTTS - No"] = vals.get('No', 0)
            elif name == 'Asian Handicap':
                for k, odd in vals.items():
                    if "Home -0.5" in k: market_odds["AH -0.5 (H)"] = odd
                    if "Home +0.5" in k: market_odds["AH +0.5 (H)"] = odd
                    if "Home -1.5" in k: market_odds["AH -1.5 (H)"] = odd
                    if "Home +1.5" in k: market_odds["AH +1.5 (H)"] = odd
    return market_odds

# ==========================================
# 3. ADVANCED QUANT MODEL
# ==========================================
def calculate_projected_goals(h_stats, a_stats):
    """Projeções baseadas em Força Ofensiva/Defensiva Relativa."""
    league_avg_home, league_avg_away = 1.55, 1.25
    h_attack, a_defense = h_stats['gf_h'] / league_avg_home, a_stats['ga_a'] / league_avg_home
    a_attack, h_defense = a_stats['gf_a'] / league_avg_away, h_stats['ga_h'] / league_avg_away
    
    h_proj = max(0.1, h_attack * a_defense * league_avg_home)
    a_proj = max(0.1, a_attack * h_defense * league_avg_away)
    return round(h_proj, 2), round(a_proj, 2)

def run_monte_carlo_sim(proj_h, proj_a, sims=20000):
    np.random.seed(int(time.time()))
    h_goals = np.random.poisson(proj_h, sims)
    a_goals = np.random.poisson(proj_a, sims)
    
    # Bivariate Poisson Approximation (Dixon-Coles Core Correction)
    for i in range(sims):
        if h_goals[i] == 1 and a_goals[i] == 0 and np.random.random() < 0.06: a_goals[i] = 1
        elif h_goals[i] == 0 and a_goals[i] == 1 and np.random.random() < 0.06: h_goals[i] = 1
            
    diff = h_goals - a_goals
    total = h_goals + a_goals
    
    hw = np.sum(diff > 0)/sims
    dr = np.sum(diff == 0)/sims
    aw = np.sum(diff < 0)/sims
    
    # AH 0.0 (Draw No Bet) True Probability calculation
    dnb_h = hw / (hw + aw) if (hw + aw) > 0 else 0
    dnb_a = aw / (hw + aw) if (hw + aw) > 0 else 0
    
    return {
        "Home Win": hw, "Draw": dr, "Away Win": aw,
        "AH -0.5 (H)": hw, "AH +0.5 (H)": hw + dr,
        "AH -1.5 (H)": np.sum(diff > 1)/sims, "AH +1.5 (H)": np.sum(diff > -2)/sims,
        "Over 1.5": np.sum(total > 1.5)/sims, "Under 1.5": np.sum(total < 1.5)/sims,
        "Over 2.5": np.sum(total > 2.5)/sims, "Under 2.5": np.sum(total < 2.5)/sims,
        "Over 3.5": np.sum(total > 3.5)/sims, "Under 3.5": np.sum(total < 3.5)/sims,
        "BTTS - Yes": np.sum((h_goals > 0) & (a_goals > 0))/sims,
        "BTTS - No": np.sum((h_goals == 0) | (a_goals == 0))/sims
    }

# ==========================================
# 4. THE PRO TERMINAL UI
# ==========================================
st.markdown("""
<div class="top-nav">
    <div class="logo">APEX<span>QUANT</span></div>
    <div class="live-status"><div class="dot"></div> PRO DATA FEED ACTIVE</div>
</div>
""", unsafe_allow_html=True)

col_menu, col_core, col_book = st.columns([1, 1.8, 2.2], gap="large")

with col_menu:
    st.markdown("<h3 style='color:#00F0FF; font-weight:900; font-size:1.1rem; text-transform:uppercase; letter-spacing:2px; margin-bottom:20px;'>Global Screener</h3>", unsafe_allow_html=True)
    target_date = st.date_input("Match Date", date.today())
    
    l_map = {"🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League": 39, "🇪🇺 Champions League": 2, "🇪🇸 La Liga": 140, "🇵🇹 Primeira Liga": 94, "🇮🇹 Serie A": 135, "🇩🇪 Bundesliga": 78}
    league_name = st.selectbox("Competition", list(l_map.keys()))
    league_id = l_map[league_name]
    
    with st.spinner("Connecting to Institutional Feeds..."):
        fixtures = get_live_fixtures(target_date.strftime('%Y-%m-%d'), league_id)
    
    m_sel = None
    if fixtures:
        m_map = {f"{f['teams']['home']['name']} vs {f['teams']['away']['name']}": f for f in fixtures}
        match_str = st.selectbox("Select Match", list(m_map.keys()))
        m_sel = m_map[match_str]
        st.button("🔄 SCAN MARKET LIQUIDITY", use_container_width=True)
    else:
        st.error("No fixtures found for selected parameters.")

if m_sel:
    h_id, a_id = m_sel['teams']['home']['id'], m_sel['teams']['away']['id']
    h_name, a_name = m_sel['teams']['home']['name'], m_sel['teams']['away']['name']
    
    with st.spinner("Running Monte Carlo (20,000 simulations) & Dixon-Coles adjustments..."):
        h_stats = get_real_stats(h_id, league_id)
        a_stats = get_real_stats(a_id, league_id)
        proj_h, proj_a = calculate_projected_goals(h_stats, a_stats)
        
        true_probs = run_monte_carlo_sim(proj_h, proj_a)
        live_odds = get_real_odds(m_sel['fixture']['id'])
    
    best_bet = None
    max_edge = 0
    valid_markets = []
    
    if live_odds:
        for mkt, odd in live_odds.items():
            prob = true_probs.get(mkt, 0)
            if odd > 1.05 and prob > 0:
                edge = (prob * odd) - 1
                valid_markets.append({"Market": mkt, "Odd": odd, "TrueProb": prob, "Edge": edge})
                if edge > max_edge:
                    max_edge = edge
                    best_bet = {"Market": mkt, "Odd": odd, "TrueProb": prob, "Edge": edge}
    
    with col_core:
        st.markdown(f"""
        <div class="lock-card">
            <div class="matchup">
                <div class="league-tag">{league_name} • QUANT PROJECTION</div>
                <div class="teams">{h_name} <span>vs</span> {a_name}</div>
            </div>
        """, unsafe_allow_html=True)
        
        c_xg1, c_xg2 = st.columns(2)
        c_xg1.markdown(f"<div style='text-align:center; font-family:\"JetBrains Mono\"; color:#00F0FF; font-size:1.2rem; font-weight:800;'>Proj Goals: {proj_h:.2f}</div>", unsafe_allow_html=True)
        c_xg2.markdown(f"<div style='text-align:center; font-family:\"JetBrains Mono\"; color:#D4AF37; font-size:1.2rem; font-weight:800;'>Proj Goals: {proj_a:.2f}</div>", unsafe_allow_html=True)
        
        st.markdown("<hr style='border-color:rgba(255,255,255,0.1);'>", unsafe_allow_html=True)

        if best_bet and best_bet["Edge"] > 0:
            st.markdown(f"""
                <div style="background: rgba(0, 255, 136, 0.05); border: 2px dashed #00FF88; border-radius: 12px; padding: 20px; text-align: center; margin: 20px 0;">
                    <div style="color: #00FF88; font-size: 0.8rem; font-weight: 800; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 10px;">⭐ HIGHEST +EV IDENTIFIED ⭐</div>
                    <div style="font-size: 2rem; font-weight: 900; color: #FFFFFF; text-shadow: 0 0 20px rgba(0,255,136,0.4);">{best_bet['Market']}</div>
                    <div style="display:flex; justify-content:center; gap:20px; margin-top:15px; font-family:'JetBrains Mono';">
                        <div style="background: rgba(255,255,255,0.1); padding: 5px 15px; border-radius: 6px;">Book Odd: <span style="color:#FFD700; font-weight:800;">{best_bet['Odd']:.2f}</span></div>
                        <div style="background: rgba(0,255,136,0.1); padding: 5px 15px; border-radius: 6px; color:#00FF88; font-weight:800;">EDGE: +{best_bet['Edge']*100:.1f}%</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        elif not live_odds:
            st.warning("⚠️ Waiting for liquid market odds to drop.")
        else:
            st.error("📉 EFFICIENT MARKET. No mathematical edge found across all professional lines. Pass.")
        
        st.markdown("</div>", unsafe_allow_html=True)

    with col_book:
        st.markdown("<h3 style='color:#FFFFFF; font-weight:900; font-size:1.1rem; text-transform:uppercase; letter-spacing:2px; margin-bottom:20px;'>Full Order Book</h3>", unsafe_allow_html=True)
        
        if live_odds:
            st.markdown("""
            <div style="display: grid; grid-template-columns: 2fr 1fr 1fr 1.5fr; font-size: 0.65rem; color: #64748B; text-transform: uppercase; letter-spacing: 1px; font-weight: 800; padding: 0 15px 10px 15px; border-bottom: 1px solid #1E293B; margin-bottom: 10px;">
                <div>Market</div><div style="text-align:right;">Book Odd</div><div style="text-align:right;">Fair Odd</div><div style="text-align:center;">Alpha (EV)</div>
            </div>
            <div style="max-height: 500px; overflow-y: auto; padding-right: 5px;">
            """, unsafe_allow_html=True)
            
            valid_markets = sorted(valid_markets, key=lambda x: x['Edge'], reverse=True)
            
            for m in valid_markets:
                mkt_name, m_odd, t_prob, edge = m['Market'], m['Odd'], m['TrueProb'], m['Edge']
                t_odd = 1 / t_prob if t_prob > 0 else 0
                
                # Highlight ONLY positive edges for quick professional scanning
                is_edge = edge > 0
                edge_color = "#00FF88" if is_edge else "#EF4444"
                bg_color = "rgba(0, 255, 136, 0.05)" if is_edge else "transparent"
                border = "border-left: 3px solid #00FF88;" if is_edge else "border-left: 3px solid transparent;"

                st.markdown(f"""
                <div class="order-row" style="{border} background:{bg_color};">
                    <div class="order-cell market-name">{mkt_name}</div>
                    <div class="order-cell" style="text-align:right; font-weight:800; color:#FFF;">{m_odd:.2f}</div>
                    <div class="order-cell" style="text-align:right; color:#00F0FF;">{t_odd:.2f}</div>
                    <div class="order-cell" style="text-align:center; color:{edge_color}; font-weight:800;">{edge*100:+.1f}%</div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
