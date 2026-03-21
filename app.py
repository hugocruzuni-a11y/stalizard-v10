
import streamlit as st
import numpy as np
from scipy.stats import poisson
import pandas as pd
import plotly.graph_objects as go
import requests
from datetime import date

# --- 1. CONFIGURAÇÃO DE DESIGN ---
st.set_page_config(
    page_title="STARLINE V140 PRO - QUANT TERMINAL", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# CSS Customizado para Tooltips e Labels de Luxo
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
    
    .stApp { background: radial-gradient(circle at 50% -20%, #0f172a 0%, #000000 95%); color: #FFFFFF; font-family: 'Inter', sans-serif; }
    
    /* Design das Caixas de Texto e Botões */
    [data-testid="stSidebar"] { background-color: rgba(15, 23, 42, 0.8) !important; backdrop-filter: blur(20px); border-right: 1px solid rgba(0, 255, 136, 0.1); }
    
    .advisor-seal { 
        background: linear-gradient(135deg, rgba(0, 255, 136, 0.1) 0%, rgba(255, 255, 255, 0.02) 100%); 
        border-radius: 16px; padding: 25px; border: 1px solid rgba(0, 255, 136, 0.3); 
        box-shadow: 0 10px 30px rgba(0,0,0,0.5); margin-bottom: 25px;
    }

    .intel-card { 
        background: rgba(255, 255, 255, 0.03); border-radius: 12px; padding: 18px; 
        border: 1px solid rgba(255, 255, 255, 0.05); margin-bottom: 12px;
        transition: transform 0.2s ease;
    }
    .intel-card:hover { border-color: rgba(0, 255, 136, 0.4); transform: translateY(-2px); }

    /* Estilo para as métricas de ajuda */
    .help-icon { color: #00FF88; cursor: help; font-size: 0.8rem; margin-left: 5px; }
    
    h1, h2, h3 { letter-spacing: -0.05em; font-weight: 700; }
    .stNumberInput label, .stSelectbox label { font-size: 0.65rem !important; color: #94A3B8 !important; text-transform: uppercase; letter-spacing: 0.1em; }
    
    /* Botão Principal */
    div.stButton > button {
        background: linear-gradient(90deg, #00FF88 0%, #00BD63 100%) !important;
        color: #000000 !important; font-weight: 800; height: 3.5em; border-radius: 8px;
        border: none; text-transform: uppercase; letter-spacing: 2px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    div.stButton > button:hover { transform: scale(1.02); box-shadow: 0 0 20px rgba(0, 255, 136, 0.4); }
    </style>
    """, unsafe_allow_html=True)

# --- 2. MOTOR DE API E MATEMÁTICA (Consolidado) ---
api_key = "8171043bf0a322286bb127947dbd4041" 
api_host = "v3.football.api-sports.io" 
headers = {"x-apisports-key": api_key}

@st.cache_data(ttl=3600)
def get_team_stats(team_id, league_id):
    try:
        url = f"https://{api_host}/teams/statistics"
        res = requests.get(url, headers=headers, params={"league": league_id, "season": "2025", "team": team_id}).json()
        goals = res.get('response', {}).get('goals', {})
        return {
            "h_for": float(goals.get('for', {}).get('average', {}).get('home', 1.5)),
            "h_aga": float(goals.get('against', {}).get('average', {}).get('home', 1.0)),
            "a_for": float(goals.get('for', {}).get('average', {}).get('away', 1.2)),
            "a_aga": float(goals.get('against', {}).get('average', {}).get('away', 1.3))
        }
    except: return {"h_for": 1.5, "h_aga": 1.0, "a_for": 1.2, "a_aga": 1.3}

def calculate_probs(lh, la, rho, boost):
    lh *= (1 + boost); la *= (1 - boost)
    max_g = 10
    prob_mtx = np.outer(poisson.pmf(np.arange(max_g), lh), poisson.pmf(np.arange(max_g), la))
    for x in range(2):
        for y in range(2):
            if x==0 and y==0: prob_mtx[x,y] *= (1 - lh*la*rho)
            elif x==0 and y==1: prob_mtx[x,y] *= (1 + lh*rho)
            elif x==1 and y==0: prob_mtx[x,y] *= (1 + la*rho)
            elif x==1 and y==1: prob_mtx[x,y] *= (1 - rho)
    prob_mtx /= prob_mtx.sum()
    ph, px, pa = np.tril(prob_mtx, -1).sum(), np.trace(prob_mtx), np.triu(prob_mtx, 1).sum()
    
    # AH 0.0 e AH -1.0
    h_win_1 = np.trace(prob_mtx, offset=-1)
    ah_1_h = (ph - h_win_1) / (1 - h_win_1) if (1 - h_win_1) > 0 else 0
    ah_0_h = ph / (ph + pa) if (ph + pa) > 0 else 0
    
    o25 = prob_mtx[np.add.outer(np.arange(max_g), np.arange(max_g)) > 2.5].sum()
    return ph, px, pa, ah_0_h, ah_1_h, o25, prob_mtx

# --- 3. SIDEBAR (UI INTERATIVA) ---
with st.sidebar:
    st.markdown("<h1 style='color:#00FF88; font-size:24px;'>🏛️ ORACLE V140</h1>", unsafe_allow_html=True)
    
    with st.expander("💰 GESTÃO DE CAPITAL", expanded=True):
        bankroll = st.number_input("Banca Total (€)", value=100.0, help="O valor total que tens disponível para apostar.")
    
    with st.expander("📡 SELEÇÃO DE DADOS", expanded=True):
        league_map = {"Premier League": 39, "La Liga": 140, "Primeira Liga": 94}
        l_name = st.selectbox("Liga", list(league_map.keys()))
        
        fixtures = requests.get(f"https://{api_host}/fixtures", headers=headers, 
                               params={"date": date.today().strftime('%Y-%m-%d'), "league": league_map[l_name], "season": "2025"}).json().get('response', [])
        
        if fixtures:
            m_map = {f"{f['teams']['home']['name']} vs {f['teams']['away']['name']}": f['fixture']['id'] for f in fixtures}
            m_display = st.selectbox("Jogo", list(m_map.keys()))
            m_sel = next(f for f in fixtures if f['fixture']['id'] == m_map[m_display])
        else:
            st.warning("Sem jogos para hoje.")
            m_sel = None

    with st.expander("🛠️ CALIBRAÇÃO QUANT", expanded=False):
        rho = st.slider("Rho (Dixon-Coles)", -0.20, 0.20, -0.11, help="Ajusta a dependência de golos. Padrão: -0.11")
        boost = st.slider("Home Advantage %", 0, 25, 12) / 100.0

    with st.expander("📊 ODDS DA CASA", expanded=True):
        c1, cx, c2 = st.columns(3)
        odd1 = c1.number_input("Odd 1", value=2.10)
        oddx = cx.number_input("Odd X", value=3.40)
        odd2 = c2.number_input("Odd 2", value=3.50)
        odd_ah0 = st.number_input("Odd AH 0.0 (H)", value=1.55)
        odd_o25 = st.number_input("Odd Over 2.5", value=1.90)

    st.markdown("<br>", unsafe_allow_html=True)
    scan = st.button("🚀 EXECUTAR ALPHA SCAN")

# --- 4. ÁREA DE RESULTADOS (DESIGN DE ALTO ESCLARECIMENTO) ---
if not scan or not m_sel:
    st.markdown("<div style='text-align:center; padding-top:150px; opacity:0.1;'><h1>ORACLE V140</h1><p>Sovereign Quant Terminal</p></div>", unsafe_allow_html=True)
else:
    # Processamento
    s_h = get_team_stats(m_sel['teams']['home']['id'], league_map[l_name])
    s_a = get_team_stats(m_sel['teams']['away']['id'], league_map[l_name])
    lh, la = (s_h['h_for']*s_a['a_aga'])**0.5, (s_a['a_for']*s_h['h_aga'])**0.5
    ph, px, pa, ah0, ah1, o25, mtx = calculate_probs(lh, la, rho, boost)
    
    # UI Header
    st.markdown(f"<h1 style='font-size:50px; margin-bottom:0;'>{m_sel['teams']['home']['name'].upper()} <span style='color:#00FF88; font-weight:200;'>vs</span> {m_sel['teams']['away']['name'].upper()}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:#94A3B8; margin-top:0;'>ESTATÍSTICA BIVARIADA // DIXON-COLES ATIVO // MEDIA XG INJETADA</p>", unsafe_allow_html=True)

    # 1. Cards de Decisão
    col_main, col_side = st.columns([1.2, 0.8])
    
    mkts = [
        ("WIN: " + m_sel['teams']['home']['name'], ph, odd1),
        ("AH 0.0: " + m_sel['teams']['home']['name'], ah0, odd_ah0),
        ("OVER 2.5 GOALS", o25, odd_o25)
    ]
    best = sorted([(n,p,b,(p*b)-1) for n,p,b in mkts], key=lambda x: x[3], reverse=True)[0]
    edge = best[3]
    kelly = max(0, (edge/(best[2]-1))*0.5)
    
    with col_main:
        color = "#00FF88" if edge > 0.05 else "#FFD700" if edge > 0.02 else "#EF4444"
        st.markdown(f"""
            <div class="advisor-seal" style="border-color: {color};">
                <p style="color:#94A3B8; font-size:0.7rem; text-transform:uppercase; margin-bottom:5px;">Aposta Recomendada</p>
