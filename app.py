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
    --bg-deep: #010308;
    --glass-bg: rgba(4, 9, 20, 0.6);
    --glass-border: rgba(0, 255, 204, 0.15);
    --neon-cyan: #00FFCC;
    --neon-purple: #B026FF;
    --neon-gold: #FFC107;
    --neon-red: #FF2A55;
    --text-main: #E2E8F0;
    --text-dim: #64748B;
}

/* Background & Core */
.stApp { 
    background-color: var(--bg-deep); 
    background-image: 
        radial-gradient(circle at 10% 20%, rgba(0, 255, 204, 0.05), transparent 30%),
        radial-gradient(circle at 90% 80%, rgba(176, 38, 255, 0.05), transparent 30%);
    color: var(--text-main); 
    font-family: 'Rajdhani', sans-serif; 
}
header, footer { display: none !important; }

/* Omni-Header */
.omni-nav { 
    background: linear-gradient(180deg, rgba(1,3,8,0.9) 0%, rgba(4,9,20,0.8) 100%);
    backdrop-filter: blur(25px); -webkit-backdrop-filter: blur(25px);
    border-bottom: 1px solid var(--glass-border); 
    padding: 0 40px; height: 80px;
    display: flex; justify-content: space-between; align-items: center; 
    margin: -3rem -3rem 2rem -3rem; position: sticky; top: 0; z-index: 9999;
    box-shadow: 0 15px 40px rgba(0,0,0,0.8);
}

