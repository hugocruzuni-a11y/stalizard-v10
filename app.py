import streamlit as st
import numpy as np
from scipy.stats import poisson
import pandas as pd

# 1. Configuração Starline Ultra
st.set_page_config(page_title="STARLINE ULTRA V35", layout="wide")

# 2. CSS Elite (Design Prestige)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;800&display=swap');
    .stApp { background-color: #FFFFFF; color: #1E293B; font-family: 'Inter', sans-serif; }
    
    /* Contentores de Input com mais definição */
    div[data-testid="stVerticalBlock"] > div { 
        background-color: #FDFDFD; 
        border: 1px solid #F1F5F9;
        border-radius: 10px; 
        padding: 15px; 
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }

    /* Botão Principal Ultra */
    div.stButton > button {
        background: linear-gradient(135deg, #064E3B 0%, #065F46 100%) !important;
        color: white !important; font-weight: 800; height: 3.5em; width: 100%; border-radius: 8px; border: none;
        box-shadow: 0 4px 12px rgba(6, 78, 59, 0.25);
    }

    /* Advisor Cards Estilizados */
    .advice-card {
        padding: 15px 20px; border-radius: 8px; margin-bottom: 12px; border-left: 6px solid;
        font-size: 0.95rem; line-height: 1.4;
    }
    .val-win { background-color: #ECFDF5; border-color: #059669; color: #064E3B; } /* Verde para Vitórias */
    .val-strat { background-color: #F0F9FF; border-color: #0EA5E9; color: #075985; } /* Azul para Proteções/Golos */
    .val-neutral { background-color: #F8FAFC; border-color: #94A3B8; color: #475569; }

    /* Tabela Bloomberg Refined */
    .stTable { font-size: 0.85rem !important; border-radius: 10px !important; overflow: hidden; }
    thead tr th { background-color: #F1F5F9 !important; font-weight: 800 !important; color: #1E293B !important; }
    </style>
    """, unsafe_allow_html=True)

def reset_ultra():
    for key in list(st.session_state.keys()):
        del st.session_state[key]

# Título Prestige
st.markdown("<h2 style='color:#1E293B; font-weight:800; margin-bottom:5px;'>🏛️ STARLINE // OMNI-QUANT <span style='color:#059669; font-size:14px; font-weight:400;'>V35.0 ULTRA 1M</span></h2>", unsafe_allow_html=True)
st.markdown("---")

col_in, col_out = st.columns([1.1, 2], gap="large")

with col_in:
    st.caption("ESTRATÉGIA DE MERCADO")
    ctx = st.selectbox("", ["Liga (Regular)", "Champions/Taça (Playoff)"], key="ctx", label_visibility="collapsed")
    
    # Teams
    c1, c2 = st.columns(2)
    h_n = c1.text_input("HOME", value="LEIPZIG", key="h_n").upper()
    a_n = c2.text_input("AWAY", value="HOFFENHEIM", key="a_n").upper()
    
    # Stats
    st.markdown("<p style='font-size:11px; font-weight:800; color:#64748B; margin-bottom:2px;'>ESTATÍSTICAS GF/GA (5 JOGOS)</p>", unsafe_allow_html=True)
    s1, s2, s3, s4 = st.columns(4)
    v_hgf = s1.number_input("H-GF", 8.0)
    v_hga = s2.number_input("H-GA", 12.0)
    v_agf = s3.number_input("A-GF", 12.0)
    v_aga = s4.number_input("A-GA", 10.0)
    
    # Odds
    st.markdown("<p style='font-size:11px; font-weight:800; color:#64748B; margin-bottom:2px;'>LIVE MARKET ODDS</p>", unsafe_allow_html=True)
    g1 = st.columns(4)
    m_o1, m_ox, m_o2, m_ob = g1[0].number_input("1", 1.88), g1[1].number_input("X", 4.00), g1[2].number_input("2", 3.35), g1[3].number_input("BTTS", 1.32)
    
    g2 = st.columns(4)
    m_o15, m_o25, m_o35, m_hah = g2[0].number_input("+1.5", 1.10), g2[1].number_input("+2.5", 1.33), g2[2].number_input("+3.5", 1.78), g2[3].number_input("DNB-H", 1.33)

    g3 = st.columns(4)
    m_u15, m_u25, m_u35, m_haa = g3[0].number_input("-1.5", 4.55), g3[1].number_input("-2.5", 2.65), g3[2].number_input("-3.5", 1.75), g3[3].number_input("DNB-A", 1.85)

    btn_run = st.button("🚀 EXECUTAR 1.000.000 SIMULAÇÕES")
    st.button("🗑️ RESET ENGINE", on_click=reset_ultra)

if btn_run:
    try:
        # --- ENGINE 1M ---
        adj = 0.67 if "Champions" in ctx else 1.0
        lh, la = ((v_hgf/5)*(v_aga/5))**0.5, ((v_agf*adj/5)*(v_hga/5))**0.5
        
        sim_h = np.random.poisson(lh, 1000000)
        sim_a = np.random.poisson(la, 1000000)
        stot = sim_h + sim_a
        
        ph = np.mean(sim_h > sim_a)
        px = np.mean(sim_h == sim_a)
        pa = np.mean(sim_h < sim_a)
        norm = ph + px + pa
        ph, px, pa = ph/norm, px/norm, pa/norm

        with col_out:
            st.markdown("#### 🎯 ULTRA ADVISOR PRO")
            
            targets = [
                (f"1X2: {h_n}", ph, m_o1, "VITÓRIA"),
                (f"1X2: {a_n}", pa, m_o2, "VITÓRIA"),
                ("BTTS: YES", np.mean((sim_h>0)&(sim_a>0)), m_ob, "GOLOS"),
                ("OVER 2.5", np.mean(stot>2.5), m_o25, "GOLOS"),
                ("DNB: HOME", ph/(ph+pa), m_hah, "PROTEÇÃO"),
                ("DNB: AWAY", pa/(ph+pa), m_haa, "PROTEÇÃO")
            ]
            
            recoms = sorted([(n, p, b, (p*b)-1, t) for n, p, b, t in targets if (p*b)-1 > 0.04], key=lambda x: x[3], reverse=True)

            if recoms:
                for n, p, b, e, t in recoms[:3]:
                    style_class = "val-win" if t == "VITÓRIA" else "val-strat"
                    icon = "🚀" if t == "VITÓRIA" else "🛡️"
                    st.markdown(f"""
                    <div class="advice-card {style_class}">
                        {icon} <b>{t}: {n}</b><br>
                        Confiança: <b>{p:.1%}</b> | Edge: <b>{e:+.1%}</b> | Odd: <b>{b:.2f}</b>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown('<div class="advice-card val-neutral">🛑 MERCADO AJUSTADO: Edge inferior a 4% em 1M de ciclos.</div>', unsafe_allow_html=True)

            # Tabela Elite
            res_data, ev_styles = [], []
            for n, p, b, _ in targets + [("1X2: DRAW", px, m_ox)]:
                edge = (p * b) - 1
                bg = "rgba(5, 150, 105, 0.12)" if edge > 0.10 else "rgba(245, 158, 11, 0.12)" if edge > 0 else "none"
                ev_styles.append(bg)
                res_data.append({"MERCADO": n, "PROB": f"{p:.1%}", "FAIR": f"{1/p:.2f}", "CASA": f"{b:.2f}", "EDGE": f"{edge:+.1%}"})

            st.table(pd.DataFrame(res_data).style.apply(lambda r: [f'background-color: {ev_styles[r.name]}'] * len(r), axis=1))

            # Scores V35 (Dixon-Coles integrando as 1M simulações)
            st.write("**PROBABLE SCORES (ULTRA MODEL)**")
            hp, ap = poisson.pmf(range(6), lh), poisson.pmf(range(6), la)
            mtx = np.outer(hp, ap)
            mtx[0,0] *= 1.12; mtx[1,1] *= 1.08 # Ajuste de Elite para golos baixos
            mtx /= mtx.sum()
            idx = np.unravel_index(np.argsort(mtx.ravel())[-5:], mtx.shape)
            scs = st.columns(5)
            for j in range(4, -1, -1):
                with scs[4-j]: st.metric(f"{idx[0][j]}-{idx[1][j]}", f"{mtx[idx[0][j], idx[1][j]]:.1%}")

    except Exception as e: st.error(f"ENGINE ERROR V35: {e}")
