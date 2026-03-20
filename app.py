import streamlit as st
import numpy as np
from scipy.stats import poisson
import pandas as pd

# 1. Configuração de Página (Interface limpa e profissional)
st.set_page_config(page_title="STALIZARD V16 PRO", layout="wide")

# 2. Design "Modern White" (SaaS Style)
st.markdown("""
    <style>
    /* Fundo e texto principal */
    .stApp { background-color: #F8FAFC; color: #1E293B; }
    
    /* Inputs e Cards */
    div[data-testid="stVerticalBlock"] > div { background-color: white; border-radius: 12px; }
    .stNumberInput input { background-color: #FFFFFF !important; color: #1E293B !important; border: 1px solid #E2E8F0 !important; border-radius: 8px !important; }
    .stTextInput input { border-radius: 8px !important; border: 1px solid #E2E8F0 !important; }
    
    /* Botão de Ação Profissional */
    div.stButton > button {
        background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%);
        color: white !important;
        font-weight: 600;
        border-radius: 8px;
        height: 3.5em;
        width: 100%;
        border: none;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        transition: all 0.2s;
    }
    div.stButton > button:hover { transform: translateY(-1px); box-shadow: 0 10px 15px -3px rgba(37, 99, 235, 0.2); }
    
    /* Tabelas e Cabeçalhos */
    h1, h2, h3 { color: #0F172A !important; font-family: 'Inter', sans-serif; letter-spacing: -0.5px; }
    .stTable { background-color: white; border-radius: 12px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
    
    /* Divider */
    hr { margin: 2em 0; border-top: 1px solid #E2E8F0; }
    </style>
    """, unsafe_allow_html=True)

# --- CABEÇALHO ---
col_t1, col_t2 = st.columns([3, 1])
with col_t1:
    st.title("🏛️ STALIZARD OMNI-QUANT")
    st.caption("Professional Betting Intelligence System • V16.0 PRO")

st.markdown("---")

# --- CORPO PRINCIPAL ---
col_left, col_right = st.columns([1, 1.8], gap="large")

with col_left:
    with st.container():
        st.subheader("📍 Configuração")
        comp_type = st.selectbox("Contexto da Partida", ["Liga (Regular)", "Champions/Taça (Playoff)"])
        
        c_h, c_a = st.columns(2)
        h_name = c_h.text_input("Equipa Casa", "LEIPZIG")
        a_name = c_a.text_input("Equipa Fora", "HOFFENHEIM")
        
        st.markdown("### ⚽ Médias (GF/GA)")
        c1, c2, c3, c4 = st.columns(4)
        v_h_gf = c1.number_input("H-GF", value=8.0)
        v_h_ga = c2.number_input("H-GA", value=12.0)
        v_a_gf = c3.number_input("A-GF", value=12.0)
        v_a_ga = c4.number_input("A-GA", value=10.0)
        
        st.markdown("### 💹 Odds Reais (Market)")
        o_c1, o_c2, o_c3, o_c4 = st.columns(4)
        m_o1, m_ox, m_o2, m_obtts = o_c1.number_input("1", value=1.88), o_c2.number_input("X", value=4.00), o_c3.number_input("2", value=3.35), o_c4.number_input("BTTS", value=1.32)
        
        o_c5, o_c6, o_c7, o_c8 = st.columns(4)
        m_o15, m_o25, m_o35, m_ha0h = o_c5.number_input("+1.5", value=1.10), o_c6.number_input("+2.5", value=1.33), o_c7.number_input("+3.5", value=1.78), o_c8.number_input("DNB-H", value=1.33)

        o_c9, o_c10, o_c11, o_c12 = st.columns(4)
        m_u15, m_u25, m_u35, m_ha0a = o_c9.number_input("-1.5", value=4.55), o_c10.number_input("-2.5", value=2.65), o_c11.number_input("-3.5", value=1.75), o_c12.number_input("DNB-A", value=1.85)

        btn_run = st.button("⚡ GERAR ANÁLISE QUANTITATIVA")

# --- ÁREA DE RESULTADOS ---
if btn_run:
    try:
        # Fator Champions (Ajuste de 33%)
        calc_a_gf = float(v_a_gf)
        if comp_type == "Champions/Taça (Playoff)":
            calc_a_gf = v_a_gf * 0.67
            st.warning("⚡ **Fator Playoff Ativado:** Ajuste de agressividade para equipa visitante aplicado.")

        # Lambdas (Matemática Pura)
        l_h = ((v_h_gf/5)*(v_a_ga/5))**0.5 * 1.12
        l_a = ((calc_a_gf/5)*(v_h_ga/5))**0.5 * 0.90
        
        sim_h, sim_a = np.random.poisson(l_h, 100000), np.random.poisson(l_a, 100000)
        s_tot = sim_h + sim_a
        
        p_h = np.mean(sim_h > sim_a)
        p_x = np.mean(sim_h == sim_a)
        p_a = np.mean(sim_h < sim_a)
        norm = p_h + p_x + p_a
        p_h, p_x, p_a = p_h/norm, p_x/norm, p_a/norm

        with col_right:
            st.subheader(f"📊 Relatório: {h_name.upper()} vs {a_name.upper()}")
            
            # Dados dos Mercados
            mkts = [
                (f"1X2: {h_name.upper()}", p_h, m_o1), ("1X2: EMPATE", p_x, m_ox), (f"1X2: {a_n.upper()}", p_a, m_o2),
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
                
                if edge > 0.08: status = "💎 ALTO VALOR"
                elif edge > 0: status = "✅ POSITIVO"
                else: status = "❌ SEM VALOR"
                
                final_data.append({
                    "ANÁLISE": status,
                    "MERCADO": name,
                    "PROB %": f"{prob:.1%}",
                    "ODD": f"{bookie:.2f}",
                    "EDGE %": f"{edge:+.1%}",
                    "STAKE %": f"{stake:.1f}%"
                })

            # Tabela Estilizada
            st.table(pd.DataFrame(final_data))

            # Top Scores em Cards Horizontais
            st.markdown("### 🎯 Probabilidade de Placares")
            hp, ap = poisson.pmf(range(6), l_h), poisson.pmf(range(6), l_a)
            mtx = np.outer(hp, ap)
            idx = np.unravel_index(np.argsort(mtx.ravel())[-5:], mtx.shape)
            
            score_cols = st.columns(5)
            for i in range(4, -1, -1):
                with score_cols[4-i]:
                    st.metric(f"{idx[0][i]} - {idx[1][i]}", f"{mtx[idx[0][i], idx[1][i]]:.1%}")
    
    except Exception as e:
        st.error(f"Erro no processamento: {e}")
