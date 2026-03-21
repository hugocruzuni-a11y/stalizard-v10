import streamlit as st
import numpy as np
from scipy.stats import poisson
import pandas as pd
import plotly.graph_objects as go

# 1. Configuração de Terminal de Investimento de Luxo
st.set_page_config(
    page_title="STARLINE V80 // QUANTUM SOVEREIGN",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. CSS "Sovereign Glass" (Design 2026 de Alta Performance)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800&family=JetBrains+Mono:wght@400;700&display=swap');
    
    .stApp {
        background: radial-gradient(circle at top right, #0F172A, #000000);
        color: #F8FAFC;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    [data-testid="stSidebar"] {
        background: rgba(10, 10, 15, 0.8) !important;
        backdrop-filter: blur(25px);
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }

    .stNumberInput, .stTextInput, .stSelectbox { 
        background-color: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 10px !important;
        color: #00FF88 !important;
    }
    
    label { font-size: 0.7rem !important; font-weight: 800 !important; color: #64748B !important; text-transform: uppercase; letter-spacing: 1px; }

    div.stButton > button {
        background: linear-gradient(90deg, #00FF88 0%, #00BD63 100%) !important;
        color: #000000 !important; font-weight: 800; height: 4em; width: 100%; border-radius: 12px; border: none;
        text-transform: uppercase; letter-spacing: 2px; box-shadow: 0 10px 30px rgba(0, 255, 136, 0.2);
    }

    .matrix-table { width: 100%; border-collapse: separate; border-spacing: 0 6px; margin-top: 20px; color: white; }
    .matrix-table th { background: rgba(255, 255, 255, 0.05); color: #94A3B8; padding: 12px 15px; font-size: 0.7rem; text-transform: uppercase; text-align: left; }
    .matrix-table td { background: rgba(255, 255, 255, 0.02); padding: 14px 15px; font-size: 0.9rem; border-top: 1px solid rgba(255, 255, 255, 0.03); }
    .matrix-table tr td:first-child { border-radius: 8px 0 0 8px; font-weight: 700; }
    .matrix-table tr td:last-child { border-radius: 0 8px 8px 0; }

    .metric-card {
        background: rgba(255, 255, 255, 0.02); padding: 15px; border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.05); text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

def reset():
    for key in list(st.session_state.keys()): del st.session_state[key]

# --- SIDEBAR: CONTROLO TOTAL ---
with st.sidebar:
    st.markdown("<h1 style='font-size:22px; color:#00FF88;'>🏛️ SOVEREIGN COMMAND</h1>", unsafe_allow_html=True)
    ctx = st.selectbox("CONTEXTO", ["LIGA", "TAÇA/ELIMINATÓRIA"], key="v80_ctx")
    
    st.markdown("---")
    h_n = st.text_input("HOME", "LEIPZIG", key="v80_hn").upper()
    a_n = st.text_input("AWAY", "HOFFENHEIM", key="v80_an").upper()
    
    st.write("DADOS GF/GA (5 JOGOS)")
    c1, c2 = st.columns(2)
    hgf = c1.number_input("H-GF", value=8.0); hga = c2.number_input("H-GA", value=12.0)
    agf = c1.number_input("A-GF", value=12.0); aga = c2.number_input("A-GA", value=10.0)
    
    st.markdown("---")
    st.write("ODDS 1X2 & BTTS")
    m1 = st.number_input("ODD 1", 1.88); mx = st.number_input("ODD X", 4.00); m2 = st.number_input("ODD 2", 3.35)
    m_ob = st.number_input("BTTS YES", 1.32)
    
    st.write("ODDS OVER/UNDER")
    o15, o25, o35 = st.columns(3)
    m_o15 = o15.number_input("+1.5", 1.10); m_o25 = o25.number_input("+2.5", 1.33); m_o35 = o35.number_input("+3.5", 1.78)
    u15, u25, u35 = st.columns(3)
    m_u15 = u15.number_input("-1.5", 4.55); m_u25 = u25.number_input("-2.5", 2.65); m_u35 = u35.number_input("-3.5", 1.75)
    
    st.write("OUTROS")
    m_hah = st.number_input("DNB HOME", 1.33); m_haa = st.number_input("DNB AWAY", 1.85)
    
    st.markdown("<br>", unsafe_allow_html=True)
    run = st.button("🚀 EXECUTAR QUANTUM ENGINE")
    st.button("🗑️ RESET TERMINAL", on_click=reset)

# --- PAINEL PRINCIPAL ---
if not run:
    st.markdown("<div style='text-align:center; margin-top:20%; opacity:0.2;'><h1>SOVEREIGN ENGINE IDLE</h1></div>", unsafe_allow_html=True)
else:
    try:
        # 1. Matemática de Precisão (Poisson + Monte Carlo 1M)
        adj = 0.67 if "TAÇA" in ctx else 1.0
        lh = max(0.01, ((hgf/5)*(aga/5))**0.5)
        la = max(0.01, ((agf*adj/5)*(hga/5))**0.5)
        
        sim_h, sim_a = np.random.poisson(lh, 1000000), np.random.poisson(la, 1000000)
        stot = sim_h + sim_a
        
        # Probabilidades Base
        ph, px, pa = np.mean(sim_h > sim_a), np.mean(sim_h == sim_a), np.mean(sim_h < sim_a)
        ph, px, pa = ph/(ph+px+pa), px/(ph+px+pa), pa/(ph+px+pa)

        st.markdown(f"<h1 style='letter-spacing:-2px;'>{h_n} vs {a_n}</h1>", unsafe_allow_html=True)

        # 2. Visual Analytics
        c_v1, c_v2 = st.columns([1.2, 0.8])
        with c_v1:
            xr = list(range(7))
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=xr, y=[poisson.pmf(i, lh) for i in xr], name=h_n, fill='tozeroy', line_color='#00FF88', line_width=3))
            fig.add_trace(go.Scatter(x=xr, y=[poisson.pmf(i, la) for i in xr], name=a_n, fill='tozeroy', line_color='#3B82F6', line_width=3))
            fig.update_layout(title="CURVAS DE GOLOS (POISSON)", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white", height=320, margin=dict(l=0,r=0,t=40,b=0))
            st.plotly_chart(fig, use_container_width=True)

        with c_v2:
            # Gauge da Melhor Oportunidade
            m_list = [
                ("WIN "+h_n, ph, m1), ("DRAW", px, mx), ("WIN "+a_n, pa, m2),
                ("OVER 2.5", np.mean(stot>2.5), m_o25), ("UNDER 2.5", np.mean(stot<2.5), m_u25)
            ]
            best = max(m_list, key=lambda x: (x[1]*x[2])-1)
            fig_g = go.Figure(go.Indicator(
                mode = "gauge+number", value = ((best[1]*best[2])-1)*100,
                title = {'text': f"TOP EDGE: {best[0]}", 'font': {'size': 14, 'color': '#94A3B8'}},
                gauge = {'axis': {'range': [0, 40]}, 'bar': {'color': "#00FF88"}, 'bgcolor': "rgba(255,255,255,0.05)"},
                number = {'suffix': "%", 'font': {'size': 35, 'color': '#00FF88'}}
            ))
            fig_g.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="white", height=320)
            st.plotly_chart(fig_g, use_container_width=True)

        # 3. MATRIX TOTAL DE MERCADOS (TODOS)
        st.markdown("### 💎 QUANTUM MARKET MATRIX (Mapeamento Completo)")
        
        # Definição de todos os mercados
        all_mkts = [
            ("1X2: HOME", ph, m1),
            ("1X2: DRAW", px, mx),
            ("1X2: AWAY", pa, m2),
            ("D. CHANCE: 1X", ph+px, 1/( (1/m1)+(1/mx) )),
            ("D. CHANCE: X2", pa+px, 1/( (1/m2)+(1/mx) )),
            ("BTTS: YES", np.mean((sim_h>0)&(sim_a>0)), m_ob),
            ("OVER 0.5", np.mean(stot>0.5), 1.05), # Odds estimadas se não fornecidas
            ("OVER 1.5", np.mean(stot>1.5), m_o15),
            ("OVER 2.5", np.mean(stot>2.5), m_o25),
            ("OVER 3.5", np.mean(stot>3.5), m_o35),
            ("UNDER 1.5", np.mean(stot<1.5), m_u15),
            ("UNDER 2.5", np.mean(stot<2.5), m_u25),
            ("UNDER 3.5", np.mean(stot<3.5), m_u35),
            ("DNB: HOME", ph/(ph+pa), m_hah),
            ("DNB: AWAY", pa/(ph+pa), m_haa)
        ]

        html = "<table class='matrix-table'><thead><tr><th>MERCADO</th><th>PROB.</th><th>JUSTA</th><th>CASA</th><th>EDGE (%)</th></tr></thead><tbody>"
        for name, p, b in all_mkts:
            edge = (p * b) - 1
            clr = "#00FF88" if edge > 0.10 else "#FACC15" if edge > 0 else "#F87171"
            op = "1" if edge > 0 else "0.3"
            html += f"<tr style='opacity:{op};'><td>{name}</td><td>{p:.1%}</td><td>{1/p:.2f}</td><td style='color:#00FF88; font-weight:800;'>{b:.2f}</td><td style='color:{clr}; font-weight:800;'>{edge:+.1%}</td></tr>"
        html += "</tbody></table>"
        st.markdown(html, unsafe_allow_html=True)

        # 4. Scores e Precisão
        st.markdown("<br>", unsafe_allow_html=True)
        hp, ap = poisson.pmf(range(5), lh), poisson.pmf(range(5), la)
        mtx = np.outer(hp, ap); mtx /= mtx.sum()
        idx = np.unravel_index(np.argsort(mtx.ravel())[-3:], mtx.shape)
        sc = st.columns(3)
        for j in range(2, -1, -1):
            sc[2-j].markdown(f"<div class='metric-card'><p style='margin:0; font-size:12px; color:#64748B;'>SCORE PREVISTO</p><h3 style='margin:0;'>{idx[0][j]} - {idx[1][j]}</h3><p style='margin:0; color:#00FF88;'>{mtx[idx[0][j], idx[1][j]]:.1%}</p></div>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"ENGINE ERROR V80: {e}")
