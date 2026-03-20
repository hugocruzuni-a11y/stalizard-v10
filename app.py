import streamlit as st
import numpy as np
from scipy.stats import poisson
import pandas as pd

# 1. Configuração Starline Elite
st.set_page_config(page_title="STARLINE DEEP ADVISOR", layout="wide")

# 2. CSS Corrigido (Título visível e Design Advisor)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;800&display=swap');
    
    /* Reset do Header para não apagar o título */
    .stApp header { background-color: transparent !important; }
    .stApp { background-color: #FFFFFF; color: #1E293B; font-family: 'Inter', sans-serif; }
    
    .block-container { padding-top: 2rem !important; max-width: 95%; }

    /* Inputs Estilizados */
    .stNumberInput, .stTextInput, .stSelectbox { 
        background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 6px; margin-bottom: 12px !important;
    }
    
    /* Botões Starline */
    .btn-run > div > button {
        background: linear-gradient(135deg, #10B981 0%, #059669 100%) !important;
        color: white !important; font-weight: 700; height: 3.5em; width: 100%; border: none; border-radius: 6px;
    }
    .btn-clear > div > button {
        background: linear-gradient(135deg, #F87171 0%, #EF4444 100%) !important;
        color: white !important; font-weight: 700; height: 3.5em; width: 100%; border: none; border-radius: 6px;
    }

    /* Cards Advisor Multi-Recomendação */
    .advice-card {
        padding: 12px 18px; border-radius: 8px; margin-bottom: 10px; border-left: 5px solid; font-size: 0.95rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    .val-prestige { background-color: #ECFDF5; border-color: #10B981; color: #065F46; } 
    .val-neutral { background-color: #F8FAFC; border-color: #94A3B8; color: #1E293B; }
    </style>
    """, unsafe_allow_html=True)

def reset_starline():
    for key in st.session_state.keys():
        del st.session_state[key]

# Título corrigido com Z-Index para não apagar
st.markdown("<h3 style='margin-bottom:0px; color:#1E293B; font-weight:800;'>🏛️ STARLINE // OMNI-QUANT <span style='font-size:12px; color:#94A3B8; font-weight:400;'>V33.0 DEEP ADVISOR</span></h3>", unsafe_allow_html=True)
st.markdown("---")

col_in, col_out = st.columns([1.2, 2], gap="large")

with col_in:
    ctx = st.selectbox("CONTEXTO", ["Liga (Regular)", "Champions/Taça (Playoff)"], key="ctx")
    c1, c2 = st.columns(2)
    h_n = c1.text_input("HOME", value="LEIPZIG", key="h_n").upper()
    a_n = c2.text_input("AWAY", value="HOFFENHEIM", key="a_n").upper()
    
    st.write("**STATS GF/GA**")
    s1, s2, s3, s4 = st.columns(4)
    v_hgf, v_hga, v_agf, v_aga = s1.number_input("H-GF", 8.0), s2.number_input("H-GA", 12.0), s3.number_input("A-GF", 12.0), s4.number_input("A-GA", 10.0)
    
    st.write("**LIVE ODDS**")
    o_grid1 = st.columns(4)
    m_o1 = o_grid1[0].number_input("1", 1.88)
    m_ox = o_grid1[1].number_input("X", 4.00)
    m_o2 = o_grid1[2].number_input("2", 3.35)
    m_ob = o_grid1[3].number_input("BTTS", 1.32)
    
    o_grid2 = st.columns(4)
    m_o15 = o_grid2[0].number_input("+1.5", 1.10)
    m_o25 = o_grid2[1].number_input("+2.5", 1.33)
    m_o35 = o_grid2[2].number_input("+3.5", 1.78)
    m_hah = o_grid2[3].number_input("DNB-H", 1.33)

    o_grid3 = st.columns(4)
    m_u15 = o_grid3[0].number_input("-1.5", 4.55)
    m_u25 = o_grid3[1].number_input("-2.5", 2.65)
    m_u35 = o_grid3[2].number_input("-3.5", 1.75)
    m_haa = o_grid3[3].number_input("DNB-A", 1.85)

    st.markdown('<div class="btn-run">', unsafe_allow_html=True)
    btn_run = st.button("⚡ EXECUTAR DEEP SCAN")
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="btn-clear">', unsafe_allow_html=True)
    st.button("🗑️ CLEAR DATA", on_click=reset_starline)
    st.markdown('</div>', unsafe_allow_html=True)

if btn_run:
    try:
        adj = 0.67 if "Champions" in ctx else 1.0
        lh, la = ((v_hgf/5)*(v_aga/5))**0.5, ((v_agf*adj/5)*(v_hga/5))**0.5
        sim_h, sim_a = np.random.poisson(lh, 100000), np.random.poisson(la, 100000)
        stot = sim_h + sim_a
        ph, px, pa = np.mean(sim_h > sim_a), np.mean(sim_h == sim_a), np.mean(sim_h < sim_a)
        norm = ph + px + pa
        ph, px, pa = ph/norm, px/norm, pa/norm

        with col_out:
            st.markdown("#### 🎯 STARLINE DEEP ADVISOR: RECOMENDAÇÕES")
            
            # --- MOTOR MULTI-SCAN ---
            all_options = [
                (f"1X2: {h_n}", ph, m_o1, "VENCEDOR"), (f"1X2: {a_n}", pa, m_o2, "VENCEDOR"),
                ("BTTS: YES", np.mean((sim_h>0)&(sim_a>0)), m_ob, "GOLOS"),
                ("OVER 2.5", np.mean(stot>2.5), m_o25, "GOLOS"),
                ("DNB: HOME", ph/(ph+pa), m_hah, "PROTEÇÃO"),
                ("DNB: AWAY", pa/(ph+pa), m_haa, "PROTEÇÃO"),
                ("OVER 1.5", np.mean(stot>1.5), m_o15, "GOLOS")
            ]
            
            # Filtrar e Ordenar
            valid_recoms = []
            for n, p, b, cat in all_options:
                edge = (p * b) - 1
                if edge > 0.05: # Edge mínima de 5% para ser "Recomendação"
                    valid_recoms.append((n, p, b, edge, cat))
            
            valid_recoms = sorted(valid_recoms, key=lambda x: x[3], reverse=True)

            if valid_recoms:
                for n, p, b, e, cat in valid_recoms[:3]: # Mostra Top 3
                    icon = "💎" if e > 0.12 else "✅"
                    st.markdown(f"""
                    <div class="advice-card val-prestige">
                        {icon} <b>{cat}: {n}</b><br>
                        Edge: <b>{e:+.1%}</b> | Odd: <b>{b:.2f}</b> (Justa: {1/p:.2f})
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown('<div class="advice-card val-neutral">🛑 Sem Edge clara. Mercado muito ajustado.</div>', unsafe_allow_html=True)

            # Tabela Full
            data_list, colors = [], []
            for n, p, b, _ in all_options:
                edge = (p * b) - 1
                bg = "rgba(0, 255, 149, 0.15)" if edge > 0.08 else "rgba(255, 165, 0, 0.15)" if edge > 0 else "none"
                colors.append(bg)
                data_list.append({"MERCADO": n, "PROB": f"{p:.1%}", "JUSTA": f"{1/p:.2f}", "CASA": f"{b:.2f}", "EDGE": f"{edge:+.1%}"})

            st.table(pd.DataFrame(data_list).style.apply(lambda r: [f'background-color: {colors[r.name]}'] * len(r), axis=1))

            # Scores
            st.write("**PLACAR ESTIMADO**")
            hp, ap = poisson.pmf(range(6), lh), poisson.pmf(range(6), la)
            mtx = np.outer(hp, ap)
            idx = np.unravel_index(np.argsort(mtx.ravel())[-5:], mtx.shape)
            scs = st.columns(5)
            for j in range(4, -1, -1):
                with scs[4-j]: st.metric(f"{idx[0][j]}-{idx[1][j]}", f"{mtx[idx[0][j], idx[1][j]]:.1%}")

    except Exception as e: st.error(f"Erro: {e}")
