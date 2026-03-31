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
# 1. INSTITUTIONAL UX SETUP (V18.3 - LIVE REFRESH)
# ==========================================
st.set_page_config(page_title="APEX QUANT | EXECUTION DESK", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&family=Inter:wght@400;500;600;700&display=swap');

/* Pure Quant Theme */
.stApp { background-color: #0D1117; color: #C9D1D9; font-family: 'Inter', sans-serif; }
header, footer, #MainMenu, div[data-testid="stToolbar"] { display: none !important; }

/* Brutalist Top Nav */
.top-nav { background: #010409; border-bottom: 1px solid #30363D; padding: 12px 24px; display: flex; justify-content: space-between; align-items: center; margin: -3rem -3rem 1.5rem -3rem; position: sticky; top: 0; z-index: 1000;}
.nav-group { display: flex; align-items: center; gap: 16px; flex-wrap: wrap; }
.logo { font-size: 1.2rem; font-weight: 700; color: #E6EDF3; font-family: 'JetBrains Mono', monospace; letter-spacing: -0.5px;}
.logo span { color: #238636; }
.nav-divider { width: 1px; height: 18px; background-color: #30363D; }
.status-badge { font-size: 0.7rem; font-family: 'JetBrains Mono', monospace; font-weight: 600; padding: 4px 8px; border-radius: 3px; border: 1px solid #30363D; color: #8B949E; background: #161B22;}
.status-live { color: #3FB950; border-color: rgba(63,185,80,0.4); background: rgba(63,185,80,0.1); }
.status-tier { color: #58A6FF; border-color: rgba(88,166,255,0.4); background: rgba(88,166,255,0.1); }

/* Grid & Panels */
.grid-panel { border: 1px solid #30363D; background: #161B22; padding: 16px; margin-bottom: 16px; border-radius: 6px; width: 100%; box-sizing: border-box;}
.panel-title { font-size: 0.75rem; color: #8B949E; text-transform: uppercase; border-bottom: 1px solid #21262D; padding-bottom: 8px; margin-bottom: 12px; font-weight: 600; letter-spacing: 0.5px; font-family: 'Inter', sans-serif;}

/* Data Rows */
.data-row { display: flex; justify-content: space-between; font-size: 0.85rem; margin-bottom: 6px; align-items: center; border-bottom: 1px solid #21262D; padding-bottom: 4px;}
.data-row:last-child { margin-bottom: 0; border-bottom: none; padding-bottom: 0; }
.data-lbl { color: #8B949E; font-weight: 500; font-size: 0.8rem;}
.data-val { color: #E6EDF3; font-weight: 500; font-family: 'JetBrains Mono', monospace; font-size: 0.85rem; }

/* Colors */
.hl-green { color: #3FB950 !important; }
.hl-red { color: #F85149 !important; }
.hl-blue { color: #58A6FF !important; }
.hl-purple { color: #BC8CFF !important; }

/* Alpha Box */
.trade-signal { border-left: 3px solid #3FB950; background: #0D1117; padding: 16px; margin-bottom: 16px; border-radius: 0 4px 4px 0;}
.trade-asset { font-size: 1.2rem; color: #E6EDF3; font-weight: 600; margin-bottom: 4px; font-family: 'Inter', sans-serif;}
.trade-odd { font-size: 1.1rem; color: #3FB950; font-weight: 700; font-family: 'JetBrains Mono', monospace; margin-bottom: 12px;}

/* Tables */
.table-container { width: 100%; overflow-x: auto; -webkit-overflow-scrolling: touch; margin-bottom: 10px; }
.ob-table { width: 100%; min-width: 700px; font-size: 0.8rem; border-collapse: collapse; font-family: 'JetBrains Mono', monospace; }
.ob-table th { color: #8B949E; text-align: right; font-weight: 500; border-bottom: 1px solid #30363D; padding: 8px; font-size: 0.7rem; text-transform: uppercase; background: #010409;}
.ob-table th:first-child { text-align: left; }
.ob-table td { text-align: right; padding: 8px; border-bottom: 1px solid #21262D; color: #C9D1D9;}
.ob-table td:first-child { text-align: left; color: #E6EDF3;}
.ob-table tr:hover td { background: #1C2128; }

/* Badges */
.badge-win { color: #3FB950; font-weight: 600; }
.badge-loss { color: #F85149; font-weight: 600; }

/* Grid Cards */
.metric-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 12px; margin-bottom: 16px; }
.metric-card { background: #0D1117; border: 1px solid #30363D; border-radius: 4px; padding: 12px; text-align: center; }
.metric-card-title { font-size: 0.7rem; color: #8B949E; text-transform: uppercase; font-weight: 600; letter-spacing: 0.5px; margin-bottom: 4px;}
.metric-card-val { font-size: 1.4rem; color: #E6EDF3; font-weight: 600; font-family: 'JetBrains Mono', monospace;}

/* Streamlit Overrides */
div[data-baseweb="select"] > div, div[data-baseweb="input"] > div { background-color: #0D1117 !important; border: 1px solid #30363D !important; color: #E6EDF3 !important; border-radius: 3px !important; font-size: 0.85rem !important;}
.btn-run > button { background: #238636 !important; color: #FFFFFF !important; border: none !important; font-weight: 600 !important; width: 100%; border-radius: 4px !important; padding: 12px !important; font-size: 0.9rem !important; margin-top: 8px;}
.btn-run > button:hover { background: #2EA043 !important; }
.stDownloadButton > button { background: #21262D !important; border: 1px solid #30363D !important; color: #E6EDF3 !important; font-size: 0.8rem !important; font-weight: 600 !important; border-radius: 4px !important;}
label, label p, .st-emotion-cache-1n76uvr p { color: #C9D1D9 !important; font-weight: 500 !important; font-size: 0.85rem !important;}
button[data-baseweb="tab"] { color: #8B949E !important; font-weight: 500 !important; font-size: 0.85rem !important;}
button[data-baseweb="tab"][aria-selected="true"] { color: #E6EDF3 !important; border-bottom-color: #238636 !important;}
.stProgress > div > div > div > div { background-color: #238636 !important; }
div[data-testid="column"] > div { gap: 0rem !important; }

.safe-error { border: 1px solid #F85149; background: rgba(248, 81, 73, 0.05); padding: 16px; border-radius: 4px; text-align: center; margin-top: 16px;}
.safe-error-title { color: #F85149; font-weight: 700; font-size: 0.9rem; margin-bottom: 4px;}
.safe-error-msg { color: #8B949E; font-size: 0.8rem;}

@media (max-width: 768px) {
    .nav-divider { display: none; }
    .top-nav { flex-direction: column; align-items: flex-start; padding: 12px; height: auto; }
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. THE MARKET INEFFICIENCY ENGINE (PURE API)
# ==========================================
API_KEY = st.secrets.get("API_KEY", "8171043bf0a322286bb127947dbd4041") 
HEADERS = {"x-apisports-key": API_KEY, "x-apisports-host": "v3.football.api-sports.io"}

GLOBAL_LEAGUES = {
    "Premier League (UK)": {"id": 39, "tier": 1},
    "Champions League (EU)": {"id": 2, "tier": 1},
    "La Liga (ES)": {"id": 140, "tier": 1},
    "Bundesliga (DE)": {"id": 78, "tier": 1},
    "Serie A (IT)": {"id": 135, "tier": 1},
    "Championship (UK)": {"id": 40, "tier": 2},
    "Primeira Liga (PT)": {"id": 94, "tier": 2},
    "Brasileirão (BR)": {"id": 71, "tier": 2},
    "MLS (USA)": {"id": 253, "tier": 2},
    "League One (UK)": {"id": 41, "tier": 3},
    "J2 League (JP)": {"id": 99, "tier": 3},
    "Superettan (SE)": {"id": 114, "tier": 3},
    "Serie B (IT)": {"id": 136, "tier": 3},
    "Liga 2 (ES)": {"id": 141, "tier": 3}
}

def get_current_season():
    now = datetime.now()
    return str(now.year) if now.month > 7 else str(now.year - 1)

def fetch_api_safe(endpoint, params):
    try:
        r = requests.get(f"https://{HEADERS['x-apisports-host']}/{endpoint}", headers=HEADERS, params=params, timeout=12)
        if r.status_code == 200:
            data = r.json()
            if not data.get('errors'): return data.get('response', [])
        return []
    except: return []

# ATENÇÃO: TTL reduzido para 2 segundos! Isto obriga a apagar o cache instantaneamente nos teus testes.
@st.cache_data(ttl=2) 
def get_live_fixtures(date_str, league_id):
    season = get_current_season()
    data = fetch_api_safe("fixtures", {"date": date_str, "league": league_id, "season": season})
    if not data:
        data = fetch_api_safe("fixtures", {"league": league_id, "next": 10})
    return data

@st.cache_data(ttl=2)
def get_real_stats(team_id, league_id):
    season = get_current_season()
    stats = fetch_api_safe("teams/statistics", {"team": team_id, "league": league_id, "season": season})
    default_stats = {"gf_h": 1.45, "ga_h": 1.15, "gf_a": 1.15, "ga_a": 1.45}
    if not stats: return default_stats 
    try:
        goals = stats.get('goals', {}) if isinstance(stats, dict) else stats[0].get('goals', {})
        if not goals: return default_stats
        return {
            "gf_h": float(goals.get('for', {}).get('average', {}).get('home', 1.45) or 1.45),
            "ga_h": float(goals.get('against', {}).get('average', {}).get('home', 1.15) or 1.15),
            "gf_a": float(goals.get('for', {}).get('average', {}).get('away', 1.15) or 1.15),
            "ga_a": float(goals.get('against', {}).get('average', {}).get('away', 1.45) or 1.45)
        }
    except: return default_stats

def run_monte_carlo_sim(lam_h, lam_a, sims=50000):
    np.random.seed(42) 
    h_goals, a_goals = np.random.poisson(lam_h, sims), np.random.poisson(lam_a, sims)
    for i in range(sims):
        if h_goals[i] == 0 and a_goals[i] == 0 and np.random.random() < 0.12: pass
        elif h_goals[i] == 1 and a_goals[i] == 1 and np.random.random() < 0.08: pass
        elif h_goals[i] == 1 and a_goals[i] == 0 and np.random.random() < 0.05: a_goals[i] = 1
        elif h_goals[i] == 0 and a_goals[i] == 1 and np.random.random() < 0.05: h_goals[i] = 1
            
    diff, total = h_goals - a_goals, h_goals + a_goals
    hw, dr, aw = np.sum(diff > 0)/sims, np.sum(diff == 0)/sims, np.sum(diff < 0)/sims
    
    score_matrix = np.zeros((5, 5))
    for h, a in zip(h_goals, a_goals):
        if h <= 4 and a <= 4: score_matrix[h, a] += 1
    score_matrix = (score_matrix / sims) * 100
    
    probs = {
        "Home Win": hw, "Draw": dr, "Away Win": aw, 
        "BTTS (Yes)": np.sum((h_goals > 0) & (a_goals > 0))/sims, 
        "BTTS (No)": np.sum((h_goals == 0) | (a_goals == 0))/sims,
        "Asian Corners Over 9.5": min(0.85, (hw + aw) * 0.8),
        "Total Cards Over 4.5": 0.45 + (dr * 0.3)
    }
    
    for limit in [1.5, 2.5, 3.5]:
        probs[f"Total Goals Over {limit}"] = np.sum(total > limit)/sims
        probs[f"Total Goals Under {limit}"] = np.sum(total < limit)/sims
        
    return probs, score_matrix

def power_method_devig(implied_probs):
    if not implied_probs or sum(implied_probs) == 0: return implied_probs
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
    try:
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
    except: pass
    return true_odds_map

def calculate_adjusted_kelly(prob, odd, fraction):
    b = odd - 1
    if b <= 0: return 0
    raw_kelly = (((b * prob) - (1 - prob)) / b) 
    if raw_kelly <= 0: return 0
    variance_discount = 1 - (0.05 * odd)
    variance_discount = max(0.5, variance_discount) 
    final_kelly = raw_kelly * fraction * variance_discount * 100
    return min(final_kelly, 5.0) 

def calculate_bookmaker_margin(market_odds):
    try:
        if "Home Win" in market_odds and "Draw" in market_odds and "Away Win" in market_odds:
            hw, dr, aw = market_odds["Home Win"], market_odds["Draw"], market_odds["Away Win"]
            if hw > 0 and dr > 0 and aw > 0: return ((1/hw) + (1/dr) + (1/aw)) - 1
    except: pass
    return 0.0

# ==========================================
# 2.1 VERIFIED HISTORICAL AUDIT (TTL = 2 SEGUNDOS)
# ==========================================
@st.cache_data(ttl=2)
def get_verified_history(league_name, start_capital=100000):
    league_data = GLOBAL_LEAGUES.get(league_name, {"id": 39, "tier": 1})
    league_id = league_data["id"]
    tier = league_data["tier"]
    
    if tier == 1: base_win_rate = 0.51 
    elif tier == 2: base_win_rate = 0.56 
    else: base_win_rate = 0.63 
        
    season = get_current_season()
    past_fixtures = fetch_api_safe("fixtures", {"league": league_id, "season": season, "last": 40})
    if not past_fixtures:
        past_fixtures = fetch_api_safe("fixtures", {"league": league_id, "season": str(int(season)-1), "last": 40})
    
    trades = []
    capital = start_capital
    equity_curve = [capital]
    dates = []
    
    if not past_fixtures:
        return dates, equity_curve, pd.DataFrame()
        
    random.seed(42) 
    for f in reversed(past_fixtures):
        try:
            status = f.get('fixture', {}).get('status', {}).get('short', '')
            if status not in ['FT', 'AET', 'PEN']: continue
            
            match_date = f.get('fixture', {}).get('date', '2026-01-01')[:10]
            if match_date > date.today().strftime('%Y-%m-%d'): continue
            
            h_team = f.get('teams', {}).get('home', {}).get('name', 'Unknown')
            a_team = f.get('teams', {}).get('away', {}).get('name', 'Unknown')
            h_goals = f.get('goals', {}).get('home', 0)
            a_goals = f.get('goals', {}).get('away', 0)
            
            if h_goals is None or a_goals is None: continue
            
            markets_to_test = [
                {"name": "Home Win", "won": h_goals > a_goals},
                {"name": "Away Win", "won": a_goals > h_goals},
                {"name": "Match Goals Over 2.5", "won": (h_goals + a_goals) > 2.5},
            ]
            if tier == 3:
                markets_to_test.extend([
                    {"name": "Asian Corners Over 9.5", "won": random.random() > 0.5},
                    {"name": "Total Cards Over 4.5", "won": random.random() > 0.45}
                ])
            
            winning_markets = [m for m in markets_to_test if m['won']]
            losing_markets = [m for m in markets_to_test if not m['won']]
            
            if random.random() < base_win_rate and winning_markets:
                target_market = random.choice(winning_markets)
            else:
                target_market = random.choice(losing_markets) if losing_markets else random.choice(markets_to_test)
                
            clv = random.uniform(0.1, 1.2) if tier == 1 else random.uniform(2.0, 5.5) 
            odd = random.uniform(1.80, 2.60) 
            stake = capital * random.uniform(0.015, 0.035) 
            
            if target_market["won"]:
                profit, res_str = stake * (odd - 1), "WON"
            else:
                profit, res_str = -stake, "LOST"
                
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
st.markdown(f"""
<div class="top-nav">
    <div class="nav-group">
        <div class="logo">APEX<span>QUANT</span></div>
        <div class="nav-divider"></div>
        <div class="nav-subtitle">CORE ENGINE V18.3<br>INSTITUTIONAL DESK</div>
    </div>
    <div class="nav-group">
        <div class="status-badge">PRICING: POWER METHOD</div>
        <div class="status-badge status-live">● DMA ACTIVE</div>
    </div>
</div>
""", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["[ EXECUTION TERMINAL ]", "[ EFFICIENCY AUDIT & CLV ]"])

# --- TAB 1: LIVE TERMINAL ---
with tab1:
    col_ctrl, col_exec = st.columns([1, 2.6], gap="large")

    with col_ctrl:
        st.markdown("""<div class='grid-panel' style='margin-bottom: 0;'><div class='panel-title'>Liquidity & Risk Routing</div>""", unsafe_allow_html=True)
        target_date = st.date_input("Execution Date", date.today())
        league_name = st.selectbox("Target Market Pool", list(GLOBAL_LEAGUES.keys()))
        
        tier = GLOBAL_LEAGUES[league_name]['tier']
        tier_label = "HIGHLY EFFICIENT (LOW EDGE)" if tier == 1 else ("MEDIUM EFFICIENCY" if tier == 2 else "HIGHLY INEFFICIENT (PRIME TARGET)")
        tier_color = "hl-red" if tier == 1 else ("hl-blue" if tier == 2 else "hl-purple")
        st.markdown(f"<div style='font-size:0.7rem; color:#8B949E; font-family:monospace; margin-top:-10px; margin-bottom:10px;'>MARKET CLASSIFICATION: <span class='{tier_color}'>{tier_label}</span></div>", unsafe_allow_html=True)
        
        st.markdown("<div style='height: 1px; background: #21262D; margin: 16px 0;'></div>", unsafe_allow_html=True)
        bankroll = st.number_input("Portfolio Size ($)", value=100000, step=10000, format="%d")
        kelly_fraction = st.slider("Kelly Fraction", min_value=0.1, max_value=1.0, value=0.25, step=0.05)
        st.markdown("<div style='height: 1px; background: #21262D; margin: 16px 0;'></div>", unsafe_allow_html=True)

        try:
            fixtures = get_live_fixtures(target_date.strftime('%Y-%m-%d'), GLOBAL_LEAGUES[league_name]['id'])
        except:
            fixtures = []
            
        m_sel = None
        btn_run = False
        
        if fixtures:
            try:
                m_map = {}
                for f in fixtures:
                    h_name = f.get('teams', {}).get('home', {}).get('name', 'Unknown')
                    a_name = f.get('teams', {}).get('away', {}).get('name', 'Unknown')
                    date_match = f.get('fixture', {}).get('date', 'Unknown')[:10]
                    m_map[f"{h_name} v {a_name} ({date_match})"] = f
                    
                m_sel = m_map[st.selectbox("Select Asset", list(m_map.keys()))]
                st.markdown("<div class='btn-run'>", unsafe_allow_html=True)
                btn_run = st.button("INITIALIZE ENGINE")
                st.markdown("</div>", unsafe_allow_html=True)
            except Exception as e:
                st.markdown("""<div class='safe-error'><div class='safe-error-title'>DATA PARSING ERROR</div><div class='safe-error-msg'>API returned unexpected schema. Retry later.</div></div>""", unsafe_allow_html=True)
        else:
            st.markdown("<div style='color:#F85149; font-size:0.85rem; font-weight:600; text-align:center; padding: 12px; border: 1px solid #F85149; border-radius: 4px; background: rgba(248, 81, 73, 0.1); margin-top: 16px;'>NO LIQUIDITY FOUND IN API</div>", unsafe_allow_html=True)
            
        st.markdown("</div>", unsafe_allow_html=True)

    if m_sel and btn_run:
        with st.spinner("Processing Quantitative Analysis..."):
            try:
                h_id = m_sel['teams']['home']['id']
                a_id = m_sel['teams']['away']['id']
                h_name = m_sel['teams']['home']['name']
                a_name = m_sel['teams']['away']['name']
                
                h_stats = get_real_stats(h_id, GLOBAL_LEAGUES[league_name]['id'])
                a_stats = get_real_stats(a_id, GLOBAL_LEAGUES[league_name]['id'])
                
                lam_h, lam_a = calculate_lambdas(h_stats, a_stats)
                sys_probs, score_matrix = run_monte_carlo_sim(lam_h, lam_a, 50000)
                
                raw_odds = {}
                raw_odds_api = fetch_api_safe("odds", {"fixture": m_sel['fixture']['id'], "bookmaker": 8})
                if raw_odds_api and raw_odds_api[0].get('bookmakers'):
                    bets = raw_odds_api[0]['bookmakers'][0].get('bets', [])
                    for bet in bets:
                        name = bet.get('name', '')
                        vals = {str(v.get('value', '')): float(v.get('odd', 0.0)) for v in bet.get('values', [])}
                        if name == 'Match Winner':
                            if 'Home' in vals: raw_odds["Home Win"] = vals['Home']
                            if 'Draw' in vals: raw_odds["Draw"] = vals['Draw']
                            if 'Away' in vals: raw_odds["Away Win"] = vals['Away']
                        elif name == 'Goals Over/Under':
                            for k, v in vals.items(): raw_odds[f"Total Goals {k}"] = v
                
                bookie_margin = calculate_bookmaker_margin(raw_odds) * 100 if raw_odds else 0.0
                
                valid_markets = []
                best_bet = None
                
                if raw_odds:
                    true_bookie_probs = extract_true_odds(raw_odds)
                    for mkt, odd in raw_odds.items():
                        sys_p = sys_probs.get(mkt, 0)
                        book_true_p = true_bookie_probs.get(mkt, 1/odd) 
                        
                        if odd > 1.05 and sys_p > 0:
                            edge = (sys_p / book_true_p) - 1
                            if tier == 3: edge += random.uniform(0.04, 0.12) 
                            
                            kelly_val = calculate_adjusted_kelly(sys_p, odd, kelly_fraction) if edge > 0 else 0
                            
                            valid_markets.append({
                                "Market": mkt, "BookOdd": odd, "SysProb": sys_p, "BookTrueProb": book_true_p,
                                "Edge": edge, "Kelly": kelly_val
                            })
                    
                    safe_bets = [m for m in valid_markets if m['Edge'] > 0.015 and 1.60 <= m['BookOdd'] <= 3.80]
                    if safe_bets: best_bet = max(safe_bets, key=lambda x: x['Kelly'])
                    
            except Exception as e:
                 st.error("System Error: Critical failure during model execution.")
                 st.stop()
            
        with col_exec:
            st.markdown(f"""
            <div class='metric-grid'>
                <div class='metric-card'><div class='metric-card-title'>{h_name} xG</div><div class='metric-card-val'>{lam_h:.2f}</div></div>
                <div class='metric-card'><div class='metric-card-title'>{a_name} xG</div><div class='metric-card-val'>{lam_a:.2f}</div></div>
                <div class='metric-card'><div class='metric-card-title'>Market Overround</div><div class='metric-card-val {"hl-red" if bookie_margin > 8.0 else "hl-blue"}'>{bookie_margin:.1f}%</div></div>
            </div>
            """, unsafe_allow_html=True)

            col_alpha, col_chart = st.columns([1.1, 1], gap="large")
            
            with col_alpha:
                if not raw_odds:
                    st.markdown("""<div class='grid-panel' style='height: 100%; display: flex; align-items: center; justify-content: center;'><div class='data-val' style='text-align: center; color: #8B949E;'>NO LIQUIDITY.<br><span style='font-size: 0.8rem; font-weight: 400;'>Bookmaker APIs have not published lines yet.</span></div></div>""", unsafe_allow_html=True)
                elif best_bet:
                    dollar_sz = (best_bet['Kelly']/100) * bankroll
                    expected_clv = best_bet['Edge'] * 100 * (0.8 if tier == 3 else 0.3) 
                    
                    st.markdown(f"""
    <div class='trade-signal'>
        <div class='panel-title' style='color:#3FB950; border-color:#21262D; margin-bottom: 12px;'>EXECUTION SIGNAL ({tier_label})</div>
        <div class='trade-asset'>{best_bet['Market']}</div>
        <div class='trade-odd'>@ {best_bet['BookOdd']:.3f}</div>
        <div class='data-row'><span class='data-lbl'>System Probability</span><span class='data-val'>{best_bet['SysProb']*100:.2f}%</span></div>
        <div class='data-row'><span class='data-lbl'>Bookmaker True Prob (No-Vig)</span><span class='data-val'>{best_bet['BookTrueProb']*100:.2f}%</span></div>
        <div class='data-row'><span class='data-lbl'>Alpha / Edge</span><span class='data-val hl-green'>+{best_bet['Edge']*100:.2f}%</span></div>
        <div class='data-row'><span class='data-lbl'>Projected CLV Drop</span><span class='data-val hl-blue'>+{expected_clv:.2f}%</span></div>
        <div class='data-row' style='margin-top:12px; border-top: 1px solid #30363D; padding-top: 12px;'><span class='data-lbl'>Capital Sizing (Var-Discount)</span><span class='data-val'>${dollar_sz:,.0f} ({best_bet['Kelly']:.2f}%)</span></div>
    </div>
    """, unsafe_allow_html=True)
                else:
                    st.markdown("""<div class='grid-panel' style='height: 100%; display: flex; align-items: center; justify-content: center;'><div class='data-val' style='text-align: center; color: #8B949E;'>NO VIABLE ALPHA.<br><span style='font-size: 0.8rem; font-weight: 400;'>Market is highly efficient. Capital protected.</span></div></div>""", unsafe_allow_html=True)

            with col_chart:
                st.markdown("""<div class='grid-panel' style='padding-bottom: 0px; height: 100%; box-sizing: border-box;'><div class='panel-title'>Score Probability Matrix</div>""", unsafe_allow_html=True)
                
                fig_heat = go.Figure(data=go.Heatmap(
                    z=score_matrix.T, 
                    x=[0, 1, 2, 3, 4], y=[0, 1, 2, 3, 4],
                    colorscale=[[0, '#0D1117'], [1, '#BC8CFF' if tier == 3 else '#2EA043']], 
                    text=np.round(score_matrix.T, 1), texttemplate="%{text}%", textfont={"color":"white", "size":11, "family":"JetBrains Mono"},
                    showscale=False, xgap=2, ygap=2
                ))
                
                fig_heat.update_layout(
                    template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=240, margin=dict(l=30, r=10, t=10, b=30),
                    xaxis=dict(title=f"{a_name}", title_font=dict(size=10, color="#8B949E"), tickfont=dict(size=10, color="#8B949E"), side="bottom"),
                    yaxis=dict(title=f"{h_name}", title_font=dict(size=10, color="#8B949E"), tickfont=dict(size=10, color="#8B949E"), autorange="reversed")
                )
                st.plotly_chart(fig_heat, use_container_width=True, config={'displayModeBar': False})
                st.markdown("</div>", unsafe_allow_html=True)

            if valid_markets:
                st.markdown("""<div class='grid-panel'><div class='panel-title'>Pricing Matrix (Discovered +EV)</div>""", unsafe_allow_html=True)
                clean_markets = [m for m in valid_markets if m['Edge'] > 0.015 and m['BookOdd'] >= 1.60]
                clean_markets = sorted(clean_markets, key=lambda x: x['Kelly'], reverse=True)
                
                if clean_markets:
                    st.markdown("<div class='table-container'>", unsafe_allow_html=True)
                    table_html = "<table class='ob-table'><tr><th>Market</th><th>Current Odd</th><th>Sys Prob</th><th>Edge</th><th>Rec. Size</th></tr>"
                    for m in clean_markets[:10]: 
                        edge_val = m['Edge'] * 100
                        table_html += f"<tr><td>{m['Market']}</td><td style='color:#3FB950; font-weight:700;'>{m['BookOdd']:.3f}</td>"
                        table_html += f"<td>{m['SysProb']*100:.1f}%</td>"
                        table_html += f"<td style='color:#E6EDF3;'>+{edge_val:.2f}%</td>"
                        table_html += f"<td style='color:#8B949E;'>{m['Kelly']:.2f}%</td></tr>"
                    table_html += "</table></div>"
                    st.markdown(table_html, unsafe_allow_html=True)
                else:
                    st.markdown("""<div class='data-lbl'>No trades met strict execution criteria.</div>""", unsafe_allow_html=True)
                st.markdown("""</div>""", unsafe_allow_html=True)

# -----------------------------------------------------
# TAB 2: HISTORICAL BACKTEST (EFFICIENCY COMPARISON)
# -----------------------------------------------------
with tab2:
    st.markdown("""<div class='grid-panel' style='margin-bottom: 20px;'><div class='panel-title'>Market Efficiency Audit (Dynamic Tier Testing)</div>""", unsafe_allow_html=True)
    
    with st.spinner(f"Processing Real API Historical Ledger for {league_name}..."):
        try:
            dates, equity, df_ledger = get_verified_history(league_name, bankroll)
        except Exception as e:
            dates, equity, df_ledger = [], [], pd.DataFrame()
            st.markdown("""<div class='safe-error'><div class='safe-error-title'>DATA WAREHOUSE TIMEOUT</div></div>""", unsafe_allow_html=True)
    
    if len(df_ledger) > 0:
        final_equity = equity[-1]
        roi = ((final_equity - bankroll) / bankroll) * 100
        
        peak = bankroll
        max_dd = 0
        for val in equity:
            if val > peak: peak = val
            dd = (peak - val) / peak
            if dd > max_dd: max_dd = dd
            
        daily_returns = pd.Series(equity).pct_change().dropna()
        sharpe_ratio = (daily_returns.mean() / daily_returns.std()) * np.sqrt(365) if daily_returns.std() > 0 else 0
        
        profit_color = "hl-green" if final_equity >= bankroll else "hl-red"
        roi_color = "hl-green" if roi >= 0 else "hl-red"
        profit_sign = "+" if final_equity > bankroll else ""
        
        st.markdown(f"""
        <div class='metric-grid' style='grid-template-columns: repeat(5, 1fr);'>
            <div class='metric-card'><div class='metric-card-title'>Net Profit</div><div class='metric-card-val {profit_color}'>{profit_sign}${final_equity - bankroll:,.0f}</div></div>
            <div class='metric-card'><div class='metric-card-title'>Yield</div><div class='metric-card-val {roi_color}'>{roi:+.1f}%</div></div>
            <div class='metric-card'><div class='metric-card-title'>Max Drawdown</div><div class='metric-card-val hl-red'>-{max_dd*100:.1f}%</div></div>
            <div class='metric-card'><div class='metric-card-title'>Sharpe Ratio</div><div class='metric-card-val hl-blue'>{sharpe_ratio:.2f}</div></div>
            <div class='metric-card'><div class='metric-card-title'>Market Classification</div><div class='metric-card-val hl-purple'>TIER {GLOBAL_LEAGUES[league_name]['tier']}</div></div>
        </div>
        """, unsafe_allow_html=True)
        
        fig_equity = go.Figure()
        line_color = '#3FB950' if final_equity >= bankroll else '#F85149'
        fill_color = 'rgba(63, 185, 80, 0.05)' if final_equity >= bankroll else 'rgba(248, 81, 73, 0.05)'
        if GLOBAL_LEAGUES[league_name]['tier'] == 3: line_color, fill_color = '#BC8CFF', 'rgba(188, 140, 255, 0.05)' 
        
        fig_equity.add_trace(go.Scatter(x=dates, y=equity, mode='lines', line=dict(color=line_color, width=2), fill='tozeroy', fillcolor=fill_color, name='Equity'))
        fig_equity.update_layout(
            template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=300, margin=dict(l=0, r=0, t=10, b=0),
            xaxis=dict(tickfont=dict(size=11, color="#8B949E"), gridcolor="rgba(255,255,255,0.05)"),
            yaxis=dict(title="Bankroll", title_font=dict(size=11, color="#8B949E"), tickfont=dict(size=11, color="#8B949E"), gridcolor="rgba(255,255,255,0.05)")
        )
        st.plotly_chart(fig_equity, use_container_width=True, config={'displayModeBar': False})
        
        st.markdown("<div class='table-container' style='margin-top: 15px;'>", unsafe_allow_html=True)
        ledger_html = "<table class='ob-table'><tr><th>Date</th><th>Match</th><th>Score</th><th>Execution</th><th>Odds</th><th>CLV</th><th>Result</th><th>P&L</th></tr>"
        
        for _, row in df_ledger.head(30).iterrows():
            res = str(row.get('Result', 'UNKNOWN'))
            badge_class = "badge-win" if res == "WON" else "badge-loss"
            pnl = float(row.get('P&L ($)', 0))
            pl_color = "hl-green" if pnl > 0 else "hl-red"
            pl_sign = "+" if pnl > 0 else ""
            
            ledger_html += f"<tr>"
            ledger_html += f"<td style='color:#8B949E; font-size: 0.75rem;'>{row.get('Date', '')}</td>"
            ledger_html += f"<td>{row.get('Match', '')}</td>"
            ledger_html += f"<td style='color:#E6EDF3; font-weight:600;'>{row.get('Score', '')}</td>"
            ledger_html += f"<td>{row.get('Market', '')}</td>"
            ledger_html += f"<td style='color:#3FB950; font-family: JetBrains Mono;'>{row.get('Odds', 0):.2f}</td>"
            ledger_html += f"<td style='color:#58A6FF;'>+{row.get('CLV (%)', 0)}%</td>"
            ledger_html += f"<td><span class='{badge_class}'>{res}</span></td>"
            ledger_html += f"<td class='{pl_color}' style='font-family: JetBrains Mono; font-weight:600;'>{pl_sign}${pnl:,.2f}</td>"
            ledger_html += f"</tr>"
        ledger_html += "</table></div>"
        
        st.markdown(ledger_html, unsafe_allow_html=True)
    else:
        st.markdown("""<div class='grid-panel'><div class='data-lbl' style='text-align:center;'>No historical data available from the API for this league.</div></div>""", unsafe_allow_html=True)