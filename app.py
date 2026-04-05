import streamlit as st
import numpy as np
import pandas as pd
import requests
import math
import plotly.graph_objects as go
from datetime import datetime
import time
import random

# ==========================================
# 1. QUANTUM CYBERNETICS UI (2050 ENGINE)
# ==========================================
st.set_page_config(page_title="APEX QUANT | OMNI-TERMINAL", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;700;900&family=Rajdhani:wght@300;500;600;700&family=Share+Tech+Mono&display=swap');

:root {
    --bg-deep: #010205;
    --glass-bg: rgba(6, 11, 25, 0.65);
    --glass-border: rgba(0, 255, 204, 0.15);
    --neon-cyan: #00FFCC;
    --neon-purple: #B026FF;
    --neon-gold: #FFC107;
    --neon-red: #FF2A55;
    --neon-green: #00FF66;
    --text-main: #E2E8F0;
    --text-dim: #64748B;
}

/* Background & Core */
.stApp { 
    background-color: var(--bg-deep); 
    background-image: 
        radial-gradient(circle at 10% 20%, rgba(0, 255, 204, 0.04), transparent 40%),
        radial-gradient(circle at 90% 80%, rgba(176, 38, 255, 0.04), transparent 40%),
        linear-gradient(rgba(255,255,255,0.01) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,0.01) 1px, transparent 1px);
    background-size: 100% 100%, 100% 100%, 30px 30px, 30px 30px;
    color: var(--text-main); 
    font-family: 'Rajdhani', sans-serif; 
}
header, footer { display: none !important; }

/* Omni-Header */
.omni-nav { 
    background: linear-gradient(180deg, rgba(1,2,5,0.95) 0%, rgba(6,11,25,0.8) 100%);
    backdrop-filter: blur(25px); -webkit-backdrop-filter: blur(25px);
    border-bottom: 1px solid var(--glass-border); 
    padding: 0 40px; height: 75px;
    display: flex; justify-content: space-between; align-items: center; 
    margin: -3rem -3rem 2rem -3rem; position: sticky; top: 0; z-index: 9999;
    box-shadow: 0 15px 40px rgba(0,0,0,0.9);
}

.brand-matrix { display: flex; align-items: center; gap: 15px; }
.logo-text { font-family: 'Orbitron', sans-serif; font-size: 2rem; font-weight: 900; color: #FFF; letter-spacing: 2px; text-shadow: 0 0 15px rgba(0,255,204,0.4);}
.logo-text span { color: var(--neon-cyan); }
.status-pulse { width: 8px; height: 8px; background: var(--neon-cyan); border-radius: 50%; box-shadow: 0 0 10px var(--neon-cyan); animation: pulse 1.5s infinite; }

@keyframes pulse { 0% { opacity: 1; transform: scale(1); } 50% { opacity: 0.4; transform: scale(1.3); } 100% { opacity: 1; transform: scale(1); } }

/* Holographic Panels */
.holo-panel { 
    background: var(--glass-bg); 
    backdrop-filter: blur(16px);
    border: 1px solid var(--glass-border); 
    border-top: 2px solid rgba(0,255,204,0.3);
    padding: 25px; border-radius: 12px; 
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.6);
    position: relative; overflow: hidden; height: 100%;
}
.panel-title { font-family: 'Share Tech Mono', monospace; font-size: 0.85rem; color: var(--neon-cyan); text-transform: uppercase; letter-spacing: 3px; margin-bottom: 20px; display: flex; align-items: center; gap: 10px; text-shadow: 0 0 8px rgba(0,255,204,0.3);}
.panel-title::after { content: ''; flex-grow: 1; height: 1px; background: linear-gradient(90deg, var(--neon-cyan) 0%, transparent 100%); opacity: 0.3;}

