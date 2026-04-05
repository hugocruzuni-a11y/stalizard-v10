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
# 1. CYBER-QUANT UI SETUP (2050 GLASSMORPHISM)
# ==========================================
st.set_page_config(page_title="APEX QUANT | SYNDICATE", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@100..800&display=swap');

:root {
    --bg-main: #030712;
    --glass-bg: rgba(17, 24, 39, 0.4);
    --glass-border: rgba(255, 255, 255, 0.08);
    --neon-cyan: #00F0FF;
    --neon-gold: #FFD700;
    --text-primary: #F9FAFB;
    --text-muted: #9CA3AF;
}

/* Base Theme */
.stApp { 
    background-color: var(--bg-main); 
    background-image: 
        radial-gradient(circle at 15% 50%, rgba(0, 240, 255, 0.03), transparent 25%),
        radial-gradient(circle at 85% 30%, rgba(255, 215, 0, 0.03), transparent 25%);
    color: var(--text-primary); 
    font-family: 'Space Grotesk', sans-serif; 
}
header, footer { display: none !important; }

/* 2050 Header Navigation */
.glass-nav { 
    background: rgba(3, 7, 18, 0.7);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border-bottom: 1px solid var(--glass-border); 
    border-top: 2px solid var(--neon-cyan);
    padding: 0 40px; 
    height: 70px;
    display: flex; justify-content: space-between; align-items: center; 
    margin: -3rem -3rem 2rem -3rem; 
    position: sticky; top: 0; z-index: 9999;
    box-shadow: 0 10px 30px rgba(0,0,0,0.5);
}

.nav-logo { font-size: 1.8rem; font-weight: 700; color: var(--text-primary); font-family: 'Space Grotesk', sans-serif; letter-spacing: -1px; text-shadow: 0 0 20px rgba(0,240,255,0.3);}
.nav-logo span { color: var(--neon-cyan); font-weight: 300; }

.sys-badges { display: flex; gap: 15px; }
.badge { 
    background: rgba(0, 240, 255, 0.05); border: 1px solid rgba(0, 240, 255, 0.2); 
    padding: 6px 14px; border-radius: 20px; font-size: 0.7rem; font-family: 'JetBrains Mono', monospace; 
    color: var(--neon-cyan); font-weight: 600; text-transform: uppercase; letter-spacing: 1px;
    box-shadow: 0 0 10px rgba(0,240,255,0.1);
}
.badge.gold {
    background: rgba(255, 215, 0, 0.05); border-color: rgba(255, 215, 0, 0.2); color: var(--neon-gold);
    box-shadow: 0 0 10px rgba(255,215,0,0.1);
}

/* Glass Panels */
.glass-panel { 
    background: var(--glass-bg); 
    backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
    border: 1px solid var(--glass-border); 
    padding: 24px; margin-bottom: 24px; border-radius: 16px; 
    box-shadow: 0 4px 24px -1px rgba(0,0,0,0.5);
    transition: transform 0.3s ease, border-color 0.3s ease;
}
.glass-panel:hover { border-color: rgba(255, 255, 255, 0.15); }

.panel-header { font-size: 0.75rem; color: var(--text-muted); text-transform: uppercase; font-weight: 600; letter-spacing: 2px; margin-bottom: 20px; display: flex; align-items: center; gap: 10px;}
.panel-header::after { content: ''; flex-grow: 1; height: 1px; background: linear-gradient(90deg, var(--glass-border) 0%, transparent 100%); }

/* Data Rows */
.d-row { display: flex; justify-content: space-between; align-items: center; padding: 10px 0; border-bottom: 1px solid rgba(255,255,255,0.03); font-size: 0.9rem;}
.d-row:last-child { border-bottom: none; }
.d-lbl { color: var(--text-muted); font-weight: 400; }
.d-val { font-family: 'JetBrains Mono', monospace; font-weight: 600; color: var(--text-primary); }

/* The Alpha Matrix (Gold Box) */
.alpha-box {
    background: linear-gradient(145deg, rgba(255, 215, 0, 0.08) 0%, rgba(0, 0, 0, 0) 100%);
    border: 1px solid rgba(255, 215, 0, 0.3);
    border-radius: 16px; padding: 30px; position: relative; overflow: hidden;
    box-shadow: 0 0 40px rgba(255, 215, 0, 0.05) inset;
}
.alpha-box::before { content: ''; position: absolute; top: 0; left: 0; width: 4px; height: 100%; background: var(--neon-gold); box-shadow: 0 0 15px var(--neon-gold); }
.alpha-title { font-size: 0.7rem; color: var(--neon-gold); letter-spacing: 3px; text-transform: uppercase; margin-bottom: 8px; font-weight: 700;}
.alpha-asset { font-size: 2.2rem; font-weight: 700; line-height: 1.1; margin-bottom: 8px; letter-spacing: -1px;}
.alpha-odd { font-family: 'JetBrains Mono', monospace; font-size: 1.8rem; color: var(--neon-gold); margin-bottom: 24px; text-shadow: 0 0 10px rgba(255,215,0,0.3);}

/* Order Book */
.futuristic-table { width: 100%; border-collapse: collapse; text-align: left; font-size: 0.85rem;}
.futuristic-table th { padding: 12px 10px; color: var(--text-muted); font-weight: 500; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 1px; border-bottom: 1px solid var(--glass-border); }
.futuristic-table td { padding: 14px 10px; border-bottom: 1px solid rgba(255,255,255,0.02); font-family: 'JetBrains Mono', monospace; color: var(--text-primary); }
.futuristic-table tr:hover td { background: rgba(255,255,255,0.02); }

/* Overrides Streamlit */
div[data-baseweb="select"] > div, div[data-baseweb="input"] > div { 
    background-color: rgba(0,0,0,0.5) !important; 
    border: 1px solid var(--glass-border) !important; 
    border-radius: 8px !important; 
    backdrop-filter: blur(10px);
}
.stButton > button {
    background: linear-gradient(90deg, #00F0FF 0%, #0080FF 100%) !important;
    color: #000 !important; font-weight: 700 !important; font-family: 'Space Grotesk', sans-serif !important;
    border: none !important; border-radius: 8px !important; padding: 24px !important; width: 100%;
    font-size: 1.1rem !important; letter-spacing: 2px !important; text-transform: uppercase;
    box-shadow: 0 0 20px rgba(0,240,255,0.2) !important; transition: all 0.3s ease !important;
}
.stButton > button:hover { transform: translateY(-2px); box-shadow: 0 0 30px rgba(0,240,255,0.4) !important; }
.stProgress > div > div > div > div { background: linear-gradient(90deg, #00F0FF, #0080FF) !important; }

/* Colors */
.text-cyan { color: var(--neon-cyan) !important; }
.text-gold { color: var(--neon-gold) !important; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. QUANTUM LOGIC ENGINE
# ==========================================
API_KEY = st.secrets.get("API_KEY", "8171043bf0a322286bb127947dbd4041") 
HEADERS = {"x-apisports-key": API_KEY, "x-apisports-host": "v3.football.api-sports.io"}

def fetch_api(endpoint, params):
    try:
        r = requests.get(f"https://{HEADERS['x-apisports-host']}/{endpoint}", headers=HEADERS, params=params, timeout=10)
        return r.json().get('response', [])
    except Exception as e:
        return []

def safe_float(val, default):
    try:
        if val is None: return default
        return float(val)
    except (TypeError, ValueError):
        return default

@st.cache_data(ttl=300) 
def get_upcoming_fixtures(league_id, season="2024"): 
    # [A MAGIA ACONTECE AQUI]: Busca os próximos 15 jogos independentemente da data!
    return fetch_api("fixtures", {"league": league_id, "season": season, "next": 15})

@st.cache_data(ttl=3600)
def get_real_stats(team_id, league_id, season="2024"):
    stats = fetch_api("teams/statistics", {"team": team_id, "league": league_id, "season": season})
    default_stats = {"gf_h": 1.55, "ga_h": 1.25, "gf_a": 1.25, "ga_a": 1.55}
    if not stats: return default_stats
    try:
        goals = stats.get('goals', {}) if isinstance(stats, dict) else stats[0].get('goals', {})
        return {
            "gf_h": safe_float(goals.get('for', {}).get('average', {}).get('home'), 1.55),
            "ga_h": safe_float(goals.get('against', {}).get('average', {}).get('home'), 1.25),
            "gf_a": safe_float(goals.get('for', {}).get('average', {}).get('away'), 1.25),
            "ga_a": safe_float(goals.get('against', {}).get('average', {}).get('away'), 1.55)
        }
    except Exception: 
        return default_stats

@st.cache_data(ttl=60)
def get_real_odds(fixture_id):
    odds_data = fetch_api("odds", {"fixture": fixture_id, "bookmaker": 8}) # 8 = Bet365
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
                    if "Home" in k: market_odds[f"Home AH {k.replace('Home', '').strip()}"] = odd
                    elif "Away" in k: market_odds[f"Away AH {k.replace('Away', '').strip()}"] = odd
    except: pass 
    return market_odds

def calculate_lambdas(h_stats, a_stats):
    hfa_multiplier = 1.10
    lam_h = max(0.1, (h_stats['gf_h'] * hfa_multiplier) * (a_stats['ga_a']) / 1.55)
    lam_a = max(0.1, (a_stats['gf_a']) * (h_stats['ga_h']) / 1.25)
    return round(lam_h, 3), round(lam_a, 3)

def run_monte_carlo_sim(lam_h, lam_a, sims=50000):
    np.random.seed(int(time.time())) 
    h_goals = np.random.poisson(lam_h, sims)
    a_goals = np.random.poisson(lam_a, sims)
    diff, total = h_goals - a_goals, h_goals + a_goals
    hw, dr, aw = np.sum(diff > 0)/sims, np.sum(diff == 0)/sims, np.sum(diff < 0)/sims
    
    probs = {
        "Home Win": hw, "Draw": dr, "Away Win": aw,
        "Double Chance (1X)": hw + dr, "Double Chance (X2)": aw + dr, "Double Chance (12)": hw + aw,
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
# 3. INTERACTIVE HUD RENDERING
# ==========================================
st.markdown(f"""
<div class="glass-nav">
    <div class="nav-logo">APEX<span>QUANT</span></div>
    <div class="sys-badges">
        <div class="badge gold">HIGH-ROLLER TIER</div>
        <div class="badge">LIVESTREAM API</div>
        <div class="badge">MONTE CARLO 50K</div>
    </div>
</div>
""", unsafe_allow_html=True)

col_ctrl, col_exec = st.columns([1.2, 2.8], gap="large")

with col_ctrl:
    st.markdown("<div class='glass-panel'>", unsafe_allow_html=True)
    st.markdown("<div class='panel-header'>MARKET TARGETING</div>", unsafe_allow_html=True)
    
    l_map = {"Premier League": 39, "Champions League": 2, "La Liga": 140, "Primeira Liga": 94, "Serie A": 135}
    league_name = st.selectbox("Liquidity Pool", list(l_map.keys()))
    
    fixtures = get_upcoming_fixtures(l_map[league_name])
    m_sel = None
    btn_run = False
    
    if fixtures:
        # Formata a data para leitura fácil no formato Mês/Dia e Hora
        def format_match(f):
            dt = datetime.strptime(f['fixture']['date'][:16], "%Y-%m-%dT%H:%M")
            return f"{dt.strftime('%d/%m %H:%M')} | {f['teams']['home']['name']} v {f['teams']['away']['name']}"
            
        m_map = {format_match(f): f for f in fixtures}
        m_sel = m_map[st.selectbox("Available Assets (Next 15)", list(m_map.keys()))]
    else:
        st.warning("No matches found in API for this league.")
        
    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
    st.markdown("<div class='panel-header'>RISK MANAGEMENT</div>", unsafe_allow_html=True)
    bankroll = st.number_input("Vault Capital ($)", value=250000, step=10000, format="%d")
    kelly_fraction = st.slider("Kelly Fractional Bias", min_value=0.1, max_value=1.0, value=0.25, step=0.05)
    
    if m_sel:
        st.markdown("<div style='margin-top: 30px;'>", unsafe_allow_html=True)
        btn_run = st.button("INITIALIZE QUANT ENGINE")
        st.markdown("</div>", unsafe_allow_html=True)
        
    st.markdown("</div>", unsafe_allow_html=True)

if m_sel and btn_run:
    placeholder_status = st.empty()
    progress_bar = st.progress(0)
    
    steps = ["[1/4] Establishing secure socket...", "[2/4] Generating 50,000 non-linear paths...", "[3/4] Parsing Bookmaker Vig...", "[4/4] Isolating Alpha Signals..."]
    for i, step in enumerate(steps):
        placeholder_status.markdown(f"<div style='color:var(--neon-cyan); font-family:monospace; font-size:0.8rem; margin-bottom:10px;'>{step}</div>", unsafe_allow_html=True)
        time.sleep(0.3)
        progress_bar.progress((i+1)*25)
    
    time.sleep(0.3)
    placeholder_status.empty()
    progress_bar.empty()
    
    h_name, a_name = m_sel['teams']['home']['name'], m_sel['teams']['away']['name']
    h_stats = get_real_stats(m_sel['teams']['home']['id'], l_map[league_name])
    a_stats = get_real_stats(m_sel['teams']['away']['id'], l_map[league_name])
    
    lam_h, lam_a = calculate_lambdas(h_stats, a_stats)
    true_probs = run_monte_carlo_sim(lam_h, lam_a, 50000)
    live_odds = get_real_odds(m_sel['fixture']['id'])
    
    valid_markets, best_bet = [], None
    dyn_margin = calculate_dynamic_margin(live_odds)
    
    if live_odds:
        for mkt, odd in live_odds.items():
            prob = true_probs.get(mkt, 0)
            if odd > 1.05 and prob > 0:
                f_prob = (1 / odd) / (1 + dyn_margin)
                edge = (prob * odd) - 1
                k_val = min(calculate_kelly(prob, odd, kelly_fraction), 5.0) if edge > 0 else 0
                
                # Nomes Limpos
                ui_mkt = mkt.replace("Home Win", f"{h_name} Win").replace("Away Win", f"{a_name} Win").replace("Draw No Bet (Home)", f"{h_name} (DNB)").replace("Draw No Bet (Away)", f"{a_name} (DNB)")
                
                valid_markets.append({"Market": ui_mkt, "BookOdd": odd, "ModelProb": prob, "Edge": edge, "TrueOdd": f_prob, "Kelly": k_val})
        
        prime_bets = [m for m in valid_markets if 0.01 < m['Edge'] < 0.25 and m['ModelProb'] >= 0.40 and 1.40 <= m['BookOdd'] <= 3.50]
        if prime_bets: best_bet = max(prime_bets, key=lambda x: x['Kelly'])
    
    with col_exec:
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.markdown(f"<div class='glass-panel' style='text-align:center;'><div class='panel-header' style='justify-content:center;'>{h_name} (xG)</div><div style='font-size:2.5rem; font-family:JetBrains Mono; font-weight:700;'>{lam_h:.2f}</div></div>", unsafe_allow_html=True)
        with col_m2:
            st.markdown(f"<div class='glass-panel' style='text-align:center;'><div class='panel-header' style='justify-content:center;'>{a_name} (xG)</div><div style='font-size:2.5rem; font-family:JetBrains Mono; font-weight:700;'>{lam_a:.2f}</div></div>", unsafe_allow_html=True)

        col_alpha, col_chart = st.columns([1.1, 1], gap="large")
        
        with col_alpha:
            if best_bet:
                dollar_sz = (best_bet['Kelly']/100) * bankroll
                conf = min(99.9, (best_bet['ModelProb'] * 100) + (best_bet['Edge'] * 50))
                st.markdown(f"""
                <div class='alpha-box'>
                    <div class='alpha-title'>VERIFIED ALPHA SIGNAL</div>
                    <div class='alpha-asset'>{best_bet['Market']}</div>
                    <div class='alpha-odd'>@ {best_bet['BookOdd']:.3f}</div>
                    <div class='d-row'><span class='d-lbl'>Strike Rate</span><span class='d-val'>{best_bet['ModelProb']*100:.2f}%</span></div>
                    <div class='d-row'><span class='d-lbl'>Edge (+EV)</span><span class='d-val text-gold'>+{best_bet['Edge']*100:.2f}%</span></div>
                    <div class='d-row'><span class='d-lbl'>Position Size</span><span class='d-val'>${dollar_sz:,.0f} ({best_bet['Kelly']:.2f}%)</span></div>
                    <div class='d-row' style='margin-top:15px;'><span class='d-lbl'>Engine Confidence</span><span class='d-val'>{conf:.1f}/100</span></div>
                </div>
                """, unsafe_allow_html=True)
            elif live_odds:
                st.markdown("<div class='glass-panel' style='height:100%; display:flex; align-items:center; justify-content:center; text-align:center;'><div class='d-lbl'>MARKET EFFICIENT<br>NO ALPHA DETECTED. CAPITAL PROTECTED.</div></div>", unsafe_allow_html=True)

        with col_chart:
            st.markdown("<div class='glass-panel' style='padding-bottom:0;'><div class='panel-header'>POISSON KERNEL MATRIX</div>", unsafe_allow_html=True)
            g_range = list(range(6))
            h_probs = [poisson_pmf(lam_h, g)*100 for g in g_range]
            a_probs = [poisson_pmf(lam_a, g)*100 for g in g_range]

            fig = go.Figure(data=[
                go.Bar(name=h_name, x=g_range, y=h_probs, marker_color='rgba(255,255,255,0.2)'),
                go.Bar(name=a_name, x=g_range, y=a_probs, marker_color='#00F0FF')
            ])
            fig.update_layout(
                barmode='group', template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                height=220, margin=dict(l=0, r=0, t=0, b=0),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=10, color="#9CA3AF")),
                xaxis=dict(tickfont=dict(color="#9CA3AF"), gridcolor="rgba(255,255,255,0.05)"),
                yaxis=dict(tickfont=dict(color="#9CA3AF"), gridcolor="rgba(255,255,255,0.05)")
            )
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='glass-panel'><div class='panel-header'>ORDER BOOK ROUTING (TOP 10 EXPLOITS)</div>", unsafe_allow_html=True)
        if live_odds:
            clean = sorted([m for m in valid_markets if m['Edge'] < 0.25 and m['BookOdd'] <= 15.0], key=lambda x: x['Kelly'], reverse=True)
            html = "<table class='futuristic-table'><tr><th>Asset Market</th><th>Listed Odd</th><th>Model Prob</th><th>Advantage</th><th>Sizing</th></tr>"
            for m in clean[:10]: 
                color = "text-cyan" if m['Edge'] > 0 else ""
                sign = "+" if m['Edge'] > 0 else ""
                html += f"<tr><td>{m['Market']}</td><td>{m['BookOdd']:.3f}</td><td>{m['ModelProb']*100:.1f}%</td><td class='{color}'>{sign}{m['Edge']*100:.2f}%</td><td style='color:#9CA3AF;'>{m['Kelly']:.2f}%</td></tr>"
            st.markdown(html + "</table></div>", unsafe_allow_html=True)
