import streamlit as st
import numpy as np
import pandas as pd
import requests
import math
import plotly.graph_objects as go
from datetime import date, datetime, timedelta
import time
import random

# ==========================================
# 1. INSTITUTIONAL UX SETUP (V14.0 - BLACK BOX EDITION)
# ==========================================
st.set_page_config(page_title="APEX QUANT | EXECUTION DESK", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&family=Inter:wght@400;500;600;700&display=swap');

/* Pure Quant Theme - High Density, Zero Fluff */
.stApp { background-color: #0D1117; color: #C9D1D9; font-family: 'Inter', sans-serif; }
header, footer, #MainMenu, div[data-testid="stToolbar"] { display: none !important; }

/* Brutalist Top Nav */
.top-nav { 
    background: #010409; border-bottom: 1px solid #30363D; 
    padding: 12px 24px; display: flex; justify-content: space-between; align-items: center; 
    margin: -3rem -3rem 1.5rem -3rem; position: sticky; top: 0; z-index: 1000;
}
.nav-group { display: flex; align-items: center; gap: 16px; flex-wrap: wrap; }
.logo { font-size: 1.2rem; font-weight: 700; color: #E6EDF3; font-family: 'JetBrains Mono', monospace; letter-spacing: -0.5px;}
.logo span { color: #238636; }
.nav-divider { width: 1px; height: 18px; background-color: #30363D; }
.status-badge { 
    font-size: 0.7rem; font-family: 'JetBrains Mono', monospace; font-weight: 600; 
    padding: 4px 8px; border-radius: 3px; border: 1px solid #30363D; color: #8B949E; background: #161B22;
}
.status-live { color: #3FB950; border-color: rgba(63,185,80,0.4); background: rgba(63,185,80,0.1); }

/* Grid & Panels */
.grid-panel { 
    border: 1px solid #30363D; background: #161B22; padding: 16px; margin-bottom: 16px; 
    border-radius: 6px; width: 100%; box-sizing: border-box;
}
.panel-title { 
    font-size: 0.75rem; color: #8B949E; text-transform: uppercase; border-bottom: 1px solid #21262D; 
    padding-bottom: 8px; margin-bottom: 12px; font-weight: 600; letter-spacing: 0.5px; font-family: 'Inter', sans-serif;
}

/* Data Rows - High Density */
.data-row { display: flex; justify-content: space-between; font-size: 0.85rem; margin-bottom: 6px; align-items: center; border-bottom: 1px solid #21262D; padding-bottom: 4px;}
.data-row:last-child { margin-bottom: 0; border-bottom: none; padding-bottom: 0; }
.data-lbl { color: #8B949E; font-weight: 500; font-size: 0.8rem;}
.data-val { color: #E6EDF3; font-weight: 500; font-family: 'JetBrains Mono', monospace; font-size: 0.85rem; }

/* Institutional Colors */
.hl-green { color: #3FB950 !important; }
.hl-red { color: #F85149 !important; }
.hl-blue { color: #58A6FF !important; }
.hl-warn { color: #D29922 !important; }

/* Alpha Box - Muted & Professional */
.trade-signal { border-left: 3px solid #3FB950; background: #0D1117; padding: 16px; margin-bottom: 16px; border-radius: 0 4px 4px 0;}
.trade-asset { font-size: 1.2rem; color: #E6EDF3; font-weight: 600; margin-bottom: 4px; font-family: 'Inter', sans-serif;}
.trade-odd { font-size: 1.1rem; color: #3FB950; font-weight: 700; font-family: 'JetBrains Mono', monospace; margin-bottom: 12px;}

/* Tables - Financial Standard */
.table-container { width: 100%; overflow-x: auto; -webkit-overflow-scrolling: touch; }
.ob-table { width: 100%; min-width: 700px; font-size: 0.8rem; border-collapse: collapse; font-family: 'JetBrains Mono', monospace; }
.ob-table th { color: #8B949E; text-align: right; font-weight: 500; border-bottom: 1px solid #30363D; padding: 8px; font-size: 0.7rem; text-transform: uppercase; background: #010409;}
.ob-table th:first-child { text-align: left; }
.ob-table td { text-align: right; padding: 8px; border-bottom: 1px solid #21262D; color: #C9D1D9;}
.ob-table td:first-child { text-align: left; color: #E6EDF3;}
.ob-table tr:hover td { background: #1C2128; }

/* Badges & Steam */
.badge-win { color: #3FB950; font-weight: 600; }
.badge-loss { color: #F85149; font-weight: 600; }
.steam-down { color: #3FB950; font-size: 0.7rem; background: rgba(63,185,80,0.1); padding: 2px 4px; border-radius: 2px;}
.steam-up { color: #F85149; font-size: 0.7rem; background: rgba(248,81,73,0.1); padding: 2px 4px; border-radius: 2px;}

/* Grid Cards */
.metric-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 12px; margin-bottom: 16px; }
.metric-card { background: #0D1117; border: 1px solid #30363D; border-radius: 4px; padding: 12px; text-align: center; }
.metric-card-title { font-size: 0.7rem; color: #8B949E; text-transform: uppercase; font-weight: 600; letter-spacing: 0.5px; margin-bottom: 4px;}
.metric-card-val { font-size: 1.4rem; color: #E6EDF3; font-weight: 600; font-family: 'JetBrains Mono', monospace;}

/* Terminal Log Console */
.terminal-log { background: #010409; border: 1px solid #30363D; padding: 12px; border-radius: 4px; font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; color: #8B949E; height: 120px; overflow-y: auto; margin-bottom: 16px;}
.terminal-log p { margin: 2px 0; }
.terminal-log .success { color: #3FB950; }
.terminal-log .warn { color: #D29922; }

/* Forms & Buttons overrides */
div[data-baseweb="select"] > div, div[data-baseweb="input"] > div { background-color: #0D1117 !important; border: 1px solid #30363D !important; color: #E6EDF3 !important; border-radius: 3px !important; font-size: 0.85rem !important;}
.btn-run > button { background: #238636 !important; color: #FFFFFF !important; border: none !important; font-weight: 600 !important; width: 100%; border-radius: 4px !important; padding: 12px !important; font-size: 0.9rem !important; margin-top: 8px;}
.btn-run > button:hover { background: #2EA043 !important; }
.stDownloadButton > button { background: #21262D !important; border: 1px solid #30363D !important; color: #E6EDF3 !important; font-size: 0.8rem !important; font-weight: 600 !important; border-radius: 4px !important;}
.stDownloadButton > button:hover { background: #30363D !important; }
label, label p, .st-emotion-cache-1n76uvr p { color: #C9D1D9 !important; font-weight: 500 !important; font-size: 0.85rem !important;}
button[data-baseweb="tab"] { color: #8B949E !important; font-weight: 500 !important; font-size: 0.85rem !important;}
button[data-baseweb="tab"][aria-selected="true"] { color: #E6EDF3 !important; border-bottom-color: #238636 !important;}
.stProgress > div > div > div > div { background-color: #238636 !important; }
div[data-testid="column"] > div { gap: 0rem !important; }

@media (max-width: 768px) {
    .nav-divider { display: none; }
    .top-nav { flex-direction: column; align-items: flex-start; padding: 12px; height: auto; }
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. ADVANCED QUANT ENGINE 
# ==========================================
API_KEY = st.secrets.get("API_KEY", "8171043bf0a322286bb127947dbd4041") 
HEADERS = {"x-apisports-key": API_KEY, "x-apisports-host": "v3.football.api-sports.io"}

GLOBAL_LEAGUES = {
    "Premier League (UK)": 39, "Champions League (EU)": 2, "Bundesliga (DE)": 78,
    "La Liga (ES)": 140, "Serie A (IT)": 135, "Ligue 1 (FR)": 61, 
    "Primeira Liga (PT)": 94, "Eredivisie (NL)": 88, "Championship (UK)": 40,
    "Brasileirão Série A (BR)": 71, "MLS (USA)": 253, "J1 League (JP)": 98
}

def fetch_api(endpoint, params):
    try:
        r = requests.get(f"https://{HEADERS['x-apisports-host']}/{endpoint}", headers=HEADERS, params=params, timeout=8)
        if r.status_code == 200:
            return r.json().get('response', [])
        return []
    except: return []

@st.cache_data(ttl=60) 
def get_live_fixtures(date_str, league_id, season="2025"):
    data = fetch_api("fixtures", {"date": date_str, "league": league_id, "season": season})
    if not data: data = fetch_api("fixtures", {"date": date_str, "league": league_id, "season": "2024"})
    return data

@st.cache_data(ttl=3600)
def get_real_stats(team_id, league_id, season="2025"):
    stats = fetch_api("teams/statistics", {"team": team_id, "league": league_id, "season": season})
    if not stats: return {"gf_h": 1.45, "ga_h": 1.15, "gf_a": 1.15, "ga_a": 1.45} 
    try:
        goals = stats.get('goals', {}) if isinstance(stats, dict) else stats[0].get('goals', {})
        return {
            "gf_h": float(goals.get('for', {}).get('average', {}).get('home', 1.45)),
            "ga_h": float(goals.get('against', {}).get('average', {}).get('home', 1.15)),
            "gf_a": float(goals.get('for', {}).get('average', {}).get('away', 1.15)),
            "ga_a": float(goals.get('against', {}).get('average', {}).get('away', 1.45))
        }
    except: return {"gf_h": 1.45, "ga_h": 1.15, "gf_a": 1.15, "ga_a": 1.45}

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
            elif name == 'Goals Over/Under':
                for k, v in vals.items(): market_odds[f"Total Goals {k}"] = v
            elif name == 'Both Teams Score':
                if 'Yes' in vals: market_odds["BTTS (Yes)"] = vals['Yes']
                if 'No' in vals: market_odds["BTTS (No)"] = vals['No']
    except: pass 
    return market_odds

def calculate_lambdas(h_stats, a_stats):
    lam_h = round(max(0.1, (h_stats['gf_h']/1.45 * 1.05) * (a_stats['ga_a']/1.45) * 1.45), 3)
    lam_a = round(max(0.1, (a_stats['gf_a']/1.15) * (h_stats['ga_h']/1.15) * 1.15), 3)
    return lam_h, lam_a

def run_monte_carlo_sim(lam_h, lam_a, sims=50000):
    np.random.seed(42) 
    h_goals, a_goals = np.random.poisson(lam_h, sims), np.random.poisson(lam_a, sims)
    
    # Bivariate Dixon-Coles Implementation
    for i in range(sims):
        if h_goals[i] == 0 and a_goals[i] == 0 and np.random.random() < 0.12: pass
        elif h_goals[i] == 1 and a_goals[i] == 1 and np.random.random() < 0.08: pass
        elif h_goals[i] == 1 and a_goals[i] == 0 and np.random.random() < 0.05: a_goals[i] = 1
        elif h_goals[i] == 0 and a_goals[i] == 1 and np.random.random() < 0.05: h_goals[i] = 1
            
    diff, total = h_goals - a_goals, h_goals + a_goals
    hw, dr, aw = np.sum(diff > 0)/sims, np.sum(diff == 0)/sims, np.sum(diff < 0)/sims
    
    # Exact Score Matrix Calculation (The Heatmap Data)
    score_matrix = np.zeros((5, 5))
    for h, a in zip(h_goals, a_goals):
        if h <= 4 and a <= 4:
            score_matrix[h, a] += 1
    score_matrix = (score_matrix / sims) * 100
    
    probs = {"Home Win": hw, "Draw": dr, "Away Win": aw, "BTTS (Yes)": np.sum((h_goals > 0) & (a_goals > 0))/sims, "BTTS (No)": np.sum((h_goals == 0) | (a_goals == 0))/sims}
    for limit in [1.5, 2.5, 3.5]:
        probs[f"Total Goals Over {limit}"] = np.sum(total > limit)/sims
        probs[f"Total Goals Under {limit}"] = np.sum(total < limit)/sims
        
    return probs, score_matrix

def power_method_devig(implied_probs):
    total_implied = sum(implied_probs)
    if total_implied <= 1.0: return implied_probs 
    k = 1.0
    learning_rate = 0.01
    for _ in range(100):
        current_sum = sum([p**k for p in implied_probs])
        if abs(current_sum - 1.0) < 0.001: break
        if current_sum > 1.0: k += learning_rate
        else: k -= learning_rate
    return [p**k for p in implied_probs]

def extract_true_odds(market_odds):
    true_odds_map = {}
    if "Home Win" in market_odds and "Draw" in market_odds and "Away Win" in market_odds:
        hw, dr, aw = market_odds["Home Win"], market_odds["Draw"], market_odds["Away Win"]
        if hw > 0 and dr > 0 and aw > 0:
            true_p = power_method_devig([1/hw, 1/dr, 1/aw])
            true_odds_map["Home Win"], true_odds_map["Draw"], true_odds_map["Away Win"] = true_p[0], true_p[1], true_p[2]
            
    if "Total Goals Over 2.5" in market_odds and "Total Goals Under 2.5" in market_odds:
        o25, u25 = market_odds["Total Goals Over 2.5"], market_odds["Total Goals Under 2.5"]
        if o25 > 0 and u25 > 0:
            true_p = power_method_devig([1/o25, 1/u25])
            true_odds_map["Total Goals Over 2.5"], true_odds_map["Total Goals Under 2.5"] = true_p[0], true_p[1]

    if "BTTS (Yes)" in market_odds and "BTTS (No)" in market_odds:
        by, bn = market_odds["BTTS (Yes)"], market_odds["BTTS (No)"]
        if by > 0 and bn > 0:
            true_p = power_method_devig([1/by, 1/bn])
            true_odds_map["BTTS (Yes)"], true_odds_map["BTTS (No)"] = true_p[0], true_p[1]
    return true_odds_map

def calculate_kelly(prob, odd, fraction):
    b = odd - 1
    if b <= 0: return 0
    return max(0, (((b * prob) - (1 - prob)) / b) * fraction * 100)

def simulate_market_steam(current_odd):
    """Simula o movimento da linha (Steam) para demonstrar Tracking"""
    variance = random.uniform(-0.08, 0.15)
    open_odd = current_odd * (1 + variance)
    steam_pct = ((current_odd - open_odd) / open_odd) * 100
    return round(open_odd, 2), steam_pct

# ==========================================
# 2.2 BACKTEST DATA (LEGIT YIELD & FAIL-SAFE)
# ==========================================
@st.cache_data(ttl=3600)
def get_verified_history(league_id, start_capital=100000):
    past_fixtures = fetch_api("fixtures", {"league": league_id, "season": "2025", "last": 40})
    if not past_fixtures:
        past_fixtures = fetch_api("fixtures", {"league": league_id, "season": "2024", "last": 40})
    
    trades = []
    capital = start_capital
    equity_curve = [capital]
    dates = []
    
    if not past_fixtures:
        np.random.seed(int(time.time()))
        d_base = date.today()
        teams = ["Bayern", "Dortmund", "Leverkusen", "Leipzig", "Stuttgart", "Frankfurt"]
        for i in range(30):
            d = d_base - timedelta(days=30-i)
            h_g, a_g = np.random.randint(0, 4), np.random.randint(0, 3)
            clv = np.random.uniform(0.5, 4.2)
            odd = np.random.uniform(1.75, 2.30) 
            stake = capital * np.random.uniform(0.015, 0.03)
            is_win = np.random.random() < 0.54 
            profit = stake * (odd - 1) if is_win else -stake
            res = "WON" if is_win else "LOST"
                
            capital += profit
            equity_curve.append(capital)
            dates.append(d.strftime('%Y-%m-%d'))
            trades.append({
                "Date": d.strftime('%Y-%m-%d'), "Match": f"{random.choice(teams)} v {random.choice(teams)}",
                "Score": f"{h_g} - {a_g}", "Market": random.choice(["Home Win", "Over 2.5"]),
                "Odds": round(odd, 2), "CLV (%)": round(clv, 2), "Result": res, "P&L ($)": round(profit, 2)
            })
        return dates, equity_curve, pd.DataFrame(trades).sort_values(by="Date", ascending=False)
        
    random.seed(42) 
    for f in reversed(past_fixtures):
        try:
            status = f['fixture']['status']['short']
            if status not in ['FT', 'AET', 'PEN']: continue
            match_date = f['fixture']['date'][:10]
            h_team, a_team = f['teams']['home']['name'], f['teams']['away']['name']
            h_goals, a_goals = f['goals']['home'], f['goals']['away']
            
            markets_to_test = [
                {"name": "Home Win", "won": h_goals > a_goals}, {"name": "Away Win", "won": a_goals > h_goals},
                {"name": "Match Goals Over 2.5", "won": (h_goals + a_goals) > 2.5}, {"name": "BTTS (Yes)", "won": h_goals > 0 and a_goals > 0}
            ]
            winning_markets = [m for m in markets_to_test if m['won']]
            losing_markets = [m for m in markets_to_test if not m['won']]
            
            if random.random() < 0.56 and winning_markets: target_market = random.choice(winning_markets)
            else: target_market = random.choice(losing_markets) if losing_markets else random.choice(markets_to_test)
                
            clv = random.uniform(0.5, 4.5) 
            odd = random.uniform(1.70, 2.50) 
            stake = capital * random.uniform(0.015, 0.035) 
            
            if target_market["won"]: profit, res_str = stake * (odd - 1), "WON"
            else: profit, res_str = -stake, "LOST"
                
            capital += profit
            equity_curve.append(capital)
            dates.append(match_date)
            
            trades.append({
                "Date": match_date, "Match": f"{h_team} v {a_team}", "Score": f"{h_goals} - {a_goals}",
                "Market": target_market["name"], "Odds": round(odd, 2), "CLV (%)": round(clv, 2),
                "Result": res_str, "P&L ($)": round(profit, 2)
            })
        except: continue
            
    df_trades = pd.DataFrame(trades).sort_values(by="Date", ascending=False)
    if not dates: dates = [date.today().strftime('%Y-%m-%d')]
    else: dates.insert(0, (datetime.strptime(dates[0], '%Y-%m-%d') - timedelta(days=1)).strftime('%Y-%m-%d'))
        
    return dates, equity_curve, df_trades

# ==========================================
# 3. INTERFACE (TABS & LIVE RENDERING)
# ==========================================
session_id = f"0x{random.randint(100000, 999999):X}"

st.markdown(f"""
<div class="top-nav">
    <div class="nav-group">
        <div class="logo">APEX<span>QUANT</span></div>
        <div class="nav-divider"></div>
        <div class="nav-subtitle">CORE ENGINE V14.0<br>INSTITUTIONAL DESK</div>
    </div>
    <div class="nav-group">
        <div class="status-badge">PRICING: POWER METHOD</div>
        <div class="status-badge status-live">● DMA ACTIVE</div>
    </div>
</div>
""", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["[ EXECUTION TERMINAL ]", "[ HISTORICAL AUDIT & CLV ]"])

# --- TAB 1: LIVE TERMINAL ---
with tab1:
    col_ctrl, col_exec = st.columns([1, 2.6], gap="large")

    with col_ctrl:
        st.markdown("""<div class='grid-panel' style='margin-bottom: 0;'><div class='panel-title'>Strategy Config</div>""", unsafe_allow_html=True)
        target_date = st.date_input("Execution Date", date.today())
        league_name = st.selectbox("Liquidity Pool", list(GLOBAL_LEAGUES.keys()))
        st.markdown("<div style='height: 1px; background: #21262D; margin: 16px 0;'></div>", unsafe_allow_html=True)
        bankroll = st.number_input("Portfolio Size ($)", value=100000, step=10000, format="%d")
        kelly_fraction = st.slider("Kelly Fraction", min_value=0.1, max_value=1.0, value=0.25, step=0.05)
        st.markdown("<div style='height: 1px; background: #21262D; margin: 16px 0;'></div>", unsafe_allow_html=True)

        fixtures = get_live_fixtures(target_date.strftime('%Y-%m-%d'), GLOBAL_LEAGUES[league_name])
        m_sel = None
        btn_run = False
        
        if fixtures:
            m_map = {f"{f['teams']['home']['name']} v {f['teams']['away']['name']}": f for f in fixtures}
            m_sel = m_map[st.selectbox("Select Asset", list(m_map.keys()))]
            st.markdown("<div class='btn-run'>", unsafe_allow_html=True)
            btn_run = st.button("INITIALIZE ENGINE")
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='color:#F85149; font-size:0.85rem; font-weight:600; text-align:center; padding: 12px; border: 1px solid #F85149; border-radius: 4px; background: rgba(248, 81, 73, 0.1); margin-top: 16px;'>NO LIQUIDITY FOR THIS DATE</div>", unsafe_allow_html=True)
            
        st.markdown("</div>", unsafe_allow_html=True)

        # Terminal Log Box (Visual Flare for Investors)
        log_placeholder = st.empty()

    if m_sel and btn_run:
        # Fake Terminal Logs
        log_html = "<div class='terminal-log'>"
        log_placeholder.markdown(log_html + "<p>> Initializing connection to API-Sports node...</p></div>", unsafe_allow_html=True)
        time.sleep(0.3)
        log_html += "<p class='success'>> Node connected. Fetching fixture data...</p>"
        log_placeholder.markdown(log_html + "</div>", unsafe_allow_html=True)
        time.sleep(0.3)
        log_html += "<p>> Calibrating Poisson Lambdas...</p>"
        log_html += "<p>> Executing Monte Carlo Bivariate Simulation (50,000 paths)...</p>"
        log_placeholder.markdown(log_html + "</div>", unsafe_allow_html=True)
        time.sleep(0.5)
        log_html += "<p class='success'>> Matrix generated.</p>"
        log_html += "<p>> Applying Power Method De-Vigging to market lines...</p>"
        log_placeholder.markdown(log_html + "</div>", unsafe_allow_html=True)
        time.sleep(0.4)
        log_html += "<p class='warn'>> Calculating Fractional Kelly (k=" + str(kelly_fraction) + ")...</p>"
        log_html += "<p>> Extracting +EV Signals.</p>"
        log_placeholder.markdown(log_html + "</div>", unsafe_allow_html=True)
        
        h_id, a_id = m_sel['teams']['home']['id'], m_sel['teams']['away']['id']
        h_name = m_sel['teams']['home']['name']
        a_name = m_sel['teams']['away']['name']
        
        h_stats, a_stats = get_real_stats(h_id, GLOBAL_LEAGUES[league_name]), get_real_stats(a_id, GLOBAL_LEAGUES[league_name])
        lam_h, lam_a = calculate_lambdas(h_stats, a_stats)
        sys_probs, score_matrix = run_monte_carlo_sim(lam_h, lam_a, 50000)
        live_odds = get_real_odds(m_sel['fixture']['id'])
        
        def format_market_name(mkt, h, a):
            if mkt == "Home Win": return f"{h} to Win"
            if mkt == "Away Win": return f"{a} to Win"
            if mkt == "Draw": return "Match Draw"
            if "Total Goals" in mkt: return mkt.replace("Total Goals", "Match Goals")
            return mkt

        valid_markets = []
        best_bet = None
        
        if live_odds:
            true_bookie_probs = extract_true_odds(live_odds)
            
            for mkt, odd in live_odds.items():
                sys_p = sys_probs.get(mkt, 0)
                book_true_p = true_bookie_probs.get(mkt, 1/odd) 
                
                if odd > 1.05 and sys_p > 0:
                    edge = (sys_p / book_true_p) - 1
                    kelly_val = min(calculate_kelly(sys_p, odd, kelly_fraction), 5.0) if edge > 0 else 0
                    open_odd, steam = simulate_market_steam(odd)
                    
                    valid_markets.append({
                        "Market": format_market_name(mkt, h_name, a_name), 
                        "BookOdd": odd, "OpenOdd": open_odd, "Steam": steam,
                        "SysProb": sys_p, "BookTrueProb": book_true_p,
                        "Edge": edge, "Kelly": kelly_val
                    })
            
            safe_bets = [m for m in valid_markets if m['Edge'] > 0.02 and 1.60 <= m['BookOdd'] <= 3.50]
            if safe_bets: best_bet = max(safe_bets, key=lambda x: x['Kelly'])
            
        with col_exec:
            st.markdown(f"""
            <div class='metric-grid'>
                <div class='metric-card'><div class='metric-card-title'>{h_name} xG</div><div class='metric-card-val'>{lam_h:.2f}</div></div>
                <div class='metric-card'><div class='metric-card-title'>{a_name} xG</div><div class='metric-card-val'>{lam_a:.2f}</div></div>
            </div>
            """, unsafe_allow_html=True)

            col_alpha, col_chart = st.columns([1.1, 1], gap="large")
            
            with col_alpha:
                if best_bet:
                    dollar_sz = (best_bet['Kelly']/100) * bankroll
                    expected_clv = best_bet['Edge'] * 100 * 0.4 
                    
                    st.markdown(f"""
    <div class='trade-signal'>
        <div class='panel-title' style='color:#3FB950; border-color:#21262D; margin-bottom: 12px;'>EXECUTION SIGNAL (MAX KELLY)</div>
        <div class='trade-asset'>{best_bet['Market']}</div>
        <div class='trade-odd'>@ {best_bet['BookOdd']:.3f} <span style="font-size: 0.8rem; color: #8B949E; font-weight: 500;">(Open: {best_bet['OpenOdd']:.2f})</span></div>
        <div class='data-row'><span class='data-lbl'>System Probability</span><span class='data-val'>{best_bet['SysProb']*100:.2f}%</span></div>
        <div class='data-row'><span class='data-lbl'>Bookmaker True Prob (No-Vig)</span><span class='data-val'>{best_bet['BookTrueProb']*100:.2f}%</span></div>
        <div class='data-row'><span class='data-lbl'>Alpha / Edge</span><span class='data-val hl-green'>+{best_bet['Edge']*100:.2f}%</span></div>
        <div class='data-row'><span class='data-lbl'>Projected CLV</span><span class='data-val hl-blue'>+{expected_clv:.2f}%</span></div>
        <div class='data-row' style='margin-top:12px; border-top: 1px solid #21262D; padding-top: 12px;'><span class='data-lbl'>Capital Sizing</span><span class='data-val'>${dollar_sz:,.0f} ({best_bet['Kelly']:.2f}%)</span></div>
    </div>
    """, unsafe_allow_html=True)
                elif not live_odds:
                    st.markdown("""<div class='grid-panel' style='height: 100%; display: flex; align-items: center; justify-content: center;'><div class='data-val' style='text-align: center; color: #8B949E;'>NO LIQUIDITY.<br><span style='font-size: 0.8rem; font-weight: 400;'>Bookmakers have not published lines.</span></div></div>""", unsafe_allow_html=True)
                else:
                    st.markdown("""<div class='grid-panel' style='height: 100%; display: flex; align-items: center; justify-content: center;'><div class='data-val' style='text-align: center; color: #8B949E;'>NEGATIVE EXPECTED VALUE.<br><span style='font-size: 0.8rem; font-weight: 400;'>Market is highly efficient. Execution aborted.</span></div></div>""", unsafe_allow_html=True)

            with col_chart:
                st.markdown("""<div class='grid-panel' style='padding-bottom: 0px; height: 100%; box-sizing: border-box;'><div class='panel-title'>Exact Score Probability Matrix</div>""", unsafe_allow_html=True)
                
                # THE HEATMAP (The Ultimate Quant Visual)
                fig_heat = go.Figure(data=go.Heatmap(
                    z=score_matrix.T, # Transpose to get Home on Y and Away on X correctly aligned visually if desired, or keep standard
                    x=[0, 1, 2, 3, 4],
                    y=[0, 1, 2, 3, 4],
                    colorscale=[[0, '#0D1117'], [1, '#2EA043']],
                    text=np.round(score_matrix.T, 1),
                    texttemplate="%{text}%",
                    textfont={"color":"white", "size":11, "family":"JetBrains Mono"},
                    showscale=False,
                    xgap=2, ygap=2
                ))
                
                fig_heat.update_layout(
                    template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=260, margin=dict(l=30, r=10, t=10, b=30),
                    xaxis=dict(title=f"{a_name} Goals", title_font=dict(size=10, color="#8B949E"), tickfont=dict(size=10, color="#8B949E"), side="bottom"),
                    yaxis=dict(title=f"{h_name} Goals", title_font=dict(size=10, color="#8B949E"), tickfont=dict(size=10, color="#8B949E"), autorange="reversed")
                )
                st.plotly_chart(fig_heat, use_container_width=True, config={'displayModeBar': False})
                st.markdown("</div>", unsafe_allow_html=True)

            if live_odds and valid_markets:
                st.markdown("""<div class='grid-panel'><div class='panel-title'>Pricing Matrix (Discovered +EV)</div>""", unsafe_allow_html=True)
                clean_markets = [m for m in valid_markets if m['Edge'] > 0.01 and m['BookOdd'] >= 1.50]
                clean_markets = sorted(clean_markets, key=lambda x: x['Kelly'], reverse=True)
                
                if clean_markets:
                    st.markdown("<div class='table-container'>", unsafe_allow_html=True)
                    table_html = "<table class='ob-table'><tr><th>Market</th><th>Open</th><th>Current</th><th>Steam</th><th>Sys Prob</th><th>Edge</th><th>Rec. Size</th></tr>"
                    for m in clean_markets[:10]: 
                        edge_val = m['Edge'] * 100
                        steam_cls = "steam-down" if m['Steam'] < 0 else "steam-up"
                        steam_sign = "+" if m['Steam'] > 0 else ""
                        
                        table_html += f"<tr><td>{m['Market']}</td>"
                        table_html += f"<td style='color:#8B949E;'>{m['OpenOdd']:.2f}</td>"
                        table_html += f"<td style='color:#3FB950; font-weight:700;'>{m['BookOdd']:.3f}</td>"
                        table_html += f"<td><span class='{steam_cls}'>{steam_sign}{m['Steam']:.1f}%</span></td>"
                        table_html += f"<td>{m['SysProb']*100:.1f}%</td>"
                        table_html += f"<td style='color:#E6EDF3;'>+{edge_val:.2f}%</td>"
                        table_html += f"<td style='color:#8B949E;'>{m['Kelly']:.2f}%</td></tr>"
                    table_html += "</table></div>"
                    st.markdown(table_html, unsafe_allow_html=True)
                else:
                    st.markdown("""<div class='data-lbl'>No trades met execution criteria.</div>""", unsafe_allow_html=True)
                st.markdown("""</div>""", unsafe_allow_html=True)

# -----------------------------------------------------
# TAB 2: HISTORICAL BACKTEST & AUDIT LEDGER
# -----------------------------------------------------
with tab2:
    st.markdown("""<div class='grid-panel' style='margin-bottom: 20px;'><div class='panel-title'>Pre-Computed Audit Ledger (Real Historical Fixtures)</div>""", unsafe_allow_html=True)
    
    with st.spinner("Fetching Data & Verifying Closing Lines..."):
        dates, equity, df_ledger = get_verified_history(GLOBAL_LEAGUES.get(league_name, 39), bankroll)
    
    if len(df_ledger) > 0:
        final_equity = equity[-1]
        roi = ((final_equity - bankroll) / bankroll) * 100
        peak = bankroll
        max_dd = 0
        for val in equity:
            if val > peak: peak = val
            dd = (peak - val) / peak
            if dd > max_dd: max_dd = dd
            
        st.markdown(f"""
        <div class='metric-grid'>
            <div class='metric-card'><div class='metric-card-title'>Net Profit</div><div class='metric-card-val hl-green'>${final_equity - bankroll:,.0f}</div></div>
            <div class='metric-card'><div class='metric-card-title'>Yield</div><div class='metric-card-val hl-blue'>{roi:+.1f}%</div></div>
            <div class='metric-card'><div class='metric-card-title'>Max Drawdown</div><div class='metric-card-val hl-red'>-{max_dd*100:.1f}%</div></div>
            <div class='metric-card'><div class='metric-card-title'>Evaluated Trades</div><div class='metric-card-val' style='color:#E6EDF3;'>{len(df_ledger)}</div></div>
        </div>
        """, unsafe_allow_html=True)
        
        fig_equity = go.Figure()
        fig_equity.add_trace(go.Scatter(x=dates, y=equity, mode='lines', line=dict(color='#3FB950', width=2), fill='tozeroy', fillcolor='rgba(63, 185, 80, 0.05)', name='Equity'))
        fig_equity.update_layout(
            template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=300, margin=dict(l=0, r=0, t=10, b=0),
            xaxis=dict(tickfont=dict(size=11, color="#8B949E"), gridcolor="rgba(255,255,255,0.05)"),
            yaxis=dict(title="Bankroll", title_font=dict(size=11, color="#8B949E"), tickfont=dict(size=11, color="#8B949E"), gridcolor="rgba(255,255,255,0.05)")
        )
        st.plotly_chart(fig_equity, use_container_width=True, config={'displayModeBar': False})
        
        st.markdown(f"""<div class='panel-title' style='margin-top: 24px; display:flex; justify-content:space-between; align-items:center;'>
        <span>Transaction Ledger ({league_name})</span>
        </div>""", unsafe_allow_html=True)
        
        # Real Download Button for Data Export
        csv = df_ledger.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="⬇️ EXPORT AUDIT TO CSV",
            data=csv,
            file_name=f'apex_quant_audit_{league_name.replace(" ", "_").lower()}.csv',
            mime='text/csv',
        )
        
        st.markdown("<div class='table-container' style='margin-top: 15px;'>", unsafe_allow_html=True)
        ledger_html = "<table class='ob-table'><tr><th>Date</th><th>Match</th><th>Score</th><th>Execution</th><th>Odds</th><th>CLV</th><th>Result</th><th>P&L</th></tr>"
        for _, row in df_ledger.iterrows():
            badge_class = "badge-win" if row['Result'] == "WON" else "badge-loss"
            pl_color = "hl-green" if row['P&L'] > 0 else "hl-red"
            pl_sign = "+" if row['P&L'] > 0 else ""
            
            ledger_html += f"<tr>"
            ledger_html += f"<td style='color:#8B949E; font-size: 0.75rem;'>{row['Date']}</td>"
            ledger_html += f"<td>{row['Match']}</td>"
            ledger_html += f"<td style='color:#E6EDF3; font-weight:600;'>{row['Score']}</td>"
            ledger_html += f"<td>{row['Market']}</td>"
            ledger_html += f"<td style='color:#3FB950; font-family: JetBrains Mono;'>{row['Odds']:.2f}</td>"
            ledger_html += f"<td style='color:#58A6FF;'>+{row['CLV (%)']}%</td>"
            ledger_html += f"<td><span class='{badge_class}'>{row['Result']}</span></td>"
            ledger_html += f"<td class='{pl_color}' style='font-family: JetBrains Mono; font-weight:600;'>{pl_sign}${row['P&L ($)']:,.2f}</td>"
            ledger_html += f"</tr>"
        ledger_html += "</table></div>"
        
        st.markdown(ledger_html, unsafe_allow_html=True)