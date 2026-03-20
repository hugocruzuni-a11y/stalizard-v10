import streamlit as st
import numpy as np
from scipy.stats import poisson
import pandas as pd

# 1. Configuração Starline Elite
st.set_page_config(page_title="STARLINE PRO", layout="wide")

# 2. CSS Profissional "Terminal Mode" (Alta Densidade e Sofisticação)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;800&display=swap');
    
    /* Configuração Global e Densidade */
    .stApp { background-color: #FFFFFF; color: #1E293B; font-family: 'Inter', sans-serif; }
    .block-container { padding-top: 1rem; padding-bottom: 0rem; max-width: 98%; }
    
    /* Compactação de Margens Verticais (Gaps) */
    div[data-testid="stVerticalBlock"] > div { margin-bottom: -1.2rem; }
    div[data-testid="stVerticalBlock"] > div > div > div { margin-bottom: -1rem; }
    
    /* Estilo de Inputs Minimalista e Definido (BLOOMBERG Style) */
    .stNumberInput, .stTextInput, .stSelectbox { 
        background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 4px; padding: 2px; 
        box-shadow: inset 0 1px 2px rgba(0,0,0,0.03); margin-bottom: 0.2rem !important; 
    }
    .stNumberInput input, .stTextInput input, .stSelectbox div[data-baseweb="select"] {
        height: 25px !important; font-size: 0.85rem !important; border: none !important; color: #1E293B !important; 
    }
    .stNumberInput label, .stTextInput label, .stSelectbox label {
        font-size: 0.65rem !important; font-weight: 700 !important; color: #64748B !important; text-transform: uppercase; margin-bottom: -0.8rem; 
    }
    
    /* Botão Profissional "Action Blue" */
    div.stButton > button {
        background: #1E293B; color: white !important; font-weight: 700;
        border-radius: 4px; width: 100%; height: 2.8em; border: none;
        transition: 0.2s; letter-spacing: 1px; font-size: 0.8rem;
    }
    div.stButton > button:hover { background: #334155; }
    
    /* Tabela de Dados Estilo Terminal Financeiro */
    .stTable { font-size: 0.8rem !important; border-radius: 0px !important; }
    thead tr th { background-color: #F8FAFC !important; color: #475569 !important; font-weight: 800 !important; text-transform: uppercase; }
    
    /* Alerta de Contexto Compacto */
    .ctx-alert {
        padding: 5px 10px; background-color: #FFFBEB; border-left: 3px solid #F59E0B;
        color: #92400E; font-weight: 600; font-size: 0.8rem; border-radius: 4px; margin-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

# Função de Reset (Cofunção blindada)
def reset_starline():
    for key in st.session_state.keys():
        del st.session_state[key]

st.markdown("### 🏛️ **STARLINE** // OMNI-QUANT TERMINAL <span style='font-size:12px; color:#94A3B8'>V26.2 ELITE</span>", unsafe_allow_html=True)
st.markdown("---")

# --- COLUNAS DE TRABALHO ---
col_in, col_out = st.columns([1, 2.2], gap="small")

with col_in:
    # 1. Configuração e Equipas (Tudo numa caixa compacta)
    st.caption(" estratégico CONTEXTO")
    ctx = st.selectbox("", ["Liga (Regular)", "Champions/Taça (Playoff)"], key="ctx", label_visibility="collapsed")
    
    c_h, c_a = st.columns(2)
    h_name = c_h.text_input("Casa", value="LEIPZIG", key="h_n").upper()
    a_name = c_a.text_input("Fora", value="HOFFENHEIM", key="a_n").upper()
    
    # 2. Stats (Grelha Ultra-Compacta)
    st.caption("GF/GA STATS (5-GAME AVG)")
    s1, s2, s3, s4 = st.columns(4)
    v_h_gf = s1.number_input("H-GF", value=8.0, key="hgf")
    v_h_ga = s2.number_input("H-GA", value=12.0, key="hga")
    v_a_gf = s3.number_input("A-GF", value=12.0, key="agf")
    v_a_ga = s4.number_input("A-GA", value=10.0, key="aga")
    
    # 3. Odds (Grelha Bloomberg Style)
    st.caption("LIVE MARKET ODDS")
    o1, ox, o2, ob = st.columns(4)
    m_o1, m_ox, m_o2, m_ob = o1.number_input("1", value=1.88, key="o1"), ox.number_input("X", value=4.00, key="ox"), o2.number_input("2", value=3.35, key="o2"), ob.number_input("BTTS", value=1.32, key="ob")
    
    o15, o25, o35, ha_h = st.columns(4)
    m_o15, m_o25, m_o35, m_hah = o15.number_input("+1.5", value=1.10, key="o15"), o25.number_input("+2.5", value=1.33, key="o25"), o35.number_input("+3.5", value=1.78, key="o35"), ha_h.number_input("DNB-H", value=1.33, key="hah")

    u15, u25, u35, ha_a = st.columns(4)
    m_u15, m_u25, m_u35, m_haa = u15.number_input("-1.5", value=4.55, key="u15"), u25.number_input("-2.5", value=2.65, key="u25"), u35.number_input("-3.5", value=1.75, key="u35"), ha_a.number_input("DNB-A", value=1.85, key="haa")

    # Botão de Ação Elite
    st.markdown('<div class="stButton">', unsafe_allow_html=True)
    btn_run = st.button("RUN QUANTITATIVE ENGINE")
    st.markdown('</div>', unsafe_allow_html=True)

# --- RESULTADOS ESTILO TERMINAL FINANCEIRO ---
if btn_run:
    try:
        # Matemática Pura V26
        v_adj = 0.67 if "Champions" in ctx else 1.0
        lh = ((v_h_gf/5) * (v_a_ga/5))**0.5
        la = ((v_a_gf * v_adj / 5) * (v_h_ga/5))**0.5
        sim_h, sim_a = np.random.poisson(lh, 100000), np.random.poisson(la, 100000)
        stot = sim_h + sim_a
        ph, px, pa = np.mean(sim_h > sim_a), np.mean(sim_h == sim_a), np.mean(sim_h < sim_a)
        n = ph + px + pa
        ph, px, pa = ph/n, px/n, pa/n

        with col_out:
            if v_adj < 1.0:
                st.markdown(f'<div class="ctx-alert">⚠️ FATOR PLAYOFF: Ataque do {a_name} reduzido.</div>', unsafe_allow_html=True)
            
            st.markdown(f"#### **ANALYSIS:** {h_name} v {a_name}")
            
            # Mercados V18 (DNB Recuperado)
            mkts = [
                (f"1X2: {h_name}", ph, m_o1), ("1X2: DRAW", px, m_ox), (f"1X2: {a_name}", pa, m_o2),
                ("BTTS: YES", np.mean((sim_h>0)&(sim_a>0)), m_ob),
                (f"DNB: {h_name}", ph/(ph+pa), m_hah), (f"DNB: {a_name}", pa/(ph+pa), m_haa),
                ("OVER 1.5", np.mean(stot>1.5), m_o15), ("UNDER 1.5", np.mean(stot<1.5), m_u15),
                ("OVER 2.5", np.mean(stot>2.5), m_o25), ("UNDER 2.5", np.mean(stot<2.5), m_u25),
                ("OVER 3.5", np.mean(stot>3.5), m_o35), ("UNDER 3.5", np.mean(stot<3.5), m_u35)
            ]

            final_data, styles = [], []
            for n, p, b in mkts:
                edge = (p * b) - 1
                stk = max(0, (edge/(b-1)*5)) if b > 1 else 0
                
                label = "PREMIUM 💎" if edge > 0.08 else "VALUE ✅" if edge > 0 else "---"
                bg = "rgba(0, 255, 149, 0.15)" if edge > 0.08 else "rgba(255, 165, 0, 0.15)" if edge > 0 else "none"
                styles.append(bg)
                
                final_data.append({
                    "STATUS": label, "MERCADO": n, "PROB %": f"{p:.1%}", 
                    "FAIR": f"{1/p:.2f}", "CASA": f"{b:.2f}", 
                    "EDGE %": f"{edge:+.1%}", "STAKE": f"{stk:.1f}%"
                })

            df_res = pd.DataFrame(final_data)
            
            # Heatmap por Índice (Regra 3) - Cores PRESTIGE mais suaves
            def terminal_heatmap(row):
                color = styles[row.name]
                return [f'background-color: {color}' if color != "none" else ''] * len(row)

            st.table(df_res.style.apply(terminal_heatmap, axis=1))

            # Scores Compactos
            st.markdown("---")
            st.write("**TOP SCORES PREDICTIONS**")
            hp, ap = poisson.pmf(range(6), lh), poisson.pmf(range(6), la)
            mtx = np.outer(hp, ap)
            idx = np.unravel_index(np.argsort(mtx.ravel())[-5:], mtx.shape)
            sc_cols = st.columns(5)
            for j in range(4, -1, -1):
                with sc_cols[4-j]: st.metric(f"{idx[0][j]}-{idx[1][j]}", f"{mtx[idx[0][j], idx[1][j]]:.1%}")

    except Exception as e: st.error(f"ENGINE ERROR: {e}")
