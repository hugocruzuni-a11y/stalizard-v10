import streamlit as st
import numpy as np
from scipy.stats import poisson
import pandas as pd

# 1. Configuração de Página Estável
st.set_page_config(page_title="STALIZARD V21 PRO", layout="wide")

# 2. CSS Seguro (Sem sobreposições de caixas)
st.markdown("""
    <style>
    .stApp { background-color: #F8FAFC; color: #1E293B; }
    /* Espaçamento entre blocos de input */
    .stNumberInput, .stTextInput, .stSelectbox { margin-bottom: 10px !important; }
    
    /* Botão Profissional */
    div.stButton > button {
        background: #1E293B !important;
        color: white !important;
        font-weight: bold;
        width: 100%;
        border-radius: 6px;
        height: 3em;
        border: none;
    }
    
    /* Tabela de Resultados */
    .stTable { background-color: white; border-radius: 8px; }
    
    /* Alerta de Contexto */
    .ctx-alert {
        padding: 10px;
        background-color: #FFFBEB;
        border-left: 5px solid #F59E0B;
        color: #92400E;
        font-weight: bold;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🏛️ STALIZARD // OMNI-QUANT V21")
st.markdown("---")

# --- COLUNAS ---
col_in, col_out = st.columns([1, 2], gap="large")

with col_in:
    st.subheader("📋 DADOS DE ENTRADA")
    ctx = st.selectbox("CONTEXTO DA PARTIDA", ["Liga (Regular)", "Champions/Taça (Playoff)"])
    
    h_name = st.text_input("EQUIPA CASA", "LEIPZIG").upper()
    a_name = st.text_input("EQUIPA FORA", "HOFFENHEIM").upper()
    
    st.write("**ESTATÍSTICAS (GF/GA)**")
    c1, c2, c3, c4 = st.columns(4)
    v_h_gf = c1.number_input("H-GF", value=8.0)
    v_h_ga = c2.number_input("H-GA", value=12.0)
    v_a_gf = c3.number_input("A-GF", value=12.0)
    v_a_ga = c4.number_input("A-GA", value=10.0)
    
    st.write("**ODDS DE MERCADO**")
    o1, ox, o2, ob = st.columns(4)
    m_o1, m_ox, m_o2, m_ob = o1.number_input("1", value=1.88), ox.number_input("X", value=4.00), o2.number_input("2", value=3.35), ob.number_input("BTTS", value=1.32)
    
    o15, o25, o35, hah = st.columns(4)
    m_o15, m_o25, m_o35, m_hah = o15.number_input("+1.5", value=1.10), o25.number_input("+2.5", value=1.33), o35.number_input("+3.5", value=1.78), hah.number_input("DNB-H", value=1.33)

    u15, u25, u35, haa = st.columns(4)
    m_u15, m_u25, m_u35, m_haa = u15.number_input("-1.5", value=4.55), u25.number_input("-2.5", value=2.65), u35.number_input("-3.5", value=1.75), haa.number_input("DNB-A", value=1.85)

    btn = st.button("⚡ EXECUTAR ANÁLISE")

# --- LÓGICA E RESULTADOS ---
if btn:
    try:
        # Fator Champions (0.67 para playoff)
        adj = 0.67 if "Champions" in ctx else 1.0
        
        # Matemática Poisson Calibrada
        lh = ((v_h_gf/5)*(v_a_ga/5))**0.5 * 1.12
        la = ((v_a_gf * adj / 5)*(v_h_ga/5))**0.5 * 0.90
        
        sim_h, sim_a = np.random.poisson(lh, 100000), np.random.poisson(la, 100000)
        tot = sim_h + sim_a
        
        ph, px, pa = np.mean(sim_h > sim_a), np.mean(sim_h == sim_a), np.mean(sim_h < sim_a)
        norm = ph + px + pa
        ph, px, pa = ph/norm, px/norm, pa/norm

        with col_out:
            if adj < 1.0:
                st.markdown(f'<div class="ctx-alert">⚠️ FATOR CHAMPIONS APLICADO: Ataque de fora ({a_name}) reduzido em 33%.</div>', unsafe_allow_html=True)
            
            st.subheader(f"📊 RESULTADOS: {h_name} vs {a_name}")
            
            mkts = [
                (f"1X2: {h_name}", ph, m_o1), ("1X2: DRAW", px, m_ox), (f"1X2: {a_name}", pa, m_o2),
                ("BTTS: YES", np.mean((sim_h>0)&(sim_a>0)), m_ob),
                (f"DNB: {h_name}", ph/(ph+pa), m_hah), (f"DNB: {a_name}", pa/(ph+pa), m_haa),
                ("OVER 2.5", np.mean(tot>2.5), m_o25), ("UNDER 2.5", np.mean(tot<2.5), m_u25),
                ("OVER 3.5", np.mean(tot>3.5), m_o35), ("UNDER 3.5", np.mean(tot<3.5), m_u35)
            ]

            res_list = []
            for n, p, b in mkts:
                edge = (p * b) - 1
                stk = max(0, (edge/(b-1)*5)) if b > 1 else 0
                status = "PREMIUM 💎" if edge > 0.08 else "VALUE ✅" if edge > 0 else "---"
                res_list.append({
                    "STATUS": status, "MERCADO": n, "PROB %": f"{p:.1%}", 
                    "JUSTA": f"{1/p:.2f}", "CASA": f"{b:.2f}", 
                    "EDGE %": f"{edge:+.1%}", "STAKE": f"{stk:.1f}%", "ev": edge
                })

            df = pd.DataFrame(res_list)

            # --- CÁLCULO DE CORES (HEATMAP) ---
            def apply_colors(row):
                if row['ev'] > 0.08: return ['color: #15803D; font-weight: bold'] * len(row) # Verde Forte
                if row['ev'] > 0: return ['color: #B45309; font-weight: bold'] * len(row) # Laranja Forte
                return [''] * len(row)

            st.table(df.drop(columns=['ev']).style.apply(apply_colors, axis=1))

            st.markdown("---")
            st.write("**TOP 5 PLACARES EXATOS:**")
            hp, ap = poisson.pmf(range(6), lh), poisson.pmf(range(6), la)
            mtx = np.outer(hp, ap)
            idx = np.unravel_index(np.argsort(mtx.ravel())[-5:], mtx.shape)
            
            cols = st.columns(5)
            for i in range(4, -1, -1):
                with cols[4-i]:
                    st.metric(f"{idx[0][i]} - {idx[1][i]}", f"{mtx[idx[0][i], idx[1][i]]:.1%}")

    except Exception as e:
        st.error(f"Erro no processamento: {e}")
