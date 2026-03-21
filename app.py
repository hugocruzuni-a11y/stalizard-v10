import streamlit as st
import numpy as np
from scipy.stats import poisson
import pandas as pd
import plotly.graph_objects as go

# 1. Configuração de Sistema High-End
st.set_page_config(
    page_title="STARLINE V70 // QUANTUM GLASS",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. CSS "Quantum Glass 2026" (Design de Luxo e Legibilidade Extrema)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800&family=JetBrains+Mono:wght@400;700&display=swap');
    
    /* Root & Background */
    .stApp {
        background: radial-gradient(circle at top right, #0F172A, #000000);
        color: #F8FAFC;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* Sidebar Glassmorphism */
    [data-testid="stSidebar"] {
        background: rgba(15, 23, 42, 0.7) !important;
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }

    /* Inputs Modernos - Sem limites visíveis */
    .stNumberInput, .stTextInput, .stSelectbox { 
        background-color: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        color: #00FF88 !important;
    }
    
    label {
        font-size: 0.75rem !important;
        font-weight: 600 !important;
        color: #94A3B8 !important;
        letter-spacing: 1px;
    }

    /* Botão de Execução Magnético */
    div.stButton > button {
        background: linear-gradient(90deg, #00FF88 0%, #00BD63 100%) !important;
        color: #000000 !important;
        font-weight: 800;
        height: 4.5em;
        width: 100%;
        border-radius: 14px;
        border: none;
        text-transform: uppercase;
        letter-spacing: 2px;
        box-shadow: 0 10px 30px rgba(0, 255, 136, 0.2);
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    div.stButton > button:hover {
        transform: translateY(-5px) scale(1.02);
        box-shadow: 0 15px 40px rgba(0, 255, 136, 0.4);
    }

    /* Tabela Estilo Bloomberg 2026 */
    .matrix-table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0 8px;
        margin-top: 20px;
    }
    .matrix-table th {
        background: rgba(255, 255, 255, 0.03);
        color: #64748B;
        padding: 16px;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    }
    .matrix-table td {
        background: rgba(255, 255, 255, 0.02);
        padding: 18px;
        font-size: 0.95rem;
        border-top: 1px solid rgba(255, 255, 255, 0.03);
        border-bottom: 1px solid rgba(255, 255, 255, 0.03);
    }
    .matrix-table tr td:first-child { border-left: 1px solid rgba(255, 255, 255, 0.03); border-radius: 12px 0 0 12px; }
    .matrix-table tr td:last-child { border-right: 1px solid rgba(255, 255, 255, 0.03); border-radius: 0 12px 12px 0; }

    /* Widgets de Valor */
    .metric-card {
        background: rgba(255, 255, 255, 0.02);
        padding: 20px;
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Funções de Suporte
def reset():
    for key in list(st.session_state.keys()): del st.session_state[key]

# --- SIDEBAR: O CENTRO DE COMANDO ---
with st.sidebar:
    st.markdown("<h1 style='font-size:24px; color:#00FF88; margin-bottom:0;'>⚙️ COMMAND</h1>", unsafe_allow_html=True)
    st.caption("OMNI-QUANT ENGINE V70.0")
    
    bank = st.number_input("BANKROLL (€)", value=1000.0, step=100.0)
    ctx = st.selectbox("STRATEGY", ["LEAGUE / REGULAR", "CUP / KNOCKOUT"])
    
    st.markdown("---")
    h_n = st.text_input("HOME TEAM", "VILLARREAL").upper()
    a_n = st.text_input("AWAY TEAM", "REAL SOCIEDAD").upper()
    
    st.write("STATS (LAST 5)")
    c1, c2 = st.columns(2)
    hgf = c1.number_input("H-GF", value=9.0, step=0.1)
    hga = c2.number_input("H-GA", value=7.0, step=0.1)
    agf = c1.number_input("A-GF", value=12.0, step=0.1)
    aga = c2.number_input("A-GA", value=10.0, step=0.1)
    
    st.markdown("---")
    st.write("LIVE MARKET QUOTES")
    m1 = st.number_input("ODD 1", value=1.88, step=0.01)
    mx = st.number_input("ODD X", value=4.00, step=0.01)
    m2 = st.number_input("ODD 2", value=3.35, step=0.01)
    
    m_o15 = st.number_input("OVER 1.5", value=1.10)
    m_o25 = st.number_input("OVER 2.5", value=1.33)
    m_u25 = st.number_input("UNDER 2.5", value=2.65)
    m_ob = st.number_input("BTTS YES", value=1.32)
    
    st.markdown("<br>", unsafe_allow_html=True)
    run = st.button("🚀 EXECUTE QUANTUM SCAN")
    st.button("🗑️ RESET TERMINAL", on_click=reset)

# --- PAINEL PRINCIPAL: A MATRIX ---
if not run:
    st.markdown("<div style='text-align:center; margin-top:15%; opacity:0.1;'><h1>QUANTUM ENGINE IDLE</h1><p>AWAITING INPUT PARAMETERS...</p></div>", unsafe_allow_html=True)
else:
    # Engine de Cálculo 1.000.000 Sims
    adj = 0.67 if "CUP" in ctx else 1.0
    lh = max(0.01, ((hgf/5)*(aga/5))**0.5)
    la = max(0.01, ((agf*adj/5)*(hga/5))**0.5)
    
    sim_h, sim_a = np.random.poisson(lh, 1000000), np.random.poisson(la, 1000000)
    stot = sim_h + sim_a
    ph, px, pa = np.mean(sim_h > sim_a), np.mean(sim_h == sim_a), np.mean(sim_h < sim_a)
    ph, px, pa = ph/(ph+px+pa), px/(ph+px+pa), pa/(ph+px+pa)

    # Header de Jogo
    st.markdown(f"<h1 style='letter-spacing:-2px; margin-bottom:0;'>{h_n} <span style='color:#00FF88; font-weight:300;'>VS</span> {a_n}</h1>", unsafe_allow_html=True)
    st.markdown("<p style='font-family:\"JetBrains Mono\"; color:#64748B;'>TERMINAL_ID: STARLINE_V70 // STATUS: ANALYZED // SIMS: 1,000,000</p>", unsafe_allow_html=True)

    # Top Metrics Row
    c_m1, c_m2, c_m3 = st.columns(3)
    with c_m1:
        st.markdown(f"<div class='metric-card'><p style='margin:0; color:#64748B;'>WIN PROB {h_n}</p><h2 style='margin:0; color:#00FF88;'>{ph:.1%}</h2></div>", unsafe_allow_html=True)
    with c_m2:
        st.markdown(f"<div class='metric-card'><p style='margin:0; color:#64748B;'>WIN PROB {a_n}</p><h2 style='margin:0; color:#3B82F6;'>{pa:.1%}</h2></div>", unsafe_allow_html=True)
    with c_m3:
        st.markdown(f"<div class='metric-card'><p style='margin:0; color:#64748B;'>DRAW PROB</p><h2 style='margin:0; color:#94A3B8;'>{px:.1%}</h2></div>", unsafe_allow_html=True)

    # Middle Row: Visual Analytics
    c_viz1, c_viz2 = st.columns([1.2, 0.8])
    
    with c_viz1:
        xr = list(range(6))
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=xr, y=[poisson.pmf(i, lh) for i in xr], name=h_n, fill='tozeroy', line_color='#00FF88', line_width=4))
        fig.add_trace(go.Scatter(x=xr, y=[poisson.pmf(i, la) for i in xr], name=a_n, fill='tozeroy', line_color='#3B82F6', line_width=4))
        fig.update_layout(
            title="POISSON GOAL CURVES", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font_color="white", height=350, margin=dict(l=0,r=0,t=40,b=0),
            xaxis=dict(gridcolor='rgba(255,255,255,0.05)'), yaxis=dict(gridcolor='rgba(255,255,255,0.05)')
        )
        st.plotly_chart(fig, use_container_width=True)

    with c_viz2:
        # Gauge de Edge Suprema
        mkts_raw = [
            ("HOME WIN", ph, m1), ("DRAW", px, mx), ("AWAY WIN", pa, m2),
            ("OVER 2.5", np.mean(stot>2.5), m_o25), ("UNDER 2.5", np.mean(stot<2.5), m_u25), ("BTTS YES", np.mean((sim_h>0)&(sim_a>0)), m_ob)
        ]
        best_m = max(mkts_raw, key=lambda x: (x[1]*x[2])-1)
        best_e = (best_m[1]*best_m[2])-1
        
        fig_g = go.Figure(go.Indicator(
            mode = "gauge+number", value = best_e*100,
            title = {'text': f"ALPHA EDGE: {best_m[0]}", 'font': {'size': 14, 'color': '#94A3B8'}},
            gauge = {
                'axis': {'range': [0, 50], 'tickcolor': "#00FF88"},
                'bar': {'color': "#00FF88"},
                'bgcolor': "rgba(0,0,0,0.3)",
                'threshold': {'line': {'color': "white", 'width': 2}, 'thickness': 0.8, 'value': 45}
            },
            number = {'suffix': "%", 'font': {'size': 40, 'color': '#00FF88'}}
        ))
        fig_g.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="white", height=350, margin=dict(l=20,r=20,t=80,b=0))
        st.plotly_chart(fig_g, use_container_width=True)

    # --- THE TRADING MATRIX V70 ---
    st.markdown("### 💎 REAL-TIME TRADING MATRIX")
    
    table_html = """
    <table class='matrix-table'>
        <thead>
            <tr>
                <th>Market</th>
                <th>Prob.</th>
                <th>Fair Odd</th>
                <th>Bookie</th>
                <th>Edge (%)</th>
                <th>Stake Advice</th>
                <th>Expected Profit</th>
            </tr>
        </thead>
        <tbody>
    """
    
    for name, p, b in mkts_raw:
        edge = (p * b) - 1
        kelly = (edge / (b - 1)) * 0.20 if edge > 0.02 else 0 # 20% Fractional Kelly
        stk = bank * kelly
        prof = (stk * b) - stk if stk > 0 else 0
        
        # Color Logic Néon
        e_color = "#00FF88" if edge > 0.10 else "#FACC15" if edge > 0 else "#F87171"
        row_style = "style='opacity:0.3;'" if edge < 0 else ""
        
        table_html += f"""
            <tr {row_style}>
                <td style='font-weight:700;'>{name}</td>
                <td>{p:.1%}</td>
                <td>{1/p:.2f}</td>
                <td style='color:#00FF88; font-weight:800;'>{b:.2f}</td>
                <td style='color:{e_color}; font-weight:800;'>{edge:+.1%}</td>
                <td style='font-family:"JetBrains Mono";'>{stk:.2f}€</td>
                <td style='color:{e_color}; font-weight:800;'>{prof:.2f}€</td>
            </tr>
        """
    
    table_html += "</tbody></table>"
    st.write(table_html, unsafe_allow_html=True)

    # Footer: Intelligence Scores
    st.markdown("<br>", unsafe_allow_html=True)
    st.write("**PROBABLE SCORE MATRIX (TOP 3)**")
    hp, ap = poisson.pmf(range(5), lh), poisson.pmf(range(5), la)
    mtx = np.outer(hp, ap); mtx /= mtx.sum()
    idx = np.unravel_index(np.argsort(mtx.ravel())[-3:], mtx.shape)
    s_cols = st.columns(3)
    for j in range(2, -1, -1):
        s_cols[2-j].markdown(f"""
            <div style='background:rgba(255,255,255,0.03); padding:15px; border-radius:12px; border:1px solid rgba(255,255,255,0.05); text-align:center;'>
                <p style='margin:0; font-size:12px; color:#64748B;'>SCORE PREDICTION</p>
                <h3 style='margin:0; color:#FFFFFF;'>{idx[0][j]} - {idx[1][j]}</h3>
                <p style='margin:0; color:#00FF88;'>{mtx[idx[0][j], idx[1][j]]:.1%}</p>
            </div>
        """, unsafe_allow_html=True)
