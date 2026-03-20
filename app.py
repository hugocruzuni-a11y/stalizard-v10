import streamlit as st
import numpy as np
from scipy.stats import poisson
import pandas as pd

# 1. Configuração da Página para Look "Desktop"
st.set_page_config(page_title="STALIZARD V11", layout="wide", initial_sidebar_state="collapsed")

# 2. CSS para emular o layout original (Preto, Neon e Tabelas sólidas)
st.markdown("""
    <style>
    .main { background-color: #000000; color: #FFFFFF; font-family: 'Courier New', Courier, monospace; }
    [data-testid="stAppViewContainer"] { background-color: #000000; }
    
    /* Botão RUN original */
    div.stButton > button {
        background-color: #00F2FF !important;
        color: #000000 !important;
        font-weight: bold !important;
        font-size: 20px !important;
        border-radius: 0px !important;
        height: 3em !important;
        width: 100% !important;
        border: none !important;
        margin-top: 20px;
    }
    
    /* Inputs estilo "Card" */
    .stNumberInput input { background-color: #000000 !important; color: #00F2FF !important; border: 1px solid #333 !important; font-size: 18px !important; }
    .stTextInput input { background-color: #000000 !important; color: #FFFFFF !important; border: 1px solid #333 !important; }
    
    /* Estilo da Tabela para parecer o Treeview do Tkinter */
    .styled-table {
        width: 100%;
        border-collapse: collapse;
        background-color: #0A0A0C;
        color: white;
        font-size: 16px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🏛️ STALIZARD // OMNI-QUANT V11")
st.markdown("---")

# --- LAYOUT EM COLUNAS (Como no original) ---
col_left, col_right = st.columns([1.2, 2], gap="large")

with col_left:
    st.markdown("### 📋 STRATEGIC DATA")
    h_n = st.text_input("HOME TEAM", "SPORTING CP")
    a_n = st.text_input("AWAY TEAM", "BOAVISTA")
    
    st.markdown("### ⚽ GF / GA STATS")
    c1, c2, c3, c4 = st.columns(4)
    h_gf = c1.number_input("H-GF", value=14.0)
    h_ga = c2.number_input("H-GA", value=3.0)
    a_gf = c3.number_input("A-GF", value=5.0)
    a_ga = c4.number_input("A-GA", value=11.0)
    
    st.markdown("### 💰 LIVE MARKET ODDS")
    # Grelha de Odds como no original
    o_c1, o_c2, o_c3, o_c4 = st.columns(4)
    o1 = o_c1.number_input("1", value=1.22)
    ox = o_c2.number_input("X", value=6.50)
    o2 = o_c3.number_input("2", value=13.00)
    obtts = o_c4.number_input("BTTS", value=2.10)
    
    o_c5, o_c6, o_c7, o_c8 = st.columns(4)
    o_o15 = o_c5.number_input("+1.5", value=1.18)
    o_o25 = o_c6.number_input("+2.5", value=1.55)
    o_o35 = o_c7.number_input("+3.5", value=2.35)
    o_ha0h = o_c8.number_input("HA0-H", value=1.05)

    o_c9, o_c10, o_c11, o_c12 = st.columns(4)
    o_u15 = o_c9.number_input("-1.5", value=4.50)
    o_u25 = o_c10.number_input("-2.5", value=2.40)
    o_u35 = o_c11.number_input("-3.5", value=1.55)
    o_ha0a = o_c12.number_input("HA0-A", value=9.00)

    run_btn = st.button("⚡ RUN ANALYSIS")

# --- LÓGICA DE CÁLCULO ---
if run_btn:
    lh = ((h_gf/5)*(a_ga/5))**0.5 * 1.12
    la = ((a_gf/5)*(h_ga/5))**0.5 * 0.90
    sim_h, sim_a = np.random.poisson(lh, 100000), np.random.poisson(la, 100000)
    tot = sim_h + sim_a
    pv, pe, pd = np.mean(sim_h > sim_a), np.mean(sim_h == sim_a), np.mean(sim_h < sim_a)
    nt = pv + pe + pd
    pv, pe, pd = pv/nt, pe/nt, pd/nt

    mkts_data = [
        (f"1X2: {h_n.upper()}", pv, o1), ("1X2: DRAW", pe, ox), (f"1X2: {a_n.upper()}", pd, o2),
        ("BTTS: SIM", np.mean((sim_h>0)&(sim_a>0)), obtts), (f"HA0: {h_n.upper()}", pv/(pv+pd), o_ha0h),
        (f"HA0: {a_n.upper()}", pd/(pv+pd), o_ha0a), ("OVER 1.5", np.mean(tot>1.5), o_o15),
        ("UNDER 1.5", np.mean(tot<1.5), o_u15), ("OVER 2.5", np.mean(tot>2.5), o_o25),
        ("UNDER 2.5", np.mean(tot<2.5), o_u25), ("OVER 3.5", np.mean(tot>3.5), o_o35), ("UNDER 3.5", np.mean(tot<3.5), o_u35)
    ]

    results = []
    for name, prob, bookie in mkts_data:
        fair = 1/prob if prob > 0 else 0
        edge = (prob * bookie) - 1 if bookie > 0 else -1
        stk = max(0, (edge/(bookie-1)*5)) if bookie > 1 else 0
        results.append({
            "MARKET": name, "PROB": f"{prob:.1%}", "FAIR": f"{fair:.2f}", 
            "BOOKIE": f"{bookie:.2f}", "EDGE": f"{edge:+.1%}", "STAKE": f"{stk:.1f}%", "val": edge
        })

    with col_right:
        st.subheader("📊 QUANTITATIVE RESULTS")
        df = pd.DataFrame(results)
        
        # Função de Cores original aplicada à tabela do site
        def highlight_vals(row):
            color = 'white'
            if row['val'] > 0.07: color = '#00FF95'
            elif row['val'] > 0.03: color = '#FFA500'
            return [f'color: {color}'] * len(row)

        st.table(df.drop(columns=['val']).style.apply(highlight_vals, axis=1))

        # Scores Exatos como no original (Lista Vertical)
        st.markdown("---")
        st.subheader("🎯 TOP 5 SCORES")
        hp, ap = poisson.pmf(range(6), lh), poisson.pmf(range(6), la)
        mtx = np.outer(hp, ap)
        idx = np.unravel_index(np.argsort(mtx.ravel())[-5:], mtx.shape)
        
        for i in range(4, -1, -1):
            score = f"{idx[0][i]} - {idx[1][i]}"
            prb = f"{mtx[idx[0][i], idx[1][i]]:.1%}"
            st.markdown(f"**{score}** <span style='float:right; color:#FFD700'>{prb}</span>", unsafe_allow_html=True)
