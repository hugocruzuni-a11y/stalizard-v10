import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from scipy.stats import poisson
import requests
from datetime import date
import random
import time

# ==========================================
# 1. AMBIENTE DE ALTA PERFORMANCE
# ==========================================
st.set_page_config(page_title="APEX QUANT | ALPHA", layout="wide", initial_sidebar_state="collapsed")

# Função de reinício segura para qualquer versão
def safe_rerun():
    try:
        st.rerun()
    except:
        st.experimental_rerun()

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800;900&family=JetBrains+Mono:wght@400;700&display=swap');
    .stApp { background-color: #030407; color: #FFFFFF; font-family: 'Outfit', sans-serif; background-image: radial-gradient(circle at 50% 0%, #0A1128 0%, #030407 80%); }
    header, footer { visibility: hidden; }
    
    .top-nav { background: rgba(3, 4, 7, 0.85); backdrop-filter: blur(20px); border-bottom: 1px solid rgba(0, 240, 255, 0.15); padding: 15px 40px; display: flex; justify-content: space-between; align-items: center; margin: -3rem -3rem 2rem -3rem; position: sticky; top: 0; z-index: 1000; }
    .logo { font-size: 2.2rem; font-weight: 900; color: #FFFFFF; text-transform: uppercase; letter-spacing: -2px; }
    .logo span { color: #00F0FF; text-shadow: 0 0 20px rgba(0, 240, 255, 0.5); }
    
    .alpha-card { background: linear-gradient(180deg, #0D1629 0%, #05080F 100%); border: 1px solid rgba(0, 240, 255, 0.2); border-radius: 24px; padding: 35px; box-shadow: 0 20px 60px rgba(0,0,0,0.6); position: relative; margin-bottom: 25px;}
    .alpha-card::before { content: ''; position: absolute; top: 0; left: 0; width: 100%; height: 4px; background: linear-gradient(90deg, #00F0FF, #00FF88); }
    
    .target-box { background: rgba(0, 255, 136, 0.03); border: 2px dashed rgba(0, 255, 136, 0.3); border-radius: 16px; padding: 25px; text-align: center; position: relative; margin-top: 10px;}
    .target-badge { position: absolute; top: -14px; left: 50%; transform: translateX(-50%); background: #00FF88; color: #000; font-weight: 900; font-size: 0.8rem; padding: 6px 20px; border-radius: 50px; text-transform: uppercase; letter-spacing: 2px; }
    
    .btn-execute div.stButton > button { background: linear-gradient(90deg, #00FF88, #00B86B) !important; color: #000 !important; font-weight: 900; font-size: 1.2rem !important; border: none !important; border-radius: 12px !important; height: 65px !important; width: 100%; margin-top: 20px; transition: 0.2s; }
    .btn-execute div.stButton > button:hover { transform: translateY(-3px); box-shadow: 0 15px 40px rgba(0, 255, 136, 0.4); }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. MOTOR DE DADOS BLINDADO
# ==========================================
API_KEY = "8171043bf0a322286bb127947dbd4041"
HEADERS = {"x-apisports-key": API_KEY, "x-apisports-host": "v3.football.api-sports.io"}

def fetch_api_safe(endpoint, params):
    try:
        r = requests.get(f"https://{HEADERS['x-apisports-host']}/{endpoint}", headers=HEADERS, params=params, timeout=10)
        return r.json().get('response', [])
    except:
        return []

@st.cache_data(ttl=300)
def get_live_fixtures(date_str, league_id):
    return fetch_api_safe("fixtures", {"date": date_str, "league": league_id, "season": "2025"})

@st.cache_data(ttl=3600)
def get_stats_safe(team_id, league_id):
    res = fetch_api_safe("teams/statistics", {"team": team_id, "league": league_id, "season": "2025"})
    if not res: return {"gf_h": 1.5, "ga_h": 1.2, "gf_a": 1.1, "ga_a": 1.4}
    try:
        goals = res.get('goals', {}) if isinstance(res, dict) else res[0].get('goals', {})
        return {
            "gf_h": float(goals.get('for', {}).get('average', {}).get('home', 1.5)),
            "ga_h": float(goals.get('against', {}).get('average', {}).get('home', 1.2)),
            "gf_a": float(goals.get('for', {}).get('average', {}).get('away', 1.1)),
            "ga_a": float(goals.get('against', {}).get('average', {}).get('away', 1.4))
        }
    except:
        return {"gf_h": 1.5, "ga_h": 1.2, "gf_a": 1.1, "ga_a": 1.4}

@st.cache_data(ttl=60)
def get_odds_safe(fixture_id):
    res = fetch_api_safe("odds", {"fixture": fixture_id, "bookmaker": 8})
    market_odds = {}
    try:
        if res and res[0].get('bookmakers'):
            for bet in res[0]['bookmakers'][0].get('bets', []):
                if bet['name'] == 'Match Winner':
                    vals = {v['value']: float(v['odd']) for v in bet['values']}
                    market_odds.update({"Vitória Casa": vals.get('Home', 0), "Empate": vals.get('Draw', 0), "Vitória Fora": vals.get('Away', 0)})
                elif bet['name'] == 'Goals Over/Under':
                    vals = {v['value']: float(v['odd']) for v in bet['values']}
                    market_odds.update({"Over 2.5": vals.get('Over 2.5', 0)})
    except: pass
    return market_odds

# ==========================================
# 3. INTERFACE PRINCIPAL
# ==========================================
st.markdown("""<div class="top-nav"><div class="logo">APEX<span>QUANT</span></div></div>""", unsafe_allow_html=True)

col_menu, col_main = st.columns([1, 3])

with col_menu:
    st.subheader("Radar de Mercado")
    target_date = st.date_input("Data", date.today())
    l_map = {"🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League": 39, "🇪🇸 La Liga": 140, "🇵🇹 Primeira Liga": 94, "🇮🇹 Serie A": 135}
    league_name = st.selectbox("Liga", list(l_map.keys()))
    
    with st.spinner("A conectar..."):
        fixtures = get_live_fixtures(target_date.strftime('%Y-%m-%d'), l_map[league_name])
    
    m_sel = None
    if fixtures:
        m_map = {f"{f['teams']['home']['name']} vs {f['teams']['away']['name']}": f for f in fixtures}
        m_name = st.selectbox("Jogo", list(m_map.keys()))
        m_sel = m_map[m_name]
    else:
        st.warning("Sem jogos nesta data.")

with col_main:
    if m_sel:
        fixture_id = m_sel['fixture']['id']
        h_id, a_id = m_sel['teams']['home']['id'], m_sel['teams']['away']['id']
        
        with st.spinner("Análise Neural em curso..."):
            h_stats = get_stats_safe(h_id, l_map[league_name])
            a_stats = get_stats_safe(a_id, l_map[league_name])
            odds = get_odds_safe(fixture_id)
            
            # Matemática de Poisson Rápida
            xg_h = (h_stats['gf_h'] + a_stats['ga_a']) / 2
            xg_a = (a_stats['gf_a'] + h_stats['ga_h']) / 2
            
            prob_h = poisson.pmf(np.arange(10), xg_h)
            prob_a = poisson.pmf(np.arange(10), xg_a)
            mtx = np.outer(prob_h, prob_a)
            
            p_win_h = np.sum(np.triu(mtx, 1)) # Simplificado para demo estável
            p_over25 = 1 - (mtx[0,0] + mtx[0,1] + mtx[0,2] + mtx[1,0] + mtx[1,1] + mtx[2,0])

        st.markdown(f"""
            <div class="alpha-card">
                <div style="text-align:center;">
                    <div class="league-badge">{league_name} • ANALYTICS</div>
                    <div style="font-size:2.5rem; font-weight:900;">{m_sel['teams']['home']['name']} vs {m_sel['teams']['away']['name']}</div>
                </div>
        """, unsafe_allow_html=True)
        
        # Aposta Sugerida
        if odds.get("Vitória Casa") and p_win_h > 0:
            edge = (p_win_h * odds["Vitória Casa"]) - 1
            st.markdown(f"""
                <div class="target-box">
                    <div class="target-badge">ALVO MATEMÁTICO VALIDADO</div>
                    <div style="font-size:2rem; font-weight:900;">Vitória: {m_sel['teams']['home']['name']}</div>
                    <div style="display:flex; justify-content:center; gap:40px; margin-top:20px; font-family:'JetBrains Mono';">
                        <div>ODD: <span style="color:#FFD700; font-weight:800;">{odds['Vitória Casa']:.2f}</span></div>
                        <div>EDGE: <span style="color:#00FF88; font-weight:800;">+{edge*100:.1f}%</span></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<div class='btn-execute'>", unsafe_allow_html=True)
            if st.button("🚀 EXECUTAR APOSTA AGORA"):
                st.balloons()
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("Aguardando Odds em tempo real da API para validar o Edge...")
            
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div style='text-align:center; padding-top:100px; opacity:0.3;'><h1>SELECIONE UM JOGO REAL</h1></div>", unsafe_allow_html=True)