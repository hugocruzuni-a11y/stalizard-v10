import streamlit as st
import numpy as np
from scipy.stats import poisson
import pandas as pd

# --- CONFIGURAÇÃO DE ELITE ---
st.set_page_config(page_title="STALIZARD V12 PRO", layout="wide")

# --- CSS CUSTOMIZADO (ULTRA-MODERNO) ---
st.markdown("""
    <style>
    .main { background-color: #050505; color: #FFFFFF; font-family: 'Inter', sans-serif; }
    .stNumberInput input { background-color: #111 !important; color: #00F2FF !important; border: 1px solid #333 !important; border-radius: 5px; }
    .stTextInput input { background-color: #111 !important; color: #FFF !important; border: 1px solid #333 !important; }
    
    /* Botão Neon Animado */
    div.stButton > button {
        background: linear-gradient(90deg, #00F2FF, #0072FF) !important;
        color: black !important;
        font-weight: 900 !important;
        letter-spacing: 1px;
        border-radius: 10px !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(0, 242, 255, 0.3);
        transition: 0.3s;
    }
    div.stButton > button:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(0, 242, 255, 0.5); }
    
    /* Estilo de Tabela Profissional */
    .styled-table { border-radius: 10px; overflow: hidden; }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER ---
st.title("🏛️ STALIZARD // OMNI-QUANT ELITE V12")
st.write("SISTEMA DE ANÁLISE QUANTITATIVA DE ALTA PRECISÃO")

# --- CONTAINER PRINCIPAL ---
with st.container():
    col_left, col_right = st.columns([1.3, 2], gap="large")

    with col_left:
        st.markdown("### 🏟️ DADOS DO EVENTO")
        h_n = st.text_input("EQUIPA DA CASA", "SPORTING CP").upper()
        a_n = st.text_input("EQUIPA DE FORA", "BOAVISTA").upper()
        
        st.markdown("---")
        st.markdown("### 📊 ESTATÍSTICA (GOLOS)")
        c1, c2, c3, c4 = st.columns(4)
        h_gf = c1.number_input("H-GF", value=14.0)
        h_ga = c2.number_input("H-GA", value=3.0)
        a_gf = c3.number_input("A-GF", value=5.0)
        a_ga = c4.number_input("A-GA", value=11.0)
        
        st.markdown("---")
        st.markdown("### 💰 MERCADO (ODDS REAIS)")
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

        run_btn = st.button("⚡ CALCULAR OPORTUNIDADES")

# --- MOTOR DE CÁLCULO V12 ---
if run_btn:
    # Matemática calibrada
    lh = ((h_gf/5)*(a_ga/5))**0.5 * 1.12
    la = ((a_gf/5)*(h_ga/5))**0.5 * 0.90
    sim_h, sim_a = np.random.poisson(lh, 100000), np.random.poisson(la, 100000)
    tot = sim_h + sim_a
    pv, pe, pd = np.mean(sim_h > sim_a), np.mean(sim_h == sim_a), np.mean(sim_h < sim_a)
    nt = pv + pe + pd
    pv, pe, pd = pv/nt, pe/nt, pd/nt

    with col_right:
        # Gráficos de Probabilidade Rápidos
        st.markdown(f"#### ⚖️ EQUILÍBRIO DE FORÇAS")
        p_c1, p_c2, p_c3 = st.columns(3)
        p_c1.metric(h_n, f"{pv:.1%}")
        p_c2.metric("EMPATE", f"{pe:.1%}")
        p_c3.metric(a_n, f"{pd:.1%}")
        
        st.progress(pv) # Barra visual Sporting
        
        # Tabela de Resultados
        mkts_data = [
            (f"1X2: {h_n}", pv, o1), ("1X2: EMPATE", pe, ox), (f"1X2: {a_n}", pd, o2),
            ("BTTS: SIM", np.mean((sim_h>0)&(sim_a>0)), obtts), 
            (f"DNB: {h_n}", pv/(pv+pd), o_ha0h), (f"DNB: {a_n}", pd/(pv+pd), o_ha0a),
            ("OVER 1.5", np.mean(tot>1.5), o_o15), ("UNDER 1.5", np.mean(tot<1.5), o_u15),
            ("OVER 2.5", np.mean(tot>2.5), o_o25), ("UNDER 2.5", np.mean(tot<2.5), o_u25),
            ("OVER 3.5", np.mean(tot>3.5), o_o35), ("UNDER 3.5", np.mean(tot<3.5), o_u35)
        ]

        results = []
        for name, prob, bookie in mkts_data:
            fair = 1/prob if prob > 0 else 0
            edge = (prob * bookie) - 1 if bookie > 0 else -1
            stk = max(0, (edge/(bookie-1)*4)) if bookie > 1 else 0 # Kelly 1/4
            results.append({
                "MARKET": name, "PROB": f"{prob:.1%}", "FAIR": f"{fair:.2f}", 
                "BOOKIE": f"{bookie:.2f}", "EDGE": f"{edge:+.1%}", "STAKE": f"{stk:.1f}%", "val": edge
            })

        df = pd.DataFrame(results)
        
        # Estilização Neon da Tabela
        def style_rows(row):
            if row['val'] > 0.08: return ['background-color: #051F14; color: #00FF95; font-weight: bold'] * len(row)
            if row['val'] > 0.03: return ['background-color: #1F1505; color: #FFA500'] * len(row)
            return [''] * len(row)

        st.table(df.drop(columns=['val']).style.apply(style_rows, axis=1))

        # Placar Exato com Design de Card
        st.markdown("---")
        st.markdown("### 🎯 TOP SCORES PREDICTED")
        hp, ap = poisson.pmf(range(6), lh), poisson.pmf(range(6), la)
        mtx = np.outer(hp, ap)
        idx = np.unravel_index(np.argsort(mtx.ravel())[-5:], mtx.shape)
        
        sc_cols = st.columns(5)
        for i in range(4, -1, -1):
            with sc_cols[4-i]:
                st.markdown(f"""
                <div style="background-color:#111; padding:10px; border-radius:5px; border-bottom: 2px solid #FFD700; text-align:center">
                    <div style="font-size:20px; font-weight:bold">{idx[0][i]} - {idx[1][i]}</div>
                    <div style="color:#888; font-size:12px">{mtx[idx[0][i], idx[1][i]]:.1%}</div>
                </div>
                """, unsafe_allow_html=True)
