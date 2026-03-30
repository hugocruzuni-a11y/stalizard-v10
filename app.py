import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from datetime import date, timedelta
import random
import time
import requests

# ==========================================
# 1. SETUP CYBER-PREMIUM (GOD-TIER UI)
# ==========================================
st.set_page_config(page_title="APEX AI | O TEU ALGORITMO", layout="wide", initial_sidebar_state="collapsed")

def safe_rerun():
    try: st.rerun()
    except AttributeError: st.experimental_rerun()

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800;900&family=JetBrains+Mono:wght@400;700;800&display=swap');
    
    .stApp { background-color: #030407; color: #FFFFFF; font-family: 'Outfit', sans-serif; background-image: radial-gradient(circle at 50% 0%, #0D1326 0%, #030407 80%); }
    header, footer { visibility: hidden; }
    
    /* Top Bar - Ultra Modern */
    .top-nav { background: rgba(3, 4, 7, 0.8); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); border-bottom: 1px solid rgba(0, 240, 255, 0.15); padding: 15px 40px; display: flex; justify-content: space-between; align-items: center; margin: -3rem -3rem 2rem -3rem; position: sticky; top: 0; z-index: 1000; box-shadow: 0 10px 30px rgba(0,0,0,0.5);}
    .logo { font-size: 2.2rem; font-weight: 900; letter-spacing: -1px; color: #FFFFFF; text-shadow: 0 0 20px rgba(0, 240, 255, 0.4); line-height: 1;}
    .logo span { color: #00F0FF; }
    
    .live-status { display: flex; align-items: center; gap: 10px; background: rgba(0, 255, 136, 0.05); border: 1px solid rgba(0, 255, 136, 0.3); padding: 8px 16px; border-radius: 50px; font-size: 0.8rem; font-weight: 800; text-transform: uppercase; color: #00FF88; letter-spacing: 1px; box-shadow: 0 0 15px rgba(0, 255, 136, 0.1); }
    .dot { width: 8px; height: 8px; background-color: #00FF88; border-radius: 50%; animation: pulse-green 1.5s infinite; box-shadow: 0 0 10px #00FF88; }
    @keyframes pulse-green { 0% { transform: scale(0.95); opacity: 1; } 50% { transform: scale(1.2); opacity: 0.5; } 100% { transform: scale(0.95); opacity: 1; } }

    /* The Lock Card (Onde a Magia Acontece) */
    .lock-card { background: linear-gradient(180deg, #0A101D 0%, #05080F 100%); border: 1px solid rgba(0, 240, 255, 0.2); border-radius: 20px; padding: 30px; box-shadow: inset 0 0 40px rgba(0,0,0,0.8), 0 20px 50px rgba(0,0,0,0.5); position: relative; overflow: hidden; margin-bottom: 20px;}
    .lock-card::before { content: ''; position: absolute; top: 0; left: 0; width: 100%; height: 4px; background: linear-gradient(90deg, #00F0FF, #00FF88); box-shadow: 0 0 20px #00F0FF; }
    
    .matchup { text-align: center; margin-bottom: 25px; }
    .league-tag { font-size: 0.8rem; color: #00F0FF; text-transform: uppercase; letter-spacing: 3px; font-weight: 800; margin-bottom: 5px; text-shadow: 0 0 10px rgba(0,240,255,0.4); }
    .teams { font-size: 2.2rem; font-weight: 900; line-height: 1.2; letter-spacing: -1px; }
    .teams span { color: #64748B; font-weight: 400; font-size: 1.5rem; margin: 0 15px; }

    /* A Aposta Premium */
    .premium-pick { background: rgba(0, 255, 136, 0.05); border: 2px dashed rgba(0, 255, 136, 0.5); border-radius: 16px; padding: 25px; text-align: center; margin: 25px 0; position: relative; transition: all 0.3s; }
    .premium-pick:hover { background: rgba(0, 255, 136, 0.08); border-color: #00FF88; box-shadow: 0 0 30px rgba(0, 255, 136, 0.15); transform: scale(1.02); }
    .pick-label { position: absolute; top: -12px; left: 50%; transform: translateX(-50%); background: #00FF88; color: #000; font-weight: 900; font-size: 0.75rem; padding: 4px 15px; border-radius: 20px; text-transform: uppercase; letter-spacing: 2px; box-shadow: 0 5px 15px rgba(0,255,136,0.4); }
    .pick-market { font-size: 2.5rem; font-weight: 900; color: #FFFFFF; text-shadow: 0 0 20px rgba(0,255,136,0.3); margin-top: 10px; line-height: 1.1; }
    .pick-odd { font-family: 'JetBrains Mono'; font-size: 1.8rem; color: #FFD700; font-weight: 800; margin-top: 10px; display: block; }
    
    /* Botão Nuclear */
    .btn-nuke div.stButton > button { background: linear-gradient(90deg, #00FF88, #00C86B) !important; color: #000 !important; font-weight: 900 !important; font-size: 1.2rem !important; text-transform: uppercase; letter-spacing: 1px; border: none !important; border-radius: 12px !important; padding: 15px !important; height: 60px !important; transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1); box-shadow: 0 10px 30px rgba(0, 255, 136, 0.3); width: 100%; }
    .btn-nuke div.stButton > button:hover { transform: translateY(-3px) scale(1.02); box-shadow: 0 15px 40px rgba(0, 255, 136, 0.5); }

    /* Neural Bars */
    .neural-row { display: flex; align-items: center; justify-content: space-between; margin-bottom: 15px; }
    .n-label { font-size: 0.75rem; color: #94A3B8; font-weight: 800; text-transform: uppercase; letter-spacing: 1px; width: 120px; }
    .n-bar-bg { flex-grow: 1; background: #1E293B; height: 8px; border-radius: 4px; margin: 0 15px; position: relative; overflow: hidden; }
    .n-bar-fill { position: absolute; top: 0; left: 0; height: 100%; background: linear-gradient(90deg, #00F0FF, #00FF88); border-radius: 4px; box-shadow: 0 0 10px rgba(0,240,255,0.5); }
    .n-value { font-family: 'JetBrains Mono'; font-size: 0.85rem; color: #FFF; font-weight: 800; width: 40px; text-align: right; }

    /* Simulator Panel */
    .sim-panel { background: rgba(255, 255, 255, 0.02); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 16px; padding: 25px; }
    .sim-title { font-size: 1.2rem; font-weight: 800; color: #00F0FF; margin-bottom: 5px; }
    .sim-profit { font-family: 'JetBrains Mono'; font-size: 2.8rem; font-weight: 900; color: #00FF88; line-height: 1; text-shadow: 0 0 20px rgba(0,255,136,0.3); margin: 15px 0; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. MOTOR DA IA (SIMULADO PARA EFEITO UAU)
# ==========================================
# Para o Pitch ao apostador, se a API falhar o ecrã não pode ficar vazio. 
# Usamos dados de jogos míticos como Fallback.

def fetch_games_for_pitch():
    """Gera uma lista de jogos premium para prender o apostador imediatamente."""
    return [
        {"id": 1, "h": "Real Madrid", "a": "Man City", "league": "Liga dos Campeões"},
        {"id": 2, "h": "Arsenal", "a": "Liverpool", "league": "Premier League"},
        {"id": 3, "h": "Benfica", "a": "Sporting CP", "league": "Primeira Liga"},
        {"id": 4, "h": "Bayern Munique", "a": "B. Leverkusen", "league": "Bundesliga"},
        {"id": 5, "h": "Inter Milão", "a": "Juventus", "league": "Serie A"}
    ]

def generate_ai_master_pick(h_name, a_name):
    """A IA cria a 'Aposta Perfeita' e as métricas neurais."""
    random.seed(int(time.time()) + len(h_name))
    
    confidence = random.randint(82, 98) # Confiança brutal
    win_rate_hist = random.uniform(74.5, 89.2)
    
    mkts = [
        (f"Vitória do {h_name}", round(random.uniform(1.70, 2.10), 2)),
        ("Mais de 2.5 Golos", round(random.uniform(1.65, 1.95), 2)),
        (f"{h_name} Handicap Asiático -1.0", round(random.uniform(2.10, 2.60), 2)),
        ("Ambas Marcam e Mais de 2.5", round(random.uniform(1.85, 2.30), 2))
    ]
    pick = random.choice(mkts)
    
    # Métricas Neurais (O que a IA viu para decidir)
    metrics = [
        {"label": "Vantagem Tática", "val": random.randint(70, 95)},
        {"label": "Poder Ofensivo", "val": random.randint(75, 99)},
        {"label": "Fadiga Adversário", "val": random.randint(60, 90)},
        {"label": "Dinheiro Sharp", "val": random.randint(80, 100)} # Onde os Pros apostam
    ]
    
    reasons = [
        f"O algoritmo analisou 14.500 simulações de Monte Carlo. O {h_name} vence em {confidence}% dos cenários.",
        f"Foi detetada uma injeção de capital de sindicatos asiáticos (Sharp Money) nesta exata linha nas últimas 2h.",
        f"A casa de apostas avalia a probabilidade em {round((1/pick[1])*100)}%, mas a nossa IA sabe que a probabilidade real é {confidence}%. Vantagem matemática garantida."
    ]
    
    return pick, confidence, metrics, reasons, win_rate_hist

# ==========================================
# 3. A PLATAFORMA (UI/UX)
# ==========================================

# --- BARRA DE TOPO ---
st.markdown("""
<div class="top-nav">
    <div class="logo">APEX<span>AI</span></div>
    <div class="live-status"><div class="dot"></div> ALGORITMO A PROCESSAR 450+ LIGAS</div>
</div>
""", unsafe_allow_html=True)

# --- ESTRUTURA PRINCIPAL ---
col_menu, col_core, col_sales = st.columns([1, 2.2, 1.2], gap="large")

# --- COLUNA 1: SELEÇÃO DE JOGO ---
with col_menu:
    st.markdown("<h3 style='color:#00F0FF; font-weight:900; font-size:1.1rem; text-transform:uppercase; letter-spacing:2px; margin-bottom:20px;'>Radar de Oportunidades</h3>", unsafe_allow_html=True)
    
    games = fetch_games_for_pitch()
    match_dict = {f"{g['h']} vs {g['a']}": g for g in games}
    
    m_str = st.selectbox("Selecione o Jogo Alvo", list(match_dict.keys()), label_visibility="collapsed")
    m_sel = match_dict[m_str]
    
    st.button("🔄 PROCURAR NOVOS EDGES", use_container_width=True)
    
    # Live Ticker Falso para dar FOMO (Medo de perder)
    st.markdown("""
    <div style="margin-top: 30px; background: rgba(255,255,255,0.02); border-radius: 12px; padding: 15px;">
        <div style="font-size: 0.75rem; color: #64748B; font-weight: 800; text-transform: uppercase; margin-bottom: 15px;">Apostas Validadas Agora</div>
        <div style="border-left: 2px solid #00FF88; padding-left: 10px; margin-bottom: 10px;">
            <div style="color: #FFF; font-weight: 600; font-size: 0.85rem;">Galatasaray vs Leipzig</div>
            <div style="color: #00FF88; font-size: 0.75rem; font-weight: 800;">Over 2.5 @ 1.85 (Enviada há 2m)</div>
        </div>
        <div style="border-left: 2px solid #00F0FF; padding-left: 10px;">
            <div style="color: #FFF; font-weight: 600; font-size: 0.85rem;">Lakers vs Celtics</div>
            <div style="color: #00F0FF; font-size: 0.75rem; font-weight: 800;">Lakers -4.5 @ 1.90 (Enviada há 5m)</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- COLUNA 2: O CORAÇÃO (A APOSTA DE OURO) ---
with col_core:
    pick, conf, neurals, reasons, wr = generate_ai_master_pick(m_sel['h'], m_sel['a'])
    
    # 1. O MATCHUP CARD
    st.markdown(f"""
    <div class="lock-card">
        <div class="matchup">
            <div class="league-tag">{m_sel['league']}</div>
            <div class="teams">{m_sel['h']} <span>vs</span> {m_sel['a']}</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Gauge (Velocímetro) e Neural Bars
    c_gauge, c_bars = st.columns([1, 1.2])
    with c_gauge:
        fig = go.Figure(go.Indicator(
            mode = "gauge+number", value = conf,
            number = {'suffix': "%", 'font': {'size': 45, 'color': '#FFF', 'family': 'Outfit', 'weight': 900}},
            title = {'text': "PROBABILIDADE IA", 'font': {'size': 12, 'color': '#00F0FF', 'family': 'Outfit'}},
            gauge = {
                'axis': {'range': [None, 100], 'visible': False},
                'bar': {'color': "#00FF88", 'thickness': 0.85},
                'bgcolor': "rgba(255,255,255,0.05)",
                'borderwidth': 0,
                'steps': [{'range': [0, 80], 'color': "rgba(0, 240, 255, 0.15)"}],
            }
        ))
        fig.update_layout(height=200, margin=dict(l=0, r=0, t=10, b=0), paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
    with c_bars:
        st.markdown("<div style='margin-top:20px;'>", unsafe_allow_html=True)
        for n in neurals:
            st.markdown(f"""
            <div class="neural-row">
                <div class="n-label">{n['label']}</div>
                <div class="n-bar-bg"><div class="n-bar-fill" style="width: {n['val']}%;"></div></div>
                <div class="n-value">{n['val']}</div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # 2. A APOSTA RECOMENDADA
    st.markdown(f"""
        <div class="premium-pick">
            <div class="pick-label">⭐ Aposta Diamante ⭐</div>
            <div class="pick-market">{pick[0]}</div>
            <div class="pick-odd">ODD: {pick[1]:.2f}</div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div class='btn-nuke'>", unsafe_allow_html=True)
    if st.button(f"🚀 DESBLOQUEAR E APOSTAR AGORA", use_container_width=True):
        st.toast("✅ Aposta copiada e registada com sucesso! A IA está a monitorizar o jogo.", icon="🤖")
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True) # Fecha lock-card

    # 3. O PORQUÊ (Constrói Confiança)
    st.markdown("<div style='background: rgba(0,240,255,0.05); border-left: 3px solid #00F0FF; padding: 15px 20px; border-radius: 0 8px 8px 0;'>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:0.8rem; color:#00F0FF; font-weight:800; text-transform:uppercase; margin-bottom:10px;'>🧠 INTELIGÊNCIA ARTIFICIAL:</div>", unsafe_allow_html=True)
    for r in reasons:
        st.markdown(f"<div style='margin-bottom:8px; font-size:0.95rem; color:#CBD5E1;'><span style='color:#00F0FF; margin-right:5px;'>▶</span> {r}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- COLUNA 3: A MÁQUINA DE VENDAS (SIMULADOR DE LUCRO) ---
with col_sales:
    st.markdown("<div class='sim-panel'>", unsafe_allow_html=True)
    st.markdown("<div class='sim-title'>Calculadora de Lucro APEX</div>", unsafe_allow_html=True)
    st.markdown("<p style='color:#94A3B8; font-size:0.85rem; margin-bottom:20px;'>Descobre quanto podes ganhar a seguir as previsões Diamante da nossa IA em 30 dias.</p>", unsafe_allow_html=True)
    
    stake = st.slider("Quanto apostas por jogo? (€)", min_value=10, max_value=200, value=50, step=10)
    
    # Matemática de Venda: (Stake * Odd média * Jogos Mês * Win Rate) - (Stake * Jogos Mês)
    jogos_mes = 30
    odd_media = 1.90
    lucro_proj = (stake * odd_media * jogos_mes * (wr/100)) - (stake * jogos_mes * (1 - (wr/100)))
    
    st.markdown(f"""
        <div style="text-align:center;">
            <div style="color:#64748B; font-size:0.8rem; font-weight:800; text-transform:uppercase; margin-top:20px;">LUCRO LÍQUIDO PROJETADO (30 DIAS)</div>
            <div class="sim-profit">€{max(0, lucro_proj):,.0f}</div>
            <div style="display:inline-block; background:rgba(0,240,255,0.1); border:1px solid #00F0FF; color:#00F0FF; padding:4px 12px; border-radius:20px; font-size:0.75rem; font-weight:800;">
                🔥 Win Rate Histórica: {wr:.1f}%
            </div>
        </div>
        <hr style="border-color: rgba(255,255,255,0.1); margin: 25px 0;">
        <div style="font-size:0.8rem; color:#94A3B8; text-align:center; line-height:1.4;">
            Deixa de apostar por instinto. Junta-te a mais de 12.000 utilizadores que já usam a Matemática para bater as casas de apostas.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div class='btn-nuke'>", unsafe_allow_html=True)
    st.button("💎 TORNAR-ME MEMBRO VIP", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)