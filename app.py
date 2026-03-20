import streamlit as st
import numpy as np
from scipy.stats import poisson
import pandas as pd # Importado como 'pd' para compatibilidade total

# 1. Configuração de Página (Interface de Alta Performance)
st.set_page_config(page_title="STALIZARD V20 HEATMAP", layout="wide")

# 2. CSS "Prestige Light" com Heatmap Dinâmico
st.markdown("""
    <style>
    /* Reset e Fundo */
    .stApp { background-color: #F8FAFC; color: #1E293B; font-family: 'Inter', sans-serif; }
    .block-container { padding-top: 1.5rem; max-width: 95%; }
    
    /* Design de Cards para Inputs */
    div[data-testid="stVerticalBlock"] > div { background-color: white; border-radius: 12px; padding: 15px; box-shadow: 0 1px 3px rgba(0,0,0,0.02); }
    
    /* Inputs Estilizados */
    .stNumberInput input, .stTextInput input, .stSelectbox div[data-baseweb="select"] {
        background-color: #FFFFFF !important; border: 1px solid #E2E8F0 !important; border-radius: 8px !important; color: #1E293B !important;
    }
    .stNumberInput label, .stTextInput label, .stSelectbox label {
        font-size: 0.75rem !important; font-weight: 800 !important; color: #475569 !important; text-transform: uppercase; letter-spacing: 0.5px;
    }

    /* Botão Profissional "Action Blue" */
    div.stButton > button {
        background: linear-gradient(135deg, #1E293B 0%, #334155 100%);
        color: white !important; font-weight: 700; border-radius: 8px; height: 3.5em; width: 100%; border: none;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); transition: 0.3s; margin-top: 20px;
    }
    div.stButton > button:hover { transform: translateY(-2px); box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.2); }
    
    /* Tabela Bloomberg Style - Alta Densidade */
    .stTable { font-size: 0.85rem !important; background-color: white; border-radius: 12px; overflow: hidden; }
    thead tr th { background-color: #F1F5F9 !important; border-bottom: 2px solid #1E293B !important; color: #1E293B !important; font-weight: 800 !important; }
    
    /* Alerta Champions */
    .champions-alert { background-color: #FFFBEB; border-left: 5px solid #F59E0B; padding: 10px; color: #92400E; font-weight: 600; margin-bottom: 15px; border-radius: 4px;}
    </style>
    """, unsafe_allow_html=True)

# --- HEADER ULTRA-LEAN ---
st.markdown("### 🏛️ **STALIZARD** // OMNI-QUANT TERMINAL <span style='font-size:12px; color:#94A3B8'>V20.0 HEATMAP ELITE</span>", unsafe_allow_html=True)
st.markdown("---")

# --- WORKSPACE ---
col_in, col_out = st.columns([1.1, 2], gap="large")

with col_in:
    with st.container():
        st.markdown("**STRATEGIC CONTEXT**")
        ctx = st.selectbox("", ["Liga (Regular)", "Champions/Taça (Playoff)"], label_visibility="collapsed")
        
        c_h, c_a = st.columns(2)
        h_name = c_h.text_input("HOME", "LEIPZIG").upper()
        a_name = c_a.text_input("AWAY", "HOFFENHEIM").upper()
    
    with st.container():
        st.markdown("**GF/GA STATS (5-GAME AVG)**")
        cg1, cg2, cg3, cg4 = st.columns(4)
        v_h_gf = cg1.number_input("H-GF", value=8.0)
        v_h_ga = cg2.number_input("H-GA", value=12.0)
        v_a_gf = cg3.number_input("A-GF", value=12.0)
        v_a_ga = cg4.number_input("A-GA", value=10.0)
    
    with st.container():
        st.markdown("**LIVE MARKET ODDS**")
        oc1, oc2, oc3, oc4 = st.columns(4)
        m_o1, m_ox, m_o2, m_ob = oc1.number_input("1", value=1.88), oc2.number_input("X", value=4.00), oc3.number_input("2", value=3.35), oc4.number_input("BTTS", value=1.32)
        
        oc5, oc6, oc7, oc8 = st.columns(4)
        m_o15, m_o25, m_o35, m_hah = oc5.number_input("+1.5", value=1.10), oc6.number_input("+2.5", value=1.33), oc7.number_input("+3.5", value=1.78), oc8.number_input("DNB-H", value=1.33)

        oc9, oc10, oc11, oc12 = st.columns(4)
        m_u15, m_u25, m_u35, m_haa = oc9.number_input("-1.5", value=4.55), oc10.number_input("-2.5", value=2.65), oc11.number_input("-3.5", value=1.75), oc12.number_input("DNB-A", value=1.85)

        btn = st.button("RUN QUANTITATIVE ENGINE V20")

