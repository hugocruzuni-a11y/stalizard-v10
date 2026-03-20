import streamlit as st
import numpy as np
from scipy.stats import poisson
import pandas as pd

# 1. Configuração de Página (Compacta)
st.set_page_config(page_title="STALIZARD V17", layout="wide")

# 2. CSS para Redução de Espaços e Alta Densidade
st.markdown("""
    <style>
    .block-container { padding-top: 1rem; padding-bottom: 0rem; }
    div[data-testid="stVerticalBlock"] > div { margin-bottom: -1rem; }
    .stNumberInput label, .stTextInput label { font-size: 0.8rem !important; margin-bottom: -0.5rem; }
    .stNumberInput input { height: 35px !important; font-size: 0.9rem !important; }
    div.stButton > button {
        background: #2563EB; color: white; font-weight: bold;
        height: 2.5em; width: 100%; border-radius: 4px; margin-top: 10px;
    }
    .stTable { font-size: 0.85rem !important; }
    th { background-color: #F1F5F9 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- CABEÇALHO COMPACTO ---
c_t1, c_t2 = st.columns([3, 1])
with c_t1: st.subheader("🏛️ STALIZARD OMNI-QUANT V17")

# --- GRID DE TRABALHO ---
col_left, col_right = st.columns([1.1, 2], gap="small")

with col_left:
    comp_type = st.selectbox("CONTEXTO", ["Liga (Regular)", "Champions/Taça (Playoff)"], label_visibility="collapsed")
    
    # Equipas
    c_h, c_a = st.columns(2)
    h_name = c_h.text_input("CASA", "LEIPZIG")
    a_name = c_a.text_input("FORA", "HOFFENHEIM")
    
    # Médias Compactas
    st.write("**MÉDIAS GF/GA**")
    cg1, cg2, cg3, cg4 = st.columns(4)
    v_h_gf = cg1.number_input("H-GF", value=8.0)
    v_h_ga = cg2.number_input("H-GA", value=12.0)
    v_a_gf = cg3.number_input("A-GF", value=12.0)
    v_a_ga = cg4.number_input("A-GA", value=10.0)
    
    # Odds Compactas
    st.write("**ODDS MERCADO**")
    oc1, oc2, oc3, oc4 = st.columns(4)
    m_o1 = oc1.number_input("1", value=1.88)
    m_ox = oc2.number_input("X", value=4.00)
    m_o2 = oc3.number_input("2", value=3.35)
    m_obtts = oc4.number_input("BTTS", value=1.32)
    
    oc5, oc6, oc7, oc8 = st.columns(4)
    m_o15, m_o25, m_o35, m_ha0h = oc5.number_input("+1.5", value=1.10), oc6.number_input("+2.5", value=1.33), oc7.number_input("+3.5", value=1.78), oc8.number_input("DNB-H", value=1.33)

    oc9, oc10, oc11, oc12 = st.columns(4)
    m_u15, m_u25, m_u35, m_ha0a = oc9.number_input("-1.5", value=4.55), oc10.number_input("-2.5", value=2.65), oc11.number_input("-3.5", value=1.75), oc12.number_input("DNB-A", value=1.85)

    btn_run = st.button("⚡ ANALISAR")

# --- RESULTADOS ALTA DENSIDADE ---
if btn_run:
    try:
        calc_a_gf = float(v_a_gf)
        if comp_type == "Champions/Taça (Playoff)": calc_a_gf = v_a_gf * 0.67

        l_h = ((v_h_gf/5)*(v_a_ga/5))**0.5 * 1.12
        l_a = ((calc_a_gf/5)*(v_h_ga/5))**0.5 * 0.90
        sim_h, sim_a = np.random.poisson(l_h, 100000), np.random.poisson(l_a, 100000)
        s_tot = sim_h + sim_a
        p_h, p_x, p_a = np.mean(sim_h > sim_a), np.mean(sim_h == sim_a), np.mean(sim_h < sim_a)
        norm = p_h + p_x + p_a
        p_h, p_x, p_a = p_h/norm, p_x/norm, p_a/norm

        with col_right:
            st.write(f"**RELATÓRIO: {h_name.upper()} vs {a_name.upper()}**")
            mkts = [
                (f"1X2: {h_name.upper()}", p_h, m_o1), ("1X2: DRAW", p_x, m_ox), (f"1X2: {a_name.upper()}", p_a, m_o2),
                ("BTTS: SIM", np.mean((sim_h>0)&(sim_a>0)), m_obtts), 
                (f"DNB: {h_name.upper()}", p_h/(p_h+p_a), m_ha0h), (f"DNB: {a_name.upper()}", p_a/(p_h+p_a), m_ha0a),
                ("OVER 2.5", np.mean(s_tot>2.5), m_o25), ("UNDER 2.5", np.mean(s_tot<2.5), m_u25),
                ("OVER 3.5", np.mean(s_tot>3.5), m_o35), ("UNDER 3.5", np.mean(s_tot<3.5), m_u35)
            ]

            final_data = []
            for name, prob, bookie in mkts:
                edge = (prob * bookie) - 1
                stk = max(0, (edge/(bookie-1)*5)) if bookie > 1 else 0
                status = "💎" if edge > 0.08 else "✅" if edge > 0 else " "
                final_data.append({"VAL": status, "MERCADO": name, "PROB": f"{prob:.1%}", "JUSTA": f"{1/prob:.2f}", "CASA": f"{bookie:.2f}", "EDGE": f"{edge:+.1%}", "STK": f"{stk:.1f}%"})

            st.table(pd.DataFrame(final_data))

            # Scores Compactos
            hp, ap = poisson.pmf(range(6), l_h), poisson.pmf(range(6), l_a)
            mtx = np.outer(hp, ap)
            idx = np.unravel_index(np.argsort(mtx.ravel())[-5:], mtx.shape)
            
            st.write("**TOP SCORES:**")
            score_line = ""
            for i in range(4, -1, -1):
                score_line += f"| **{idx[0][i]}-{idx[1][i]}** ({mtx[idx[0][i], idx[1][i]]:.1%}) "
            st.markdown(score_line + "|")

    except Exception as e: st.error(f"Erro: {e}")
