import streamlit as st
import numpy as np
from scipy.stats import poisson
import pandas as pd
import plotly.graph_objects as go

# 1. Configuração de Terminal de Luxo de 2026
st.set_page_config(
    page_title="STARLINE V81 // SOVEREIGN INTEL",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. CSS Quantum Glass (Foco em Advisor e Heatmap de Tabela)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800&family=JetBrains+Mono:wght@400;700&display=swap');
    
    .stApp {
        background: radial-gradient(circle at top right, #0F172A, #000000);
        color: #F8FAFC;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* Sidebar Glassmorphism Profundo */
    [data-testid="stSidebar"] {
        background: rgba(10, 10, 15, 0.85) !important;
        backdrop-filter: blur(25px);
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }

    .stNumberInput, .stTextInput, .stSelectbox { 
        background-color: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 10px !important;
        color: #00FF88 !important;
    }

    /* Advisor Cards Estilizados */
    .advisor-card {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 16px;
        padding: 20px;
        border-left: 8px solid #00FF88;
        margin-bottom: 15px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    .advisor-header { font-size: 0.7rem; font-weight: 800; color: #64748B; text-transform: uppercase; letter-spacing: 2px; }
    .advisor-title { font-size: 1.4rem; font-weight: 800; color: #FFFFFF; margin: 5px 0; }
    .advisor-stat { font-family: 'JetBrains Mono'; font-size: 0.9rem; color: #00FF88; }

    /* Matrix Table Heatmap */
    .matrix-table { width: 100%; border-collapse: separate; border-spacing: 0 4px; margin-top: 10px; }
    .matrix-table th { background: rgba(255, 255, 255, 0.05); color: #94A3B8; padding: 12px; font-size: 0.7rem; text-transform: uppercase; text-align: left; }
    .matrix-table td { padding: 14px 12px; font-size: 0.9rem; border-top: 1px solid rgba(255, 255, 255, 0.02); }
    .matrix-table tr td:first-child { border-radius: 8px 0 0 8px; font-weight: 700; }
    .matrix-table tr td:last-child { border-radius: 0 8px 8px 0; }

    div.stButton > button {
        background: linear-gradient(90deg, #00FF88 0%, #00BD63 100%) !important;
        color: #000000 !important; font-weight: 800; height: 4em; width: 100%; border-radius: 12px; border: none;
        text-transform: uppercase; letter-spacing: 2px;
    }
    </style>
    """, unsafe_allow_html=True)

def reset():
    for key in list(st.session_state.keys()): del st.session_state[key]

# --- SIDEBAR: INPUT DE ELITE ---
with st.sidebar:
    st.markdown("<h1 style='font-size:22px; color:#00FF88;'>🏛️ SOVEREIGN COMMAND</h1>", unsafe_allow_html=True)
    ctx = st.selectbox("CONTEXTO", ["LIGA", "TAÇA/ELIMINATÓRIA"], key="v81_ctx")
    
    st.markdown("---")
    h_n = st.text_input("HOME", "LEIPZIG", key="v81_hn").upper()
    a_n = st.text_input("AWAY", "HOFFENHEIM", key="v81_an").upper()
    
    col1, col2 = st.columns(2)
    hgf = col1.number_input("H-GF", 8.0); hga = col2.number_input("H-GA", 12.0)
    agf = col1.number_input("A-GF", 12.0); aga = col2.number_input("A-GA", 10.0)
    
    st.markdown("---")
    m1 = st.number_input("ODD 1", 1.88); mx = st.number_input("ODD X", 4.00); m2 = st.number_input("ODD 2", 3.35)
    m_ob = st.number_input("BTTS YES", 1.32)
    
    o15, o25, o35 = st.columns(3)
    m_o15 = o15.number_input("+1.5", 1.10); m_o25 = o25.number_input("+2.5", 1.33); m_o35 = o35.number_input("+3.5", 1.78)
    u15, u25, u35 = st.columns(3)
    m_u15 = u15.number_input("-1.5", 4.55); m_u25 = u25.number_input("-2.5", 2.65); m_u35 = u35.number_input("-3.5", 1.75)
    
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

        c_top1, c_top2 = st.columns([1.1, 0.9])
        
        with c_top1:
            st.markdown("### 🎯 QUANTUM ADVISOR")
            # Lista de Mercados para o Advisor
            all_mkts = [
                ("1X2: "+h_n, ph, m1, "WIN"), ("1X2: DRAW", px, mx, "DRAW"), ("1X2: "+a_n, pa, m2, "WIN"),
                ("BTTS: YES", np.mean((sim_h>0)&(sim_a>0)), m_ob, "GOAL"),
                ("OVER 1.5", np.mean(stot>1.5), m_o15, "GOAL"), ("OVER 2.5", np.mean(stot>2.5), m_o25, "GOAL"),
                ("UNDER 2.5", np.mean(stot<2.5), m_u25, "UNDER"), ("UNDER 3.5", np.mean(stot<3.5), m_u35, "UNDER")
            ]
            
            # Seleção das 2 Melhores Edges
            recoms = sorted([(n, p, b, (p*b)-1, t) for n, p, b, t in all_mkts if (p*b)-1 > 0.05], key=lambda x: x[3], reverse=True)
            
            if recoms:
                for name, p, b, edge, mtype in recoms[:2]:
                    color = "#00FF88" if mtype == "WIN" else "#3B82F6" if mtype == "UNDER" else "#FACC15"
                    st.markdown(f"""
                        <div class="advisor-card" style="border-left-color: {color};">
                            <div class="advisor-header">{mtype} SIGNAL // CONFIDANCE: {p:.1%}</div>
                            <div class="advisor-title">{name}</div>
                            <div class="advisor-stat">ALPHA EDGE: {edge:+.1%} | ODD: {b:.2f} (FAIR: {1/p:.2f})</div>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown("<div class='advisor-card' style='border-left-color: #64748B;'>NO HIGH EDGE SIGNALS DETECTED</div>", unsafe_allow_html=True)

        with c_top2:
            fig = go.Figure()
            xr = list(range(6))
            fig.add_trace(go.Scatter(x=xr, y=[poisson.pmf(i, lh) for i in xr], name=h_n, fill='tozeroy', line_color='#00FF88'))
            fig.add_trace(go.Scatter(x=xr, y=[poisson.pmf(i, la) for i in xr], name=a_n, fill='tozeroy', line_color='#3B82F6'))
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white", height=280, margin=dict(l=0,r=0,t=20,b=0))
            st.plotly_chart(fig, use_container_width=True)

        # --- MATRIX COM HEATMAP DE CORES ---
        st.markdown("### 💎 MARKET MATRIX (HEATMAP ACTIVE)")
        
        html = "<table class='matrix-table'><thead><tr><th>MERCADO</th><th>PROB.</th><th>JUSTA</th><th>CASA</th><th>EDGE (%)</th></tr></thead><tbody>"
        for name, p, b, t in all_mkts:
            edge = (p * b) - 1
            # Cores dinâmicas na Edge
            edge_color = "#00FF88" if edge > 0.12 else "#FACC15" if edge > 0.02 else "#F87171"
            # Opacidade e fundo de aposta
            bg_cell = "rgba(0, 255, 136, 0.08)" if edge > 0.08 else "transparent"
            op = "1" if edge > 0 else "0.3"
            
            html += f"""
                <tr style='opacity:{op}; background-color:{bg_cell};'>
                    <td>{name}</td>
                    <td>{p:.1%}</td>
                    <td>{1/p:.2f}</td>
                    <td style='color:#00FF88; font-weight:800;'>{b:.2f}</td>
                    <td style='color:{edge_color}; font-weight:800;'>{edge:+.1%}</td>
                </tr>
            """
        html += "</tbody></table>"
        st.markdown(html, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"ENGINE ERROR V81: {e}")
else:
    st.markdown("<div style='text-align:center; margin-top:20%; opacity:0.2;'><h1>SOVEREIGN ENGINE IDLE</h1></div>", unsafe_allow_html=True)
