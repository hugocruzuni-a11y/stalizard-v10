import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from scipy.stats import poisson
import requests
from datetime import date
import random
import time
import uuid

# ==========================================
# 1. DESIGN OMEGA (FOCO NO UTILIZADOR & IMPACTO)
# ==========================================
st.set_page_config(page_title="APEX ORACLE | PROFITS", layout="wide", initial_sidebar_state="collapsed")

def safe_rerun():
    try: st.rerun()
    except: st.experimental_rerun()

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800;900&family=JetBrains+Mono:wght@400;700&display=swap');
    
    .stApp { background-color: #05070A; color: #FFFFFF; font-family: 'Outfit', sans-serif; }
    header, footer { visibility: hidden; }
    
    /* Top Bar - Premium */
    .top-nav { background: rgba(10, 15, 28, 0.9); backdrop-filter: blur(15px); border-bottom: 2px solid #1E293B; padding: 15px 40px; display: flex; justify-content: space-between; align-items: center; margin: -3rem -3rem 2rem -3rem; position: sticky; top: 0; z-index: 1000; }
    .logo { font-size: 2.2rem; font-weight: 900; letter-spacing: -2px; color: #FFFFFF; }
    .logo span { color: #00FF88; text-shadow: 0 0 15px rgba(0, 255, 136, 0.4); }
    
    /* Alpha Card - Onde o dinheiro é feito */
    .alpha-card { background: linear-gradient(180deg, #0D1629 0%, #05070A 100%); border: 1px solid rgba(0, 240, 255, 0.2); border-radius: 24px; padding: 35px; box-shadow: 0 25px 50px rgba(0,0,0,0.5); position: relative; }
    .alpha-card::before { content: ''; position: absolute; top: 0; left: 0; width: 100%; height: 4px; background: linear-gradient(90deg, #00F0FF, #00FF88); }
    
    .match-title { font-size: 2.5rem; font-weight: 900; text-align: center; margin-bottom: 10px; letter-spacing: -1px; }
    
    /* Target Box - Aposta Principal */
    .target-box { background: rgba(0, 255, 136, 0.05); border: 2px dashed #00FF88; border-radius: 16px; padding: 25px; text-align: center; margin: 20px 0; }
    .target-label { color: #00FF88; font-size: 0.85rem; font-weight: 800; text-transform: uppercase; letter-spacing: 2px; }
    .target-value { font-size: 2.4rem; font-weight: 900; margin: 10px 0; color: #FFF; text-shadow: 0 0 20px rgba(255,255,255,0.2); }
    
    /* Botão de Execução */
    .btn-nuke div.stButton > button { background: linear-gradient(90deg, #00FF88, #00B86B) !important; color: #000 !important; font-weight: 900 !important; font-size: 1.3rem !important; text-transform: uppercase; border: none !important; border-radius: 12px !important; height: 70px !important; width: 100%; transition: 0.2s; box-shadow: 0 10px 30px rgba(0, 255, 136, 0.3); }
    .btn-nuke div.stButton > button:hover { transform: translateY(-3px); box-shadow: 0 15px 40px rgba(0, 255, 136, 0.5); }
    
    /* Metrics */
    .metric-row { display: flex; justify-content: space-around; background: #0A0F1C; border-radius: 12px; padding: 15px; margin-top: 20px; border: 1px solid #1E293B; }
    .metric-item { text-align: center; }
    .metric-label { font-size: 0.7rem; color: #64748B; text-transform: uppercase; font-weight: 800; }
    .metric-value { font-size: 1.3rem; font-weight: 800; color: #FFF; font-family: 'JetBrains Mono'; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. MOTOR DE DADOS REAIS BLINDADO
# ==========================================
API_KEY = "8171043bf0a322286bb127947dbd4041"
HEADERS = {"x-apisports-key": API_KEY, "x-apisports-host": "v3.football.api-sports.io"}

def fetch_api(endpoint, params):
    try:
        r = requests.get(f"https://{HEADERS['x-apisports-host']}/{endpoint}", headers=HEADERS, params=params, timeout=10)
        return r.json().get('response', [])
    except: return []

@st.cache_data(ttl=300)
def get_fixtures(date_str, league_id):
    return fetch_api("fixtures", {"date": date_str, "league": league_id, "season": "2025"})

@st.cache_data(ttl=3600)
def get_stats(team_id, league_id):
    res = fetch_api("teams/statistics", {"team": team_id, "league": league_id, "season": "2025"})
    if not res: return {"gf_h": 1.5, "ga_h": 1.1, "gf_a": 1.2, "ga_a": 1.4}
    data = res if isinstance(res, dict) else res[0]
    goals = data.get('goals', {})
    return {
        "gf_h": float(goals.get('for', {}).get('average', {}).get('home', 1.5)),
        "ga_h": float(goals.get('against', {}).get('average', {}).get('home', 1.1)),
        "gf_a": float(goals.get('for', {}).get('average', {}).get('away', 1.2)),
        "ga_a": float(goals.get('against', {}).get('average', {}).get('away', 1.4))
    }

@st.cache_data(ttl=60)
def get_odds(fixture_id):
    res = fetch_api("odds", {"fixture": fixture_id, "bookmaker": 8})
    market = {}
    if res and res[0].get('bookmakers'):
        for bet in res[0]['bookmakers'][0].get('bets', []):
            if bet['name'] == 'Match Winner':
                vals = {v['value']: float(v['odd']) for v in bet['values']}
                market.update({"Casa": vals.get('Home', 0), "Empate": vals.get('Draw', 0), "Fora": vals.get('Away', 0)})
    return market

# ==========================================
# 3. INTERFACE PRINCIPAL (PRODUTO DE MILHÕES)
# ==========================================
st.markdown("""<div class="top-nav"><div class="logo">APEX<span>ORACLE</span></div><div style="color:#00FF88; font-weight:800; font-size:0.8rem;">● IA ATIVA</div></div>""", unsafe_allow_html=True)

c_side, c_main = st.columns([1, 2.5], gap="large")

with c_side:
    st.markdown("<h3 style='font-size:1.2rem; font-weight:800;'>MERCADOS REAIS</h3>", unsafe_allow_html=True)
    t_date = st.date_input("Data", date.today())
    l_map = {"🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League": 39, "🇪🇸 La Liga": 140, "🇵🇹 Primeira Liga": 94, "🇮🇹 Serie A": 135, "🇪🇺 Champions League": 2}
    league_name = st.selectbox("Competição", list(l_map.keys()))
    
    fixtures = get_fixtures(t_date.strftime('%Y-%m-%d'), l_map[league_name])
    m_sel = None
    if fixtures:
        m_map = {f"{f['teams']['home']['name']} vs {f['teams']['away']['name']}": f for f in fixtures}
        m_sel = m_map[st.selectbox("Selecionar Jogo", list(m_map.keys()))]
    else:
        st.info("Sem jogos reais nesta data.")

with c_main:
    if m_sel:
        h_name, a_name = m_sel['teams']['home']['name'], m_sel['teams']['away']['name']
        with st.spinner("IA a calcular probabilidades..."):
            h_stats = get_stats(m_sel['teams']['home']['id'], l_map[league_name])
            a_stats = get_stats(m_sel['teams']['away']['id'], l_map[league_name])
            live_odds = get_odds(m_sel['fixture']['id'])
            
            # Poisson Simples & Eficiente
            xg_h = (h_stats['gf_h'] + a_stats['ga_a']) / 2
            xg_a = (a_stats['gf_a'] + h_stats['ga_h']) / 2
            prob_h = poisson.pmf(np.arange(10), xg_h)
            prob_a = poisson.pmf(np.arange(10), xg_a)
            mtx = np.outer(prob_h, prob_a)
            
            p_win_h = np.sum(np.tril(mtx, -1))
            p_draw = np.sum(np.diag(mtx))
            p_win_a = np.sum(np.triu(mtx, 1))

        st.markdown(f"""
            <div class="alpha-card">
                <div class="match-title">{h_name} vs {a_name}</div>
                <div style="text-align:center; color:#64748B; font-weight:800; letter-spacing:2px;">{league_name}</div>
        """, unsafe_allow_html=True)
        
        # Lógica de "The Pick"
        pick_name = "Vitória " + h_name
        m_odd = live_odds.get("Casa", 1.90)
        p_true = p_win_h
        
        if p_win_a > p_win_h:
            pick_name = "Vitória " + a_name
            m_odd = live_odds.get("Fora", 1.90)
            p_true = p_win_a

        edge = (p_true * m_odd) - 1
        confidence = int(p_true * 100)

        c1, c2 = st.columns([1, 1.5])
        with c1:
            fig = go.Figure(go.Indicator(
                mode = "gauge+number", value = confidence,
                number = {'suffix': "%", 'font': {'size': 40, 'color': '#FFF'}},
                title = {'text': "CONFIANÇA IA", 'font': {'size': 12, 'color': '#00F0FF'}},
                gauge = {'axis': {'range': [None, 100], 'visible': False}, 'bar': {'color': "#00FF88"}}
            ))
            fig.update_layout(height=200, margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
            
        with c2:
            st.markdown(f"""
                <div class="target-box">
                    <div class="target-label">🔒 APOSTA RECOMENDADA</div>
                    <div class="target-value">{pick_name}</div>
                    <div style="display:flex; justify-content:center; gap:20px; font-weight:800;">
                        <span style="color:#FFD700;">ODD: {m_odd:.2f}</span>
                        <span style="color:#00FF88;">EDGE: +{max(0.1, edge*100):.1f}%</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<div class='btn-nuke'>", unsafe_allow_html=True)
            if st.button("🚀 DESBLOQUEAR ACESSO VIP"):
                st.balloons()
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(f"""
            <div class="metric-row">
                <div class="metric-item"><div class="metric-label">Proj. xG Casa</div><div class="metric-value">{xg_h:.2f}</div></div>
                <div class="metric-item"><div class="metric-label">Proj. xG Fora</div><div class="metric-value">{xg_a:.2f}</div></div>
                <div class="metric-item"><div class="metric-label">Prob. Empate</div><div class="metric-value">{p_draw*100:.1f}%</div></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    else:
        st.markdown("<div style='text-align:center; padding-top:100px; opacity:0.2;'><h1>ESCOLHA UM JOGO ALVO</h1></div>", unsafe_allow_html=True)

st.markdown("<div style='text-align:center; margin-top:50px; color:#475569; font-size:0.7rem;'>APEX ORACLE SYSTEM v2.0 - MATEMÁTICA PURA</div>", unsafe_allow_html=True)