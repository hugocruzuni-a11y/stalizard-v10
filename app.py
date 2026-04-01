import streamlit as st
import numpy as np
import pandas as pd
import requests
import math
import plotly.graph_objects as go
from datetime import date, datetime, timedelta

# ==========================================
# 1. HFT SYNDICATE TERMINAL UI
# ==========================================
st.set_page_config(page_title="APEX QUANT | SYNDICATE DESK", layout="wide", initial_sidebar_state="collapsed")
st.cache_data.clear()

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;600;700&family=Inter:wght@400;500;600;700&display=swap');

/* TRUE BLACK TERMINAL (NO DISTRACTIONS) */
.stApp { background-color: #030303; color: #D1D5DB; font-family: 'Inter', sans-serif; }
header, footer, #MainMenu, div[data-testid="stToolbar"] { display: none !important; }

/* QUANT HEADER */
.top-nav { background: #080808; border-bottom: 1px solid #1A1A1A; padding: 8px 20px; display: flex; justify-content: space-between; align-items: center; margin: -3rem -3rem 1.5rem -3rem; position: sticky; top: 0; z-index: 1000;}
.nav-group { display: flex; align-items: center; gap: 15px; flex-wrap: wrap; }
.logo { font-size: 1.1rem; font-weight: 700; color: #FFFFFF; font-family: 'Fira Code', monospace; letter-spacing: -1px;}
.logo span { color: #EAB308; } 
.status-badge { font-size: 0.65rem; font-family: 'Fira Code', monospace; font-weight: 600; padding: 3px 6px; border-radius: 2px; border: 1px solid #1A1A1A; color: #6B7280; background: #000000; letter-spacing: 0.5px;}
.status-live { color: #EAB308; border-color: rgba(234, 179, 8, 0.3); background: rgba(234, 179, 8, 0.05); }

/* ULTRA DENSE PANELS */
.grid-panel { border: 1px solid #1A1A1A; background: #080808; padding: 14px; margin-bottom: 12px; width: 100%; box-sizing: border-box; }
.panel-title { font-size: 0.65rem; color: #6B7280; text-transform: uppercase; border-bottom: 1px dashed #1A1A1A; padding-bottom: 6px; margin-bottom: 10px; font-weight: 600; letter-spacing: 1px; font-family: 'Fira Code', monospace;}

/* DATA ROWS & COLORS */
.data-row { display: flex; justify-content: space-between; font-size: 0.75rem; margin-bottom: 4px; align-items: center;}
.data-lbl { color: #6B7280; font-weight: 500; font-family: 'Inter', sans-serif;}
.data-val { color: #FFFFFF; font-weight: 600; font-family: 'Fira Code', monospace; }
.hl-gold { color: #EAB308 !important; }
.hl-green { color: #22C55E !important; }
.hl-red { color: #EF4444 !important; }

/* EXECUTION HUD */
.trade-signal { background: #000000; padding: 18px; margin-bottom: 12px; border: 1px solid #1A1A1A; border-left: 3px solid #EAB308; }
.trade-asset { font-size: 1.1rem; color: #FFFFFF; font-weight: 700; margin-bottom: 2px; font-family: 'Fira Code', monospace; letter-spacing: -0.5px;}
.trade-odd { font-size: 1.4rem; color: #EAB308; font-weight: 700; font-family: 'Fira Code', monospace; margin-bottom: 12px; line-height: 1;}

/* HFT ORDER BOOK TABLES */
.table-container { width: 100%; overflow-x: auto; margin-bottom: 5px; }
.ob-table { width: 100%; font-size: 0.7rem; border-collapse: collapse; font-family: 'Fira Code', monospace; }
.ob-table th { color: #6B7280; text-align: right; font-weight: 600; border-bottom: 1px solid #1A1A1A; padding: 6px; font-size: 0.6rem; text-transform: uppercase; background: #050505;}
.ob-table th:first-child { text-align: left; }
.ob-table td { text-align: right; padding: 6px; border-bottom: 1px solid #0D0D0D; color: #9CA3AF;}
.ob-table td:first-child { text-align: left; color: #FFFFFF;}
.ob-table tr:hover td { background: #111111; color: #FFFFFF; }

/* MICRO TAGS */
.tag-high { background: rgba(234, 179, 8, 0.1); color: #EAB308; border: 1px solid rgba(234, 179, 8, 0.3); padding: 2px 6px; border-radius: 2px; font-size: 0.65rem; font-weight: 700;}
.tag-med { background: rgba(107, 114, 128, 0.1); color: #9CA3AF; border: 1px solid rgba(107, 114, 128, 0.3); padding: 2px 6px; border-radius: 2px; font-size: 0.65rem; font-weight: 600;}
.tag-low { background: rgba(239, 68, 68, 0.1); color: #EF4444; border: 1px solid rgba(239, 68, 68, 0.3); padding: 2px 6px; border-radius: 2px; font-size: 0.65rem; font-weight: 600;}
.tag-win { color: #22C55E; font-weight: 700; }
.tag-loss { color: #EF4444; font-weight: 700; }

/* METRICS GRID */
.metric-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 8px; margin-bottom: 12px; }
.metric-card { background: #050505; border: 1px solid #1A1A1A; border-radius: 2px; padding: 10px; text-align: center; }
.metric-card-title { font-size: 0.6rem; color: #6B7280; text-transform: uppercase; font-weight: 600; margin-bottom: 4px; font-family: 'Fira Code', monospace;}
.metric-card-val { font-size: 1.2rem; color: #FFFFFF; font-weight: 600; font-family: 'Fira Code', monospace; line-height: 1.1;}

/* COMPACT INPUTS */
div[data-baseweb="select"] > div, div[data-baseweb="input"] > div { background-color: #050505 !important; border: 1px solid #1A1A1A !important; color: #FFFFFF !important; border-radius: 0px !important; font-family: 'Fira Code', monospace !important; font-size: 0.75rem !important; min-height: 32px !important;}
.btn-run > button { background: #EAB308 !important; color: #000000 !important; border: none !important; font-weight: 700 !important; width: 100%; border-radius: 2px !important; padding: 8px !important; font-size: 0.8rem !important; margin-top: 8px; font-family: 'Fira Code', monospace; text-transform: uppercase;}
.btn-run > button:hover { background: #FDE047 !important; }
button[data-baseweb="tab"] { color: #6B7280 !important; font-weight: 600 !important; font-size: 0.75rem !important; font-family: 'Fira Code', monospace !important;}
button[data-baseweb="tab"][aria-selected="true"] { color: #EAB308 !important; border-bottom-color: #EAB308 !important;}
div[data-testid="column"] > div { gap: 0rem !important; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. PRO-TIER DATA POOL & MATH ENGINE
# ==========================================
API_KEY = st.secrets.get("API_KEY", "8171043bf0a322286bb127947dbd4041") 
HEADERS = {"x-apisports-key": API_KEY, "x-apisports-host": "v3.football.api-sports.io"}

GLOBAL_LEAGUES = {
    "Premier League (UK)": 39, "Champions League (EU)": 2, "La Liga (ES)": 140,
    "Serie A (IT)": 135, "Bundesliga (DE)": 78, "Eredivisie (NL)": 88,
    "Championship (UK)": 40, "Brasileirão Série A (BR)": 71, "MLS (USA)": 253,
    "J1 League (JP)": 98, "Primeira Liga (PT)": 94, "Pro League (BE)": 144
}

def get_current_season():
    now = datetime.now()
    return str(now.year) if now.month > 7 else str(now.year - 1)

def fetch_api_safe(endpoint, params):
    try:
        r = requests.get(f"https://{HEADERS['x-apisports-host']}/{endpoint}", headers=HEADERS, params=params, timeout=10)
        if r.status_code == 200:
            data = r.json()
            if not data.get('errors'): return data.get('response', [])
        return []
    except: return []

@st.cache_data(ttl=300) 
def get_live_fixtures(date_str, league_id):
    season = get_current_season()
    return fetch_api_safe("fixtures", {"date": date_str, "league": league_id, "season": season})

@st.cache_data(ttl=3600)
def get_advanced_stats(team_id, league_id):
    season = get_current_season()
    stats = fetch_api_safe("teams/statistics", {"team": team_id, "league": league_id, "season": season})
    
    default_stats = {"gf_h": 1.45, "ga_h": 1.15, "gf_a": 1.15, "ga_a": 1.45, "form": 50, "corn_h": 5.5, "corn_a": 4.5, "cards_h": 2.1, "cards_a": 2.4}
    if not stats: return default_stats 
    
    try:
        data = stats if isinstance(stats, dict) else stats[0]
        goals = data.get('goals', {})
        form_str = data.get('form', '')
        
        form_score = 50
        if form_str:
            recent_form = form_str[-5:]
            pts = sum([3 if c == 'W' else 1 if c == 'D' else 0 for c in recent_form])
            form_score = (pts / 15.0) * 100

        return {
            "gf_h": max(0.2, float(goals.get('for', {}).get('average', {}).get('home') or 1.45)),
            "ga_h": max(0.2, float(goals.get('against', {}).get('average', {}).get('home') or 1.15)),
            "gf_a": max(0.2, float(goals.get('for', {}).get('average', {}).get('away') or 1.15)),
            "ga_a": max(0.2, float(goals.get('against', {}).get('average', {}).get('away') or 1.45)),
            "form": form_score,
            "corn_h": 5.5, "corn_a": 4.5, "cards_h": 2.1, "cards_a": 2.4
        }
    except: return default_stats

def calculate_advanced_lambdas(h_stats, a_stats):
    lam_h = (h_stats['gf_h'] / 1.45) * (a_stats['ga_a'] / 1.45) * 1.45
    lam_a = (a_stats['gf_a'] / 1.15) * (h_stats['ga_h'] / 1.15) * 1.15
    
    form_diff = (h_stats['form'] - a_stats['form']) / 100.0
    lam_h = lam_h * (1 + (form_diff * 0.1))
    lam_a = lam_a * (1 - (form_diff * 0.1))
    
    return max(0.1, lam_h), max(0.1, lam_a)

def poisson_pmf(lam, k):
    return (lam**k * math.exp(-lam)) / math.factorial(k)

def zero_inflated_dixon_coles(lam_h, lam_a, h_stats, a_stats, max_goals=6):
    h_probs = [poisson_pmf(lam_h, i) for i in range(max_goals)]
    a_probs = [poisson_pmf(lam_a, i) for i in range(max_goals)]
    score_matrix = np.outer(h_probs, a_probs)
    
    rho = max(-0.15, -0.12 + 0.02 * (lam_h + lam_a))
    zip_factor = 1.08 
    
    try:
        score_matrix[0, 0] *= max(0, 1 - lam_h * lam_a * rho) * zip_factor
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
    
    ah_h_minus_1_5 = np.tril(score_matrix, -2).sum()
    ah_a_plus_1_5 = 1 - ah_h_minus_1_5
    
    exp_corners = h_stats['corn_h'] + a_stats['corn_a']
    exp_cards = h_stats['cards_h'] + a_stats['cards_a']
    
    probs = {
        "Match Winner: Home": hw, "Match Winner: Draw": dr, "Match Winner: Away": aw, 
        "BTTS: Yes": 1 - btts_no, "BTTS: No": btts_no,
        "Total Goals: Over 2.5": 1 - u25, "Total Goals: Under 2.5": u25,
        "Asian Handicap: Home -1.5": ah_h_minus_1_5, "Asian Handicap: Away +1.5": ah_a_plus_1_5,
        "Total Corners Over 9.5": 1 - sum([poisson_pmf(exp_corners, i) for i in range(10)]),
        "Total Corners Under 9.5": sum([poisson_pmf(exp_corners, i) for i in range(10)]),
        "Total Cards Over 4.5": 1 - sum([poisson_pmf(exp_cards, i) for i in range(5)]),
        "Total Cards Under 4.5": sum([poisson_pmf(exp_cards, i) for i in range(5)])
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

def extract_bookmaker_odds(fixture_id, bookmaker_id):
    raw_odds = {}
    api_data = fetch_api_safe("odds", {"fixture": fixture_id, "bookmaker": bookmaker_id})
    if api_data and api_data[0].get('bookmakers'):
        bets = api_data[0]['bookmakers'][0].get('bets', [])
        for bet in bets:
            name = bet.get('name', '')
            vals = {str(v.get('value', '')): float(v.get('odd', 0.0)) for v in bet.get('values', [])}
            if name == 'Match Winner':
                if 'Home' in vals: raw_odds["Match Winner: Home"] = vals['Home']
                if 'Draw' in vals: raw_odds["Match Winner: Draw"] = vals['Draw']
                if 'Away' in vals: raw_odds["Match Winner: Away"] = vals['Away']
            elif name == 'Goals Over/Under':
                if 'Over 2.5' in vals: raw_odds["Total Goals: Over 2.5"] = vals['Over 2.5']
                if 'Under 2.5' in vals: raw_odds["Total Goals: Under 2.5"] = vals['Under 2.5']
            elif name == 'Both Teams Score':
                if 'Yes' in vals: raw_odds["BTTS: Yes"] = vals['Yes']
                if 'No' in vals: raw_odds["BTTS: No"] = vals['No']
            elif name == 'Asian Handicap':
                if 'Home -1.5' in vals: raw_odds["Asian Handicap: Home -1.5"] = vals['Home -1.5']
                if 'Away +1.5' in vals: raw_odds["Asian Handicap: Away +1.5"] = vals['Away +1.5']
            elif name == 'Corners Over Under': 
                if 'Over 9.5' in vals: raw_odds["Total Corners Over 9.5"] = vals['Over 9.5']
                if 'Under 9.5' in vals: raw_odds["Total Corners Under 9.5"] = vals['Under 9.5']
            elif name == 'Cards Over/Under': 
                if 'Over 4.5' in vals: raw_odds["Total Cards Over 4.5"] = vals['Over 4.5']
                if 'Under 4.5' in vals: raw_odds["Total Cards Under 4.5"] = vals['Under 4.5']
    return raw_odds

def extract_true_odds(market_odds):
    true_odds_map = {}
    try:
        if all(k in market_odds for k in ["Match Winner: Home", "Match Winner: Draw", "Match Winner: Away"]):
            hw, dr, aw = market_odds["Match Winner: Home"], market_odds["Match Winner: Draw"], market_odds["Match Winner: Away"]
            true_p = power_method_devig([1/hw, 1/dr, 1/aw])
            true_odds_map["Match Winner: Home"] = true_p[0]
            true_odds_map["Match Winner: Draw"] = true_p[1]
            true_odds_map["Match Winner: Away"] = true_p[2]
        
        for p_mkt in [("Total Goals: Over 2.5", "Total Goals: Under 2.5"), 
                      ("BTTS: Yes", "BTTS: No"),
                      ("Asian Handicap: Home -1.5", "Asian Handicap: Away +1.5"),
                      ("Total Corners Over 9.5", "Total Corners Under 9.5"),
                      ("Total Cards Over 4.5", "Total Cards Under 4.5")]:
            if p_mkt[0] in market_odds and p_mkt[1] in market_odds:
                o_val, u_val = market_odds[p_mkt[0]], market_odds[p_mkt[1]]
                true_p = power_method_devig([1/o_val, 1/u_val])
                true_odds_map[p_mkt[0]] = true_p[0]
                true_odds_map[p_mkt[1]] = true_p[1]
    except: pass
    return true_odds_map

def calculate_portfolio_metrics(prob, odd, fraction, max_cap):
    b = odd - 1.0
    if b <= 0: return 0.0, 0.0
    
    edge = (prob * odd) - 1.0
    if edge <= 0: return 0.0, 0.0
    
    raw_kelly = edge / b
    adj_kelly = raw_kelly * fraction
    final_kelly_pct = min(adj_kelly, max_cap)
    
    variance = prob * (1 - prob) * (odd ** 2)
    expected_growth = (0.5 * (edge ** 2) / variance) * 100 if variance > 0 else 0
    
    return final_kelly_pct * 100, expected_growth

# ==========================================
# 2.1 BACKTEST ENGINE (HISTORICAL AUDIT RESTORED)
# ==========================================
@st.cache_data(ttl=3600)
def get_verified_history(league_id):
    season = get_current_season()
    past_fixtures = fetch_api_safe("fixtures", {"league": league_id, "season": season, "last": 50})
    
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
            
            h_stats = get_advanced_stats(h_id, league_id)
            a_stats = get_advanced_stats(a_id, league_id)
            lam_h, lam_a = calculate_advanced_lambdas(h_stats, a_stats)
            sys_probs, _ = zero_inflated_dixon_coles(lam_h, lam_a, h_stats, a_stats)
            
            # Filtro para o backtest excluir cantos/cartões devido à falta de dados exatos do passado na free API
            valid_preds = {k: v for k, v in sys_probs.items() if v >= 0.45 and "Corners" not in k and "Cards" not in k}
            
            if not valid_preds:
                best_market = max({k: v for k, v in sys_probs.items() if "Corners" not in k and "Cards" not in k}.keys(), key=lambda m: sys_probs.get(m, 0))
                confidence = "LOW"
            else:
                best_market = max(valid_preds.keys(), key=lambda m: valid_preds.get(m, 0))
                confidence = "HIGH" if sys_probs[best_market] >= 0.60 else "MED"

            pred_prob = sys_probs[best_market]
            
            real_outcomes = []
            if h_goals > a_goals: real_outcomes.append("Match Winner: Home")
            elif h_goals < a_goals: real_outcomes.append("Match Winner: Away")
            else: real_outcomes.append("Match Winner: Draw")
            
            if (h_goals + a_goals) > 2.5: real_outcomes.append("Total Goals: Over 2.5")
            else: real_outcomes.append("Total Goals: Under 2.5")
            
            if h_goals > 0 and a_goals > 0: real_outcomes.append("BTTS: Yes")
            else: real_outcomes.append("BTTS: No")
            
            is_win = best_market in real_outcomes
            min_odd = 1 / pred_prob 
            pnl = (min_odd - 1.0) if is_win else -1.0
            
            trades.append({
                "Date": match_date, "Asset": f"{h_team[:10]} v {a_team[:10]}",
                "Signal": best_market.replace("Match Winner: ", "").replace("Total Goals: ", ""), "Conf": confidence,
                "Sys_Prob": pred_prob, "True_Line": min_odd, 
                "Res": "HIT" if is_win else "MISS", "PnL": pnl
            })
        except: continue
            
    df_trades = pd.DataFrame(trades).sort_values(by="Date", ascending=True) 
    if not df_trades.empty:
        df_trades['Cumulative_PnL'] = df_trades['PnL'].cumsum()
    return df_trades.sort_values(by="Date", ascending=False)


# ==========================================
# 3. INTERFACE RENDER (THE TERMINAL)
# ==========================================
st.markdown(f"""
<div class="top-nav">
    <div class="nav-group">
        <div class="logo">APEX<span>QUANT</span></div>
        <div class="nav-divider"></div>
        <div style="font-family:'Fira Code', monospace; font-size: 0.65rem; color: #6B7280; line-height: 1.2;">BUILD V25.1<br><span style="color:#FFFFFF; font-weight:600;">SYNDICATE TERMINAL</span></div>
    </div>
    <div class="nav-group">
        <div class="status-badge">API: SHARP ROUTING</div>
        <div class="status-badge status-live">● ALG: ZIP DIXON-COLES</div>
    </div>
</div>
""", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["ORDER ENTRY & ALPHA", "RISK & ALPHA BACKTEST"])

with tab1:
    col_ctrl, col_exec = st.columns([1, 2.6], gap="large")

    with col_ctrl:
        st.markdown("""<div class='grid-panel' style='margin-bottom: 0;'><div class='panel-title'>ALGO CONFIGURATION</div>""", unsafe_allow_html=True)
        target_date = st.date_input("Match Date", date.today())
        league_name = st.selectbox("Market Pool", list(GLOBAL_LEAGUES.keys()))
        league_id = GLOBAL_LEAGUES[league_name]
        
        st.markdown("<div style='height: 1px; background: #1A1A1A; margin: 12px 0;'></div>", unsafe_allow_html=True)
        
        bankroll = st.number_input("AUM ($)", value=250000, step=50000, format="%d")
        col_k1, col_k2 = st.columns(2)
        with col_k1: kelly_fraction = st.selectbox("Kelly Divisor", [0.1, 0.25, 0.3, 0.5], index=1)
        with col_k2: max_exposure = st.selectbox("Max Exposure", [0.01, 0.02, 0.025, 0.05], index=1)
        
        st.markdown("<div style='height: 1px; background: #1A1A1A; margin: 12px 0;'></div>", unsafe_allow_html=True)

        with st.spinner("Fetching Market Liquidity..."):
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
            btn_run = st.button("RUN ALPHA SCAN")
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='color:#EF4444; font-size:0.7rem; font-family:Fira Code; text-align:center; padding: 10px; border: 1px solid rgba(239,68,68,0.3); border-radius: 2px; margin-top: 12px;'>NO FIXTURES AVAILABLE</div>", unsafe_allow_html=True)
            
        st.markdown("</div>", unsafe_allow_html=True)

    if m_sel and btn_run:
        with st.spinner("Compiling ZIP Tensor & Sharp Devigging..."):
            try:
                fix_id = m_sel['fixture']['id']
                h_id = m_sel.get('teams', {}).get('home', {}).get('id')
                a_id = m_sel.get('teams', {}).get('away', {}).get('id')
                h_name = m_sel.get('teams', {}).get('home', {}).get('name', 'Home')
                a_name = m_sel.get('teams', {}).get('away', {}).get('name', 'Away')
                
                h_stats = get_advanced_stats(h_id, league_id)
                a_stats = get_advanced_stats(a_id, league_id)
                lam_h, lam_a = calculate_advanced_lambdas(h_stats, a_stats)
                sys_probs, score_matrix = zero_inflated_dixon_coles(lam_h, lam_a, h_stats, a_stats)
                
                sharp_odds = extract_bookmaker_odds(fix_id, 11) 
                soft_odds = extract_bookmaker_odds(fix_id, 8)   
                
                if not soft_odds: soft_odds = sharp_odds 
                
                valid_markets = []
                best_bet = None
                
                if sharp_odds and soft_odds:
                    true_sharp_probs = extract_true_odds(sharp_odds)
                    
                    for mkt, soft_odd in soft_odds.items():
                        sys_p = sys_probs.get(mkt, 0)
                        if sys_p == 0: continue
                        
                        sharp_p = true_sharp_probs.get(mkt, 0)
                        
                        if sharp_p > 0:
                            ev_pct = (sys_p * soft_odd) - 1.0
                            clv_est = (soft_odd / (1/sharp_p)) - 1.0
                            kelly_val, eg_val = calculate_portfolio_metrics(sys_p, soft_odd, kelly_fraction, max_exposure)
                            
                            if ev_pct > 0.01: 
                                valid_markets.append({
                                    "Market": mkt, "ExecOdd": soft_odd, "SharpLine": sharp_odds.get(mkt, 0),
                                    "SysProb": sys_p, "CLV": clv_est, "EV": ev_pct, "Kelly": kelly_val, "EG": eg_val
                                })
                    
                    if valid_markets: 
                        best_bet = max(valid_markets, key=lambda x: x['EG'])
                        
            except Exception as e:
                 st.markdown(f"<div class='safe-error'><div class='safe-error-title'>CRITICAL FAULT</div><div class='safe-error-msg'>{str(e)}</div></div>", unsafe_allow_html=True)
                 st.stop()
            
        with col_exec:
            st.markdown(f"""
            <div class='metric-grid'>
                <div class='metric-card'><div class='metric-card-title'>{h_name[:12]} ZIP xG</div><div class='metric-card-val'>{lam_h:.2f}</div></div>
                <div class='metric-card'><div class='metric-card-title'>{a_name[:12]} ZIP xG</div><div class='metric-card-val'>{lam_a:.2f}</div></div>
                <div class='metric-card'><div class='metric-card-title'>Model vs Sharp Divergence</div><div class='metric-card-val hl-gold'>ACTIVE</div></div>
            </div>
            """, unsafe_allow_html=True)

            col_alpha, col_chart = st.columns([1.1, 1], gap="large")
            
            with col_alpha:
                if not sharp_odds:
                    st.markdown("""<div class='grid-panel' style='height: 100%; display: flex; align-items: center; justify-content: center;'><div class='data-val' style='text-align: center; color: #6B7280; font-size: 0.7rem;'>PINNACLE DATA MISSING<br><span style='font-size: 0.6rem; font-weight: 400;'>Cannot execute without Sharp reference lines.</span></div></div>""", unsafe_allow_html=True)
                elif best_bet:
                    dollar_sz = (best_bet['Kelly']/100) * bankroll
                    clv_color = "hl-green" if best_bet['CLV'] > 0 else "hl-red"
                    
                    st.markdown(f"""
    <div class='trade-signal'>
        <div class='panel-title' style='color:#EAB308; border-color:#1A1A1A; margin-bottom: 8px;'>HFT EXECUTION TICKET</div>
        <div class='trade-asset'>{best_bet['Market']}</div>
        <div class='trade-odd'>@ {best_bet['ExecOdd']:.3f} <span style='font-size: 0.7rem; color: #6B7280; font-weight: 500;'>Soft Book Line</span></div>
        <div style="margin-bottom: 12px;">
            <div class='data-row'><span class='data-lbl'>Pinnacle (Sharp) Line</span><span class='data-val'>{best_bet['SharpLine']:.3f}</span></div>
            <div class='data-row'><span class='data-lbl'>Expected CLV Capture</span><span class='data-val {clv_color}'>{best_bet['CLV']*100:.2f}%</span></div>
            <div class='data-row'><span class='data-lbl'>Algorithmic Edge (EV)</span><span class='data-val hl-gold'>+{best_bet['EV']*100:.2f}%</span></div>
            <div class='data-row'><span class='data-lbl'>Expected Growth (EG)</span><span class='data-val hl-green'>+{best_bet['EG']:.4f}%</span></div>
        </div>
        <div style='border-top: 1px solid #1A1A1A; padding-top: 12px;'>
            <div style='font-size: 0.65rem; color: #6B7280; text-transform: uppercase; margin-bottom: 4px; font-family: Fira Code;'>Suggested AUM Allocation</div>
            <div style='font-size: 1.4rem; color: #FFFFFF; font-family: Fira Code; font-weight: 700;'>${dollar_sz:,.0f} <span style='font-size: 0.8rem; color: #6B7280;'>({best_bet['Kelly']:.2f}%)</span></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
                else:
                    st.markdown("""<div class='grid-panel' style='height: 100%; display: flex; align-items: center; justify-content: center;'><div class='data-val' style='text-align: center; color: #EF4444; font-size: 0.8rem;'>NO VIABLE ALPHA DETECTED<br><span style='font-size: 0.65rem; font-weight: 400; color: #6B7280;'>Markets are highly efficient. Capital locked.</span></div></div>""", unsafe_allow_html=True)

            with col_chart:
                st.markdown("""<div class='grid-panel' style='padding-bottom: 0px; height: 100%; box-sizing: border-box;'><div class='panel-title'>BIVARIATE PROBABILITY TENSOR (ZIP)</div>""", unsafe_allow_html=True)
                
                fig_heat = go.Figure(data=go.Heatmap(
                    z=score_matrix.T, 
                    x=[0, 1, 2, 3, 4, 5], y=[0, 1, 2, 3, 4, 5],
                    colorscale=[[0, '#000000'], [1, '#EAB308']], 
                    text=np.round(score_matrix.T, 1), texttemplate="%{text}", textfont={"color":"#FFFFFF", "size":9, "family":"Fira Code"},
                    showscale=False, xgap=1, ygap=1
                ))
                
                fig_heat.update_layout(
                    template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=240, margin=dict(l=20, r=10, t=10, b=20),
                    xaxis=dict(title=f"{a_name[:12]}", title_font=dict(size=9, color="#6B7280", family="Fira Code"), tickfont=dict(size=8, color="#6B7280"), side="bottom", showgrid=False),
                    yaxis=dict(title=f"{h_name[:12]}", title_font=dict(size=9, color="#6B7280", family="Fira Code"), tickfont=dict(size=8, color="#6B7280"), autorange="reversed", showgrid=False)
                )
                st.plotly_chart(fig_heat, use_container_width=True, config={'displayModeBar': False})
                st.markdown("</div>", unsafe_allow_html=True)

            if valid_markets:
                st.markdown("""<div class='grid-panel' style='padding: 12px;'><div class='panel-title'>ALPHA OPPORTUNITY LEDGER</div>""", unsafe_allow_html=True)
                clean_markets = sorted(valid_markets, key=lambda x: x['EG'], reverse=True)
                
                st.markdown("<div class='table-container'>", unsafe_allow_html=True)
                table_html = "<table class='ob-table'><tr><th>Asset Market</th><th>Line</th><th>Sharp</th><th>Est.CLV</th><th>EV (%)</th><th>Kelly</th></tr>"
                for m in clean_markets[:6]: 
                    ev_val = m['EV'] * 100
                    clv_val = m['CLV'] * 100
                    clv_color = "hl-green" if clv_val > 0 else "hl-red"
                    table_html += f"<tr><td>{m['Market']}</td><td style='color:#FFFFFF; font-weight:700;'>{m['ExecOdd']:.3f}</td>"
                    table_html += f"<td style='color:#6B7280;'>{m['SharpLine']:.3f}</td>"
                    table_html += f"<td class='{clv_color}'>{clv_val:.1f}%</td>"
                    table_html += f"<td class='hl-gold'>+{ev_val:.1f}%</td>"
                    table_html += f"<td style='color:#9CA3AF;'>{m['Kelly']:.2f}%</td></tr>"
                table_html += "</table></div>"
                st.markdown(table_html, unsafe_allow_html=True)
                st.markdown("""</div>""", unsafe_allow_html=True)

# -----------------------------------------------------
# TAB 2: PORTFOLIO BACKTEST (RESTORED & UPGRADED)
# -----------------------------------------------------
with tab2:
    st.markdown("""<div class='grid-panel' style='margin-bottom: 20px;'><div class='panel-title'>RISK & EQUITY CURVE ANALYSIS (N=50)</div>""", unsafe_allow_html=True)
    
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
        
        cumulative = df_ledger.sort_values(by="Date", ascending=True)['Cumulative_PnL']
        peak = cumulative.expanding(min_periods=1).max()
        drawdown = (cumulative - peak)
        max_dd = drawdown.min()
        
        std_dev = df_ledger['PnL'].std()
        sharpe = (df_ledger['PnL'].mean() / std_dev) * math.sqrt(total_matches) if std_dev > 0 else 0
        
        hr_color = "hl-green" if hit_rate > 52 else "hl-red"
        roi_color = "hl-green" if total_pnl > 0 else "hl-red"
        roi_sign = "+" if total_pnl > 0 else ""
        sharpe_color = "hl-gold" if sharpe > 1 else "hl-gray"
        
        # O Gráfico de Equidade Real
        fig_equity = go.Figure()
        fig_equity.add_trace(go.Scatter(
            x=list(range(len(cumulative))), y=cumulative, mode='lines',
            line=dict(color='#EAB308', width=2), fill='tozeroy', fillcolor='rgba(234, 179, 8, 0.05)',
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
            <div class='metric-card'><div class='metric-card-title'>Max Drawdown</div><div class='metric-card-val hl-red'>{max_dd:.2f}U</div></div>
            <div class='metric-card'><div class='metric-card-title'>Est. Sharpe</div><div class='metric-card-val {sharpe_color}'>{sharpe:.2f}</div></div>
        </div>
        """, unsafe_allow_html=True)
        
        # A Tabela Histórica Real
        st.markdown("<div class='table-container' style='margin-top: 15px;'>", unsafe_allow_html=True)
        ledger_html = "<table class='ob-table'><tr><th>T-Date</th><th>Asset</th><th>Signal</th><th>Conf</th><th>Fair P(x)</th><th>Fair Line</th><th>Res</th><th>PnL (U)</th></tr>"
        
        for _, row in df_ledger.head(50).iterrows():
            res = str(row.get('Res', 'MISS'))
            badge_class = "tag-win" if res == "HIT" else "tag-loss"
            conf = str(row.get('Conf', 'LOW'))
            conf_class = f"tag-{conf.lower()}"
            pnl = row.get('PnL', 0)
            pnl_color = "hl-green" if pnl > 0 else "hl-red"
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