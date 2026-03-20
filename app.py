import streamlit as st
import numpy as np
from scipy.stats import poisson
import pandas as pd

# 1. Configuração de Página (Interface Profissional SaaS Style)
st.set_page_config(page_title="STALIZARD OMNI-QUANT PRO", layout="wide")

# 2. Design "Modern Fintech" (Copia e cola com atenção)
st.markdown("""
    <style>
    /* Fundo Principal Cinza-Azulado Leve */
    .stApp { background-color: #F8FAFC; color: #1E293B; font-family: 'Inter', sans-serif; }
    
    /* Organização em Cards Brancos */
    div[data-testid="stVerticalBlock"] > div { background-color: white; border-radius: 12px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.02); }
    
    /* Inputs Estilizados (Modernos) */
    .stNumberInput input { background-color: #FFFFFF !important; color: #1E293B !important; border: 1px solid #E2E8F0 !important; border-radius: 8px !important; font-size: 16px !important; }
    .stTextInput input { border-radius: 8px !important; border: 1px solid #E2E8F0 !important; background-color: #FFFFFF !important; color: #1E293B !important; }
    .stSelectbox div[data-baseweb="select"] { background-color: #FFFFFF !important; color: #1E293B !important; border: 1px solid #E2E8F0 !important; border-radius: 8px !important; }
    
    /* Botão de Ação "Fintech Blue" com degradê */
    div.stButton > button {
        background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%);
        color: white !important;
        font-weight: 700;
        letter-spacing: -0.2px;
        border-radius: 8px;
        height: 3.8em;
        width: 100%;
        border: none;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        transition: all 0.2s;
        margin-top: 25px;
    }
    div.stButton > button:hover { transform: translateY(-1px); box-shadow: 0 10px 15px -3px rgba(37, 99, 235, 0.25); }
    
    /* Cabeçalhos e Tabela */
    h1, h2, h3 { color: #0F172A !important; letter-spacing: -0.5px; font-weight: 800 !important; }
    .stTable { background-color: white; border-radius: 12px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
    
    /* Divider e Caption */
    hr { margin: 2em 0; border-top: 1px solid #E2E8F0; }
    .stCaption { color: #64748B !important; }
    </style>
    """, unsafe_allow_html=True)

# --- CABEÇALHO ---
col_head1, col_head2 = st.columns([3, 1])
with col_head1:
    st.title("🏛️ STALIZARD OMNI-QUANT")
    st.caption("Professional Betting Intelligence System • V16.0 PRO")
st.markdown("---")

# --- CORPO PRINCIPAL (Design de 2 Colunas Fixas) ---
col_left, col_right = st.columns([1, 1.8], gap="large")

with col_left:
    # Card de Configuração
    with st.container():
        st.subheader("🛠️ Configuração Inicial")
        comp_type = st.selectbox("Contexto da Partida", ["Liga (Regular)", "Champions/Taça (Playoff)"])
        
        c_h, c_a = st.columns(2)
        h_name = c_h.text_input("Equipa Casa", "LEIPZIG")
        a_name = c_a.text_input("Equipa Fora", "HOFFENHEIM")
    
    # Card de Estatísticas
    with st.container():
        st.markdown("### ⚽ Médias (GF / GA)")
        c_g1, c_g2, c_g3, c_g4 = st.columns(4)
        v_h_gf = c_g1.number_input("H-GF", value=8.0)
        v_h_ga = c_c_g2.number_input("H-GA", value=12.0)
        v_a_gf = c_g3.number_input("A-GF", value=12.0)
        v_a_ga = c_g4.number_input("A-GA", value=10.0)
    
    # Card de Odds
    with st.container():
        st.markdown("### 💹 Odds de Mercado (Live)")
        o_c1, o_c2, o_c3, o_c4 = st.columns(4)
        m_o1 = o_c1.number_input("Casa (1)", value=1.88)
        m_ox = o_c2.number_input("Empate (X)", value=4.00)
        m_o2 = o_c3.number_input("Fora (2)", value=3.35)
        m_obtts = o_c4.number_input("BTTS", value=1.32)
        
        o_c5, o_c6, o_c7, o_c8 = st.columns(4)
        m_o15, m_o25, m_o35, m_ha0h = o_c5.number_input("+1.5", value=1.10), o_c6.number_input("+2.5", value=1.33), o_c7.number_input("+3.5", value=1.78), o_c8.number_input("DNB-H", value=1.33)

        o_c9, o_c10, o_c11, o_c12 = st.columns(4)
        m_u15, m_u25, m_u35, m_ha0a = o_c9.number_input("-1.5", value=4.55), o_c10.number_input("-2.5", value=2.65), o_c11.number_input("-3.5", value=1.75), o_c12.number_input("DNB-A", value=1.85)

        # Botão Profissional (Upgrade Visual)
        btn_run = st.button("⚡ GERAR ANÁLISE QUANTITATIVA")