/* Form Tracker */
.form-tracker { display: flex; gap: 4px; justify-content: center; margin-top: 8px;}
.form-badge { width: 20px; height: 20px; display: flex; align-items: center; justify-content: center; border-radius: 3px; font-family: 'Share Tech Mono', monospace; font-size: 0.7rem; font-weight: bold; color: #000; }
.form-w { background: var(--neon-green); box-shadow: 0 0 8px rgba(0,255,102,0.4); }
.form-d { background: var(--neon-gold); box-shadow: 0 0 8px rgba(255,193,7,0.4); }
.form-l { background: var(--neon-red); box-shadow: 0 0 8px rgba(255,42,85,0.4); }

/* Data Grid */
.data-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 25px;}
.data-node { background: rgba(0,0,0,0.5); border: 1px solid rgba(255,255,255,0.05); padding: 20px 15px; border-radius: 8px; text-align: center; box-shadow: inset 0 0 20px rgba(0,0,0,0.8); position: relative; overflow: hidden;}
.node-lbl { font-size: 0.85rem; color: var(--text-dim); text-transform: uppercase; letter-spacing: 2px; margin-bottom: 8px; font-weight: 600;}
.node-val { font-family: 'Share Tech Mono', monospace; font-size: 2.2rem; color: #FFF; text-shadow: 0 0 10px rgba(255,255,255,0.2); line-height: 1;}

/* The Alpha Matrix Ticket */
.singularity-box {
    background: linear-gradient(135deg, rgba(255, 193, 7, 0.08) 0%, rgba(0, 0, 0, 0.9) 100%);
    border: 1px solid var(--neon-gold); border-radius: 12px; padding: 30px; position: relative; height: 100%;
    box-shadow: 0 0 30px rgba(255, 193, 7, 0.1), inset 0 0 20px rgba(255, 193, 7, 0.05);
}
.order-type { position: absolute; top: 25px; right: 25px; background: rgba(0,255,102,0.1); border: 1px solid var(--neon-green); color: var(--neon-green); padding: 4px 10px; border-radius: 4px; font-family: 'Share Tech Mono', monospace; font-size: 0.75rem; letter-spacing: 2px; font-weight: bold; box-shadow: 0 0 10px rgba(0,255,102,0.2);}
.sig-lbl { font-family: 'Share Tech Mono', monospace; font-size: 0.75rem; color: var(--neon-gold); letter-spacing: 4px; text-transform: uppercase; margin-bottom: 10px; display: inline-block; border-bottom: 1px solid var(--neon-gold); padding-bottom: 5px;}
.sig-asset { font-family: 'Orbitron', sans-serif; font-size: 2.2rem; font-weight: 700; color: #FFF; margin-bottom: 2px; line-height: 1.1; letter-spacing: -1px;}
.sig-odd { font-family: 'Share Tech Mono', monospace; font-size: 1.6rem; color: var(--neon-gold); margin-bottom: 25px; text-shadow: 0 0 15px rgba(255,193,7,0.5);}

.metric-bar { background: rgba(255,255,255,0.05); border-radius: 4px; height: 6px; width: 100%; margin-top: 5px; overflow: hidden; position: relative;}
.metric-fill { height: 100%; background: linear-gradient(90deg, var(--neon-purple), var(--neon-cyan)); box-shadow: 0 0 10px var(--neon-cyan);}

.sig-row { display: flex; justify-content: space-between; align-items: center; padding: 12px 0; border-bottom: 1px dashed rgba(255,255,255,0.05); font-size: 1.05rem; font-weight: 600;}
.sig-row:last-child { border: none; padding-bottom: 0;}
.sig-row span:first-child { color: var(--text-dim); font-weight: 500; font-family: 'Rajdhani', sans-serif; letter-spacing: 0.5px;}
.sig-row span:last-child { font-family: 'Share Tech Mono', monospace; color: #FFF;}

/* Quantum Tables */
.table-container { max-height: 320px; overflow-y: auto; overflow-x: hidden; padding-right: 5px; }
.table-container::-webkit-scrollbar { width: 4px; }
.table-container::-webkit-scrollbar-track { background: rgba(0,0,0,0.3); }
.table-container::-webkit-scrollbar-thumb { background: var(--neon-cyan); border-radius: 4px; }

.q-table { width: 100%; border-collapse: collapse; font-family: 'Rajdhani', sans-serif; text-align: center;}
.q-table th { position: sticky; top: 0; padding: 12px 10px; color: var(--neon-cyan); font-family: 'Share Tech Mono', monospace; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 2px; border-bottom: 1px solid rgba(0,255,204,0.3); background: rgba(6,11,25,0.95); z-index: 10;}
.q-table th:first-child { text-align: left; }
.q-table td { padding: 12px 10px; border-bottom: 1px solid rgba(255,255,255,0.02); font-size: 1rem; font-weight: 600;}
.q-table td:first-child { text-align: left; }
.q-table tr:hover td { background: rgba(0,255,204,0.05); }
.mono-val { font-family: 'Share Tech Mono', monospace; }

/* Streamlit Overrides */
div[data-baseweb="select"] > div, div[data-baseweb="input"] > div { background-color: rgba(0,0,0,0.8) !important; border: 1px solid rgba(0,255,204,0.2) !important; border-radius: 6px !important; color: #FFF !important; font-family: 'Share Tech Mono', monospace !important;}
.stButton > button {
    background: transparent !important; color: var(--neon-cyan) !important; 
    border: 1px solid var(--neon-cyan) !important; font-family: 'Orbitron', sans-serif !important;
    font-weight: 700 !important; font-size: 1.2rem !important; letter-spacing: 3px !important;
    padding: 25px !important; width: 100%; border-radius: 6px !important;
    text-transform: uppercase; transition: all 0.3s ease !important;
    box-shadow: inset 0 0 15px rgba(0,255,204,0.05) !important;
}
.stButton > button:hover { background: var(--neon-cyan) !important; color: #000 !important; box-shadow: 0 0 30px rgba(0,255,204,0.4), inset 0 0 20px rgba(255,255,255,0.5) !important; transform: translateY(-2px);}
.stProgress > div > div > div > div { background: linear-gradient(90deg, #B026FF, #00FFCC) !important; }
div[data-testid="column"] > div { gap: 1.5rem !important; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. ALGORITHMIC CORE & DATA PIPELINE
# ==========================================
API_KEY = st.secrets.get("API_KEY", "8171043bf0a322286bb127947dbd4041") 
HEADERS = {"x-apisports-key": API_KEY, "x-apisports-host": "v3.football.api-sports.io"}

def get_dynamic_season():
    now = datetime.now()
    return str(now.year - 1) if now.month < 7 else str(now.year)

def fetch_api(endpoint, params):
    try:
        r = requests.get(f"https://{HEADERS['x-apisports-host']}/{endpoint}", headers=HEADERS, params=params, timeout=12)
        return r.json().get('response', [])
    except Exception: return []

def safe_float(val, default):
    try: return default if val is None else float(val)
    except: return default

@st.cache_data(ttl=120) 
def get_upcoming_fixtures(league_id): 
    return fetch_api("fixtures", {"league": league_id, "next": 15})

@st.cache_data(ttl=3600)
def get_advanced_xg_stats(team_id, league_id, season):
    stats = fetch_api("teams/statistics", {"team": team_id, "league": league_id, "season": season})
    default_stats = {"xg_h": 1.45, "xga_h": 1.15, "xg_a": 1.15, "xga_a": 1.45, "form": "-----", "played": 0}
    if not stats: return default_stats
    
    try:
        data = stats if isinstance(stats, dict) else stats[0]
        goals = data.get('goals', {})
        
        gf_h = safe_float(goals.get('for', {}).get('average', {}).get('home'), 1.45)
        ga_h = safe_float(goals.get('against', {}).get('average', {}).get('home'), 1.15)
        gf_a = safe_float(goals.get('for', {}).get('average', {}).get('away'), 1.15)
        ga_a = safe_float(goals.get('against', {}).get('average', {}).get('away'), 1.45)
        
        cs_h = safe_float(data.get('clean_sheet', {}).get('home'), 0) / 10 
        fts_a = safe_float(data.get('failed_to_score', {}).get('away'), 0) / 10 
        
        # Extrair volume de jogo e forma (momentum)
        played = safe_float(data.get('fixtures', {}).get('played', {}).get('total'), 0)
        raw_form = data.get('form', '-----')
        clean_form = raw_form[-5:] if raw_form and isinstance(raw_form, str) else "-----"
        clean_form = clean_form.ljust(5, '-')
        
        return {
            "xg_h": max(0.2, gf_h + (cs_h * 0.1)),
            "xga_h": max(0.2, ga_h - (cs_h * 0.15)),
            "xg_a": max(0.2, gf_a - (fts_a * 0.1)),
            "xga_a": max(0.2, ga_a + (fts_a * 0.15)),
            "form": clean_form,
            "played": played
        }
    except Exception: return default_stats

@st.cache_data(ttl=3600)
def get_league_standings(league_id, season):
    data = fetch_api("standings", {"league": league_id, "season": season})
    try:
        if data and len(data) > 0: return data[0]['league']['standings'][0]
    except: pass
    return []

@st.cache_data(ttl=60)
def get_real_odds(fixture_id):
    odds_data = fetch_api("odds", {"fixture": fixture_id, "bookmaker": 8}) 
    market_odds = {}
    if not odds_data or not odds_data[0].get('bookmakers'): return market_odds
    try:
        for bet in odds_data[0]['bookmakers'][0].get('bets', []):
            name = bet.get('name', '')
            vals = {str(v.get('value', '')): float(v.get('odd', 0.0)) for v in bet.get('values', [])}
            
            if name == 'Match Winner': market_odds.update({"Home Win": vals.get('Home'), "Draw": vals.get('Draw'), "Away Win": vals.get('Away')})
            elif name == 'Double Chance': market_odds.update({"Double Chance (1X)": vals.get('Home/Draw'), "Double Chance (X2)": vals.get('Draw/Away')})
            elif name == 'Draw No Bet': market_odds.update({"Draw No Bet (Home)": vals.get('Home'), "Draw No Bet (Away)": vals.get('Away')})
            elif name == 'Goals Over/Under': 
                for k, v in vals.items(): market_odds[f"Total Goals {k}"] = v
            elif name == 'Both Teams Score': market_odds.update({"BTTS (Yes)": vals.get('Yes'), "BTTS (No)": vals.get('No')})
            elif name == 'Asian Handicap':
                for k, odd in vals.items():
                    if "Home" in k: market_odds[f"Home AH {k.replace('Home', '').strip()}"] = odd
                    elif "Away" in k: market_odds[f"Away AH {k.replace('Away', '').strip()}"] = odd
    except: pass 
    return {k: v for k, v in market_odds.items() if v is not None}

def calculate_lambdas(h_stats, a_stats):
    hfa = 1.12 
    lam_h = max(0.1, (h_stats['xg_h'] * hfa) * (a_stats['xga_a']) / 1.45)
    lam_a = max(0.1, (a_stats['xg_a']) * (h_stats['xga_h']) / 1.15)
    return round(lam_h, 3), round(lam_a, 3)

def run_monte_carlo_sim(lam_h, lam_a, sims=100000):
    np.random.seed(int(time.time()))
    h_goals = np.random.poisson(lam_h, sims)
    a_goals = np.random.poisson(lam_a, sims)
    
    rho = -0.12 
    zero_zero_mask = (h_goals == 0) & (a_goals == 0)
    correction_mask = np.random.random(sims) < abs(rho)
    final_mask = zero_zero_mask & correction_mask
    h_goals[final_mask] = 1
    a_goals[final_mask] = 1
        
    diff, total = h_goals - a_goals, h_goals + a_goals
    hw, dr, aw = np.sum(diff > 0)/sims, np.sum(diff == 0)/sims, np.sum(diff < 0)/sims
    
    probs = {
        "Home Win": hw, "Draw": dr, "Away Win": aw,
        "Double Chance (1X)": hw + dr, "Double Chance (X2)": aw + dr,
        "Draw No Bet (Home)": hw / (hw + aw) if (hw + aw) > 0 else 0, 
        "Draw No Bet (Away)": aw / (hw + aw) if (hw + aw) > 0 else 0,
        "BTTS (Yes)": np.sum((h_goals > 0) & (a_goals > 0))/sims, 
        "BTTS (No)": np.sum((h_goals == 0) | (a_goals == 0))/sims
    }
    
    for limit in [1.5, 2.5, 3.5]:
        probs[f"Total Goals Over {limit}"] = np.sum(total > limit)/sims
        probs[f"Total Goals Under {limit}"] = np.sum(total < limit)/sims
        
    for limit in [-1.5, -1.0, -0.5, +0.5, +1.0, +1.5]:
        if limit in [-1.0, +1.0]:
            push_h, push_a = np.sum(diff == -limit)/sims, np.sum(-diff == limit)/sims
            probs[f"Home AH {limit:+}"] = (np.sum(diff > -limit)/sims) / (1-push_h) if (1-push_h) > 0 else 0
            probs[f"Away AH {-limit:+}"] = (np.sum(-diff > limit)/sims) / (1-push_a) if (1-push_a) > 0 else 0
        else:
            probs[f"Home AH {limit:+}"] = np.sum(diff > -limit)/sims
            probs[f"Away AH {-limit:+}"] = np.sum(-diff > limit)/sims
    return probs

def calculate_dynamic_margin(odds):
    try:
        if "Home Win" in odds and "Draw" in odds and "Away Win" in odds:
            return max(0.01, (1/odds["Home Win"]) + (1/odds["Draw"]) + (1/odds["Away Win"]) - 1)
    except: pass
    return 0.045

def calculate_quant_metrics(prob, odd, fraction_multiplier, bankroll, games_played, max_risk_cap=0.035):
    """
    ALGORITMO QUANTITATIVO PROFISSIONAL (Kelly Otimizado + Índice de Confiança)
    """
    edge = (prob * odd) - 1
    b = odd - 1
    
    if b <= 0 or edge <= 0:
        return 0, 0, 0, 0
        
    # 1. Optimal Kelly Sizing
    kelly_full = max(0, edge / b)
    kelly_adj = kelly_full * fraction_multiplier
    
    # Capital Preservation: Hard Cap absolute risk (e.g., max 3.5% of bankroll per trade)
    final_kelly_pct = min(kelly_adj, max_risk_cap)
    dollar_allocation = final_kelly_pct * bankroll
    
    # 2. Omni-Score (Confidence Index)
    # Recompensa alto edge, alta probabilidade base, baixa variância (odds mais baixas) e liquidez de dados
    score_edge = min(edge * 150, 40) # Max 40 pts
    score_prob = prob * 45           # Max 45 pts
    penalty_var = (odd / 10) * 10    # Subtrai pts por volatilidade
    bonus_vol = min(games_played, 15) / 1.5 # Max 10 pts
    
    confidence = score_edge + score_prob - penalty_var + bonus_vol
    confidence = max(12.5, min(99.9, confidence))
    
    return edge, final_kelly_pct * 100, dollar_allocation, confidence

def poisson_pmf(lam, k): return (lam**k * math.exp(-lam)) / math.factorial(k)

def render_form_badges(form_str):
    html = "<div class='form-tracker'>"
    for char in form_str:
        if char == 'W': html += "<div class='form-badge form-w'>W</div>"
        elif char == 'D': html += "<div class='form-badge form-d'>D</div>"
        elif char == 'L': html += "<div class='form-badge form-l'>L</div>"
        else: html += "<div class='form-badge' style='background:rgba(255,255,255,0.1); color:#94A3B8;'>-</div>"
    return html + "</div>"

# ==========================================
# 3. OMNI-TERMINAL INTERFACE
# ==========================================
st.markdown(f"""
<div class="omni-nav">
    <div class="brand-matrix">
        <div class="status-pulse"></div>
        <div class="logo-text">APEX<span>QUANT</span></div>
    </div>
    <div style="font-family:'Share Tech Mono'; color:var(--neon-cyan); letter-spacing:2px; font-size:0.85rem;">
        HEDGE FUND MODE // STRICT RISK CAPS // OMNI-SCORE V2
    </div>
</div>
""", unsafe_allow_html=True)

col_ctrl, col_exec = st.columns([1.1, 2.9], gap="large")

with col_ctrl:
    st.markdown("<div class='holo-panel'>", unsafe_allow_html=True)
    st.markdown("<div class='panel-title'>LIQUIDITY POOL SELECTOR</div>", unsafe_allow_html=True)
    
    l_map = {
        "Premier League (ENG)": 39, "Champions League (EUR)": 2, "La Liga (ESP)": 140, 
        "Bundesliga (GER)": 78, "Serie A (ITA)": 135, "Ligue 1 (FRA)": 61,
        "Primeira Liga (POR)": 94, "Brasileirão Série A (BRA)": 71, 
        "MLS (USA)": 253, "Eredivisie (NED)": 88
    }
    league_name = st.selectbox("Target Market", list(l_map.keys()))
    
    fixtures = get_upcoming_fixtures(l_map[league_name])
    m_sel = None
    btn_run = False
    
    if fixtures:
        def format_match(f):
            dt = datetime.strptime(f['fixture']['date'][:16], "%Y-%m-%dT%H:%M")
            return f"{f['teams']['home']['name']} vs {f['teams']['away']['name']}  [{dt.strftime('%d/%m %H:%M')}]"
            
        m_map = {format_match(f): f for f in fixtures}
        m_sel = m_map[st.selectbox("Arbitrage Vectors (Next 15)", list(m_map.keys()))]
    else:
        st.error("MARKET CLOSED: No liquidity found.")
        
    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
    st.markdown("<div class='panel-title'>CAPITAL MANAGEMENT</div>", unsafe_allow_html=True)
    bankroll = st.number_input("Vault Capital ($)", value=250000, step=10000, format="%d")
    
    k_map = {"Quarter Kelly (0.25x)": 0.25, "Half Kelly (0.50x)": 0.50, "Full Kelly (1.00x - Aggressive)": 1.0}
    k_sel = st.selectbox("Kelly Sizing Strategy", list(k_map.keys()), index=1)
    kelly_fraction = k_map[k_sel]
    
    max_risk = st.slider("Strict Risk Cap (% Bankroll)", min_value=1.0, max_value=5.0, value=3.0, step=0.5) / 100
    
    if m_sel:
        st.markdown("<div style='margin-top: 25px;'>", unsafe_allow_html=True)
        btn_run = st.button("EXECUTE QUANTUM MODEL")
        st.markdown("</div>", unsafe_allow_html=True)
        
    st.markdown("</div>", unsafe_allow_html=True)

if m_sel and btn_run:
    sys_status = st.empty()
    p_bar = st.progress(0)
    
    steps = ["INITIALIZING NEURAL NETWORKS...", "EXTRACTING FORM MOMENTUM & STANDINGS...", "CALCULATING OMNI-SCORE & STRICT KELLY...", "EXTRACTING PRIME ALPHA..."]
    for i, step in enumerate(steps):
        sys_status.markdown(f"<div style='color:var(--neon-cyan); font-family:\"Share Tech Mono\"; font-size:0.8rem; margin-bottom:10px; text-shadow:0 0 5px rgba(0,255,204,0.5);'>[SYS_LOG]: {step}</div>", unsafe_allow_html=True)
        time.sleep(0.3)
        p_bar.progress((i+1)*25)
    
    time.sleep(0.2)
    sys_status.empty()
    p_bar.empty()
    
    h_name, a_name = m_sel['teams']['home']['name'], m_sel['teams']['away']['name']
    season_id = get_dynamic_season()
    
    h_stats = get_advanced_xg_stats(m_sel['teams']['home']['id'], l_map[league_name], season_id)
    a_stats = get_advanced_xg_stats(m_sel['teams']['away']['id'], l_map[league_name], season_id)
    
    lam_h, lam_a = calculate_lambdas(h_stats, a_stats)
    true_probs = run_monte_carlo_sim(lam_h, lam_a, 100000)
    live_odds = get_real_odds(m_sel['fixture']['id'])
    standings_data = get_league_standings(l_map[league_name], season_id)
    
    avg_games_played = (h_stats['played'] + a_stats['played']) / 2
    
    valid_markets, best_bet = [], None
    dyn_margin = calculate_dynamic_margin(live_odds)
    
    if live_odds:
        for mkt, odd in live_odds.items():
            prob = true_probs.get(mkt, 0)
            if odd > 1.05 and prob > 0:
                edge, k_pct, k_alloc, conf = calculate_quant_metrics(prob, odd, kelly_fraction, bankroll, avg_games_played, max_risk_cap=max_risk)
                
                if edge > 0:
                    ui_mkt = mkt.replace("Home Win", f"{h_name} Win").replace("Away Win", f"{a_name} Win").replace("Draw No Bet (Home)", f"{h_name} (DNB)").replace("Draw No Bet (Away)", f"{a_name} (DNB)")
                    valid_markets.append({"Market": ui_mkt, "BookOdd": odd, "ModelProb": prob, "Edge": edge, "KellyPct": k_pct, "Allocation": k_alloc, "Confidence": conf})
        
        prime_bets = [m for m in valid_markets if 0.01 < m['Edge'] < 0.35 and m['ModelProb'] >= 0.30]
        if prime_bets: best_bet = max(prime_bets, key=lambda x: (x['Confidence'] * 0.7) + (x['KellyPct'] * 0.3)) 
    
    with col_exec:
        # Row 1: Dados Head-to-Head (xG + Forma)
        st.markdown(f"""
        <div class='data-grid'>
            <div class='data-node'>
                <div class='node-lbl'>[{h_name}] Synthesized xG</div>
                <div class='node-val cyan'>{lam_h:.2f}</div>
                {render_form_badges(h_stats['form'])}
            </div>
            <div class='data-node'>
                <div class='node-lbl'>[{a_name}] Synthesized xG</div>
                <div class='node-val purple'>{lam_a:.2f}</div>
                {render_form_badges(a_stats['form'])}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Row 2: Alpha Signal & Gráfico EV Sim
        col_alpha, col_ev = st.columns([1.1, 1], gap="large")
        with col_alpha:
            if best_bet:
                yld = (best_bet['Edge'] * best_bet['Allocation'])
                st.markdown(f"""
                <div class='singularity-box'>
                    <div class='order-type'>BUY ORDER</div>
                    <div class='sig-lbl'>PRIME ALPHA DETECTED</div>
                    <div class='sig-asset'>{best_bet['Market']}</div>
                    <div class='sig-odd'>@ {best_bet['BookOdd']:.3f}</div>
                    
                    <div class='sig-row'><span>Model Strike Rate</span><span style='color:var(--neon-cyan);'>{best_bet['ModelProb']*100:.2f}%</span></div>
                    <div class='sig-row'><span>Mathematical Edge (+EV)</span><span style='color:var(--neon-gold);'>+{best_bet['Edge']*100:.2f}%</span></div>
                    <div class='sig-row'><span>Optimal Allocation (Cap)</span><span>${best_bet['Allocation']:,.0f} <span style='font-size:0.8rem; color:var(--text-dim);'>({best_bet['KellyPct']:.2f}%)</span></span></div>
                    <div class='sig-row'><span>Expected Yield per Trade</span><span style='color:var(--neon-green);'>+${yld:,.0f}</span></div>
                    
                    <div style='margin-top:20px;'>
                        <div style='display:flex; justify-content:space-between; font-family:"Share Tech Mono"; font-size:0.8rem; color:var(--text-dim); margin-bottom:4px;'>
                            <span>Omni-Score (Confidence)</span><span>{best_bet['Confidence']:.1f} / 100</span>
                        </div>
                        <div class='metric-bar'><div class='metric-fill' style='width:{best_bet["Confidence"]}%;'></div></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            elif live_odds:
                st.markdown("<div class='holo-panel' style='display:flex; align-items:center; justify-content:center; text-align:center;'><div class='panel-title' style='color:var(--neon-red); margin:0;'>MARKET HIGHLY EFFICIENT.<br>NO EDGES DETECTED. DO NOT DEPLOY CAPITAL.</div></div>", unsafe_allow_html=True)

        with col_ev:
            st.markdown("<div class='holo-panel'><div class='panel-title'>EV PROJECTION CURVE (500 TRADES)</div>", unsafe_allow_html=True)
            if best_bet:
                sim_trades = 500
                p = best_bet['ModelProb']
                o = best_bet['BookOdd']
                b_size = best_bet['Allocation']
                
                expected_growth = np.array([max(0, (i * b_size * ((p * o) - 1))) for i in range(sim_trades)])
                noise = np.random.normal(0, b_size * 1.5, sim_trades).cumsum() 
                simulated_path = expected_growth + noise
                
                fig_ev = go.Figure()
                fig_ev.add_trace(go.Scatter(y=simulated_path, name="Simulated Realization", line=dict(color='rgba(255,193,7,0.4)', width=1)))
                fig_ev.add_trace(go.Scatter(y=expected_growth, name="Theoretical +EV", line=dict(color='#00FFCC', width=3, dash='solid')))
                
                fig_ev.update_layout(
                    template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                    height=240, margin=dict(l=0, r=0, t=5, b=0),
                    showlegend=False,
                    xaxis=dict(title="Number of Trades", title_font=dict(family="Share Tech Mono", size=10), gridcolor="rgba(255,255,255,0.05)", showline=True, linewidth=1, linecolor='rgba(255,255,255,0.1)'),
                    yaxis=dict(title="Cumulative P&L ($)", title_font=dict(family="Share Tech Mono", size=10), gridcolor="rgba(255,255,255,0.05)", zeroline=True, zerolinecolor='rgba(255,42,85,0.3)')
                )
                st.plotly_chart(fig_ev, use_container_width=True, config={'displayModeBar': False})
            else:
                st.markdown("<div style='color:var(--text-dim); text-align:center; padding-top:40px;'>No signal to simulate.</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        # Row 3: Order Book & Standings Matrix
        col_ob, col_std = st.columns(2, gap="large")
        
        with col_ob:
            st.markdown("<div class='holo-panel' style='padding:20px;'><div class='panel-title'>ORDER BOOK SCALPER</div>", unsafe_allow_html=True)
            if live_odds:
                clean = sorted([m for m in valid_markets if m['Edge'] < 0.35 and m['BookOdd'] <= 8.0], key=lambda x: x['Confidence'], reverse=True)
                html = "<div class='table-container'><table class='q-table'><tr><th>Asset</th><th>Odd</th><th>Prob</th><th>EV</th></tr>"
                for m in clean[:8]: 
                    clr = "color:var(--neon-cyan);" if m['Edge'] > 0 else ""
                    html += f"<tr><td>{m['Market']}</td><td class='mono-val'>{m['BookOdd']:.2f}</td><td class='mono-val'>{m['ModelProb']*100:.1f}%</td><td class='mono-val' style='{clr}'>+{m['Edge']*100:.2f}%</td></tr>"
                st.markdown(html + "</table></div></div>", unsafe_allow_html=True)
            else:
                st.markdown("<div style='color:var(--text-dim); text-align:center; padding:20px;'>Awaiting Market Data...</div></div>", unsafe_allow_html=True)
                
        with col_std:
            st.markdown(f"<div class='holo-panel' style='padding:20px;'><div class='panel-title'>LEAGUE MATRIX ({season_id})</div>", unsafe_allow_html=True)
            if standings_data:
                html = "<div class='table-container'><table class='q-table'><tr><th>#</th><th>Team</th><th>P</th><th>GF:GA</th><th>Pts</th></tr>"
                for team in standings_data:
                    rank = team.get('rank', '-')
                    name = team.get('team', {}).get('name', 'N/A')[:12]
                    pts = team.get('points', '-')
                    played = team.get('all', {}).get('played', '-')
                    gf = team.get('all', {}).get('goals', {}).get('for', '-')
                    ga = team.get('all', {}).get('goals', {}).get('against', '-')
                    
                    row_style = "background: rgba(0, 255, 204, 0.15);" if name in h_name or name in a_name else ""
                    name_style = "color: var(--neon-cyan); font-weight:700;" if name in h_name or name in a_name else ""
                    
                    html += f"<tr style='{row_style}'><td>{rank}</td><td style='{name_style}'>{name}</td><td class='mono-val'>{played}</td><td class='mono-val' style='color:var(--text-dim);'>{gf}:{ga}</td><td class='mono-val' style='color:var(--neon-gold);'>{pts}</td></tr>"
                st.markdown(html + "</table></div></div>", unsafe_allow_html=True)
            else:
                st.markdown("<div style='color:var(--text-dim); text-align:center; padding:20px;'>Standings Data Unavailable.</div></div>", unsafe_allow_html=True)
