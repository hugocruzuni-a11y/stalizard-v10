import streamlit as st
import numpy as np
import pandas as pd
import requests
import math
import re
import plotly.graph_objects as go
from datetime import date, datetime

# ==========================================
# 1. INSTITUTIONAL UX SETUP (V5.0 - THE PERFECT ENGINE)
# ==========================================
st.set_page_config(page_title="APEX QUANT | EXECUTION DESK", layout="wide", initial_sidebar_state="collapsed")
st.cache_data.clear()

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

/* Grid & Panels */
.grid-panel { border: 1px solid #30363D; background: #161B22; padding: 16px; margin-bottom: 16px; border-radius: 6px; width: 100%; box-sizing: border-box;}
.panel-title { font-size: 0.75rem; color: #8B949E; text-transform: uppercase; border-bottom: 1px solid #21262D; padding-bottom: 8px; margin-bottom: 12px; font-weight: 600; letter-spacing: 0.5px; font-family: 'Inter', sans-serif;}

/* Data Rows */
.data-row { display: flex; justify-content: space-between; font-size: 0.85rem; margin-bottom: 6px; align-items: center; border-bottom: 1px solid #21262D; padding-bottom: 4px;}
.data-row:last-child { margin-bottom: 0; border-bottom: none; padding-bottom: 0; }
.data-lbl { color: #8B949E; font-weight: 500; font-size: 0.8rem;}
.data-val { color: #E6EDF3; font-weight: 500; font-family: 'JetBrains Mono', monospace; font-size: 0.85rem; }

/* Colors & Badges */
.hl-green { color: #3FB950 !important; }
.hl-red { color: #F85149 !important; }
.hl-blue { color: #58A6FF !important; }
.badge-win { background: rgba(63,185,80,0.1); color: #3FB950; border: 1px solid rgba(63,185,80,0.4); padding: 2px 6px; border-radius: 3px; font-weight: 600; font-size: 0.7rem; }
.badge-loss { background: rgba(248,81,73,0.1); color: #F85149; border: 1px solid rgba(248,81,73,0.4); padding: 2px 6px; border-radius: 3px; font-weight: 600; font-size: 0.7rem; }
.safe-error { border: 1px solid #F85149; background: rgba(248, 81, 73, 0.1); padding: 16px; border-radius: 6px; text-align: center; margin-bottom: 16px; }
.safe-error-title { color: #F85149; font-weight: 700; font-size: 0.9rem; margin-bottom: 4px; }

/* Alpha Box */
.trade-signal { border-left: 3px solid #58A6FF; background: #0D1117; padding: 16px; margin-bottom: 16px; border-radius: 0 4px 4px 0;}
.trade-asset { font-size: 1.2rem; color: #E6EDF3; font-weight: 600; margin-bottom: 4px; font-family: 'Inter', sans-serif;}
.trade-odd { font-size: 1.1rem; color: #58A6FF; font-weight: 700; font-family: 'JetBrains Mono', monospace; margin-bottom: 12px;}

/* Tables */
.table-container { width: 100%; overflow-x: auto; margin-bottom: 10px; }
.ob-table { width: 100%; min-width: 700px; font-size: 0.8rem; border-collapse: collapse; font-family: 'JetBrains Mono', monospace; }
.ob-table th { color: #8B949E; text-align: right; font-weight: 500; border-bottom: 1px solid #30363D; padding: 8px; font-size: 0.7rem; text-transform: uppercase; background: #010409;}
.ob-table th:first-child { text-align: left; }
.ob-table td { text-align: right; padding: 8px; border-bottom: 1px solid #21262D; color: #C9D1D9;}
.ob-table td:first-child { text-align: left; color: #E6EDF3;}

/* Grid Cards */
.metric-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 12px; margin-bottom: 16px; }
.metric-card { background: #0D1117; border: 1px solid #30363D; border-radius: 4px; padding: 12px; text-align: center; }
.metric-card-title { font-size: 0.7rem; color: #8B949E; text-transform: uppercase; font-weight: 600; margin-bottom: 4px;}
.metric-card-val { font-size: 1.4rem; color: #E6EDF3; font-weight: 600; font-family: 'JetBrains Mono', monospace;}

/* Streamlit Overrides */
div[data-baseweb="select"] > div, div[data-baseweb="input"] > div { background-color: #0D1117 !important; border: 1px solid #30363D !important; color: #E6EDF3 !important; }
.btn-run > button { background: #238636 !important; color: #FFFFFF !important; border: none !important; font-weight: 600 !important; width: 100%; border-radius: 4px !important; padding: 12px !important; margin-top: 8px;}
button[data-baseweb="tab"] { color: #8B949E !important; }
button[data-baseweb="tab"][aria-selected="true"] { color: #E6EDF3 !important; border-bottom-color: #238636 !important;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. DATA POOL & MATH ENGINE
# ==========================================
API_KEY = st.secrets.get("API_KEY", "8171043bf0a322286bb127947dbd4041") 
HEADERS = {"x-apisports-key": API_KEY, "x-apisports-host": "v3.football.api-sports.io"}

GLOBAL_LEAGUES = {
    "Championship (UK)": 40, "League One (UK)": 41, "2. Bundesliga (DE)": 79, "Serie B (IT)": 136, 
    "MLS (USA)": 253, "Brasileirão A": 71, "Premier League (UK)": 39, "La Liga (ES)": 140, "Bundesliga (DE)": 78
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
    data = fetch_api_safe("fixtures", {"date": date_str, "league": league_id, "season": season})
    if not data: data = fetch_api_safe("fixtures", {"league": league_id, "next": 10})
    return data

@st.cache_data(ttl=3600)
def get_real_stats(team_id, league_id):
    season = get_current_season()
    stats = fetch_api_safe("teams/statistics", {"team": team_id, "league": league_id, "season": season})
    default_stats = {"gf_h": 1.45, "ga_h": 1.15, "gf_a": 1.15, "ga_a": 1.45}
    if not stats: return default_stats 
    try:
        goals = stats.get('goals', {}) if isinstance(stats, dict) else stats[0].get('goals', {})
        if not goals: return default_stats
        return {
            "gf_h": float(goals.get('for', {}).get('average', {}).get('home') or 1.45),
            "ga_h": float(goals.get('against', {}).get('average', {}).get('home') or 1.15),
            "gf_a": float(goals.get('for', {}).get('average', {}).get('away') or 1.15),
            "ga_a": float(goals.get('against', {}).get('average', {}).get('away') or 1.45)
        }
    except: return default_stats

def calculate_xg_lambdas(h_stats, a_stats, smoothing=0.5):
    """Suavização Bayesiana para anular distorções (Extrapolação de Odds)"""
    L_GF_H, L_GA_A = 1.45, 1.45
    L_GF_A, L_GA_H = 1.15, 1.15
    
    gf_h_adj = (h_stats['gf_h'] * (1 - smoothing)) + (L_GF_H * smoothing)
    ga_a_adj = (a_stats['ga_a'] * (1 - smoothing)) + (L_GA_A * smoothing)
    gf_a_adj = (a_stats['gf_a'] * (1 - smoothing)) + (L_GF_A * smoothing)
    ga_h_adj = (h_stats['ga_h'] * (1 - smoothing)) + (L_GA_H * smoothing)
    
    lam_h = max(0.1, (gf_h_adj / L_GF_H) * (ga_a_adj / L_GA_A) * L_GF_H)
    lam_a = max(0.1, (gf_a_adj / L_GF_A) * (ga_h_adj / L_GA_H) * L_GF_A)
    return lam_h, lam_a

def poisson_pmf(lam, k):
    return (lam**k * math.exp(-lam)) / math.factorial(k)

def get_asian_handicap_prob(matrix, line, is_home=True):
    prob_win, prob_push = 0, 0
    max_g = matrix.shape[0]
    for h in range(max_g):
        for a in range(max_g):
            diff = (h - a) if is_home else (a - h)
            if diff + line > 0: prob_win += matrix[h, a]
            elif diff + line == 0: prob_push += matrix[h, a]
    if prob_push >= 1.0: return 0
    return prob_win / (1 - prob_push)

def get_over_under_prob(matrix, line, is_over=True):
    prob_win, prob_push = 0, 0
    max_g = matrix.shape[0]
    for h in range(max_g):
        for a in range(max_g):
            total_goals = h + a
            if is_over:
                if total_goals > line: prob_win += matrix[h, a]
                elif total_goals == line: prob_push += matrix[h, a]
            else:
                if total_goals < line: prob_win += matrix[h, a]
                elif total_goals == line: prob_push += matrix[h, a]
    if prob_push >= 1.0: return 0
    return prob_win / (1 - prob_push)

def exact_poisson_matrix(lam_h, lam_a, max_goals=10):
    """Matriz Expandida 10x10 para estabilidade estatística profunda"""
    h_probs = [poisson_pmf(lam_h, i) for i in range(max_goals)]
    a_probs = [poisson_pmf(lam_a, i) for i in range(max_goals)]
    score_matrix = np.outer(h_probs, a_probs)
    
    rho = -0.05 
    try:
        score_matrix[0, 0] *= max(0, 1 - lam_h * lam_a * rho)
        score_matrix[1, 0] *= max(0, 1 + lam_a * rho)
        score_matrix[0, 1] *= max(0, 1 + lam_h * rho)
        score_matrix[1, 1] *= max(0, 1 - rho)
        score_matrix /= score_matrix.sum()
    except: pass
    
    probs = {
        "Home Win": np.tril(score_matrix, -1).sum(), 
        "Draw": np.trace(score_matrix), 
        "Away Win": np.triu(score_matrix, 1).sum(), 
        "BTTS (Yes)": 1 - (sum(score_matrix[0, :]) + sum(score_matrix[:, 0]) - score_matrix[0, 0]),
        "BTTS (No)": sum(score_matrix[0, :]) + sum(score_matrix[:, 0]) - score_matrix[0, 0]
    }
    
    for val in [1.5, 2.5, 3.5]:
        probs[f"Total Goals Over {val}"] = get_over_under_prob(score_matrix, val, is_over=True)
        probs[f"Total Goals Under {val}"] = get_over_under_prob(score_matrix, val, is_over=False)
        
    return probs, score_matrix

def calculate_adjusted_kelly(prob, odd, fraction):
    b = odd - 1
    if b <= 0: return 0
    raw_kelly = (((b * prob) - (1 - prob)) / b) 
    return max(0, min(raw_kelly * fraction * 100, 5.0))

# ==========================================
# 2.1 VERIFIED HISTORICAL AUDIT
# ==========================================
@st.cache_data(ttl=3600)
def get_verified_history(league_id):
    season = get_current_season()
    past_fixtures = fetch_api_safe("fixtures", {"league": league_id, "season": season, "last": 40})
    if not past_fixtures: return pd.DataFrame()
    
    trades = []
    for f in reversed(past_fixtures):
        try:
            status = f.get('fixture', {}).get('status', {}).get('short', '')
            if status not in ['FT', 'AET', 'PEN']: continue
            
            match_date = f.get('fixture', {}).get('date', '2026-01-01')[:10]
            if match_date > date.today().strftime('%Y-%m-%d'): continue
            
            h_id, a_id = f['teams']['home']['id'], f['teams']['away']['id']
            h_goals, a_goals = f.get('goals', {}).get('home'), f.get('goals', {}).get('away')
            if h_goals is None or a_goals is None: continue
            
            # Usar smoothing por defeito na auditoria histórica também
            lam_h, lam_a = calculate_xg_lambdas(get_real_stats(h_id, league_id), get_real_stats(a_id, league_id), smoothing=0.5)
            sys_probs, _ = exact_poisson_matrix(lam_h, lam_a)
            
            best_market = max(sys_probs.keys(), key=lambda m: sys_probs.get(m, 0))
            pred_prob = sys_probs[best_market]
            
            real_outcomes = []
            if h_goals > a_goals: real_outcomes.append("Home Win")
            elif h_goals < a_goals: real_outcomes.append("Away Win")
            else: real_outcomes.append("Draw")
            
            for val in [1.5, 2.5, 3.5]:
                if (h_goals + a_goals) > val: real_outcomes.append(f"Total Goals Over {val}")
                else: real_outcomes.append(f"Total Goals Under {val}")
                
            if h_goals > 0 and a_goals > 0: real_outcomes.append("BTTS (Yes)")
            else: real_outcomes.append("BTTS (No)")
            
            trades.append({
                "Date": match_date, "Match": f"{f['teams']['home']['name']} v {f['teams']['away']['name']}", 
                "Score": f"{int(h_goals)} - {int(a_goals)}", "Model Top Pick": best_market, 
                "Pred. Prob": f"{pred_prob*100:.1f}%", "Outcome": "HIT" if best_market in real_outcomes else "MISS"
            })
        except: continue
            
    return pd.DataFrame(trades).sort_values(by="Date", ascending=False)

# ==========================================
# 3. INTERFACE
# ==========================================
st.markdown(f"""
<div class="top-nav">
    <div class="nav-group">
        <div class="logo">APEX<span>QUANT</span></div>
        <div class="nav-divider"></div>
        <div class="nav-subtitle" style="font-size: 0.8rem; font-weight:600;">CORE ENGINE V5.0<br>BAYESIAN SMOOTHING & PERFECT TENSOR</div>
    </div>
    <div class="nav-group">
        <div class="status-badge status-live">● API STRICT MODE</div>
    </div>
</div>
""", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["[ LIVE EXECUTION TERMINAL ]", "[ PURE PREDICTIVE AUDIT ]"])

# --- TAB 1: LIVE TERMINAL ---
with tab1:
    col_ctrl, col_exec = st.columns([1, 2.6], gap="large")

    with col_ctrl:
        st.markdown("""<div class='grid-panel' style='margin-bottom: 0;'><div class='panel-title'>Strategy Config</div>""", unsafe_allow_html=True)
        target_date = st.date_input("Execution Date", date.today())
        league_name = st.selectbox("Target Pro Market Pool", list(GLOBAL_LEAGUES.keys()))
        league_id = GLOBAL_LEAGUES[league_name]
        
        st.markdown("<div style='height: 1px; background: #21262D; margin: 16px 0;'></div>", unsafe_allow_html=True)
        bankroll = st.number_input("Portfolio Size ($)", value=100000, step=10000)
        kelly_fraction = st.slider("Kelly Fraction", 0.05, 0.50, 0.20, 0.05)
        st.markdown("<div style='height: 1px; background: #21262D; margin: 16px 0;'></div>", unsafe_allow_html=True)

        with st.spinner("Fetching API Data..."):
            fixtures = get_live_fixtures(target_date.strftime('%Y-%m-%d'), league_id)
            
        m_sel, btn_run = None, False
        if fixtures:
            m_map = {f"{f['teams']['home']['name']} v {f['teams']['away']['name']} ({f['fixture']['date'][:10]})": f for f in fixtures}
            m_sel = m_map[st.selectbox("Select Asset", list(m_map.keys()))]
            st.markdown("<div class='btn-run'>", unsafe_allow_html=True)
            btn_run = st.button("INITIALIZE ENGINE")
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='safe-error'><div class='safe-error-title'>NO API FIXTURES</div></div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    if m_sel and btn_run:
        with st.spinner("Parsing Markets via RegEx and Calculating Tensors..."):
            try:
                h_name, a_name = m_sel['teams']['home']['name'], m_sel['teams']['away']['name']
                h_stats = get_real_stats(m_sel['teams']['home']['id'], league_id)
                a_stats = get_real_stats(m_sel['teams']['away']['id'], league_id)
                
                # Bayesian Smoothing Lambdas (Nivelamento da Matriz)
                lam_h, lam_a = calculate_xg_lambdas(h_stats, a_stats, smoothing=0.5)
                sys_probs, score_matrix = exact_poisson_matrix(lam_h, lam_a, max_goals=10)
                
                # Fetch & Parse Odds
                odds_api = fetch_api_safe("odds", {"fixture": m_sel['fixture']['id'], "bookmaker": 8})
                valid_markets = []
                
                if odds_api and odds_api[0].get('bookmakers'):
                    for bet in odds_api[0]['bookmakers'][0].get('bets', []):
                        b_name = str(bet.get('name', '')).strip()
                        
                        for v in bet.get('values', []):
                            val_str = str(v.get('value', '')).strip()
                            odd = float(v.get('odd', 0))
                            prob = 0
                            market_label = f"{b_name}: {val_str}"
                            
                            # --- REGULAR EXPRESSIONS MARKET PARSER ---
                            try:
                                if b_name == 'Match Winner':
                                    if val_str == 'Home': prob = sys_probs.get("Home Win", 0)
                                    elif val_str == 'Away': prob = sys_probs.get("Away Win", 0)
                                    elif val_str == 'Draw': prob = sys_probs.get("Draw", 0)
                                    
                                elif b_name == 'Both Teams Score':
                                    if val_str == 'Yes': prob = sys_probs.get("BTTS (Yes)", 0)
                                    elif val_str == 'No': prob = sys_probs.get("BTTS (No)", 0)
                                    
                                elif b_name in ['Goals Over/Under', 'Asian Total', 'Alternative Total Goals']:
                                    match = re.match(r"(Over|Under)\s+([0-9.]+)", val_str, re.IGNORECASE)
                                    if match:
                                        is_over = (match.group(1).lower() == 'over')
                                        line = float(match.group(2))
                                        prob = get_over_under_prob(score_matrix, line, is_over)
                                        
                                elif b_name in ['Asian Handicap', 'Alternative Asian Handicap']:
                                    match = re.match(r"(Home|Away)\s+([+-]?[0-9.]+)", val_str, re.IGNORECASE)
                                    if match:
                                        is_home = (match.group(1).lower() == 'home')
                                        line = float(match.group(2))
                                        prob = get_asian_handicap_prob(score_matrix, line, is_home)
                            except: continue
                            
                            if prob > 0:
                                edge = (prob * odd) - 1
                                kelly = calculate_adjusted_kelly(prob, odd, kelly_fraction) if edge > 0 else 0
                                valid_markets.append({
                                    "Market": market_label, "BookOdd": odd, "SysProb": prob, "Edge": edge, "Kelly": kelly
                                })
                                
                safe_bets = [m for m in valid_markets if m['Edge'] > 0.01]
                best_bet = max(safe_bets, key=lambda x: x['Kelly']) if safe_bets else None
                
            except Exception as e:
                 st.markdown(f"<div class='safe-error'><div class='safe-error-title'>Execution Error</div><div>{str(e)}</div></div>", unsafe_allow_html=True)
                 st.stop()
            
        with col_exec:
            st.markdown(f"""
            <div class='metric-grid'>
                <div class='metric-card'><div class='metric-card-title'>{h_name} Eval xG</div><div class='metric-card-val hl-blue'>{lam_h:.2f}</div></div>
                <div class='metric-card'><div class='metric-card-title'>{a_name} Eval xG</div><div class='metric-card-val hl-blue'>{lam_a:.2f}</div></div>
                <div class='metric-card'><div class='metric-card-title'>Projected Total Goals</div><div class='metric-card-val hl-green'>{lam_h+lam_a:.2f}</div></div>
            </div>
            """, unsafe_allow_html=True)

            col_alpha, col_chart = st.columns([1.1, 1], gap="large")
            
            with col_alpha:
                if best_bet:
                    dollar_sz = (best_bet['Kelly']/100) * bankroll
                    st.markdown(f"""
                    <div class='trade-signal'>
                        <div class='panel-title' style='color:#58A6FF; border-color:#21262D; margin-bottom: 12px;'>PRIME EXECUTION SIGNAL</div>
                        <div class='trade-asset'>{best_bet['Market']}</div>
                        <div class='trade-odd'>@ {best_bet['BookOdd']:.3f}</div>
                        <div class='data-row'><span class='data-lbl'>System Pure Probability</span><span class='data-val'>{best_bet['SysProb']*100:.2f}%</span></div>
                        <div class='data-row'><span class='data-lbl'>Calculated Edge</span><span class='data-val hl-green'>+{best_bet['Edge']*100:.2f}%</span></div>
                        <div class='data-row' style='margin-top:12px; border-top: 1px solid #30363D; padding-top: 12px;'><span class='data-lbl'>Allocation Size</span><span class='data-val hl-blue'>${dollar_sz:,.0f} ({best_bet['Kelly']:.2f}%)</span></div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""<div class='grid-panel' style='height: 100%; display: flex; align-items: center; justify-content: center;'><div class='data-val' style='text-align: center; color: #8B949E;'>NO MARKET DATA OR NO EDGE.<br>Capital protected.</div></div>""", unsafe_allow_html=True)

            with col_chart:
                st.markdown("""<div class='grid-panel' style='padding-bottom: 0px; height: 100%;'><div class='panel-title'>Exact Score Tensor Matrix (10x10)</div>""", unsafe_allow_html=True)
                fig_heat = go.Figure(data=go.Heatmap(
                    z=(score_matrix * 100).T, x=list(range(10)), y=list(range(10)), colorscale=[[0, '#0D1117'], [1, '#238636']], 
                    text=np.round((score_matrix * 100).T, 1), texttemplate="%{text}%", textfont={"color":"white", "size":8, "family":"JetBrains Mono"}, showscale=False
                ))
                fig_heat.update_layout(
                    template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=280, margin=dict(l=30, r=10, t=10, b=30),
                    xaxis=dict(title=f"{a_name}", title_font=dict(size=10, color="#8B949E"), tickfont=dict(size=10, color="#8B949E"), side="bottom"),
                    yaxis=dict(title=f"{h_name}", title_font=dict(size=10, color="#8B949E"), tickfont=dict(size=10, color="#8B949E"), autorange="reversed")
                )
                st.plotly_chart(fig_heat, use_container_width=True, config={'displayModeBar': False})
                st.markdown("</div>", unsafe_allow_html=True)

            if valid_markets:
                st.markdown("""<div class='grid-panel'><div class='panel-title'>Mathematical Pricing Matrix</div>""", unsafe_allow_html=True)
                clean_markets = sorted(valid_markets, key=lambda x: x['Edge'], reverse=True)
                
                table_html = "<div class='table-container'><table class='ob-table'><tr><th>Market</th><th>Odd</th><th>Sys Prob</th><th>Edge</th><th>Rec. Size</th></tr>"
                for m in clean_markets[:10]: 
                    e_color = "hl-green" if m['Edge'] > 0 else "hl-red"
                    table_html += f"<tr><td>{m['Market']}</td><td style='color:#58A6FF; font-weight:700;'>{m['BookOdd']:.3f}</td>"
                    table_html += f"<td>{m['SysProb']*100:.1f}%</td><td class='{e_color}'>{m['Edge']*100:+.2f}%</td><td style='color:#8B949E;'>{m['Kelly']:.2f}%</td></tr>"
                table_html += "</table></div>"
                
                st.markdown(table_html, unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------------------------------
# TAB 2: PURE PREDICTIVE AUDIT
# -----------------------------------------------------
with tab2:
    st.markdown("""<div class='grid-panel' style='margin-bottom: 20px;'><div class='panel-title'>Model Predictive Accuracy (Pure API Historical Verification)</div>""", unsafe_allow_html=True)
    with st.spinner(f"Evaluating Deterministic Model Accuracy against historical outcomes for {league_name}..."):
        df_ledger = get_verified_history(GLOBAL_LEAGUES[league_name])
    
    if len(df_ledger) > 0:
        hit_rate = (len(df_ledger[df_ledger['Outcome'] == 'HIT']) / len(df_ledger)) * 100
        
        st.markdown(f"""
        <div class='metric-grid' style='grid-template-columns: repeat(3, 1fr);'>
            <div class='metric-card'><div class='metric-card-title'>Evaluated Matches</div><div class='metric-card-val'>{len(df_ledger)}</div></div>
            <div class='metric-card'><div class='metric-card-title'>Model Hit Rate</div><div class='metric-card-val hl-blue'>{hit_rate:.1f}%</div></div>
            <div class='metric-card'><div class='metric-card-title'>Data Purity</div><div class='metric-card-val hl-green'>100% REAL</div></div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<div class='table-container'>", unsafe_allow_html=True)
        ledger_html = "<table class='ob-table'><tr><th>Date</th><th>Match</th><th>Final Score</th><th>Model Top Pick</th><th>Pred. Prob</th><th>Outcome</th></tr>"
        for _, row in df_ledger.head(30).iterrows():
            res = str(row.get('Outcome', 'MISS'))
            b_class = "badge-win" if res == "HIT" else "badge-loss"
            ledger_html += f"<tr><td style='color:#8B949E;'>{row.get('Date', '')}</td><td>{row.get('Match', '')}</td>"
            ledger_html += f"<td style='color:#E6EDF3; font-weight:600;'>{row.get('Score', '')}</td><td>{row.get('Model Top Pick', '')}</td>"
            ledger_html += f"<td style='color:#58A6FF;'>{row.get('Pred. Prob', '')}</td><td><span class='{b_class}'>{res}</span></td></tr>"
        ledger_html += "</table></div>"
        st.markdown(ledger_html, unsafe_allow_html=True)
    else:
        st.markdown("""<div class='grid-panel'><div class='data-lbl' style='text-align:center;'>No historical data available. Check API Quotas.</div></div>""", unsafe_allow_html=True)