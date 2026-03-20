import streamlit as st
import numpy as np
from scipy.stats import poisson
import pandas as pd

# 1. Configuração Starline Elite (Foco Desktop)
st.set_page_config(page_title="STARLINE PRO", layout="wide")

# 2. CSS de Alta Performance para Macbook (Sem sobreposições)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;800&display=swap');
    
    /* Global - Fundo Branco */
    .stApp { background-color: #FFFFFF; color: #1E293B; font-family: 'Inter', sans-serif; }
    
    /* Margens do Contentor Principal */
    .block-container { padding-top: 2rem; max-width: 95%; }

    /* Inputs Estilizados (Estilo Bloomberg) */
    .stNumberInput, .stTextInput, .stSelectbox { 
        background-color: #F8FAFC; 
        border: 1px solid #E2E8F0; 
        border-radius: 6px; 
        margin-bottom: 15px !important;
        padding: 2px;
    }
    
    .stNumberInput label, .stTextInput label, .stSelectbox label {
        font-size: 0.7rem !important; 
        font-weight: 800 !important; 
        color: #475569 !important; 
        text-transform: uppercase;
        margin-bottom: 5px !important;
    }

    /* Botões Coloridos Starline */
    .btn-run > div > button {
        background: linear-gradient(135deg, #10B981 0%, #059669 100%) !important;
        color: white !important;
        font-weight: 700; border-radius: 6px; height: 3.5em; width: 100%; border: none;
        text-transform: uppercase; transition: 0.3s;
    }
    
    .btn-clear > div > button {
        background: linear-gradient(135deg, #F87171 0%, #EF4444 100%) !important;
        color: white !important;
        font-weight: 700; border-radius: 6px; height: 3.5em; width: 100%; border: none;
        text-transform: uppercase; transition: 0.3s;
    }

    /* Tabela Heatmap */
    .stTable { font-size: 0.85rem !important; border-radius: 8px !important; overflow: hidden; border: 1px solid #E2E8F0; }
    thead tr th { background-color: #F8FAFC !important; border-bottom: 2px solid #E2E8F0 !important; font-weight: 800 !important; }

    /* Alerta Champions */
    .ctx-alert {
        padding: 15px; background-color: #FFFBEB; border-left: 5px solid #F59E0B;
        color: #92400E; font-weight: 600; border-radius: 8px; margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# Função de Reset Blindada
def reset_starline():
    for key in st.session_state.keys():
        del st.session_state[key]

# Título Starline
st.markdown("### 🏛️ **STARLINE** // OMNI-QUANT <span style='font-size:12px; color:#94A3B8'>V29.0 MAC-ELITE</span>", unsafe_allow_html=True)
st.markdown("---")

# --- WORKSPACE ---
col_in, col_out = st.columns([1.2, 2], gap="large")

with col_in:
    # Contexto e Equipas
    st.caption("CONTEXTO ESTRATÉGICO")
    ctx = st.selectbox("", ["Liga (Regular)", "Champions/Taça (Playoff)"], key="ctx", label_visibility="collapsed")
    
    c_h, c_a = st.columns(2)
    h_name = c_h.text_input("HOME TEAM", value="LEIPZIG", key="h_n").upper()
    a_name = c_a.text_input("AWAY TEAM", value="HOFFENHEIM", key="a_n").upper()
    
    # Estatísticas
    st.caption("GF/GA STATS (5-GAME AVG)")
    s1, s2, s3, s4 = st.columns(4)
    v_h_gf = s1.number_input("H-GF", value=8.0, key="hgf")
    v_h_ga = s2.number_input("H-GA", value=12.0, key="hga")
    v_a_gf = s3.number_input("A-GF", value=12.0, key="agf")
    v_a_ga = s4.number_input("A-GA", value=10.0, key="aga")
    
    # Odds Grid
    st.caption("MARKET ODDS (LIVE)")
    o1, ox, o2, ob = st.columns(4)
    m_o1, m_ox, m_o2, m_ob = o1.number_input("1", 1.88, key="o1"), ox.number_input("X", 4.00, key="ox"), o2.number_input("2", 3.35, key="o2"), ob.number_input("BTTS", 1.32, key="ob")
    
    o15, o25, o35, hah = st.columns(4)
    m_o15, m_o25, m_o35, m_hah = o15.number_input("+1.5", 1.10, key="o15"), o25.number_input("+2.5", 1.33, key="o25"), o35.number_input("+3.5", 1.78, key="o35"), hah.number_input("DNB-H", 1.33, key="hah")

    u15, u25, u35, haa = st.columns(4)
    m_u15, m_u25, m_u35, m_haa = u15.number_input("-1.5", 4.55, key="u15"), u25.number_input("-2.5", 2.65, key="u25"), u35.number_input("-3.5", 1.75, key="u35"), haa.number_input("DNB-A", 1.85, key="haa")

    # Botões Alinhados
    st.markdown('<div class="btn-run">', unsafe_allow_html=True)
    btn_run = st.button("⚡ ANALISAR AGORA")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="btn-clear">', unsafe_allow_html=True)
    st.button("🗑️ CLEAR DATA", on_click=reset_starline)
    st.markdown('</div>', unsafe_allow_html=True)

# --- RESULTADOS (HEATMAP POR ÍNDICE) ---
if btn_run:
    try:
        # Matemática Pura (Sem Home Advantage Fixo)
        adj = 0.67 if "Champions" in ctx else 1.0
        lh = ((v_h_gf/5) * (v_a_ga/5))**0.5
        la = ((v_a_gf * adj / 5) * (v_h_ga/5))**0.5
        
        sim_h, sim_a = np.random.poisson(lh, 100000), np.random.poisson(la, 100000)
        stot = sim_h + sim_a
        ph, px, pa = np.mean(sim_h > sim_a), np.mean(sim_h == sim_a), np.mean(sim_h < sim_a)
        norm = ph + px + pa
        ph, px, pa = ph/norm, px/norm, pa/norm

        with col_out:
            if adj < 1.0:
                st.markdown(f'<div class="ctx-alert">⚠️ FATOR PLAYOFF: Ataque do {a_name} reduzido em 33% para contexto de elite.</div>', unsafe_allow_html=True)
            
            st.subheader(f"📊 REPORT: {h_name} v {a_name}")
            
            mkts = [
                (f"1X2: {h_name}", ph, m_o1), ("1X2: DRAW", px, m_ox), (f"1X2: {a_name}", pa, m_o2),
                ("BTTS: YES", np.mean((sim_h>0)&(sim_a>0)), m_ob),
                ("DNB: HOME", ph/(ph+pa), m_hah), ("DNB: AWAY", pa/(ph+pa), m_haa),
                ("OVER 1.5", np.mean(stot>1.5), m_o15), ("UNDER 1.5", np.mean(stot<1.5), m_u15),
                ("OVER 2.5", np.mean(stot>2.5), m_o25), ("UNDER 2.5", np.mean(stot<2.5), m_u25),
                ("OVER 3.5", np.mean(stot>3.5), m_o35), ("UNDER 3.5", np.mean(stot<3.5), m_u35)
            ]

            final_rows, styles = [], []
            for n, p, b in mkts:
                edge = (p * b) - 1
                stk = max(0, (edge/(b-1)*5)) if b > 1 else 0
                
                # Definição de Cores Prestige
                bg = "rgba(255, 255, 255, 0)"
                if edge > 0.08: bg = "rgba(0, 255, 149, 0.15)"
                elif edge > 0: bg = "rgba(255, 165, 0, 0.15)"
                styles.append(bg)
                
                final_rows.append({
                    "MERCADO": n, "PROB %": f"{p:.1%}", "FAIR": f"{1/p:.2f}", 
                    "BOOKIE": f"{b:.2f}", "EDGE": f"{edge:+.1%}", "STAKE": f"{stk:.1f}%"
                })

            df_res = pd.DataFrame(final_rows)
            # Heatmap por Índice (Regra 3 - 100% Blindado)
            st.table(df_res.style.apply(lambda r: [f'background-color: {styles[r.name]}'] * len(r), axis=1))

            st.markdown("---")
            st.write("**🎯 TOP SCORE PREDICTIONS**")
            hp, ap = poisson.pmf(range(6), lh), poisson.pmf(range(6), la)
            mtx = np.outer(hp, ap)
            idx = np.unravel_index(np.argsort(mtx.ravel())[-5:], mtx.shape)
            scs = st.columns(5)
            for j in range(4, -1, -1):
                with scs[4-j]: st.metric(f"{idx[0][j]}-{idx[1][j]}", f"{mtx[idx[0][j], idx[1][j]]:.1%}")

    except Exception as e: st.error(f"ENGINE ERROR: {e}")
