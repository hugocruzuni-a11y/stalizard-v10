import streamlit as st
import numpy as np
import pandas as pd
import requests
from datetime import date
import time

# ==========================================
# 1. INSTITUTIONAL UX SETUP (READABLE)
# ==========================================
st.set_page_config(page_title="APEX QUANT TERMINAL", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700;800&family=Inter:wght@400;600;800&display=swap');

.stApp { background-color: #050505; color: #E0E0E0; font-family: 'Inter', sans-serif; }
header, footer { visibility: hidden; }

/* Top Nav */
.top-nav { background: #000000; border-bottom: 1px solid #1E293B; padding: 12px 25px; display: flex; justify-content: space-between; align-items: center; margin: -3rem -3rem 1.5rem -3rem; position: sticky; top: 0; z-index: 1000;}
.logo { font-size: 1.4rem; font-weight: 800; color: #FFFFFF; font-family: 'JetBrains Mono', monospace; }
.logo span { color: #10B981; }
.sys-status { font-size: 0.75rem; font-weight: 600; color: #10B981; font-family: 'JetBrains Mono', monospace;}

/* Grid Panels */
.grid-panel { border: 1px solid #1E293B; background: #0B0F19; padding: 20px; margin-bottom: 15px; border-radius: 4px; }
.panel-title { font-size: 0.75rem; color: #94A3B8; text-transform: uppercase; border-bottom: 1px solid #1E293B; padding-bottom: 8px; margin-bottom: 12px; font-weight: 800; letter-spacing: 1px; }

/* Metrics */
.data-row { display: flex; justify-content: space-between; font-size: 0.85rem; margin-bottom: 6px; }
.data-lbl { color: #94A3B8; font-weight: 600; }
.data-val { color: #F8FAFC; font-weight: 800; font-family: 'JetBrains Mono', monospace; }
.hl-green { color: #10B981; }
.hl-red { color: #EF4444; }
.hl-blue { color: #38BDF8; }
.hl-warn { color: #F59E0B; }

/* Order Book Table */
.ob-table { width: 100%; font-size: 0.8rem; border-collapse: collapse; font-family: 'JetBrains Mono', monospace; }
.ob-table th { color: #64748B; text-align: right; font-weight: 700; border-bottom: 2px solid #1E293B; padding: 8px 0; font-family: 'Inter', sans-serif; font-size: 0.7rem; text-transform: uppercase; }
.ob-table th:first-child { text-align: left; }
.ob-table td { text-align: right; padding: 10px 0; border-bottom: 1px solid #0F172A; }
.ob-table td:first-child { text-align: left; color: #F8FAFC; font-weight: 700; font-family: 'Inter', sans-serif; }
.ob-table tr:hover { background: #0F172A; }

/* Alpha Box */
.trade-signal { border: 1px solid #10B981; background: rgba(16, 185, 129, 0.05); padding: 20px; margin-top: 15px; border-radius: 4px; }
.trade-asset { font-size: 1.8rem; color: #10B981; font-weight: 800; margin-bottom: 15px; }

/* Override Widgets */
div[data-baseweb="select"] > div { background-color: #0B0F19 !important; border: 1px solid #1E293B !important; color: #F8FAFC !important; }
div[data-baseweb="input"] > div { background-color: #0B0F19 !important; border: 1px solid #1E293B !important; color: #F8FAFC !important; }
.stButton > button { background: #1E293B !important; color: #F8FAFC !important; border: 1px solid #334155 !important; font-weight: 800 !important; width: 100%; transition: all 0.2s; }
.stButton > button:hover { background: #10B981 !important; color: #000 !important; border-color: #10B981 !important; }

/* Insights Manual */
.manual-box { font-size: 0.75rem; color: #94A3B8; border-left: 2px solid #38BDF8; padding-left: 12px; margin-top: 10px; line-height: 1.5; }
.manual-term { color: #38BDF8; font-weight: 800; display: block; margin-top: 10px; text-transform: uppercase; }
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
            # Nomes de mercado limpos e legíveis
            if name == 'Match Winner':
                if 'Home' in vals: market_odds["Home Win"] = vals['Home']
                if 'Draw' in vals: market_odds["Draw"] = vals['Draw']
                if 'Away' in vals: market_odds["Away Win"] = vals['Away']
            elif name == 'Goals Over/Under':
                if 'Over 2.5' in vals: market_odds["Over 2.5 Goals"] = vals['Over 2.5']
                if 'Under 2.5' in vals: market_odds["Under 2.5 Goals"] = vals['Under 2.5']
            elif name == 'Both Teams Score':
                if 'Yes' in vals: market_odds["Both Teams to Score (Yes)"] = vals['Yes']
                if 'No' in vals: market_odds["Both Teams to Score (No)"] = vals['No']
            elif name == 'Asian Handicap':
                for k, odd in vals.items():
                    if "-0.5" in k and "Home" in k: market_odds["Asian Handicap -0.5"] = odd
                    if "+0.5" in k and "Home" in k: market_odds["Asian Handicap +0.5"] = odd
    except: pass 
    return market_odds

def calculate_lambdas(h_stats, a_stats):
    # Aplicação de Home Field Advantage Factor (HFA) de 10% na Força do Mandante
    hfa_multiplier = 1.10 
    lam_h = round(max(0.1, (h_stats['gf_h']/1.55 * hfa_multiplier) * (a_stats['ga_a']/1.55) * 1.55), 3)
    lam_a = round(max(0.1, (a_stats['gf_a']/1.25) * (h_stats['ga_h']/1.25) * 1.25), 3)
    return lam_h, lam_a

def run_monte_carlo_sim(lam_h, lam_a, sims=50000):
    np.random.seed(int(time.time()))
    h_goals, a_goals = np.random.poisson(lam_h, sims), np.random.poisson(lam_a, sims)
    
    # Dixon-Coles
    for i in range(sims):
        if h_goals[i] == 1 and a_goals[i] == 0 and np.random.random() < 0.05: a_goals[i] = 1
        elif h_goals[i] == 0 and a_goals[i] == 1 and np.random.random() < 0.05: h_goals[i] = 1
            
    diff, total = h_goals - a_goals, h_goals + a_goals
    hw, dr, aw = np.sum(diff > 0)/sims, np.sum(diff == 0)/sims, np.sum(diff < 0)/sims
    
    # Mapeamento usando os nomes legíveis
    return {
        "Home Win": hw, "Draw": dr, "Away Win": aw,
        "Asian Handicap -0.5": hw, "Asian Handicap +0.5": hw + dr,
        "Over 2.5 Goals": np.sum(total > 2.5)/sims, "Under 2.5 Goals": np.sum(total < 2.5)/sims,
        "Both Teams to Score (Yes)": np.sum((h_goals > 0) & (a_goals > 0))/sims, 
        "Both Teams to Score (No)": np.sum((h_goals == 0) | (a_goals == 0))/sims
    }

def calculate_dynamic_margin(odds):
    """Calcula a margem exata da casa de apostas baseada no mercado 1X2"""
    try:
        hw, dr, aw = odds.get("Home Win", 0), odds.get("Draw", 0), odds.get("Away Win", 0)
        if hw > 0 and dr > 0 and aw > 0:
            implied_sum = (1/hw) + (1/dr) + (1/aw)
            return max(0.01, implied_sum - 1)
    except: pass
    return 0.045 # Margem fallback

def calculate_kelly(prob, odd, fraction=0.25):
    b = odd - 1
    q = 1 - prob
    return max(0, (((b * prob) - q) / b) * fraction * 100)

# ==========================================
# 3. INTERFACE (READABLE & PROFESSIONAL)
# ==========================================
st.markdown("""
<div class="top-nav">
<div>APEX <span>QUANT</span></div>
<div class="sys-status">● LIVE DATA FEED CONNECTED</div>
</div>
""", unsafe_allow_html=True)

col_ctrl, col_exec = st.columns([1, 2.5], gap="large")

with col_ctrl:
    st.markdown("""
<div class='grid-panel'>
<div class='panel-title'>Model Setup</div>
""", unsafe_allow_html=True)
    
    target_date = st.date_input("Match Date", date.today())
    l_map = {"Premier League": 39, "Champions League": 2, "La Liga": 140, "Primeira Liga": 94, "Serie A": 135}
    league_name = st.selectbox("Select League", list(l_map.keys()))
    bankroll = st.number_input("Total Bankroll ($)", value=100000, step=10000)
    
    fixtures = get_live_fixtures(target_date.strftime('%Y-%m-%d'), l_map[league_name])
    m_sel = None
    if fixtures:
        m_map = {f"{f['teams']['home']['name']} v {f['teams']['away']['name']}": f for f in fixtures}
        m_sel = m_map[st.selectbox("Select Fixture", list(m_map.keys()))]
        btn_run = st.button("Calculate Market Edge")
    else:
        st.markdown("""
<div style='color:#EF4444; font-size:0.8rem; font-weight:600;'>No fixtures found for this date.</div>
""", unsafe_allow_html=True)
        
    st.markdown("""
</div>
""", unsafe_allow_html=True)
    
    st.markdown("""
<div class='grid-panel'>
<div class='panel-title'>Quant Insights (Manual)</div>
<div class='manual-box'>
<span class='manual-term'>Dynamic De-Vigging</span>
O modelo analisa o Overround (margem de lucro) exato que a casa está a aplicar ao jogo atual e remove-o matematicamente para encontrar a probabilidade real (True Odds).
<span class='manual-term'>Poisson Distribution (λ)</span>
A expectativa matemática de golos. O modelo cruza a força de ataque com a fraqueza defensiva e adiciona um multiplicador de 10% (Home Field Advantage).
<span class='manual-term'>Expected Value (+EV)</span>
Indica a margem de lucro teórico a longo prazo, cruzando as True Odds do modelo com a linha de pagamento da casa de apostas.
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
    dynamic_margin = calculate_dynamic_margin(live_odds)
    
    if live_odds:
        for mkt, odd in live_odds.items():
            prob = true_probs.get(mkt, 0)
            if odd > 1.05 and prob > 0:
                f_prob = (1 / odd) / (1 + dynamic_margin)
                edge = (prob * odd) - 1
                valid_markets.append({"Market": mkt, "BookOdd": odd, "ModelProb": prob, "Edge": edge, "TrueOdd": f_prob})
                if edge > max_edge:
                    max_edge, best_bet = edge, valid_markets[-1]
    
    with col_exec:
        col_m1, col_m2 = st.columns([1, 1])
        with col_m1:
            st.markdown(f"""
<div class='grid-panel'>
<div class='panel-title'>Poisson Distribution Metrics</div>
<div class='data-row'><span class='data-lbl'>Home Exp. Goals (λ)</span><span class='data-val hl-blue'>{lam_h:.3f}</span></div>
<div class='data-row'><span class='data-lbl'>Away Exp. Goals (λ)</span><span class='data-val hl-blue'>{lam_a:.3f}</span></div>
<div class='data-row'><span class='data-lbl'>Monte Carlo Iterations</span><span class='data-val'>50,000</span></div>
<div class='data-row'><span class='data-lbl'>Detected Market Margin</span><span class='data-val hl-warn'>{dynamic_margin*100:.2f}%</span></div>
</div>
""", unsafe_allow_html=True)
            
        with col_m2:
            if best_bet and best_bet["Edge"] > 0:
                rec_kelly = calculate_kelly(best_bet['ModelProb'], best_bet['BookOdd'])
                dollar_sz = (rec_kelly/100) * bankroll
                
                # Anomaly Alert para Edges absurdos
                warning_html = ""
                if best_bet["Edge"] > 0.30:
                    warning_html = "<div style='color: #F59E0B; font-size: 0.75rem; margin-top: 15px; text-align: center; border: 1px dashed #F59E0B; padding: 5px;'>⚠️ MARKET ANOMALY: Edge > 30%. Verify late injuries or line-up changes before execution.</div>"

                st.markdown(f"""
<div class='trade-signal'>
<div class='panel-title' style='color:#10B981; border-color:#10B981;'>Highest Expected Value (+EV)</div>
<div class='trade-asset'>{best_bet['Market']} @ {best_bet['BookOdd']:.3f}</div>
<div class='data-row'><span class='data-lbl'>Model Probability</span><span class='data-val'>{best_bet['ModelProb']*100:.2f}%</span></div>
<div class='data-row'><span class='data-lbl'>Expected Value (Edge)</span><span class='data-val hl-green'>+{best_bet['Edge']*100:.2f}%</span></div>
<div class='data-row'><span class='data-lbl'>Rec. Bankroll Size (1/4 Kelly)</span><span class='data-val hl-blue'>${dollar_sz:,.0f} ({rec_kelly:.2f}%)</span></div>
{warning_html}
</div>
""", unsafe_allow_html=True)
            elif live_odds:
                st.markdown("""
<div class='grid-panel'><div class='data-val hl-red'>Efficient Market Detected. Pass.</div></div>
""", unsafe_allow_html=True)

        st.markdown("""
<div class='grid-panel'>
<div class='panel-title'>Algorithmic Order Book</div>
""", unsafe_allow_html=True)
        
        if live_odds:
            valid_markets = sorted(valid_markets, key=lambda x: x['Edge'], reverse=True)
            
            table_html = "<table class='ob-table'><tr><th>Market</th><th>Book Odds</th><th>True Odds (No-Vig)</th><th>Model Prob</th><th>Edge (+EV)</th></tr>"
            
            for m in valid_markets:
                edge_val = m['Edge'] * 100
                color_cls = "hl-green" if edge_val > 0 else "hl-red"
                sign = "+" if edge_val > 0 else ""
                
                row = f"<tr><td>{m['Market']}</td><td>{m['BookOdd']:.3f}</td>"
                row += f"<td>{m['TrueOdd']*100:.1f}%</td><td>{m['ModelProb']*100:.1f}%</td>"
                row += f"<td class='{color_cls}'>{sign}{edge_val:.2f}%</td></tr>"
                
                table_html += row
                
            table_html += "</table>"
            
            st.markdown(table_html, unsafe_allow_html=True)
        else:
            st.markdown("""
<div class='data-lbl'>Waiting for market liquidity...</div>
""", unsafe_allow_html=True)
            
        st.markdown("""
</div>
""", unsafe_allow_html=True)
