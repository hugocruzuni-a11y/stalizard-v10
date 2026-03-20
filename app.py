import streamlit as st
import numpy as np
from scipy.stats import poisson
import pandas as pandas_lib

# 1. Configuração de Interface Profissional
st.set_page_config(page_title="STALIZARD V19 PRO", layout="wide")

# 2. CSS de Alta Fidelidade (Sem sobreposições)
st.markdown("""
    <style>
    .block-container { padding-top: 2rem; max-width: 95%; }
    
    /* Cartões de Secção */
    .quant-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 20px;
    }
    
    /* Labels e Inputs */
    .stNumberInput label, .stTextInput label, .stSelectbox label {
        font-size: 0.7rem !important;
        font-weight: 800 !important;
        color: #475569 !important;
        text-transform: uppercase;
    }
    
    /* Botão de Ação Elite */
    div.stButton > button {
        background: linear-gradient(135deg, #1E293B 0%, #334155 100%);
        color: white !important;
        font-weight: 700;
        border-radius: 6px;
        width: 100%;
        height: 50px;
        border: none;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        transition: 0.3s;
    }
    div.stButton > button:hover { transform: translateY(-2px); box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.2); }
    
    /* Tabela Estilo Bloomberg */
    .stTable { font-size: 0.9rem !important; }
    thead tr th { background-color: #F8FAFC !important; border-bottom: 2px solid #1E293B !important; }
    
    /* Warning de Champions */
    .champions-alert {
        background-color: #FFFBEB;
        border-left: 5px solid #F59E0B;
        padding: 10px;
        color: #92400E;
        font-weight: 600;
        margin-bottom: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER ---
st.markdown("### 🏛️ **STALIZARD** // OMNI-QUANT TERMINAL <span style='font-size:12px; color:#94A3B8'>V19.0 ELITE</span>", unsafe_allow_html=True)
st.markdown("---")

# --- COLUNAS DE TRABALHO ---
col_in, col_out = st.columns([1.1, 2], gap="large")

with col_in:
    # 1. Contexto
    st.markdown("**STRATEGIC CONTEXT**")
    ctx = st.selectbox("", ["Liga (Regular)", "Champions/Taça (Playoff)"], label_visibility="collapsed")
    
    # 2. Equipas
    st.markdown("**TEAMS**")
    c_h, c_a = st.columns(2)
    h_name = c_h.text_input("HOME TEAM", "LEIPZIG")
    a_name = c_a.text_input("AWAY TEAM", "HOFFENHEIM")
    
    # 3. Stats (Em grelha limpa)
    st.markdown("**GF/GA STATS (5-GAME AVG)**")
    cg1, cg2, cg3, cg4 = st.columns(4)
    v_h_gf = cg1.number_input("H-GF", value=8.0)
    v_h_ga = cg2.number_input("H-GA", value=12.0)
    v_a_gf = cg3.number_input("A-GF", value=12.0)
    v_a_ga = cg4.number_input("A-GA", value=10.0)
    
    # 4. Odds Market (Grelha organizada)
    st.markdown("**LIVE MARKET ODDS**")
    o1, ox, o2, ob = st.columns(4)
    m_o1, m_ox, m_o2, m_ob = o1.number_input("1", value=1.88), ox.number_input("X", value=4.00), o2.number_input("2", value=3.35), ob.number_input("BTTS", value=1.32)
    
    o15, o25, o35, hah = st.columns(4)
    m_o15, m_o25, m_o35, m_hah = o15.number_input("+1.5", value=1.10), o25.number_input("+2.5", value=1.33), o35.number_input("+3.5", value=1.78), hah.number_input("DNB-H", value=1.33)

    u15, u25, u35, haa = st.columns(4)
    m_u15, m_u25, m_u35, m_haa = u15.number_input("-1.5", value=4.55), u25.number_input("-2.5", value=2.65), u35.number_input("-3.5", value=1.75), haa.number_input("DNB-A", value=1.85)

    btn = st.button("RUN QUANTITATIVE ENGINE")

# --- PROCESSAMENTO ---
if btn:
    try:
        # Fator Champions / Playoff
        adj_factor = 0.67 if "Champions" in ctx else 1.0
        if adj_factor < 1.0:
            st.markdown(f'<div class="champions-alert">⚠️ FATOR PLAYOFF: Ataque do {a_name} reduzido em 33% para contexto de elite.</div>', unsafe_allow_html=True)
        
        # Matemática Poisson
        lh = ((float(v_h_gf)/5)*(float(v_a_ga)/5))**0.5 * 1.12
        la = ((float(v_a_gf)*adj_factor/5)*(float(v_h_ga)/5))**0.5 * 0.90
        
        sim_h, sim_a = np.random.poisson(lh, 100000), np.random.poisson(la, 100000)
        tot = sim_h + sim_a
        
        ph, px, pa = np.mean(sim_h > sim_a), np.mean(sim_h == sim_a), np.mean(sim_h < sim_a)
        norm = ph + px + pa
        ph, px, pa = ph/norm, px/norm, pa/norm

        with col_out:
            st.markdown(f"#### **ANALYSIS:** {h_name.upper()} v {a_name.upper()}")
            
            raw_data = [
                (f"1X2: {h_name.upper()}", ph, m_o1), ("1X2: DRAW", px, m_ox), (f"1X2: {a_name.upper()}", pa, m_o2),
                ("BTTS: YES", np.mean((sim_h>0)&(sim_a>0)), m_ob),
                ("DNB: HOME", ph/(ph+pa), m_hah), ("DNB: AWAY", pa/(ph+pa), m_haa),
                ("OVER 2.5", np.mean(tot>2.5), m_o25), ("UNDER 2.5", np.mean(tot<2.5), m_u25),
                ("OVER 3.5", np.mean(tot>3.5), m_o35), ("UNDER 3.5", np.mean(tot<3.5), m_u35)
            ]

            processed = []
            for n, p, b in raw_data:
                edge = (p * b) - 1
                stk = max(0, (edge/(b-1)*5)) if b > 1 else 0
                label = "PREMIUM 💎" if edge > 0.08 else "VALUE ✅" if edge > 0 else "---"
                processed.append({
                    "STATUS": label, "MARKET": n, "PROB %": f"{p:.1%}", 
                    "FAIR": f"{1/p:.2f}", "BOOKIE": f"{b:.2f}", 
                    "EDGE %": f"{edge:+.1%}", "STAKE": f"{stk:.1f}%"
                })

            st.table(pandas_lib.DataFrame(processed))

            # Scores Exatos
            st.markdown("**TOP SCORE PREDICTIONS:**")
            hp, ap = poisson.pmf(range(6), lh), poisson.pmf(range(6), la)
            mtx = np.outer(hp, ap)
            idx = np.unravel_index(np.argsort(mtx.ravel())[-5:], mtx.shape)
            
            sc_cols = st.columns(5)
            for i in range(4, -1, -1):
                with sc_cols[4-i]:
                    st.metric(f"{idx[0][i]}-{idx[1][i]}", f"{mtx[idx[0][i], idx[1][i]]:.1%}")

    except Exception as e:
        st.error(f"ENGINE ERROR: {e}")
