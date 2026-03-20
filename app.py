import streamlit as st
import numpy as np
from scipy.stats import poisson
import pandas as pd

# 1. Configuração Starline Elite
st.set_page_config(page_title="STARLINE PRO", layout="wide")

# 2. CSS Profissional Adaptável (Mobile First)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;800&display=swap');
    
    .stApp { background-color: #FFFFFF; color: #1E293B; font-family: 'Inter', sans-serif; }
    
    /* Content Padding para Telemóvel */
    .block-container { padding: 1rem 1rem !important; max-width: 100%; }

    /* Inputs Modernos */
    .stNumberInput, .stTextInput, .stSelectbox { 
        background-color: #F8FAFC; 
        border: 1px solid #E2E8F0; 
        border-radius: 8px; 
        margin-bottom: 10px !important;
    }
    
    .stNumberInput label, .stTextInput label, .stSelectbox label {
        font-size: 0.75rem !important; 
        font-weight: 800 !important; 
        color: #475569 !important; 
        text-transform: uppercase;
    }

    /* Botões Adaptáveis */
    .stButton > button {
        width: 100%; 
        border-radius: 8px; 
        height: 3.5em; 
        font-weight: 700;
        text-transform: uppercase;
        border: none;
        transition: 0.3s;
    }
    
    /* Analisar: Verde Starline */
    .btn-run > div > button {
        background: linear-gradient(135deg, #10B981 0%, #059669 100%) !important;
        color: white !important;
    }

    /* Clear: Cinza/Vermelho Suave */
    .btn-clear > div > button {
        background: #F1F5F9 !important;
        color: #64748B !important;
        border: 1px solid #E2E8F0 !important;
    }

    /* Tabela Responsiva */
    .stTable { font-size: 0.85rem !important; overflow-x: auto; display: block; }

    /* Alerta Contexto */
    .ctx-alert {
        padding: 12px; background-color: #FFFBEB; border-left: 4px solid #F59E0B;
        color: #92400E; font-weight: 600; font-size: 0.85rem; border-radius: 8px; margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# Função de Reset
def reset_starline():
    for key in st.session_state.keys():
        del st.session_state[key]

st.markdown("### 🏛️ **STARLINE** // OMNI-QUANT <span style='font-size:12px; color:#94A3B8'>V28.0 PRO</span>", unsafe_allow_html=True)

# --- LAYOUT ADAPTÁVEL ---
# No telemóvel, o Streamlit empilha estas colunas automaticamente
col_in, col_out = st.columns([1, 1.5], gap="medium")

with col_in:
    st.caption("ESTRATÉGICO CONTEXTO")
    ctx = st.selectbox("", ["Liga (Regular)", "Champions/Taça (Playoff)"], key="ctx", label_visibility="collapsed")
    
    h_n_col, a_n_col = st.columns(2)
    h_name = h_n_col.text_input("HOME", value="LEIPZIG", key="h_n").upper()
    a_name = a_n_col.text_input("AWAY", value="HOFFENHEIM", key="a_n").upper()
    
    st.caption("ESTATÍSTICAS GF/GA")
    s1, s2, s3, s4 = st.columns(4) # Em telemóvel isto vira 2x2 ou 1x4
    v_h_gf = s1.number_input("H-GF", value=8.0, key="hgf")
    v_h_ga = s2.number_input("H-GA", value=12.0, key="hga")
    v_a_gf = s3.number_input("A-GF", value=12.0, key="agf")
    v_a_ga = s4.number_input("A-GA", value=10.0, key="aga")
    
    st.caption("MARKET ODDS")
    o1, ox, o2, ob = st.columns(4)
    m_o1, m_ox, m_o2, m_ob = o1.number_input("1", 1.88, key="o1"), ox.number_input("X", 4.00, key="ox"), o2.number_input("2", 3.35, key="o2"), ob.number_input("BTTS", 1.32, key="ob")
    
    o15, o25, o35, hah = st.columns(4)
    m_o15, m_o25, m_o35, m_hah = o15.number_input("+1.5", 1.10, key="o15"), o25.number_input("+2.5", 1.33, key="o25"), o35.number_input("+3.5", 1.78, key="o35"), hah.number_input("DNB-H", 1.33, key="hah")

    u15, u25, u35, haa = st.columns(4)
    m_u15, m_u25, m_u35, m_haa = u15.number_input("-1.5", 4.55, key="u15"), u25.number_input("-2.5", 2.65, key="u25"), u35.number_input("-3.5", 1.75, key="u35"), haa.number_input("DNB-A", 1.85, key="haa")

    # Botões com IDs para CSS
    st.markdown('<div class="btn-run">', unsafe_allow_html=True)
    btn_run = st.button("⚡ ANALISAR AGORA")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="btn-clear">', unsafe_allow_html=True)
    st.button("🗑️ CLEAR DATA", on_click=reset_starline)
    st.markdown('</div>', unsafe_allow_html=True)

# --- PROCESSAMENTO ---
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
                st.markdown(f'<div class="ctx-alert">⚠️ FATOR PLAYOFF: Ataque do {a_name} reduzido em 33%.</div>', unsafe_allow_html=True)
            
            st.subheader(f"📊 REPORT: {h_name} v {a_name}")
            
            mkts = [
                (f"1X2: {h_name}", ph, m_o1), ("1X2: DRAW", px, m_ox), (f"1X2: {a_name}", pa, m_o2),
                ("BTTS: YES", np.mean((sh>0)&(sa>0)), m_ob),
                ("DNB: HOME", ph/(ph+pa), m_hah), ("DNB: AWAY", pa/(ph+pa), m_haa),
                ("OVER 2.5", np.mean(stot>2.5), m_o25), ("UNDER 2.5", np.mean(stot<2.5), m_u25),
                ("OVER 3.5", np.mean(stot>3.5), m_o35), ("UNDER 3.5", np.mean(stot<3.5), m_u35)
            ]

            final_rows, styles = [], []
            for n, p, b in mkts:
                edge = (p * b) - 1
                stk = max(0, (edge/(b-1)*5)) if b > 1 else 0
                bg = "rgba(0, 255, 149, 0.15)" if edge > 0.08 else "rgba(255, 165, 0, 0.15)" if edge > 0 else "none"
                styles.append(bg)
                final_rows.append({"MERCADO": n, "PROB": f"{p:.1%}", "JUSTA": f"{1/p:.2f}", "CASA": f"{b:.2f}", "EDGE": f"{edge:+.1%}", "STAKE": f"{stk:.1f}%"})

            df_res = pd.DataFrame(final_rows)
            st.table(df_res.style.apply(lambda r: [f'background-color: {styles[r.name]}'] * len(r), axis=1))

            st.write("**TOP SCORES**")
            hp, ap = poisson.pmf(range(6), lh), poisson.pmf(range(6), la)
            mtx = np.outer(hp, ap)
            idx = np.unravel_index(np.argsort(mtx.ravel())[-5:], mtx.shape)
            
            # Scores em 1 coluna no telemóvel para melhor leitura
            for j in range(4, -1, -1):
                st.write(f"🎯 **{idx[0][j]} - {idx[1][j]}** → {mtx[idx[0][j], idx[1][j]]:.1%}")

    except Exception as e: st.error(f"Erro: {e}")
