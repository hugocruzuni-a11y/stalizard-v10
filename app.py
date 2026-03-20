import streamlit as st
import numpy as np
from scipy.stats import poisson
import pandas as pd

# 1. Configuração de Painel PRO
st.set_page_config(page_title="STALIZARD V15 PRO", layout="wide")

# 2. Design Neon Minimalista
st.markdown("""
    <style>
    .main { background-color: #000000; color: #FFFFFF; font-family: 'Inter', sans-serif; }
    [data-testid="stAppViewContainer"] { background-color: #000000; }
    .stNumberInput input { background-color: #000 !important; color: #00F2FF !important; border: 1px solid #444 !important; }
    .stTextInput input { background-color: #000 !important; color: #FFFFFF !important; border: 1px solid #444 !important; }
    div.stButton > button { background: #00F2FF; color: black; font-weight: bold; width: 100%; border-radius: 5px; height: 3em; margin-top: 20px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏛️ STALIZARD // OMNI-QUANT PRO V15")

col_left, col_right = st.columns([1.2, 2], gap="large")

with col_left:
    st.markdown("### STRATEGIC DATA")
    comp_type = st.selectbox("CONTEXTO", ["Liga (Regular)", "Champions/Taça (Playoff)"])
    h_name = st.text_input("EQUIPA CASA", "RB LEIPZIG").upper()
    a_name = st.text_input("EQUIPA FORA", "HOFFENHEIM").upper()
    
    st.markdown("### GF / GA STATS")
    c1, c2, c3, c4 = st.columns(4)
    v_h_gf = c1.number_input("H-GF", value=8.0)
    v_h_ga = c2.number_input("H-GA", value=12.0)
    v_a_gf = c3.number_input("A-GF", value=12.0)
    v_a_ga = c4.number_input("A-GA", value=10.0)
    
    st.markdown("### LIVE ODDS")
    o_c1, o_c2, o_c3, o_c4 = st.columns(4)
    m_o1, m_ox, m_o2, m_obtts = o_c1.number_input("1", value=1.88), o_c2.number_input("X", value=4.00), o_c3.number_input("2", value=3.35), o_c4.number_input("BTTS", value=1.32)
    
    o_c5, o_c6, o_c7, o_c8 = st.columns(4)
    m_o15, m_o25, m_o35, m_ha0h = o_c5.number_input("+1.5", value=1.10), o_c6.number_input("+2.5", value=1.33), o_c7.number_input("+3.5", value=1.78), o_c8.number_input("DNB-H", value=1.33)

    o_c9, o_c10, o_c11, o_c12 = st.columns(4)
    m_u15, m_u25, m_u35, m_ha0a = o_c9.number_input("-1.5", value=4.55), o_c10.number_input("-2.5", value=2.65), o_c11.number_input("-3.5", value=1.75), o_c12.number_input("DNB-A", value=1.85)

    btn_run = st.button("⚡ CALCULAR AGORA")

if btn_run:
    try:
        # Fator Champions (Ajuste de 33%)
        calc_a_gf = float(v_a_gf)
        if comp_type == "Champions/Taça (Playoff)":
            calc_a_gf = v_a_gf * 0.67
            st.warning("⚠️ Fator Champions Ativo: Ataque Fora reduzido.")

        # Lambdas
        l_h = ((v_h_gf/5)*(v_a_ga/5))**0.5 * 1.12
        l_a = ((calc_a_gf/5)*(v_h_ga/5))**0.5 * 0.90
        
        sim_h, sim_a = np.random.poisson(l_h, 100000), np.random.poisson(l_a, 100000)
        s_tot = sim_h + sim_a
        
        # Probabilidades
        p_h = np.mean(sim_h > sim_a)
        p_x = np.mean(sim_h == sim_a)
        p_a = np.mean(sim_h < sim_a)
        norm = p_h + p_x + p_a
        p_h, p_x, p_a = p_h/norm, p_x/norm, p_a/norm

        with col_right:
            st.subheader(f"📊 RESULTADOS: {h_name} vs {a_name}")
            
            # Dados dos Mercados
            mkts = [
                (f"1X2: {h_name}", p_h, m_o1), ("1X2: DRAW", p_x, m_ox), (f"1X2: {a_name}", p_a, m_o2),
                ("BTTS: SIM", np.mean((sim_h>0)&(sim_a>0)), m_obtts), 
                (f"DNB: {h_name}", p_h/(p_h+p_a), m_ha0h), (f"DNB: {a_name}", p_a/(p_h+p_a), m_ha0a),
                ("OVER 1.5", np.mean(s_tot>1.5), m_o15), ("UNDER 1.5", np.mean(s_tot<1.5), m_u15),
                ("OVER 2.5", np.mean(s_tot>2.5), m_o25), ("UNDER 2.5", np.mean(s_tot<2.5), m_u25),
                ("OVER 3.5", np.mean(s_tot>3.5), m_o35), ("UNDER 3.5", np.mean(s_tot<3.5), m_u35)
            ]

            final_data = []
            for name, prob, bookie in mkts:
                edge = (prob * bookie) - 1
                stake = max(0, (edge/(bookie-1)*5)) if bookie > 1 else 0
                
                # SINALIZADOR DE VALOR (Emoji em vez de cores complexas)
                status = "🚨" if edge > 0.08 else "✅" if edge > 0 else "❌"
                
                final_data.append({
                    "VALUE": status,
                    "MERCADO": name,
                    "PROB": f"{prob:.1%}",
                    "BOOKIE": f"{bookie:.2f}",
                    "EDGE": f"{edge:+.1%}",
                    "STAKE": f"{stake:.1f}%"
                })

            st.table(pd.DataFrame(final_data))

            # Top Scores
            st.markdown("---")
            st.subheader("🎯 TOP 5 SCORES")
            hp, ap = poisson.pmf(range(6), l_h), poisson.pmf(range(6), l_a)
            mtx = np.outer(hp, ap)
            idx = np.unravel_index(np.argsort(mtx.ravel())[-5:], mtx.shape)
            for i in range(4, -1, -1):
                st.write(f"**{idx[0][i]} - {idx[1][i]}** | Probabilidade: {mtx[idx[0][i], idx[1][i]]:.1%}")
    
    except Exception as e:
        st.error(f"Erro no cálculo: {e}")
