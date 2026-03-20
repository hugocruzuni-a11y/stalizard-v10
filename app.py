import streamlit as st
import numpy as np
from scipy.stats import poisson
import pandas as pd

# 1. Configuração de Página (Interface Profissional SaaS Style)
st.set_page_config(page_title="STALIZARD OMNI-QUANT PRO", layout="wide")

# 2. Design "Modern Fintech"
st.markdown("""
    <style>
    .stApp { background-color: #F8FAFC; color: #1E293B; font-family: 'Inter', sans-serif; }
    div[data-testid="stVerticalBlock"] > div { background-color: white; border-radius: 12px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.02); }
    .stNumberInput input { background-color: #FFFFFF !important; color: #1E293B !important; border: 1px solid #E2E8F0 !important; border-radius: 8px !important; }
    .stTextInput input { border-radius: 8px !important; border: 1px solid #E2E8F0 !important; background-color: #FFFFFF !important; }
    .stSelectbox div[data-baseweb="select"] { background-color: #FFFFFF !important; border: 1px solid #E2E8F0 !important; border-radius: 8px !important; }
    div.stButton > button {
        background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%);
        color: white !important;
        font-weight: 700;
        border-radius: 8px;
        height: 3.8em;
        width: 100%;
        border: none;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        transition: all 0.2s;
        margin-top: 25px;
    }
    div.stButton > button:hover { transform: translateY(-1px); box-shadow: 0 10px 15px -3px rgba(37, 99, 235, 0.25); }
    h1, h2, h3 { color: #0F172A !important; font-weight: 800 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- CABEÇALHO ---
st.title("🏛️ STALIZARD OMNI-QUANT")
st.caption("Professional Betting Intelligence System • V16.2 PRO")
st.markdown("---")

# --- CORPO PRINCIPAL ---
col_left, col_right = st.columns([1, 1.8], gap="large")

with col_left:
    with st.container():
        st.subheader("🛠️ Configuração")
        comp_type = st.selectbox("Contexto da Partida", ["Liga (Regular)", "Champions/Taça (Playoff)"])
        c_h, c_a = st.columns(2)
        h_name = c_h.text_input("Equipa Casa", "LEIPZIG")
        a_name = c_a.text_input("Equipa Fora", "HOFFENHEIM")
    
    with st.container():
        st.markdown("### ⚽ Médias (GF / GA)")
        cg1, cg2, cg3, cg4 = st.columns(4)
        v_h_gf = cg1.number_input("H-GF", value=8.0)
        v_h_ga = cg2.number_input("H-GA", value=12.0)
        v_a_gf = cg3.number_input("A-GF", value=12.0)
        v_a_ga = cg4.number_input("A-GA", value=10.0)
    
    with st.container():
        st.markdown("### 💹 Odds de Mercado")
        oc1, oc2, oc3, oc4 = st.columns(4)
        m_o1, m_ox, m_o2, m_obtts = oc1.number_input("1", value=1.88), oc2.number_input("X", value=4.00), oc3.number_input("2", value=3.35), oc4.number_input("BTTS", value=1.32)
        
        oc5, oc6, oc7, oc8 = st.columns(4)
        m_o15, m_o25, m_o35, m_ha0h = oc5.number_input("+1.5", value=1.10), oc6.number_input("+2.5", value=1.33), oc7.number_input("+3.5", value=1.78), oc8.number_input("DNB-H", value=1.33)

        oc9, oc10, oc11, oc12 = st.columns(4)
        m_u15, m_u25, m_u35, m_ha0a = oc9.number_input("-1.5", value=4.55), oc10.number_input("-2.5", value=2.65), oc11.number_input("-3.5", value=1.75), oc12.number_input("DNB-A", value=1.85)

        btn_run = st.button("⚡ GERAR ANÁLISE QUANTITATIVA")

# --- RESULTADOS ---
if btn_run:
    try:
        calc_a_gf = float(v_a_gf)
        if comp_type == "Champions/Taça (Playoff)":
            calc_a_gf = v_a_gf * 0.67
            st.warning("⚠️ **Fator Playoff Ativado:** Ajuste aplicado.")

        l_h = ((v_h_gf/5)*(v_a_ga/5))**0.5 * 1.12
        l_a = ((calc_a_gf/5)*(v_h_ga/5))**0.5 * 0.90
        sim_h, sim_a = np.random.poisson(l_h, 100000), np.random.poisson(l_a, 100000)
        s_tot = sim_h + sim_a
        
        p_h, p_x, p_a = np.mean(sim_h > sim_a), np.mean(sim_h == sim_a), np.mean(sim_h < sim_a)
        norm = p_h + p_x + p_a
        p_h, p_x, p_a = p_h/norm, p_x/norm, p_a/norm

        with col_right:
            st.subheader(f"📊 Relatório: {h_name.upper()} vs {a_name.upper()}")
            mkts = [
                (f"1X2: {h_name.upper()}", p_h, m_o1), ("1X2: DRAW", p_x, m_ox), (f"1X2: {a_name.upper()}", p_a, m_o2),
                ("BTTS: SIM", np.mean((sim_h>0)&(sim_a>0)), m_obtts), 
                (f"DNB: {h_name.upper()}", p_h/(p_h+p_a), m_ha0h), (f"DNB: {a_name.upper()}", p_a/(p_h+p_a), m_ha0a),
                ("OVER 1.5", np.mean(s_tot>1.5), m_o15), ("UNDER 1.5", np.mean(s_tot<1.5), m_u15),
                ("OVER 2.5", np.mean(s_tot>2.5), m_o25), ("UNDER 2.5", np.mean(s_tot<2.5), m_u25),
                ("OVER 3.5", np.mean(s_tot>3.5), m_o35), ("UNDER 3.5", np.mean(s_tot<3.5), m_u35)
            ]

            final_data = []
            for name, prob, bookie in mkts:
                edge = (prob * bookie) - 1
                stake = max(0, (edge/(bookie-1)*5)) if bookie > 1 else 0
                status = "💎 ALTO VALOR" if edge > 0.08 else "✅ POSITIVO" if edge > 0 else "❌ SEM VALOR"
                final_data.append({"ANÁLISE": status, "MERCADO": name, "PROB": f"{prob:.1%}", "JUSTA": f"{1/prob:.2f}", "CASA": f"{bookie:.2f}", "EDGE": f"{edge:+.1%}", "STAKE": f"{stake:.1f}%"})

            st.table(pd.DataFrame(final_data))

            st.markdown("---")
            st.markdown("### 🎯 Top Placares Exatos")
            hp, ap = poisson.pmf(range(6), l_h), poisson.pmf(range(6), l_a)
            mtx = np.outer(hp, ap)
            idx = np.unravel_index(np.argsort(mtx.ravel())[-5:], mtx.shape)
            sc_cols = st.columns(5)
            for i in range(4, -1, -1):
                with sc_cols[4-i]:
                    st.metric(f"{idx[0][i]} - {idx[1][i]}", f"{mtx[idx[0][i], idx[1][i]]:.1%}")
    except Exception as e:
        st.error(f"Erro: {e}")
