import streamlit as st
import numpy as np
from scipy.stats import poisson
import pandas as pd

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="STALIZARD V10 // OMNI-QUANT", layout="wide", initial_sidebar_state="collapsed")

# --- ESTILO VISUAL NEON (CSS) ---
st.markdown("""
    <style>
    .main { background-color: #000000; color: #FFFFFF; }
    div.stButton > button {
        background-color: #00F2FF !important;
        color: #000000 !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        height: 3em !important;
        width: 100% !important;
        border: none !important;
    }
    .stNumberInput input { background-color: #0D0D10 !important; color: #00F2FF !important; font-size: 20px !important; }
    .stTextInput input { background-color: #0D0D10 !important; color: #FFFFFF !important; }
    h1, h2, h3 { color: #00F2FF !important; font-family: 'Courier New', Courier, monospace; }
    .css-12w0qpk { border: 1px solid #1A1A1E !important; border-radius: 10px !important; padding: 20px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- TÍTULO PRINCIPAL ---
st.title("🏛️ STALIZARD // OMNI-MAX WEB V10")
st.markdown("---")

# --- LAYOUT DE COLUNAS ---
col_in, col_out = st.columns([1, 1.8], gap="large")

with col_in:
    st.subheader("STRATEGIC DATA")
    h_n = st.text_input("HOME TEAM", "SPORTING CP")
    a_n = st.text_input("AWAY TEAM", "BOAVISTA")
    
    st.markdown("### GF / GA STATS")
    c1, c2 = st.columns(2)
    h_gf = c1.number_input("H-GF (Marcados)", value=14.0, step=0.5)
    h_ga = c2.number_input("H-GA (Sofridos)", value=3.0, step=0.5)
    
    c3, c4 = st.columns(2)
    a_gf = c3.number_input("A-GF (Marcados)", value=5.0, step=0.5)
    a_ga = c4.number_input("A-GA (Sofridos)", value=11.0, step=0.5)
    
    st.markdown("### LIVE MARKET ODDS")
    o_c1, o_c2, o_c3 = st.columns(3)
    o1 = o_c1.number_input("1 (Casa)", value=1.22)
    ox = o_c2.number_input("X (Empate)", value=6.50)
    o2 = o_c3.number_input("2 (Fora)", value=13.00)
    
    o_c4, o_c5, o_c6 = st.columns(3)
    obtts = o_c4.number_input("BTTS (Sim)", value=2.10)
    o25 = o_c5.number_input("+2.5 Golos", value=1.55)
    o35 = o_c6.number_input("+3.5 Golos", value=2.35)

    run_btn = st.button("⚡ RUN QUANT ANALYSIS")

# --- LOGICA MATEMÁTICA ---
if run_btn:
    try:
        # Cálculo de Lambdas (Médias Expectáveis) com Home Advantage de 1.12
        lh = ((h_gf/5)*(a_ga/5))**0.5 * 1.12
        la = ((a_gf/5)*(h_ga/5))**0.5 * 0.90
        
        # Simulação Monte Carlo (100.000 iterações para velocidade web)
        sim_h = np.random.poisson(lh, 100000)
        sim_a = np.random.poisson(la, 100000)
        tot = sim_h + sim_a
        
        pv, pe, pd = np.mean(sim_h > sim_a), np.mean(sim_h == sim_a), np.mean(sim_h < sim_a)
        
        # Lista de Mercados para Processar
        mkts_raw = [
            (f"1X2: {h_n.upper()}", pv, o1),
            ("1X2: DRAW", pe, ox),
            (f"1X2: {a_n.upper()}", pd, o2),
            ("BTTS: SIM", np.mean((sim_h>0)&(sim_a>0)), obtts),
            ("OVER 2.5", np.mean(tot>2.5), o25),
            ("OVER 3.5", np.mean(tot>3.5), o35)
        ]
        
        results = []
        for name, prob, bookie in mkts_raw:
            fair = 1/prob
            edge = (prob * bookie) - 1
            # Kelly Fracionado (1/4) para segurança de banca
            stk = max(0, (edge/(bookie-1)*5)) if bookie > 1 else 0
            
            results.append({
                "MARKET": name,
                "PROB": f"{prob:.1%}",
                "FAIR": f"{fair:.2f}",
                "BOOKIE": f"{bookie:.2f}",
                "EDGE": f"{edge:+.1%}",
                "STAKE": f"{stk:.1f}%",
                "raw_edge": edge
            })

        with col_out:
            st.subheader("QUANTITATIVE RESULTS")
            
            # Criar DataFrame e aplicar cores
            df = pd.DataFrame(results)
            
            def color_edge(val):
                edge_val = float(val.replace('%', '').replace('+', '')) / 100
                if edge_val > 0.07: return 'color: #00FF95; font-weight: bold' # Verde Neon
                if edge_val > 0.03: return 'color: #FFA500; font-weight: bold' # Laranja Ouro
                return 'color: white'

            st.table(df.drop(columns=['raw_edge']).style.applymap(color_edge, subset=['EDGE']))
            
            # --- TOP SCORES ---
            st.markdown("---")
            st.subheader("🎯 TOP 5 EXACT SCORES")
            hp, ap = poisson.pmf(range(6), lh), poisson.pmf(range(6), la)
            mtx = np.outer(hp, ap)
            idx = np.unravel_index(np.argsort(mtx.ravel())[-5:], mtx.shape)
            
            s_col1, s_col2 = st.columns(2)
            for i in range(4, -1, -1):
                score_str = f"{idx[0][i]} - {idx[1][i]}"
                prob_str = f"{mtx[idx[0][i], idx[1][i]]:.1%}"
                s_col1.write(f"**{score_str}**")
                s_col2.write(f"Probabilidade: {prob_str}")

    except Exception as e:
        st.error(f"Erro nos dados: {e}")

else:
    with col_out:
        st.info("Insere os dados à esquerda e clica em RUN para veres a análise quântica.")