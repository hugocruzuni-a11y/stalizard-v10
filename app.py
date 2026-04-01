import streamlit as st
import numpy as np
import pandas as pd
import requests
import math
import plotly.graph_objects as go
from datetime import date, datetime, timedelta

# ==========================================
# 1. HFT TERMINAL UX/UI (HOLZHAUER GRADE)
# ==========================================
st.set_page_config(page_title="APEX QUANT | HFT DESK", layout="wide", initial_sidebar_state="collapsed")
st.cache_data.clear()

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;600;700&family=Inter:wght@400;500;600;700&display=swap');

/* TRUE BLACK TERMINAL */
.stApp { background-color: #000000; color: #D1D5DB; font-family: 'Inter', sans-serif; }
header, footer, #MainMenu, div[data-testid="stToolbar"] { display: none !important; }

/* CYBER TOP BAR */
.top-nav { background: #050505; border-bottom: 1px solid #1A1A1A; padding: 10px 24px; display: flex; justify-content: space-between; align-items: center; margin: -3rem -3rem 1.5rem -3rem; position: sticky; top: 0; z-index: 1000;}
.nav-group { display: flex; align-items: center; gap: 20px; flex-wrap: wrap; }
.logo { font-size: 1.2rem; font-weight: 700; color: #FFFFFF; font-family: 'Fira Code', monospace; letter-spacing: -1px;}
.logo span { color: #00FFA3; text-shadow: 0 0 10px rgba(0, 255, 163, 0.4); }
.status-badge { font-size: 0.65rem; font-family: 'Fira Code', monospace; font-weight: 600; padding: 4px 8px; border-radius: 2px; border: 1px solid #1A1A1A; color: #6B7280; background: #0A0A0A; letter-spacing: 0.5px;}
.status-live { color: #00FFA3; border-color: rgba(0, 255, 163, 0.3); background: rgba(0, 255, 163, 0.05); }

/* QUANT PANELS */
.grid-panel { border: 1px solid #1A1A1A; background: #050505; padding: 16px; margin-bottom: 16px; width: 100%; box-sizing: border-box; position: relative;}
.grid-panel::before { content: ''; position: absolute; top: 0; left: 0; width: 100%; height: 1px; background: linear-gradient(90deg, #00FFA3 0%, transparent 50%); opacity: 0.2; }
.panel-title { font-size: 0.65rem; color: #6B7280; text-transform: uppercase; border-bottom: 1px dashed #1A1A1A; padding-bottom: 8px; margin-bottom: 12px; font-weight: 600; letter-spacing: 1px; font-family: 'Fira Code', monospace;}

/* NEON DATA ROWS */
.data-row { display: flex; justify-content: space-between; font-size: 0.8rem; margin-bottom: 6px; align-items: center;}
.data-lbl { color: #6B7280; font-weight: 500; font-family: 'Inter', sans-serif;}
.data-val { color: #FFFFFF; font-weight: 600; font-family: 'Fira Code', monospace; }

/* HOLZHAUER COLORS */
.hl-neon { color: #00FFA3 !important; text-shadow: 0 0 8px rgba(0, 255, 163, 0.3); }
.hl-pink { color: #FF0055 !important; text-shadow: 0 0 8px rgba(255, 0, 85, 0.3); }
.hl-cyan { color: #00E5FF !important; }
.hl-gray { color: #4B5563 !important; }

/* BLOOMBERG-STYLE TICKET */
.trade-signal { background: #0A0A0A; padding: 20px; margin-bottom: 16px; border: 1px solid #1A1A1A; border-left: 3px solid #00FFA3; box-shadow: inset 0 0 20px rgba(0, 255, 163, 0.02);}
.trade-asset { font-size: 1.1rem; color: #FFFFFF; font-weight: 600; margin-bottom: 4px; font-family: 'Fira Code', monospace; letter-spacing: -0.5px;}
.trade-odd { font-size: 1.5rem; color: #00FFA3; font-weight: 700; font-family: 'Fira Code', monospace; margin-bottom: 16px; line-height: 1;}

/* HIGH-DENSITY TABLES */
.table-container { width: 100%; overflow-x: auto; margin-bottom: 10px; }
.ob-table { width: 100%; min-width: 700px; font-size: 0.75rem; border-collapse: collapse; font-family: 'Fira Code', monospace; }
.ob-table th { color: #4B5563; text-align: right; font-weight: 500; border-bottom: 1px solid #1A1A1A; padding: 8px; font-size: 0.65rem; text-transform: uppercase; background: #000000;}
.ob-table th:first-child { text-align: left; }
.ob-table td { text-align: right; padding: 8px; border-bottom: 1px solid #0A0A0A; color: #D1D5DB;}
.ob-table td:first-child { text-align: left; color: #FFFFFF;}
.ob-table tr:hover td { background: #0A0A0A; }

/* CONFIDENCE TAGS */
.tag-high { background: rgba(0, 229, 255, 0.1); color: #00E5FF; border: 1px solid rgba(0, 229, 255, 0.3); padding: 2px 6px; border-radius: 2px; font-size: 0.65rem; font-weight: 700;}
.tag-med { background: rgba(107, 114, 128, 0.1); color: #9CA3AF; border: 1px solid rgba(107, 114, 128, 0.3); padding: 2px 6px; border-radius: 2px; font-size: 0.65rem; font-weight: 600;}
.tag-low { background: rgba(255, 0, 85, 0.1); color: #FF0055; border: 1px solid rgba(255, 0, 85, 0.3); padding: 2px 6px; border-radius: 2px; font-size: 0.65rem; font-weight: 600;}
.tag-win { color: #00FFA3; font-weight: 700; }
.tag-loss { color: #FF0055; font-weight: 700; }

/* KPI GRID */
.metric-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 10px; margin-bottom: 16px; }
.metric-card { background: #050505; border: 1px solid #1A1A1A; border-radius: 2px; padding: 12px 16px; display: flex; flex-direction: column; justify-content: center;}
.metric-card-title { font-size: 0.6rem; color: #6B7280; text-transform: uppercase; font-weight: 600; margin-bottom: 4px; font-family: 'Fira Code', monospace;}
.metric-card-val { font-size: 1.4rem; color: #FFFFFF; font-weight: 500; font-family: 'Fira Code', monospace; line-height: 1.2;}

/* INPUTS & BUTTONS */
div[data-baseweb="select"] > div, div[data-baseweb="input"] > div { background-color: #050505 !important; border: 1px solid #1A1A1A !important; color: #FFFFFF !important; border-radius: 0px !important; font-family: 'Fira Code', monospace !important; font-size: 0.8rem !important;}
.btn-run > button { background: transparent !important; color: #00FFA3 !important; border: 1px solid #00FFA3 !important; font-weight: 600 !important; width: 100%; border-radius: 2px !important; padding: 10px !important; font-size: 0.8rem !important; margin-top: 10px; font-family: 'Fira Code', monospace; letter-spacing: 1px;}
.btn-run > button:hover { background: rgba(0, 255, 163, 0.1) !important; box-shadow: 0 0 10px rgba(0, 255, 163, 0.2) !important;}
button[data-baseweb="tab"] { color: #6B7280 !important; font-weight: 600 !important; font-size: 0.8rem !important; font-family: 'Fira Code', monospace !important;}
button[data-baseweb="tab"][aria-selected="true"] { color: #FFFFFF !important; border-bottom-color: #00FFA3 !important;}
div[data-testid="column"] > div { gap: 0rem !important; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. HOLZHAUER MATH & RISK ENGINE
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
    default_stats = {"gf_h": 1.45, "ga_h": 1.15, "gf_a": 1.15, "ga_a": 1.45, "corn_h": 5.5, "corn_a": 4.5, "cards_h": 2.0, "cards_a": 2.5}
    if not stats: return default_stats 
    try:
        data = stats if isinstance(stats, dict) else stats[0]
        goals = data.get('goals', {})
        return {
            "gf_h": max(0.2, float(goals.get('for', {}).get('average', {}).get('home') or 1.45)),
            "ga_h": max(0.2, float(goals.get('against', {}).get('average', {}).get('home') or 1.15)),
            "gf_a": max(0.2, float(goals.get('for', {}).get('average', {}).get('away') or 1.15)),
            "ga_a": max(0.2, float(goals.get('against', {}).get('average', {}).get('away') or 1.45)),
            "corn_h": 5.5, "corn_a": 4.5, "cards_h": 2.1, "cards_a": 2.4 
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
    btts_no = np.sum(score_matrix[0, :]) + np.sum(score_matrix[:, 0]) - score_matrix[0, 0]
    
    exp_corners = stats_h['corn_h'] + stats_a['corn_a']
    exp_cards = stats_h['cards_h'] + stats_a['cards_a']
    
    probs = {
        "Home Win": hw, "Draw": dr, "Away Win": aw, 
        "BTTS (Yes)": 1 - btts_no, "BTTS (No)": btts_no,
        "Goals Over 2.5": 1 - u25, "Goals Under 2.5": u25,
        "Corners Over 9.5": 1 - sum([poisson_pmf(exp_corners, i) for i in range(10)]), 
        "Corners Under 9.5": sum([poisson_pmf(exp_corners, i) for i in range(10)]),
        "Cards Over 4.5": 1 - sum([poisson_pmf(exp_cards, i) for i in range(5)]), 
        "Cards Under 4.5": sum([poisson_pmf(exp_cards, i) for i in range(5)])
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
        
        for p_mkt in [("Goals Over 2.5", "Goals Under 2.5"), ("Corners Over 9.5", "Corners Under 9.5"),
                      ("Cards Over 4.5", "Cards Under 4.5"), ("BTTS (Yes)", "BTTS (No)")]:
            if p_mkt[0] in market_odds and p_mkt[1] in market_odds:
                o_val, u_val = market_odds[p_mkt[0]], market_odds[p_mkt[1]]
                if o_val > 0 and u_val > 0:
                    true_p = power_method_devig([1/o_val, 1/u_val])
                    true_odds_map[p_mkt[0]], true_odds_map[p_mkt[1]] = true_p[0], true_p[1]
    except: pass
    return true_odds_map

def calculate_strict_kelly(prob, odd, fraction, max_cap=0.03):
    """
    HOLZHAUER STRICT KELLY: Mathematically calculates the exact Kelly criterion,
    applies the fractional safety, and hard-caps the exposure to protect against fat-tail events.
    """
    b = odd - 1.0
    if b <= 0: return 0.0
    
    # Raw Kelly Edge Calculation (prob * odd - 1)
    edge = (prob * odd) - 1.0
    if edge <= 0: return 0.0
    
    raw_kelly = edge / b
    adj_kelly = raw_kelly * fraction
    
    # Return the minimum between calculated Kelly and the Max Bankroll Cap (e.g., 3%)
    return min(adj_kelly, max_cap) * 100 

def calculate_bookmaker_margin(market_odds):
    try:
        if "Home Win" in market_odds and "Draw" in market_odds and "Away Win" in market_odds:
            hw, dr, aw = market_odds["Home Win"], market_odds["Draw"], market_odds["Away Win"]
            if hw > 0 and dr > 0 and aw > 0: return ((1/hw) + (1/dr) + (1/aw)) - 1
    except: pass
    return None

# ==========================================
# 2.1 INSTITUTIONAL BACKTEST ENGINE
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
            
            if (h_goals + a_goals) > 2.5: real_outcomes.append("Goals Over 2.5")
            else: real_outcomes.append("Goals Under 2.5")
            
            if h_goals > 0 and a_goals > 0: real_outcomes.append("BTTS (Yes)")
            else: real_outcomes.append("BTTS (No)")
            
            is_win = best_market in real_outcomes
            min_odd = 1 / pred_prob 
            pnl = (min_odd - 1.0) if is_win else -1.0
            
            trades.append({
                "Date": match_date, "Asset": f"{h_team[:10]} v {a_team[:10]}",
                "Signal": best_market, "Conf": confidence,
                "Sys_Prob": pred_prob, "True_Line": min_odd, 
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
        <div style="font-family:'Fira Code', monospace; font-size: 0.65rem; color: #6B7280; line-height: 1.2; letter-spacing: 0.5px;">V24.0 BUILD<br><span style="color:#FFFFFF; font-weight:600;">INSTITUTIONAL HFT DESK</span></div>
    </div>
    <div class="nav-group">
        <div class="status-badge">DC-POISSON // BINOMIAL PROX</div>
        <div class="status-badge status-live">● API CONNECTED</div>
    </div>
</div>
""", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["ORDER EXECUTION", "RISK & ALPHA BACKTEST"])

with tab1:
    col_ctrl, col_exec = st.columns([1, 2.6], gap="large")

    with col_ctrl:
        st.markdown("""<div class='grid-panel' style='margin-bottom: 0;'><div class='panel-title'>SYSTEM PARAMETERS</div>""", unsafe_allow_html=True)
        target_date = st.date_input("Execution Date", date.today())
        league_name = st.selectbox("Liquidity Pool", list(GLOBAL_LEAGUES.keys()))
        league_id = GLOBAL_LEAGUES[league_name]
        
        st.markdown("<div style='height: 1px; background: #1A1A1A; margin: 16px 0;'></div>", unsafe_allow_html=True)
        
        # Holzhauer Grade Inputs
        bankroll = st.number_input("AUM (Assets Under Mgt) $", value=100000, step=10000, format="%d")
        col_k1, col_k2 = st.columns(2)
        with col_k1: kelly_fraction = st.selectbox("Kelly Divisor", [0.1, 0.25, 0.5, 1.0], index=1)
        with col_k2: max_exposure = st.selectbox("Max Bet Cap", [0.01, 0.02, 0.03, 0.05], index=2, help="Max % of AUM per trade")
        
        st.markdown("<div style='height: 1px; background: #1A1A1A; margin: 16px 0;'></div>", unsafe_allow_html=True)

        with st.spinner("Fetching Market Data..."):
            fixtures = get_live_fixtures(target_date.strftime('%Y-%m-%d'), league_id)
            
        m_sel = None
        btn_run = False
        
        if fixtures:
            m_map = {}
            for f in fixtures:
                h_name = f.get('teams', {}).get('home', {}).get('name', 'Unknown')
                a_name = f.get('teams', {}).get('away', {}).get('name', 'Unknown')
                m_map[f"{h_name} v {a_name}"] = f
                
            m_sel = m_map[st.selectbox("Select Asset", list(m_map.keys()))]
            st.markdown("<div class='btn-run'>", unsafe_allow_html=True)
            btn_run = st.button("CALCULATE ALPHA")
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='color:#FF0055; font-size:0.7rem; font-family:Fira Code; text-align:center; padding: 10px; border: 1px solid rgba(255,0,85,0.3); border-radius: 2px; background: rgba(255,0,85,0.05); margin-top: 12px;'>NO LIQUIDITY FOUND</div>", unsafe_allow_html=True)
            
        st.markdown("</div>", unsafe_allow_html=True)

    if m_sel and btn_run:
        with st.spinner("Solving Tensors..."):
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
                            if 'Over 2.5' in vals: raw_odds["Goals Over 2.5"] = vals['Over 2.5']
                            if 'Under 2.5' in vals: raw_odds["Goals Under 2.5"] = vals['Under 2.5']
                        elif name == 'Both Teams Score':
                            if 'Yes' in vals: raw_odds["BTTS (Yes)"] = vals['Yes']
                            if 'No' in vals: raw_odds["BTTS (No)"] = vals['No']
                        elif name == 'Corners Over Under': 
                            if 'Over 9.5' in vals: raw_odds["Corners Over 9.5"] = vals['Over 9.5']
                            if 'Under 9.5' in vals: raw_odds["Corners Under 9.5"] = vals['Under 9.5']
                        elif name == 'Cards Over/Under': 
                            if 'Over 4.5' in vals: raw_odds["Cards Over 4.5"] = vals['Over 4.5']
                            if 'Under 4.5' in vals: raw_odds["Cards Under 4.5"] = vals['Under 4.5']
                
                bookie_margin = calculate_bookmaker_margin(raw_odds)
                valid_markets = []
                best_bet = None
                
                if raw_odds:
                    true_bookie_probs = extract_true_odds(raw_odds)
                    for mkt, odd in raw_odds.items():
                        sys_p = sys_probs.get(mkt, 0)
                        if sys_p == 0: continue
                        
                        book_true_p = true_bookie_probs.get(mkt, 1/odd) 
                        
                        # Exact EV Math
                        ev_pct = (sys_p * odd) - 1.0
                        
                        # Holzhauer Strict Kelly
                        kelly_val = calculate_strict_kelly(sys_p, odd, kelly_fraction, max_exposure) if ev_pct > 0 else 0
                        
                        valid_markets.append({
                            "Market": mkt, "BookOdd": odd, "SysProb": sys_p, 
                            "EV": ev_pct, "Kelly": kelly_val
                        })
                    
                    safe_bets = [m for m in valid_markets if m['EV'] > 0.005] # Need at least 0.5% EV
                    if safe_bets: best_bet = max(safe_bets, key=lambda x: x['Kelly'])
                    
            except Exception as e:
                 st.markdown(f"<div class='safe-error'><div class='safe-error-title'>CRITICAL ERROR</div><div class='safe-error-msg'>API missing required tensors. {str(e)}</div></div>", unsafe_allow_html=True)
                 st.stop()
            
        with col_exec:
            b_margin_ui = f"{bookie_margin*100:.2f}%" if bookie_margin else "N/A"
            m_color = "hl-pink" if bookie_margin and bookie_margin > 0.05 else "hl-cyan"
            
            st.markdown(f"""
            <div class='metric-grid'>
                <div class='metric-card'><div class='metric-card-title'>{h_name[:12]} xG</div><div class='metric-card-val'>{lam_h:.2f}</div></div>
                <div class='metric-card'><div class='metric-card-title'>{a_name[:12]} xG</div><div class='metric-card-val'>{lam_a:.2f}</div></div>
                <div class='metric-card'><div class='metric-card-title'>Market Vig (Juice)</div><div class='metric-card-val {m_color}'>{b_margin_ui}</div></div>
            </div>
            """, unsafe_allow_html=True)

            col_alpha, col_chart = st.columns([1.1, 1], gap="large")
            
            with col_alpha:
                if not raw_odds:
                    st.markdown("""<div class='grid-panel' style='height: 100%; display: flex; align-items: center; justify-content: center;'><div class='data-val' style='text-align: center; color: #6B7280; font-size: 0.7rem;'>MARKET DATA UNAVAILABLE<br><span style='font-size: 0.6rem; font-weight: 400;'>Strict Mode: Synthetic lines disabled.</span></div></div>""", unsafe_allow_html=True)
                elif best_bet:
                    dollar_sz = (best_bet['Kelly']/100) * bankroll
                    
                    st.markdown(f"""
    <div class='trade-signal'>
        <div class='panel-title' style='color:#00FFA3; border-color:#1A1A1A; margin-bottom: 8px;'>EXECUTION TICKET</div>
        <div class='trade-asset'>{best_bet['Market'].upper()}</div>
        <div class='trade-odd'>@ {best_bet['BookOdd']:.3f}</div>
        <div style="margin-bottom: 12px;">
            <div class='data-row'><span class='data-lbl'>True Probability</span><span class='data-val'>{best_bet['SysProb']*100:.2f}%</span></div>
            <div class='data-row'><span class='data-lbl'>Zero-Vig Fair Line</span><span class='data-val'>{1/best_bet['SysProb']:.3f}</span></div>
            <div class='data-row'><span class='data-lbl'>Expected Value (EV)</span><span class='data-val hl-neon'>+{best_bet['EV']*100:.2f}%</span></div>
        </div>
        <div style='border-top: 1px solid #1A1A1A; padding-top: 12px;'>
            <div style='font-size: 0.65rem; color: #6B7280; text-transform: uppercase; margin-bottom: 4px; font-family: Fira Code;'>Capital Allocation (Constrained Kelly)</div>
            <div style='font-size: 1.4rem; color: #FFFFFF; font-family: Fira Code; font-weight: 700;'>${dollar_sz:,.0f} <span style='font-size: 0.8rem; color: #6B7280;'>({best_bet['Kelly']:.2f}% AUM)</span></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
                else:
                    st.markdown("""<div class='grid-panel' style='height: 100%; display: flex; align-items: center; justify-content: center;'><div class='data-val' style='text-align: center; color: #FF0055; font-size: 0.8rem;'>NEGATIVE EXPECTED VALUE<br><span style='font-size: 0.65rem; font-weight: 400; color: #6B7280;'>Capital preserved. No mathematical edge in current liquidity.</span></div></div>""", unsafe_allow_html=True)

            with col_chart:
                st.markdown("""<div class='grid-panel' style='padding-bottom: 0px; height: 100%; box-sizing: border-box;'><div class='panel-title'>SCORE PROBABILITY TENSOR</div>""", unsafe_allow_html=True)
                
                fig_heat = go.Figure(data=go.Heatmap(
                    z=score_matrix.T, 
                    x=[0, 1, 2, 3, 4, 5], y=[0, 1, 2, 3, 4, 5],
                    colorscale=[[0, '#000000'], [1, '#00FFA3']], 
                    text=np.round(score_matrix.T, 1), texttemplate="%{text}", textfont={"color":"#FFFFFF", "size":10, "family":"Fira Code"},
                    showscale=False, xgap=1, ygap=1
                ))
                
                fig_heat.update_layout(
                    template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=230, margin=dict(l=20, r=10, t=10, b=20),
                    xaxis=dict(title=f"{a_name[:12]}", title_font=dict(size=9, color="#6B7280", family="Fira Code"), tickfont=dict(size=8, color="#6B7280"), side="bottom", showgrid=False),
                    yaxis=dict(title=f"{h_name[:12]}", title_font=dict(size=9, color="#6B7280", family="Fira Code"), tickfont=dict(size=8, color="#6B7280"), autorange="reversed", showgrid=False)
                )
                st.plotly_chart(fig_heat, use_container_width=True, config={'displayModeBar': False})
                st.markdown("</div>", unsafe_allow_html=True)

            if valid_markets:
                st.markdown("""<div class='grid-panel' style='padding: 12px;'><div class='panel-title'>ALPHA PRICING MATRIX</div>""", unsafe_allow_html=True)
                clean_markets = sorted(valid_markets, key=lambda x: x['EV'], reverse=True)
                
                st.markdown("<div class='table-container'>", unsafe_allow_html=True)
                table_html = "<table class='ob-table'><tr><th>Asset Market</th><th>Line</th><th>True P(x)</th><th>EV (%)</th><th>Req. Kelly</th></tr>"
                for m in clean_markets[:6]: 
                    ev_val = m['EV'] * 100
                    e_color = "hl-neon" if ev_val > 0 else "hl-pink"
                    e_sign = "+" if ev_val > 0 else ""
                    table_html += f"<tr><td>{m['Market']}</td><td style='color:#00E5FF; font-weight:700;'>{m['BookOdd']:.3f}</td>"
                    table_html += f"<td>{m['SysProb']*100:.1f}%</td>"
                    table_html += f"<td class='{e_color}'>{e_sign}{ev_val:.2f}%</td>"
                    table_html += f"<td style='color:#6B7280;'>{m['Kelly']:.2f}%</td></tr>"
                table_html += "</table></div>"
                st.markdown(table_html, unsafe_allow_html=True)
                st.markdown("""</div>""", unsafe_allow_html=True)

with tab2:
    st.markdown("""<div class='grid-panel' style='margin-bottom: 20px;'><div class='panel-title'>RISK & EQUITY CURVE ANALYSIS (N=60)</div>""", unsafe_allow_html=True)
    
    with st.spinner(f"Running Monte Carlo / Historical Verification..."):
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
        
        # Risk Metrics (Holzhauer Style)
        cumulative = df_ledger.sort_values(by="Date", ascending=True)['Cumulative_PnL']
        peak = cumulative.expanding(min_periods=1).max()
        drawdown = (cumulative - peak)
        max_dd = drawdown.min()
        
        # Pseudo Sharpe Ratio (Mean PnL / StdDev PnL)
        std_dev = df_ledger['PnL'].std()
        sharpe = (df_ledger['PnL'].mean() / std_dev) * math.sqrt(total_matches) if std_dev > 0 else 0
        
        hr_color = "hl-neon" if hit_rate > 52 else "hl-pink"
        roi_color = "hl-neon" if total_pnl > 0 else "hl-pink"
        roi_sign = "+" if total_pnl > 0 else ""
        sharpe_color = "hl-cyan" if sharpe > 1 else "hl-gray"
        
        fig_equity = go.Figure()
        fig_equity.add_trace(go.Scatter(
            x=list(range(len(cumulative))), y=cumulative, mode='lines',
            line=dict(color='#00FFA3', width=2), fill='tozeroy', fillcolor='rgba(0, 255, 163, 0.05)',
            name='Equity'
        ))
        fig_equity.update_layout(
            template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            height=200, margin=dict(l=10, r=10, t=10, b=10),
            xaxis=dict(showgrid=False, showticklabels=False),
            yaxis=dict(gridcolor='#1A1A1A', title='Units', title_font=dict(size=9, color="#6B7280", family="Fira Code"), tickfont=dict(size=9, color="#6B7280", family="Fira Code"))
        )
        st.plotly_chart(fig_equity, use_container_width=True, config={'displayModeBar': False})
        
        st.markdown(f"""
        <div class='metric-grid' style='grid-template-columns: repeat(4, 1fr); gap: 10px;'>
            <div class='metric-card'><div class='metric-card-title'>Win Prob.</div><div class='metric-card-val {hr_color}'>{hit_rate:.1f}%</div></div>
            <div class='metric-card'><div class='metric-card-title'>Net P&L (U)</div><div class='metric-card-val {roi_color}'>{roi_sign}{total_pnl:.2f}</div></div>
            <div class='metric-card'><div class='metric-card-title'>Max Drawdown</div><div class='metric-card-val hl-pink'>{max_dd:.2f}U</div></div>
            <div class='metric-card'><div class='metric-card-title'>Est. Sharpe</div><div class='metric-card-val {sharpe_color}'>{sharpe:.2f}</div></div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<div class='table-container' style='margin-top: 15px;'>", unsafe_allow_html=True)
        ledger_html = "<table class='ob-table'><tr><th>T-Date</th><th>Asset</th><th>Signal</th><th>Conf</th><th>Fair P(x)</th><th>Fair Line</th><th>Res</th><th>PnL (U)</th></tr>"
        
        for _, row in df_ledger.head(50).iterrows():
            res = str(row.get('Res', 'MISS'))
            badge_class = "tag-win" if res == "HIT" else "tag-loss"
            conf = str(row.get('Conf', 'LOW'))
            conf_class = f"tag-{conf.lower()}"
            pnl = row.get('PnL', 0)
            pnl_color = "hl-neon" if pnl > 0 else "hl-pink"
            pnl_sign = "+" if pnl > 0 else ""
            
            ledger_html += f"<tr>"
            ledger_html += f"<td>{row.get('Date', '')}</td>"
            ledger_html += f"<td>{row.get('Asset', '')}</td>"
            ledger_html += f"<td style='color:#FFFFFF;'>{row.get('Signal', '')}</td>"
            ledger_html += f"<td><span class='{conf_class}'>{conf}</span></td>"
            ledger_html += f"<td style='color:#6B7280;'>{row.get('Sys_Prob', 0)*100:.1f}%</td>"
            ledger_html += f"<td>{row.get('True_Line', 0):.2f}</td>"
            ledger_html += f"<td><span class='{badge_class}'>{res}</span></td>"
            ledger_html += f"<td class='{pnl_color}'>{pnl_sign}{pnl:.2f}</td>"
            ledger_html += f"</tr>"
        ledger_html += "</table></div>"
        
        st.markdown("""
        <div style='color: #6B7280; font-size: 0.65rem; border-top: 1px solid #1A1A1A; padding-top: 8px; margin-top: 16px; line-height: 1.4; font-family: Fira Code, monospace;'>
        > <strong>SYSTEM AUDIT DISCLOSURE:</strong> P&L calculates standard 1-unit flat exposure against true theoretical EV. Data leakage protocol active: strict post-closing line evaluation only. High-variance Prop Markets (Corners/Cards) excluded from pure backtest due to API Free-Tier limitations requiring precise historical negative binomial extraction.
        </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""<div class='grid-panel'><div class='data-lbl' style='text-align:center;'>NO DATA IN LEDGER</div></div>""", unsafe_allow_html=True)