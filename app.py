import streamlit as st
import numpy as np
from scipy.stats import poisson
import pandas as pd
import plotly.graph_objects as go

# 1. Configuração de Terminal de Investimento
st.set_page_config(page_title="STARLINE V85 - SHARK EDITION", layout="wide", initial_sidebar_state="expanded")

# 2. CSS "Shark Stealth" (Otimizado para Legibilidade e Contraste)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Plus+Jakarta+Sans:wght@400;700;800&display=swap');
    
    .stApp { background-color: #000000; color: #FFFFFF; font-family: 'Plus Jakarta Sans', sans-serif; }
    
    /* Sidebar Compacta */
    [data-testid="stSidebar"] { background-color: #050505 !important; border-right: 1px solid #111111; }
    
    /* Títulos e Tipografia */
    h1, h2, h3 { color: #FFFFFF !important; font-weight: 800 !important; letter-spacing: -1px; }
    .stMetric { background-color: #0A0A0A; border: 1px solid #1A1A1A; border-radius: 10px; padding: 10px; }

    /* ADVISOR COMPACTO (Design 2026) */
    .advisor-bar {
        background: #0A0A0A; border: 1px solid #1A1A1A; border-left: 6px solid #00FF88;
        padding: 15px 25px; border-radius: 8px; margin-bottom: 20px;
        display: flex; justify-content: space-between; align-items: center;
    }

    /* BOTÃO DE EXECUÇÃO NÉON */
    div.stButton > button {
        background: #00FF88 !important; color: #000000 !important; font-weight: 800; 
        height: 3.5em; width: 100%; border: none; border-radius: 6px; text-transform: uppercase;
    }

    /* TABELA DE TRADING (CENTRAMENTO E CORES) */
    .styled-table {
        width: 100%; border-collapse: collapse; background-color: #000000;
        color: #FFFFFF; font-family: 'JetBrains Mono', monospace; text-align: center;
    }
    .styled-table th {
        background-color: #0A0A0A; color: #64748B; padding: 12px;
        text-transform: uppercase; font-size: 0.75rem; border-bottom: 2px solid #1A1A1A;
        text-align: center !important;
    }
    .styled-table td {
        padding: 14px; border-bottom: 1px solid #111111; text-align: center !important;
    }
    </style>
    """, unsafe_allow_html=True)

def reset():
    for key in list(st.session_state.keys()): del st.session_state[key]

# --- SIDEBAR DE COMANDO ---
with st.sidebar:
    st.markdown("<h2 style='color:#00FF88;'>⚙️ TERMINAL</h2>", unsafe_allow_html=True)
    bank = st.number_input("BANCA (€)", value=1000.0)
    ctx = st.selectbox("ESTRATÉGIA", ["REGULAR", "PLAYOFF"])
    
    st.markdown("---")
    h_n = st.text_input("HOME", "LEIPZIG").upper()
    a_n = st.text_input("AWAY", "HOFFENHEIM").upper()
    
    c1, c2 = st.columns(2)
    hgf = c1.number_input("HGF", 8.0); hga = c2.number_input("HGA", 12.0)
    agf = c1.number_input("AGF", 12.0); aga = c2.number_input("AGA", 10.0)
    
    st.markdown("---")
    st.write("LIVE ODDS")
    m1 = st.number_input("1", 1.90); mx = st.number_input("X", 4.00); m2 = st.number_input("2", 3.35)
    m_o25 = st.number_input("O2.5", 1.33); m_u25 = st.number_input("U2.5", 2.65)
    m_ob = st.number_input("BTTS", 1.32); m_hah = st.number_input("DNB-H", 1.33)
    
    run = st.button("🚀 SCAN QUANTUM")
    st.button("🗑️ RESET", on_click=reset)

if run:
    # ENGINE 1M
    adj = 0.67 if ctx == "PLAYOFF" else 1.0
    lh, la = max(0.01, ((hgf/5)*(aga/5))**0.5), max(0.01, ((agf*adj/5)*(hga/5))**0.5)
    sim_h, sim_a = np.random.poisson(lh, 1000000), np.random.poisson(la, 1000000)
    stot = sim_h + sim_a
    ph, px, pa = np.mean(sim_h > sim_a), np.mean(sim_h == sim_a), np.mean(sim_h < sim_a)
    ph, px, pa = ph/(ph+px+pa), px/(ph+px+pa), pa/(ph+px+pa)

    st.markdown(f"<h1 style='margin-bottom:0;'>{h_n} vs {a_n}</h1>", unsafe_allow_html=True)

    # 1. ADVISOR COMPACTO (TOP)
    mkts = [
        ("1X2: "+h_n, ph, m1), ("1X2: "+a_n, pa, m2),
        ("OVER 2.5", np.mean(stot>2.5), m_o25), ("UNDER 2.5", np.mean(stot<2.5), m_u25),
        ("BTTS: YES", np.mean((sim_h>0)&(sim_a>0)), m_ob), ("DNB: "+h_n, ph/(ph+pa), m_hah)
    ]
    recoms = sorted([(n, p, b, (p*b)-1) for n, p, b in mkts if (p*b)-1 > 0.05], key=lambda x: x[3], reverse=True)

    if recoms:
        n, p, b, edge = recoms[0]
        st.markdown(f"""
            <div class="advisor-bar">
                <div style="font-weight:800; font-size:1.1rem; color:white;">🎯 SINAL ALPHA: <span style="color:#00FF88;">{n}</span></div>
                <div style="font-weight:700; color:#00FF88;">EDGE: {edge:+.1%} | CONFIDANÇA: {p:.1%} | ODD: {b:.2f}</div>
            </div>
        """, unsafe_allow_html=True)

    # 2. MATRIX DE TRADING (CENTER)
    st.markdown("### 💎 MARKET MATRIX")
    
    # Construção da tabela HTML para centramento absoluto e cores
    table_html = """
    <table class="styled-table">
        <thead>
            <tr>
                <th>Mercado</th>
                <th>Probabilidade (%)</th>
                <th>Odd Justa</th>
                <th>Odd Casa</th>
                <th>Valor Esperado (EV)</th>
            </tr>
        </thead>
        <tbody>
    """
    
    for n, p, b in mkts + [("1X2: DRAW", px, mx)]:
        edge = (p * b) - 1
        # Lógica de Heatmap
        bg_color = "rgba(0, 255, 136, 0.15)" if edge > 0.10 else "rgba(255, 255, 255, 0.02)"
        edge_txt_color = "#00FF88" if edge > 0 else "#FF1744"
        op = "1" if edge > 0 else "0.4"
        
        table_html += f"""
        <tr style="background-color:{bg_color}; opacity:{op};">
            <td style="font-weight:700; color:#FFFFFF;">{n}</td>
            <td>{p:.1%}</td>
            <td>{1/p:.2f}</td>
            <td style="font-weight:700; color:#00FF88;">{b:.2f}</td>
            <td style="font-weight:800; color:{edge_txt_color};">{edge:+.1%}</td>
        </tr>
        """
    
    table_html += "</tbody></table>"
    st.markdown(table_html, unsafe_allow_html=True)

    # 3. GRÁFICOS E SCORES (BOTTOM)
    st.markdown("<br>", unsafe_allow_html=True)
    c_viz, c_sc = st.columns([1.3, 0.7])
    
    with c_viz:
        xr = list(range(7))
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=xr, y=[poisson.pmf(i, lh) for i in xr], name=h_n, fill='tozeroy', line_color='#00FF88'))
        fig.add_trace(go.Scatter(x=xr, y=[poisson.pmf(i, la) for i in xr], name=a_n, fill='tozeroy', line_color='#3B82F6'))
        fig.update_layout(paper_bgcolor='black', plot_bgcolor='black', font_color="white", height=300, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig, use_container_width=True)
        
    with c_sc:
        st.write("**PROBABLE SCORES**")
        hp, ap = poisson.pmf(range(5), lh), poisson.pmf(range(5), la)
        mtx = np.outer(hp, ap); mtx /= mtx.sum()
        idx = np.unravel_index(np.argsort(mtx.ravel())[-3:], mtx.shape)
        for j in range(2, -1, -1):
            st.metric(f"PLACAR {idx[0][j]}-{idx[1][j]}", f"{mtx[idx[0][j], idx[1][j]]:.1%}")
