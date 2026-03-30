import streamlit as st
import numpy as np
import pandas as pd
import requests
from datetime import date
import time

# ==========================================
# 1. HFT TERMINAL SETUP & CYBER STYLING
# ==========================================
st.set_page_config(page_title="APEX QUANT | HFT TERMINAL", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;700;800&display=swap');
    
    .stApp { background-color: #000000; color: #00FF41; font-family: 'JetBrains Mono', monospace; }
    header, footer { visibility: hidden; }
    
    /* Terminal Nav */
    .top-nav { background: #050505; border-bottom: 2px solid #003B00; padding: 15px 40px; display: flex; justify-content: space-between; align-items: center; margin: -3rem -3rem 2rem -3rem; position: sticky; top: 0; z-index: 1000;}
    .logo { font-size: 1.8rem; font-weight: 800; letter-spacing: 2px; color: #FFFFFF; }
    .logo span { color: #00FF41; text-shadow: 0 0 8px #00FF41; }
    
    .sys-status { color: #00FF41; font-size: 0.8rem; letter-spacing: 2px; text-transform: uppercase; animation: blink 2s infinite; }
    @keyframes blink { 0% { opacity: 1; } 50% { opacity: 0.4; } 100% { opacity: 1; } }

    /* Alpha Grid */
    .data-matrix { border: 1px solid #003B00; background: #020402; padding: 20px; box-shadow: inset 0 0 20px rgba(0,255,65,0.05); }
    .neon-text { color: #00FF41; text-shadow: 0 0 5px #00FF41; font-weight: 800; }
    .warning-text { color: #FFB000; text-shadow: 0 0 5px #FFB000; font-weight: 800; }
    .danger-text { color: #FF003C; text-shadow: 0 0 5px #FF003C; font-weight: 800; }
    
    .metric-row { display: flex; justify-content: space-between; border-bottom: 1px dashed #003B00; padding: 8px 0; font-size: 0.85rem; }
    .metric-label { color: #555555; }
    
    /* Order Book Table */
    .ob-header { display: grid; grid-template-columns: 2fr 1fr 1fr 1fr 1fr; border-bottom: 2px solid #00FF41; padding-bottom: 5px; margin-bottom: 10px; font-size: 0.75rem; color: #00FF41; font-weight: 800; }
    .ob-row { display: grid; grid-template-columns: 2fr 1fr 1fr 1fr 1fr; border-bottom: 1px solid #111; padding: 8px 0; font-size: 0.85rem; transition: background 0.1s; }
    .ob-row:hover { background: rgba(0, 255, 65, 0.1); cursor: crosshair; }
    
    /* Alpha Alert Box */
    .alpha-box { border: 2px solid #00FF41; background: rgba(0, 255, 65, 0.05); padding: 20px; margin: 20px 0; text-align: center; box-shadow: 0 0 30px rgba(0, 255, 65, 0.2); position: relative; }
    .alpha-box::before { content: '[ EXECUTION TARGET ACQUIRED ]'; position: absolute; top: -10px; left: 20px; background: #000; padding: 0 10px; font-size: 0.7rem; color: #00FF41; }
    
    /* Buttons */
    .stButton > button { background: #00FF41 !important; color: #000 !important; border: none !important; border-radius: 0 !important; font-family: 'JetBrains Mono' !important; font-weight: 800 !important; text-transform: uppercase; box-shadow: 0 0 10px rgba(0, 255, 65, 0.4); }
    .stButton > button:hover { background: #FFF !important; box-shadow: 0 0 20px rgba(255, 255, 255, 0.8); }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. DATA ENGINE & ADVANCED MATH
# ==========================================
# A tua chave protegida com fallback para a apresentação
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
    if odds_data and odds_data[0].get('bookmakers'):
        for bet in odds_data[0]['bookmakers'][0].get('bets', []):
            name = bet['name']
            vals = {str(v['value']): float(v['odd']) for v in bet['values']}
            if name == 'Match Winner':
                market_odds["Home Win"], market_odds["Draw"], market_odds["Away Win"] = vals.get('Home', 0), vals.get('Draw', 0), vals.get('Away', 0)
            elif name == 'Goals Over/Under':
                market_odds["Over 2.5"], market_odds["Under 2.5"] = vals.get('Over 2.5', 0), vals.get('Under 2.5', 0)
            elif name == 'Both Teams Score':
                market_odds["BTTS - Yes"], market_odds["BTTS - No"] = vals.get('Yes', 0), vals.get('No', 0)
    return market_odds

def calculate_projected_goals(h_stats, a_stats):
    h_attack, a_defense = h_stats['gf_h'] / 1.55, a_stats['ga_a'] / 1.55
    a_attack, h_defense = a_stats['gf_a'] / 1.25, h_stats['ga_h'] / 1.25
    return round(max(0.1, h_attack * a_defense * 1.55), 2), round(max(0.1, a_attack * h_defense * 1.25), 2)

def run_monte_carlo_sim(proj_h, proj_a, sims=25000):
    np.random.seed(int(time.time()))
    h_goals, a_goals = np.random.poisson(proj_h, sims), np.random.poisson(proj_a, sims)
    
    # Bivariate Correction (Dixon-Coles)
    for i in range(sims):
        if h_goals[i] == 1 and a_goals[i] == 0 and np.random.random() < 0.06: a_goals[i] = 1
        elif h_goals[i] == 0 and a_goals[i] == 1 and np.random.random() < 0.06: h_goals[i] = 1
            
    diff, total = h_goals - a_goals, h_goals + a_goals
    hw, dr, aw = np.sum(diff > 0)/sims, np.sum(diff == 0)/sims, np.sum(diff < 0)/sims
    return {
        "Home Win": hw, "Draw": dr, "Away Win": aw,
        "Over 2.5": np.sum(total > 2.5)/sims, "Under 2.5": np.sum(total < 2.5)/sims,
        "BTTS - Yes": np.sum((h_goals > 0) & (a_goals > 0))/sims, "BTTS - No": np.sum((h_goals == 0) | (a_goals == 0))/sims
    }

def calculate_kelly(prob, odd, fraction=0.25):
    b = odd - 1
    q = 1 - prob
    kelly_pct = ((b * prob) - q) / b
    return max(0, kelly_pct) * fraction * 100

def get_market_vig(odds, mkt_type):
    """Calcula e remove a margem (VIG) para descobrir a probabilidade real do Mercado."""
    try:
        if mkt_type == "1X2":
            implied_sum = (1/odds["Home Win"]) + (1/odds["Draw"]) + (1/odds["Away Win"])
            return implied_sum - 1
        elif mkt_type == "OU":
            implied_sum = (1/odds["Over 2.5"]) + (1/odds["Under 2.5"])
            return implied_sum - 1
    except: return 0.05
    return 0.05

# ==========================================
# 3. HFT TERMINAL UI
# ==========================================
st.markdown("""
<div class="top-nav">
    <div class="logo">APEX<span>QUANT</span> // SYS_CORE</div>
    <div class="sys-status">● HFT FEED ACTIVE // DE-VIG ALGO RUNNING</div>
</div>
""", unsafe_allow_html=True)

col_cmd, col_data, col_book = st.columns([1, 1.8, 2.2], gap="large")

with col_cmd:
    st.markdown("<div style='color:#555; font-size:0.7rem; margin-bottom:10px;'>[ SYS_INPUT_MODULE ]</div>", unsafe_allow_html=True)
    target_date = st.date_input("TARGET_DATE", date.today())
    l_map = {"ENG_PREMIER": 39, "EUR_CHAMPIONS": 2, "ESP_LIGA": 140, "POR_PRIMEIRA": 94, "ITA_SERIE_A": 135}
    league_name = st.selectbox("TARGET_EXCHANGE", list(l_map.keys()))
    
    with st.spinner("FETCHING LIQUIDITY..."):
        fixtures = get_live_fixtures(target_date.strftime('%Y-%m-%d'), l_map[league_name])
    
    m_sel = None
    if fixtures:
        m_map = {f"{f['teams']['home']['name'].upper()} // {f['teams']['away']['name'].upper()}": f for f in fixtures}
        m_sel = m_map[st.selectbox("SELECT_ASSET", list(m_map.keys()))]
        st.button("EXEC_QUANT_MODEL()", use_container_width=True)

if m_sel:
    h_id, a_id = m_sel['teams']['home']['id'], m_sel['teams']['away']['id']
    with st.spinner("CALCULATING POISSON DEVIANCE & NO-VIG PROBS..."):
        h_stats, a_stats = get_real_stats(h_id, l_map[league_name]), get_real_stats(a_id, l_map[league_name])
        proj_h, proj_a = calculate_projected_goals(h_stats, a_stats)
        true_probs = run_monte_carlo_sim(proj_h, proj_a, 25000)
        live_odds = get_real_odds(m_sel['fixture']['id'])
    
    # Process Market Data
    valid_markets = []
    best_bet, max_edge = None, 0
    vig_1x2 = get_market_vig(live_odds, "1X2") if live_odds else 0.05
    
    if live_odds:
        for mkt, odd in live_odds.items():
            prob = true_probs.get(mkt, 0)
            if odd > 1.05 and prob > 0:
                # Remove o Vig para calcular a Fair Odd do Mercado
                market_implied = 1 / odd
                market_fair_prob = market_implied / (1 + vig_1x2)
                
                edge = (prob * odd) - 1
                valid_markets.append({
                    "Market": mkt, "Odd": odd, "TrueProb": prob, "Edge": edge, 
                    "MarketFairProb": market_fair_prob, "Vig": vig_1x2
                })
                if edge > max_edge:
                    max_edge, best_bet = edge, valid_markets[-1]
    
    with col_data:
        # ATENÇÃO: Código HTML colado à esquerda para evitar a caixa branca do Markdown
        st.markdown(f"""
<div class="data-matrix">
    <div style="font-size: 0.7rem; color: #555; margin-bottom: 15px;">// ASSET_METADATA_STREAM</div>
    <div style="font-size: 1.5rem; color: #FFF; font-weight: 800; margin-bottom: 5px;">{m_sel['teams']['home']['name'].upper()}</div>
    <div style="font-size: 1.5rem; color: #FFF; font-weight: 800; margin-bottom: 20px;">{m_sel['teams']['away']['name'].upper()}</div>
    
    <div class="metric-row"><span class="metric-label">SYS.XG_PROXY_HOME :</span><span class="neon-text">{proj_h:.3f}</span></div>
    <div class="metric-row"><span class="metric-label">SYS.XG_PROXY_AWAY :</span><span class="neon-text">{proj_a:.3f}</span></div>
    <div class="metric-row"><span class="metric-label">POISSON_SIM_PATHS :</span><span class="neon-text">25,000</span></div>
    <div class="metric-row"><span class="metric-label">MARKET_VIG_DETECT :</span><span class="warning-text">{(vig_1x2*100):.2f}%</span></div>
    <div class="metric-row"><span class="metric-label">ALPHA_CORRELATION :</span><span class="neon-text">ACTIVE</span></div>
</div>
""", unsafe_allow_html=True)

        if best_bet and best_bet["Edge"] > 0:
            rec_kelly = calculate_kelly(best_bet['TrueProb'], best_bet['Odd'])
            # ATENÇÃO: HTML colado à esquerda novamente
            st.markdown(f"""
<div class="alpha-box">
    <div style="font-size: 2.5rem; font-weight: 800; color: #00FF41; margin-bottom: 10px;">{best_bet['Market'].upper()}</div>
    <div style="display: flex; justify-content: space-between; text-align: left; background: #000; padding: 15px; border: 1px solid #003B00;">
        <div>
            <div style="color: #555; font-size: 0.7rem;">BOOK_QUOTE</div>
            <div style="color: #FFF; font-size: 1.2rem; font-weight: 800;">{best_bet['Odd']:.3f}</div>
        </div>
        <div>
            <div style="color: #555; font-size: 0.7rem;">SYS_FAIR_PRICE</div>
            <div style="color: #00FF41; font-size: 1.2rem; font-weight: 800;">{(1/best_bet['TrueProb']):.3f}</div>
        </div>
        <div>
            <div style="color: #555; font-size: 0.7rem;">CALC_EDGE (EV)</div>
            <div style="color: #00FF41; font-size: 1.2rem; font-weight: 800;">+{best_bet['Edge']*100:.2f}%</div>
        </div>
        <div>
            <div style="color: #555; font-size: 0.7rem;">REC_SIZE (¼ KELLY)</div>
            <div style="color: #FFB000; font-size: 1.2rem; font-weight: 800;">{rec_kelly:.2f}%</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)
            if st.button("> INITIATE_TRADE_SEQUENCE()", use_container_width=True):
                st.toast("SYS: Trade payload compiled. Ready for API dispatch.", icon="📟")

    with col_book:
        st.markdown("<div style='color:#555; font-size:0.7rem; margin-bottom:10px;'>[ ALGORITHMIC_ORDER_BOOK ]</div>", unsafe_allow_html=True)
        if live_odds:
            st.markdown("""
            <div class="ob-header">
                <div>MARKET_ID</div>
                <div style="text-align:right;">QUOTE</div>
                <div style="text-align:right;">MKT_NO_VIG</div>
                <div style="text-align:right;">SYS_PROB</div>
                <div style="text-align:right;">ALPHA</div>
            </div>
            <div style="background: #020402; border: 1px solid #003B00; padding: 10px; max-height: 500px; overflow-y: auto;">
            """, unsafe_allow_html=True)
            
            valid_markets = sorted(valid_markets, key=lambda x: x['Edge'], reverse=True)
            for m in valid_markets:
                is_edge = m['Edge'] > 0
                txt_color = "#00FF41" if is_edge else "#FF003C"
                alpha_txt = f"+{m['Edge']*100:.2f}%" if is_edge else f"{m['Edge']*100:.2f}%"
                
                st.markdown(f"""
                <div class="ob-row">
                    <div style="color:#FFF;">{m['Market']}</div>
                    <div style="text-align:right; color:#FFF;">{m['Odd']:.3f}</div>
                    <div style="text-align:right; color:#555;">{m['MarketFairProb']*100:.1f}%</div>
                    <div style="text-align:right; color:#00FF41;">{m['TrueProb']*100:.1f}%</div>
                    <div style="text-align:right; color:{txt_color}; font-weight:800;">{alpha_txt}</div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='danger-text'>ERR: LIQUIDITY_NOT_FOUND // AWAITING_MARKET_MAKERS</div>", unsafe_allow_html=True)
