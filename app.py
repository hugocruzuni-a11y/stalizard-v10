import streamlit as st
import numpy as np
from scipy.stats import poisson
import pandas as pd

# 1. Configuração de Página para Painel PRO
st.set_page_config(page_title="STALIZARD V14 PRO", layout="wide")

# 2. Design Neon e Preto Sólido
st.markdown("""
    <style>
    .main { background-color: #000000; color: #FFFFFF; font-family: 'Inter', sans-serif; }
    [data-testid="stAppViewContainer"] { background-color: #000000; }
    .stNumberInput input { background-color: #000 !important; color: #00F2FF !important; border: 1px solid #333 !important; }
    .stTextInput input { background-color: #000 !important; color: #FFFFFF !important; border: 1px solid #333 !important; }
    .stSelectbox div[data-baseweb="select"] { background-color: #000 !important; color: #FFFFFF !important; border: 1px solid #333 !important; }
    
    div.stButton > button {
        background: #00F2FF;
        color: black;
        font-weight: bold;
        width: 100%;
        border-radius: 0;
        margin-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🏛️ STALIZARD // OMNI-QUANT PRO V14")

# --- CONTAINER PRINCIPAL ---
col_left, col_right = st.columns([1.2, 2], gap="large")

with col_left:
    st.markdown("### STRATEGIC DATA")
    comp = st.selectbox("COMPETITION CONTEXT", ["Liga (Regular)", "Champions/Taça (Playoff)"])
    h_n = st.text_input("HOME TEAM", "RB LEIPZIG").upper()
    a_n = st.text_input("AWAY TEAM", "HOFFENHEIM").upper()
    
    st.markdown("### GF / GA STATS")
    c1, c2, c3, c4 = st.columns(4)
    h_gf = c1.number_input("H-GF", value=8.0, step=0.5)
    h_ga = c2.number_input("H-GA", value=12.0, step=0.5)
    a_gf_input = c3.number_input("A-GF", value=12.0, step=0.5)
    a_ga = c4.number_input("A-GA", value=10.0, step=0.5)
    
    st.markdown("### LIVE MARKET ODDS")
    o_c1, o_c2, o_c3, o_c4 = st.columns(4)
    o1, ox, o2, obtts = o_c1.number_input("1", value=1.88), o_c2.number_input("X", value=4.00), o_c3.number_input("2", value=3.35), o_c4.number_input("BTTS", value=1.32)
    
    o_c5, o_c6, o_c7, o_c8 = st.columns(4)
    o_o15, o_o25, o_o35, o_ha0h = o_c5.number_input("+1.5", value=1.10), o_c6.number_input("+2.5", value=1.33), o_c7.number_input("+3.5", value=1.78), o_c8.number_input("HA0-H", value=1.33)

    o_c9, o_c10, o_c11, o_c12 = st.columns(4)
    o_u15, o_u25, o_u35, o_ha0a = o_c9.number_input("-1.5", value=4.55), o_c10.number_input("-2.5", value=2.65), o_c11.number_input("-3.5", value=1.75), o_c12.number_input("HA0-A", value=1.85)

    run_btn = st.button("⚡ RUN QUANT ANALYSIS")

# --- MOTOR PRO V14 ---
if run_btn:
    try:
        # APLICAÇÃO DO FILTRO DE COMPETIÇÃO
        a_gf_calc = a_gf_input
        if comp == "Champions/Taça (Playoff)":
            a_gf_calc = a_gf_input * 0.67 # Redução de 33% para ataque de fora em playoff
            st.warning("⚠️ Fator Champions Aplicado: Ataque do Hoffenheim reduzido em 33% por jogar fora num playoff.")

        # Matemática calibrada
        lh = ((float(h_gf)/5)*(float(a_ga)/5))**0.5 * 1.12
        la = ((float(a_gf_calc)/5)*(float(h_ga)/5))**0.5 * 0.90
        
        sim_h, sim_a = np.random.poisson(lh, 100000), np.random.poisson(la, 100000)
        tot = sim_h + sim_a
        
        pv, pe, pd = np.mean(sim_h > sim_a), np.mean(sim_h == sim_a), np.mean(sim_h < sim_a)
        nt = pv + pe + pd
        pv, pe, pd = pv/nt, pe/nt, pd/nt

        with col_right:
            st.markdown(f"#### ⚖️ BALANCE: {h_n} vs {a_n}")
            p_c1, p_c2, p_c3 = st.columns(3)
            p_c1.metric("HOME", f"{pv:.1%}")
            p_c2.metric("DRAW", f"{pe:.1%}")
            p_c3.metric("AWAY", f"{pd:.1%}")
            st.progress(pv)

            # TABELA COMPLETA DE MERCADOS (12)
            mkts_data = [
                (f"1X2: {h_n}", pv, o1), ("1X2: EMPATE", pe, ox), (f"1X2: {a_n}", pd, o2),
                ("BTTS: SIM", np.mean((sim_h>0)&(sim_a>0)), obtts), 
                (f"HA0: {h_n}", pv/(pv+pd), o_ha0h), (f"HA0: {a_n}", pd/(pv+pd), o_ha0a),
                ("OVER 1.5", np.mean(tot>1.5), o_o15), ("UNDER 1.5", np.mean(tot<1.5), o_u15),
                ("OVER 2.5", np.mean(tot>2.5), o_o25), ("UNDER 2.5", np.mean(tot<2.5), o_u25),
                ("OVER 3.5", np.mean(tot>3.5), o_o35), ("UNDER 3.5", np.mean(tot<3.5), o_u35)
            ]

            results_list = []
            for name, prob_v, bookie in mkts_data:
                fair = 1/prob_v if prob_v > 0 else 0
                edge = (prob_v * bookie) - 1 if bookie > 0 else -1
                stk = max(0, (edge/(bookie-1)*5)) if bookie > 1 else 0
                results_list.append({
                    "MARKET": name, "PROB": f"{prob_v:.1%}", "FAIR": f"{fair:.2f}", 
                    "BOOKIE": f"{bookie:.2f}", "EDGE": f"{edge:+.1%}", "STAKE": f"{stk:.1f}%", "val": edge
                })

            df_final = pd.DataFrame(results_list)
            
            # Função de Destaque Neon
            def highlight(row):
                color = 'white'
                if row['val'] > 0.08: color = '#00FF95' # Verde Neon (Valor Alto)
                elif row['val'] > 0.03: color = '#FFA500' # Laranja Ouro (Valor Médio)
                return [f'color: {color}'] * len(row)

            st.table(df_final.drop(columns=['val']).style.apply(highlight, axis=1))

            # Top Scores com Design Vertical
            st.markdown("---")
            st.subheader("🎯 TOP SCORES PREDICTED")
            hp, ap = poisson.pmf(range(6), lh), poisson.pmf(range(6), la)
            mtx = np.outer(hp, ap)
            idx = np.unravel_index(np.argsort(mtx.ravel())[-5:], mtx.shape)
            
            for i in range(4, -1, -1):
                score = f"{idx[0][i]} - {idx[1][i]}"
                prb = f"{mtx[idx[0][i], idx[1][i]]:.1%}"
                st.markdown(f"**{score}** <span style='float:right; color:#FFD700'>{prb}</span>", unsafe_allow_html=True)
    
    except Exception as e:
        st.error(f"Erro no processamento PRO: {e}")
