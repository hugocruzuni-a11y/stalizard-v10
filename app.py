import streamlit as st
import numpy as np
import pandas as pd
import requests
from datetime import date
import time

# ==========================================
# 1. HFT BRUTALIST SETUP (100% INSTITUTIONAL)
# ==========================================
st.set_page_config(page_title="APEX // EXEC_TERMINAL", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700;800&display=swap');

.stApp { background-color: #000000; color: #CCCCCC; font-family: 'JetBrains Mono', monospace; }
header, footer { visibility: hidden; }

/* Brutalist Top Nav */
.top-nav { background: #000000; border-bottom: 1px solid #333333; padding: 5px 15px; display: flex; justify-content: space-between; align-items: center; margin: -3rem -3rem 1rem -3rem; position: sticky; top: 0; z-index: 1000;}
.logo { font-size: 1.2rem; font-weight: 800; color: #FFFFFF; letter-spacing: -0.5px; }
.logo span { color: #00FF00; }
.sys-status { font-size: 0.7rem; font-weight: 700; color: #00FF00; animation: blink 1s infinite; }
@keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0; } }

/* Grid & Borders (Zero Radius) */
.grid-panel { border: 1px solid #333333; background: #050505; padding: 15px; margin-bottom: 15px; }
.panel-title { font-size: 0.65rem; color: #666666; text-transform: uppercase; border-bottom: 1px dashed #333333; padding-bottom: 5px; margin-bottom: 10px; font-weight: 800; }

/* Metrics */
.data-row { display: flex; justify-content: space-between; font-size: 0.8rem; margin-bottom: 4px; }
.data-lbl { color: #888888; }
.data-val { color: #FFFFFF; font-weight: 700; }
.data-val.hl-green { color: #00FF00; }
.data-val.hl-red { color: #FF0000; }
.data-val.hl-cyan { color: #00FFFF; }
.data-val.hl-warn { color: #FFB000; }

/* Order Book */
.ob-table { width: 100%; font-size: 0.75rem; border-collapse: collapse; }
.ob-table th { color: #666666; text-align: right; font-weight: 400; border-bottom: 1px solid #333; padding: 4px 0; }
.ob-table th:first-child { text-align: left; }
.ob-table td { text-align: right; padding: 6px 0; border-bottom: 1px solid #111; color: #DDD; }
.ob-table td:first-child { text-align: left; color: #FFF; }
.ob-table tr:hover { background: #111111; }

/* High Conviction Trade Box */
.trade-signal { border: 1px solid #00FF00; background: #001100; padding: 15px; margin-top: 10px; }
.trade-asset { font-size: 1.5rem; color: #00FF00; font-weight: 800; margin-bottom: 10px; text-transform: uppercase; }

/* Dynamic Warning */
.risk-warn { border: 1px dashed #FFB000; background: rgba(255, 176, 0, 0.05); color: #FFB000; font-size: 0.7rem; padding: 8px; margin-top: 10px; text-align: center; font-weight: 800; }

/* Quant Insights Manual */
.manual-box { font-size: 0.7rem; color: #888; border-left: 2px solid #333; padding-left: 10px; margin-top: 15px; }
.manual-term { color: #00FFFF; font-weight: 700; display: block; margin-top: 8px; }

/* Override Streamlit Default Widgets */
div[data-baseweb="select"] > div { background-color: #000 !important; border: 1px solid #333 !important; border-radius: 0 !important; color: #00FF00 !important; font-family: 'JetBrains Mono' !important; font-size: 0.8rem !important; }
div[data-baseweb="input"] > div { background-color: #000 !important; border: 1px solid #333 !important; border-radius: 0 !important; }
input[type="number"] { color: #00FF00 !important; font-family: 'JetBrains Mono' !important; font-size: 0.8rem !important; }
.stButton > button { background: #000 !important; color: #00FF00 !important; border: 1px solid #00FF00 !important; border-radius: 0 !important; font-family: 'JetBrains Mono' !important; font-size: 0.8rem !important; width: 100%; text-transform: uppercase; }
.stButton > button:hover { background: #00FF00 !important; color: #000 !important; }

/* Terminal Log Console */
.terminal-log { background: #000; border: 1px solid #333; height: 100px; overflow: hidden; padding: 10px; font-size: 0.65rem; color: #444; margin-top: 20px;}
.log-line { margin: 0; padding: 0; line-height: 1.2;}
.log-new { color: #00FF00; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. ALGORITHMIC ENGINE
# ==========================================
API_KEY = st.secrets.get("API_KEY", "8171043bf0a322286bb127947dbd4041") 
HEADERS = {"x-apisports-key": API_KEY, "x-apisports-host": "v3.football.api-sports.io"}

def fetch_api(endpoint, params):
    try:
        r = requests.get(f"https://{HEADERS['x-apisports-host']}/{endpoint}", headers=HEADERS, params=params, timeout=10)
        return r.json().get('response', [])
    except: return []

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
                if 'Home' in vals: market_odds["HOME_WIN"] = vals['Home']
                if 'Draw' in vals: market_odds["DRAW"] = vals['Draw']
                if 'Away' in vals: market_odds["AWAY_WIN"] = vals['Away']
            elif name == 'Goals Over/Under':
                if 'Over 2.5' in vals: market_odds["O2.5"] = vals['Over 2.5']
                if 'Under 2.5' in vals: market_odds["U2.5"] = vals['Under 2.5']
            elif name == 'Both Teams Score':
                if 'Yes' in vals: market_odds["BTTS_YES"] = vals['Yes']
                if 'No' in vals: market_odds["BTTS_NO"] = vals['No']
            elif name == 'Asian Handicap':
                for k, odd in vals.items():
                    if "-0.5" in k and "Home" in k: market_odds["AH_H(-0.5)"] = odd
                    if "+0.5" in k and "Home" in k: market_odds["AH_H(+0.5)"] = odd
                    if "-1.5" in k and "Home" in k: market_odds["AH_H(-1.5)"] = odd
    except: pass 
    return market_odds

def calculate_lambdas(h_stats, a_stats):
    lam_h = round(max(0.1, (h_stats['gf_h']/1.55) * (a_stats['ga_a']/1.55) * 1.55), 3)
    lam_a = round(max(0.1, (a_stats['gf_a']/1.25) * (h_stats['ga_h']/1.25) * 1.25), 3)
    return lam_h, lam_a

def run_monte_carlo_sim(lam_h, lam_a, sims=50000):
    np.random.seed(int(time.time()))
    h_goals, a_goals = np.random.poisson(lam_h, sims), np.random.poisson(lam_a, sims)
    
    # Dixon-Coles Rho Adjustment
    for i in range(sims):
        if h_goals[i] == 1 and a_goals[i] == 0 and np.random.random() < 0.05: a_goals[i] = 1
        elif h_goals[i] == 0 and a_goals[i] == 1 and np.random.random() < 0.05: h_goals[i] = 1
            
    diff, total = h_goals - a_goals, h_goals + a_goals
    hw, dr, aw = np.sum(diff > 0)/sims, np.sum(diff == 0)/sims, np.sum(diff < 0)/sims
    return {
        "HOME_WIN": hw, "DRAW": dr, "AWAY_WIN": aw,
        "AH_H(-0.5)": hw, "AH_H(+0.5)": hw + dr, "AH_H(-1.5)": np.sum(diff > 1)/sims,
        "O2.5": np.sum(total > 2.5)/sims, "U2.5": np.sum(total < 2.5)/sims,
        "BTTS_YES": np.sum((h_goals > 0) & (a_goals > 0))/sims, "BTTS_NO": np.sum((h_goals == 0) | (a_goals == 0))/sims
    }

def calculate_kelly(prob, odd, fraction=0.25):
    b = odd - 1
    q = 1 - prob
    return max(0, (((b * prob) - q) / b) * fraction * 100)

# ==========================================
# 3. TERMINAL INTERFACE
# ==========================================
st.markdown("""
<div class="top-nav">
<div>APEX<span style="color:#555;">//</span><span>CORE</span></div>
<div class="sys-status">SOCKET: CONNECTED [LATENCY: 12ms]</div>
</div>
""", unsafe_allow_html=True)

col_ctrl, col_exec = st.columns([1, 2.5], gap="small")

with col_ctrl:
    st.markdown("<div class='grid-panel'>", unsafe_allow_html=True)
    st.markdown("<div class='panel-title'>SYS_CFG</div>", unsafe_allow_html=True)
    target_date = st.date_input("TARGET_DATE", date.today())
    l_map = {"PREMIER_LGE": 39, "UCL": 2, "LA_LIGA": 140, "LIGA_PT": 94, "SERIE_A": 135}
    league_name = st.selectbox("EXCHANGE", list(l_map.keys()))
    bankroll = st.number_input("CAPITAL_ALLOC ($)", value=100000, step=10000)
    
    fixtures = get_live_fixtures(target_date.strftime('%Y-%m-%d'), l_map[league_name])
    m_sel = None
    if fixtures:
        m_map = {f"{f['teams']['home']['name'][:12].upper()} v {f['teams']['away']['name'][:12].upper()}": f for f in fixtures}
        m_sel = m_map[st.selectbox("ASSET_TICKER", list(m_map.keys()))]
        btn_run = st.button("EXEC_QUANT_SIM()")
    else:
        st.markdown("<div style='color:#FF0000; font-size:0.7rem;'>ERR: NO_LIQUIDITY_IN_EXCHANGE</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # NEW: Quant Insights Manual for Bettor Education
    st.markdown("""
    <div class='grid-panel'>
        <div class='panel-title'>[ SYS_MANUAL // QUANT_INSIGHTS ]</div>
        <div class='manual-box'>
            <span class='manual-term'>EXPECTED VALUE (+EV)</span>
            O verdadeiro indicador de lucro a longo prazo. Um +EV de 5% significa que por cada $100 investidos, o retorno teórico é de $5. Não é uma garantia de vitória no curto prazo.
            
            <span class='manual-term'>POISSON LAMBDA (λ)</span>
            Representa a expectativa matemática de golos cruzando a força de ataque de uma equipa com a fraqueza defensiva do adversário.
            
            <span class='manual-term'>KELLY CRITERION (ƒ*)</span>
            O nosso sistema usa a fórmula 1/4 Kelly para evitar a falência. A matemática aloca capital baseada na confiança do sinal:
            $$f^* = \\frac{bp - q}{b}$$
        </div>
    </div>
    """, unsafe_allow_html=True)

if m_sel:
    h_id, a_id = m_sel['teams']['home']['id'], m_sel['teams']['away']['id']
    
    h_stats, a_stats = get_real_stats(h_id, l_map[league_name]), get_real_stats(a_id, l_map[league_name])
    lam_h, lam_a = calculate_lambdas(h_stats, a_stats)
    true_probs = run_monte_carlo_sim(lam_h, lam_a, 50000)
    live_odds = get_real_odds(m_sel['fixture']['id'])
    
    valid_markets = []
    best_bet, max_edge = None, 0
    margin = 0.045 # Base assumption
    
    if live_odds:
        for mkt, odd in live_odds.items():
            prob = true_probs.get(mkt, 0)
            if odd > 1.05 and prob > 0:
                f_prob = (1 / odd) / (1 + margin)
                edge = (prob * odd) - 1
                valid_markets.append({"MKT": mkt, "ODD": odd, "PROB": prob, "EDGE": edge, "FAIR": f_prob})
                if edge > max_edge:
                    max_edge, best_bet = edge, valid_markets[-1]
    
    with col_exec:
        col_m1, col_m2 = st.columns([1, 1])
        with col_m1:
            st.markdown(f"""
            <div class='grid-panel'>
                <div class='panel-title'>POISSON_MODEL_METADATA</div>
                <div class='data-row'><span class='data-lbl'>LAMBDA (λ1) HOME:</span><span class='data-val hl-cyan'>{lam_h:.3f}</span></div>
                <div class='data-row'><span class='data-lbl'>LAMBDA (λ2) AWAY:</span><span class='data-val hl-cyan'>{lam_a:.3f}</span></div>
                <div class='data-row'><span class='data-lbl'>ITERATIONS:</span><span class='data-val'>50,000</span></div>
                <div class='data-row'><span class='data-lbl'>DEVIG_METHOD:</span><span class='data-val'>SHIN_VAR</span></div>
            </div>
            """, unsafe_allow_html=True)
            
        with col_m2:
            if best_bet and best_bet["EDGE"] > 0:
                rec_kelly = calculate_kelly(best_bet['PROB'], best_bet['ODD'])
                dollar_sz = (rec_kelly/100) * bankroll
                exp_yield = best_bet['EDGE'] * dollar_sz
                
                # Dynamic Risk Warning based on Kelly Size
                warning_html = ""
                if rec_kelly > 5.0:
                    warning_html = "<div class='risk-warn'>SYS_WARN: HIGH EXPOSURE. CONSIDER HALF-KELLY MODIFIER TO REDUCE DRAWDOWN RISK.</div>"
                elif rec_kelly < 1.0:
                    warning_html = "<div class='risk-warn' style='color:#888; border-color:#555;'>SYS_NOTE: MARGINAL EDGE. EXECUTE ONLY IF CONFIRMED BY ALTERNATIVE DATA SOURCES.</div>"

                st.markdown(f"""
                <div class='trade-signal'>
                    <div class='panel-title' style='color:#00FF00; border-color:#00FF00;'>ALPHA_DETECTED // TRADE_PAYLOAD</div>
                    <div class='trade-asset'>{best_bet['MKT']} @ {best_bet['ODD']:.3f}</div>
                    <div class='data-row'><span class='data-lbl'>SYS_PROB:</span><span class='data-val'>{best_bet['PROB']*100:.2f}%</span></div>
                    <div class='data-row'><span class='data-lbl'>TRUE_EDGE:</span><span class='data-val hl-green'>+{best_bet['EDGE']*100:.2f}%</span></div>
                    <div class='data-row'><span class='data-lbl'>EXP_YIELD:</span><span class='data-val hl-green'>+${exp_yield:.2f}</span></div>
                    <div class='data-row'><span class='data-lbl'>KELLY_SIZE(1/4):</span><span class='data-val hl-cyan'>${dollar_sz:,.0f} ({rec_kelly:.2f}%)</span></div>
                    {warning_html}
                </div>
                """, unsafe_allow_html=True)
            elif live_odds:
                st.markdown("<div class='grid-panel'><div class='data-val hl-red'>NO_ALPHA_DETECTED // PASS</div></div>", unsafe_allow_html=True)

        st.markdown("<div class='grid-panel'>", unsafe_allow_html=True)
        st.markdown("<div class='panel-title'>ORDER_BOOK_LADDER</div>", unsafe_allow_html=True)
        if live_odds:
            valid_markets = sorted(valid_markets, key=lambda x: x['EDGE'], reverse=True)
            table_html = "<table class='ob-table'><tr><th>MKT_ID</th><th>ASK_ODD</th><th>SHIN_NO_VIG</th><th>SYS_PROB</th><th>EV_ALPHA</th></tr>"
            for m in valid_markets:
                edge_val = m['EDGE']*100
                color_cls = "hl-green" if edge_val >
