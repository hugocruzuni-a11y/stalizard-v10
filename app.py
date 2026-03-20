import streamlit as st
import numpy as np
from scipy.stats import poisson
import pandas as pd

# 1. Configuração da Página (Tema Dark Mode Nativo)
st.set_page_config(page_title="STALIZARD V10.1", layout="wide")

# 2. CSS Personalizado para Look Profissional
st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #050505; border-right: 1px solid #1A1A1E; }
    .stMetric { background-color: #0D0D10; border: 1px solid #222; padding: 15px; border-radius: 10px; }
    div.stButton > button { 
        background-color: #00F2FF !important; 
        color: #000 !important; 
        font-weight: bold; 
        border-radius: 8px; 
        border: none;
        transition: 0.3s;
    }
    div.stButton > button:hover { transform: scale(1.02); background-color: #00DDEB !important; }
    .main { background-color: #000000; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR (INPUTS) ---
with st.sidebar:
    st.image("https://img.icons8.com/neon/96/000000/strategy.png", width=80)
    st.title("STALIZARD V10.1")
    st.markdown("---")
    
    st.header("📋 STRATEGIC DATA")
    h_n = st.text_input("HOME", "SPORTING CP").upper()
    a_n = st.text_input("AWAY", "BOAVISTA").upper()
    
    st.header("⚽ GF / GA STATS")
    col_a, col_b = st.columns(2)
    h_gf = col_a.number_input("H-GF", value=14.0)
    h_ga = col_b.number_input("H-GA", value=3.0)
    a_gf = col_a.number_input("A-GF", value=5.0)
    a_ga = col_b.number_input("A-GA", value=11.0)
    
    st.header("💰 MARKET ODDS")
    o1 = st.number_input("Odd 1", value=1.22)
    ox = st.number_input("Odd X", value=6.50)
    o2 = st.number_input("Odd 2", value=13.00)
    obtts = st.number_input("Odd BTTS", value=2.10)
    
    o25 = st.number_input("Odd +2.5", value=1.55)
    u25 = st.number_input("Odd -2.5", value=2.40)
    o35 = st.number_input("Odd +3.5", value=2.35)
    u35 = st.number_input("Odd -3.5", value=1.55)
    
    ha0h = st.number_input("Odd HA0 (H)", value=1.05)
    ha0a = st.number_input("Odd HA0 (A)", value=9.00)
    
    run_btn = st.button("⚡ ANALISAR JOGO")

# --- ÁREA PRINCIPAL (RESULTADOS) ---
if run_btn:
    # Matemática V9.3 / V10
    lh = ((h_gf/5)*(a_ga/5))**0.5 * 1.12
    la = ((a_gf/5)*(h_ga/5))**0.5 * 0.90
    sim_h, sim_a = np.random.poisson(lh, 100000), np.random.poisson(la, 100000)
    tot = sim_h + sim_a
    pv, pe, pd = np.mean(sim_h > sim_a), np.mean(sim_h == sim_a), np.mean(sim_h < sim_a)
    nt = pv + pe + pd
    pv, pe, pd = pv/nt, pe/nt, pd/nt

    st.header(f"🏛️ ANÁLISE: {h_n} vs {a_n}")
    
    # 1. Tabela de Mercados
    mkts = [
        ("1X2: CASA", pv, o1), ("1X2: DRAW", pe, ox), ("1X2: FORA", pd, o2),
        ("BTTS: SIM", np.mean((sim_h>0)&(sim_a>0)), obtts),
        ("HA0: CASA", pv/(pv+pd), ha0h), ("HA0: FORA", pd/(pv+pd), ha0a),
        ("OVER 2.5", np.mean(tot>2.5), o25), ("UNDER 2.5", np.mean(tot<2.5), u25),
        ("OVER 3.5", np.mean(tot>3.5), o35), ("UNDER 3.5", np.mean(tot<3.5), u35)
    ]

    results = []
    for name, prob, bookie in mkts:
        fair = 1/prob if prob > 0 else 0
        edge = (prob * bookie) - 1 if bookie > 0 else -1
        stk = max(0, (edge/(bookie-1)*5)) if bookie > 1 else 0
        results.append({
            "MERCADO": name, "PROB": prob, "FAIR": fair, 
            "BOOKIE": bookie, "EDGE": edge, "STAKE": f"{stk:.1f}%"
        })

    df = pd.DataFrame(results)

    # Estilização da Tabela
    def highlight_edge(s):
        if s > 0.07: return 'background-color: #051F14; color: #00FF95; font-weight: bold'
        if s > 0.03: return 'background-color: #1F1505; color: #FFA500'
        return ''

    st.subheader("📊 OPORTUNIDADES DETETADAS")
    st.dataframe(
        df.style.format({
            "PROB": "{:.1%}", "FAIR": "{:.2f}", 
            "BOOKIE": "{:.2f}", "EDGE": "{:+.1%}"
        }).applymap(highlight_edge, subset=['EDGE']),
        use_container_width=True,
        height=450
    )

    # 2. Cards de Scores Exatos
    st.markdown("---")
    st.subheader("🎯 PLACARES MAIS PROVÁVEIS")
    hp, ap = poisson.pmf(range(6), lh), poisson.pmf(range(6), la)
    mtx = np.outer(hp, ap)
    idx = np.unravel_index(np.argsort(mtx.ravel())[-5:], mtx.shape)
    
    score_cols = st.columns(5)
    for i in range(4, -1, -1):
        with score_cols[4-i]:
            st.metric(
                label=f"SCORE {5-i}", 
                value=f"{idx[0][i]} - {idx[1][i]}", 
                delta=f"{mtx[idx[0][i], idx[1][i]]:.1%}"
            )

else:
    st.info("👈 Abre a barra lateral e insere os dados para começar.")
    st.warning("Dica: No telemóvel, clica no '>' no topo esquerdo para abrir os inputs.")
