import streamlit as st
import numpy as np
from scipy.stats import poisson
import pandas as pd
import plotly.graph_objects as go
import requests
from datetime import date

# --- 1. CONFIGURAÇÃO INSTITUCIONAL ---
st.set_page_config(
    page_title="STARLINE V140 PRO - PURE SOVEREIGN", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# --- 2. SOVEREIGN ELITE CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@200;300;400;600;700&display=swap');
    .stApp { background: radial-gradient(circle at 50% -20%, #1e293b 0%, #000000 95%); color: #FFFFFF; font-family: 'Inter', sans-serif; }
    [data-testid="stSidebar"] { background-color: rgba(255, 255, 255, 0.01) !important; backdrop-filter: blur(45px) !important; border-right: 1px solid rgba(255, 255, 255, 0.05) !important; }
    [data-testid="stSidebar"] .stNumberInput input, [data-testid="stSidebar"] .stTextInput input, [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] {
        background-color: rgba(255, 255, 255, 0.96) !important; border: 1px solid rgba(0, 255, 136, 0.2) !important; color: #000000 !important; 
        font-family: 'Inter', sans-serif !important; font-weight: 300 !important; font-size: 0.85rem !important; border-radius: 4px !important;
    }
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

# --- 3. MOTOR DE API DIRETA ---
api_key = "8171043bf0a322286bb127947dbd4041" 
api_host = "v3.football.api-sports.io" 

headers = {
    "x-apisports-key": api_key
}

def get_fixtures_today(league_id):
    today = date.today().strftime('%Y-%m-%d')
    url = f"https://{api_host}/fixtures"
    querystring = {"date": today, "league": league_id, "season": "2025"} 
    try:
        response = requests.get(url, headers=headers, params=querystring)
        return response.json().get('response', [])
    except:
        return []

def get_team_xg_stats(team_id, league_id):
    url = f"https://{api_host}/teams/statistics"
    querystring = {"league": league_id, "season": "2025", "team": team_id}
    try:
        response = requests.get(url, headers=headers, params=querystring)
        goals_stats = response.json().get('response', {}).get('goals', {})
        xgF_h = float(goals_stats.get('for', {}).get('average', {}).get('home', 1.5))
        xgA_h = float(goals_stats.get('against', {}).get('average', {}).get('home', 1.0))
        xgF_a = float(goals_stats.get('for', {}).get('average', {}).get('away', 1.2))
        xgA_a = float(goals_stats.get('against', {}).get('average', {}).get('away', 1.3))
        return xgF_h, xgA_h, xgF_a, xgA_a
    except:
        return 1.5, 1.0, 1.2, 1.3 

def get_pre_match_odds(fixture_id):
    """Extrator Avançado de Odds (Bet365) para Múltiplos Mercados"""
    url = f"https://{api_host}/odds"
    querystring = {"fixture": fixture_id, "bookmaker": 8} 
    # Dicionário de fallback seguro caso a API não tenha certas odds disponíveis
    odds_dict = {
        "1": 2.00, "X": 3.00, "2": 3.00, 
        "O15": 1.30, "U15": 3.40, "O25": 1.85, "U25": 1.85, "O35": 3.20, "U35": 1.35, 
        "BTTS": 1.80, "DNB_H": 1.50, "DNB_A": 2.50
    }
    
    try:
        response = requests.get(url, headers=headers, params=querystring)
        data = response.json().get('response', [])
        if data:
            markets = data[0]['bookmakers'][0]['bets']
            for mkt in markets:
                if mkt['name'] == 'Match Winner':
                    odds_dict["1"] = float(mkt['values'][0]['odd'])
                    odds_dict["X"] = float(mkt['values'][1]['odd'])
                    odds_dict["2"] = float(mkt['values'][2]['odd'])
                elif mkt['name'] == 'Goals Over/Under':
                    for val in mkt['values']:
                        if val['value'] == 'Over 1.5': odds_dict["O15"] = float(val['odd'])
                        if val['value'] == 'Under 1.5': odds_dict["U15"] = float(val['odd'])
                        if val['value'] == 'Over 2.5': odds_dict["O25"] = float(val['odd'])
                        if val['value'] == 'Under 2.5': odds_dict["U25"] = float(val['odd'])
                        if val['value'] == 'Over 3.5': odds_dict["O35"] = float(val['odd'])
                        if val['value'] == 'Under 3.5': odds_dict["U35"] = float(val['odd'])
                elif mkt['name'] == 'Both Teams Score':
                    odds_dict["BTTS"] = float(mkt['values'][0]['odd'])
                elif mkt['name'] == 'Home/Away': # Draw No Bet / AH 0.0 market
                    odds_dict["DNB_H"] = float(mkt['values'][0]['odd'])
                    odds_dict["DNB_A"] = float(mkt['values'][1]['odd'])
        return odds_dict
    except:
        return odds_dict

# --- 4. SIDEBAR COCKPIT ---
with st.sidebar:
    st.markdown("<h2 style='color:#00FF88; font-size:22px; font-weight:700;'>🏛️ ORACLE V140 PRO</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#475569; font-size:0.65rem; font-weight:700;'>01 // LIVE API INJECTION</p>", unsafe_allow_html=True)
    
    league_map = {"Premier League (UK)": 39, "La Liga (ES)": 140, "Champions League": 2, "Primeira Liga (PT)": 94}
    league_name = st.selectbox("SELECT LEAGUE", list(league_map.keys()))
    league_id = league_map[league_name]
    
    fixtures = get_fixtures_today(league_id)
    match_selected = None
    
    if not fixtures:
        st.warning(f"Não há jogos agendados hoje para a {league_name}.")
        # Mock de segurança para renderizar o painel sem erros
        live_odds = get_pre_match_odds(0) 
    else:
        match_map = {f"{f['teams']['home']['name']} vs {f['teams']['away']['name']}": f['fixture']['id'] for f in fixtures}
        match_display = st.selectbox("SELECT MATCH", list(match_map.keys()))
        match_id = match_map[match_display]
        match_selected = next(f for f in fixtures if f['fixture']['id'] == match_id)
        
        with st.spinner('A extrair Todas as Odds do Mercado...'):
            live_odds = get_pre_match_odds(match_id)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<p style='color:#475569; font-size:0.65rem; font-weight:700;'>02 // ADVANCED MODEL TUNING</p>", unsafe_allow_html=True)
    rho_param = st.slider("Dixon-Coles Rho (ρ)", min_value=-0.2, max_value=0.2, value=-0.11, step=0.01)
    home_adv_boost = st.slider("Home Advantage Boost (%)", min_value=0, max_value=25, value=12, step=1) / 100.0

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<p style='color:#475569; font-size:0.65rem; font-weight:700;'>03 // FULL MARKET ODDS (Auto-Filled)</p>", unsafe_allow_html=True)
    c1, cx, c2 = st.columns(3)
    m1 = c1.number_input("1", value=live_odds["1"], format="%.2f")
    mx = cx.number_input("X", value=live_odds["X"], format="%.2f")
    m2 = c2.number_input("2", value=live_odds["2"], format="%.2f")
    
    st.write("GOALS LADDER")
    c3, c4 = st.columns(2)
    o15_i = c3.number_input("O1.5", value=live_odds["O15"], format="%.2f")
    u15_i = c4.number_input("U1.5", value=live_odds["U15"], format="%.2f")
    o25_i = c3.number_input("O2.5", value=live_odds["O25"], format="%.2f")
    u25_i = c4.number_input("U2.5", value=live_odds["U25"], format="%.2f")
    o35_i = c3.number_input("O3.5", value=live_odds["O35"], format="%.2f")
    u35_i = c4.number_input("U3.5", value=live_odds["U35"], format="%.2f")
    
    st.write("SPECIALS")
    m_ob = st.number_input("BTTS (YES)", value=live_odds["BTTS"], format="%.2f")
    c5, c6 = st.columns(2)
    ah_h = c5.number_input("AH 0.0 (H)", value=live_odds["DNB_H"], format="%.2f")
    ah_a = c6.number_input("AH 0.0 (A)", value=live_odds["DNB_A"], format="%.2f")
    
    st.markdown("<br>", unsafe_allow_html=True)
    run_scan = st.button("🚀 EXECUTE ALPHA SCAN")

# --- 5. RESULTS INTERFACE ---
if not run_scan or not match_selected:
    st.markdown("<div style='text-align:center; padding-top:150px; opacity:0.1;'><h1>ORACLE V140 PRO</h1><p>INSTITUTIONAL QUANT ENGINE</p></div>", unsafe_allow_html=True)
else:
    with st.spinner('A processar Matriz Quantitativa de Espectro Total...'):
        h_id = match_selected['teams']['home']['id']
        a_id = match_selected['teams']['away']['id']
        h_n = match_selected['teams']['home']['name'].upper()
        a_n = match_selected['teams']['away']['name'].upper()
        
        h_xgF, h_xgA, _, _ = get_team_xg_stats(h_id, league_id)
        _, _, a_xgF, a_xgA = get_team_xg_stats(a_id, league_id)

    # Motor Lambdas
    lh = (h_xgF * a_xgA) ** 0.5 * (1 + home_adv_boost)
    la = (a_xgF * h_xgA) ** 0.5 * (1 - home_adv_boost)

    # Matriz Exata
    max_goals = 10
    hp = poisson.pmf(np.arange(max_goals), lh)
    ap = poisson.pmf(np.arange(max_goals), la)
    prob_matrix = np.outer(hp, ap)

    # Correção Dixon-Coles
    for x in range(2):
        for y in range(2):
            if x == 0 and y == 0: correction = 1 - (lh * la * rho_param)
            elif x == 0 and y == 1: correction = 1 + (lh * rho_param)
            elif x == 1 and y == 0: correction = 1 + (la * rho_param)
            elif x == 1 and y == 1: correction = 1 - rho_param
            else: correction = 1.0
            prob_matrix[x, y] = max(0, prob_matrix[x, y] * correction)

    prob_matrix /= prob_matrix.sum()

    # Probabilidades de Match Odds
    ph = np.tril(prob_matrix, -1).sum() 
    px = np.trace(prob_matrix)          
    pa = np.triu(prob_matrix, 1).sum()  

    # Probabilidades de Golos (Escada Completa)
    goals_sum_matrix = np.add.outer(np.arange(max_goals), np.arange(max_goals))
    o15_prob = prob_matrix[goals_sum_matrix > 1.5].sum()
    u15_prob = prob_matrix[goals_sum_matrix < 1.5].sum()
    o25_prob = prob_matrix[goals_sum_matrix > 2.5].sum()
    u25_prob = prob_matrix[goals_sum_matrix < 2.5].sum()
    o35_prob = prob_matrix[goals_sum_matrix > 3.5].sum()
    u35_prob = prob_matrix[goals_sum_matrix < 3.5].sum()

    # Probabilidades de Mercados Especiais (BTTS e AH 0.0)
    btts_prob = prob_matrix[1:, 1:].sum() 
    # AH 0.0 (Draw No Bet) isola o empate da matemática
    ah_h_prob = ph / (ph + pa) if (ph + pa) > 0 else 0 
    ah_a_prob = pa / (ph + pa) if (ph + pa) > 0 else 0 

    cv = np.sqrt(lh + la) / (lh + la) if (lh + la) > 0 else 1
    conf_score = max(50.0, min(99.9, 100 * (1 - (cv / 2.8))))

    # --- UI RENDER ---
    st.markdown(f"<h1 style='letter-spacing:-3px; font-size:55px; margin:0; font-weight:700;'>{h_n} <span style='color:#00FF88; font-weight:300;'>vs</span> {a_n}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:#64748B; font-size:0.8rem; text-transform:uppercase;'>{league_name} // Match ID: {match_id} // Full Market Sync</p>", unsafe_allow_html=True)
    
    col_res, col_risk = st.columns([1.1, 0.9])
    
    # Lista Completa de Mercados Re-integrada
    mkts = [
        ("WIN: "+h_n, ph, m1), ("WIN: "+a_n, pa, m2), ("DRAW (X)", px, mx),
        ("O1.5 GOALS", o15_prob, o15_i), ("U1.5 GOALS", u15_prob, u15_i),
        ("O2.5 GOALS", o25_prob, o25_i), ("U2.5 GOALS", u25_prob, u25_i),
        ("O3.5 GOALS", o35_prob, o35_i), ("U3.5 GOALS", u35_prob, u35_i),
        ("BTTS (YES)", btts_prob, m_ob),
        ("AH 0.0: "+h_n, ah_h_prob, ah_h), ("AH 0.0: "+a_n, ah_a_prob, ah_a)
    ]
    
    # O Alpha Scanner: Encontrar o melhor Edge e calcular Quarter-Kelly
    valid_mkts = [(n, p, b, (p*b)-1) for n, p, b in mkts if p > 0 and b > 1.01]
    best = sorted(valid_mkts, key=lambda x: x[3], reverse=True)[0]
    
    # Se não houver valor no mercado inteiro, ele protege-te.
    if best[3] > 0.02: # Só recomenda se tiver mais de 2% de edge
        kelly = max(0, (best[3] / (best[2] - 1)) * 0.25)
        seal_color = "#00FF88"
        status_msg = f"ALPHA EDGE DETECTED: {best[3]:+.1%} | Q-KELLY STAKE: {kelly:.2%}"
    else:
        kelly = 0.0
        seal_color = "#FF8C00"
        status_msg = "NO CLEAR VALUE DETECTED | DO NOT BET"

    with col_res:
        st.markdown(f"""<div class="advisor-seal" style="border-color: rgba({int(seal_color[1:3], 16)}, {int(seal_color[3:5], 16)}, {int(seal_color[5:7], 16)}, 0.4);"><h1 class="advisor-title">{best[0]}</h1><p class="advisor-subtitle" style="color:{seal_color};">{status_msg}</p></div>""", unsafe_allow_html=True)
    
    with col_risk:
        st.markdown(f"""<div class="risk-card"><b style="color:#00FF88; letter-spacing:1px; font-size:0.65rem;">🛡️ INSTITUTIONAL CONFIDENCE</b><h2 style="margin:5px 0; font-size:2rem; font-weight:700;">{conf_score:.1f}%</h2><p style="color:#64748B; font-size:0.75rem; margin:0;">FULL MATRIX & Q-KELLY ACTIVE</p></div>""", unsafe_allow_html=True)

    c_ins1, c_ins2 = st.columns(2)
    with c_ins1:
        st.markdown(f"""<div class="intel-card"><b style="color:#00FF88;">🧠 QUANT TACTICAL ANALYSIS</b><br>
        <span style="color:#CBD5E1; line-height:1.6;">Home xGF: <b>{h_xgF:.2f}</b> | Away xGF: <b>{a_xgF:.2f}</b><br>
        Expected Total (xG): <b>{(lh+la):.2f}</b> | Dixon-Coles ρ: <b>{rho_param}</b></span></div>""", unsafe_allow_html=True)
    with c_ins2:
        idx = np.unravel_index(np.argsort(prob_matrix.ravel())[-2:], prob_matrix.shape)
        st.markdown(f"""<div class="intel-card"><b style="color:#00FF88;">🎯 EXACT SCORE MATRIX (TOP 2)</b><br>
        <span style="color:#CBD5E1;">1. {idx[0][1]}-{idx[1][1]} ({prob_matrix[idx[0][1], idx[1][1]]:.1%}) | 2. {idx[0][0]}-{idx[1][0]} ({prob_matrix[idx[0][0], idx[1][0]]:.1%})</span></div>""", unsafe_allow_html=True)

    # MATRIZ DE TABELA (Com formatação Alpha)
    df = pd.DataFrame(mkts, columns=["Market", "Prob", "Odd"])
    df["Fair"] = 1/df["Prob"]
    df["Edge"] = (df["Prob"] * df["Odd"]) - 1
    
    # Destaca em verde apenas apostas de valor comprovado (>2%)
    row_colors = [['rgba(0, 255, 136, 0.15)' if e > 0.05 else 'rgba(0, 255, 136, 0.05)' if e > 0.02 else 'rgba(255, 255, 255, 0.01)' for e in df["Edge"]]]

    fig = go.Figure(data=[go.Table(
        header=dict(values=['<b>MARKET</b>', '<b>PROB</b>', '<b>FAIR ODD</b>', '<b>BOOKIE</b>', '<b>TRUE EDGE</b>'], fill_color='#0A0A0A', align='center', font=dict(color='#475569', size=11), height=45),
        cells=dict(values=[df.Market, df.Prob.map('{:.1%}'.format), df.Fair.map('{:.2f}'.format), df.Odd.map('{:.2f}'.format), df.Edge.map('{:+.1%}'.format)],
                   fill_color=row_colors, align='center', font=dict(color='white', size=13), height=40))])
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), paper_bgcolor='rgba(0,0,0,0)', height=(len(mkts)*42+60))
    st.plotly_chart(fig, use_container_width=True)

    # GRÁFICO (Densidade)
    xr = list(range(7))
    marg_h = prob_matrix.sum(axis=1)[:7]
    marg_a = prob_matrix.sum(axis=0)[:7]
    
    fig_p = go.Figure()
    fig_p.add_trace(go.Scatter(x=xr, y=marg_h, name=h_n, fill='tozeroy', line_color='#00FF88', line_width=4))
    fig_p.add_trace(go.Scatter(x=xr, y=marg_a, name=a_n, fill='tozeroy', line_color='#3B82F6', line_width=4))
    fig_p.update_layout(title="DIXON-COLES PROBABILITY MASS", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white", height=300)
    st.plotly_chart(fig_p, use_container_width=True)
