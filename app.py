import streamlit as st
import numpy as np
from scipy.stats import poisson
import pandas as pandas_lib

# 1. Configuração de Interface de Alta Performance
st.set_page_config(page_title="STALIZARD V18 PRO", layout="wide")

# 2. CSS "Industrial-Chic" (Alta Densidade e Sofisticação)
st.markdown("""
    <style>
    /* Reset de margens para densidade máxima */
    .block-container { padding-top: 1rem; padding-bottom: 0rem; max-width: 95%; }
    
    /* Estilo de Inputs Minimalista */
    .stNumberInput label, .stTextInput label, .stSelectbox label { 
        font-size: 0.75rem !important; font-weight: 700 !important; color: #64748B !important; margin-bottom: -15px; 
    }
    input { border-radius: 4px !important; border: 1px solid #E2E8F0 !important; height: 32px !important; font-size: 0.9rem !important; }
    
    /* Botão Profissional "Action Blue" */
    div.stButton > button {
        background: #1E293B; color: white !important; font-weight: 700;
        border-radius: 4px; width: 100%; height: 45px; border: none;
        transition: 0.2s; letter-spacing: 1px;
    }
    div.stButton > button:hover { background: #334155; border: 1px solid #00F2FF; }
    
    /* Tabela de Dados Estilo Terminal */
    .stTable { font-size: 0.85rem !important; border-radius: 0px !important; }
    thead tr th { background-color: #F8FAFC !important; color: #475569 !important; font-weight: 800 !important; text-transform: uppercase; border-bottom: 2px solid #E2E8F0 !important; }
    
    /* Status de Valor Sofisticado */
    .edge-gold { color: #B45309; font-weight: 900; }
    .edge-green { color: #15803D; font-weight: 700; }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER ULTRA-LEAN ---
h1, h2 = st.columns([4, 1])
h1.markdown("### 🏛️ **STALIZARD** // OMNI-QUANT TERMINAL <span style='font-size:12px; color:#94A3B8'>V18.0 ELITE</span>", unsafe_allow_html=True)
st.markdown("---")

# --- WORKSPACE ---
col_in, col_out = st.columns([1, 2.2], gap="medium")

with col_in:
    # Contexto e Equipas
    st.caption("STRATEGIC CONTEXT")
    ctx = st.selectbox("", ["Liga (Regular)", "Champions/Taça (Playoff)"], label_visibility="collapsed")
    
    c_h, c_a = st.columns(2)
    h_name = c_h.text_input("HOME", "LEIPZIG")
    a_name = c_a.text_input("AWAY", "HOFFENHEIM")
    
    # Métias Compactas
    st.caption("GF/GA STATS (5-GAME AVG)")
    cg1, cg2, cg3, cg4 = st.columns(4)
    v_h_gf = cg1.number_input("H-GF", value=8.0)
    v_h_ga = cg2.number_input("H-GA", value=12.0)
    v_a_gf = cg3.number_input("A-GF", value=12.0)
    v_a_ga = cg4.number_input("A-GA", value=10.0)
    
    # Odds Grid
    st.caption("LIVE MARKET ODDS")
    o1, ox, o2, ob = st.columns(4)
    m_o1 = o1.number_input("1", value=1.88)
    m_ox = ox.number_input("X", value=4.00)
    m_o2 = o2.number_input("2", value=3.35)
    m_ob = ob.number_input("BTTS", value=1.32)
    
    o15, o25, o35, ha_h = st.columns(4)
    m_o15 = o15.number_input("+1.5", value=1.10)
    m_o25 = o25.number_input("+2.5", value=1.33)
    m_o35 = o35.number_input("+3.5", value=1.78)
    m_ha_h = ha_h.number_input("DNB-H", value=1.33)

    u15, u25, u35, ha_a = st.columns(4)
    m_u15 = u15.number_input("-1.5", value=4.55)
    m_u25 = u25.number_input("-2.5", value=2.65)
    m_u35 = u35.number_input("-3.5", value=1.75)
    m_ha_a = ha_a.number_input("DNB-A", value=1.85)

    btn = st.button("RUN QUANTITATIVE ENGINE")

if btn:
    try:
        # Motor de Cálculo Blindado
        adj_a_gf = float(v_a_gf) * (0.67 if "Champions" in ctx else 1.0)
        
        # Poisson Lambdas
        lh = ((float(v_h_gf)/5)*(float(v_a_ga)/5))**0.5 * 1.12
        la = ((float(adj_a_gf)/5)*(float(v_h_ga)/5))**0.5 * 0.90
        
        sim_h, sim_a = np.random.poisson(lh, 100000), np.random.poisson(la, 100000)
        tot = sim_h + sim_a
        
        ph, px, pa = np.mean(sim_h > sim_a), np.mean(sim_h == sim_a), np.mean(sim_h < sim_a)
        norm = ph + px + pa
        ph, px, pa = ph/norm, px/norm, pa/norm

        with col_out:
            st.markdown(f"#### **ANALYSIS:** {h_name.upper()} v {a_name.upper()}")
            
            # Tabela de Mercados
            raw_mkts = [
                (f"1X2: {h_name.upper()}", ph, m_o1), ("1X2: DRAW", px, m_ox), (f"1X2: {a_name.upper()}", pa, m_o2),
                ("BTTS: YES", np.mean((sim_h>0)&(sim_a>0)), m_ob),
                ("DNB: HOME", ph/(ph+pa), m_ha_h), ("DNB: AWAY", pa/(ph+pa), m_ha_a),
                ("OVER 2.5", np.mean(tot>2.5), m_o25), ("UNDER 2.5", np.mean(tot<2.5), m_u25),
                ("OVER 3.5", np.mean(tot>3.5), m_o35), ("UNDER 3.5", np.mean(tot<3.5), m_u35)
            ]

            data_dump = []
            for n, p, b in raw_mkts:
                edge = (p * b) - 1
                stk = max(0, (edge/(b-1)*5)) if b > 1 else 0
                label = "PREMIUM 💎" if edge > 0.08 else "VALUE ✅" if edge > 0 else "---"
                data_dump.append({
                    "STATUS": label, "MARKET": n, "PROB %": f"{p:.1%}", 
                    "FAIR": f"{1/p:.2f}", "BOOKIE": f"{b:.2f}", 
                    "EDGE %": f"{edge:+.1%}", "STAKE": f"{stk:.1f}%"
                })

            st.table(pandas_lib.DataFrame(data_dump))

            # Scores Horizontais Estilo Ticker
            hp, ap = poisson.pmf(range(6), lh), poisson.pmf(range(6), la)
            mtx = np.outer(hp, ap)
            idx = np.unravel_index(np.argsort(mtx.ravel())[-5:], mtx.shape)
            
            st.markdown("**TOP SCORE PREDICTIONS:**")
            score_cols = st.columns(5)
            for i in range(4, -1, -1):
                with score_cols[4-i]:
                    st.markdown(f"""
                    <div style="background:#F1F5F9; border-left:3px solid #1E293B; padding:5px 10px;">
                        <span style="font-size:14px; font-weight:bold;">{idx[0][i]}-{idx[1][i]}</span><br>
                        <span style="font-size:11px; color:#64748B;">{mtx[idx[0][i], idx[1][i]]:.1%}</span>
                    </div>
                    """, unsafe_allow_html=True)

    except Exception as e: st.error(f"ENGINE ERROR: {e}")