if btn:
    try:
        # Fator Champions (O teu detalhe favorito)
        comp_adj = 0.67 if "Champions" in ctx else 1.0
        
        # Matemática Poisson V15-V18 PRO (Trancada)
        lh = ((float(v_h_gf)/5)*(float(v_a_ga)/5))**0.5 * 1.12
        la = ((float(v_a_gf)*comp_adj/5)*(float(v_h_ga)/5))**0.5 * 0.90
        
        sim_h, sim_a = np.random.poisson(lh, 100000), np.random.poisson(la, 100000)
        tot = sim_h + sim_a
        
        ph, px, pa = np.mean(sim_h > sim_a), np.mean(sim_h == sim_a), np.mean(sim_h < sim_a)
        norm = ph + px + pa
        ph, px, pa = ph/norm, px/norm, pa/norm

        with col_out:
            if comp_adj < 1.0:
                st.markdown(f'<div class="champions-alert">⚠️ FATOR PLAYOFF: Ataque do {a_name} reduzido em 33% para contexto de elite.</div>', unsafe_allow_html=True)
            
            st.markdown(f"#### **ANALYSIS:** {h_name} v {a_name}")
            
            # Mercados V18 (DNB Recuperado)
            mkts_data = [
                (f"1X2: {h_name}", ph, m_o1), ("1X2: DRAW", px, m_ox), (f"1X2: {a_name}", pa, m_o2),
                ("BTTS: YES", np.mean((sim_h>0)&(sim_a>0)), m_ob),
                (f"DNB: {h_name}", ph/(ph+pa), m_hah), (f"DNB: {a_name}", pa/(ph+pa), m_haa),
                ("OVER 2.5", np.mean(tot>2.5), m_o25), ("UNDER 2.5", np.mean(tot<2.5), m_u25),
                ("OVER 3.5", np.mean(tot>3.5), m_o35), ("UNDER 3.5", np.mean(tot<3.5), m_u35)
            ]

            final_dump = []
            for n, p, b in mkts_data:
                edge = (p * b) - 1
                stk = max(0, (edge/(b-1)*5)) if b > 1 else 0
                label = "PREMIUM" if edge > 0.08 else "VALUE" if edge > 0 else "---"
                final_dump.append({
                    "STATUS": label, "MARKET": n, "PROB %": f"{p:.1%}", 
                    "FAIR": f"{1/p:.2f}", "BOOKIE": f"{b:.2f}", 
                    "EDGE %": f"{edge:+.1%}", "STAKE": f"{stk:.1f}%", "ev": edge
                })

            # --- A NOVA TABELA "HEATMAP" (Zero Erros) ---
            df = pd.DataFrame(final_dump)
            
            # Função de Estilo Dinâmico (Heatmap V15 Style)
            def style_heatmap(row):
                color = 'white' # Default
                if row['ev'] > 0.08: color = '#00FF95' # Verde Neon
                elif row['ev'] > 0: color = '#FFA500' # Laranja Ouro
                return [f'color: {color}; font-weight: bold' if color != 'white' else ''] * len(row)

            # Renderização da Tabela com Estilo (Heatmap Ativado)
            st.table(df.drop(columns=['ev']).style.apply(style_heatmap, axis=1))

            st.markdown("---")
            st.subheader("🎯 TOP SCORE PREDICTIONS")
            hp, ap = poisson.pmf(range(6), lh), poisson.pmf(range(6), la)
            mtx = np.outer(hp, ap)
            idx = np.unravel_index(np.argsort(mtx.ravel())[-5:], mtx.shape)
            
            score_cols = st.columns(5)
            for i in range(4, -1, -1):
                with score_cols[4-i]:
                    st.metric(f"{idx[0][i]} - {idx[1][i]}", f"{mtx[idx[0][i], idx[1][i]]:.1%}")

    except Exception as e: st.error(f"ENGINE ERROR V20: {e}")
