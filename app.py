import streamlit as st
import numpy as np
from scipy.stats import poisson
import pandas as pd

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="STALIZARD V10 // OMNI-QUANT", layout="wide")

# --- ESTILO VISUAL (CSS) ---
st.markdown("""
    <style>
    .main { background-color: #000000; color: #FFFFFF; }
    div.stButton > button {
        background-color: #00F2FF !important;
        color: #000000 !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        width: 100% !important;
    }
    .stNumberInput input { background-color: #0D0D10 !important; color: #00F2FF !important; }
    .stTextInput input { background-color: #0D0D10 !important; color: #FFFFFF !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏛️ STALIZARD // OMNI-MAX WEB V10")

# --- COLUNAS DE INPUT ---
col_in, col_out = st.columns([1, 2], gap="large")

with col_in:
    st.subheader("STRATEGIC DATA")
    h_n = st.text_input("HOME TEAM", "SPORTING CP")
    a_n = st.text_input("AWAY TEAM", "BOAVISTA")
    
    st.markdown("### GF / GA STATS")
    c1, c2, c3, c4 = st.columns(4)
    h_gf = c1.number_input("H-GF", value=14.0)
    h_ga = c2.number_input("H-GA", value=3.0)
    a_gf = c3.number_input("A-GF", value=5.0)
    a_ga = c4.number_input("A-GA", value=11.0)
    
    st.markdown("### LIVE MARKET ODDS")
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

    run_btn = st.button("⚡ RUN QUANT ANALYSIS")

# --- LÓGICA DE CÁLCULO ---
if run_btn:
    # Lambdas (Home Advantage 1.12)
    lh = ((h_gf/5)*(a_ga/5))**0.5 * 1.12
    la = ((a_gf/5)*(h_ga/5))**0.5 * 0.90
    
    sim_h = np.random.poisson(lh, 100000)
    sim_a = np.random.poisson(la, 100000)
    tot = sim_h + sim_a
    
    pv, pe, pd = np.mean(sim_h > sim_a), np.mean(sim_h == sim_a), np.mean(sim_h < sim_a)
    nt = pv + pe + pd
    pv, pe, pd = pv/nt, pe/nt, pd/nt

    # Definição de todos os mercados (12 no total)
    mkts_data = [
        (f"1X2: {h_n.upper()}", pv, o1),
        ("1X2: DRAW", pe, ox),
        (f"1X2: {a_n.upper()}", pd, o2),
        ("BTTS: SIM", np.mean((sim_h>0)&(sim_a>0)), obtts),
        (f"HA0: {h_n.upper()}", pv/(pv+pd), o_ha0h),
        (f"HA0: {a_n.upper()}", pd/(pv+pd), o_ha0a),
        ("OVER 1.5", np.mean(tot>1.5), o_o15),
        ("UNDER 1.5", np.mean(tot<1.5), o_u15),
        ("OVER 2.5", np.mean(tot>2.5), o_o25),
        ("UNDER 2.5", np.mean(tot<2.5), o_u25),
        ("OVER 3.5", np.mean(tot>3.5), o_o35),
        ("UNDER 3.5", np.mean(tot<3.5), o_u35)
    ]

    results = []
    for name, prob, bookie in mkts_data:
        fair = 1/prob
        edge = (prob * bookie) - 1 if bookie > 0 else -1
        stk = max(0, (edge/(bookie-1)*5)) if bookie > 1 else 0
        
        results.append({
            "MARKET": name,
            "PROB": f"{prob:.1%}",
            "FAIR": f"{fair:.2f}",
            "BOOKIE": f"{bookie:.2f}",
            "EDGE": f"{edge:+.1%}",
            "STAKE": f"{stk:.1f}%",
            "val": edge
        })

    with col_out:
        st.subheader("QUANTITATIVE RESULTS")
        df = pd.DataFrame(results)

        # Função de Cores Neon
        def apply_neon(row):
            color = 'white'
            if row['val'] > 0.07: color = '#00FF95' # Verde
            elif row['val'] > 0.03: color = '#FFA500' # Laranja
            return [f'color: {color}'] * len(row)

        st.table(df.drop(columns=['val']).style.apply(apply_neon, axis=1))

        # Top Scores
        st.markdown("---")
        st.subheader("🎯 TOP 5 EXACT SCORES")
        hp, ap = poisson.pmf(range(6), lh), poisson.pmf(range(6), la)
        mtx = np.outer(hp, ap)
        idx = np.unravel_index(np.argsort(mtx.ravel())[-5:], mtx.shape)
        
        sc1, sc2 = st.columns(2)
        for i in range(4, -1, -1):
            sc1.write(f"**{idx[0][i]} - {idx[1][i]}**")
            sc2.write(f"Prob: {mtx[idx[0][i], idx[1][i]]:.1%}")
