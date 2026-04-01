import streamlit as st
import numpy as np
import pandas as pd
import requests
import math
import plotly.graph_objects as go
from datetime import date, datetime, timedelta
import time

# ==========================================
# 1. INSTITUTIONAL UX SETUP (V22.1 PRO UI)
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
.status-badge { font-size: 0.7rem; font-family: 'JetBrains Mono', monospace; font-weight: 600; padding: 4px 8px; border-radius: 3px; border: 1px solid #30363D; color: #A3B1C6; background: #161B22;}
.status-live { color: #3FB950; border-color: rgba(63,185,80,0.4); background: rgba(63,185,80,0.1); }

/* Grid & Panels */
.grid-panel { border: 1px solid #30363D; background: #161B22; padding: 18px; margin-bottom: 16px; border-radius: 6px; width: 100%; box-sizing: border-box; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }
.panel-title { font-size: 0.75rem; color: #A3B1C6; text-transform: uppercase; border-bottom: 1px solid #21262D; padding-bottom: 8px; margin-bottom: 12px; font-weight: 600; letter-spacing: 0.5px; font-family: 'Inter', sans-serif;}

/* Data Rows */
.data-row { display: flex; justify-content: space-between; font-size: 0.85rem; margin-bottom: 8px; align-items: center; border-bottom: 1px dashed #21262D; padding-bottom: 6px;}
.data-row:last-child { margin-bottom: 0; border-bottom: none; padding-bottom: 0; }
.data-lbl { color: #8B949E; font-weight: 500; font-size: 0.8rem;}
.data-val { color: #E6EDF3; font-weight: 600; font-family: 'JetBrains Mono', monospace; font-size: 0.85rem; }

/* Colors & Outcome Badges */
.hl-green { color: #3FB950 !important; }
.hl-red { color: #F85149 !important; }
.hl-blue { color: #58A6FF !important; }
.hl-gray { color: #8B949E !important; }
.badge-win { background: rgba(63,185,80,0.15); color: #3FB950; border: 1px solid rgba(63,185,80,0.4); padding: 3px 8px; border-radius: 4px; font-weight: 600; font-size: 0.7rem; letter-spacing: 0.5px;}
.badge-loss { background: rgba(248,81,73,0.15); color: #F85149; border: 1px solid rgba(248,81,73,0.4); padding: 3px 8px; border-radius: 4px; font-weight: 600; font-size: 0.7rem; letter-spacing: 0.5px;}

/* Confidence Badges */
.badge-high { color: #58A6FF; font-weight: 700; background: rgba(88, 166, 255, 0.1); padding: 2px 6px; border-radius: 3px; border: 1px solid rgba(88, 166, 255, 0.2); }
.badge-med { color: #A3B1C6; font-weight: 600; background: rgba(163, 177, 198, 0.1); padding: 2px 6px; border-radius: 3px; border: 1px solid rgba(163, 177, 198, 0.2); }
.badge-low { color: #F85149; font-weight: 600; background: rgba(248, 81, 73, 0.1); padding: 2px 6px; border-radius: 3px; border: 1px solid rgba(248, 81, 73, 0.2); }

/* Alerts */
.safe-error { border: 1px solid #F85149; background: rgba(248, 81, 73, 0.1); padding: 16px; border-radius: 6px; text-align: center; margin-bottom: 16px; }
.safe-error-title { color: #F85149; font-weight: 700; font-size: 0.9rem; margin-bottom: 4px; }
.safe-error-msg { color: #C9D1D9; font-size: 0.8rem; }

/* Alpha Box */
.trade-signal { border-left: 3px solid #58A6FF; background: #010409; padding: 20px; margin-bottom: 16px; border-radius: 0 6px 6px 0; box-shadow: inset 0 0 10px rgba(0,0,0,0.5);}
.trade-asset { font-size: 1.25rem; color: #E6EDF3; font-weight: 600; margin-bottom: 4px; font-family: 'Inter', sans-serif;}
.trade-odd { font-size: 1.15rem; color: #58A6FF; font-weight: 700; font-family: 'JetBrains Mono', monospace; margin-bottom: 16px;}

/* Tables */
.table-container { width: 100%; overflow-x: auto; -webkit-overflow-scrolling: touch; margin-bottom: 10px; }
.ob-table { width: 100%; min-width: 700px; font-size: 0.8rem; border-collapse: collapse; font-family: 'JetBrains Mono', monospace; }
.ob-table th { color: #A3B1C6; text-align: right; font-weight: 600; border-bottom: 1px solid #30363D; padding: 10px 8px; font-size: 0.7rem; text-transform: uppercase; background: #010409;}
.ob-table th:first-child { text-align: left; }
.ob-table td { text-align: right; padding: 10px 8px; border-bottom: 1px solid #21262D; color: #C9D1D9;}
.ob-table td:first-child { text-align: left; color: #E6EDF3;}
.ob-table tr { transition: background-color 0.15s ease; }
.ob-table tr:hover td { background: #1C2128; cursor: default;}

/* Grid Cards */
.metric-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 14px; margin-bottom: 16px; }
.metric-card { background: #010409; border: 1px solid #30363D; border-radius: 6px; padding: 14px; text-align: center; transition: border-color 0.2s ease, transform 0.2s ease; }
.metric-card:hover { border-color: #58A6FF; transform: translateY(-2px); }
.metric-card-title { font-size: 0.7rem; color: #A3B1C6; text-transform: uppercase; font-weight: 600; letter-spacing: 0.5px; margin-bottom: 6px;}
.metric-card-val { font-size: 1.5rem; color: #E6EDF3; font-weight: 600; font-family: 'JetBrains Mono', monospace;}

/* Streamlit Overrides */
div[data-baseweb="select"] > div, div[data-baseweb="input"] > div { background-color: #010409 !important; border: 1px solid #30363D !important; color: #E6EDF3 !important; border-radius: 4px !important; font-size: 0.85rem !important;}
.btn-run > button { background: #238636 !important; color: #FFFFFF !important; border: none !important; font-weight: 600 !important; width: 100%; border-radius: 4px !important; padding: 12px !important; font-size: 0.9rem !important; margin-top: 12px; transition: background-color 0.2s ease;}
.btn-run > button:hover { background: #2EA043 !important; }
button[data-baseweb="tab"] { color: #8B949E !important; font-weight: 500 !important; font-size: 0.9rem !important;}
button[data-baseweb="tab"][aria-selected="true"] { color: #E6EDF3 !important; border-bottom-color: #238636 !important;}
.stProgress > div > div > div > div { background-color: #238636 !important; }
div[data-testid="column"] > div { gap: 0rem !important; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. PRO-TIER DATA POOL & MATH ENGINE (V22.1 OPTIMIZED)
# ==========================================
API_KEY = st.secrets.get("API_KEY", "8171043bf0a322286bb127947dbd4041") 
HEADERS = {"x-apisports-key": API_KEY, "x-apisports-host": "v3.football.api-sports.io"}

# Ligas com Maior Ineficiência de Mercado (Maior +EV para Modelos Quants)
GLOBAL_LEAGUES = {
    # Nível 1: Elevada Ineficiência & Boa Liquidez (O paraíso dos apostadores pro)
    "Championship (UK)": 40, "League One (UK)": 41, 
    "2. Bundesliga (DE)": 79, "Serie B (IT)": 136, "La Liga 2 (ES)": 141,
    "MLS (USA)": 253, "J1 League (JP)": 98, "Brasileirão Série A (BR)": 71,
    "Eredivisie (NL)": 88, "Primeira Liga (PT)": 94, "Pro League (BE)": 144,
    # Nível 2: Mercados Eficientes (Menos Edge, mas maior Volume)
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
    
    # Baseline europeia rigorosa para estabilização de inícios de época
    default_stats = {"gf_h": 1.45, "ga_h": 1.15, "gf_a": 1.15, "ga_a": 1.45}
    if not stats: return default_stats 
    
    try:
        goals = stats.get('goals', {}) if isinstance(stats, dict) else stats[0].get('goals', {})
        if not goals: return default_stats
        
        # Leitura com fallback de segurança para evitar divisão por zero
        return {
            "gf_h": max(0.2, float(goals.get('for', {}).get('average', {}).get('home') or 1.45)),
            "ga_h": max(0.2, float(goals.get('against', {}).get('average', {}).get('home') or 1.15)),
            "gf_a": max(0.2, float(goals.get('for', {}).get('average', {}).get('away') or 1.15)),
            "ga_a": max(0.2, float(goals.get('against', {}).get('average', {}).get('away') or 1.45))
        }
    except: return default_stats

def calculate_lambdas(h_stats, a_stats):
    # Cálculo Expectativa de Golos (Ataque da equipa x Defesa do adversário / Média da Liga)
    lam_h = (h_stats['gf_h'] / 1.45) * (a_stats['ga_a'] / 1.45) * 1.45
    lam_a = (a_stats['gf_a'] / 1.15) * (h_stats['ga_h'] / 1.15) * 1.15
    return lam_h, lam_a

def poisson_pmf(lam, k):
    return (lam**k * math.exp(-lam)) / math.factorial(k)

def exact_poisson_matrix(lam_h, lam_a, max_goals=6):
    """
    Tensor Matrix com Correção Dixon-Coles Dinâmica.
    """
    h_probs = [poisson_pmf(lam_h, i) for i in range(max_goals)]
    a_probs = [poisson_pmf(lam_a, i) for i in range(max_goals)]
    
    score_matrix = np.outer(h_probs, a_probs)
    
    # DIXON-COLES RHO DINÂMICO
    # Ajusta o parâmetro de dependência consoante os xG. Jogos com menos xG têm mais empates teóricos.
    rho = max(-0.15, -0.12 + 0.02 * (lam_h + lam_a))
    
    try:
        score_matrix[0, 0] *= max(0, 1 - lam_h * lam_a * rho)
        score_matrix[1, 0] *= max(0, 1 + lam_a * rho)
        score_matrix[0, 1] *= max(0, 1 + lam_h * rho)
        score_matrix[1, 1] *= max(0, 1 - rho)
        # Normalização matemática para a matriz somar exatamente 1.0
        score_matrix = score_matrix / score_matrix.sum()
    except: pass
    
    # Extração Matricial
    hw = np.tril(score_matrix, -1).sum()
    dr = np.trace(score_matrix)
    aw = np.triu(score_matrix, 1).sum()
    
    u15 = np.sum([score_matrix[i, j] for i in range(max_goals) for j in range(max_goals) if i + j < 1.5])
    o15 = 1 - u15
    
    u25 = np.sum([score_matrix[i, j] for i in range(max_goals) for j in range(max_goals) if i + j < 2.5])
    o25 = 1 - u25
    
    u35 = np.sum([score_matrix[i, j] for i in range(max_goals) for j in range(max_goals) if i + j < 3.5])
    o35 = 1 - u35
    
    btts_no = np.sum(score_matrix[0, :]) + np.sum(score_matrix[:, 0]) - score_matrix[0, 0]
    btts_yes = 1 - btts_no
    
    probs = {
        "Home Win": hw, "Draw": dr, "Away Win": aw, 
        "BTTS (Yes)": btts_yes, "BTTS (No)": btts_no,
        "Total Goals Over 1.5": o15, "Total Goals Under 1.5": u15,
        "Total Goals Over 2.5": o25, "Total Goals Under 2.5": u25,
        "Total Goals Over 3.5": o35, "Total Goals Under 3.5": u35
    }
    
    return probs, score_matrix * 100

def power_method_devig(implied_probs):
    """
    Otimizado usando Busca Binária (Bisection Method) para precisão Quant.
    Garante convergência em menos passos e remove a dependência da taxa de aprendizagem.
    """
    if not implied_probs or sum(implied_probs) <= 1.0: return implied_probs 
    
    low, high = 0.0, 1.0
    mid = 1.0
    
    # Converge iterativamente para encontrar a True Probability
    for _ in range(50):
        mid = (low + high) / 2
        current_sum = sum([p**mid for p in implied_probs])
        if abs(current_sum - 1.0) < 0.0001: break
        if current_sum > 1.0: low = mid
        else: high = mid
        
    return [p**mid for p in implied_probs]

def extract_true_odds(market_odds):
    """Remove a margem da casa de apostas usando Devigging Bisectional"""
    true_odds_map = {}
    try:
        if "Home Win" in market_odds and "Draw" in market_odds and "Away Win" in market_odds:
            hw, dr, aw = market_odds["Home Win"], market_odds["Draw"], market_odds["Away Win"]
            if hw > 0 and dr > 0 and aw > 0:
                true_p = power_method_devig([1/hw, 1/dr, 1/aw])
                true_odds_map["Home Win"], true_odds_map["Draw"], true_odds_map["Away Win"] = true_p[0], true_p[1], true_p[2]
        
        for val in ["1.5", "2.5", "3.5"]:
            o_key, u_key = f"Total Goals Over {val}", f"Total Goals Under {val}"
            if o_key in market_odds and u_key in market_odds:
                o_val, u_val = market_odds[o_key], market_odds[u_key]
                if o_val > 0 and u_val > 0:
                    true_p = power_method_devig([1/o_val, 1/u_val])
                    true_odds_map[o_key], true_odds_map[u_key] = true_p[0], true_p[1]
                    
        if "BTTS (Yes)" in market_odds and "BTTS (No)" in market_odds:
            y_val, n_val = market_odds["BTTS (Yes)"], market_odds["BTTS (No)"]
            if y_val > 0 and n_val > 0:
                true_p = power_method_devig([1/y_val, 1/n_val])
                true_odds_map["BTTS (Yes)"], true_odds_map["BTTS (No)"] = true_p[0], true_p[1]
                
    except: pass
    return true_odds_map

def calculate_adjusted_kelly(prob, odd, fraction):
    """Kelly Criterion rigoroso com limite de risco de capital (5%)"""
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
# 2.1 VERIFIED HISTORICAL AUDIT (V22.1 PRO-AUDIT)
# ==========================================
@st.cache_data(ttl=3600)
def get_verified_history(league_id):
    season = get_current_season()
    
    # 1. EXPANSÃO DA AMOSTRA: 100 jogos para garantir Significância Estatística Real
    past_fixtures = fetch_api_safe("fixtures", {"league": league_id, "season": season, "last": 100})
    if not past_fixtures:
        past_fixtures = fetch_api_safe("fixtures", {"league": league_id, "season": str(int(season)-1), "last": 100})
    
    trades = []
    
    if not past_fixtures: return pd.DataFrame()
        
    for f in reversed(past_fixtures):
        try:
            status = f.get('fixture', {}).get('status', {}).get('short', '')
            # Filtro estrito: Apenas jogos concluídos
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
            
            # Recalcula as probabilidades matemáticas usando o Tensor Dixon-Coles atualizado
            h_stats = get_real_stats(h_id, league_id)
            a_stats = get_real_stats(a_id, league_id)
            lam_h, lam_a = calculate_lambdas(h_stats, a_stats)
            sys_probs, _ = exact_poisson_matrix(lam_h, lam_a)
            
            # 2. FILTRO DE CONFIANÇA E VARIÂNCIA
            # Procura mercados com pelo menos 45% de probabilidade pura para reduzir o ruído
            valid_preds = {k: v for k, v in sys_probs.items() if v >= 0.45}
            
            if not valid_preds:
                # Jogo hiper-equilibrado/caótico (Nenhum mercado seguro)
                best_market = max(sys_probs.keys(), key=lambda m: sys_probs.get(m, 0))
                confidence = "LOW"
            else:
                # Seleciona a previsão mais forte e categoriza a confiança
                best_market = max(valid_preds.keys(), key=lambda m: valid_preds.get(m, 0))
                confidence = "HIGH" if sys_probs[best_market] >= 0.60 else "MED"

            pred_prob = sys_probs[best_market]
            
            # 3. COMPARAÇÃO CONTRA A REALIDADE ABSOLUTA
            real_outcomes = []
            if h_goals > a_goals: real_outcomes.append("Home Win")
            elif h_goals < a_goals: real_outcomes.append("Away Win")
            else: real_outcomes.append("Draw")
            
            if (h_goals + a_goals) > 1.5: real_outcomes.append("Total Goals Over 1.5")
            else: real_outcomes.append("Total Goals Under 1.5")
            
            if (h_goals + a_goals) > 2.5: real_outcomes.append("Total Goals Over 2.5")
            else: real_outcomes.append("Total Goals Under 2.5")
            
            if (h_goals + a_goals) > 3.5: real_outcomes.append("Total Goals Over 3.5")
            else: real_outcomes.append("Total Goals Under 3.5")
            
            if h_goals > 0 and a_goals > 0: real_outcomes.append("BTTS (Yes)")
            else: real_outcomes.append("BTTS (No)")
            
            is_win = best_market in real_outcomes
            min_odd = 1 / pred_prob # Odd Justa Mínima (+EV breakpoint)
            
            trades.append({
                "Date": match_date, 
                "Match": f"{h_team} v {a_team}", 
                "Score": f"{int(h_goals)} - {int(a_goals)}",
                "Model Top Pick": best_market, 
                "Conf": confidence,
                "Pred. Prob": f"{pred_prob*100:.1f}%", 
                "Min Fair Odd": round(min_odd, 2), 
                "Outcome": "HIT" if is_win else "MISS"
            })
        except: continue
            
    # Retorna o Ledger ordenado do jogo mais recente para o mais antigo
    df_trades = pd.DataFrame(trades).sort_values(by="Date", ascending=False)
    return df_trades

# ==========================================
# 3. INTERFACE (V22.1 - PRO UI)
# ==========================================
st.markdown(f"""
<div class="top-nav">
    <div class="nav-group">
        <div class="logo">APEX<span>QUANT</span></div>
        <div class="nav-divider"></div>
        <div class="nav-subtitle">CORE ENGINE V22.1<br>DIXON-COLES DYNAMIC</div>
    </div>
    <div class="nav-group">
        <div class="status-badge">MATH: POISSON TENSOR (DC ADJ)</div>
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
        bankroll = st.number_input("Portfolio Size ($)", value=100000, step=10000, format="%d")
        kelly_fraction = st.slider("Kelly Fraction", min_value=0.1, max_value=1.0, value=0.25, step=0.05)
        st.markdown("<div style='height: 1px; background: #21262D; margin: 16px 0;'></div>", unsafe_allow_html=True)

        with st.spinner("Fetching API Data..."):
            fixtures = get_live_fixtures(target_date.strftime('%Y-%m-%d'), league_id)
            
        m_sel = None
        btn_run = False
        
        if fixtures:
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
        else:
            st.markdown("<div style='color:#F85149; font-size:0.85rem; font-weight:600; text-align:center; padding: 12px; border: 1px solid #F85149; border-radius: 4px; background: rgba(248, 81, 73, 0.1); margin-top: 16px;'>NO API FIXTURES AVAILABLE</div>", unsafe_allow_html=True)
            
        st.markdown("</div>", unsafe_allow_html=True)

    if m_sel and btn_run:
        with st.spinner("Calculating Dixon-Coles Probability Tensors..."):
            try:
                h_id = m_sel.get('teams', {}).get('home', {}).get('id')
                a_id = m_sel.get('teams', {}).get('away', {}).get('id')
                h_name = m_sel.get('teams', {}).get('home', {}).get('name', 'Home Team')
                a_name = m_sel.get('teams', {}).get('away', {}).get('name', 'Away Team')
                
                h_stats = get_real_stats(h_id, league_id)
                a_stats = get_real_stats(a_id, league_id)
                
                lam_h, lam_a = calculate_lambdas(h_stats, a_stats)
                sys_probs, score_matrix = exact_poisson_matrix(lam_h, lam_a, max_goals=6)
                
                raw_odds = {}
                raw_odds_api = fetch_api_safe("odds", {"fixture": m_sel['fixture']['id'], "bookmaker": 8})
                
                # Leitura expandida de mercados API
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
                        elif name == 'Both Teams Score':
                            if 'Yes' in vals: raw_odds["BTTS (Yes)"] = vals['Yes']
                            if 'No' in vals: raw_odds["BTTS (No)"] = vals['No']
                
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
                            "Market": mkt, "BookOdd": odd, "SysProb": sys_p, "BookTrueProb": book_true_p,
                            "Edge": edge, "Kelly": kelly_val
                        })
                    
                    safe_bets = [m for m in valid_markets if m['Edge'] > 0.01]
                    if safe_bets: best_bet = max(safe_bets, key=lambda x: x['Kelly'])
                    
            except Exception as e:
                 st.markdown(f"<div class='safe-error'><div class='safe-error-title'>Execution Error</div><div class='safe-error-msg'>Required parameters missing from API. {str(e)}</div></div>", unsafe_allow_html=True)
                 st.stop()
            
        with col_exec:
            b_margin_ui = f"{bookie_margin*100:.1f}%" if bookie_margin else "UNAVAILABLE"
            m_color = "hl-red" if bookie_margin and bookie_margin > 0.08 else "hl-blue"
            
            st.markdown(f"""
            <div class='metric-grid'>
                <div class='metric-card'><div class='metric-card-title'>{h_name} Eval xG</div><div class='metric-card-val'>{lam_h:.2f}</div></div>
                <div class='metric-card'><div class='metric-card-title'>{a_name} Eval xG</div><div class='metric-card-val'>{lam_a:.2f}</div></div>
                <div class='metric-card'><div class='metric-card-title'>Bookmaker Overround</div><div class='metric-card-val {m_color}'>{b_margin_ui}</div></div>
            </div>
            """, unsafe_allow_html=True)

            col_alpha, col_chart = st.columns([1.1, 1], gap="large")
            
            with col_alpha:
                if not raw_odds:
                    st.markdown("""<div class='grid-panel' style='height: 100%; display: flex; align-items: center; justify-content: center;'><div class='data-val' style='text-align: center; color: #8B949E;'>NO MARKET DATA.<br><span style='font-size: 0.8rem; font-weight: 400;'>Strict Mode active. No synthetic odds injected. API lines missing.</span></div></div>""", unsafe_allow_html=True)
                elif best_bet:
                    dollar_sz = (best_bet['Kelly']/100) * bankroll
                    expected_clv = best_bet['Edge'] * 100 * 0.4
                    
                    st.markdown(f"""
    <div class='trade-signal'>
        <div class='panel-title' style='color:#58A6FF; border-color:#21262D; margin-bottom: 12px;'>PRIME EXECUTION SIGNAL</div>
        <div class='trade-asset'>{best_bet['Market']}</div>
        <div class='trade-odd'>@ {best_bet['BookOdd']:.3f}</div>
        <div class='data-row'><span class='data-lbl'>System Pure Probability</span><span class='data-val'>{best_bet['SysProb']*100:.2f}%</span></div>
        <div class='data-row'><span class='data-lbl'>Bookmaker Devig Prob</span><span class='data-val'>{best_bet['BookTrueProb']*100:.2f}%</span></div>
        <div class='data-row'><span class='data-lbl'>Calculated Edge</span><span class='data-val hl-green'>+{best_bet['Edge']*100:.2f}%</span></div>
        <div class='data-row'><span class='data-lbl'>Expected CLV Drop</span><span class='data-val hl-blue'>+{expected_clv:.2f}%</span></div>
        <div class='data-row' style='margin-top:12px; border-top: 1px solid #30363D; padding-top: 12px;'><span class='data-lbl'>Allocation Size</span><span class='data-val'>${dollar_sz:,.0f} ({best_bet['Kelly']:.2f}%)</span></div>
    </div>
    """, unsafe_allow_html=True)
                else:
                    st.markdown("""<div class='grid-panel' style='height: 100%; display: flex; align-items: center; justify-content: center;'><div class='data-val' style='text-align: center; color: #8B949E;'>NEGATIVE EXPECTED VALUE.<br><span style='font-size: 0.8rem; font-weight: 400;'>Market is mathematically efficient. No edge found. Capital protected.</span></div></div>""", unsafe_allow_html=True)

            with col_chart:
                st.markdown("""<div class='grid-panel' style='padding-bottom: 0px; height: 100%; box-sizing: border-box;'><div class='panel-title'>Exact Score Tensor Matrix</div>""", unsafe_allow_html=True)
                
                fig_heat = go.Figure(data=go.Heatmap(
                    z=score_matrix.T, 
                    x=[0, 1, 2, 3, 4, 5], y=[0, 1, 2, 3, 4, 5],
                    colorscale=[[0, '#0D1117'], [1, '#238636']], 
                    text=np.round(score_matrix.T, 1), texttemplate="%{text}%", textfont={"color":"white", "size":10, "family":"JetBrains Mono"},
                    showscale=False, xgap=2, ygap=2
                ))
                
                fig_heat.update_layout(
                    template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=260, margin=dict(l=30, r=10, t=10, b=30),
                    xaxis=dict(title=f"{a_name}", title_font=dict(size=10, color="#8B949E"), tickfont=dict(size=10, color="#8B949E"), side="bottom"),
                    yaxis=dict(title=f"{h_name}", title_font=dict(size=10, color="#8B949E"), tickfont=dict(size=10, color="#8B949E"), autorange="reversed")
                )
                st.plotly_chart(fig_heat, use_container_width=True, config={'displayModeBar': False})
                st.markdown("</div>", unsafe_allow_html=True)

            if valid_markets:
                st.markdown("""<div class='grid-panel'><div class='panel-title'>Mathematical Pricing Matrix</div>""", unsafe_allow_html=True)
                clean_markets = sorted(valid_markets, key=lambda x: x['SysProb'], reverse=True)
                
                st.markdown("<div class='table-container'>", unsafe_allow_html=True)
                table_html = "<table class='ob-table'><tr><th>Market</th><th>Live Odd</th><th>Sys Prob</th><th>Edge</th><th>Rec. Size</th></tr>"
                for m in clean_markets[:8]: 
                    edge_val = m['Edge'] * 100
                    e_color = "hl-green" if edge_val > 0 else "hl-red"
                    e_sign = "+" if edge_val > 0 else ""
                    table_html += f"<tr><td>{m['Market']}</td><td style='color:#58A6FF; font-weight:700;'>{m['BookOdd']:.3f}</td>"
                    table_html += f"<td>{m['SysProb']*100:.1f}%</td>"
                    table_html += f"<td class='{e_color}'>{e_sign}{edge_val:.2f}%</td>"
                    table_html += f"<td style='color:#8B949E;'>{m['Kelly']:.2f}%</td></tr>"
                table_html += "</table></div>"
                st.markdown(table_html, unsafe_allow_html=True)
                st.markdown("""</div>""", unsafe_allow_html=True)

# -----------------------------------------------------
# TAB 2: PURE PREDICTIVE AUDIT (V22.1 ENHANCED ANALYTICS)
# -----------------------------------------------------
with tab2:
    st.markdown("""<div class='grid-panel' style='margin-bottom: 20px;'><div class='panel-title'>Model Predictive Accuracy (100 Matches Deep Audit)</div>""", unsafe_allow_html=True)
    
    with st.spinner(f"Evaluating Deterministic Model Accuracy against historical outcomes for {league_name}..."):
        try:
            df_ledger = get_verified_history(GLOBAL_LEAGUES[league_name])
        except Exception as e:
            df_ledger = pd.DataFrame()
            st.markdown("""<div class='safe-error'><div class='safe-error-title'>API LIMIT REACHED</div><div class='safe-error-msg'>Unable to fetch historical ledger. Check your API-Sports quota.</div></div>""", unsafe_allow_html=True)
    
    if len(df_ledger) > 0:
        # 1. Base Metrics
        total_matches = len(df_ledger)
        hits = len(df_ledger[df_ledger['Outcome'] == 'HIT'])
        hit_rate = (hits / total_matches) * 100 if total_matches > 0 else 0
        
        # 2. High-Conviction Metrics (The Real Edge)
        df_high = df_ledger[df_ledger['Conf'] == 'HIGH']
        high_matches = len(df_high)
        high_hits = len(df_high[df_high['Outcome'] == 'HIT'])
        high_hr = (high_hits / high_matches) * 100 if high_matches > 0 else 0
        
        # 3. Theoretical Flat Yield (ROI assuming 1 Unit per bet at Min Fair Odd)
        theo_profit = 0.0
        brier_sum = 0.0
        for _, row in df_ledger.iterrows():
            # Profitability calc
            if row['Outcome'] == 'HIT':
                theo_profit += (row['Min Fair Odd'] - 1.0)
            else:
                theo_profit -= 1.0
                
            # Brier Score calc
            prob_str = row['Pred. Prob'].replace('%', '')
            prob = float(prob_str) / 100
            actual = 1.0 if row['Outcome'] == 'HIT' else 0.0
            brier_sum += (prob - actual)**2
            
        brier_score = brier_sum / total_matches if total_matches > 0 else 0
        roi_pct = (theo_profit / total_matches) * 100 if total_matches > 0 else 0
        
        # Colors based on performance
        hr_color = "hl-green" if hit_rate > 50 else "hl-red"
        high_hr_color = "hl-green" if high_hr > 55 else "hl-gray"
        roi_color = "hl-green" if roi_pct > 0 else "hl-red"
        roi_sign = "+" if roi_pct > 0 else ""
        
        st.markdown(f"""
        <div class='metric-grid' style='grid-template-columns: repeat(5, 1fr);'>
            <div class='metric-card'><div class='metric-card-title'>Matches Validated</div><div class='metric-card-val' style='color:#E6EDF3;'>{total_matches}</div></div>
            <div class='metric-card'><div class='metric-card-title'>Global Hit Rate</div><div class='metric-card-val {hr_color}'>{hit_rate:.1f}%</div></div>
            <div class='metric-card'><div class='metric-card-title'>High-Conf Hit Rate</div><div class='metric-card-val {high_hr_color}'>{high_hr:.1f}%</div></div>
            <div class='metric-card'><div class='metric-card-title'>Theo. Yield (ROI)</div><div class='metric-card-val {roi_color}'>{roi_sign}{roi_pct:.1f}%</div></div>
            <div class='metric-card'><div class='metric-card-title'>Brier Score</div><div class='metric-card-val hl-blue'>{brier_score:.3f}</div></div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<div class='table-container' style='margin-top: 15px;'>", unsafe_allow_html=True)
        ledger_html = "<table class='ob-table'><tr><th>Date</th><th>Match</th><th>Final Score</th><th>Model Top Pick</th><th>Conf</th><th>Pred. Prob</th><th>Min Fair Odd</th><th>Outcome</th></tr>"
        
        for _, row in df_ledger.head(100).iterrows():
            res = str(row.get('Outcome', 'MISS'))
            badge_class = "badge-win" if res == "HIT" else "badge-loss"
            
            # Formatação visual da Confiança
            conf = str(row.get('Conf', 'LOW'))
            conf_color = "#58A6FF" if conf == "HIGH" else ("#8B949E" if conf == "MED" else "#F85149")
            
            ledger_html += f"<tr>"
            ledger_html += f"<td style='color:#8B949E; font-size: 0.75rem;'>{row.get('Date', '')}</td>"
            ledger_html += f"<td>{row.get('Match', '')}</td>"
            ledger_html += f"<td style='color:#E6EDF3; font-weight:600;'>{row.get('Score', '')}</td>"
            ledger_html += f"<td>{row.get('Model Top Pick', '')}</td>"
            ledger_html += f"<td style='color:{conf_color}; font-weight:700;'>{conf}</td>"
            ledger_html += f"<td style='color:#E6EDF3;'>{row.get('Pred. Prob', '')}</td>"
            ledger_html += f"<td style='color:#8B949E; font-family: JetBrains Mono;'>{row.get('Min Fair Odd', 0):.2f}</td>"
            ledger_html += f"<td><span class='{badge_class}'>{res}</span></td>"
            ledger_html += f"</tr>"
        ledger_html += "</table></div>"
        
        st.markdown(ledger_html, unsafe_allow_html=True)
        
        st.markdown("""
        <div style='color: #8B949E; font-size: 0.75rem; border-top: 1px solid #21262D; padding-top: 12px; margin-top: 24px;'>
        <strong>Strict Audit Notes:</strong> The "Conf" (Confidence) metric categorizes the predictive edge. HIGH (>60%), MED (45-60%), LOW (<45%). High variance games with LOW confidence should traditionally be avoided. <strong>Theo. Yield</strong> calculates the simulated Return on Investment assuming a 1-unit flat stake executed perfectly at the calculated Min Fair Odd.
        </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""<div class='grid-panel'><div class='data-lbl' style='text-align:center;'>No historical data available. Check API Quotas.</div></div>""", unsafe_allow_html=True)