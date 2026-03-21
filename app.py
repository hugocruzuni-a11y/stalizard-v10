import streamlit as st
import numpy as np
from scipy.stats import poisson
import pandas as pd

# 1. Configuração Starline Ultra Prestige (Macbook Optimized)
st.set_page_config(page_title="STARLINE ULTRA V36.3", layout="wide")

# 2. CSS Elite (Fundo Branco, Design Prestige Clean)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
    
    .stApp { background-color: #FFFFFF; color: #1E293B; font-family: 'Inter', sans-serif; }
    .block-container { padding: 1rem 2rem 0rem 3rem !important; max-width: 100% !important; }

    /* Inputs Estilizados Sem Restrições Visíveis */
    .stNumberInput, .stTextInput, .stSelectbox { 
        background-color: #F8FAFC !important; border: 1px solid #E2E8F0 !important; border-radius: 6px !important; margin-bottom: 5px !important; 
    }
    .stNumberInput label, .stTextInput label, .stSelectbox label {
        font-size: 0.65rem !important; font-weight: 800 !important; color: #64748B !important; text-transform: uppercase; margin-bottom: 0px !important;
    }

    /* Botão Principal Ultra */
    div.stButton > button {
        background: linear-gradient(135deg, #064E3B 0%, #065F46 100%) !important;
        color: white !important; font-weight: 800; height: 3.8em; width: 100%; border-radius: 8px; border: none;
        box-shadow: 0 4px 12px rgba(6, 78, 59, 0.2); margin-top: 10px;
    }

    /* Advisor Prestige Cards */
    .advice-card {
        padding: 16px 20px; border-radius: 10px; margin-bottom: 12px; border-left: 6px solid;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .val-win { background-color: #ECFDF5; border-color: #10B981; color: #064E3B; } 
    .val-strat { background-color: #F0F9FF; border-color: #0EA5E9; color: #075985; }
    .val-neutral { background-color: #F1F5F9; border-color: #94A3B8; color: #1E293B; }

    /* Tabela Bloomberg Style */
    .stTable { font-size: 0.85rem !important; border-radius: 8px !important; overflow: hidden; border: 1px solid #E2E8F0; }
    thead tr th { background-color: #F8FAFC !important; color: #475569 !important; font-weight: 800 !important; }
    </style>
    """, unsafe_allow_html=True)

# Função de Reset Robusta
def reset_ultra():
    for key in list(st.session_state.keys()):
        del st.session_state[key]

# Título Desbloqueado
st.markdown("<h3 style='color:#1E293B; font-weight:800; margin: 10px 0px 5px 0px; letter-spacing:-1px;'>🏛️ STARLINE // OMNI-QUANT <span style='color:#059669; font-size:12px; font-weight:400; letter-spacing:0px;'>V36.3 ULTRA 1M</span></h3>", unsafe_allow_html=True)
st.markdown("---")

# Layout de 2 Colunas
col_in, col_out = st.columns([1, 2.2], gap="large")

with col_in:
    # 1. Estratégia e Teams
    ctx = st.selectbox("ESTRATÉGIA", ["Liga (Regular)", "Champions/Taça (Playoff)"], key="ctx")
    
    ch, ca = st.columns(2)
    h_n = ch.text_input("HOME TEAM", value="VILLARREAL", key="h_n").upper()
    a_n = ca.text_input("AWAY TEAM", value="REAL SOCIEDAD", key="a_n").upper()
    
    # 2. Stats (GF/GA) - SEM MÍNIMOS NEM MÁXIMOS
    st.markdown("<p style='font-size:10px; font-weight:800; color:#64748B; margin-top:15px;'>STATS GF/GA (5 JOGOS)</p>", unsafe_allow_html=True)
    s1, s2 = st.columns(2)
    v_hgf = s1.number_input("H-GF", value=9.0, step=0.1, key="hgf_k")
    v_hga = s2.number_input("H-GA", value=7.0, step=0.1, key="hga_k")
    s3, s4 = st.columns(2)
    v_agf = s3.number_input("A-GF", value=12.0, step=0.1, key="agf_k")
    v_aga = s4.number_input("A-GA", value=10.0, step=0.1, key="aga_k")
    
    # 3. LIVE ODDS - TOTALMENTE ABERTAS
    st.markdown("<p style='font-size:10px; font-weight:800; color:#64748B; margin-top:15px;'>MARKET ODDS</p>", unsafe_allow_html=True)
    o1, ox = st.columns(2); m_o1 = o1.number_input("ODD 1", value=1.88, step=0.01, key="o1_k"); m_ox = ox.number_input("ODD X", value=4.00, step=0.01, key="ox_k")
    o2, ob = st.columns(2); m_o2 = o2.number_input("ODD 2", value=3.35, step=0.01, key="o2_k"); m_ob = ob.number_input("BTTS YES", value=1.32, step=0.01, key="ob_k")
    
    st.markdown("<p style='font-size:10px; font-weight:800; color:#64748B;'>GOLOS & PROTEÇÃO</p>", unsafe_allow_html=True)
    o15, o25 = st.columns(2); m_o15 = o15.number_input("OVER 1.5", value=1.10, step=0.01, key="o15_k"); m_o25 = o25.number_input("OVER 2.5", value=1.33, step=0.01, key="o25_k")
    o35, hah = st.columns(2); m_o35 = o35.number_input("OVER 3.5", value=1.78, step=0.01, key="o35_k"); m_hah = hah.number_input("DNB HOME", value=1.33, step=0.01, key="hah_k")
    u15, u25 = st.columns(2); m_u15 = u15.number_input("UNDER 1.5", value=4.55, step=0.01, key="u15_k"); m_u25 = u25.number_input("UNDER 2.5", value=2.65, step=0.01, key="u25_k")
    u35, haa = st.columns(2); m_u35 = u35.number_input("UNDER 3.5", value=1.75, step=0.01, key="u35_k"); m_haa = haa.number_input("DNB AWAY", value=1.85, step=0.01, key="haa_k")

    btn_run = st.button("🚀 EXECUTAR 1.000.000 SIMULAÇÕES")
    st.button("🗑️ RESET ENGINE", on_click=reset_ultra)

# --- ENGINE ULTRA 1M ---
if btn_run:
    try:
        adj = 0.67 if "Champions" in ctx else 1.0
        # Lambdas (Cálculo Direto)
        lh, la = ((v_hgf/5)*(v_aga/5))**0.5, ((v_agf*adj/5)*(v_hga/5))**0.5
        
        # Simulação Massiva
        sim_h, sim_a = np.random.poisson(lh, 1000000), np.random.poisson(la, 1000000)
        stot = sim_h + sim_a
        
        # Probabilidades
        ph, px, pa = np.mean(sim_h > sim_a), np.mean(sim_h == sim_a), np.mean(sim_h < sim_a)
        norm = ph + px + pa
        ph, px, pa = ph/norm, px/norm, pa/norm

        with col_out:
            st.markdown("#### 🎯 ULTRA ADVISOR PRO")
            
            targets = [
                (f"1X2: {h_n}", ph, m_o1, "VITÓRIA"), (f"1X2: {a_n}", pa, m_o2, "VITÓRIA"),
                ("BTTS: YES", np.mean((sim_h>0)&(sim_a>0)), m_ob, "GOLOS"),
                ("OVER 2.5", np.mean(stot>2.5), m_o25, "GOLOS"),
                ("DNB: HOME", ph/(ph+pa), m_hah, "PROTEÇÃO"),
                ("DNB: AWAY", pa/(ph+pa), m_haa, "PROTEÇÃO")
            ]
            
            recoms = sorted([(n, p, b, (p*b)-1, t) for n, p, b, t in targets if (p*b)-1 > 0.04], key=lambda x: x[3], reverse=True)

            if recoms:
                for n, p, b, e, t in recoms[:3]:
                    style = "val-win" if t == "VITÓRIA" else "val-strat"
                    st.markdown(f'<div class="advice-card {style}"><b>{t}: {n}</b><br>Confiança: {p:.1%} | Edge: {e:+.1%} | Odd: {b:.2f}</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="advice-card val-neutral">🛑 Sem Edge clara detetada acima de 4%.</div>', unsafe_allow_html=True)

            # Tabela Full
            res_data, ev_styles = [], []
            full_list = targets + [("1X2: DRAW", px, m_ox, "EMPATE"), ("OVER 1.5", np.mean(stot>1.5), m_o15, "GOLOS"), ("UNDER 2.5", 1-np.mean(stot>2.5), m_u25, "GOLOS")]
            for n, p, b, _ in full_list:
                edge = (p * b) - 1
                bg = "rgba(5, 150, 105, 0.12)" if edge > 0.10 else "rgba(245, 158, 11, 0.12)" if edge > 0 else "none"
                ev_styles.append(bg)
                res_data.append({"MERCADO": n, "PROB": f"{p:.1%}", "JUSTA": f"{1/p:.2f}", "CASA": f"{b:.2f}", "EDGE": f"{edge:+.1%}"})

            st.table(pd.DataFrame(res_data).style.apply(lambda r: [f'background-color: {ev_styles[r.name]}'] * len(r), axis=1))

            # PlacaRES
            hp, ap = poisson.pmf(range(6), lh), poisson.pmf(range(6), la)
            mtx = np.outer(hp, ap)
            mtx[0,0] *= 1.12; mtx[1,1] *= 1.08
            mtx /= mtx.sum()
            idx = np.unravel_index(np.argsort(mtx.ravel())[-5:], mtx.shape)
            scs = st.columns(5)
            for j in range(4, -1, -1):
                with scs[4-j]: st.metric(f"{idx[0][j]}-{idx[1][j]}", f"{mtx[idx[0][j], idx[1][j]]:.1%}")

    except Exception as e: st.error(f"ENGINE ERROR V36.3: {e}")
