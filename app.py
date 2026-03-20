import streamlit as st
import numpy as np
from scipy.stats import poisson
import pandas as pd

# 1. Configuração Starline Ultra Prestige
st.set_page_config(page_title="STARLINE ULTRA V35.1", layout="wide")

# 2. CSS Elite Refinado (Fundo Branco, Maior Espaçamento e Design Prestige Clean)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
    
    /* Configuração Global e Densidade Segura */
    .stApp { background-color: #FFFFFF; color: #1E293B; font-family: 'Inter', sans-serif; }
    .block-container { padding-top: 2rem !important; max-width: 95%; gap: 2rem; }

    /* Inputs Estilizados Prestige Clean */
    .stNumberInput, .stTextInput, .stSelectbox { 
        background-color: #F8FAFC !important; border: 1px solid #E2E8F0 !important; border-radius: 8px !important; margin-bottom: 2px !important; 
    }
    .stNumberInput input, .stTextInput input, .stSelectbox div[data-baseweb="select"] {
        color: #1E293B !important; font-size: 15px !important;
    }
    .stNumberInput label, .stTextInput label, .stSelectbox label {
        font-size: 0.7rem !important; font-weight: 700 !important; color: #64748B !important; text-transform: uppercase; margin-bottom: -5px !important;
    }

    /* Botão Principal Ultra (Deep Green) */
    div.stButton > button {
        background: linear-gradient(135deg, #064E3B 0%, #065F46 100%) !important;
        color: white !important; font-weight: 800; height: 3.5em; width: 100%; border-radius: 8px; border: none;
        box-shadow: 0 4px 12px rgba(6, 78, 59, 0.25);
    }

    /* Advisor Cards Estilizados Prestige Clean */
    .advice-card {
        padding: 18px 25px; border-radius: 10px; margin-bottom: 12px; border-left: 6px solid;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.03), 0 2px 4px -1px rgba(0,0,0,0.02);
    }
    .val-win { background-color: #ECFDF5; border-color: #059669; color: #064E3B; } /* Verde - Vitória Direta */
    .val-strat { background-color: #F0F9FF; border-color: #0EA5E9; color: #075985; } /* Azul - Proteção/Golos */
    .val-neutral { background-color: #F1F5F9; border-color: #94A3B8; color: #1E293B; }

    /* Tabela Bloomberg Style Refined */
    .stTable { font-size: 0.85rem !important; border-radius: 10px !important; overflow: hidden; border: 1px solid #E2E8F0; }
    thead tr th { background-color: #F8FAFC !important; border-bottom: 2px solid #E2E8F0 !important; font-weight: 800 !important; }
    
    /* Alerta Champions Moderno */
    .ctx-alert {
        padding: 15px; background-color: #FFFBEB; border-left: 5px solid #F59E0B;
        color: #92400E; font-weight: bold; margin-bottom: 20px; border-radius: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

# Função de Reset Blindada
def reset_ultra():
    for key in list(st.session_state.keys()):
        del st.session_state[key]

# Título Prestige Clean
st.markdown("<h2 style='color:#1E293B; font-weight:800; margin-bottom:5px; letter-spacing: -1px;'>🏛️ STARLINE // OMNI-QUANT <span style='color:#059669; font-size:14px; font-weight:400; letter-spacing: 0px;'>V35.1 ULTRA 1M</span></h2>", unsafe_allow_html=True)
st.markdown("---")

# Layout de Colunas Respirável
col_in, col_out = st.columns([1.1, 2], gap="large")

with col_in:
    # 1. Configuração e Equipas
    st.caption("CONTEXTO ESTRATÉGICO")
    ctx = st.selectbox("", ["Liga (Regular)", "Champions/Taça (Playoff)"], key="ctx", label_visibility="collapsed")
    
    c_teams1, c_teams2 = st.columns(2)
    h_n = c_teams1.text_input("HOME", value="LEIPZIG", key="h_n").upper()
    a_n = c_teams2.text_input("AWAY", value="HOFFENHEIM", key="a_n").upper()
    
    # 2. Stats (Grelha Respirável V35.1)
    st.markdown("<p style='font-size:11px; font-weight:800; color:#64748B; margin: 10px 0px 2px 0px;'>DADOS GF/GA (5 JOGOS)</p>", unsafe_allow_html=True)
    c_s1, c_s2, c_s3, c_s4 = st.columns(4)
    v_hgf, v_hga, v_agf, v_aga = c_s1.number_input("H-GF", 8.0), c_s2.number_input("H-GA", 12.0), c_s3.number_input("A-GF", 12.0), c_s4.number_input("A-GA", 10.0)
    
    # 3. Odds Grid Prestige
    st.markdown("<p style='font-size:11px; font-weight:800; color:#64748B; margin: 10px 0px 2px 0px;'>LIVE MARKET ODDS</p>", unsafe_allow_html=True)
    c_o1, c_o2, c_o3, c_o4 = st.columns(4)
    m_o1, m_ox, m_o2, m_ob = c_o1.number_input("1", 1.88), c_o2.number_input("X", 4.00), c_o3.number_input("2", 3.35), c_o4.number_input("BTTS", 1.32)
    
    c_o5, c_o6, c_o7, c_o8 = st.columns(4)
    m_o15, m_o25, m_o35, m_hah = c_o5.number_input("+1.5", 1.10), c_o6.number_input("+2.5", 1.33), c_o7.number_input("+3.5", 1.78), c_o8.number_input("DNB-H", 1.33)

    c_o9, c_o10, c_o11, c_o12 = st.columns(4)
    m_u15, m_u25, m_u35, m_haa = c_o9.number_input("-1.5", 4.55), c_o10.number_input("-2.5", 2.65), c_o11.number_input("-3.5", 1.75), c_o12.number_input("DNB-A", 1.85)

    # Ação Ultra
    btn_run = st.button("🚀 EXECUTAR 1.000.000 SIMULAÇÕES")
    st.button("🗑️ RESET ENGINE", on_click=reset_ultra)

# --- PROCESSAMENTO ULTRA 1M (O Cérebro) ---
if btn_run:
    try:
        adj = 0.67 if "Champions" in ctx else 1.0
        lh, la = ((v_hgf/5)*(v_aga/5))**0.5, ((v_agf*adj/5)*(v_hga/5))**0.5
        
        # Simulação Ultra 1M (Processamento Vetorizado)
        sim_h, sim_a = np.random.poisson(lh, 1000000), np.random.poisson(la, 1000000)
        stot = sim_h + sim_a
        
        ph, px, pa = np.mean(sim_h > sim_a), np.mean(sim_h == sim_a), np.mean(sim_h < sim_a)
        norm = ph + px + pa
        ph, px, pa = ph/norm, px/norm, pa/norm

        with col_out:
            st.markdown("#### 🎯 ULTRA ADVISOR PRO (DEEP INTERPRETATION)")
            
            # Mercados base para análise
            mkts = [
                (f"1X2: {h_n}", ph, m_o1, "VITÓRIA"), (f"1X2: {a_n}", pa, m_o2, "VITÓRIA"),
                ("BTTS: YES", np.mean((sim_h>0)&(sim_a>0)), m_ob, "GOLOS"),
                ("OVER 2.5", np.mean(stot>2.5), m_o25, "GOLOS"),
                ("DNB: HOME", ph/(ph+pa), m_hah, "PROTEÇÃO"),
                ("DNB: AWAY", pa/(ph+pa), m_haa, "PROTEÇÃO")
            ]
            
            # Lógica Advisor V35.1 Prestige Clean
            recoms = sorted([(n, p, b, (p*b)-1, t) for n, p, b, t in mkts if (p*b)-1 > 0.04], key=lambda x: x[3], reverse=True)

            if recoms:
                for n, p, b, e, t in recoms[:3]:
                    style_class = "val-win" if t == "VITÓRIA" else "val-strat"
                    icon = "🚀" if t == "VITÓRIA" else "🛡️"
                    st.markdown(f"""
                    <div class="advice-card {style_class}">
                        {icon} <b>{t}: {n}</b><br>
                        Confiança: <b>{p:.1%}</b> | Edge: <b>{e:+.1%}</b> | Odd Real: <b style='color:#1E293B'>{b:.2f}</b>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown('<div class="advice-card val-neutral">🛑 CONSELHO ULTRA: Sem Edge clara acima de 4% detetada em 1M de ciclos. Evite entradas.</div>', unsafe_allow_html=True)

            # Tabela de Mercados (O Heatmap)
            full_list = mkts + [("1X2: DRAW", px, m_ox, "EMPATE"), ("OVER 1.5", np.mean(stot>1.5), m_o15, "GOLOS"), ("OVER 3.5", np.mean(stot>3.5), m_o35, "GOLOS"), ("UNDER 2.5", 1 - np.mean(stot>2.5), m_u25, "GOLOS")]
            res_data, ev_styles = [], []
            for n, p, b, _ in full_list:
                edge = (p * b) - 1
                bg = "rgba(5, 150, 105, 0.12)" if edge > 0.10 else "rgba(245, 158, 11, 0.12)" if edge > 0 else "none"
                ev_styles.append(bg)
                res_data.append({"MERCADO": n, "PROB": f"{p:.1%}", "FAIR": f"{1/p:.2f}", "CASA": f"{b:.2f}", "EDGE": f"{edge:+.1%}"})

            st.table(pd.DataFrame(res_data).style.apply(lambda r: [f'background-color: {ev_styles[r.name]}'] * len(r), axis=1))

            # Scores (Dixon-Coles integrando as 1M simulações)
            st.write("**PROBABLE SCORES (ULTRA MODEL V35)**")
            hp, ap = poisson.pmf(range(6), lh), poisson.pmf(range(6), la)
            mtx = np.outer(hp, ap)
            mtx[0,0] *= 1.12; mtx[1,1] *= 1.08 # Ajuste de Elite
            mtx /= mtx.sum()
            idx = np.unravel_index(np.argsort(mtx.ravel())[-5:], mtx.shape)
            scs = st.columns(5)
            for j in range(4, -1, -1):
                with scs[4-j]: st.metric(f"{idx[0][j]}-{idx[1][j]}", f"{mtx[idx[0][j], idx[1][j]]:.1%}")

    except Exception as e: st.error(f"ENGINE ERROR V35.1: {e}")
