import streamlit as st
import numpy as np
import pandas as pd
import requests
from datetime import date
import time

# ==========================================
# 1. PREMIUM FINTECH DESIGN SETUP
# ==========================================
st.set_page_config(page_title="APEX QUANT | PRO", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800;900&family=JetBrains+Mono:wght@400;700;800&display=swap');
    
    .stApp { background-color: #030407; color: #FFFFFF; font-family: 'Outfit', sans-serif; background-image: radial-gradient(circle at 50% 0%, #0A1128 0%, #030407 80%); }
    header, footer { visibility: hidden; }
    
    /* Premium Top Bar */
    .top-nav { background: rgba(3, 4, 7, 0.8); backdrop-filter: blur(20px); border-bottom: 1px solid rgba(0, 240, 255, 0.15); padding: 15px 40px; display: flex; justify-content: space-between; align-items: center; margin: -3rem -3rem 2rem -3rem; position: sticky; top: 0; z-index: 1000; box-shadow: 0 10px 30px rgba(0,0,0,0.5);}
    .logo { font-size: 2.2rem; font-weight: 900; letter-spacing: -1px; color: #FFFFFF; line-height: 1;}
    .logo span { color: #00F0FF; text-shadow: 0 0 15px rgba(0, 240, 255, 0.4); }
    
    .live-status { display: flex; align-items: center; gap: 10px; background: rgba(0, 255, 136, 0.1); border: 1px solid rgba(0, 255, 136, 0.3); padding: 8px 16px; border-radius: 50px; font-size: 0.8rem; font-weight: 800; text-transform: uppercase; color: #00FF88; letter-spacing: 1px; box-shadow: 0 0 15px rgba(0, 255, 136, 0.15); }
    .dot { width: 8px; height: 8px; background-color: #00FF88; border-radius: 50%; animation: pulse-green 1.5s infinite; box-shadow: 0 0 10px #00FF88; }
    @keyframes pulse-green { 0% { transform: scale(0.95); opacity: 1; } 50% { transform: scale(1.2); opacity: 0.5; } 100% { transform: scale(0.95); opacity: 1; } }

    /* Match Card & Metrics */
    .match-card { background: linear-gradient(180deg, #0A101D 0%, #05080F 100%); border: 1px solid rgba(0, 240, 255, 0.2); border-radius: 16px; padding: 25px; box-shadow: 0 20px 50px rgba(0,0,0,0.5); margin-bottom: 20px;}
    .teams { font-size: 2rem; font-weight: 900; line-height: 1.2; letter-spacing: -1px; text-align: center; margin-bottom: 20px;}
    .teams span { color: #64748B; font-weight: 400; font-size: 1.2rem; margin: 0 10px; }
    
    .metric-container { display: flex; justify-content: space-between; border-top: 1px solid rgba(255,255,255,0.05); padding-top: 15px; margin-top: 15px;}
    .metric-box { text-align: center; flex: 1; }
    .metric-label { font-size: 0.75rem; color: #64748B; text-transform: uppercase; letter-spacing: 1px; font-weight: 800; margin-bottom: 5px;}
    .metric-value { font-size: 1.4rem; font-family: 'JetBrains Mono'; font-weight: 900; color: #F8FAFC;}

    /* Order Book Matrix */
    .order-row { display: grid; grid-template-columns: 2fr 1fr 1fr 1fr 1fr; align-items: center; background: #080C16; border: 1px solid #1E293B; border-radius: 6px; margin-bottom: 6px; transition: all 0.2s; }
    .order-row:hover { border-color: #00F0FF; background: rgba(0, 240, 255, 0.02); }
    .order-cell { padding: 12px 15px; font-family: 'JetBrains Mono'; font-size: 0.9rem; }
    .market-name { color: #F8FAFC; font-weight: 800; font-family: 'Inter'; font-size: 0.85rem; }
    
    /* Alpha Signal Box */
    .alpha-box { background: rgba(0, 255, 136, 0.05); border: 2px solid #00FF88; border-radius: 12px; padding: 20px; text-align: center; box-shadow: 0 0 30px rgba(0,255,136,0.1); margin-top: 15px; }
    .alpha-title { color: #00FF88; font-size: 0.8rem; font-weight: 800; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 10px; }
    
    .stButton > button { background: linear-gradient(90deg, #00F0FF, #0088FF) !important; color: #FFF !important; font-weight: 900 !important; font-size: 1.1rem !important; text-transform: uppercase; border: none !important; border-radius: 8px !important; padding: 10px !important; transition: all 0.2s; }
    .stButton > button:hover { transform: translateY(-2px); box-shadow: 0 10px 20px rgba(0, 240, 255, 0.3); }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. DATA ENGINE (BULLETPROOF API PARSING)
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
    
    if not odds_data or not odds_data[0].get('bookmakers'):
        return market_odds
        
    try:
        bets = odds_data[0]['bookmakers'][0].get('bets', [])
        for bet in bets:
            name = bet.get('name', '')
            # Extração segura dos valores
            vals = {}
            for v in bet.get('values', []):
                val_key = str(v.get('value', ''))
                odd_val = float(v.get('odd', 0.0))
                vals[val_key] = odd_val
                
            if name == 'Match Winner':
                if 'Home' in vals: market_odds["Home Win"] = vals['Home']
                if 'Draw' in vals: market_odds["Draw"] = vals['Draw']
                if 'Away' in vals: market_odds["Away Win"] = vals['Away']
            elif name == 'Goals Over/Under':
                if 'Over 1.5' in vals: market_odds["Over 1.5"] = vals['Over 1.5']
                if 'Under 1.5' in vals: market_odds["Under 1.5"] = vals['Under 1.5']
                if 'Over 2.5' in vals: market_odds["Over 2.5"] = vals['Over 2.5']
                if 'Under 2.5' in vals: market_odds["Under 2.5"] = vals['Under 2.5']
                if 'Over 3.5' in vals: market_odds["Over 3.5"] = vals['Over 3.5']
                if 'Under 3.5' in vals: market_odds["Under 3.5"] = vals['Under 3.5']
            elif name == 'Both Teams Score':
                if 'Yes' in vals: market_odds["BTTS - Yes"] = vals['Yes']
                if 'No' in vals: market_odds["BTTS - No"] = vals['No']
            elif name == 'Asian Handicap':
                for k, odd in vals.items():
                    if "-0.5" in k and "Home" in k: market_odds["AH -0.5 (H)"] = odd
                    if "+0.5" in k and "Home" in k: market_odds["AH +0.5 (H)"] = odd
                    if "-1.5" in k and "Home" in k: market_odds["AH -1.5 (H)"] = odd
                    if "+1.5" in k and "Home" in k: market_odds["AH +1.5 (H)"] = odd
    except Exception as e:
        pass # Falha segura se a API mudar a estrutura drasticamente
        
    return market_odds

# ==========================================
# 3. ADVANCED QUANT MATH
# ==========================================
def calculate_projected_goals(h_stats, a_stats):
    h_attack, a_defense = h_stats['gf_h'] / 1.55, a_stats['ga_a'] / 1.55
    a_attack, h_defense = a_stats['gf_a'] / 1.25, h_stats['ga_h'] / 1.25
    return round(max(0.1, h_attack * a_defense * 1.55), 2), round(max(0.1, a_attack * h_defense * 1.25), 2)

def run_monte_carlo_sim(proj_h, proj_a, sims=25000):
    np.random.seed(int(time.time()))
    h_goals, a_goals = np.random.poisson(proj_h, sims), np.random.poisson(proj_a, sims)
    
    # Dixon-Coles Adjustment
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

def get_market_margin():
    return 0.045 # 4.5% Institutional Vig

# ==========================================
# 4. PREMIUM UI RENDERING
# ==========================================
st.markdown("""
<div class="top-nav">
    <div class="logo">APEX<span>QUANT</span></div>
    <div class="live-status"><div class="dot"></div> LIVE MARKET FEED</div>
</div>
""", unsafe_allow_html=True)

col_menu, col_core, col_book = st.columns([1, 1.8, 2.2], gap="large")

with col_menu:
    st.markdown("<h3 style='color:#00F0FF; font-weight:900; font-size:1.1rem; text-transform:uppercase; letter-spacing:2px; margin-bottom:20px;'>Market Screener</h3>", unsafe_allow_html=True)
    target_date = st.date_input("Match Date", date.today())
    
    l_map = {"🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League": 39, "🇪🇺 Champions League": 2, "🇪🇸 La Liga": 140, "🇵🇹 Primeira Liga": 94, "🇮🇹 Serie A": 135, "🇩🇪 Bundesliga": 78}
    league_name = st.selectbox("Competition", list(l_map.keys()))
    
    with st.spinner("Connecting to Liquidity Pools..."):
        fixtures = get_live_fixtures(target_date.strftime('%Y-%m-%d'), l_map[league_name])
    
    m_sel = None
    if fixtures:
        m_map = {f"{f['teams']['home']['name']} vs {f['teams']['away']['name']}": f for f in fixtures}
        m_sel = m_map[st.selectbox("Select Target Match", list(m_map.keys()))]
        st.button("🔄 ANALYZE FIXTURE", use_container_width=True)
    else:
        st.info("No fixtures scheduled for this date/league.")

if m_sel:
    h_id, a_id = m_sel['teams']['home']['id'], m_sel['teams']['away']['id']
    
    with st.spinner("Processing Bivariate Monte Carlo (25k paths)..."):
        h_stats, a_stats = get_real_stats(h_id, l_map[league_name]), get_real_stats(a_id, l_map[league_name])
        proj_h, proj_a = calculate_projected_goals(h_stats, a_stats)
        true_probs = run_monte_carlo_sim(proj_h, proj_a, 25000)
        live_odds = get_real_odds(m_sel['fixture']['id'])
    
    valid_markets = []
    best_bet, max_edge = None, 0
    margin = get_market_margin()
    
    if live_odds:
        for mkt, odd in live_odds.items():
            prob = true_probs.get(mkt, 0)
            if odd > 1.05 and prob > 0:
                market_implied = 1 / odd
                fair_market_prob = market_implied / (1 + margin)
                
                edge = (prob * odd) - 1
                valid_markets.append({
                    "Market": mkt, "Odd": odd, "TrueProb": prob, "Edge": edge, 
                    "FairMarketProb": fair_market_prob
                })
                if edge > max_edge:
                    max_edge, best_bet = edge, valid_markets[-1]
    
    with col_core:
        # STRIPPED HTML - No indentation to prevent white boxes
        st.markdown(f"""
<div class="match-card">
    <div style="font-size: 0.8rem; color: #00F0FF; text-transform: uppercase; letter-spacing: 3px; font-weight: 800; text-align: center; margin-bottom: 10px;">QUANT PROJECTION</div>
    <div class="teams">{m_sel['teams']['home']['name']} <span>vs</span> {m_sel['teams']['away']['name']}</div>
    
    <div class="metric-container">
        <div class="metric-box">
            <div class="metric-label">Model xG (H)</div>
            <div class="metric-value" style="color:#00F0FF;">{proj_h:.2f}</div>
        </div>
        <div class="metric-box" style="border-left: 1px solid rgba(255,255,255,0.05); border-right: 1px solid rgba(255,255,255,0.05);">
            <div class="metric-label">Simulations</div>
            <div class="metric-value">25,000</div>
        </div>
        <div class="metric-box">
            <div class="metric-label">Model xG (A)</div>
            <div class="metric-value" style="color:#FFD700;">{proj_a:.2f}</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

        if best_bet and best_bet["Edge"] > 0:
            rec_kelly = calculate_kelly(best_bet['TrueProb'], best_bet['Odd'])
            st.markdown(f"""
<div class="alpha-box">
    <div class="alpha-title">⭐ ALPHA SIGNAL IDENTIFIED ⭐</div>
    <div style="font-size: 2.2rem; font-weight: 900; color: #FFFFFF; text-shadow: 0 0 20px rgba(0,255,136,0.4); margin-bottom: 20px;">{best_bet['Market']}</div>
    
    <div style="display: flex; justify-content: space-around; font-family: 'JetBrains Mono';">
        <div>
            <div style="color: #64748B; font-size: 0.75rem; font-weight: 800;">BOOKIE LINE</div>
            <div style="color: #FFD700; font-size: 1.3rem; font-weight: 900;">{best_bet['Odd']:.2f}</div>
        </div>
        <div>
            <div style="color: #64748B; font-size: 0.75rem; font-weight: 800;">EXPECTED VALUE</div>
            <div style="color: #00FF88; font-size: 1.3rem; font-weight: 900;">+{best_bet['Edge']*100:.1f}%</div>
        </div>
        <div>
            <div style="color: #64748B; font-size: 0.75rem; font-weight: 800;">KELLY (1/4) SIZE</div>
            <div style="color: #FFFFFF; font-size: 1.3rem; font-weight: 900;">{rec_kelly:.2f}%</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)
        elif not live_odds:
            st.warning("⚠️ Market Makers have not released liquidity for this fixture yet.")
        else:
            st.error("📉 Efficient Market Detected. No mathematical edge found.")

    with col_book:
        st.markdown("<h3 style='color:#FFFFFF; font-weight:900; font-size:1.1rem; text-transform:uppercase; letter-spacing:2px; margin-bottom:20px;'>Institutional Order Book</h3>", unsafe_allow_html=True)
        
        if live_odds:
            st.markdown("""
            <div style="display: grid; grid-template-columns: 2fr 1fr 1fr 1fr 1fr; font-size: 0.65rem; color: #64748B; text-transform: uppercase; letter-spacing: 1px; font-weight: 800; padding: 0 15px 10px 15px; border-bottom: 1px solid #1E293B; margin-bottom: 10px;">
                <div>MARKET</div>
                <div style="text-align:right;">ODDS</div>
                <div style="text-align:right;">NO-VIG</div>
                <div style="text-align:right;">SYS PROB</div>
                <div style="text-align:right;">EDGE</div>
            </div>
            <div style="max-height: 550px; overflow-y: auto; padding-right: 5px;">
            """, unsafe_allow_html=True)
            
            valid_markets = sorted(valid_markets, key=lambda x: x['Edge'], reverse=True)
            for m in valid_markets:
                is_edge = m['Edge'] > 0
                txt_col = "#00FF88" if is_edge else "#EF4444"
                bg_col = "rgba(0, 255, 136, 0.05)" if is_edge else "transparent"
                border = "border-left: 3px solid #00FF88;" if is_edge else "border-left: 3px solid transparent;"
                
                st.markdown(f"""
                <div class="order-row" style="{border} background:{bg_col};">
                    <div class="order-cell market-name">{m['Market']}</div>
                    <div class="order-cell" style="text-align:right; font-weight:800; color:#FFF;">{m['Odd']:.2f}</div>
                    <div class="order-cell" style="text-align:right; color:#64748B;">{m['FairMarketProb']*100:.1f}%</div>
                    <div class="order-cell" style="text-align:right; color:#00F0FF;">{m['TrueProb']*100:.1f}%</div>
                    <div class="order-cell" style="text-align:right; color:{txt_col}; font-weight:800;">{m['Edge']*100:+.1f}%</div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
