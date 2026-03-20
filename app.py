import streamlit as st
import numpy as np
from scipy.stats import poisson
import pandas as pd

# 1. Configuração de Página
st.set_page_config(page_title="STALIZARD V23 PRO", layout="wide")

# 2. CSS Estável
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; color: #1E293B; }
    div.stButton > button {
        background: #1E293B !important;
        color: white !important;
        font-weight: bold;
        width: 100%;
        border-radius: 4px;
        height: 3em;
        margin-top: 10px;
    }
    .ctx-alert {
        padding: 15px; background-color: #FFFBEB; border-left: 5px solid #F59E0B;
        color: #92400E; font-weight: bold; margin-bottom: 20px; border-radius: 4px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🏛️ STALIZARD // OMNI-QUANT V23")

# --- COLUNAS ---
col_in, col_out = st.columns([1.2, 2], gap="large")

with col_in:
    st.subheader("📋 DADOS DE ENTRADA")
    ctx_choice = st.selectbox("CONTEXTO", ["Liga (Regular)", "Champions/Taça (Playoff)"])
    
    c_h, c_a = st.columns(2)
    h_name = c_h.text_input("HOME TEAM", "LEIPZIG").upper()
    a_name = c_a.text_input("AWAY TEAM", "HOFFENHEIM").upper()
    
    st.write("**GF / GA STATS**")
    s1, s2, s3, s4 = st.columns(4)
    v_h_gf, v_h_ga, v_a_gf, v_a_ga = s1.number_input("H-GF", value=8.0), s2.number_input("H-GA", value=12.0), s3.number_input("A-GF", value=12.0), s4.number_input("A-GA", value=10.0)
    
    st.write("**MARKET ODDS**")
    o1, ox, o2, ob = st.columns(4)
    m_o1, m_ox, m_o2, m_ob = o1.number_input("1", value=1.88), ox.number_input("X", value=4.00), o2.number_input("2", value=3.35), ob.number_input("BTTS", value=1.32)
    
    o15, o25, o35, hah = st.columns(4)
    m_o15, m_o25, m_o35, m_ha0h = o15.number_input("+1.5", value=1.10), o25.number_input("+2.5", value=1.33), o35.number_input("+3.5", value=1.78), hah.number_input("DNB-H", value=1.33)

    u15, u25, u35, haa = st.columns(4)
    m_u15, m_u25, m_u35, m_ha0a = u15.number_input("-1.5", value=4.55), u25.number_input("-2.5", value=2.65), u35.number_input("-3.5", value=1.75), haa.number_input("DNB-A", value=1.85)

    btn_run = st.button("⚡ ANALISAR AGORA")

# --- LÓGICA ---
if btn_run:
    try:
        adj = 0.67 if "Champions" in ctx_choice else 1.0
        lh = ((v_h_gf/5)*(v_a_ga/5))**0.5 * 1.12
        la = ((v_a_gf * adj / 5)*(v_h_ga/5))**0.5 * 0.90
        
        sh, sa = np.random.poisson(lh, 100000), np.random.poisson(la, 100000)
        stot = sh + sa
        ph, px, pa = np.mean(sh > sa), np.mean(sh == sa), np.mean(sh < sa)
        norm = ph + px + pa
        ph, px, pa = ph/norm, px/norm, pa/norm

        with col_out:
            if adj < 1.0:
                st.markdown(f'<div class="ctx-alert">⚠️ FATOR PLAYOFF: Ataque do {a_name} reduzido em 33%.</div>', unsafe_allow_html=True)
            
            st.subheader(f"📊 REPORT: {h_name} v {a_name}")
            
            mkts = [
                (f"1X2: {h_name}", ph, m_o1), ("1X2: DRAW", px, m_ox), (f"1X2: {a_name}", pa, m_o2),
                ("BTTS: YES", np.mean((sh>0)&(sa>0)), m_ob),
                (f"DNB: {h_name}", ph/(ph+pa), m_ha0h), (f"DNB: {a_name}", pa/(ph+pa), m_ha0a),
                ("OVER 2.5", np.mean(stot>2.5), m_o25), ("UNDER 2.5", np.mean(stot<2.5), m_u25),
                ("OVER 3.5", np.mean(stot>3.5), m_o35), ("UNDER 3.5", np.mean(stot<3.5), m_u35)
            ]

            # CONSTRUÇÃO DA TABELA SEM COLUNA 'EV' ESCONDIDA (Para evitar erro 'ev')
            data = []
            for n, p, b in mkts:
                edge = (p * b) - 1
                stk = max(0, (edge/(b-1)*5)) if b > 1 else 0
                
                # Definir a cor diretamente como uma string
                color = "none"
                if edge > 0.08: color = "rgba(0, 255, 149, 0.2)" # Verde suave
                elif edge > 0: color = "rgba(255, 165, 0, 0.2)"  # Laranja suave
                
                data.append({
                    "MERCADO": n, "PROB": f"{p:.1%}", "JUSTA": f"{1/p:.2f}", 
                    "CASA": f"{b:.2f}", "EDGE": f"{edge:+.1%}", "STAKE": f"{stk:.1f}%",
                    "_bg_color": color # Coluna interna de cor
                })

            df = pd.DataFrame(data)

            # --- NOVA FUNÇÃO DE COR BLINDADA ---
            def apply_bg(row):
                return [f'background-color: {row["_bg_color"]}'] * len(row)

            # Exibir tabela (Escondendo a coluna técnica de cor)
            st.table(df.style.apply(apply_bg, axis=1).hide(axis='columns', subset=['_bg_color']))

            st.markdown("---")
            st.write("**TOP 5 PLACARES EXATOS:**")
            hp, ap = poisson.pmf(range(6), lh), poisson.pmf(range(6), la)
            mtx = np.outer(hp, ap)
            idx = np.unravel_index(np.argsort(mtx.ravel())[-5:], mtx.shape)
            scs = st.columns(5)
            for j in range(4, -1, -1):
                with scs[4-j]: st.metric(f"{idx[0][j]} - {idx[1][j]}", f"{mtx[idx[0][j], idx[1][j]]:.1%}")

    except Exception as e:
        st.error(f"ENGINE ERROR: {e}")
