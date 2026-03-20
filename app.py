import streamlit as st
import numpy as np
from scipy.stats import poisson
import pandas as pd

# 1. Configuração de Página (Simples e Funcional)
st.set_page_config(page_title="STALIZARD V22 PRO", layout="wide")

# 2. CSS Blindado (Sem margens negativas, sem erros de sobreposição)
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; color: #1E293B; }
    .stNumberInput, .stTextInput, .stSelectbox { margin-bottom: 5px !important; }
    
    /* Botão Profissional Azul Escuro */
    div.stButton > button {
        background: #1E293B !important;
        color: white !important;
        font-weight: bold;
        width: 100%;
        border-radius: 4px;
        height: 3em;
        border: none;
        margin-top: 10px;
    }
    
    /* Tabela de Resultados */
    .stTable { background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px; }
    
    /* Alerta de Contexto */
    .ctx-alert {
        padding: 15px;
        background-color: #FFFBEB;
        border-left: 5px solid #F59E0B;
        color: #92400E;
        font-weight: bold;
        margin-bottom: 20px;
        border-radius: 4px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🏛️ STALIZARD // OMNI-QUANT V22")

# --- COLUNAS DE TRABALHO ---
col_in, col_out = st.columns([1.2, 2], gap="large")

with col_in:
    st.subheader("📋 INPUT DATA")
    # Contexto
    ctx_choice = st.selectbox("CONTEXTO DA PARTIDA", ["Liga (Regular)", "Champions/Taça (Playoff)"])
    
    # Equipas
    col_h, col_a = st.columns(2)
    h_name_input = col_h.text_input("HOME TEAM", "LEIPZIG").upper()
    a_name_input = col_a.text_input("AWAY TEAM", "HOFFENHEIM").upper()
    
    # Stats
    st.write("**GF / GA STATS (MÉDIAS)**")
    s1, s2, s3, s4 = st.columns(4)
    v_h_gf = s1.number_input("H-GF", value=8.0)
    v_h_ga = s2.number_input("H-GA", value=12.0)
    v_a_gf = s3.number_input("A-GF", value=12.0)
    v_a_ga = s4.number_input("A-GA", value=10.0)
    
    # Odds
    st.write("**MARKET ODDS (LIVE)**")
    o1, ox, o2, ob = st.columns(4)
    m_o1, m_ox, m_o2, m_obtts = o1.number_input("1", value=1.88), ox.number_input("X", value=4.00), o2.number_input("2", value=3.35), ob.number_input("BTTS", value=1.32)
    
    o15, o25, o35, hah = st.columns(4)
    m_o15, m_o25, m_o35, m_ha0h = o15.number_input("+1.5", value=1.10), o25.number_input("+2.5", value=1.33), o35.number_input("+3.5", value=1.78), hah.number_input("DNB-H", value=1.33)

    u15, u25, u35, haa = st.columns(4)
    m_u15, m_u25, m_u35, m_ha0a = u15.number_input("-1.5", value=4.55), u25.number_input("-2.5", value=2.65), u35.number_input("-3.5", value=1.75), haa.number_input("DNB-A", value=1.85)

    btn_run = st.button("⚡ ANALISAR AGORA")

# --- MOTOR DE CÁLCULO ---
if btn_run:
    try:
        # Fator Champions (Penalização de 33% no ataque fora)
        fator_adj = 0.67 if "Champions" in ctx_choice else 1.0
        
        # Matemática Poisson (Calibrada V15/V20)
        lamb_h = ((v_h_gf/5)*(v_a_ga/5))**0.5 * 1.12
        lamb_a = ((v_a_gf * fator_adj / 5)*(v_h_ga/5))**0.5 * 0.90
        
        # Simulação Monte Carlo
        sh, sa = np.random.poisson(lamb_h, 100000), np.random.poisson(lamb_a, 100000)
        stot = sh + sa
        
        # Probabilidades 1X2
        prob_h = np.mean(sh > sa)
        prob_x = np.mean(sh == sa)
        prob_a = np.mean(sh < sa)
        n_sum = prob_h + prob_x + prob_a
        prob_h, prob_x, prob_a = prob_h/n_sum, prob_x/n_sum, prob_a/n_sum

        with col_out:
            if fator_adj < 1.0:
                st.markdown(f'<div class="ctx-alert">⚠️ FATOR PLAYOFF: Ataque do {a_name_input} reduzido em 33% para contexto Champions/Taça.</div>', unsafe_allow_html=True)
            
            st.subheader(f"📊 REPORT: {h_name_input} v {a_name_input}")
            
            # Lista de Mercados (Fiel ao V15)
            markets_list = [
                (f"1X2: {h_name_input}", prob_h, m_o1), 
                ("1X2: DRAW", prob_x, m_ox), 
                (f"1X2: {a_name_input}", prob_a, m_o2),
                ("BTTS: YES", np.mean((sh>0)&(sa>0)), m_obtts), 
                (f"DNB: {h_name_input}", prob_h/(prob_h+prob_a), m_ha0h), 
                (f"DNB: {a_name_input}", prob_a/(prob_h+prob_a), m_ha0a),
                ("OVER 1.5", np.mean(stot>1.5), m_o15), 
                ("UNDER 1.5", np.mean(stot<1.5), m_u15),
                ("OVER 2.5", np.mean(stot>2.5), m_o25), 
                ("UNDER 2.5", np.mean(stot<2.5), m_u25),
                ("OVER 3.5", np.mean(stot>3.5), m_o35), 
                ("UNDER 3.5", np.mean(stot<3.5), m_u35)
            ]

            final_rows = []
            for name, p, b in markets_list:
                edge_val = (p * b) - 1
                stk_val = max(0, (edge_val/(b-1)*5)) if b > 1 else 0
                status_label = "PREMIUM 💎" if edge_val > 0.08 else "VALUE ✅" if edge_val > 0 else "---"
                
                final_rows.append({
                    "STATUS": status_label, "MARKET": name, "PROB %": f"{p:.1%}", 
                    "FAIR": f"{1/p:.2f}", "BOOKIE": f"{b:.2f}", 
                    "EDGE %": f"{edge_val:+.1%}", "STAKE": f"{stk_val:.1f}%", "ev": edge_val
                })

            df_res = pd.DataFrame(final_rows)

            # --- APLICAÇÃO DE CORES (VERDE / LARANJA) ---
            def color_rows(row):
                if row['ev'] > 0.08: return ['color: #15803D; font-weight: bold'] * len(row) # Verde Escuro PRO
                if row['ev'] > 0: return ['color: #B45309; font-weight: bold'] * len(row) # Laranja Escuro PRO
                return [''] * len(row)

            st.table(df_res.drop(columns=['ev']).style.apply(color_rows, axis=1))

            # Scores Exatos
            st.markdown("---")
            st.write("**PROBABLE SCORES (TOP 5):**")
            hp, ap = poisson.pmf(range(6), lamb_h), poisson.pmf(range(6), lamb_a)
            score_mtx = np.outer(hp, ap)
            idx_scores = np.unravel_index(np.argsort(score_mtx.ravel())[-5:], score_mtx.shape)
            
            sc_cols = st.columns(5)
            for j in range(4, -1, -1):
                with sc_cols[4-j]:
                    st.metric(f"{idx_scores[0][j]} - {idx_scores[1][j]}", f"{score_mtx[idx_scores[0][j], idx_scores[1][j]]:.1%}")

    except Exception as e:
        st.error(f"ENGINE ERROR: {e}")
