import streamlit as st
import numpy as np
from scipy.stats import poisson
import pandas as pd
import plotly.graph_objects as go
import requests
from datetime import date
import time

# --- 1. CONFIGURAÇÃO INSTITUCIONAL ---
st.set_page_config(
    page_title="STARLINE V140 PRO - SYNDICATE BUILD", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@200;300;400;600;700&display=swap');
    .stApp { background: radial-gradient(circle at 50% -20%, #0f172a 0%, #000000 95%); color: #FFFFFF; font-family: 'Inter', sans-serif; }
    [data-testid="stSidebar"] { background-color: rgba(255, 255, 255, 0.01) !important; backdrop-filter: blur(45px) !important; border-right: 1px solid rgba(255, 255, 255, 0.05) !important; }
    [data-testid="stSidebar"] .stNumberInput input, [data-testid="stSidebar"] .stTextInput input, [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] { background-color: rgba(255, 255, 255, 0.96) !important; border: 1px solid rgba(0, 255, 136, 0.2) !important; color: #000000 !important; font-family: 'Inter', sans-serif !important; font-weight: 300 !important; font-size: 0.85rem !important; border-radius: 4px !important; }
    .advisor-seal { background: linear-gradient(135deg, rgba(0, 255, 136, 0.08) 0%, rgba(255, 255, 255, 0.02) 100%); border-radius: 12px; padding: 15px 25px; border: 1px solid rgba(0, 255, 136, 0.4); margin-bottom: 20px; display: inline-block; }
    .risk-card { background: rgba(255, 255, 255, 0.02); border-radius: 12px; padding: 15px 25px; border: 1px solid rgba(255, 255, 255, 0.1); margin-bottom: 20px; }
    .advisor-title { color: white; font-size: 1.6rem; font-weight: 700; margin: 0; letter-spacing: -1px; }
    .advisor-subtitle { color: #00FF88; font-size: 0.85rem; font-weight: 400; margin: 0; letter-spacing: 1px; }
    .intel-card { background: rgba(255, 255, 255, 0.02); border-radius: 12px; padding: 20px; border: 1px solid rgba(255, 255, 255, 0.05); font-weight: 300; font-size: 0.85rem; margin-bottom: 10px; }
    label { font-size: 0.62rem !important; font-weight: 600 !important; color: #64748B !important; text-transform: uppercase; letter-spacing: 1.2px; }
    div.stButton > button { background: linear-gradient(90deg, #00FF88 0%, #00BD63 100%) !important; color: #000000 !important; font-weight: 700; height: 4em; width: 100%; border-radius: 6px; border: none; text-transform: uppercase; letter-spacing: 2px; box-shadow: 0 10px 25px rgba(0, 255, 136, 0.1); }
    hr { border-top: 1px solid rgba(255, 255, 255, 0.03) !important; margin: 15px 0 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. MOTOR DE API DIRETA ---
api_key = "8171043bf0a322286bb127947dbd4041" 
api_host = "v3.football.api-sports.io" 
headers = {"x-apisports-key": api_key}

@st.cache_data(ttl=3600)
def get_team_stats_cached(team_id, league_id):
    url = f"https://{api_host}/teams/statistics"
    try:
        response = requests.get(url, headers=headers, params={"league": league_id, "season": "2025", "team": team_id})
        goals_stats = response.json().get('response', {}).get('goals', {})
        return {
            "h_for": float(goals_stats.get('for', {}).get('average', {}).get('home', 1.5)),
            "h_aga": float(goals_stats.get('against', {}).get('average', {}).get('home', 1.0)),
            "a_for": float(goals_stats.get('for', {}).get('average', {}).get('away', 1.2)),
            "a_aga": float(goals_stats.get('against', {}).get('average', {}).get('away', 1.3))
        }
    except:
        return {"h_for": 1.5, "h_aga": 1.0, "a_for": 1.2, "a_aga": 1.3}

def get_fixtures_today(league_id):
    url = f"https://{api_host}/fixtures"
    try:
        response = requests.get(url, headers=headers, params={"date": date.today().strftime('%Y-%m-%d'), "league": league_id, "season": "2025"})
        return response.json().get('response', [])
    except:
        return []

def calculate_pro_markets(lh, la, rho, ah_boost):
    """Motor Matemático para Mercados Profissionais"""
    lh_boosted = lh * (1 + ah_boost)
    la_boosted = la * (1 - ah_boost)
    
    max_goals = 10
    prob_matrix = np.outer(poisson.pmf(np.arange(max_goals), lh_boosted), poisson.pmf(np.arange(max_goals), la_boosted))

    # Dixon-Coles Correction
    for x in range(2):
        for y in range(2):
            if x == 0 and y == 0: prob_matrix[x, y] *= max(0, 1 - (lh_boosted * la_boosted * rho))
            elif x == 0 and y == 1: prob_matrix[x, y] *= max(0, 1 + (lh_boosted * rho))
            elif x == 1 and y == 0: prob_matrix[x, y] *= max(0, 1 + (la_boosted * rho))
            elif x == 1 and y == 1: prob_matrix[x, y] *= max(0, 1 - rho)
    prob_matrix /= prob_matrix.sum()
    
    # Match Odds (1X2)
    ph = np.tril(prob_matrix, -1).sum() 
    px = np.trace(prob_matrix)          
    pa = np.triu(prob_matrix, 1).sum()  
    
    # Extração de Diagonais para Handicaps Asiáticos Exatos
    h_win_by_1 = np.trace(prob_matrix, offset=-1)
    a_win_by_1 = np.trace(prob_matrix, offset=1)
    h_win_by_2plus = ph - h_win_by_1
    a_win_by_2plus = pa - a_win_by_1

    # Asian Handicaps - Home
    ah_0_h = ph / (ph + pa) if (ph + pa) > 0 else 0 # DNB
    ah_minus_05_h = ph # Win
    ah_plus_05_h = ph + px # Double Chance
    ah_minus_1_h = h_win_by_2plus / (1 - h_win_by_1) if (1 - h_win_by_1) > 0 else 0 # Refund on exactly 1
    
    # Asian Handicaps - Away
    ah_0_a = pa / (ph + pa) if (ph + pa) > 0 else 0 
    ah_minus_05_a = pa 
    ah_plus_05_a = pa + px 
    ah_minus_1_a = a_win_by_2plus / (1 - a_win_by_1) if (1 - a_win_by_1) > 0 else 0 

    # Asian Goal Lines (Over/Under)
    goals_sum = np.add.outer(np.arange(max_goals), np.arange(max_goals))
    o25_prob = prob_matrix[goals_sum > 2.5].sum()
    u25_prob = prob_matrix[goals_sum < 2.5].sum()
    
    return {
        "1": ph, "X": px, "2": pa,
        "O2.5": o25_prob, "U2.5": u25_prob,
        "AH 0.0 (H)": ah_0_h, "AH -0.5 (H)": ah_minus_05_h, "AH +0.5 (H)": ah_plus_05_h, "AH -1.0 (H)": ah_minus_1_h,
        "AH 0.0 (A)": ah_0_a, "AH -0.5 (A)": ah_minus_05_a, "AH +0.5 (A)": ah_plus_05_a, "AH -1.0 (A)": ah_minus_1_a
    }, prob_matrix

# --- 3. SIDEBAR COCKPIT ---
with st.sidebar:
    st.markdown("<h2 style='color:#00FF88; font-size:22px; font-weight:700;'>🏛️ ORACLE V140 PRO</h2>", unsafe_allow_html=True)
    
    st.markdown("<p style='color:#475569; font-size:0.65rem; font-weight:700;'>01 // BANKROLL MANAGEMENT</p>", unsafe_allow_html=True)
    bankroll = st.number_input("TOTAL BANKROLL (€)", value=100.0, step=10.0, format="%.2f")
    
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<p style='color:#475569; font-size:0.65rem; font-weight:700;'>02 // LIVE API INJECTION</p>", unsafe_allow_html=True)
    league_map = {"Premier League": 39, "La Liga": 140, "Serie A": 135, "Primeira Liga (PT)": 94}
    league_name = st.selectbox("SELECT LEAGUE", list(league_map.keys()))
    fixtures = get_fixtures_today(league_map[league_name])
    match_selected = None
    
    if fixtures:
        match_map = {f"{f['teams']['home']['name']} vs {f['teams']['away']['name']}": f['fixture']['id'] for f in fixtures}
        match_display = st.selectbox("SELECT MATCH", list(match_map.keys()))
        match_selected = next(f for f in fixtures if f['fixture']['id'] == match_map[match_display])

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<p style='color:#475569; font-size:0.65rem; font-weight:700;'>03 // PRO MARKET ODDS (Manual/Fallback)</p>", unsafe_allow_html=True)
    c1, cx, c2 = st.columns(3)
    m1 = c1.number_input("1", value=2.10); mx = cx.number_input("X", value=3.40); m2 = c2.number_input("2", value=3.50)
    
    c3, c4 = st.columns(2)
    ah_minus_05 = c3.number_input("AH -0.5 (H)", value=2.10)
    ah_minus_1 = c4.number_input("AH -1.0 (H)", value=3.20)
    o25 = c3.number_input("O2.5", value=1.90)
    u25 = c4.number_input("U2.5", value=1.90)

    st.markdown("<br>", unsafe_allow_html=True)
    run_scan = st.button("🚀 EXECUTE SYNDICATE SCAN")

# --- 4. RESULTS INTERFACE ---
if not run_scan or not match_selected:
    st.markdown("<div style='text-align:center; padding-top:150px; opacity:0.1;'><h1>ORACLE V140 PRO</h1><p>PRO SYNDICATE BUILD</p></div>", unsafe_allow_html=True)
else:
    with st.spinner('A processar Mercados Asiáticos...'):
        h_id, a_id = match_selected['teams']['home']['id'], match_selected['teams']['away']['id']
        h_n, a_n = match_selected['teams']['home']['name'].upper(), match_selected['teams']['away']['name'].upper()
        
        stats_h = get_team_stats_cached(h_id, league_map[league_name])
        stats_a = get_team_stats_cached(a_id, league_map[league_name])
        
        lh = (stats_h["h_for"] * stats_a["a_aga"]) ** 0.5
        la = (stats_a["a_for"] * stats_h["h_aga"]) ** 0.5

        # Rho a -0.11 e Home Boost a 12% como norma institucional
        probs, prob_matrix = calculate_pro_markets(lh, la, -0.11, 0.12)

    cv = np.sqrt(lh + la) / (lh + la) if (lh + la) > 0 else 1
    conf_score = max(50.0, min(99.9, 100 * (1 - (cv / 2.8))))

    # --- UI RENDER ---
    st.markdown(f"<h1 style='letter-spacing:-3px; font-size:55px; margin:0; font-weight:700;'>{h_n} <span style='color:#00FF88; font-weight:300;'>vs</span> {a_n}</h1>", unsafe_allow_html=True)
    
    col_res, col_risk = st.columns([1.1, 0.9])
    
    mkts = [
        ("WIN: "+h_n, probs["1"], m1), ("WIN: "+a_n, probs["2"], m2), ("DRAW (X)", probs["X"], mx),
        ("AH -0.5: "+h_n, probs["AH -0.5 (H)"], ah_minus_05), 
        ("AH -1.0: "+h_n, probs["AH -1.0 (H)"], ah_minus_1),
        ("O2.5 GOALS", probs["O2.5"], o25), ("U2.5 GOALS", probs["U2.5"], u25)
    ]
    
    valid_mkts = [(n, p, b, (p*b)-1) for n, p, b in mkts if p > 0 and b > 1.01]
    best = sorted(valid_mkts, key=lambda x: x[3], reverse=True)[0]
    
    # SMALL BANKROLL BUILDER (HALF-KELLY)
    if best[3] > 0.03: 
        kelly_pct = max(0, (best[3] / (best[2] - 1)) * 0.50) # 0.50 = Half Kelly
        stake_eur = max(1.0, bankroll * kelly_pct) # Aposta mínima de 1€
        seal_color = "#00FF88"
        status_msg = f"PRO EDGE: {best[3]:+.1%} | STAKE: {stake_eur:.2f}€ ({kelly_pct:.1%} da Banca)"
    else:
        stake_eur = 0.0
        seal_color = "#FF8C00"
        status_msg = "NO PRO VALUE DETECTED | DO NOT BET"

    with col_res:
        st.markdown(f"""<div class="advisor-seal" style="border-color: rgba({int(seal_color[1:3], 16)}, {int(seal_color[3:5], 16)}, {int(seal_color[5:7], 16)}, 0.4);"><h1 class="advisor-title">{best[0]}</h1><p class="advisor-subtitle" style="color:{seal_color};">{status_msg}</p></div>""", unsafe_allow_html=True)
    with col_risk:
        st.markdown(f"""<div class="risk-card"><b style="color:#00FF88; letter-spacing:1px; font-size:0.65rem;">🛡️ INSTITUTIONAL CONFIDENCE</b><h2 style="margin:5px 0; font-size:2rem; font-weight:700;">{conf_score:.1f}%</h2><p style="color:#64748B; font-size:0.75rem; margin:0;">ASIAN MARKETS & HALF-KELLY ACTIVE</p></div>""", unsafe_allow_html=True)

    df = pd.DataFrame(mkts, columns=["Market", "Prob", "Odd"])
    df["Fair"] = 1/df["Prob"]
    df["Edge"] = (df["Prob"] * df["Odd"]) - 1
    row_colors = [['rgba(0, 255, 136, 0.15)' if e > 0.05 else 'rgba(0, 255, 136, 0.05)' if e > 0.03 else 'rgba(255, 255, 255, 0.01)' for e in df["Edge"]]]

    fig = go.Figure(data=[go.Table(
        header=dict(values=['<b>PRO MARKET</b>', '<b>QUANT PROB</b>', '<b>FAIR ODD</b>', '<b>BOOKIE</b>', '<b>TRUE EDGE</b>'], fill_color='#0A0A0A', align='center', font=dict(color='#475569', size=11), height=45),
        cells=dict(values=[df.Market, df.Prob.map('{:.1%}'.format), df.Fair.map('{:.2f}'.format), df.Odd.map('{:.2f}'.format), df.Edge.map('{:+.1%}'.format)],
                   fill_color=row_colors, align='center', font=dict(color='white', size=13), height=40))])
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), paper_bgcolor='rgba(0,0,0,0)', height=(len(mkts)*42+60))
    st.plotly_chart(fig, use_container_width=True)
