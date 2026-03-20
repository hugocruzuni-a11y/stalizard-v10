import streamlit as st
import numpy as np
from scipy.stats import poisson
import pandas as pandas_lib # Renomeado para evitar qualquer conflito

# 1. Configuração de Painel PRO
st.set_page_config(page_title="STALIZARD V14.1 PRO", layout="wide")

# 2. Design Neon e Preto Sólido
st.markdown("""
    <style>
    .main { background-color: #000000; color: #FFFFFF; font-family: 'Inter', sans-serif; }
    [data-testid="stAppViewContainer"] { background-color: #000000; }
    .stNumberInput input { background-color: #000 !important; color: #00F2FF !important; border: 1px solid #333 !important; }
    .stTextInput input { background-color: #000 !important; color: #FFFFFF !important; border: 1px solid #333 !important; }
    div.stButton > button { background: #00F2FF; color: black; font-weight: bold; width: 100%; border-radius: 0; margin-top: 20px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏛️ STALIZARD // OMNI-QUANT PRO V14.1")

# --- CONTAINER DE INPUT ---
col_left, col_right = st.columns([1.2, 2], gap="large")

with col_left:
    st.markdown("### STRATEGIC DATA")
    comp_type = st.selectbox("COMPETITION CONTEXT", ["Liga (Regular)", "Champions/Taça (Playoff)"])
    h_name = st.text_input("HOME TEAM", "RB LEIPZIG").upper()
    a_name = st.text_input("AWAY TEAM", "HOFFENHEIM").upper()
    
    st.markdown("### GF / GA STATS")
    c1, c2, c3, c4 = st.columns(4)
    val_h_gf = c1.number_input("H-GF", value=8.0)
    val_h_ga = c2.number_input("H-GA", value=12.0)
    val_a_gf = c3.number_input("A-GF", value=12.0)
    val_a_ga = c4.number_input("A-GA", value=10.0)
    
    st.markdown("### LIVE MARKET ODDS")
    o_c1, o_c2, o_c3, o_c4 = st.columns(4)
    m_o1, m_ox, m_o2, m_obtts = o_c1.number_input("1", value=1.88), o_c2.number_input("X", value=4.00), o_c3.number_input("2", value=3.35), o_c4.number_input("BTTS", value=1.32)
    
    o_c5, o_c6, o_c7, o_c8 = st.columns(4)
    m_o15, m_o25, m_o35, m_ha0h = o_c5.number_input("+1.5", value=1.10), o_c6.number_input("+2.5", value=1.33), o_c7.number_input("+3.5", value=1.78), o_c8.number_input("HA0-H", value=1.33)

    o_c9, o_c10, o_c11, o_c12 = st.columns(4)
    m_u15, m_u25, m_u35, m_ha0a = o_c9.number_input("-1.5", value=4.55), o_c10.number_input("-2.5", value=2.65), o_c11.number_input("-3.5", value=1.75), o_c12.number_input("HA0-A", value=1.85)

    btn_run = st.button("⚡ RUN QUANT ANALYSIS")

# --- MOTOR PRO V14.1 ---
if btn_run:
    try:
        # Fator Champions
        calc_a_gf = float(val_a_gf)
        if comp_type == "Champions/Taça (Playoff)":
            calc_a_gf = float(val_a_gf) * 0.67
            st.warning("⚠️ Fator Champions: Ataque de fora reduzido em 33%.")

        # Matemática Poisson
        l_h = ((float(val_h_gf)/5)*(float(val_a_ga)/5))**0.5 * 1.12
        l_a = ((float(calc_a_gf)/5)*(float(val_h_ga)/5))**0.5 * 0.90
        
        s_h, s_a = np.random.poisson(l_h, 100000), np.random.poisson(l_a, 100000)
        s_tot = s_h + s_a
        
        prob_h = np.mean(s_h > s_a)
        prob_x = np.mean(s_h == s_a)
        prob_a = np.mean(s_h < s_a)
        norm = prob_h + prob_x + prob_a
        prob_h, prob_x, prob_a = prob_h/norm, prob_x/norm, prob_a/norm

        with col_right:
            st.markdown(f"#### ⚖️ BALANCE: {h_name} vs {a_name}")
            p1, px, p2 = st.columns(3)
            p1.metric("HOME", f"{prob_h:.1%}")
            px.metric("DRAW", f"{prob_x:.1%}")
            p2.metric("AWAY", f"{prob_a:.1%}")
            st.progress(prob_h)

            # Lista de Mercados Completa
            mkts_data = [
                (f"1X2: {h_name}", prob_h, m_o1), ("1X2: DRAW", prob_x, m_ox), (f"1X2: {a_name}", prob_a, m_o2),
                ("BTTS: SIM", np.mean((s_h>0)&(s_a>0)), m_obtts), 
                (f"HA0: {h_name}", prob_h/(prob_h+prob_a), m_ha0h), (f"HA0: {a_name}", prob_a/(prob_h+prob_a), m_ha0a),
                ("OVER 1.5", np.mean(s_tot>1.5), m_o15), ("UNDER 1.5", np.mean(s_tot<1.5), m_u15),
                ("OVER 2.5", np.mean(s_tot>2.5), m_o25), ("UNDER 2.5", np.mean(s_tot<2.5), m_u25),
                ("OVER 3.5", np.mean(s_tot>3.5), m_o35), ("UNDER 3.5", np.mean(s_tot<3.5), m_u35)
            ]

            final_list = []
            for m_name, m_prob, m_bookie in mkts_data:
                m_fair = 1/m_prob if m_prob > 0 else 0
                m_edge = (m_prob * m_bookie) - 1
                m_stk = max(0, (m_edge/(m_bookie-1)*5)) if m_bookie > 1 else 0
                final_list.append({
                    "MARKET": m_name, "PROB": f"{m_prob:.1%}", "FAIR": f"{m_fair:.2f}", 
                    "BOOKIE": f"{m_bookie:.2f}", "EDGE": f"{m_edge:+.1%}", "STAKE": f"{m_stk:.1f}%", "ev": m_edge
                })

            # CRÍTICO: Uso explícito da biblioteca renomeada
            df_final = pandas_lib.DataFrame(final_list)
            
            def apply_style(row):
                c = 'white'
                if row['ev'] > 0.08: c = '#00FF95'
                elif row['ev'] > 0.03: c = '#FFA500'
                return [f'color: {c}'] * len(row)

            st.table(df_final.drop(columns=['ev']).style.apply(apply_style, axis=1))

            st.markdown("---")
            st.subheader("🎯 TOP SCORES")
            hp, ap = poisson.pmf(range(6), l_h), poisson.pmf(range(6), l_a)
            mtx = np.outer(hp, ap)
            idx = np.unravel_index(np.argsort(mtx.ravel())[-5:], mtx.shape)
            for i in range(4, -1, -1):
                st.write(f"**{idx[0][i]} - {idx[1][i]}** | Prob: {mtx[idx[0][i], idx[1][i]]:.1%}")
    
    except Exception as e:
        st.error(f"Erro Crítico: {e}")
