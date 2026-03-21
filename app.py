import streamlit as st
import numpy as np
from scipy.stats import poisson
import pandas as pd
import plotly.graph_objects as go

# 1. Configuração de Sistema de Alta Performance
st.set_page_config(
    page_title="STARLINE V82 // QUANTUM MATRIX",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. CSS Quantum Sovereign (Otimizado para Visualização de Dados)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800&family=JetBrains+Mono:wght@400;700&display=swap');
    
    .stApp {
        background: radial-gradient(circle at top right, #0F172A, #000000);
        color: #F8FAFC;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    [data-testid="stSidebar"] {
        background: rgba(10, 10, 15, 0.9) !important;
        backdrop-filter: blur(25px);
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }

    .stNumberInput, .stTextInput, .stSelectbox { 
        background-color: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 10px !important;
        color: #00FF88 !important;
    }

    label { font-size: 0.7rem !important; font-weight: 800 !important; color: #64748B !important; text-transform: uppercase; }

    /* Estilização do Advisor */
    .advisor-card {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 16px;
        padding: 24px;
        border-left: 8px solid #00FF88;
        margin-bottom: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    
    div.stButton > button {
        background: linear-gradient(90deg, #00FF88 0%, #00BD63 100%) !important;
        color: #000000 !important; font-weight: 800; height: 4em; width: 100%; border-radius: 12px; border: none;
        text-transform: uppercase; letter-spacing: 2px;
    }
    </style>
    """, unsafe_allow_html=True)

def reset():
    for key in list(st.session_state.keys()): del st.session_state[key]

# --- SIDEBAR: CONTROLO DE DADOS ---
with st.sidebar:
    st.markdown("<h1 style='font-size:22px; color:#00FF88;'>🏛️ SOVEREIGN COMMAND</h1>", unsafe_allow_html=True)
    ctx = st.selectbox("ESTRATÉGIA", ["LIGA", "TAÇA/ELIMINATÓRIA"], key="v82_ctx")
    
    st.markdown("---")
    h_n = st.text_input("HOME", "LEIPZIG", key="v82_hn").upper()
    a_n = st.text_input("AWAY", "HOFFENHEIM", key="v82_an").upper()
    
    col1, col2 = st.columns(2)
    hgf = col1.number_input("H-GF", value=8.0); hga = col2.number_input("H-GA", value=12.0)
    agf = col1.number_input("A-GF", value=12.0); aga = col2.number_input("A-GA", value=10.0)
    
    st.markdown("---")
    st.write("ODDS MERCADO")
    m1 = st.number_input("ODD 1", 1.88); mx = st.number_input("ODD X", 4.00); m2 = st.number_input("ODD 2", 3.35)
    
    o15, o25, u25 = st.columns(3)
    m_o15 = o15.number_input("+1.5", 1.10); m_o25 = o25.number_input("+2.5", 1.33); m_u25 = u25.number_input("-2.5", 2.65)
    
    m_ob = st.number_input("BTTS YES", 1.32); m_hah = st.number_input("DNB HOME", 1.33)
    
    st.markdown("<br>", unsafe_allow_html=True)
    run = st.button("🚀 EXECUTAR QUANTUM ENGINE")
    st.button("🗑️ RESET TERMINAL", on_click=reset)

# --- PAINEL PRINCIPAL ---
if run:
    try:
        # Matemática de Precisão 1M
        adj = 0.67 if "TAÇA" in ctx else 1.0
        lh, la = max(0.01, ((hgf/5)*(aga/5))**0.5), max(0.01, ((agf*adj/5)*(hga/5))**0.5)
        sim_h, sim_a = np.random.poisson(lh, 1000000), np.random.poisson(la, 1000000)
        stot = sim_h + sim_a
        ph, px, pa = np.mean(sim_h > sim_a), np.mean(sim_h == sim_a), np.mean(sim_h < sim_a)
        ph, px, pa = ph/(ph+px+pa), px/(ph+px+pa), pa/(ph+px+pa)

        st.markdown(f"<h1 style='letter-spacing:-2px; margin:0;'>{h_n} vs {a_n}</h1>", unsafe_allow_html=True)

        c_top, c_graph = st.columns([1.1, 0.9])
        
        with c_top:
            st.markdown("### 🎯 QUANTUM ADVISOR")
            mkts = [
                ("1X2: "+h_n, ph, m1, "WIN"), ("1X2: "+a_n, pa, m2, "WIN"),
                ("BTTS: YES", np.mean((sim_h>0)&(sim_a>0)), m_ob, "GOAL"),
                ("OVER 2.5", np.mean(stot>2.5), m_o25, "GOAL"),
                ("UNDER 2.5", np.mean(stot<2.5), m_u25, "UNDER")
            ]
            recoms = sorted([(n, p, b, (p*b)-1, t) for n, p, b, t in mkts if (p*b)-1 > 0.05], key=lambda x: x[3], reverse=True)
            
            if recoms:
                name, p, b, edge, mtype = recoms[0]
                color = "#00FF88" if mtype == "WIN" else "#3B82F6" if mtype == "UNDER" else "#FACC15"
                st.markdown(f"""
                    <div class="advisor-card" style="border-left-color: {color};">
                        <div style="font-size:0.7rem; font-weight:800; color:#64748B; letter-spacing:2px;">{mtype} SIGNAL // EDGE: {edge:+.1%}</div>
                        <div style="font-size:1.6rem; font-weight:800; color:white; margin:5px 0;">{name}</div>
                        <div style="font-family:'JetBrains Mono'; color:{color}; font-size:1rem;">CONFIDANCE: {p:.1%} | ODD: {b:.2f} (FAIR: {1/p:.2f})</div>
                    </div>
                """, unsafe_allow_html=True)

        with c_graph:
            xr = list(range(6))
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=xr, y=[poisson.pmf(i, lh) for i in xr], name=h_n, fill='tozeroy', line_color='#00FF88'))
            fig.add_trace(go.Scatter(x=xr, y=[poisson.pmf(i, la) for i in xr], name=a_n, fill='tozeroy', line_color='#3B82F6'))
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white", height=250, margin=dict(l=0,r=0,t=0,b=0))
            st.plotly_chart(fig, use_container_width=True)

        # --- THE MATRIX BREAKTHROUGH (REDUX) ---
        st.markdown("### 💎 MARKET MATRIX (HEATMAP ACTIVE)")
        
        # HTML Robusto com CSS embutido para evitar erros de renderização
        html_code = """
        <div style="background:transparent; font-family:'Plus Jakarta Sans', sans-serif;">
        <table style="width:100%; border-collapse:separate; border-spacing:0 8px; color:white;">
            <thead>
                <tr style="color:#64748B; font-size:12px; text-transform:uppercase;">
                    <th style="text-align:left; padding:15px;">Mercado</th>
                    <th style="text-align:left; padding:15px;">Prob.</th>
                    <th style="text-align:left; padding:15px;">Justa</th>
                    <th style="text-align:left; padding:15px;">Casa</th>
                    <th style="text-align:left; padding:15px;">Edge</th>
                </tr>
            </thead>
            <tbody>
        """
        
        for name, p, b, t in mkts + [("1X2: DRAW", px, mx, "DRAW"), ("OVER 1.5", np.mean(stot>1.5), m_o15, "GOAL"), ("DNB: HOME", ph/(ph+pa), m_hah, "PROT")]:
            edge = (p * b) - 1
            color = "#00FF88" if edge > 0.12 else "#FACC15" if edge > 0 else "#F87171"
            bg = "rgba(0, 255, 136, 0.08)" if edge > 0.08 else "rgba(255,255,255,0.01)"
            opacity = "1" if edge > 0 else "0.3"
            
            html_code += f"""
            <tr style="background:{bg}; opacity:{opacity};">
                <td style="padding:15px; border-radius:12px 0 0 12px; font-weight:700;">{name}</td>
                <td style="padding:15px;">{p:.1%}</td>
                <td style="padding:15px;">{1/p:.2f}</td>
                <td style="padding:15px; color:#00FF88; font-weight:800;">{b:.2f}</td>
                <td style="padding:15px; color:{color}; font-weight:800;">{edge:+.1%}</td>
            </tr>
            """
        
        html_code += "</tbody></table></div>"
        
        # Renderização via markdown com proteção adicional
        st.markdown(html_code, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"ENGINE ERROR V82: {e}")
else:
    st.markdown("<div style='text-align:center; margin-top:20%; opacity:0.2;'><h1>SOVEREIGN ENGINE IDLE</h1></div>", unsafe_allow_html=True)
