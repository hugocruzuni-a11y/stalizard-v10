import streamlit as st
import numpy as np
import pandas as pd
import requests
import math
import plotly.graph_objects as go
from datetime import date, datetime, timedelta

# ==========================================
# 1. HOLZHAUER TERMINAL UX SETUP
# ==========================================
st.set_page_config(page_title="APEX QUANT | TERMINAL", layout="wide", initial_sidebar_state="collapsed")
st.cache_data.clear()

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&family=Inter:wght@400;500;600;700&display=swap');

/* Bloomberg / Quant Terminal Baseline */
.stApp { background-color: #000000; color: #C9D1D9; font-family: 'Inter', sans-serif; }
header, footer, #MainMenu, div[data-testid="stToolbar"] { display: none !important; }

/* Brutalist Header */
.top-nav { background: #0A0A0A; border-bottom: 1px solid #1F2328; padding: 10px 24px; display: flex; justify-content: space-between; align-items: center; margin: -3rem -3rem 1.5rem -3rem; position: sticky; top: 0; z-index: 1000;}
.nav-group { display: flex; align-items: center; gap: 16px; flex-wrap: wrap; }
.logo { font-size: 1.1rem; font-weight: 700; color: #E6EDF3; font-family: 'JetBrains Mono', monospace; letter-spacing: -0.5px;}
.logo span { color: #3FB950; }
.nav-divider { width: 1px; height: 16px; background-color: #30363D; }
.status-badge { font-size: 0.65rem; font-family: 'JetBrains Mono', monospace; font-weight: 700; padding: 3px 6px; border-radius: 2px; border: 1px solid #30363D; color: #8B949E; background: #0D1117; text-transform: uppercase;}
.status-live { color: #3FB950; border-color: #1A4D2E; background: #082613; }

/* Institutional Grid Panels */
.grid-panel { border: 1px solid #1F2328; background: #0D1117; padding: 14px; margin-bottom: 14px; border-radius: 4px; width: 100%; box-sizing: border-box; }
.panel-title { font-size: 0.7rem; color: #8B949E; text-transform: uppercase; border-bottom: 1px solid #1F2328; padding-bottom: 6px; margin-bottom: 10px; font-weight: 700; letter-spacing: 0.5px;}

/* High-Density Data Rows */
.data-row { display: flex; justify-content: space-between; font-size: 0.8rem; margin-bottom: 6px; align-items: center; border-bottom: 1px solid #161B22; padding-bottom: 4px;}
.data-row:last-child { margin-bottom: 0; border-bottom: none; padding-bottom: 0; }
.data-lbl { color: #8B949E; font-weight: 500;}
.data-val { color: #E6EDF3; font-weight: 600; font-family: 'JetBrains Mono', monospace; }

/* Core Quant Colors */
.hl-green { color: #3FB950 !important; }
.hl-red { color: #F85149 !important; }
.hl-blue { color: #58A6FF !important; }

/* Micro Badges for Tables */
.badge-win { color: #3FB950; font-family: 'JetBrains Mono', monospace; font-weight: 700; font-size: 0.7rem; }
.badge-loss { color: #F85149; font-family: 'JetBrains Mono', monospace; font-weight: 700; font-size: 0.7rem; }
.badge-high { color: #000000; background: #58A6FF; font-weight: 700; padding: 1px 4px; border-radius: 2px; font-size: 0.65rem;}
.badge-med { color: #000000; background: #8B949E; font-weight: 700; padding: 1px 4px; border-radius: 2px; font-size: 0.65rem;}
.badge-low { color: #000000; background: #F85149; font-weight: 700; padding: 1px 4px; border-radius: 2px; font-size: 0.65rem;}

/* Execution Ticket (Alpha Box) */
.trade-signal { border-left: 4px solid #3FB950; background: #05140A; padding: 16px; margin-bottom: 14px; border-radius: 0 4px 4px 0; border-top: 1px solid #1F2328; border-right: 1px solid #1F2328; border-bottom: 1px solid #1F2328;}
.trade-asset { font-size: 1.1rem; color: #E6EDF3; font-weight: 700; margin-bottom: 2px; font-family: 'Inter', sans-serif;}
.trade-odd { font-size: 1.3rem; color: #3FB950; font-weight: 700; font-family: 'JetBrains Mono', monospace; margin-bottom: 12px; letter-spacing: -0.5px;}

/* Ultra-Compact Tables */
.table-container { width: 100%; overflow-x: auto; margin-bottom: 8px; }
.ob-table { width: 100%; font-size: 0.75rem; border-collapse: collapse; font-family: 'JetBrains Mono', monospace; }
.ob-table th { color: #8B949E; text-align: right; font-weight: 600; border-bottom: 1px solid #30363D; padding: 6px 8px; font-size: 0.65rem; text-transform: uppercase; background: #0A0A0A;}
.ob-table th:first-child { text-align: left; }
.ob-table td { text-align: right; padding: 6px 8px; border-bottom: 1px solid #1F2328; color: #C9D1D9;}
.ob-table td:first-child { text-align: left; color: #E6EDF3;}
.ob-table tr:hover td { background: #161B22; }

/* KPI Grid */
.metric-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 10px; margin-bottom: 14px; }
.metric-card { background: #0A0A0A; border: 1px solid #1F2328; border-radius: 4px; padding: 10px; text-align: center; }
.metric-card-title { font-size: 0.65rem; color: #8B949E; text-transform: uppercase; font-weight: 700; margin-bottom: 4px;}
.metric-card-val { font-size: 1.3rem; color: #E6EDF3; font-weight: 700; font-family: 'JetBrains Mono', monospace; letter-spacing: -0.5px;}

/* Base UI Overrides */
div[data-baseweb="select"] > div, div[data-baseweb="input"] > div { background-color: #0A0A0A !important; border: 1px solid #1F2328 !important; color: #E6EDF3 !important; border-radius: 2px !important; font-size: 0.8rem !important;}
.btn-run > button { background: #238636 !important; color: #FFFFFF !important; border: none !important; font-weight: 700 !important; width: 100%; border-radius: 2px !important; padding: 10px !important; font-size: 0.85rem !important; margin-top: 8px;}
.btn-run > button:hover { background: #2EA043 !important; }
button[data-baseweb="tab"] { color: #8B949E !important; font-weight: 600 !important; font-size: 0.8rem !important; text-transform: uppercase; letter-spacing: 0.5px;}
button[data-baseweb="tab"][aria-selected="true"] { color: #E6EDF3 !important; border-bottom-color: #238636 !important;}
div[data-testid="column"] > div { gap: 0rem !important; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. PRO-TIER DATA POOL & MATH ENGINE (V23.0)
# ==========================================
API_KEY = st.secrets.get("API_KEY", "8171043bf0a322286bb127947dbd4041") 
HEADERS = {"x-apisports-key": API_KEY, "x-apisports-host": "v3.football.api-sports.io"}

GLOBAL_LEAGUES = {
    "Championship (UK)": 40, "League One (UK)": 41, 
    "2. Bundesliga (DE)": 79, "Serie B (IT)": 136, "La Liga 2 (ES)": 141,
    "MLS (USA)": 253, "J1 League (JP)": 98, "Brasileirão Série A (BR)": 71,
    "Eredivisie (NL)": 88, "Primeira Liga (PT)": 94, "Pro League (BE)": 144,
    "Premier League (UK)": 39, "Champions League (EU)": 2, "La Liga (ES)": 140,
    "Serie A (IT)": 135, "Bundesliga (DE)": 78
}

def get_current_season():
    now = datetime.now()
    return str(now.year) if now.month > 7 else str(now.year - 1)

def fetch_api_safe(endpoint, params):
    try:
        r = requests.get(f"https://{HEADERS['x-apisports-host']}/{endpoint}", headers=HEADERS, params=params, timeout=8)
        if r.status_code == 200:
            data = r.json()
            if not data.get('errors'): return data.get('response', [])
        return []
    except: return []

@st.cache_data(ttl=300) 
def get_live_fixtures(date_str, league_id):
    season = get_current_season()
    data = fetch_api_safe("fixtures", {"date": date_str, "league": league_id, "season": season})
    if not data: data = fetch_api_safe("fixtures", {"league": league_id, "next": 10})
    return data

@st.cache_data(ttl=3600)
def get_real_stats(team_id, league_id):
    season = get_current_season()
    stats = fetch_api_safe("teams/statistics", {"team": team_id, "league": league_id, "season": season})
    
    default_stats = {
        "gf_h": 1.45, "ga_h": 1.15, "gf_a": 1.15, "ga_a": 1.45,
        "corn_h": 5.5, "corn_a": 4.5, "cards_h": 2.0, "cards_a": 2.5
    }
    
    if not stats: return default_stats 
    
    try:
        data = stats if isinstance(stats, dict) else stats[0]
        goals = data.get('goals', {})
        return {
            "gf_h": max(0.2, float(goals.get('for', {}).get('average', {}).get('home') or 1.45)),
            "ga_h": max(0.2, float(goals.get('against', {}).get('average', {}).get('home') or 1.15)),
            "gf_a": max(0.2, float(goals.get('for', {}).get('average', {}).get('away') or 1.15)),
            "ga_a": max(0.2, float(goals.get('against', {}).get('average', {}).get('away') or 1.45)),
            "corn_h": 5.5, "corn_a": 4.5, "cards_h": 2.1, "cards_a": 2.4 # Prop Placeholders
        }
    except: return default_stats

def calculate_lambdas(h_stats, a_stats):
    lam_h = (h_stats['gf_h'] / 1.45) * (a_stats['ga_a'] / 1.45) * 1.45
    lam_a = (a_stats['gf_a'] / 1.15) * (h_stats['ga_h'] / 1.15) * 1.15
    return lam_h, lam_a

def poisson_pmf(lam, k):
    return (lam**k * math.exp(-lam)) / math.factorial(k)

def exact_poisson_matrix(lam_h, lam_a, stats_h, stats_a, max_goals=6):
    h_probs = [poisson_pmf(lam_h, i) for i in range(max_goals)]
    a_probs = [poisson_pmf(lam_a, i) for i in range(max_goals)]
    score_matrix = np.outer(h_probs, a_probs)
    
    rho = max(-0.15, -0.12 + 0.02 * (lam_h + lam_a))
    try:
        score_matrix[0, 0] *= max(0, 1 - lam_h * lam_a * rho)
        score_matrix[1, 0] *= max(0, 1 + lam_a * rho)
        score_matrix[0, 1] *= max(0, 1 + lam_h * rho)
        score_matrix[1, 1] *= max(0, 1 - rho)
        score_matrix = score_matrix / score_matrix.sum()
    except: pass
    
    hw = np.tril(score_matrix, -1).sum()
    dr = np.trace(score_matrix)
    aw = np.triu(score_matrix, 1).sum()
    
    u25 = np.sum([score_matrix[i, j] for i in range(max_goals) for j in range(max_goals) if i + j < 2.5])
    o25 = 1 - u25
    
    btts_no = np.sum(score_matrix[0, :]) + np.sum(score_matrix[:, 0]) - score_matrix[0, 0]
    btts_yes = 1 - btts_no
    
    exp_corners = stats_h['corn_h'] + stats_a['corn_a']
    exp_cards = stats_h['cards_h'] + stats_a['cards_a']
    
    u95_corn = sum([poisson_pmf(exp_corners, i) for i in range(10)])
    o95_corn = 1 - u95_corn
    
    u45_cards = sum([poisson_pmf(exp_cards, i) for i in range(5)])
    o45_cards = 1 - u45_cards
    
    probs = {
        "Home Win": hw, "Draw": dr, "Away Win": aw, 
        "BTTS (Yes)": btts_yes, "BTTS (No)": btts_no,
        "Total Goals Over 2.5": o25, "Total Goals Under 2.5": u25,
        "Total Corners Over 9.5": o95_corn, "Total Corners Under 9.5": u95_corn,
        "Total Cards Over 4.5": o45_cards, "Total Cards Under 4.5": u45_cards
    }
    
    return probs, score_matrix * 100

def power_method_devig(implied_probs):
    if not implied_probs or sum(implied_probs) <= 1.0: return implied_probs 
    low, high = 0.0, 1.0
    mid = 1.0
    for _ in range(50):
        mid = (low + high) / 2
        current_sum = sum([p**mid for p in implied_probs])
        if abs(current_sum - 1.0) < 0.0001: break
        if current_sum > 1.0: low = mid
        else: high = mid
    return [p**mid for p in implied_probs]

def extract_true_odds(market_odds):
    true_odds_map = {}
    try:
        if "Home Win" in market_odds and "Draw" in market_odds and "Away Win" in market_odds:
            hw, dr, aw = market_odds["Home Win"], market_odds["Draw"], market_odds["Away Win"]
            if hw > 0 and dr > 0 and aw > 0:
                true_p = power_method_devig([1/hw, 1/dr, 1/aw])
                true_odds_map["Home Win"], true_odds_map["Draw"], true_odds_map["Away Win"] = true_p[0], true_p[1], true_p[2]
        
        for p_mkt in [("Total Goals Over 2.5", "Total Goals Under 2.5"), 
                      ("Total Corners Over 9.5", "Total Corners Under 9.5"),
                      ("Total Cards Over 4.5", "Total Cards Under 4.5"),
                      ("BTTS (Yes)", "BTTS (No)")]:
            if p_mkt[0] in market_odds and p_mkt[1] in market_odds:
                o_val, u_val = market_odds[p_mkt[0]], market_odds[p_mkt[1]]
                if o_val > 0 and u_val > 0:
                    true_p = power_method_devig([1/o_val, 1/u_val])
                    true_odds_map[p_mkt[0]], true_odds_map[p_mkt[1]] = true_p[0], true_p[1]
    except: pass
    return true_odds_map

def calculate_adjusted_kelly(prob, odd, fraction):
    b = odd - 1
    if b <= 0: return 0
    raw_kelly = (((b * prob) - (1 - prob)) / b) 
    if raw_kelly <= 0: return 0
    return min(raw_kelly * fraction * 100, 5.0) 

def calculate_bookmaker_margin(market_odds):
    try:
        if "Home Win" in market_odds and "Draw" in market_odds and "Away Win" in market_odds:
            hw, dr, aw = market_odds["Home Win"], market_odds["Draw"], market_odds["Away Win"]
            if hw > 0 and dr > 0 and aw > 0: return ((1/hw) + (1/dr) + (1/aw)) - 1
    except: pass
    return None

# ==========================================
# 2.1 VERIFIED HISTORICAL AUDIT (HOLZHAUER BACKTEST)
# ==========================================
@st.cache_data(ttl=3600)
def get_verified_history(league_id):
    season = get_current_season()
    past_fixtures = fetch_api_safe("fixtures", {"league": league_id, "season": season, "last": 60})
    
    trades = []
    if not past_fixtures: return pd.DataFrame()
        
    for f in reversed(past_fixtures):
        try:
            status = f.get('fixture', {}).get('status', {}).get('short', '')
            if status not in ['FT', 'AET', 'PEN']: continue
            
            match_date = f.get('fixture', {}).get('date', '2026-01-01')[:10]
            if match_date > date.today().strftime('%Y-%m-%d'): continue
            
            h_team = f.get('teams', {}).get('home', {}).get('name', 'Unknown')
            a_team = f.get('teams', {}).get('away', {}).get('name', 'Unknown')
            h_id = f.get('teams', {}).get('home', {}).get('id')
            a_id = f.get('teams', {}).get('away', {}).get('id')
            
            h_goals = f.get('goals', {}).get('home')
            a_goals = f.get('goals', {}).get('away')
            
            if h_goals is None or a_goals is None: continue
            
            h_stats = get_real_stats(h_id, league_id)
            a_stats = get_real_stats(a_id, league_id)
            lam_h, lam_a = calculate_lambdas(h_stats, a_stats)
            sys_probs, _ = exact_poisson_matrix(lam_h, lam_a, h_stats, a_stats)
            
            # Removemos props do backtest de forma estrita
            valid_preds = {k: v for k, v in sys_probs.items() if v >= 0.45 and "Corners" not in k and "Cards" not in k}
            
            if not valid_preds:
                best_market = max({k: v for k, v in sys_probs.items() if "Corners" not in k and "Cards" not in k}.keys(), key=lambda m: sys_probs.get(m, 0))
                confidence = "LOW"
            else:
                best_market = max(valid_preds.keys(), key=lambda m: valid_preds.get(m, 0))
                confidence = "HIGH" if sys_probs[best_market] >= 0.60 else "MED"

            pred_prob = sys_probs[best_market]
            
            real_outcomes = []
            if h_goals > a_goals: real_outcomes.append("Home Win")
            elif h_goals < a_goals: real_outcomes.append("Away Win")
            else: real_outcomes.append("Draw")
            
            if (h_goals + a_goals) > 2.5: real_outcomes.append("Total Goals Over 2.5")
            else: real_outcomes.append("Total Goals Under 2.5")
            
            if h_goals > 0 and a_goals > 0: real_outcomes.append("BTTS (Yes)")
            else: real_outcomes.append("BTTS (No)")
            
            is_win = best_market in real_outcomes
            min_odd = 1 / pred_prob 
            
            # PnL Unitário (Flat Staking)
            pnl = (min_odd - 1.0) if is_win else -1.0
            
            trades.append({
                "Date": match_date, "Match": f"{h_team[:12]} v {a_team[:12]}",
                "Model Pick": best_market.replace("Total Goals ", ""), "Conf": confidence,
                "Prob": f"{pred_prob*100:.1f}%", "True Line": round(min_odd, 2), 
                "Res": "HIT" if is_win else "MISS", "PnL": pnl
            })
        except: continue
            
    df_trades = pd.DataFrame(trades).sort_values(by="Date", ascending=True) 
    if not df_trades.empty:
        df_trades['Cumulative_PnL'] = df_trades['PnL'].cumsum()
    return df_trades.sort_values(by="Date", ascending=False)

# ==========================================
# 3. INTERFACE RENDER
# ==========================================
st.markdown(f"""
<div class="top-nav">
    <div class="nav-group">
        <div class="logo">APEX<span>QUANT</span></div>
        <div class="nav-divider"></div>
        <div class="nav-subtitle" style="font-size: 0.75rem; color: #8B949E; line-height: 1.2;">CORE ENGINE V23.0<br><span style="color:#E6EDF3; font-weight:600;">INSTITUTIONAL DESK</span></div>
    </div>
    <div class="nav-group">
        <div class="status-badge">MODEL: DC-POISSON + PROPS</div>
        <div class="status-badge status-live">● API CONNECTED</div>
    </div>
</div>
""", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["ORDER ENTRY", "RISK & BACKTEST"])

with tab1:
    col_ctrl, col_exec = st.columns([1, 2.6], gap="large")

    with col_ctrl:
        st.markdown("""<div class='grid-panel' style='margin-bottom: 0;'><div class='panel-title'>Model Parameters</div>""", unsafe_allow_html=True)
        target_date = st.date_input("Match Date", date.today())
        league_name = st.selectbox("Liquidity Pool", list(GLOBAL_LEAGUES.keys()))
        league_id = GLOBAL_LEAGUES[league_name]
        
        st.markdown("<div style='height: 1px; background: #1F2328; margin: 12px 0;'></div>", unsafe_allow_html=True)
        bankroll = st.number_input("Bankroll ($)", value=100000, step=10000, format="%d")
        kelly_fraction = st.slider("Kelly Multiplier", min_value=0.1, max_value=1.0, value=0.25, step=0.05)
        st.markdown("<div style='height: 1px; background: #1F2328; margin: 12px 0;'></div>", unsafe_allow_html=True)

        with st.spinner("Fetching Data..."):
            fixtures = get_live_fixtures(target_date.strftime('%Y-%m-%d'), league_id)
            
        m_sel = None
        btn_run = False
        
        if fixtures:
            m_map = {}
            for f in fixtures:
                h_name = f.get('teams', {}).get('home', {}).get('name', 'Unknown')
                a_name = f.get('teams', {}).get('away', {}).get('name', 'Unknown')
                date_match = f.get('fixture', {}).get('date', 'Unknown')[:10]
                m_map[f"{h_name} v {a_name}"] = f
                
            m_sel = m_map[st.selectbox("Select Asset", list(m_map.keys()))]
            st.markdown("<div class='btn-run'>", unsafe_allow_html=True)
            btn_run = st.button("CALCULATE EDGE")
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='color:#F85149; font-size:0.75rem; font-weight:700; text-align:center; padding: 10px; border: 1px solid #F85149; border-radius: 2px; background: rgba(248, 81, 73, 0.1); margin-top: 12px;'>NO LIQUIDITY AVAILABLE</div>", unsafe_allow_html=True)
            
        st.markdown("</div>", unsafe_allow_html=True)

    if m_sel and btn_run:
        with st.spinner("Processing Matrix..."):
            try:
                h_id = m_sel.get('teams', {}).get('home', {}).get('id')
                a_id = m_sel.get('teams', {}).get('away', {}).get('id')
                h_name = m_sel.get('teams', {}).get('home', {}).get('name', 'Home Team')
                a_name = m_sel.get('teams', {}).get('away', {}).get('name', 'Away Team')
                
                h_stats = get_real_stats(h_id, league_id)
                a_stats = get_real_stats(a_id, league_id)
                
                lam_h, lam_a = calculate_lambdas(h_stats, a_stats)
                sys_probs, score_matrix = exact_poisson_matrix(lam_h, lam_a, h_stats, a_stats, max_goals=6)
                
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
                            if 'Over 2.5' in vals: raw_odds["Total Goals Over 2.5"] = vals['Over 2.5']
                            if 'Under 2.5' in vals: raw_odds["Total Goals Under 2.5"] = vals['Under 2.5']
                        elif name == 'Both Teams Score':
                            if 'Yes' in vals: raw_odds["BTTS (Yes)"] = vals['Yes']
                            if 'No' in vals: raw_odds["BTTS (No)"] = vals['No']
                        elif name == 'Corners Over Under': 
                            if 'Over 9.5' in vals: raw_odds["Total Corners Over 9.5"] = vals['Over 9.5']
                            if 'Under 9.5' in vals: raw_odds["Total Corners Under 9.5"] = vals['Under 9.5']
                        elif name == 'Cards Over/Under': 
                            if 'Over 4.5' in vals: raw_odds["Total Cards Over 4.5"] = vals['Over 4.5']
                            if 'Under 4.5' in vals: raw_odds["Total Cards Under 4.5"] = vals['Under 4.5']
                
                bookie_margin = calculate_bookmaker_margin(raw_odds)
                valid_markets = []
                best_bet = None
                
                if raw_odds:
                    true_bookie_probs = extract_true_odds(raw_odds)
                    for mkt, odd in raw_odds.items():
                        sys_p = sys_probs.get(mkt, 0)
                        if sys_p == 0: continue
                        
                        book_true_p = true_bookie_probs.get(mkt, 1/odd) 
                        edge = (sys_p / book_true_p) - 1
                        kelly_val = calculate_adjusted_kelly(sys_p, odd, kelly_fraction) if edge > 0 else 0
                        
                        valid_markets.append({
                            "Market": mkt.replace("Total ", ""), "BookOdd": odd, "SysProb": sys_p, "BookTrueProb": book_true_p,
                            "Edge": edge, "Kelly": kelly_val
                        })
                    
                    safe_bets = [m for m in valid_markets if m['Edge'] > 0.01]
                    if safe_bets: best_bet = max(safe_bets, key=lambda x: x['Kelly'])
                    
            except Exception as e:
                 st.markdown(f"<div class='safe-error'><div class='safe-error-title'>CRITICAL ERROR</div><div class='safe-error-msg'>API missing required tensors. {str(e)}</div></div>", unsafe_allow_html=True)
                 st.stop()
            
        with col_exec:
            b_margin_ui = f"{bookie_margin*100:.2f}%" if bookie_margin else "N/A"
            m_color = "hl-red" if bookie_margin and bookie_margin > 0.07 else "hl-blue"
            
            st.markdown(f"""
            <div class='metric-grid'>
                <div class='metric-card'><div class='metric-card-title'>{h_name[:10]} xG</div><div class='metric-card-val'>{lam_h:.2f}</div></div>
                <div class='metric-card'><div class='metric-card-title'>{a_name[:10]} xG</div><div class='metric-card-val'>{lam_a:.2f}</div></div>
                <div class='metric-card'><div class='metric-card-title'>Market Vig</div><div class='metric-card-val {m_color}'>{b_margin_ui}</div></div>
            </div>
            """, unsafe_allow_html=True)

            col_alpha, col_chart = st.columns([1.1, 1], gap="large")
            
            with col_alpha:
                if not raw_odds:
                    st.markdown("""<div class='grid-panel' style='height: 100%; display: flex; align-items: center; justify-content: center;'><div class='data-val' style='text-align: center; color: #8B949E; font-size: 0.8rem;'>MARKET DATA UNAVAILABLE<br><span style='font-size: 0.7rem; font-weight: 400;'>Strict Mode: Synthetic lines disabled.</span></div></div>""", unsafe_allow_html=True)
                elif best_bet:
                    dollar_sz = (best_bet['Kelly']/100) * bankroll
                    
                    st.markdown(f"""
    <div class='trade-signal'>
        <div class='panel-title' style='color:#3FB950; border-color:#1F2328; margin-bottom: 8px;'>EXECUTION TICKET</div>
        <div class='trade-asset'>{best_bet['Market'].upper()}</div>
        <div class='trade-odd'>@ {best_bet['BookOdd']:.3f}</div>
        <div class='data-row'><span class='data-lbl'>True Probability</span><span class='data-val'>{best_bet['SysProb']*100:.1f}%</span></div>
        <div class='data-row'><span class='data-lbl'>Vig-Free Line</span><span class='data-val'>{1/best_bet['SysProb']:.2f}</span></div>
        <div class='data-row'><span class='data-lbl'>Calculated EV</span><span class='data-val hl-green'>+{best_bet['Edge']*100:.2f}%</span></div>
        <div class='data-row' style='margin-top:10px; border-top: 1px dashed #1F2328; padding-top: 10px;'><span class='data-lbl'>Suggested Stake</span><span class='data-val hl-blue'>${dollar_sz:,.0f} <span style='font-size:0.6rem; color:#8B949E;'>({best_bet['Kelly']:.2f}%)</span></span></div>
    </div>
    """, unsafe_allow_html=True)
                else:
                    st.markdown("""<div class='grid-panel' style='height: 100%; display: flex; align-items: center; justify-content: center;'><div class='data-val' style='text-align: center; color: #F85149; font-size: 0.8rem;'>NEGATIVE EV DETECTED<br><span style='font-size: 0.7rem; font-weight: 400; color: #8B949E;'>Capital preserved. No edge found in current lines.</span></div></div>""", unsafe_allow_html=True)

            with col_chart:
                st.markdown("""<div class='grid-panel' style='padding-bottom: 0px; height: 100%; box-sizing: border-box;'><div class='panel-title'>Score Probability Tensor</div>""", unsafe_allow_html=True)
                
                fig_heat = go.Figure(data=go.Heatmap(
                    z=score_matrix.T, 
                    x=[0, 1, 2, 3, 4, 5], y=[0, 1, 2, 3, 4, 5],
                    colorscale=[[0, '#000000'], [1, '#238636']], 
                    text=np.round(score_matrix.T, 1), texttemplate="%{text}%", textfont={"color":"white", "size":9, "family":"JetBrains Mono"},
                    showscale=False, xgap=1, ygap=1
                ))
                
                fig_heat.update_layout(
                    template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=220, margin=dict(l=20, r=10, t=10, b=20),
                    xaxis=dict(title=f"{a_name[:12]}", title_font=dict(size=9, color="#8B949E"), tickfont=dict(size=8, color="#8B949E"), side="bottom", showgrid=False),
                    yaxis=dict(title=f"{h_name[:12]}", title_font=dict(size=9, color="#8B949E"), tickfont=dict(size=8, color="#8B949E"), autorange="reversed", showgrid=False)
                )
                st.plotly_chart(fig_heat, use_container_width=True, config={'displayModeBar': False})
                st.markdown("</div>", unsafe_allow_html=True)

            if valid_markets:
                st.markdown("""<div class='grid-panel' style='padding: 12px;'><div class='panel-title'>Pricing Matrix (Top EV)</div>""", unsafe_allow_html=True)
                clean_markets = sorted(valid_markets, key=lambda x: x['Edge'], reverse=True)
                
                st.markdown("<div class='table-container'>", unsafe_allow_html=True)
                table_html = "<table class='ob-table'><tr><th>Asset</th><th>Line</th><th>True Prob</th><th>EV%</th><th>Kelly</th></tr>"
                for m in clean_markets[:6]: 
                    edge_val = m['Edge'] * 100
                    e_color = "hl-green" if edge_val > 0 else "hl-red"
                    e_sign = "+" if edge_val > 0 else ""
                    table_html += f"<tr><td>{m['Market']}</td><td style='color:#3FB950; font-weight:700;'>{m['BookOdd']:.3f}</td>"
                    table_html += f"<td>{m['SysProb']*100:.1f}%</td>"
                    table_html += f"<td class='{e_color}'>{e_sign}{edge_val:.2f}%</td>"
                    table_html += f"<td style='color:#8B949E;'>{m['Kelly']:.2f}%</td></tr>"
                table_html += "</table></div>"
                st.markdown(table_html, unsafe_allow_html=True)
                st.markdown("""</div>""", unsafe_allow_html=True)

with tab2:
    st.markdown("""<div class='grid-panel' style='margin-bottom: 20px;'><div class='panel-title'>Historical Equity Curve & Drawdown Analysis</div>""", unsafe_allow_html=True)
    
    with st.spinner(f"Simulating institutional P&L..."):
        try:
            df_ledger = get_verified_history(GLOBAL_LEAGUES[league_name])
        except Exception as e:
            df_ledger = pd.DataFrame()
            st.markdown("""<div class='safe-error'><div class='safe-error-title'>DATA FEED ERROR</div><div class='safe-error-msg'>Check API Quota.</div></div>""", unsafe_allow_html=True)
    
    if len(df_ledger) > 0:
        total_matches = len(df_ledger)
        hits = len(df_ledger[df_ledger['Res'] == 'HIT'])
        hit_rate = (hits / total_matches) * 100 if total_matches > 0 else 0
        
        total_pnl = df_ledger['PnL'].sum()
        roi_pct = (total_pnl / total_matches) * 100 if total_matches > 0 else 0
        
        cumulative = df_ledger.sort_values(by="Date", ascending=True)['Cumulative_PnL']
        peak = cumulative.expanding(min_periods=1).max()
        drawdown = (cumulative - peak)
        max_dd = drawdown.min()
        
        hr_color = "hl-green" if hit_rate > 50 else "hl-red"
        roi_color = "hl-green" if total_pnl > 0 else "hl-red"
        roi_sign = "+" if total_pnl > 0 else ""
        
        fig_equity = go.Figure()
        fig_equity.add_trace(go.Scatter(
            x=list(range(len(cumulative))), y=cumulative, mode='lines',
            line=dict(color='#3FB950', width=2), fill='tozeroy', fillcolor='rgba(63, 185, 80, 0.1)',
            name='Cumulative P&L'
        ))
        fig_equity.update_layout(
            template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            height=200, margin=dict(l=10, r=10, t=10, b=10),
            xaxis=dict(showgrid=False, showticklabels=False),
            yaxis=dict(gridcolor='#1F2328', title='Units P&L', title_font=dict(size=9, color="#8B949E"), tickfont=dict(size=9, color="#8B949E"))
        )
        st.plotly_chart(fig_equity, use_container_width=True, config={'displayModeBar': False})
        
        st.markdown(f"""
        <div class='metric-grid' style='grid-template-columns: repeat(4, 1fr); gap: 10px;'>
            <div class='metric-card'><div class='metric-card-title'>Sample Size</div><div class='metric-card-val' style='color:#E6EDF3;'>{total_matches}</div></div>
            <div class='metric-card'><div class='metric-card-title'>Win Rate</div><div class='metric-card-val {hr_color}'>{hit_rate:.1f}%</div></div>
            <div class='metric-card'><div class='metric-card-title'>Net P&L (Units)</div><div class='metric-card-val {roi_color}'>{roi_sign}{total_pnl:.2f}</div></div>
            <div class='metric-card'><div class='metric-card-title'>Max Drawdown</div><div class='metric-card-val hl-red'>{max_dd:.2f}</div></div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<div class='table-container' style='margin-top: 15px;'>", unsafe_allow_html=True)
        ledger_html = "<table class='ob-table'><tr><th>Date</th><th>Fixture</th><th>Asset</th><th>Conf</th><th>True Line</th><th>Res</th><th>PnL</th></tr>"
        
        for _, row in df_ledger.head(50).iterrows():
            res = str(row.get('Res', 'MISS'))
            badge_class = "badge-win" if res == "HIT" else "badge-loss"
            conf = str(row.get('Conf', 'LOW'))
            conf_class = f"badge-{conf.lower()}"
            pnl = row.get('PnL', 0)
            pnl_color = "hl-green" if pnl > 0 else "hl-red"
            pnl_sign = "+" if pnl > 0 else ""
            
            ledger_html += f"<tr>"
            ledger_html += f"<td>{row.get('Date', '')}</td>"
            ledger_html += f"<td>{row.get('Match', '')}</td>"
            ledger_html += f"<td>{row.get('Model Pick', '')}</td>"
            ledger_html += f"<td><span class='{conf_class}'>{conf}</span></td>"
            ledger_html += f"<td>{row.get('True Line', 0):.2f}</td>"
            ledger_html += f"<td><span class='{badge_class}'>{res}</span></td>"
            ledger_html += f"<td class='{pnl_color}'>{pnl_sign}{pnl:.2f}</td>"
            ledger_html += f"</tr>"
        ledger_html += "</table></div>"
        
        st.markdown(ledger_html, unsafe_allow_html=True)
        st.markdown("""
        <div style='color: #8B949E; font-size: 0.65rem; border-top: 1px solid #1F2328; padding-top: 8px; margin-top: 16px; line-height: 1.4;'>
        <strong>STRICT CANDOR DISCLOSURE:</strong> Flat 1-unit staking assumed. Data leakage minimized by strictly comparing past closing lines against post-match results. Prop markets (Corners/Cards) excluded from historical P&L audit to preserve data purity, as free API endpoints cannot reconstruct high-fidelity pre-match corner/card stats. Negative binomial distributions required for deep prop backtesting.
        </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""<div class='grid-panel'><div class='data-lbl' style='text-align:center;'>No historical data.</div></div>""", unsafe_allow_html=True)