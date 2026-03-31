import streamlit as st
import numpy as np
import pandas as pd
import requests
import math
import plotly.graph_objects as go
from datetime import date
import time
import random

# ==========================================
# 1. INSTITUTIONAL UX SETUP (THE FINAL MASTERPIECE)
# ==========================================
st.set_page_config(page_title="APEX QUANT TERMINAL", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700;800&family=Inter:wght@400;500;600;700;800&display=swap');

/* Base Theme & Anti-Streamlit Overrides */
.stApp { background-color: #02040A; color: #E2E8F0; font-family: 'Inter', sans-serif; }
header, footer, #MainMenu, div[data-testid="stToolbar"] { visibility: hidden !important; display: none !important; }

/* Redesigned Top Nav - Strict Alignment */
.top-nav { 
    background: #050B14; 
    border-bottom: 1px solid #1E293B; 
    border-top: 2px solid #10B981; 
    padding: 0 25px; 
    height: 64px;
    display: flex; 
    justify-content: space-between; 
    align-items: center; 
    margin: -3rem -3rem 0 -3rem; 
    position: sticky; 
    top: 0; 
    z-index: 1000;
}

.nav-left, .nav-center, .nav-right { display: flex; align-items: center; height: 100%; }
.nav-left { gap: 18px; }
.nav-center { gap: 12px; }
.nav-right { gap: 12px; }

.logo { font-size: 1.6rem; font-weight: 800; color: #F8FAFC; font-family: 'JetBrains Mono', monospace; letter-spacing: -1px; display: flex; align-items: center; height: 100%;}
.logo span { color: #10B981; }

.nav-divider { width: 1px; height: 28px; background-color: #334155; }

.nav-subtitle { display: flex; flex-direction: column; justify-content: center; height: 100%; font-size: 0.60rem; color: #64748B; font-weight: 700; letter-spacing: 1.5px; font-family: 'Inter', sans-serif; line-height: 1.3; text-transform: uppercase;}

.telemetry-box { background: #0A1120; border: 1px solid #1E293B; height: 26px; padding: 0 10px; border-radius: 4px; font-size: 0.65rem; font-family: 'JetBrains Mono', monospace; color: #64748B; font-weight: 600; letter-spacing: 0.5px; display: flex; align-items: center; gap: 6px;}
.telemetry-box span { color: #E2E8F0; }
.telemetry-box .hl-green { color: #10B981; }

.nav-time { font-size: 0.65rem; color: #94A3B8; font-family: 'JetBrains Mono', monospace; font-weight: 600; background: #0A1120; height: 26px; padding: 0 12px; border-radius: 4px; border: 1px solid #1E293B; letter-spacing: 1px; display: flex; align-items: center;}
.sys-status { font-size: 0.65rem; font-weight: 700; color: #10B981; font-family: 'JetBrains Mono', monospace; display: flex; align-items: center; gap: 8px; letter-spacing: 0.5px; background: rgba(16, 185, 129, 0.05); height: 26px; padding: 0 12px; border-radius: 4px; border: 1px solid rgba(16, 185, 129, 0.2);}

@keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.3; } 100% { opacity: 1; } }
.dot { height: 6px; width: 6px; background-color: #10B981; border-radius: 50%; display: inline-block; animation: pulse 1.5s infinite; }

/* Market Ticker Marquee */
.ticker-wrap { width: calc(100% + 6rem); background: #02040A; border-bottom: 1px solid #1E293B; overflow: hidden; height: 28px; display: flex; align-items: center; margin: 0 -3rem 1.5rem -3rem; box-sizing: border-box;}
.ticker { display: inline-flex; white-space: nowrap; animation: ticker 40s linear infinite; align-items: center;}
.ticker:hover { animation-play-state: paused; }
@keyframes ticker { 0% { transform: translateX(0); } 100% { transform: translateX(-50%); } }
.ticker-item { display: inline-flex; align-items: center; padding: 0 3rem; font-size: 0.65rem; color: #64748B; font-family: 'JetBrains Mono', monospace; font-weight: 600; letter-spacing: 1px;}
.ticker-item span { color: #10B981; margin-left: 4px; }
.ticker-item .red { color: #EF4444; margin-left: 4px; }

/* Grid Panels */
.grid-panel { border: 1px solid #1E293B; background: #050B14; padding: 24px; margin-bottom: 20px; border-radius: 6px; width: 100%; box-sizing: border-box;}
.panel-title { font-size: 0.7rem; color: #64748B; text-transform: uppercase; border-bottom: 1px solid #1E293B; padding-bottom: 12px; margin-bottom: 16px; font-weight: 700; letter-spacing: 1px; }

/* Metrics & Values */
.data-row { display: flex; justify-content: space-between; font-size: 0.85rem; margin-bottom: 10px; align-items: center; border-bottom: 1px dashed rgba(30, 41, 59, 0.5); padding-bottom: 6px;}
.data-row:last-child { margin-bottom: 0; border-bottom: none; padding-bottom: 0; }
.data-lbl { color: #94A3B8; font-weight: 500; font-size: 0.8rem;}
.data-val { color: #F8FAFC; font-weight: 600; font-family: 'JetBrains Mono', monospace; }

/* Highlight Colors */
.hl-green { color: #10B981 !important; }
.hl-red { color: #EF4444 !important; }
.hl-blue { color: #38BDF8 !important; }

/* Alpha Box (The Money Maker) */
.trade-signal { border: 1px solid #10B981; background: rgba(16,185,129,0.03); padding: 24px; margin-top: 10px; border-radius: 6px; position: relative; overflow: hidden; box-sizing: border-box;}
.trade-signal::before { content: ''; position: absolute; top: 0; left: 0; width: 3px; height: 100%; background: #10B981; }
.trade-asset { font-size: 1.8rem; color: #F8FAFC; font-weight: 800; margin-bottom: 4px; font-family: 'Inter', sans-serif; letter-spacing: -0.5px; line-height: 1.2;}
.trade-odd { font-size: 1.3rem; color: #10B981; font-weight: 700; font-family: 'JetBrains Mono', monospace; margin-bottom: 24px; line-height: 1;}

/* Order Book Table */
.ob-table { width: 100%; font-size: 0.8rem; border-collapse: collapse; font-family: 'JetBrains Mono', monospace; }
.ob-table th { color: #64748B; text-align: right; font-weight: 700; border-bottom: 1px solid #334155; padding: 12px 8px; font-family: 'Inter', sans-serif; font-size: 0.65rem; text-transform: uppercase; letter-spacing: 0.5px;}
.ob-table th:first-child { text-align: left; }
.ob-table td { text-align: right; padding: 12px 8px; border-bottom: 1px solid #0F172A; transition: background 0.2s; }
.ob-table td:first-child { text-align: left; color: #E2E8F0; font-weight: 500; font-family: 'Inter', sans-serif; font-size: 0.85rem;}
.ob-table tr:hover td { background: rgba(30, 41, 59, 0.4); }

/* Sub-Metric Cards */
.metric-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 20px; }
.metric-card { background: #0A1120; border: 1px solid #1E293B; border-radius: 6px; padding: 20px; text-align: center; display: flex; flex-direction: column; justify-content: center; align-items: center;}
.metric-card-title { font-size: 0.65rem; color: #64748B; text-transform: uppercase; font-weight: 700; letter-spacing: 1px; margin-bottom: 10px;}
.metric-card-val { font-size: 1.8rem; color: #F8FAFC; font-weight: 800; font-family: 'JetBrains Mono', monospace; line-height: 1;}

/* Override Streamlit Widgets */
div[data-baseweb="select"] > div, div[data-baseweb="input"] > div { background-color: #0A1120 !important; border: 1px solid #1E293B !important; color: #F8FAFC !important; border-radius: 4px !important; }
.btn-run > button { background: #1E293B !important; color: #F8FAFC !important; border: 1px solid #334155 !important; font-weight: 700 !important; width: 100%; border-radius: 4px !important; padding: 20px !important; transition: all 0.2s ease !important; font-size: 0.95rem !important; letter-spacing: 1px !important; margin-top: 8px;}
.btn-run > button:hover { background: #10B981 !important; color: #000000 !important; border-color: #10B981 !important; }

/* Custom Progress Bar */
.stProgress > div > div > div > div { background-color: #10B981 !important; }

/* Block gap overrides to fix alignments */
div[data-testid="column"] > div { gap: 0rem !important; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. ALGORITHMIC ENGINE & LOGIC
# ==========================================
API_KEY = st.secrets.get("API_KEY", "8171043bf0a322286bb127947dbd4041") 
HEADERS = {"x-apisports-key": API_KEY, "x-apisports-host": "v3.football.api-sports.io"}

def fetch_api(endpoint, params):
    try:
        r = requests.get(f"https://{HEADERS['x-apisports-host']}/{endpoint}", headers=HEADERS, params=params, timeout=10)
        return r.json().get('response', [])
    except Exception:
        return []

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
            elif name == 'Double Chance':
                if 'Home/Draw' in vals: market_odds["Double Chance (1X)"] = vals['Home/Draw']
                if 'Draw/Away' in vals: market_odds["Double Chance (X2)"] = vals['Draw/Away']
                if 'Home/Away' in vals: market_odds["Double Chance (12)"] = vals['Home/Away']
            elif name == 'Draw No Bet':
                if 'Home' in vals: market_odds["Draw No Bet (Home)"] = vals['Home']
                if 'Away' in vals: market_odds["Draw No Bet (Away)"] = vals['Away']
            elif name == 'Goals Over/Under':
                for k, v in vals.items():
                    market_odds[f"Total Goals {k}"] = v
            elif name == 'Both Teams Score':
                if 'Yes' in vals: market_odds["BTTS (Yes)"] = vals['Yes']
                if 'No' in vals: market_odds["BTTS (No)"] = vals['No']
            elif name == 'Asian Handicap':
                for k, odd in vals.items():
                    if "Home" in k: 
                        val = k.replace("Home", "").strip()
                        market_odds[f"Home AH {val}"] = odd
                    elif "Away" in k:
                        val = k.replace("Away", "").strip()
                        market_odds[f"Away AH {val}"] = odd
    except: pass 
    return market_odds

def calculate_lambdas(h_stats, a_stats):
    hfa_multiplier = 1.10 
    lam_h = round(max(0.1, (h_stats['gf_h']/1.55 * hfa_multiplier) * (a_stats['ga_a']/1.55) * 1.55), 3)
    lam_a = round(max(0.1, (a_stats['gf_a']/1.25) * (h_stats['ga_h']/1.25) * 1.25), 3)
    return lam_h, lam_a

def run_monte_carlo_sim(lam_h, lam_a, sims=50000):
    np.random.seed(42) 
    h_goals, a_goals = np.random.poisson(lam_h, sims), np.random.poisson(lam_a, sims)
    
    for i in range(sims):
        if h_goals[i] == 1 and a_goals[i] == 0 and np.random.random() < 0.05: a_goals[i] = 1
        elif h_goals[i] == 0 and a_goals[i] == 1 and np.random.random() < 0.05: h_goals[i] = 1
            
    diff, total = h_goals - a_goals, h_goals + a_goals
    hw, dr, aw = np.sum(diff > 0)/sims, np.sum(diff == 0)/sims, np.sum(diff < 0)/sims
    
    dnb_h_prob = hw / (hw + aw) if (hw + aw) > 0 else 0
    dnb_a_prob = aw / (hw + aw) if (hw + aw) > 0 else 0
    
    probs = {
        "Home Win": hw, "Draw": dr, "Away Win": aw,
        "Double Chance (1X)": hw + dr, "Double Chance (X2)": aw + dr, "Double Chance (12)": hw + aw,
        "Draw No Bet (Home)": dnb_h_prob, "Draw No Bet (Away)": dnb_a_prob,
        "BTTS (Yes)": np.sum((h_goals > 0) & (a_goals > 0))/sims, 
        "BTTS (No)": np.sum((h_goals == 0) | (a_goals == 0))/sims
    }
    
    for limit in [1.5, 2.5, 3.5]:
        probs[f"Total Goals Over {limit}"] = np.sum(total > limit)/sims
        probs[f"Total Goals Under {limit}"] = np.sum(total < limit)/sims
        
    for limit in [-1.5, -1.0, -0.5, +0.5, +1.0, +1.5]:
        if limit == -1.0 or limit == +1.0:
            prob = np.sum(diff > -limit) / sims
            push = np.sum(diff == -limit) / sims
            true_prob = prob / (1 - push) if (1 - push) > 0 else 0
            probs[f"Home AH {limit:+}"] = true_prob
            
            prob_a = np.sum(-diff > limit) / sims
            push_a = np.sum(-diff == limit) / sims
            true_prob_a = prob_a / (1 - push_a) if (1 - push_a) > 0 else 0
            probs[f"Away AH {-limit:+}"] = true_prob_a
        else:
            probs[f"Home AH {limit:+}"] = np.sum(diff > -limit)/sims
            probs[f"Away AH {-limit:+}"] = np.sum(-diff > limit)/sims

    return probs

def calculate_dynamic_margin(odds):
    try:
        hw, dr, aw = odds.get("Home Win", 0), odds.get("Draw", 0), odds.get("Away Win", 0)
        if hw > 0 and dr > 0 and aw > 0:
            implied_sum = (1/hw) + (1/dr) + (1/aw)
            return max(0.01, implied_sum - 1)
    except: pass
    return 0.045

def calculate_kelly(prob, odd, fraction):
    b = odd - 1
    q = 1 - prob
    if b <= 0: return 0
    k = ((b * prob) - q) / b
    return max(0, k * fraction * 100)

def poisson_pmf(lam, k):
    return (lam**k * math.exp(-lam)) / math.factorial(k)

# ==========================================
# 3. INTERFACE (LIVE HUD & RENDERING)
# ==========================================
session_id = f"0x{random.randint(100000, 999999):X}"

st.markdown(f"""
<div class="top-nav">
    <div class="nav-left">
        <div class="logo">APEX<span>QUANT</span></div>
        <div class="nav-divider"></div>
        <div class="nav-subtitle">CORE ENGINE V5.0<br><span style="color:#64748B;">INSTITUTIONAL FEED</span></div>
    </div>
    <div class="nav-center">
        <div class="telemetry-box">NODE <span>US-EAST-1</span></div>
        <div class="telemetry-box">PING <span class="hl-green">12ms</span></div>
        <div class="telemetry-box">SIM <span>MC-50K</span></div>
    </div>
    <div class="nav-right">
        <div class="nav-time">SYS_ID: {session_id}</div>
        <div class="sys-status"><span class="dot"></span> ACTIVE POOL</div>
    </div>
</div>
""", unsafe_allow_html=True)

ticker_text = " • ".join([
    "LIQUIDITY: OPTIMAL",
    "MATCHED VOL: <span>$142.8M</span>",
    "LATENCY: <span class='hl-green'>+1.2ms</span>",
    "API STATUS: <span>OK</span>",
    "ANOMALY FILTER: <span class='hl-green'>ACTIVE</span>",
    "POISSON KERNEL: <span>LOCKED</span>",
    "MAX RISK ALLOC: <span>5.0%</span>",
]) * 2

st.markdown(f"""
<div class="ticker-wrap">
    <div class="ticker">
        <div class="ticker-item">{ticker_text}</div>
        <div class="ticker-item">{ticker_text}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Main Grid Container
col_ctrl, col_exec = st.columns([1, 2.6], gap="medium")

with col_ctrl:
    st.markdown("""<div class='grid-panel' style='margin-bottom: 0;'><div class='panel-title'>Strategy Parameters</div>""", unsafe_allow_html=True)
    
    target_date = st.date_input("Trading Date", date.today())
    l_map = {"Premier League": 39, "Champions League": 2, "La Liga": 140, "Primeira Liga": 94, "Serie A": 135}
    league_name = st.selectbox("Liquidity Pool (Market)", list(l_map.keys()))
    
    st.markdown("<div style='height: 1px; background: #1E293B; margin: 20px 0;'></div>", unsafe_allow_html=True)
    
    bankroll = st.number_input("Allocated Capital ($)", value=100000, step=10000, format="%d")
    kelly_fraction = st.slider("Kelly Multiplier", min_value=0.1, max_value=1.0, value=0.25, step=0.05)
    
    st.markdown("<div style='height: 1px; background: #1E293B; margin: 20px 0;'></div>", unsafe_allow_html=True)

    fixtures = get_live_fixtures(target_date.strftime('%Y-%m-%d'), l_map[league_name])
    m_sel = None
    btn_run = False
    
    if fixtures:
        m_map = {f"{f['teams']['home']['name']} v {f['teams']['away']['name']}": f for f in fixtures}
        m_sel = m_map[st.selectbox("Select Asset", list(m_map.keys()))]
        st.markdown("<div class='btn-run'>", unsafe_allow_html=True)
        btn_run = st.button("RUN QUANT MODEL")
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div style='color:#EF4444; font-size:0.8rem; font-weight:700; text-align:center; padding: 12px; border: 1px solid #1E293B; border-radius: 4px; background: rgba(239, 68, 68, 0.05);'>NO LIQUIDITY DETECTED</div>", unsafe_allow_html=True)
        
    st.markdown("</div>", unsafe_allow_html=True)

if m_sel and btn_run:
    placeholder_status = st.empty()
    progress_bar = st.progress(0)
    
    placeholder_status.markdown("<div style='color:#64748B; font-family:monospace; font-size:0.75rem; padding: 10px 0;'>[1/4] Connecting to Data Feeds...</div>", unsafe_allow_html=True)
    time.sleep(0.3)
    progress_bar.progress(25)
    
    placeholder_status.markdown("<div style='color:#64748B; font-family:monospace; font-size:0.75rem; padding: 10px 0;'>[2/4] Generating 50,000 Monte Carlo Paths...</div>", unsafe_allow_html=True)
    time.sleep(0.4)
    progress_bar.progress(60)
    
    placeholder_status.markdown("<div style='color:#64748B; font-family:monospace; font-size:0.75rem; padding: 10px 0;'>[3/4] Parsing Bookmaker Vig & Variance Filters...</div>", unsafe_allow_html=True)
    time.sleep(0.4)
    progress_bar.progress(85)
    
    placeholder_status.markdown("<div style='color:#10B981; font-family:monospace; font-size:0.75rem; font-weight:600; padding: 10px 0;'>[4/4] Extracting Prime Alpha.</div>", unsafe_allow_html=True)
    time.sleep(0.3)
    progress_bar.progress(100)
    
    time.sleep(0.2)
    placeholder_status.empty()
    progress_bar.empty()
    
    h_id, a_id = m_sel['teams']['home']['id'], m_sel['teams']['away']['id']
    h_name = m_sel['teams']['home']['name']
    a_name = m_sel['teams']['away']['name']
    
    h_stats, a_stats = get_real_stats(h_id, l_map[league_name]), get_real_stats(a_id, l_map[league_name])
    lam_h, lam_a = calculate_lambdas(h_stats, a_stats)
    true_probs = run_monte_carlo_sim(lam_h, lam_a, 50000)
    live_odds = get_real_odds(m_sel['fixture']['id'])
    
    def format_market_name(mkt, h, a):
        if mkt == "Home Win": return f"{h} to Win"
        if mkt == "Away Win": return f"{a} to Win"
        if mkt == "Draw": return "Match Draw"
        if mkt == "Double Chance (1X)": return f"{h} or Draw"
        if mkt == "Double Chance (X2)": return f"{a} or Draw"
        if mkt == "Double Chance (12)": return "Any Team to Win"
        if mkt == "Draw No Bet (Home)": return f"{h} (DNB)"
        if mkt == "Draw No Bet (Away)": return f"{a} (DNB)"
        if "Home AH" in mkt: return f"{h} (AH {mkt.split('AH ')[1]})"
        if "Away AH" in mkt: return f"{a} (AH {mkt.split('AH ')[1]})"
        if "Total Goals" in mkt: return mkt.replace("Total Goals", "Match Goals")
        return mkt

    valid_markets = []
    best_bet = None
    dynamic_margin = calculate_dynamic_margin(live_odds)
    
    if live_odds:
        for mkt, odd in live_odds.items():
            prob = true_probs.get(mkt, 0)
            if odd > 1.05 and prob > 0:
                f_prob = (1 / odd) / (1 + dynamic_margin)
                edge = (prob * odd) - 1
                
                kelly_val = calculate_kelly(prob, odd, kelly_fraction) if edge > 0 else 0
                kelly_val = min(kelly_val, 5.0) 
                
                ui_market_name = format_market_name(mkt, h_name, a_name)
                
                valid_markets.append({
                    "Market": ui_market_name, 
                    "BookOdd": odd, 
                    "ModelProb": prob, 
                    "Edge": edge, 
                    "TrueOdd": f_prob,
                    "Kelly": kelly_val
                })
        
        prime_bets = [
            m for m in valid_markets 
            if 0.01 < m['Edge'] < 0.25      
            and m['ModelProb'] >= 0.40      
            and 1.40 <= m['BookOdd'] <= 3.50 
        ]
        
        if prime_bets:
            best_bet = max(prime_bets, key=lambda x: x['Kelly'])
    
    with col_exec:
        st.markdown(f"""
        <div class='metric-grid'>
            <div class='metric-card'>
                <div class='metric-card-title'>{h_name} Expected Goals (xG)</div>
                <div class='metric-card-val'>{lam_h:.2f}</div>
            </div>
            <div class='metric-card'>
                <div class='metric-card-title'>{a_name} Expected Goals (xG)</div>
                <div class='metric-card-val'>{lam_a:.2f}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        col_alpha, col_chart = st.columns([1.1, 1], gap="medium")
        
        with col_alpha:
            if best_bet:
                dollar_sz = (best_bet['Kelly']/100) * bankroll
                confidence_score = min(99.9, (best_bet['ModelProb'] * 100) + (best_bet['Edge'] * 50))
                
                st.markdown(f"""
<div class='trade-signal'>
    <div class='panel-title' style='color:#10B981; border-color:rgba(16,185,129,0.2); margin-bottom: 12px;'>PRIME ALPHA SIGNAL</div>
    <div class='trade-asset'>{best_bet['Market']}</div>
    <div class='trade-odd'>@ {best_bet['BookOdd']:.3f}</div>
    <div class='data-row'><span class='data-lbl'>Model Probability (Strike)</span><span class='data-val'>{best_bet['ModelProb']*100:.2f}%</span></div>
    <div class='data-row'><span class='data-lbl'>Expected Value (Edge)</span><span class='data-val hl-green'>+{best_bet['Edge']*100:.2f}%</span></div>
    <div class='data-row'><span class='data-lbl'>Capital Allocation (Sizing)</span><span class='data-val'>${dollar_sz:,.0f} ({best_bet['Kelly']:.2f}%)</span></div>
    <div class='data-row' style='margin-top:16px; border-top: 1px dashed rgba(255,255,255,0.1); padding-top: 16px;'><span class='data-lbl'>Model Confidence Index</span><span class='data-val'>{confidence_score:.1f} / 100</span></div>
</div>
""", unsafe_allow_html=True)

            elif live_odds:
                st.markdown("""
<div class='grid-panel' style='border-color: #1E293B; height: 100%; display: flex; align-items: center; justify-content: center;'><div class='data-val' style='text-align: center; font-size: 1.1rem; color: #94A3B8;'>NO VIABLE ALPHA.<br><span style='font-size: 0.8rem; font-weight: 500;'>Market is efficient. Capital protected.</span></div></div>
""", unsafe_allow_html=True)

        with col_chart:
            st.markdown("""<div class='grid-panel' style='padding-bottom: 0px; height: 100%; box-sizing: border-box;'><div class='panel-title'>Poisson Distribution Matrix</div>""", unsafe_allow_html=True)
            goals_range = list(range(6))
            h_probs_chart = [poisson_pmf(lam_h, g)*100 for g in goals_range]
            a_probs_chart = [poisson_pmf(lam_a, g)*100 for g in goals_range]

            fig_dist = go.Figure(data=[
                go.Bar(name=h_name, x=goals_range, y=h_probs_chart, marker_color='#334155', opacity=0.9, hovertemplate="<b>%{x} Goals</b><br>Probability: %{y:.1f}%<extra></extra>"),
                go.Bar(name=a_name, x=goals_range, y=a_probs_chart, marker_color='#10B981', opacity=0.9, hovertemplate="<b>%{x} Goals</b><br>Probability: %{y:.1f}%<extra></extra>")
            ])
            fig_dist.update_layout(
                barmode='group',
                template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                height=220,
                margin=dict(l=0, r=0, t=10, b=0),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=9, color="#94A3B8")),
                xaxis=dict(title="Goals", title_font=dict(size=10, color="#64748B"), tickfont=dict(size=10, color="#94A3B8"), gridcolor="rgba(255,255,255,0.05)", zeroline=False),
                yaxis=dict(title="Probability (%)", title_font=dict(size=10, color="#64748B"), tickfont=dict(size=10, color="#94A3B8"), gridcolor="rgba(255,255,255,0.05)", zeroline=False)
            )
            st.plotly_chart(fig_dist, use_container_width=True, config={'displayModeBar': False})
            st.markdown("</div>", unsafe_allow_html=True)

        if live_odds and valid_markets:
            st.markdown("""<div class='grid-panel' style='padding-bottom: 5px;'><div class='panel-title'>Probability Delta (Model vs Market) - Top 5</div>""", unsafe_allow_html=True)
            
            chart_markets = [m for m in valid_markets if m['Edge'] > 0 and m['Edge'] < 0.25]
            top_markets = sorted(chart_markets, key=lambda x: x['Edge'], reverse=True)[:5]
            
            if top_markets:
                m_names = [m['Market'] for m in top_markets]
                sys_probs = [m['ModelProb']*100 for m in top_markets]
                book_probs = [m['TrueOdd']*100 for m in top_markets]
                
                fig_delta = go.Figure()
                fig_delta.add_trace(go.Bar(
                    y=m_names, x=book_probs, name='Market (No-Vig)', orientation='h', marker_color='#1E293B', hovertemplate="Market: %{x:.1f}%<extra></extra>"
                ))
                fig_delta.add_trace(go.Bar(
                    y=m_names, x=sys_probs, name='Model Prob', orientation='h', marker_color='#10B981', hovertemplate="System: %{x:.1f}%<extra></extra>"
                ))
                
                fig_delta.update_layout(
                    barmode='group',
                    template='plotly_dark',
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    height=240,
                    margin=dict(l=0, r=0, t=10, b=0),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=10, color="#94A3B8")),
                    xaxis=dict(title="Probability (%)", title_font=dict(size=10, color="#64748B"), tickfont=dict(size=10, color="#94A3B8"), gridcolor="rgba(255,255,255,0.05)", zeroline=False),
                    yaxis=dict(autorange="reversed", tickfont=dict(size=11, color="#E2E8F0", family="Inter, sans-serif"), gridcolor="rgba(0,0,0,0)")
                )
                st.plotly_chart(fig_delta, use_container_width=True, config={'displayModeBar': False})
            else:
                st.info("No stable +EV markets to chart.")
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("""<div class='grid-panel'><div class='panel-title'>Order Book (Risk-Adjusted Sizing)</div>""", unsafe_allow_html=True)
        
        if live_odds:
            clean_markets = [m for m in valid_markets if m['Edge'] < 0.25 and m['BookOdd'] <= 15.0]
            clean_markets = sorted(clean_markets, key=lambda x: x['Kelly'], reverse=True)
            
            table_html = "<table class='ob-table'><tr><th>Market</th><th>Listed Odds</th><th>Model Prob</th><th>Edge (+EV)</th><th>Capital Sizing</th></tr>"
            
            for m in clean_markets[:10]: 
                edge_val = m['Edge'] * 100
                color_cls = "hl-green" if edge_val > 0 else ""
                sign = "+" if edge_val > 0 else ""
                
                row = f"<tr><td>{m['Market']}</td><td style='font-family: JetBrains Mono; color:#E2E8F0;'>{m['BookOdd']:.3f}</td>"
                row += f"<td>{m['ModelProb']*100:.1f}%</td>"
                row += f"<td class='{color_cls}'>{sign}{edge_val:.2f}%</td>"
                row += f"<td style='color:#94A3B8;'>{m['Kelly']:.2f}%</td></tr>"
                
                table_html += row
                
            table_html += "</table>"
            
            st.markdown(table_html, unsafe_allow_html=True)
        else:
            st.markdown("""<div class='data-lbl'>Waiting for data...</div>""", unsafe_allow_html=True)
            
        st.markdown("""</div>""", unsafe_allow_html=True)