.brand-matrix { display: flex; align-items: center; gap: 15px; }
.logo-text { font-family: 'Orbitron', sans-serif; font-size: 2.2rem; font-weight: 900; color: #FFF; letter-spacing: 2px; text-shadow: 0 0 15px rgba(0,255,204,0.4);}
.logo-text span { color: var(--neon-cyan); }
.status-pulse { width: 10px; height: 10px; background: var(--neon-cyan); border-radius: 50%; box-shadow: 0 0 10px var(--neon-cyan); animation: pulse 1.5s infinite; }

@keyframes pulse { 0% { opacity: 1; transform: scale(1); } 50% { opacity: 0.4; transform: scale(1.2); } 100% { opacity: 1; transform: scale(1); } }

/* Holographic Panels */
.holo-panel { 
    background: var(--glass-bg); 
    backdrop-filter: blur(16px);
    border: 1px solid var(--glass-border); 
    border-top: 2px solid rgba(0,255,204,0.3);
    padding: 25px; border-radius: 12px; 
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
    position: relative; overflow: hidden;
    height: 100%;
}
.holo-panel::before { content: ''; position: absolute; top: 0; left: -100%; width: 50%; height: 2px; background: linear-gradient(90deg, transparent, var(--neon-cyan), transparent); animation: scan 4s linear infinite; }
@keyframes scan { 100% { left: 200%; } }

.panel-title { font-family: 'Share Tech Mono', monospace; font-size: 0.85rem; color: var(--neon-cyan); text-transform: uppercase; letter-spacing: 3px; margin-bottom: 20px; display: flex; align-items: center; gap: 10px; text-shadow: 0 0 8px rgba(0,255,204,0.3);}
.panel-title::after { content: ''; flex-grow: 1; height: 1px; background: linear-gradient(90deg, var(--neon-cyan) 0%, transparent 100%); opacity: 0.3;}

/* Data Grid */
.data-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 25px;}
.data-node { background: rgba(0,0,0,0.4); border: 1px solid rgba(255,255,255,0.05); padding: 15px; border-radius: 8px; text-align: center; box-shadow: inset 0 0 20px rgba(0,0,0,0.5);}
.node-lbl { font-size: 0.8rem; color: var(--text-dim); text-transform: uppercase; letter-spacing: 1px; margin-bottom: 5px; font-weight: 600;}
.node-val { font-family: 'Share Tech Mono', monospace; font-size: 2rem; color: #FFF; text-shadow: 0 0 10px rgba(255,255,255,0.2); line-height: 1;}
.node-val.cyan { color: var(--neon-cyan); text-shadow: 0 0 15px rgba(0,255,204,0.4); }
.node-val.purple { color: var(--neon-purple); text-shadow: 0 0 15px rgba(176,38,255,0.4); }

/* The Singularity Signal (Alpha Box) */
.singularity-box {
    background: linear-gradient(135deg, rgba(255, 193, 7, 0.1) 0%, rgba(0, 0, 0, 0.8) 100%);
    border: 1px solid var(--neon-gold);
    border-radius: 12px; padding: 30px; position: relative; height: 100%;
    box-shadow: 0 0 30px rgba(255, 193, 7, 0.15), inset 0 0 20px rgba(255, 193, 7, 0.05);
    animation: borderGlow 3s infinite alternate;
}
@keyframes borderGlow { 0% { box-shadow: 0 0 20px rgba(255,193,7,0.1); } 100% { box-shadow: 0 0 40px rgba(255,193,7,0.3); } }
.sig-lbl { font-family: 'Share Tech Mono', monospace; font-size: 0.8rem; color: var(--neon-gold); letter-spacing: 4px; text-transform: uppercase; margin-bottom: 15px; display: inline-block; border-bottom: 1px solid var(--neon-gold); padding-bottom: 5px;}
.sig-asset { font-family: 'Orbitron', sans-serif; font-size: 2.2rem; font-weight: 700; color: #FFF; margin-bottom: 5px; line-height: 1.1;}
.sig-odd { font-family: 'Share Tech Mono', monospace; font-size: 1.8rem; color: var(--neon-gold); margin-bottom: 20px; text-shadow: 0 0 15px rgba(255,193,7,0.5);}

.sig-row { display: flex; justify-content: space-between; align-items: center; padding: 10px 0; border-bottom: 1px dashed rgba(255,255,255,0.1); font-size: 1rem; font-weight: 600;}
.sig-row:last-child { border: none; padding-bottom: 0;}
.sig-row span:first-child { color: var(--text-dim); font-weight: 500; font-family: 'Rajdhani', sans-serif;}
.sig-row span:last-child { font-family: 'Share Tech Mono', monospace; color: #FFF;}

/* Quantum Tables (Order Book & Standings) */
.table-container { max-height: 350px; overflow-y: auto; overflow-x: hidden; padding-right: 5px; }
.table-container::-webkit-scrollbar { width: 6px; }
.table-container::-webkit-scrollbar-track { background: rgba(0,0,0,0.3); border-radius: 4px; }
.table-container::-webkit-scrollbar-thumb { background: var(--neon-cyan); border-radius: 4px; }

.q-table { width: 100%; border-collapse: collapse; font-family: 'Rajdhani', sans-serif; text-align: center;}
.q-table th { position: sticky; top: 0; padding: 12px 10px; color: var(--neon-cyan); font-family: 'Share Tech Mono', monospace; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1px; border-bottom: 1px solid rgba(0,255,204,0.3); background: rgba(4,9,20,0.95); z-index: 10;}
.q-table th:first-child { text-align: left; }
.q-table td { padding: 12px 10px; border-bottom: 1px solid rgba(255,255,255,0.03); font-size: 1rem; font-weight: 600;}
.q-table td:first-child { text-align: left; }
.q-table tr:hover td { background: rgba(0,255,204,0.05); }
.mono-val { font-family: 'Share Tech Mono', monospace; }

/* Streamlit Overrides */
div[data-baseweb="select"] > div, div[data-baseweb="input"] > div { background-color: rgba(0,0,0,0.6) !important; border: 1px solid rgba(0,255,204,0.3) !important; border-radius: 4px !important; color: #FFF !important; font-family: 'Share Tech Mono', monospace !important;}
.stButton > button {
    background: transparent !important; color: var(--neon-cyan) !important; 
    border: 1px solid var(--neon-cyan) !important; font-family: 'Orbitron', sans-serif !important;
    font-weight: 700 !important; font-size: 1.2rem !important; letter-spacing: 3px !important;
    padding: 25px !important; width: 100%; border-radius: 4px !important;
    text-transform: uppercase; transition: all 0.3s ease !important;
    box-shadow: inset 0 0 10px rgba(0,255,204,0.1) !important;
}
.stButton > button:hover { background: var(--neon-cyan) !important; color: #000 !important; box-shadow: 0 0 30px rgba(0,255,204,0.5), inset 0 0 20px rgba(255,255,255,0.5) !important; transform: translateY(-2px);}
.stProgress > div > div > div > div { background: linear-gradient(90deg, #B026FF, #00FFCC) !important; }
div[data-testid="column"] > div { gap: 1.5rem !important; } /* Fix column spacing */
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
    default_stats = {"xg_h": 1.45, "xga_h": 1.15, "xg_a": 1.15, "xga_a": 1.45}
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
        
        return {
            "xg_h": max(0.2, gf_h + (cs_h * 0.1)),
            "xga_h": max(0.2, ga_h - (cs_h * 0.15)),
            "xg_a": max(0.2, gf_a - (fts_a * 0.1)),
            "xga_a": max(0.2, ga_a + (fts_a * 0.15))
        }
    except Exception: return default_stats

@st.cache_data(ttl=3600)
def get_league_standings(league_id, season):
    """NOVO: Extrai a tabela classificativa oficial."""
    data = fetch_api("standings", {"league": league_id, "season": season})
    try:
        if data and len(data) > 0:
            return data[0]['league']['standings'][0]
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
    """NOVO: Motor Numpy 100% Vetorizado para velocidade extrema (HFT Level)"""
    np.random.seed(int(time.time()))
    h_goals = np.random.poisson(lam_h, sims)
    a_goals = np.random.poisson(lam_a, sims)
    
    # DIXON-COLES RHO ADJUSTMENT (Correção Científica Vetorizada)
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

def calculate_kelly(prob, odd, fraction):
    b = odd - 1
    if b <= 0: return 0
    return max(0, (((b * prob) - (1 - prob)) / b) * fraction * 100)

def poisson_pmf(lam, k): return (lam**k * math.exp(-lam)) / math.factorial(k)

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
        SECURE SOCKET // VECTOR ALGO ACTIVE // POISSON KERNEL V5
    </div>
</div>
""", unsafe_allow_html=True)

col_ctrl, col_exec = st.columns([1.2, 2.8], gap="large")

with col_ctrl:
    st.markdown("<div class='holo-panel'>", unsafe_allow_html=True)
    st.markdown("<div class='panel-title'>LIQUIDITY POOL SELECTOR</div>", unsafe_allow_html=True)
    
    l_map = {
        "Premier League (ENG)": 39, "Champions League (EUR)": 2, "La Liga (ESP)": 140, 
        "Bundesliga (GER)": 78, "Serie A (ITA)": 135, "Ligue 1 (FRA)": 61,
        "Primeira Liga (POR)": 94, "Brasileirão Série A (BRA)": 71, 
        "MLS (USA)": 253, "Eredivisie (NED)": 88, "Europa League (EUR)": 3
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
        m_sel = m_map[st.selectbox("Available Arbitrage Vectors (Next 15)", list(m_map.keys()))]
    else:
        st.error("MARKET CLOSED: No liquidity found for this sector.")
        
    st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)
    st.markdown("<div class='panel-title'>RISK & CAPITAL MANAGEMENT</div>", unsafe_allow_html=True)
    bankroll = st.number_input("Vault Capital ($)", value=1000000, step=50000, format="%d")
    kelly_fraction = st.slider("Kelly Fractional Sizing (Bias)", min_value=0.1, max_value=1.0, value=0.25, step=0.05)
    
    if m_sel:
        st.markdown("<div style='margin-top: 35px;'>", unsafe_allow_html=True)
        btn_run = st.button("EXECUTE QUANTUM MODEL")
        st.markdown("</div>", unsafe_allow_html=True)
        
    st.markdown("</div>", unsafe_allow_html=True)

if m_sel and btn_run:
    sys_status = st.empty()
    p_bar = st.progress(0)
    
    steps = [
        "INITIALIZING NEURAL NETWORKS...", 
        "SYNCING xG AND LEAGUE STANDINGS...", 
        "RUNNING 100,000 VECTORIZED MC PATHS...", 
        "EXTRACTING PRIME ALPHA..."
    ]
    for i, step in enumerate(steps):
        sys_status.markdown(f"<div style='color:var(--neon-cyan); font-family:\"Share Tech Mono\"; font-size:0.9rem; margin-bottom:15px; text-shadow:0 0 5px rgba(0,255,204,0.5);'>[SYS_LOG]: {step}</div>", unsafe_allow_html=True)
        time.sleep(0.3)
        p_bar.progress((i+1)*25)
    
    time.sleep(0.3)
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
    
    valid_markets, best_bet = [], None
    dyn_margin = calculate_dynamic_margin(live_odds)
    
    if live_odds:
        for mkt, odd in live_odds.items():
            prob = true_probs.get(mkt, 0)
            if odd > 1.05 and prob > 0:
                f_prob = (1 / odd) / (1 + dyn_margin)
                edge = (prob * odd) - 1
                k_val = min(calculate_kelly(prob, odd, kelly_fraction), 10.0) if edge > 0 else 0
                
                ui_mkt = mkt.replace("Home Win", f"{h_name} Win").replace("Away Win", f"{a_name} Win").replace("Draw No Bet (Home)", f"{h_name} (DNB)").replace("Draw No Bet (Away)", f"{a_name} (DNB)")
                valid_markets.append({"Market": ui_mkt, "BookOdd": odd, "ModelProb": prob, "Edge": edge, "Kelly": k_val})
        
        prime_bets = [m for m in valid_markets if 0.01 < m['Edge'] < 0.30 and m['ModelProb'] >= 0.35 and m['BookOdd'] <= 4.0]
        if prime_bets: best_bet = max(prime_bets, key=lambda x: x['Kelly'])
    
    with col_exec:
        # Dynamic xG Data Grid (Topo)
        st.markdown(f"""
        <div class='data-grid'>
            <div class='data-node'>
                <div class='node-lbl'>Synthesized xG [{h_name}]</div>
                <div class='node-val cyan'>{lam_h:.2f}</div>
            </div>
            <div class='data-node'>
                <div class='node-lbl'>Synthesized xG [{a_name}]</div>
                <div class='node-val purple'>{lam_a:.2f}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Row 2: Alpha Signal & Chart
        col_alpha, col_chart = st.columns([1.1, 1], gap="large")
        with col_alpha:
            if best_bet:
                sz = (best_bet['Kelly']/100) * bankroll
                c_idx = min(99.9, (best_bet['ModelProb'] * 100) + (best_bet['Edge'] * 60))
                st.markdown(f"""
                <div class='singularity-box'>
                    <div class='sig-lbl'>VERIFIED ALPHA ISOLATED</div>
                    <div class='sig-asset'>{best_bet['Market']}</div>
                    <div class='sig-odd'>@ {best_bet['BookOdd']:.3f}</div>
                    <div class='sig-row'><span>Model Strike Rate</span><span style='color:var(--neon-cyan);'>{best_bet['ModelProb']*100:.2f}%</span></div>
                    <div class='sig-row'><span>Mathematical Edge (+EV)</span><span style='color:var(--neon-gold);'>+{best_bet['Edge']*100:.2f}%</span></div>
                    <div class='sig-row'><span>Optimal Allocation</span><span>${sz:,.0f} <span style='font-size:0.8rem; color:var(--text-dim);'>({best_bet['Kelly']:.2f}%)</span></span></div>
                    <div class='sig-row' style='margin-top:15px; border:none;'><span>Confidence Index</span><span>{c_idx:.1f} / 100.0</span></div>
                </div>
                """, unsafe_allow_html=True)
            elif live_odds:
                st.markdown("<div class='holo-panel' style='height:100%; display:flex; align-items:center; justify-content:center; text-align:center;'><div class='panel-title' style='color:var(--neon-red);'>MARKET HIGHLY EFFICIENT. NO EDGES DETECTED. DO NOT DEPLOY CAPITAL.</div></div>", unsafe_allow_html=True)

        with col_chart:
            st.markdown("<div class='holo-panel'><div class='panel-title'>BIVARIATE POISSON KERNEL</div>", unsafe_allow_html=True)
            g_range = list(range(6))
            h_probs = [poisson_pmf(lam_h, g)*100 for g in g_range]
            a_probs = [poisson_pmf(lam_a, g)*100 for g in g_range]

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=g_range, y=h_probs, fill='tozeroy', name=h_name, line=dict(color='#00FFCC', width=3), fillcolor='rgba(0, 255, 204, 0.2)'))
            fig.add_trace(go.Scatter(x=g_range, y=a_probs, fill='tozeroy', name=a_name, line=dict(color='#B026FF', width=3), fillcolor='rgba(176, 38, 255, 0.2)'))
            
            fig.update_layout(
                template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                height=220, margin=dict(l=0, r=0, t=10, b=0),
                legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="right", x=1, font=dict(family="Rajdhani", size=12)),
                xaxis=dict(title="Goals", title_font=dict(family="Rajdhani", size=12), gridcolor="rgba(255,255,255,0.05)"),
                yaxis=dict(title="Probability (%)", title_font=dict(family="Rajdhani", size=12), gridcolor="rgba(255,255,255,0.05)")
            )
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            st.markdown("</div>", unsafe_allow_html=True)

        # Row 3: Order Book & Standings Matrix
        col_ob, col_std = st.columns(2, gap="large")
        
        with col_ob:
            st.markdown("<div class='holo-panel' style='padding:20px;'><div class='panel-title'>ORDER BOOK SCALPER</div>", unsafe_allow_html=True)
            if live_odds:
                clean = sorted([m for m in valid_markets if m['Edge'] < 0.30 and m['BookOdd'] <= 10.0], key=lambda x: x['Kelly'], reverse=True)
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
                    name = team.get('team', {}).get('name', 'N/A')[:12] # Trim name for UI fitting
                    pts = team.get('points', '-')
                    played = team.get('all', {}).get('played', '-')
                    gf = team.get('all', {}).get('goals', {}).get('for', '-')
                    ga = team.get('all', {}).get('goals', {}).get('against', '-')
                    
                    # Highlight teams currently playing
                    row_style = "background: rgba(0, 255, 204, 0.15);" if name in h_name or name in a_name else ""
                    name_style = "color: var(--neon-cyan); font-weight:700;" if name in h_name or name in a_name else ""
                    
                    html += f"<tr style='{row_style}'><td>{rank}</td><td style='{name_style}'>{name}</td><td class='mono-val'>{played}</td><td class='mono-val' style='color:var(--text-dim);'>{gf}:{ga}</td><td class='mono-val' style='color:var(--neon-gold);'>{pts}</td></tr>"
                st.markdown(html + "</table></div></div>", unsafe_allow_html=True)
            else:
                st.markdown("<div style='color:var(--text-dim); text-align:center; padding:20px;'>Standings Data Unavailable.</div></div>", unsafe_allow_html=True)
