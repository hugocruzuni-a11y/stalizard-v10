import streamlit as st
import numpy as np
from scipy.stats import poisson
import pandas as pd

# 1. Configuração Starline
st.set_page_config(page_title="STARLINE PRO", layout="wide")

# 2. CSS Estável
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; color: #1E293B; }
    div.stButton > button {
        font-weight: bold; width: 100%; border-radius: 4px; height: 3em; border: none;
    }
    .btn-run > div > button { background: #1E293B !important; color: white !important; }
    .btn-clear > div > button { background: #F1F5F9 !important; color: #64748B !important; border: 1px solid #E2E8F0 !important; }
    
    .ctx-alert {
        padding: 15px; background-color: #FFFBEB; border-left: 5px solid #F59E0B;
        color: #92400E; font-weight: bold; margin-bottom: 20px; border-radius: 4px;
    }
    </style>
    """, unsafe_allow_html=True)

# FUNÇÃO DE RESET CORRIGIDA (Sem erro de no-op)
def reset_data():
    for key in st.session_state.keys():
        del st.session_state[key]

st.title("🏛️ STARLINE // OMNI-QUANT")

# --- COLUNAS ---
col_in, col_out = st.columns([1.2, 2], gap="large")

with col_in:
    st.subheader("📋 DADOS DE ENTRADA")
    
    ctx = st.selectbox("CONTEXTO", ["Liga (Regular)", "Champions/Taça (Playoff)"], key="ctx")
    
    c_h, c_a = st.columns(2)
    h_name = c_h.text_input("HOME TEAM", value="LEIPZIG", key="h_n").upper()
    a_name = c_a.text_input("AWAY TEAM", value="HOFFENHEIM", key="a_n").upper()
    
    st.write("**ESTATÍSTICAS (ÚLTIMOS 5 JOGOS)**")
    s1, s2, s3, s4 = st.columns(4)
    v_h_gf = s1.number_input("H-GF", value=8.0, key="hgf")
    v_h_ga = s2.number_input("H-GA", value=12.0, key="hga")
    v_a_gf = s3.number_input("A-GF", value=12.0, key="agf")
    v_a_ga = s4.number_input("A-GA", value=10.0, key="aga")
    
    st.write("**LIVE ODDS**")
    o_c1, o_c2, o_c3, o_c4 = st.columns(4)
    m_o1 = o_c1.number_input("1", value=1.88, key="o1")
    m_ox = o_c2.number_input("X", value=4.00, key="ox")
    m_o2 = o_c3.number_input("2", value=3.35, key="o2")
    m_ob = o_c4.number_input("BTTS", value=1.32, key="ob")
    
    o_c5, o_c6, o_c7, o_c8 = st.columns(4)
    m_o15, m_o25, m_o35, m_hah = o_c5.number_input("+1.5", value=1.10, key="o15"), o_c6.number_input("+2.5", value=1.33, key="o25"), o_c7.number_input("+3.5", value=1.78, key="o35"), o_c8.number_input("DNB-H", value=1.33, key="hah")

    o_c9, o_c10, o_c11, o_c12 = st.columns(4)
    m_u15, m_u25, m_u35, m_haa = o_c9.number_input("-1.5", value=4.55, key="u15"), o_c10.number_input("-2.5", value=2.65, key="u25"), o_c11.number_input("-3.5", value=1.75, key="u35"), o_c12.number_input("DNB-A", value=1.85, key="haa")

    # Botões
    c_btn1, c_btn2 = st.columns(2)
    with c_btn1:
        st.markdown('<div class="btn-run">', unsafe_allow_html=True)
        btn_run = st.button("⚡ ANALISAR")
        st.markdown('</div>', unsafe_allow_html=True)
    with c_btn2:
        st.markdown('<div class="btn-clear">', unsafe_allow_html=True)
        # O botão CLEAR agora apenas limpa o estado, o Streamlit recarrega sozinho
        st.button("🗑️ CLEAR", on_click=reset_data)
        st.markdown('</div>', unsafe_allow_html=True)

# --- RESULTADOS ---
if btn_run:
    try:
        adj = 0.67 if "Champions" in ctx else 1.0
        lh = ((v_h_gf/5) * (v_a_ga/5))**0.5
        la = ((v_a_gf * adj / 5) * (v_h_ga/5))**0.5
        
        sh, sa = np.random.poisson(lh, 100000), np.random.poisson(la, 100000)
        stot = sh + sa
        ph, px, pa = np.mean(sh > sa), np.mean(sh == sa), np.mean(sh < sa)
        norm = ph + px + pa
        ph, px, pa = ph/norm, px/norm, pa/norm

        with col_out:
            if adj < 1.0:
                st.markdown(f'<div class="ctx-alert">⚠️ MODO CHAMPIONS: Ataque do {a_name} reduzido em 33%.</div>', unsafe_allow_html=True)
            
            st.subheader(f"📊 REPORT: {h_name} v {a_name}")
            
            mkts = [
                (f"1X2: {h_name}", ph, m_o1), ("1X2: DRAW", px, m_ox), (f"1X2: {a_name}", pa, m_o2),
                ("BTTS: YES", np.mean((sh>0)&(sa>0)), m_ob), 
                (f"DNB: {h_name}", ph/(ph+pa), m_hah), (f"DNB: {a_name}", pa/(ph+pa), m_haa),
                ("OVER 1.5", np.mean(stot>1.5), m_o15), ("UNDER 1.5", np.mean(stot<1.5), m_u15),
                ("OVER 2.5", np.mean(stot>2.5), m_o25), ("UNDER 2.5", np.mean(stot<2.5), m_u25),
                ("OVER 3.5", np.mean(stot>3.5), m_o35), ("UNDER 3.5", np.mean(stot<3.5), m_u35)
            ]

            data_list, colors = [], []
            for n, p, b in mkts:
                edge = (p * b) - 1
                stk = max(0, (edge/(b-1)*5)) if b > 1 else 0
                bg = "rgba(0, 255, 149, 0.2)" if edge > 0.08 else "rgba(255, 165, 0, 0.2)" if edge > 0 else "none"
                colors.append(bg)
                data_list.append({"MERCADO": n, "PROB": f"{p:.1%}", "JUSTA": f"{1/p:.2f}", "CASA": f"{b:.2f}", "EDGE": f"{edge:+.1%}", "STAKE": f"{stk:.1f}%"})

            df = pd.DataFrame(data_list)
            st.table(df.style.apply(lambda r: [f'background-color: {colors[r.name]}'] * len(r), axis=1))

            st.markdown("---")
            st.write("**TOP 5 PLACARES EXATOS:**")
            hp, ap = poisson.pmf(range(6), lh), poisson.pmf(range(6), la)
            mtx = np.outer(hp, ap)
            idx = np.unravel_index(np.argsort(mtx.ravel())[-5:], mtx.shape)
            scs = st.columns(5)
            for j in range(4, -1, -1):
                with scs[4-j]: st.metric(f"{idx[0][j]} - {idx[1][j]}", f"{mtx[idx[0][j], idx[1][j]]:.1%}")

    except Exception as e: st.error(f"Erro: {e}")