# --- ÁREA DE RESULTADOS (DESIGN PRESTIGE) ---
if btn_run:
    try:
        # Recuperação da Lógica Fator Champions (Igual ao que funcionou)
        calc_a_gf = float(v_a_gf)
        if comp_type == "Champions/Taça (Playoff)":
            calc_a_gf = v_a_gf * 0.67
            st.warning("⚠️ **Fator Playoff Champions Ativado:** Ajuste de agressividade para a equipa visitante aplicado.")

        # Lambdas (Matemática Pura V15)
        l_h = ((v_h_gf/5)*(v_a_ga/5))**0.5 * 1.12
        l_a = ((calc_a_gf/5)*(v_h_ga/5))**0.5 * 0.90
        
        sim_h, sim_a = np.random.poisson(l_h, 100000), np.random.poisson(l_a, 100000)
        s_tot = sim_h + sim_a
        
        # Probabilidades Normais
        p_h = np.mean(sim_h > sim_a)
        p_x = np.mean(sim_h == sim_a)
        p_a = np.mean(sim_h < sim_a)
        norm = p_h + p_x + p_a
        p_h, p_x, p_a = p_h/norm, p_x/norm, p_a/norm

        with col_right:
            st.subheader(f"📊 Relatório Quântico: {h_name.upper()} vs {a_name.upper()}")
            
            # Mercados V15 PRO
            mkts = [
                (f"1X2: {h_name.upper()}", p_h, m_o1), ("1X2: DRAW", p_x, m_ox), ("1X2: FORA", p_a, m_o2),
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
                
                # Indicador de Valor Prestige (Texto em vez de Emojis)
                if edge > 0.08: status = "💎 ALTO VALOR"
                elif edge > 0: status = "✅ POSITIVO"
                else: status = "❌ SEM VALOR"
                
                final_data.append({
                    "ANÁLISE": status,
                    "MERCADO": name,
                    "PROB %": f"{prob:.1%}",
                    "ODD JUSTA": f"{1/prob:.2f}", # Acrescentei ODD Justa
                    "ODD CASA": f"{bookie:.2f}",
                    "EDGE %": f"{edge:+.1%}",
                    "STAKE %": f"{stake:.1f}%"
                })

            # Tabela Estilizada (High Density)
            st.table(pd.DataFrame(final_data))

            # --- TOP SCORES (Upgrade Visual para Cards) ---
            st.markdown("---")
            st.markdown("### 🎯 Probabilidade de Placares Exatos")
            hp, ap = poisson.pmf(range(6), l_h), poisson.pmf(range(6), l_a)
            mtx = np.outer(hp, ap)
            idx = np.unravel_index(np.argsort(mtx.ravel())[-5:], mtx.shape)
            
            sc_cols = st.columns(5)
            for i in range(4, -1, -1):
                score_str = f"{idx[0][i]} - {idx[1][i]}"
                prob_str = f"{mtx[idx[0][i], idx[1][i]]:.1%}"
                
                with sc_cols[4-i]:
                    st.metric(label=f"SCORE {5-i}", value=score_str, delta=prob_str)
                    
    except Exception as e:
        st.error(f"Erro no processamento do Relatório: {e}")
