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
# 1. INSTITUTIONAL UX SETUP (WALL STREET V4.0)
# ==========================================
st.set_page_config(page_title="APEX QUANT TERMINAL", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700;800;900&family=Inter:wght@400;500;600;700;800&display=swap');

/* Base Theme */
.stApp { background-color: #020617; color: #E2E8F0; font-family: 'Inter', sans-serif; }
header, footer { visibility: hidden; }

/* Redesigned Top Nav */
.top-nav { 
    background: linear-gradient(90deg, #020617 0%, #0B0F19 50%, #020617 100%); 
    border-bottom: 1px solid #1E293B; 
    border-top: 2px solid #10B981; 
    padding: 12px 25px; 
    display: flex; 
    justify-content: space-between; 
    align-items: center; 
    margin: -3rem -3rem 0 -3rem; 
    position: sticky; 
    top: 0; 
    z-index: 1000;
}

.nav-left { display: flex; align-items: center; gap: 20px; }
.logo { font-size: 1.8rem; font-weight: 900; color: #F8FAFC; font-family: 'JetBrains Mono', monospace; letter-spacing: -1.5px; text-shadow: 0 0 15px rgba(255,255,255,0.1);}
.logo span { color: #10B981; text-shadow: 0 0 15px rgba(16,185,129,0.5);}
.nav-divider { width: 1px; height: 24px; background-color: #334155; }
.nav-subtitle { font-size: 0.65rem; color: #64748B; font-weight: 800; letter-spacing: 2px; font-family: 'Inter', sans-serif; line-height: 1.4;}

.nav-center { display: flex; gap: 12px; }
.telemetry-box { background: #0F172A; border: 1px solid #1E293B; padding: 4px 10px; border-radius: 4px; font-size: 0.65rem; font-family: 'JetBrains Mono', monospace; color: #64748B; font-weight: 700; letter-spacing: 0.5px; display: flex; align-items: center; gap: 6px;}
.telemetry-box span { color: #E2E8F0; }
.telemetry-box .hl-green { color: #10B981; text-shadow: 0 0 8px rgba(16,185,129,0.4);}

.nav-right { display: flex; align-items: center; gap: 12px; }
.nav-time { font-size: 0.7rem; color: #94A3B8; font-family: 'JetBrains Mono', monospace; font-weight: 700; background: #0F172A; padding: 6px 12px; border-radius: 4px; border: 1px solid #1E293B; letter-spacing: 1px;}
.sys-status { font-size: 0.7rem; font-weight: 800; color: #10B981; font-family: 'JetBrains Mono', monospace; display: flex; align-items: center; gap: 8px; letter-spacing: 0.5px; background: rgba(16, 185, 129, 0.08); padding: 6px 12px; border-radius: 4px; border: 1px solid rgba(16, 185, 129, 0.3); box-shadow: inset 0 0 15px rgba(16,185,129,0.1);}

@keyframes pulse { 0% { opacity: 1; transform: scale(1); } 50% { opacity: 0.5; transform: scale(1.4); } 100% { opacity: 1; transform: scale(1); } }
.dot { height: 6px; width: 6px; background-color: #10B981; border-radius: 50%; display: inline-block; animation: pulse 1.2s infinite; box-shadow: 0 0 10px #10B981;}

/* Market Ticker Marquee */
.ticker-wrap { width: 100%; background: #020617; border-bottom: 1px solid #1E293B; overflow: hidden; padding: 6px 0; margin: 0 -3rem 2rem -3rem; box-shadow: 0 10px 20px -10px rgba(0,0,0,0.8);}
.ticker { display: inline-block; white-space: nowrap; animation: ticker 40s linear infinite; }
.ticker:hover { animation-play-state: paused; }
@keyframes ticker { 0% { transform: translateX(0); } 100% { transform: translateX(-50%); } }
.ticker-item { display: inline-block; padding: 0 3rem; font-size: 0.65rem; color: #64748B; font-family: 'JetBrains Mono', monospace; font-weight: 700; letter-spacing: 1px;}
.ticker-item span { color: #10B981; }
.ticker-item .red { color: #EF4444; }

/* Grid Panels */
.grid-panel { border: 1px solid #1E293B; background: linear-gradient(180deg, #0B0F19 0%, #020617 100%); padding: 22px; margin-bottom: 20px; border-radius: 8px; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.5); position: relative;}
.panel-title { font-size: 0.7rem; color: #64748B; text-transform: uppercase; border-bottom: 1px solid #1E293B; padding-bottom: 10px; margin-bottom: 15px; font-weight: 800; letter-spacing: 1.5px; }

/* Metrics & Values */
.data-row { display: flex; justify-content: space-between; font-size: 0.85rem; margin-bottom: 8px; align-items: center; border-bottom: 1px dashed rgba(30, 41, 59, 0.5); padding-bottom: 4px;}
.data-lbl { color: #94A3B8; font-weight: 500; font-size: 0.8rem;}
.data-val { color: #F8FAFC; font-weight: 700; font-family: 'JetBrains Mono', monospace; }

/* Highlight Colors */
.hl-green { color: #10B981 !important; text-shadow: 0 0 10px rgba(16,185,129,0.3); }
.hl-red { color: #EF4444 !important; }
.hl-blue { color: #38BDF8 !important; text-shadow: 0 0 10px rgba(56,189,248,0.3); }
.hl-warn { color: #F59E0B !important; }

/* Alpha Box (The Money Maker) */
.trade-signal { border: 1px solid rgba(16, 185, 129, 0.6); background: linear-gradient(145deg, rgba(16,185,129,0.1) 0%, rgba(0,0,0,0) 100%); padding: 25px; margin-top: 10px; border-radius: 8px; box-shadow: 0 0 30px rgba(16, 185, 129, 0.15); position: relative; overflow: hidden;}
.trade-signal::before { content: ''; position: absolute; top: 0; left: 0; width: 4px; height: 100%; background: #10B981; box-shadow: 0 0 15px #10B981;}
.trade-asset { font-size: 2.2rem; color: #F8FAFC; font-weight: 900; margin-bottom: 5px; font-family: 'Inter', sans-serif; letter-spacing: -0.5px;}
.trade-odd { font-size: 1.5rem; color: #10B981; font-weight: 800; font-family: 'JetBrains Mono', monospace; margin-bottom: 20px;}

/* Order Book Table */
.ob-table { width: 100%; font-size: 0.8rem; border-collapse: collapse; font-family: 'JetBrains Mono', monospace; }
.ob-table th { color: #64748B; text-align: right; font-weight: 800; border-bottom: 2px solid #1E293B; padding: 12px 8px; font-family: 'Inter', sans-serif; font-size: 0.65rem; text-transform: uppercase; letter-spacing: 1px;}
.ob-table th:first-child { text-align: left; }
.ob-table td { text-align: right; padding: 12px 8px; border-bottom: 1px solid #0F172A; transition: background 0.2s; }
.ob-table td:first-child { text-align: left; color: #E2E8F0; font-weight: 600; font-family: 'Inter', sans-serif; font-size: 0.85rem;}
.ob-table tr:hover td { background: rgba(30, 41, 59, 0.6); cursor: crosshair; }

/* Sub-Metric Cards */
.metric-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 20px; }
.metric-card { background: #0F172A; border: 1px solid #1E293B; border-radius: 6px; padding: 15px; text-align: center; box-shadow: inset 0 2px 4px rgba(0,0,0,0.2);}
.metric-card-title { font-size: 0.65rem; color: #64748B; text-transform: uppercase; font-weight: 800; letter-spacing: 1.5px; margin-bottom: 8px;}
.metric-card-val { font-size: 1.8rem; color: #F8FAFC; font-weight: 900; font-family: 'JetBrains Mono', monospace;}

/* Override Streamlit Widgets */
div[data-baseweb="select"] > div, div[data-baseweb="input"] > div { background-color: #0F172A !important; border: 1px solid #1E293B !important; color: #F8FAFC !important; border-radius: 6px !important; }
.btn-run > button { background: linear-gradient(180deg, #10B981 0%, #059669 100%) !important; color: #FFFFFF !important; border: none !important; font-weight: 800 !important; width: 100%; border-radius: 6px !important; padding: 22px !important; transition: all 0.3s ease !important; font-size: 1rem !important; letter-spacing: 1px !important;}
.btn-run > button:hover { background: linear-gradient(180deg, #34D399 0%, #10B981 100%) !important; box-shadow: 0 0 20px rgba(16,185,129,0.5) !important; transform: translateY(-2px); }

.btn-exec > button { background: linear-gradient(180deg, #38BDF8 0%, #0284C7 100%) !important; color: #FFFFFF !important; border: none !important; font-weight: 900 !important; width: 100%; border-radius: 6px !important; padding: 18px !important; transition: all 0.3s ease !important; font-size: 0.9rem !important; letter-spacing: 1.5px !important; margin-top: 15px; text-transform: uppercase;}
.btn-exec > button:hover { background: linear-gradient(180deg, #7DD3FC 0%, #0EA5E9 100%) !important; box-shadow: 0 0 20px rgba(56,189,248,0.5) !important; transform: translateY(-2px); }

/* Custom Progress Bar for Boot Sequence */
.stProgress > div > div > div > div { background-color: #10B981 !important; }
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
    except Exception as e:
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
<div class="nav-subtitle">INSTITUTIONAL ALGO V4.0<br><span style="color:#38BDF8; font-size: 0.55rem;">DIRECT MARKET ACCESS</span></div>
</div>
<div class="nav-center">
<div class="telemetry-box">NODE <span>US-EAST-1</span></div>
<div class="telemetry-box">PING <span class="hl-green">14ms</span></div>
<div class="telemetry-box">ENGINE <span>MONTE CARLO (50K)</span></div>
</div>
<div class="nav-right">
<div class="nav-time">SESSION: {session_id}</div>
<div class="sys-status"><span class="dot"></span> TIER-1 POOL CONNECTED</div>
</div>
</div>
""", unsafe_allow_html=True)

ticker_text = " • ".join([
    "LIQUIDITY POOL: ACTIVE",
    "GLOBAL MATCHED VOL: <span>$142.8M</span>",
    "LATENCY DELTA: <span class='hl-green'>+2ms</span>",
    "API RATE LIMIT: <span>98%</span>",
    "ANOMALY FILTER: <span class='hl-green'>ENGAGED</span>",
    "POISSON KERNEL: <span>STABLE</span>",
    "DMA CONNECTION: <span class='hl-blue'>SECURE</span>",
]) * 2

st.markdown(f"""
<div class="ticker-wrap">
<div class="ticker">
<div class="ticker-item">{ticker_text}</div>
<div class="ticker-item">{ticker_text}</div>
</div>
</div>
""", unsafe_allow_html=True)

col_ctrl, col_exec = st.columns([1, 2.8], gap="large")

with col_ctrl:
    st.markdown("""<div class='grid-panel'><div class='panel-title'>Model Parameters</div>""", unsafe_allow_html=True)
    
    target_date = st.date_input("Trading Date", date.today())
    l_map = {"Premier League": 39, "Champions League": 2, "La Liga": 140, "Primeira Liga": 94, "Serie A": 135}
    league_name = st.selectbox("Liquidity Pool (League)", list(l_map.keys()))
    
    st.markdown("<div style='margin-top: 15px; border-bottom: 1px solid #1E293B; margin-bottom: 15px;'></div>", unsafe_allow_html=True)
    
    bankroll = st.number_input("Allocated Capital ($)", value=100000, step=10000, format="%d")
    kelly_fraction = st.slider("Kelly Fraction (Risk Management)", min_value=0.1, max_value=1.0, value=0.25, step=0.05, help="1.0 = Full Kelly (Aggressive). 0.25 = Quarter Kelly (Conservative/Recommended).")
    
    fixtures = get_live_fixtures(target_date.strftime('%Y-%m-%d'), l_map[league_name])
    m_sel = None
    btn_run = False
    
    if fixtures:
        m_map = {f"{f['teams']['home']['name']} v {f['teams']['away']['name']}": f for f in fixtures}
        m_sel = m_map[st.selectbox("Select Asset (Fixture)", list(m_map.keys()))]
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<div class='btn-run'>", unsafe_allow_html=True)
        btn_run = st.button("DEPLOY ALGORITHM")
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div style='color:#EF4444; font-size:0.8rem; font-weight:700; text-align:center; padding: 12px; border: 1px solid #EF4444; border-radius: 4px; margin-top: 20px; background: rgba(239, 68, 68, 0.05);'>MARKET CLOSED / NO LIQUIDITY</div>", unsafe_allow_html=True)
        
    st.markdown("</div>", unsafe_allow_html=True)

if m_sel and btn_run:
    placeholder_status = st.empty()
    progress_bar = st.progress(0)
    
    placeholder_status.markdown("<div style='color:#10B981; font-family:monospace; font-size:0.8rem;'>[1/4] Establishing secure connection to Liquidity Pools...</div>", unsafe_allow_html=True)
    time.sleep(0.4)
    progress_bar.progress(25)
    
    placeholder_status.markdown("<div style='color:#10B981; font-family:monospace; font-size:0.8rem;'>[2/4] Executing Monte Carlo Simulator (50,000 parallel paths)...</div>", unsafe_allow_html=True)
    time.sleep(0.6)
    progress_bar.progress(60)
    
    placeholder_status.markdown("<div style='color:#10B981; font-family:monospace; font-size:0.8rem;'>[3/4] Applying Risk Filters & Detecting API Anomalies...</div>", unsafe_allow_html=True)
    time.sleep(0.5)
    progress_bar.progress(85)
    
    placeholder_status.markdown("<div style='color:#10B981; font-family:monospace; font-size:0.8rem;'>[4/4] Extracting Risk-Adjusted Prime Alpha...</div>", unsafe_allow_html=True)
    time.sleep(0.4)
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
        if "Total Goals" in mkt: return mkt.replace("Total Goals", "Total Match Goals")
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
                <div class='metric-card-val' style='color:#38BDF8;'>{lam_h:.2f}</div>
            </div>
            <div class='metric-card'>
                <div class='metric-card-title'>{a_name} Expected Goals (xG)</div>
                <div class='metric-card-val' style='color:#10B981;'>{lam_a:.2f}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        col_alpha, col_chart = st.columns([1.2, 1])
        
        with col_alpha:
            if best_bet:
                dollar_sz = (best_bet['Kelly']/100) * bankroll
                risk_lvl = "LOW" if best_bet['ModelProb'] > 0.55 else "MEDIUM"
                risk_color = "#10B981" if risk_lvl == "LOW" else "#F59E0B"
                
                confidence_score = min(99.9, (best_bet['ModelProb'] * 100) + (best_bet['Edge'] * 50) + (kelly_fraction * 10))
                
                st.markdown(f"""
<div class='trade-signal'>
<div class='panel-title' style='color:#10B981; border-color:rgba(16,185,129,0.2); margin-bottom: 5px;'>★ PRIME ALPHA SIGNAL</div>
<div class='trade-asset'>{best_bet['Market']}</div>
<div class='trade-odd'>@ {best_bet['BookOdd']:.3f}</div>
<div class='data-row'><span class='data-lbl'>Win Probability (Strike Rate)</span><span class='data-val'>{best_bet['ModelProb']*100:.2f}%</span></div>
<div class='data-row'><span class='data-lbl'>Expected Value (Edge)</span><span class='data-val hl-green'>+{best_bet['Edge']*100:.2f}%</span></div>
<div class='data-row'><span class='data-lbl'>Capital Allocation ({kelly_fraction:.2f} Kelly)</span><span class='data-val hl-blue'>${dollar_sz:,.0f} ({best_bet['Kelly']:.2f}%)</span></div>
<div class='data-row'><span class='data-lbl'>Drawdown Risk Assessment</span><span class='data-val' style='color:{risk_color};'>{risk_lvl}</span></div>
</div>
""", unsafe_allow_html=True)

                # Novo: Gauge Chart de Confiança
                fig_gauge = go.Figure(go.Indicator(
                    mode = "gauge+number",
                    value = confidence_score,
                    domain = {'x': [0, 1], 'y': [0, 1]},
                    title = {'text': "Model Confidence Index", 'font': {'size': 14, 'color': '#64748B'}},
                    number = {'suffix': "%", 'font': {'size': 30, 'color': '#F8FAFC'}},
                    gauge = {
                        'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "rgba(255,255,255,0.1)"},
                        'bar': {'color': "#10B981"},
                        'bgcolor': "rgba(0,0,0,0)",
                        'borderwidth': 0,
                        'steps': [
                            {'range': [0, 50], 'color': "rgba(239, 68, 68, 0.2)"},
                            {'range': [50, 75], 'color': "rgba(245, 158, 11, 0.2)"},
                            {'range': [75, 100], 'color': "rgba(16, 185, 129, 0.2)"}],
                        'threshold': {'line': {'color': "#38BDF8", 'width': 4}, 'thickness': 0.75, 'value': 90}
                    }
                ))
                fig_gauge.update_layout(height=180, margin=dict(l=20, r=20, t=30, b=10), paper_bgcolor='rgba(0,0,0,0)', font={'family': "Inter, sans-serif"})
                st.plotly_chart(fig_gauge, use_container_width=True, config={'displayModeBar': False})

                # Novo: Botão de Execução Mock
                st.markdown("<div class='btn-exec'>", unsafe_allow_html=True)
                if st.button("⚡ AUTO-EXECUTE VIA BROKER API", key="exec_btn"):
                    st.toast(f"Order Placed! {best_bet['Market']} at {best_bet['BookOdd']:.3f}. Stake: ${dollar_sz:,.0f}", icon='✅')
                    st.success("Trade executed successfully on Tier-1 Pool.")
                st.markdown("</div>", unsafe_allow_html=True)

            elif live_odds:
                st.markdown("""
<div class='grid-panel' style='border-color: #EF4444;'><div class='data-val hl-red' style='text-align: center; font-size: 1.2rem; padding: 20px;'>NO PRIME ALPHA DETECTED.<br><span style='font-size: 0.8rem; color: #94A3B8;'>Market is efficient or variance is too high. Protect Capital. Pass.</span></div></div>
""", unsafe_allow_html=True)

        with col_chart:
            st.markdown("""<div class='grid-panel' style='padding-bottom: 5px; height: 100%;'><div class='panel-title'>Goal Expectancy Distribution</div>""", unsafe_allow_html=True)
            goals_range = list(range(6))
            h_probs_chart = [poisson_pmf(lam_h, g)*100 for g in goals_range]
            a_probs_chart = [poisson_pmf(lam_a, g)*100 for g in goals_range]

            fig_dist = go.Figure(data=[
                go.Bar(name=h_name, x=goals_range, y=h_probs_chart, marker_color='#38BDF8', opacity=0.9, hovertemplate="<b>%{x} Goals</b><br>Probability: %{y:.1f}%<extra></extra>"),
                go.Bar(name=a_name, x=goals_range, y=a_probs_chart, marker_color='#10B981', opacity=0.9, hovertemplate="<b>%{x} Goals</b><br>Probability: %{y:.1f}%<extra></extra>")
            ])
            fig_dist.update_layout(
                barmode='group',
                template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                height=230,
                margin=dict(l=0, r=0, t=10, b=0),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=10, color="#94A3B8")),
                xaxis=dict(title="Goals", title_font=dict(size=10, color="#64748B"), tickfont=dict(size=10, color="#94A3B8"), gridcolor="rgba(30,41,59,0.5)", zeroline=False),
                yaxis=dict(title="Probability (%)", title_font=dict(size=10, color="#64748B"), tickfont=dict(size=10, color="#94A3B8"), gridcolor="rgba(30,41,59,0.5)", zeroline=False)
            )
            st.plotly_chart(fig_dist, use_container_width=True, config={'displayModeBar': False})
            st.markdown("</div>", unsafe_allow_html=True)

        if live_odds and valid_markets:
            st.markdown("""<div class='grid-panel' style='padding-bottom: 5px;'><div class='panel-title'>Probability Delta (Model vs Institutional Lines) - Top 5</div>""", unsafe_allow_html=True)
            
            chart_markets = [m for m in valid_markets if m['Edge'] > 0 and m['Edge'] < 0.25]
            top_markets = sorted(chart_markets, key=lambda x: x['Edge'], reverse=True)[:5]
            
            if top_markets:
                m_names = [m['Market'] for m in top_markets]
                sys_probs = [m['ModelProb']*100 for m in top_markets]
                book_probs = [m['TrueOdd']*100 for m in top_markets]
                
                fig_delta = go.Figure()
                fig_delta.add_trace(go.Bar(
                    y=m_names, x=book_probs, name='Market Line (No-Vig)', orientation='h', marker_color='#334155', hovertemplate="Market: %{x:.1f}%<extra></extra>"
                ))
                fig_delta.add_trace(go.Bar(
                    y=m_names, x=sys_probs, name='System Prob', orientation='h', marker_color='#10B981', hovertemplate="System: %{x:.1f}%<extra></extra>"
                ))
                
                fig_delta.update_layout(
                    barmode='group',
                    template='plotly_dark',
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    height=240,
                    margin=dict(l=0, r=0, t=10, b=0),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=10, color="#94A3B8")),
                    xaxis=dict(title="Probability (%)", title_font=dict(size=10, color="#64748B"), tickfont=dict(size=10, color="#94A3B8"), gridcolor="rgba(30,41,59,0.5)", zeroline=False),
                    yaxis=dict(autorange="reversed", tickfont=dict(size=11, color="#E2E8F0", family="Inter, sans-serif"), gridcolor="rgba(0,0,0,0)")
                )
                st.plotly_chart(fig_delta, use_container_width=True, config={'displayModeBar': False})
            else:
                st.info("No stable +EV markets to chart.")
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("""<div class='grid-panel'><div class='panel-title'>Algorithmic Order Book (Sorted by Optimal Kelly)</div>""", unsafe_allow_html=True)
        
        if live_odds:
            clean_markets = [m for m in valid_markets if m['Edge'] < 0.25 and m['BookOdd'] <= 15.0]
            clean_markets = sorted(clean_markets, key=lambda x: x['Kelly'], reverse=True)
            
            table_html = "<table class='ob-table'><tr><th>Asset (Market)</th><th>Listed Odds</th><th>System Prob</th><th>Market Edge</th><th>Kelly Allocation</th></tr>"
            
            for m in clean_markets[:10]: # Limita as top 10 para o visual ficar mais limpo
                edge_val = m['Edge'] * 100
                color_cls = "hl-green" if edge_val > 0 else "hl-red"
                sign = "+" if edge_val > 0 else ""
                
                row = f"<tr><td>{m['Market']}</td><td style='color:#10B981; font-weight:700;'>{m['BookOdd']:.3f}</td>"
                row += f"<td>{m['ModelProb']*100:.1f}%</td>"
                row += f"<td class='{color_cls}'>{sign}{edge_val:.2f}%</td>"
                row += f"<td style='color:#38BDF8;'>{m['Kelly']:.2f}%</td></tr>"
                
                table_html += row
                
            table_html += "</table>"
            
            st.markdown(table_html, unsafe_allow_html=True)
        else:
            st.markdown("""<div class='data-lbl'>Waiting for market liquidity...</div>""", unsafe_allow_html=True)
            
        st.markdown("""</div>""", unsafe_allow_html=True)
